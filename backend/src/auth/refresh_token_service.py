import hashlib
import secrets
from datetime import datetime, timedelta, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.env import REFRESH_TOKEN_EXPIRE_IN_DAYS
from src.models.models import RefreshToken


class RefreshTokenService:
  @staticmethod
  def _hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

  @staticmethod
  def issue(db: Session, user_id: int, role_id: int) -> str:
    raw_token = secrets.token_urlsafe(32)

    db.add(RefreshToken(
      id_user=user_id,
      id_role=role_id,
      token_hash=RefreshTokenService._hash(raw_token),
      expires_at=datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_IN_DAYS),
    ))
    db.commit()

    return raw_token

  @staticmethod
  def find_by_raw_token(db: Session, raw_token: str) -> RefreshToken | None:
    token_hash = RefreshTokenService._hash(raw_token)

    return db.scalar(
      select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )

  @staticmethod
  def revoke_all_for_user(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(
      RefreshToken.id_user == user_id,
      RefreshToken.revoked.is_(False)
    ).update({'revoked': True})

    db.commit()
