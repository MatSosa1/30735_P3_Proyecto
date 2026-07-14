from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Role


class RoleController:
  # Create
  @staticmethod
  def create(db: Session, name: str) -> Role:
    new_role = Role(
      name_role=name,
    )

    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return new_role

  # Read
  @staticmethod
  def get_all(db: Session) -> list[Role]:
    return list(db.scalars(select(Role)).all())

  @staticmethod
  def get_by_id(db: Session, user_id: int) -> Role | None:
    return db.get(Role, user_id)

  @staticmethod
  def get_by_name(db: Session, name: str) -> Role | None:
    select_statement = select(Role).where(Role.name_role == name)

    return db.scalar(select_statement)

  # Update
  @staticmethod
  def update(db: Session, role_id: int, name: str | None = None) -> Role | None:
    role = db.get(Role, role_id)

    if not role:  # Not found
      return None

    # POST / PATCH
    if name is not None:
      role.name_role = name

    db.commit()
    db.refresh(role)

    return role

  # Delete
  @staticmethod
  def delete(db: Session, role_id: int) -> bool:
    role = db.get(Role, role_id)

    if role is None:
      return False

    db.delete(role)
    db.commit()

    return True
