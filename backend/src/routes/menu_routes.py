from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from src.controllers.module_controller import ModuleController
from src.controllers.role_controller import RoleController
from src.db.session import get_db
from src.routes.dependencies.dependencies import verify_token


router = APIRouter(
  prefix='/menus',
  tags=['Menus']
)


@router.get('/tree')
def get_menu_tree(
  token_data = Depends(verify_token),
  db: Session = Depends(get_db)
):
  role_id = int(token_data['role'])

  # El rol pudo haberse inactivado despues de emitido el JWT; RoleController.get_by_id ya
  # respeta el filtro global de estado=ACTIVO.
  role = RoleController.get_by_id(db, role_id)

  if not role:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail='Rol inválido'
    )

  return ModuleController.get_menu_tree(db, role_id)
