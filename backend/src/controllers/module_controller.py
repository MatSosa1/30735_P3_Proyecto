from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Module, Role


class ModuleController:
  # Create
  @staticmethod
  def create(db: Session, name: str, url: str, parent_id: int | None) -> Module:
    new_module = Module(
      name_module=name,
      url_module=url,
      parent_id_module=parent_id
    )

    db.add(new_module)
    db.commit()
    db.refresh(new_module)

    return new_module

  # Read
  @staticmethod
  def get_all(db: Session) -> list[Module]:
    return list(db.scalars(select(Module)).all())

  @staticmethod
  def get_by_id(db: Session, module_id: int) -> Module | None:
    return db.get(Module, module_id)

  # Update
  @staticmethod
  def update(db: Session, module_id: int, name: str | None = None, url: str | None = None, parent_id: int | None = None) -> Module | None:
    module = db.get(Module, module_id)

    if not module:  # Not found
      return None

    # POST / PATCH
    if name is not None:
      module.name_module = name

    if url is not None:
      module.url_module = url

    if parent_id is not None:
      module.parent_id_module = parent_id

    db.commit()
    db.refresh(module)

    return module

  @staticmethod
  def set_roles(db: Session, module_id: int, roles_id: list[int]) -> Module | None:
    module = db.get(Module, module_id)

    if not module:
      return None

    roles_select_statement = select(Role).where(Role.id_role.in_(roles_id))
    roles = list(db.scalars(roles_select_statement).all())

    module.roles_module = roles

    db.commit()
    db.refresh(module)

    return module

  # Delete
  @staticmethod
  def delete(db: Session, module_id: int) -> bool:
    module = db.get(Module, module_id)

    if module is None:
      return False

    db.delete(module)
    db.commit()

    return True
