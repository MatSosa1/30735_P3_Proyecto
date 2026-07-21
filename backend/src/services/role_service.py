from sqlalchemy.orm import Session
from sqlalchemy import select

from src.models.models import EstadoEnum, Role, RoleModule, User, UserRole
from src.services.module_service import ModuleService
from src.services.user_service import UserService


class RoleService:
  @staticmethod
  def get_all(db: Session) -> list[Role]:
    return list(db.scalars(select(Role)).all())

  @staticmethod
  def get_by_id(db: Session, role_id: int) -> Role | None:
    # select() (a diferencia de db.get()) siempre respeta el filtro global de estado=ACTIVO,
    # incluso si el objeto ya está en el identity map de la sesión.
    return db.scalar(select(Role).where(Role.id_role == role_id))

  @staticmethod
  def get_by_name(db: Session, name: str) -> Role | None:
    select_statement = select(Role).where(Role.name_role == name)

    return db.scalar(select_statement)

  @staticmethod
  def has_active_users(db: Session, role_id: int) -> bool:
    # El filtro global de estado=ACTIVO ya excluye usuarios/asignaciones inactivas de esta query
    select_statement = select(UserRole).join(User).where(UserRole.id_role == role_id)

    return db.scalar(select_statement) is not None

  # Asigna un usuario existente a un rol (POST /roles/{id}/users). Si la asignación ya existía
  # pero estaba inactiva (revocada), la reactiva en vez de duplicarla.
  @staticmethod
  def assign_user(db: Session, role_id: int, user_id: int) -> UserRole | None:
    role = RoleService.get_by_id(db, role_id)
    user = UserService.get_by_id(db, user_id)

    if not role or not user:
      return None

    existing = db.scalar(
      select(UserRole)
      .where(UserRole.id_role == role_id, UserRole.id_user == user_id)
      .execution_options(include_inactive=True)
    )

    if existing:
      if existing.estado == EstadoEnum.INACTIVO:
        # UserRole/RoleModule no heredan AuditMixin: no tienen .activate()/.deactivate()
        existing.estado = EstadoEnum.ACTIVO
        db.commit()

      return existing

    user_role = UserRole(id_role=role_id, id_user=user_id)

    db.add(user_role)
    db.commit()
    db.refresh(user_role)

    return user_role

  # Desasigna un usuario de un rol (DELETE /roles/{id}/users/{userId}). El spec permite
  # explícitamente eliminación física en este caso puntual de la tabla pivote.
  @staticmethod
  def unassign_user(db: Session, role_id: int, user_id: int) -> bool:
    user_role = db.scalar(
      select(UserRole)
      .where(UserRole.id_role == role_id, UserRole.id_user == user_id)
      .execution_options(include_inactive=True)
    )

    if not user_role:
      return False

    db.delete(user_role)
    db.commit()

    return True

  # Asigna un módulo (o item/submenú puntual, mismo modelo Module) a un rol, desde el lado
  # de "roles" (POST /roles/{id}/modules y POST /roles/{id}/menus). Simétrico a
  # ModuleService.set_roles, que hace lo mismo desde el lado de "modules".
  @staticmethod
  def assign_module(db: Session, role_id: int, module_id: int) -> RoleModule | None:
    role = RoleService.get_by_id(db, role_id)
    module = ModuleService.get_by_id(db, module_id)

    if not role or not module:
      return None

    existing = db.scalar(
      select(RoleModule)
      .where(RoleModule.id_role == role_id, RoleModule.id_module == module_id)
      .execution_options(include_inactive=True)
    )

    if existing:
      if existing.estado == EstadoEnum.INACTIVO:
        # UserRole/RoleModule no heredan AuditMixin: no tienen .activate()/.deactivate()
        existing.estado = EstadoEnum.ACTIVO
        db.commit()

      return existing

    role_module = RoleModule(id_role=role_id, id_module=module_id)

    db.add(role_module)
    db.commit()
    db.refresh(role_module)

    return role_module
