import pytest

from jwt import InvalidTokenError

from sqlalchemy.orm import Session, sessionmaker

from src.controllers.user_controller import UserController
from src.controllers.auth_controller import AuthController
from src.auth.jwt_service import JwtService
from src.db.conn import engine
from src.models.models import Base, Module, User
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
