from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.models.models import Base, Role
from src.controllers.user_controller import UserController


engine = create_engine(
  "sqlite:///:memory:",
  future=True,
)

SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)

Base.metadata.create_all(engine)


class TestUserController:
  def setup_method(self):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    self.db: Session = SessionLocal()

  def teardown_method(self):
    self.db.close()

  def test_create_user(self):
    user = UserController.create(
      self.db,
      name="Mateo",
      surname="Sosa",
      username="msosa",
      password="1234"
    )

    assert user.id_user is not None
    assert user.name_user == "Mateo"
    assert user.surname_user == "Sosa"
    assert user.username_user == "msosa"

  def test_get_by_id(self):
    created = UserController.create(
      self.db,
      "Mateo",
      "Sosa",
      "msosa",
      "1234"
    )

    user = UserController.get_by_id(
      self.db,
      created.id_user
    )

    assert user is not None
    assert user.id_user == created.id_user

  def test_get_by_username(self):
    UserController.create(
      self.db,
      "Mateo",
      "Sosa",
      "msosa",
      "1234"
    )

    user = UserController.get_by_username(
      self.db,
      "msosa"
    )

    assert user is not None
    assert user.username_user == "msosa"

  def test_update(self):
    created = UserController.create(
      self.db,
      "Mateo",
      "Sosa",
      "msosa",
      "1234"
    )

    updated = UserController.update(
      self.db,
      created.id_user,
      surname="Perez"
    )

    assert updated is not None
    assert updated.surname_user == "Perez"

  def test_delete(self):
    created = UserController.create(
      self.db,
      "Mateo",
      "Sosa",
      "msosa",
      "1234"
    )

    deleted = UserController.delete(
      self.db,
      created.id_user
    )

    assert deleted is True

    assert UserController.get_by_id(
      self.db,
      created.id_user
    ) is None

  def test_set_roles(self):
    role1 = Role(name_role="Admin")
    role2 = Role(name_role="User")

    self.db.add_all([role1, role2])
    self.db.commit()

    user = UserController.create(
      self.db,
      "Mateo",
      "Sosa",
      "msosa",
      "1234"
    )

    updated = UserController.set_roles(
      self.db,
      user.id_user,
      [role1.id_role, role2.id_role]
    )

    assert updated is not None
    assert len(updated.roles_user) == 2

    names = {r.name_role for r in updated.roles_user}

    assert names == {"Admin", "User"}

  def test_update_nonexistent_user(self):
    result = UserController.update(
      self.db,
      999,
      name="Nuevo"
    )

    assert result is None

  def test_delete_nonexistent_user(self):
    assert UserController.delete(
      self.db,
      999
    ) is False

  def test_set_roles_nonexistent_user(self):
    role = Role(name_role="Admin")

    self.db.add(role)
    self.db.commit()

    result = UserController.set_roles(
      self.db,
      999,
      [role.id_role]
    )

    assert result is None
