from typing import List
from typing import Optional

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
  pass


# Relations
users_roles = Table(
  'Users_Roles',
  Base.metadata,
  Column('id_user', ForeignKey('Users.id_user'), primary_key=True),
  Column('id_role', ForeignKey('Roles.id_role'), primary_key=True),
)

roles_modules = Table(
  'Roles_Modules',
  Base.metadata,
  Column('id_role', ForeignKey('Roles.id_role'), primary_key=True),
  Column('id_module', ForeignKey('Modules.id_module'), primary_key=True),
)


# Core Tables
class User(Base):
  __tablename__ = 'Users'

  id_user: Mapped[int] = mapped_column(primary_key=True)
  name_user: Mapped[str] = mapped_column(String(20))
  surname_user: Mapped[str] = mapped_column(String(20))
  username_user: Mapped[str] = mapped_column(String(20))
  password_user: Mapped[str] = mapped_column(Text)

  roles_user: Mapped[List['Role']] = relationship(
    secondary=users_roles,
    back_populates="users_role"
  )

class Role(Base):
  __tablename__ = 'Roles'

  id_role: Mapped[int] = mapped_column(primary_key=True)
  name_role: Mapped[str] = mapped_column(String(20))

  users_role: Mapped[List['User']] = relationship(
    secondary=users_roles,
    back_populates='roles_user'
  )
  modules_role: Mapped[List['Module']] = relationship(
    secondary=roles_modules,
    back_populates='roles_module'
  )

class Module(Base):
  __tablename__ = 'Modules'

  id_module: Mapped[int] = mapped_column(primary_key=True)
  name_module: Mapped[str] = mapped_column(String(20))
  url_module: Mapped[Optional[str]] = mapped_column(Text)
  parent_id_module: Mapped[Optional[int]] = mapped_column(ForeignKey("Modules.id_module"))

  roles_module: Mapped[List['Role']] = relationship(
    secondary=roles_modules,
    back_populates='modules_role'
  )

  parent = relationship(
    'Module',
    remote_side=[id_module],
    back_populates='children'
  )

  children = relationship(
    'Module',
    back_populates='parent'
  )
