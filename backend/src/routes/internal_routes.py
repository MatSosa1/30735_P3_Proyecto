from fastapi import APIRouter, Header, HTTPException, status

from pydantic import BaseModel

from src.config.env import INTERNAL_SERVICES_SECRET
from src.controllers.auth_controller import AuthController


class ValidateTokenBody(BaseModel):
  token: str


router = APIRouter(
  prefix='/internals',
  tags=['Internal']
)


@router.post('/validate-token')
def validate_token(
  payload: ValidateTokenBody,
  x_internal_secret: str | None = Header(default=None)
):
  # Solo microservicios hijos con el secreto compartido pueden consultar este endpoint (Zero Trust)
  if x_internal_secret != INTERNAL_SERVICES_SECRET:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail='Acceso no autorizado'
    )

  result = AuthController.validate_token(payload.token)

  if not result:
    return {
      'valid': False
    }

  return {
    'valid': True,
    'user_id': result['user_id'],
    'role_id': result['role_id']
  }
