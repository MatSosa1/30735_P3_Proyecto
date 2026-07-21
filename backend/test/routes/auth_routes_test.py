from fastapi.testclient import TestClient

from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from src.config.rate_limiter import limiter
from src.db.conn import engine
from src.models.models import RefreshToken
from main import app


SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)


class TestAuthRoutes:
  client = TestClient(app)

  def setup_method(self):
    # Evita que el rate limiting de /auth/login (5/minute) se acumule entre tests
    limiter.reset()

    self.db: Session = SessionLocal()

  def teardown_method(self):
    self.db.execute(delete(RefreshToken).where(RefreshToken.id_user == 1))
    self.db.commit()
    self.db.close()

  def _login_and_select_role(self, role_id: int = 1):
    login_response = self.client.post(
      '/api/auth/login',
      json={'username': 'msosa', 'password': '1234'}
    )

    temp_token = login_response.json()['temp_token']

    return self.client.post(
      '/api/auth/select-role',
      json={'temp_token': temp_token, 'role_id': role_id}
    )

  # POST /login
  def test_login_success(self):
    response = self.client.post(
      '/api/auth/login',
      json={'username': 'msosa', 'password': '1234'}
    )

    assert response.status_code == 200

    body = response.json()

    assert 'temp_token' in body
    assert any(role['id_role'] == 1 for role in body['roles'])

  def test_login_wrong_password(self):
    response = self.client.post(
      '/api/auth/login',
      json={'username': 'msosa', 'password': 'wrong-password'}
    )

    assert response.status_code == 401

  def test_login_nonexistent_user(self):
    response = self.client.post(
      '/api/auth/login',
      json={'username': 'no_existe', 'password': '1234'}
    )

    assert response.status_code == 401
    # Mensaje genérico: el mismo para usuario inexistente que para contraseña incorrecta
    assert response.json()['detail'] == 'Credenciales inválidas'

  # POST /select-role
  def test_select_role_success(self):
    response = self._login_and_select_role(role_id=1)

    assert response.status_code == 200

    body = response.json()

    assert 'token' in body
    assert 'refresh_token' in body

  def test_select_role_with_role_not_owned(self):
    login_response = self.client.post(
      '/api/auth/login',
      json={'username': 'msosa', 'password': '1234'}
    )

    temp_token = login_response.json()['temp_token']

    response = self.client.post(
      '/api/auth/select-role',
      json={'temp_token': temp_token, 'role_id': 3}
    )

    assert response.status_code == 401

  # POST /refresh-token
  def test_refresh_token_success(self):
    select_role_response = self._login_and_select_role(role_id=1)
    refresh_token = select_role_response.json()['refresh_token']

    response = self.client.post(
      '/api/auth/refresh-token',
      json={'refresh_token': refresh_token}
    )

    assert response.status_code == 200
    assert 'token' in response.json()

  def test_refresh_token_reuse_is_rejected(self):
    select_role_response = self._login_and_select_role(role_id=1)
    refresh_token = select_role_response.json()['refresh_token']

    first = self.client.post(
      '/api/auth/refresh-token',
      json={'refresh_token': refresh_token}
    )
    assert first.status_code == 200

    reused = self.client.post(
      '/api/auth/refresh-token',
      json={'refresh_token': refresh_token}
    )
    assert reused.status_code == 401

  # POST /logout
  def test_logout_revokes_session(self):
    select_role_response = self._login_and_select_role(role_id=1)
    token = select_role_response.json()['token']
    refresh_token = select_role_response.json()['refresh_token']

    logout_response = self.client.post(
      '/api/auth/logout',
      headers={'Authorization': f'Bearer {token}'}
    )
    assert logout_response.status_code == 200

    refresh_response = self.client.post(
      '/api/auth/refresh-token',
      json={'refresh_token': refresh_token}
    )
    assert refresh_response.status_code == 401

  # POST /internals/validate-token
  def test_validate_token_with_valid_secret(self):
    select_role_response = self._login_and_select_role(role_id=1)
    token = select_role_response.json()['token']

    response = self.client.post(
      '/api/internals/validate-token',
      json={'token': token},
      headers={'x-internal-secret': 'internalservicessecret'}
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {'valid': True, 'user_id': 1, 'role_id': 1}

  def test_validate_token_without_secret_is_forbidden(self):
    response = self.client.post(
      '/api/internals/validate-token',
      json={'token': 'whatever'}
    )

    assert response.status_code == 403

  def test_validate_token_invalid_token_with_valid_secret(self):
    response = self.client.post(
      '/api/internals/validate-token',
      json={'token': 'not-a-real-token'},
      headers={'x-internal-secret': 'internalservicessecret'}
    )

    assert response.status_code == 200
    assert response.json() == {'valid': False}
