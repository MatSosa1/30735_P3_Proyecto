from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import User, Role
from src.auth.password_service import PasswordService
from src.services.user_service import UserService


class UserController:
  # Create
  @staticmethod
  def create(db: Session, name: str, surname: str, username: str, password: str) -> User:
    new_user = User(
      name_user=name,
      surname_user=surname,
      username_user=username,
      password_user=PasswordService.generate_crypted_password(password)  # Hashed password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

  # Read
  @staticmethod
  def get_all(db: Session) -> list[User]:
    return UserService.get_all(db)

  @staticmethod
  def get_by_id(db: Session, user_id: int) -> User | None:
    return UserService.get_by_id(db, user_id)

  @staticmethod
  def get_by_username(db: Session, username: str) -> User | None:
    return UserService.get_by_username(db, username)

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
      user.password_user = PasswordService.generate_crypted_password(password)

    db.commit()
    db.refresh(user)

    return user

  @staticmethod
  def set_roles(db: Session, user_id: int, roles_id: list[int]) -> User | None:
    return UserService.set_roles(db, user_id, roles_id)

  # Delete
  @staticmethod
  def delete(db: Session, user_id: int) -> bool:
    user = db.get(User, user_id)

    if user is None:
      return False

    db.delete(user)
    db.commit()

    return True
