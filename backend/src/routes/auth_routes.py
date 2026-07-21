from fastapi import APIRouter, Depends, HTTPException, Request, status

from sqlalchemy.orm import Session

from pydantic import BaseModel

from src.config.rate_limiter import limiter
from src.controllers.auth_controller import AuthController
from src.db.session import get_db
from src.routes.dependencies.dependencies import verify_token


# Helper Classes
class UserLogin(BaseModel):
  username: str
  password: str

class SelectRole(BaseModel):
  temp_token: str
  role_id: int

class RefreshTokenBody(BaseModel):
  refresh_token: str


# Routes
router = APIRouter(
  prefix='/auth',
  tags=['Authentication']
)


@router.post('/login')
@limiter.limit('5/minute')
def login(request: Request, user: UserLogin, db: Session = Depends(get_db)):
  result = AuthController.login_step1(db, user.username, user.password)

  # Mensaje generico: no revela si fallo el usuario o la contraseña (Zero Trust)
  if not result:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail='Credenciales inválidas'
    )

  temp_token, roles = result

  return {
    'temp_token': temp_token,
    'roles': roles
  }

@router.post('/select-role')
def select_role(payload: SelectRole, db: Session = Depends(get_db)):
  result = AuthController.select_role(db, payload.temp_token, payload.role_id)

  if not result:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail='Selección de rol inválida'
    )

  token, refresh_token = result

  return {
    'token': token,
    'refresh_token': refresh_token
  }

@router.post('/refresh-token')
def refresh_token(payload: RefreshTokenBody, db: Session = Depends(get_db)):
  result = AuthController.refresh(db, payload.refresh_token)

  if not result:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail='Refresh token inválido'
    )

  token, new_refresh_token = result

  return {
    'token': token,
    'refresh_token': new_refresh_token
  }

@router.post('/logout')
def logout(token_data = Depends(verify_token), db: Session = Depends(get_db)):
  AuthController.logout(db, int(token_data['sub']))

  return {
    'message': 'Sesión cerrada'
  }
