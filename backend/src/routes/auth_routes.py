from fastapi import APIRouter, Depends

from pydantic import BaseModel

from sqlalchemy.orm import Session

from src.controllers.auth_controller import AuthController
from src.db.session import get_db


# Helper Classes
class UserLogin(BaseModel):
  username: str
  password: str
  actual_role_id: int

class UserGetRole(BaseModel):
  username: str
  password: str


# Routes
router = APIRouter(
  prefix='/auth',
  tags=['Authentication']
)


@router.post('/set_role')
def user_set_role(user: UserGetRole, db: Session = Depends(get_db)):
  roles = AuthController.get_user_roles(db, user.username, user.password)

  if not roles:
    return {
      'error': 'Usuario no existe o no tiene roles'
    }

  return {
    'roles': roles
  }

@router.post('/login')
def login(user: UserLogin, db: Session = Depends(get_db)):
  token = AuthController.login(db, user.username, user.password, user.actual_role_id)

  if not token:
    return {
      'error': 'Credenciales inválidas'
    }

  return {
    'token': token
  }
