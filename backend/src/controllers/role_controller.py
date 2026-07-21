from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Role
from src.services.role_service import RoleService


class RoleHasActiveUsersError(Exception):
  pass


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
    return RoleService.get_all(db)

  @staticmethod
  def get_by_id(db: Session, role_id: int) -> Role | None:
    return RoleService.get_by_id(db, role_id)

  @staticmethod
  def get_by_name(db: Session, name: str) -> Role | None:
    return RoleService.get_by_name(db, name)

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

    if RoleService.has_active_users(db, role_id):
      raise RoleHasActiveUsersError()

    role.deactivate()
    db.commit()

    return True
