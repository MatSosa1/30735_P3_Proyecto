from sqlalchemy.orm import Session
from sqlalchemy import select

import bcrypt

from src.models.models import User, Role


class UserController:
  # Create
  @staticmethod
  def create(db: Session, name: str, surname: str, username: str, password: str) -> User:
    hashed = bcrypt.hashpw(
      password.encode('utf-8'),
      bcrypt.gensalt()
    )

    new_user = User(
      name_user=name,
      surname_user=surname,
      username_user=username,
      password_user=hashed.decode('utf-8')  # Hashed password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

  # Read
  @staticmethod
  def get_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

  @staticmethod
  def get_by_username(db: Session, username: str) -> User | None:
    select_statement = select(User).where(User.username_user == username)

    return db.scalar(select_statement)

  # Update
  @staticmethod
  def update(db: Session, user_id: int, name: str | None = None, surname: str | None = None, username: str | None = None, password: str | None = None,) -> User | None:
    user = db.get(User, user_id)

    if not user:  # Not found
      return None

    # POST / PATCH
    if name is not None:
      user.name_user = name

    if surname is not None:
      user.surname_user = surname

    if username is not None:
      user.username_user = username

    if password is not None:
      hashed = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
      )

      user.password_user = hashed.decode('utf-8')

    db.commit()
    db.refresh(user)

    return user

  @staticmethod
  def set_roles(db: Session, user_id: int, roles_id: list[int]) -> User | None:
    user = db.get(User, user_id)

    if not user:
      return None

    roles_select_statement = select(Role).where(Role.id_role.in_(roles_id))
    roles = list(db.scalars(roles_select_statement).all())

    user.roles_user = roles

    db.commit()
    db.refresh(user)

    return user

  # Delete
  @staticmethod
  def delete(db: Session, user_id: int) -> bool:
    user = db.get(User, user_id)

    if user is None:
      return False

    db.delete(user)
    db.commit()

    return True
