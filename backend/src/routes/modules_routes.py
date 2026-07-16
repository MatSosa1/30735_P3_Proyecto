from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from pydantic import BaseModel

from src.routes.dependencies.dependencies import require_module
from src.controllers.module_controller import ModuleController
from src.db.session import get_db


# Auxiliary Classes
class ModulePost(BaseModel):
  name: str
  url: str
  parent_id: int | None = None


class ModulePatch(BaseModel):
  name: str | None = None
  url: str | None = None
  parent_id: int | None = None


class ModuleRoles(BaseModel):
  roles_id: list[int]


router = APIRouter(
  prefix='/modules',
  tags=['Modules'],
  dependencies=[
    Depends(require_module(4))
  ]
)


# GET
@router.get('/')
def get_modules(
  db: Session = Depends(get_db)
):
  return ModuleController.get_all(db)


@router.get('/{module_id}')
def get_module_by_id(
  module_id: int,
  db: Session = Depends(get_db)
):
  module = ModuleController.get_by_id(db, module_id)

  if module is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Module not found'
    )

  return module


# POST
@router.post('/', status_code=status.HTTP_201_CREATED)
def post_module(
  module: ModulePost,
  db: Session = Depends(get_db)
):
  return ModuleController.create(
    db=db,
    name=module.name,
    url=module.url,
    parent_id=module.parent_id
  )


# UPDATE
@router.patch('/{module_id}')
def patch_module(
  module_id: int,
  module: ModulePatch,
  db: Session = Depends(get_db)
):
  updated_module = ModuleController.update(
    db=db,
    module_id=module_id,
    name=module.name,
    url=module.url,
    parent_id=module.parent_id
  )

  if updated_module is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Module not found'
    )

  return updated_module


# SET ROLES
@router.put('/{module_id}/roles')
def put_module_roles(
  module_id: int,
  roles: ModuleRoles,
  db: Session = Depends(get_db)
):
  module = ModuleController.set_roles(
    db=db,
    module_id=module_id,
    roles_id=roles.roles_id
  )

  if module is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Module not found'
    )

  return module


# DELETE
@router.delete('/{module_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
  module_id: int,
  db: Session = Depends(get_db),
  
):
  deleted = ModuleController.delete(db, module_id)

  if not deleted:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='Module not found'
    )

  return {
    'message': 'Module deleted successfully'
  }
