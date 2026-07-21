import time

import jwt as pyjwt
import pytest

from fastapi.testclient import TestClient

from sqlalchemy.orm import Session, sessionmaker

from src.auth.jwt_service import JWT_ALGORITHM
from src.config.env import JWT_SECRET
from src.config.rate_limiter import limiter
from src.controllers.auth_controller import AuthController
from src.db.conn import engine
from main import app


SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)


class TestSecurity:
  client = TestClient(app)

  def setup_method(self):
    # Evita que el rate limiting de /auth/login (5/minute) se acumule entre tests
    limiter.reset()

    self.db: Session = SessionLocal()

    token = AuthController.login(
      self.db,
      'msosa',
      '1234',
      1
    )

    self.headers = {
      'Authorization': f'Bearer {token}'
    }

  def teardown_method(self):
    self.db.close()

  def _get_temp_token(self) -> str:
    response = self.client.post(
      '/api/auth/login',
      json={'username': 'msosa', 'password': '1234'}
    )

    return response.json()['temp_token']

  # --- SQL Injection (Shift-Left: el ORM parametriza, esto no debe autenticar ni romper el server) ---
  @pytest.mark.parametrize('malicious_username', [
    "msosa' OR '1'='1",
    "msosa'--",
    "'; DROP TABLE \"Users\"; --",
    "msosa' UNION SELECT * FROM \"Users\" --",
  ])
  def test_login_sql_injection_attempts_are_rejected(self, malicious_username):
    response = self.client.post(
      '/api/auth/login',
      json={'username': malicious_username, 'password': 'anything'}
    )

    assert response.status_code == 401

  def test_users_table_survives_injection_attempts(self):
    # Si un intento previo hubiera alterado/borrado la tabla, este login legitimo fallaria
    response = self.client.post(
      '/api/auth/login',
      json={'username': 'msosa', 'password': '1234'}
    )

    assert response.status_code == 200

  # --- password_user nunca debe viajar en una respuesta serializada ---
  def test_password_never_in_user_list_response(self):
    response = self.client.get('/api/users/', headers=self.headers)

    assert response.status_code == 200

    for user in response.json():
      assert 'password_user' not in user
      assert 'password' not in user

  def test_password_never_in_login_response(self):
    response = self.client.post(
      '/api/auth/login',
      json={'username': 'msosa', 'password': '1234'}
    )

    assert response.status_code == 200

    for role in response.json()['roles']:
      assert 'password_user' not in role
      assert 'password' not in role

  # --- Expiracion de JWT ---
  def test_expired_session_token_is_rejected(self):
    expired_payload = {
      'sub': '1',
      'user': 'msosa',
      'role': 1,
      'exp': int(time.time()) - 60,
    }
    expired_token = pyjwt.encode(expired_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    response = self.client.get(
      '/api/users/',
      headers={'Authorization': f'Bearer {expired_token}'}
    )

    assert response.status_code == 401

  # --- Un TempToken no debe servir como JWT de sesion ---
  def test_temp_token_cannot_be_used_as_session_token(self):
    temp_token = self._get_temp_token()

    response = self.client.get(
      '/api/users/',
      headers={'Authorization': f'Bearer {temp_token}'}
    )

    # Antes del fix: 500 (KeyError sin manejar por falta del claim 'role')
    assert response.status_code == 401

  def test_temp_token_rejected_by_internal_validate_token(self):
    temp_token = self._get_temp_token()

    response = self.client.post(
      '/api/internals/validate-token',
      json={'token': temp_token},
      headers={'x-internal-secret': 'internalservicessecret'}
    )

    assert response.status_code == 200
    assert response.json() == {'valid': False}

  # --- Un JWT de sesion no debe servir como TempToken ---
  def test_session_token_cannot_be_used_as_temp_token(self):
    temp_token = self._get_temp_token()

    select_role_response = self.client.post(
      '/api/auth/select-role',
      json={'temp_token': temp_token, 'role_id': 1}
    )
    session_token = select_role_response.json()['token']

    response = self.client.post(
      '/api/auth/select-role',
      json={'temp_token': session_token, 'role_id': 1}
    )

    assert response.status_code == 401
