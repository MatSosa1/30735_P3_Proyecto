from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Role


class RoleService:
  @staticmethod
  def get_all(db: Session) -> list[Role]:
    return list(db.scalars(select(Role)).all())

  @staticmethod
  def get_by_id(db: Session, role_id: int) -> Role | None:
    return db.get(Role, role_id)

  @staticmethod
  def get_by_name(db: Session, name: str) -> Role | None:
    select_statement = select(Role).where(Role.name_role == name)

    return db.scalar(select_statement)
