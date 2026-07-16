from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Role, User


class UserService:
  @staticmethod
  def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

  @staticmethod
  def get_by_username(db: Session, username: str) -> User | None:
    select_statement = select(User).where(User.username_user == username)

    return db.scalar(select_statement)

  @staticmethod
  def set_roles(db: Session, user_id: int, roles_id: list[int]) -> User | None:
    user = db.get(User, user_id)

    if not user:
      return None

    roles_select_statement = select(Role).where(Role.id_role.in_(roles_id))
    roles = list(db.scalars(roles_select_statement).all())

    user.roles_user = roles

    db.commit()
    db.refresh(user)

    return user
