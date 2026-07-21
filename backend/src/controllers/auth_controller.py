from datetime import datetime, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from jwt import InvalidTokenError

from src.models.models import Module, Role, RoleModule, UserRole
from src.auth.jwt_service import JwtService
from src.auth.password_service import PasswordService
from src.auth.refresh_token_service import RefreshTokenService
from src.services.user_service import UserService
from src.services.role_service import RoleService


class AuthController:
  # Get Roles (uso interno / legacy)
  @staticmethod
  def get_user_roles(db: Session, username: str, password: str) -> list[Role] | None:
    user = UserService.get_by_username(db, username)

    # If exists
    if not user:
      return None

    # Verify Password
    if not PasswordService.verify_password(password, user.password_user):
      return None

    # list(...) materializa el _AssociationList a una lista real: FastAPI/jsonable_encoder no
    # reconoce el proxy como secuencia y recursa infinitamente al intentar serializarlo tal cual.
    return list(user.roles_user)

  # Login directo usuario+contraseña+rol (uso interno / tests). El flujo HTTP real pasa por
  # login_step1 + select_role para no permitir que un token quede habilitado para todos los
  # roles del usuario a la vez (Least Privilege).
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

  # Paso 1 del login HTTP: valida credenciales, devuelve TempToken (sin rol) + roles disponibles.
  @staticmethod
  def login_step1(db: Session, username: str, password: str) -> tuple[str, list[Role]] | None:
    roles = AuthController.get_user_roles(db, username, password)

    if not roles:
      return None

    user = UserService.get_by_username(db, username)
    temp_token = JwtService.generate_temp(user.id_user, user.username_user)

    return temp_token, roles

  # Paso 2 del login HTTP: TempToken + rol elegido -> JWT de sesion + refresh token.
  @staticmethod
  def select_role(db: Session, temp_token: str, role_id: int) -> tuple[str, str] | None:
    try:
      payload = JwtService.verify_temp(temp_token)
    except InvalidTokenError:
      return None

    user_id = int(payload['sub'])
    user = UserService.get_by_id(db, user_id)

    if not user:
      return None

    has_role = db.scalar(
      select(UserRole).where(
        UserRole.id_user == user_id,
        UserRole.id_role == role_id
      )
    ) is not None

    if not has_role:
      return None

    jwt_token = JwtService.generate(user.id_user, user.username_user, role_id)
    refresh_token = RefreshTokenService.issue(db, user.id_user, role_id)

    return jwt_token, refresh_token

  # Renueva el JWT de sesion a partir de un refresh token valido. Si el refresh token ya fue
  # usado/revocado y se reintenta, se asume compromiso y se revocan TODOS los refresh tokens
  # del usuario (reuse detection).
  @staticmethod
  def refresh(db: Session, raw_refresh_token: str) -> tuple[str, str] | None:
    record = RefreshTokenService.find_by_raw_token(db, raw_refresh_token)

    if not record:
      return None

    if record.revoked:
      RefreshTokenService.revoke_all_for_user(db, record.id_user)
      return None

    # SQLite (usado en tests) devuelve datetimes naive aunque la columna sea timezone=True;
    # se asume UTC (es lo unico que este servicio escribe) para poder comparar sin TypeError.
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
      expires_at = expires_at.replace(tzinfo=UTC)

    if expires_at < datetime.now(UTC):
      return None

    user = UserService.get_by_id(db, record.id_user)

    if not user:
      return None

    # Rotacion: el refresh token usado queda revocado, se emite uno nuevo junto con el JWT
    record.revoked = True
    db.commit()

    jwt_token = JwtService.generate(user.id_user, user.username_user, record.id_role)
    new_refresh_token = RefreshTokenService.issue(db, user.id_user, record.id_role)

    return jwt_token, new_refresh_token

  # Cierra la sesion: revoca todos los refresh tokens del usuario autenticado (JWT valido).
  @staticmethod
  def logout(db: Session, user_id: int) -> None:
    RefreshTokenService.revoke_all_for_user(db, user_id)

  # Validacion de token para microservicios hijos (Zero Trust). No expone datos sensibles.
  @staticmethod
  def validate_token(token: str) -> dict | None:
    try:
      payload = JwtService.verify(token)
    except InvalidTokenError:
      return None

    return {
      'user_id': int(payload['sub']),
      'role_id': int(payload['role']),
    }

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

      has_access = db.scalar(
        select(RoleModule).where(
          RoleModule.id_role == user_actual_role,
          RoleModule.id_module == module.id_module
        )
      ) is not None

      return has_access
    except InvalidTokenError:
      return False
