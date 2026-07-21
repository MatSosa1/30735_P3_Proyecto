import enum
from datetime import datetime, UTC
from typing import List
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, event, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, Text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import with_loader_criteria


class Base(DeclarativeBase):
  pass


class EstadoEnum(str, enum.Enum):
  ACTIVO = 'ACTIVO'
  INACTIVO = 'INACTIVO'


# Standard de auditoria (Usuarios, Roles, Modulos): soft delete + timestamps + trazabilidad
class AuditMixin:
  estado: Mapped[EstadoEnum] = mapped_column(
    SQLEnum(EstadoEnum, name='estado_enum'),
    default=EstadoEnum.ACTIVO,
    server_default=EstadoEnum.ACTIVO.value,
    nullable=False,
  )
  fecha_creacion: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
  )
  fecha_actualizacion: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
  )

  @declared_attr
  def creado_por(cls) -> Mapped[Optional[int]]:
    return mapped_column(ForeignKey('Users.id_user'), nullable=True)

  @declared_attr
  def actualizado_por(cls) -> Mapped[Optional[int]]:
    return mapped_column(ForeignKey('Users.id_user'), nullable=True)

  def deactivate(self) -> None:
    self.estado = EstadoEnum.INACTIVO

  def activate(self) -> None:
    self.estado = EstadoEnum.ACTIVO


# Core Tables
class User(AuditMixin, Base):
  __tablename__ = 'Users'

  id_user: Mapped[int] = mapped_column(primary_key=True)
  name_user: Mapped[str] = mapped_column(String(20))
  surname_user: Mapped[str] = mapped_column(String(20))
  username_user: Mapped[str] = mapped_column(String(20))
  password_user: Mapped[str] = mapped_column(Text)

  user_roles: Mapped[List['UserRole']] = relationship(back_populates='user')

  roles_user = association_proxy('user_roles', 'role')

class Role(AuditMixin, Base):
  __tablename__ = 'Roles'

  id_role: Mapped[int] = mapped_column(primary_key=True)
  name_role: Mapped[str] = mapped_column(String(20))

  role_users: Mapped[List['UserRole']] = relationship(back_populates='role')
  role_modules: Mapped[List['RoleModule']] = relationship(back_populates='role')

  users_role = association_proxy('role_users', 'user')
  modules_role = association_proxy('role_modules', 'module')

class Module(AuditMixin, Base):
  __tablename__ = 'Modules'

  id_module: Mapped[int] = mapped_column(primary_key=True)
  name_module: Mapped[str] = mapped_column(String(20))
  url_module: Mapped[Optional[str]] = mapped_column(Text)
  parent_id_module: Mapped[Optional[int]] = mapped_column(ForeignKey("Modules.id_module"))

  module_roles: Mapped[List['RoleModule']] = relationship(back_populates='module')

  roles_module = association_proxy('module_roles', 'role')

  parent = relationship(
    'Module',
    remote_side=[id_module],
    back_populates='children'
  )

  children = relationship(
    'Module',
    back_populates='parent'
  )


# Relations (association objects: heredan estado/fecha_creacion propios, ver notas de auditoria del spec)
class UserRole(Base):
  __tablename__ = 'Users_Roles'

  id_user: Mapped[int] = mapped_column(ForeignKey('Users.id_user'), primary_key=True)
  id_role: Mapped[int] = mapped_column(ForeignKey('Roles.id_role'), primary_key=True)

  estado: Mapped[EstadoEnum] = mapped_column(
    SQLEnum(EstadoEnum, name='estado_enum'),
    default=EstadoEnum.ACTIVO,
    server_default=EstadoEnum.ACTIVO.value,
    nullable=False,
  )
  fecha_creacion: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
  )

  user: Mapped['User'] = relationship(back_populates='user_roles')
  role: Mapped['Role'] = relationship(back_populates='role_users')

class RoleModule(Base):
  __tablename__ = 'Roles_Modules'

  id_role: Mapped[int] = mapped_column(ForeignKey('Roles.id_role'), primary_key=True)
  id_module: Mapped[int] = mapped_column(ForeignKey('Modules.id_module'), primary_key=True)

  estado: Mapped[EstadoEnum] = mapped_column(
    SQLEnum(EstadoEnum, name='estado_enum'),
    default=EstadoEnum.ACTIVO,
    server_default=EstadoEnum.ACTIVO.value,
    nullable=False,
  )
  fecha_creacion: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
  )

  role: Mapped['Role'] = relationship(back_populates='role_modules')
  module: Mapped['Module'] = relationship(back_populates='module_roles')


# Hook de auditoria: fecha_creacion/fecha_actualizacion son manejadas exclusivamente por el ORM,
# nunca por el controlador (se sobreescriben aqui sin importar lo que el controlador haya asignado).
@event.listens_for(Session, 'before_flush')
def _stamp_audit_fields(session, flush_context, instances):
  now = datetime.now(UTC)

  for obj in session.new:
    if isinstance(obj, AuditMixin):
      obj.fecha_creacion = now
      obj.fecha_actualizacion = now

      if obj.estado is None:
        obj.estado = EstadoEnum.ACTIVO

  for obj in session.dirty:
    if isinstance(obj, AuditMixin) and session.is_modified(obj, include_collections=False):
      obj.fecha_actualizacion = now


# Filtro global (Global Scope): las entidades auditadas nunca se leen si estan INACTIVO, salvo
# que se pida explicitamente via execution_options(include_inactive=True).
_SOFT_DELETE_ENTITIES = (User, Role, Module, UserRole, RoleModule)

@event.listens_for(Session, 'do_orm_execute')
def _filter_estado_activo(orm_execute_state):
  if not orm_execute_state.is_select:
    return

  if orm_execute_state.execution_options.get('include_inactive', False):
    return

  for entity in _SOFT_DELETE_ENTITIES:
    orm_execute_state.statement = orm_execute_state.statement.options(
      with_loader_criteria(entity, entity.estado == EstadoEnum.ACTIVO, include_aliases=True)
    )
