from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Module, Role

class ModuleService:
  @staticmethod
  def get_all(db: Session) -> list[Module]:
    return list(db.scalars(select(Module)).all())

  @staticmethod
  def get_by_id(db: Session, module_id: int) -> Module | None:
    return db.get(Module, module_id)

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
