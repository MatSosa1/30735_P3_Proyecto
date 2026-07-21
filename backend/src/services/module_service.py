from sqlalchemy.orm import Session, aliased
from sqlalchemy import literal, select

from src.models.models import EstadoEnum, Module, Role, RoleModule

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

  # Recorre la cadena de ancestros del nuevo padre propuesto; True si module_id aparece en ella
  # (o si new_parent_id == module_id), lo que crearía un ciclo en el árbol (parent_id_module).
  @staticmethod
  def would_create_cycle(db: Session, module_id: int, new_parent_id: int) -> bool:
    current_id: int | None = new_parent_id
    visited: set[int] = set()

    while current_id is not None:
      if current_id == module_id or current_id in visited:
        return True

      visited.add(current_id)

      parent = db.get(Module, current_id)

      if not parent:
        return False

      current_id = parent.parent_id_module

    return False

  # Cierre de ancestros (CTE recursiva, una sola query) de todos los módulos accesibles al rol:
  # arranca en los módulos con asignación directa en Roles_Modules y sube por parent_id_module
  # hasta la raíz. Se ignora el filtro global de estado=ACTIVO a propósito (include_inactive=True):
  # se necesita ver módulos inactivos en la cadena para poder podar sus descendientes en Python
  # (ver ModuleController._build_menu_tree), por eso el estado ACTIVO de Roles_Modules se filtra
  # explícitamente acá en vez de depender del filtro global.
  @staticmethod
  def get_menu_ancestor_closure(db: Session, role_id: int):
    # 'is_accessible' distingue las hojas con asignación directa en Roles_Modules (caso base)
    # de los ancestros agregados solo para reconstruir el camino (caso recursivo) — necesario
    # para podar en ModuleController._build_menu_tree un ancestro que quedó sin ningún
    # descendiente accesible tras filtrar por estado.
    base_query = (
      select(
        Module.id_module,
        Module.parent_id_module,
        Module.name_module,
        Module.url_module,
        Module.estado,
        literal(True).label('is_accessible'),
      )
      .join(RoleModule, RoleModule.id_module == Module.id_module)
      .where(
        RoleModule.id_role == role_id,
        RoleModule.estado == EstadoEnum.ACTIVO,
      )
    )

    ancestors_cte = base_query.cte(name='menu_ancestors', recursive=True)

    parent = aliased(Module)
    recursive_query = (
      select(
        parent.id_module,
        parent.parent_id_module,
        parent.name_module,
        parent.url_module,
        parent.estado,
        literal(False).label('is_accessible'),
      )
      .join(ancestors_cte, parent.id_module == ancestors_cte.c.parent_id_module)
    )

    full_cte = ancestors_cte.union(recursive_query)

    return db.execute(
      select(full_cte).execution_options(include_inactive=True)
    ).all()
