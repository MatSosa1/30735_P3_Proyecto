from sqlalchemy.orm import Session

from jwt import InvalidTokenError

from src.models.models import Module
from src.auth.jwt_service import JwtService
from src.auth.password_service import PasswordService
from src.services.user_service import UserService
from src.services.role_service import RoleService


class AuthController:
  # Login
  @staticmethod
  def login(db: Session, username: str, password: str, role_id: int) -> str | None:  # Returns token
    user = UserService.get_by_username(db, username)

    # If exists
    if not user:
      return None

    # Verify Password
    if not PasswordService.verify_password(password, user.password_user):
      return None

    return JwtService.generate(user.id_user, user.username_user, role_id)

  # Verify role for route access
  @staticmethod
  def have_user_access(db: Session, token: str, module: Module) -> bool:
    try:
      token_dict = JwtService.verify(token)

      user_id: int = int(token_dict['sub'])
      user_actual_role: int = int(token_dict['role'])

      user = UserService.get_by_id(db, user_id)
      role = RoleService.get_by_id(db, user_actual_role)

      if not user or not role:
        return False

      if role in module.roles_module:  # Maybe only check the ids of the module
        return True

      return False
    except InvalidTokenError:
      return False
