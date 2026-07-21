from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from pydantic import BaseModel

from src.routes.dependencies.dependencies import require_module
from src.controllers.role_controller import RoleController, RoleHasActiveUsersError
from src.db.session import get_db


# Auxiliary Classes
class RolePost(BaseModel):
  name: str


class RolePatch(BaseModel):
  name: str | None = None


class RoleAssignUser(BaseModel):
  user_id: int


class RoleAssignModule(BaseModel):
  module_id: int


router = APIRouter(
  prefix='/roles',
  tags=['Roles'],
  dependencies=[
    Depends(require_module(4))
  ]
)


# GET
@router.get(
  '/',
  status_code=status.HTTP_200_OK
)
def get_roles(
  db: Session = Depends(get_db)
):
  return RoleController.get_all(db)


@router.get(
  '/{role_id}',
  status_code=status.HTTP_200_OK
)
def get_role_by_id(
  role_id: int,
  db: Session = Depends(get_db)
):
  role = RoleController.get_by_id(
    db,
    role_id
  )

  if role is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Role not found'
    )

  return role


# POST
@router.post(
  '/',
  status_code=status.HTTP_201_CREATED
)
def post_role(
  role: RolePost,
  db: Session = Depends(get_db)
):
  return RoleController.create(
    db,
    role.name
  )


# UPDATE
@router.patch(
  '/{role_id}',
  status_code=status.HTTP_200_OK
)
def patch_role(
  role_id: int,
  role: RolePatch,
  db: Session = Depends(get_db)
):
  updated_role = RoleController.update(
    db=db,
    role_id=role_id,
    name=role.name
  )

  if updated_role is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Role not found'
    )

  return updated_role


# DELETE
@router.delete(
  '/{role_id}',
  status_code=status.HTTP_204_NO_CONTENT
)
def delete_role(
  role_id: int,
  db: Session = Depends(get_db)
):
  try:
    deleted = RoleController.delete(
      db,
      role_id
    )
  except RoleHasActiveUsersError:
    raise HTTPException(
      status_code=status.HTTP_409_CONFLICT,
      detail='No se puede eliminar un rol con usuarios activos asignados'
    )

  if not deleted:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Role not found'
    )

  return None


# ASSIGN USER
@router.post(
  '/{role_id}/users',
  status_code=status.HTTP_201_CREATED
)
def assign_user_to_role(
  role_id: int,
  payload: RoleAssignUser,
  db: Session = Depends(get_db)
):
  assignment = RoleController.assign_user(
    db,
    role_id,
    payload.user_id
  )

  if assignment is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Role or User not found'
    )

  return assignment


# UNASSIGN USER
@router.delete(
  '/{role_id}/users/{user_id}',
  status_code=status.HTTP_204_NO_CONTENT
)
def unassign_user_from_role(
  role_id: int,
  user_id: int,
  db: Session = Depends(get_db)
):
  deleted = RoleController.unassign_user(
    db,
    role_id,
    user_id
  )

  if not deleted:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Assignment not found'
    )

  return None


# ASSIGN MODULE
@router.post(
  '/{role_id}/modules',
  status_code=status.HTTP_201_CREATED
)
def assign_module_to_role(
  role_id: int,
  payload: RoleAssignModule,
  db: Session = Depends(get_db)
):
  assignment = RoleController.assign_module(
    db,
    role_id,
    payload.module_id
  )

  if assignment is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Role or Module not found'
    )

  return assignment


# ASSIGN MENU (item/submenu puntual — mismo modelo Module que /modules)
@router.post(
  '/{role_id}/menus',
  status_code=status.HTTP_201_CREATED
)
def assign_menu_to_role(
  role_id: int,
  payload: RoleAssignModule,
  db: Session = Depends(get_db)
):
  assignment = RoleController.assign_module(
    db,
    role_id,
    payload.module_id
  )

  if assignment is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Role or Module not found'
    )

  return assignment
