from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import EstadoEnum, Module, Role
from src.services.module_service import ModuleService


class ModuleCycleError(Exception):
  pass


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
    return ModuleService.get_all(db)

  @staticmethod
  def get_by_id(db: Session, module_id: int) -> Module | None:
    return ModuleService.get_by_id(db, module_id)

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
      if ModuleService.would_create_cycle(db, module_id, parent_id):
        raise ModuleCycleError()

      module.parent_id_module = parent_id

    db.commit()
    db.refresh(module)

    return module

  @staticmethod
  def set_roles(db: Session, module_id: int, roles_id: list[int]) -> Module | None:
    return ModuleService.set_roles(db, module_id, roles_id)

  # Delete
  @staticmethod
  def delete(db: Session, module_id: int) -> bool:
    module = db.get(Module, module_id)

    if module is None:
      return False

    module.deactivate()
    db.commit()

    return True

  # Árbol de menú (Sprint 3): una sola query recursiva (CTE) trae el cierre de ancestros de los
  # módulos accesibles al rol; acá se poda en memoria cualquier módulo cuya cadena hasta la raíz
  # tenga un ancestro (o el propio módulo) INACTIVO — "al inactivar un módulo, sus menús no se
  # renderizan", incluso si el hijo individualmente sigue ACTIVO.
  @staticmethod
  def get_menu_tree(db: Session, role_id: int) -> list[dict]:
    rows = ModuleService.get_menu_ancestor_closure(db, role_id)

    return _build_menu_tree(rows)


def _build_menu_tree(rows) -> list[dict]:
  # Un mismo modulo puede aparecer dos veces (una vez como hoja de asignacion directa, otra como
  # ancestro de otra hoja): el resto de columnas es identico en ambas apariciones, is_accessible
  # se agrega con OR explicito mas abajo.
  by_id = {row.id_module: row for row in rows}
  accessible_leaf_ids = {row.id_module for row in rows if row.is_accessible}

  active_chain_cache: dict[int, bool] = {}

  def chain_is_active(module_id: int) -> bool:
    if module_id in active_chain_cache:
      return active_chain_cache[module_id]

    row = by_id.get(module_id)

    if row is None or row.estado != EstadoEnum.ACTIVO:
      active_chain_cache[module_id] = False
      return False

    result = True if row.parent_id_module is None else chain_is_active(row.parent_id_module)
    active_chain_cache[module_id] = result

    return result

  # Solo se conservan las hojas con asignacion directa cuya cadena completa hasta la raiz esta
  # ACTIVA. Los ancestros que existen unicamente para reconstruir el camino de una hoja podada
  # NO deben quedar como nodos vacios en el arbol final (ver bug encontrado en Sprint 3).
  kept_leaf_ids = {
    module_id for module_id in accessible_leaf_ids
    if module_id in by_id and chain_is_active(module_id)
  }

  included_ids: set[int] = set()

  for leaf_id in kept_leaf_ids:
    current_id = leaf_id

    while current_id is not None and current_id not in included_ids:
      included_ids.add(current_id)
      current_id = by_id[current_id].parent_id_module

  nodes = {
    module_id: {
      'id_module': row.id_module,
      'name_module': row.name_module,
      'url_module': row.url_module,
      'parent_id_module': row.parent_id_module,
      'children': [],
    }
    for module_id, row in by_id.items()
    if module_id in included_ids
  }

  roots = []

  for module_id, node in nodes.items():
    parent_id = node['parent_id_module']

    if parent_id in nodes:
      nodes[parent_id]['children'].append(node)
    else:
      roots.append(node)

  return roots
