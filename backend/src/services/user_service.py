from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Role, User, UserRole


class UserService:
  @staticmethod
  def get_all(db: Session) -> list[User]:
    return list(db.scalars(select(User)).all())

  @staticmethod
  def get_by_id(db: Session, user_id: int) -> User | None:
    # select() (a diferencia de db.get()) siempre respeta el filtro global de estado=ACTIVO,
    # incluso si el objeto ya está en el identity map de la sesión.
    return db.scalar(select(User).where(User.id_user == user_id))

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
    valid_role_ids = [role.id_role for role in db.scalars(roles_select_statement).all()]

    db.query(UserRole).filter(UserRole.id_user == user_id).delete()
    db.flush()

    for role_id in valid_role_ids:
      db.add(UserRole(id_user=user_id, id_role=role_id))

    db.commit()
    db.refresh(user)

    return user
