from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from src.controllers.auth_controller import AuthController
from src.db.session import get_db
from src.services.module_service import ModuleService
from src.services.role_service import RoleService
from src.services.user_service import UserService
from src.auth.jwt_service import JwtService


security = HTTPBearer()


def verify_token(credentials = Depends(security)):
  token = credentials.credentials

  try:
    return JwtService.verify(token)
  except InvalidTokenError:
    raise HTTPException(
      status_code=401,
      detail='Token inválido'
    )

def verify_admin_access(
  token_data = Depends(verify_token),
  db: Session = Depends(get_db)
):
  user_id = int(token_data['sub'])
  role_id = int(token_data['role'])

  user = UserService.get_by_id(
    db,
    user_id
  )

  role = RoleService.get_by_id(
    db,
    role_id
  )

  if not user or not role:
    raise HTTPException(
      status_code=403,
      detail='Usuario o rol inválido'
    )

  return token_data

def require_module(module_id: int):

  def dependency(
    token_data = Depends(verify_token),
    db: Session = Depends(get_db)
  ):
    user_id = int(token_data['sub'])
    role_id = int(token_data['role'])

    user = UserService.get_by_id(
      db,
      user_id
    )

    if not user:
      raise HTTPException(
        status_code=401,
        detail='User not found'
      )

    has_role = any(
      role.id_role == role_id
      for role in user.roles_user
    )

    if not has_role:
      raise HTTPException(
        status_code=403,
        detail='User does not have this role'
      )

    module = ModuleService.get_by_id(
      db,
      module_id
    )

    if not module:
      raise HTTPException(
        status_code=404,
        detail='Module not found'
      )

    has_access = any(
      role.id_role == role_id
      for role in module.roles_module
    )

    if not has_access:
      raise HTTPException(
        status_code=403,
        detail='Access denied'
      )

    return token_data

  return dependency
