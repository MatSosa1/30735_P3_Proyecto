from datetime import datetime, timedelta, UTC

import jwt

from src.config.env import JWT_SECRET, JWT_EXPIRE_IN_MINUTES, TEMP_TOKEN_EXPIRE_IN_MINUTES


JWT_ALGORITHM = 'HS256'
TEMP_TOKEN_TYPE = 'temp'

class JwtService:
  @staticmethod
  def generate(user_id: int, username: str, role_id: int) -> str:
    payload = {
      'sub': str(user_id),
      'user': username,
      'role': role_id,
      'exp': datetime.now(UTC) + timedelta(minutes=JWT_EXPIRE_IN_MINUTES)
    }

    return jwt.encode(
      payload,
      JWT_SECRET,
      algorithm=JWT_ALGORITHM
    )

  @staticmethod
  def verify(token: str):
    return jwt.decode(
      token,
      JWT_SECRET,
      algorithms=[JWT_ALGORITHM]
    )

  # TempToken: emitido tras validar credenciales (paso 1 del login), antes de elegir rol.
  # Vida muy corta y sin 'role' (Least Privilege: no habilita nada por si solo).
  @staticmethod
  def generate_temp(user_id: int, username: str) -> str:
    payload = {
      'sub': str(user_id),
      'user': username,
      'type': TEMP_TOKEN_TYPE,
      'exp': datetime.now(UTC) + timedelta(minutes=TEMP_TOKEN_EXPIRE_IN_MINUTES)
    }

    return jwt.encode(
      payload,
      JWT_SECRET,
      algorithm=JWT_ALGORITHM
    )

  @staticmethod
  def verify_temp(token: str):
    payload = jwt.decode(
      token,
      JWT_SECRET,
      algorithms=[JWT_ALGORITHM]
    )

    if payload.get('type') != TEMP_TOKEN_TYPE:
      raise jwt.InvalidTokenError('Token no es un TempToken')

    return payload
