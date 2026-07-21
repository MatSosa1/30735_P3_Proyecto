from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import Module, Role, RoleModule

class ModuleService:
  @staticmethod
  def get_all(db: Session) -> list[Module]:
    return list(db.scalars(select(Module)).all())

  @staticmethod
  def get_by_id(db: Session, module_id: int) -> Module | None:
    # select() (a diferencia de db.get()) siempre respeta el filtro global de estado=ACTIVO,
    # incluso si el objeto ya está en el identity map de la sesión.
    return db.scalar(select(Module).where(Module.id_module == module_id))

  @staticmethod
  def set_roles(db: Session, module_id: int, roles_id: list[int]) -> Module | None:
    module = db.get(Module, module_id)

    if not module:
      return None

    roles_select_statement = select(Role).where(Role.id_role.in_(roles_id))
    valid_role_ids = [role.id_role for role in db.scalars(roles_select_statement).all()]

    db.query(RoleModule).filter(RoleModule.id_module == module_id).delete()
    db.flush()

    for role_id in valid_role_ids:
      db.add(RoleModule(id_role=role_id, id_module=module_id))

    db.commit()
    db.refresh(module)

    return module
