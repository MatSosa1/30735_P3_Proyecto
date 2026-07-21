import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from pydantic import BaseModel, ConfigDict, field_validator

from src.routes.dependencies.dependencies import require_module
from src.controllers.user_controller import UserController
from src.db.session import get_db
from src.models.models import EstadoEnum


def validate_password_strength(value: str) -> str:
  if len(value) < 8:
    raise ValueError('La contraseña debe tener al menos 8 caracteres')

  if not re.search(r'[A-Z]', value):
    raise ValueError('La contraseña debe incluir al menos una letra mayúscula')

  if not re.search(r'[a-z]', value):
    raise ValueError('La contraseña debe incluir al menos una letra minúscula')

  if not re.search(r'\d', value):
    raise ValueError('La contraseña debe incluir al menos un número')

  return value


# Auxiliary Classes
class UserPost(BaseModel):
  name: str
  surname: str
  username: str
  password: str

  @field_validator('password')
  @classmethod
  def _validate_password(cls, value: str) -> str:
    return validate_password_strength(value)


class UserPatch(BaseModel):
  name: str | None = None
  surname: str | None = None
  username: str | None = None
  password: str | None = None

  @field_validator('password')
  @classmethod
  def _validate_password(cls, value: str | None) -> str | None:
    if value is None:
      return value

    return validate_password_strength(value)


# No incluye password_user: nunca se expone el hash de la contraseña en las respuestas
class UserOut(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id_user: int
  name_user: str
  surname_user: str
  username_user: str
  estado: EstadoEnum
  fecha_creacion: datetime
  fecha_actualizacion: datetime


router = APIRouter(
  prefix='/users',
  tags=['Users'],
  dependencies=[
    Depends(require_module(4))
  ]
)


# GET
@router.get(
  '/',
  status_code=status.HTTP_200_OK,
  response_model=list[UserOut]
)
def get_users(
  db: Session = Depends(get_db)
):
  return UserController.get_all(db)


@router.get(
  '/{user_id}',
  status_code=status.HTTP_200_OK,
  response_model=UserOut
)
def get_user_by_id(
  user_id: int,
  db: Session = Depends(get_db)
):
  user = UserController.get_by_id(
    db,
    user_id
  )

  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='User not found'
    )

  return user


# POST
@router.post(
  '/',
  status_code=status.HTTP_201_CREATED,
  response_model=UserOut
)
def post_user(
  user: UserPost,
  db: Session = Depends(get_db)
):
  return UserController.create(
    db,
    user.name,
    user.surname,
    user.username,
    user.password
  )


# UPDATE
@router.patch(
  '/{user_id}',
  status_code=status.HTTP_200_OK,
  response_model=UserOut
)
def patch_user(
  user_id: int,
  user: UserPatch,
  db: Session = Depends(get_db)
):
  updated_user = UserController.update(
    db=db,
    user_id=user_id,
    name=user.name,
    surname=user.surname,
    username=user.username,
    password=user.password
  )

  if updated_user is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='User not found'
    )

  return updated_user


# DELETE
@router.delete(
  '/{user_id}',
  status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(
  user_id: int,
  db: Session = Depends(get_db)
):
  deleted = UserController.delete(
    db,
    user_id
  )

  if not deleted:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail='User not found'
    )

  return None
