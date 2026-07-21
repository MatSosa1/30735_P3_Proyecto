from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from src.controllers.module_controller import ModuleController, ModuleCycleError
from src.controllers.role_controller import RoleController
from src.models.models import Base, EstadoEnum, Module


engine = create_engine(
  "sqlite:///:memory:",
  future=True,
)

SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)

Base.metadata.create_all(engine)


class TestModuleController:

  def setup_method(self):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    self.db: Session = SessionLocal()

  def teardown_method(self):
    self.db.close()

  def test_create_module(self):
    module = ModuleController.create(
      self.db,
      "Usuarios",
      "/users",
      None
    )

    assert module.id_module is not None
    assert module.name_module == "Usuarios"
    assert module.url_module == "/users"
    assert module.parent_id_module is None

  def test_get_all(self):
    ModuleController.create(
      self.db,
      "Usuarios",
      "/users",
      None
    )

    ModuleController.create(
      self.db,
      "Roles",
      "/roles",
      None
    )

    modules = ModuleController.get_all(self.db)

    assert len(modules) == 2

  def test_get_by_id(self):
    created = ModuleController.create(
      self.db,
      "Usuarios",
      "/users",
      None
    )

    module = ModuleController.get_by_id(
      self.db,
      created.id_module
    )

    assert module is not None
    assert module.id_module == created.id_module

  def test_update(self):
    created = ModuleController.create(
      self.db,
      "Usuarios",
      "/users",
      None
    )

    updated = ModuleController.update(
      self.db,
      created.id_module,
      name="Administración",
      url="/admin"
    )

    assert updated is not None
    assert updated.name_module == "Administración"
    assert updated.url_module == "/admin"

  def test_set_roles(self):
    role1 = RoleController.create(
      self.db,
      "Administrador"
    )

    role2 = RoleController.create(
      self.db,
      "Usuario"
    )

    module = ModuleController.create(
      self.db,
      "Usuarios",
      "/users",
      None
    )

    updated = ModuleController.set_roles(
      self.db,
      module.id_module,
      [role1.id_role, role2.id_role]
    )

    assert updated is not None
    assert len(updated.roles_module) == 2

    names = {role.name_role for role in updated.roles_module}

    assert names == {"Administrador", "Usuario"}

  def test_delete(self):
    created = ModuleController.create(
      self.db,
      "Usuarios",
      "/users",
      None
    )

    deleted = ModuleController.delete(
      self.db,
      created.id_module
    )

    assert deleted is True

    # No debe verse por el path público (filtro global estado=ACTIVO)...
    assert ModuleController.get_by_id(
      self.db,
      created.id_module
    ) is None

    # ...pero el registro debe seguir existiendo en BD con estado=INACTIVO (soft delete, no DELETE físico)
    still_exists = self.db.scalar(
      select(Module)
      .where(Module.id_module == created.id_module)
      .execution_options(include_inactive=True)
    )

    assert still_exists is not None
    assert still_exists.estado == EstadoEnum.INACTIVO

  def test_update_nonexistent_module(self):
    result = ModuleController.update(
      self.db,
      999,
      name="Nuevo"
    )

    assert result is None

  def test_delete_nonexistent_module(self):
    deleted = ModuleController.delete(
      self.db,
      999
    )

    assert deleted is False

  def test_get_all_empty(self):
    modules = ModuleController.get_all(self.db)

    assert modules == []

  def test_set_roles_nonexistent_module(self):
    role = RoleController.create(
      self.db,
      "Administrador"
    )

    result = ModuleController.set_roles(
      self.db,
      999,
      [role.id_role]
    )

    assert result is None

  # --- Anti-ciclo (parent_id_module) ---

  def test_update_parent_id_self_reference_is_rejected(self):
    module = ModuleController.create(self.db, "Menu", None, None)

    try:
      ModuleController.update(self.db, module.id_module, parent_id=module.id_module)
      assert False, "Expected ModuleCycleError"
    except ModuleCycleError:
      pass

  def test_update_parent_id_deep_cycle_is_rejected(self):
    root = ModuleController.create(self.db, "Menu", None, None)
    child = ModuleController.create(self.db, "Submenu", None, root.id_module)
    grandchild = ModuleController.create(self.db, "Item", "/item", child.id_module)

    # Intentar que 'root' pase a ser hijo de su propio nieto -> ciclo
    try:
      ModuleController.update(self.db, root.id_module, parent_id=grandchild.id_module)
      assert False, "Expected ModuleCycleError"
    except ModuleCycleError:
      pass

  def test_update_parent_id_valid_reparenting_is_allowed(self):
    root = ModuleController.create(self.db, "Menu", None, None)
    other_root = ModuleController.create(self.db, "Otro Menu", None, None)
    child = ModuleController.create(self.db, "Submenu", None, root.id_module)

    updated = ModuleController.update(self.db, child.id_module, parent_id=other_root.id_module)

    assert updated is not None
    assert updated.parent_id_module == other_root.id_module

  # --- Árbol de menú (GET /menus/tree) ---

  def test_menu_tree_for_role(self):
    root = ModuleController.create(self.db, "Menu", None, None)
    child = ModuleController.create(self.db, "Submenu", None, root.id_module)
    item = ModuleController.create(self.db, "Item 1", "/item1", child.id_module)

    role = RoleController.create(self.db, "Vendedor")
    RoleController.assign_module(self.db, role.id_role, item.id_module)

    tree = ModuleController.get_menu_tree(self.db, role.id_role)

    assert len(tree) == 1
    assert tree[0]['id_module'] == root.id_module
    assert len(tree[0]['children']) == 1
    assert tree[0]['children'][0]['id_module'] == child.id_module
    assert len(tree[0]['children'][0]['children']) == 1
    assert tree[0]['children'][0]['children'][0]['id_module'] == item.id_module

  def test_menu_tree_empty_for_role_without_modules(self):
    role = RoleController.create(self.db, "Visitante")

    tree = ModuleController.get_menu_tree(self.db, role.id_role)

    assert tree == []

  def test_menu_tree_hides_subtree_of_inactive_ancestor(self):
    root = ModuleController.create(self.db, "Menu", None, None)
    child = ModuleController.create(self.db, "Submenu", None, root.id_module)
    item = ModuleController.create(self.db, "Item 1", "/item1", child.id_module)

    role = RoleController.create(self.db, "Vendedor")
    RoleController.assign_module(self.db, role.id_role, item.id_module)

    # 'child' se inactiva (ej. se "elimina" el submenu) — 'item' sigue ACTIVO individualmente
    ModuleController.delete(self.db, child.id_module)

    tree = ModuleController.get_menu_tree(self.db, role.id_role)

    # El item queda oculto porque su ancestro ('child') esta INACTIVO, aunque el item
    # mismo siga ACTIVO — "al inactivar un módulo, sus menús asociados no deben renderizarse"
    assert tree == []
