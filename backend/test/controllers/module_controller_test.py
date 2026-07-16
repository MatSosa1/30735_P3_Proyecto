from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.controllers.module_controller import ModuleController
from src.controllers.role_controller import RoleController
from src.models.models import Base


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

    assert ModuleController.get_by_id(
      self.db,
      created.id_module
    ) is None

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
