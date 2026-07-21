from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Role, User, UserRole


class RoleService:
  @staticmethod
  def get_all(db: Session) -> list[Role]:
    return list(db.scalars(select(Role)).all())

  @staticmethod
  def get_by_id(db: Session, role_id: int) -> Role | None:
    # select() (a diferencia de db.get()) siempre respeta el filtro global de estado=ACTIVO,
    # incluso si el objeto ya está en el identity map de la sesión.
    return db.scalar(select(Role).where(Role.id_role == role_id))

  @staticmethod
  def get_by_name(db: Session, name: str) -> Role | None:
    select_statement = select(Role).where(Role.name_role == name)

    return db.scalar(select_statement)

  @staticmethod
  def has_active_users(db: Session, role_id: int) -> bool:
    # El filtro global de estado=ACTIVO ya excluye usuarios/asignaciones inactivas de esta query
    select_statement = select(UserRole).join(User).where(UserRole.id_role == role_id)

    return db.scalar(select_statement) is not None
