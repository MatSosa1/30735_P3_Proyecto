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
