import pytest

from jwt import InvalidTokenError

from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from src.controllers.user_controller import UserController
from src.controllers.auth_controller import AuthController
from src.auth.jwt_service import JwtService
from src.db.conn import engine
from src.models.models import Base, Module, RefreshToken, User
from src.controllers.module_controller import ModuleController

SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)

class TestJwtService:
  db: Session

  def setup_method(self):
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)

    self.db: Session = SessionLocal()

  def teardown_method(self):
    self.db.execute(delete(RefreshToken).where(RefreshToken.id_user == 1))
    self.db.commit()
    self.db.close()

  def test_generate_token(self):
    token = JwtService.generate(1, 'msosa', 1)

    assert token.__class__ == str

  def test_verify_token(self):
    token = JwtService.generate(1, 'msosa', 1)

    token_dict = JwtService.verify(token)
    # print(token_dict)

    assert token_dict['sub'] == '1'
    assert token_dict['user'] == 'msosa'

  def test_verify_invalid_token(self):
    with pytest.raises(InvalidTokenError):
      token_dict = JwtService.verify('hola')

      assert 'sub' in token_dict

  def test_valid_user_to_module(self):
    module = ModuleController.get_by_id(self.db, 4)
    user = UserController.get_by_id(self.db, 1)

    assert isinstance(module, Module)
    assert isinstance(user, User)
    assert module.id_module == 4
    assert user.id_user == 1

    token = AuthController.login(self.db, user.username_user, '1234', 1)

    assert isinstance(token, str)

    assert AuthController.have_user_access(self.db, token, module) == True

  def test_login_step1_success(self):
    result = AuthController.login_step1(self.db, 'msosa', '1234')

    assert result is not None

    temp_token, roles = result

    assert isinstance(temp_token, str)
    assert any(role.id_role == 1 for role in roles)

    payload = JwtService.verify_temp(temp_token)

    assert payload['sub'] == '1'
    assert 'role' not in payload

  def test_login_step1_wrong_password(self):
    result = AuthController.login_step1(self.db, 'msosa', 'wrong-password')

    assert result is None

  def test_select_role_success(self):
    temp_token, _ = AuthController.login_step1(self.db, 'msosa', '1234')

    result = AuthController.select_role(self.db, temp_token, 1)

    assert result is not None

    token, refresh_token = result

    payload = JwtService.verify(token)

    assert payload['sub'] == '1'
    assert payload['role'] == 1
    assert isinstance(refresh_token, str)

  def test_select_role_with_role_not_owned_by_user(self):
    temp_token, _ = AuthController.login_step1(self.db, 'msosa', '1234')

    # El rol 3 (Visitante) no está asignado a msosa en el seed
    result = AuthController.select_role(self.db, temp_token, 3)

    assert result is None

  def test_select_role_invalid_temp_token(self):
    result = AuthController.select_role(self.db, 'not-a-real-token', 1)

    assert result is None

  def test_refresh_success(self):
    temp_token, _ = AuthController.login_step1(self.db, 'msosa', '1234')
    _, refresh_token = AuthController.select_role(self.db, temp_token, 1)

    result = AuthController.refresh(self.db, refresh_token)

    assert result is not None

    new_token, new_refresh_token = result

    assert isinstance(new_token, str)
    assert new_refresh_token != refresh_token

  def test_refresh_reuse_detection_revokes_all(self):
    temp_token, _ = AuthController.login_step1(self.db, 'msosa', '1234')
    _, refresh_token = AuthController.select_role(self.db, temp_token, 1)

    first = AuthController.refresh(self.db, refresh_token)
    assert first is not None

    _, second_refresh_token = first

    # Reutilizar el refresh token ya rotado debe fallar y revocar TODOS los tokens del usuario
    reused = AuthController.refresh(self.db, refresh_token)
    assert reused is None

    # El token nuevo emitido en la primera rotación también quedó revocado por la reutilización
    also_revoked = AuthController.refresh(self.db, second_refresh_token)
    assert also_revoked is None

  def test_refresh_invalid_token(self):
    result = AuthController.refresh(self.db, 'not-a-real-refresh-token')

    assert result is None

  def test_logout_revokes_refresh_token(self):
    temp_token, _ = AuthController.login_step1(self.db, 'msosa', '1234')
    _, refresh_token = AuthController.select_role(self.db, temp_token, 1)

    AuthController.logout(self.db, 1)

    result = AuthController.refresh(self.db, refresh_token)

    assert result is None

  def test_validate_token_valid(self):
    token = AuthController.login(self.db, 'msosa', '1234', 1)

    result = AuthController.validate_token(token)

    assert result == {'user_id': 1, 'role_id': 1}

  def test_validate_token_invalid(self):
    result = AuthController.validate_token('not-a-real-token')

    assert result is None
