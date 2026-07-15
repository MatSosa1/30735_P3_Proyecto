from datetime import datetime, timedelta, UTC

import jwt

from src.config.env import JWT_SECRET, JWT_EXPIRE_IN_MINUTES


JWT_ALGORITHM = 'HS256'

class JwtService:
  @staticmethod
  def generate(user_id: int, username: str) -> str:
    payload = {
      'sub': str(user_id),
      'user': username,
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
