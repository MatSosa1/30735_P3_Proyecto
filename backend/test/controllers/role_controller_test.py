from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from src.controllers.module_controller import ModuleController
from src.controllers.role_controller import RoleController, RoleHasActiveUsersError
from src.controllers.user_controller import UserController
from src.models.models import Base, EstadoEnum, Role, RoleModule, UserRole


engine = create_engine(
  "sqlite:///:memory:",
  future=True,
)

SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)

Base.metadata.create_all(engine)


class TestRoleController:

  def setup_method(self):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    self.db: Session = SessionLocal()

  def teardown_method(self):
    self.db.close()

  def test_create_role(self):
    role = RoleController.create(
      self.db,
      "Administrador"
    )

    assert role.id_role is not None
    assert role.name_role == "Administrador"

  def test_get_all(self):
    RoleController.create(
      self.db,
      "Administrador"
    )

    RoleController.create(
      self.db,
      "Usuario"
    )

    roles = RoleController.get_all(self.db)

    assert len(roles) == 2

    names = {role.name_role for role in roles}

    assert names == {"Administrador", "Usuario"}

  def test_get_by_id(self):
    created = RoleController.create(
      self.db,
      "Administrador"
    )

    role = RoleController.get_by_id(
      self.db,
      created.id_role
    )

    assert role is not None
    assert role.id_role == created.id_role

  def test_get_by_name(self):
    RoleController.create(
      self.db,
      "Administrador"
    )

    role = RoleController.get_by_name(
      self.db,
      "Administrador"
    )

    assert role is not None
    assert role.name_role == "Administrador"

  def test_update(self):
    created = RoleController.create(
      self.db,
      "Administrador"
    )

    updated = RoleController.update(
      self.db,
      created.id_role,
      name="Super Administrador"
    )

    assert updated is not None
    assert updated.name_role == "Super Administrador"

  def test_delete(self):
    created = RoleController.create(
      self.db,
      "Administrador"
    )

    deleted = RoleController.delete(
      self.db,
      created.id_role
    )

    assert deleted is True

    # No debe verse por el path público (filtro global estado=ACTIVO)...
    assert RoleController.get_by_id(
      self.db,
      created.id_role
    ) is None

    # ...pero el registro debe seguir existiendo en BD con estado=INACTIVO (soft delete, no DELETE físico)
    still_exists = self.db.scalar(
      select(Role)
      .where(Role.id_role == created.id_role)
      .execution_options(include_inactive=True)
    )

    assert still_exists is not None
    assert still_exists.estado == EstadoEnum.INACTIVO

  def test_delete_role_with_active_users_is_rejected(self):
    role = RoleController.create(
      self.db,
      "Administrador"
    )

    user = UserController.create(
      self.db,
      "Mateo",
      "Sosa",
      "msosa",
      "1234"
    )

    self.db.add(UserRole(id_user=user.id_user, id_role=role.id_role))
    self.db.commit()

    try:
      RoleController.delete(self.db, role.id_role)
      assert False, "Expected RoleHasActiveUsersError"
    except RoleHasActiveUsersError:
      pass

    # El rol no debe haberse desactivado
    assert RoleController.get_by_id(self.db, role.id_role) is not None

  def test_update_nonexistent_role(self):
    result = RoleController.update(
      self.db,
      999,
      name="Nuevo"
    )

    assert result is None

  def test_delete_nonexistent_role(self):
    deleted = RoleController.delete(
      self.db,
      999
    )

    assert deleted is False

  def test_get_all_empty(self):
    roles = RoleController.get_all(self.db)

    assert roles == []

  def test_get_by_name_nonexistent(self):
    role = RoleController.get_by_name(
      self.db,
      "NoExiste"
    )

    assert role is None

  def test_assign_user(self):
    role = RoleController.create(self.db, "Administrador")
    user = UserController.create(self.db, "Mateo", "Sosa", "msosa", "1234")

    assignment = RoleController.assign_user(self.db, role.id_role, user.id_user)

    assert assignment is not None
    assert assignment.id_role == role.id_role
    assert assignment.id_user == user.id_user
    assert assignment.estado == EstadoEnum.ACTIVO

  def test_assign_user_reactivates_existing_inactive_assignment(self):
    role = RoleController.create(self.db, "Administrador")
    user = UserController.create(self.db, "Mateo", "Sosa", "msosa", "1234")

    assignment = RoleController.assign_user(self.db, role.id_role, user.id_user)
    # UserRole no hereda AuditMixin (no tiene .deactivate()); se asigna estado directo
    assignment.estado = EstadoEnum.INACTIVO
    self.db.commit()

    reactivated = RoleController.assign_user(self.db, role.id_role, user.id_user)

    assert reactivated is not None
    assert reactivated.id_user == user.id_user
    assert reactivated.estado == EstadoEnum.ACTIVO

  def test_assign_user_nonexistent_role_or_user(self):
    role = RoleController.create(self.db, "Administrador")

    assert RoleController.assign_user(self.db, role.id_role, 999) is None
    assert RoleController.assign_user(self.db, 999, 1) is None

  def test_unassign_user(self):
    role = RoleController.create(self.db, "Administrador")
    user = UserController.create(self.db, "Mateo", "Sosa", "msosa", "1234")

    RoleController.assign_user(self.db, role.id_role, user.id_user)

    deleted = RoleController.unassign_user(self.db, role.id_role, user.id_user)

    assert deleted is True

    still_exists = self.db.scalar(
      select(UserRole)
      .where(UserRole.id_role == role.id_role, UserRole.id_user == user.id_user)
      .execution_options(include_inactive=True)
    )

    # A diferencia de Usuarios/Roles/Modulos, esta desasignacion es fisica de verdad
    assert still_exists is None

  def test_unassign_user_nonexistent(self):
    role = RoleController.create(self.db, "Administrador")

    assert RoleController.unassign_user(self.db, role.id_role, 999) is False

  def test_assign_module(self):
    role = RoleController.create(self.db, "Administrador")
    module = ModuleController.create(self.db, "Usuarios", "/users", None)

    assignment = RoleController.assign_module(self.db, role.id_role, module.id_module)

    assert assignment is not None
    assert assignment.id_role == role.id_role
    assert assignment.id_module == module.id_module
    assert assignment.estado == EstadoEnum.ACTIVO

  def test_assign_module_nonexistent_role_or_module(self):
    role = RoleController.create(self.db, "Administrador")

    assert RoleController.assign_module(self.db, role.id_role, 999) is None
    assert RoleController.assign_module(self.db, 999, 1) is None
