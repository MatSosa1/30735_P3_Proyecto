from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from pydantic import BaseModel

from src.routes.dependencies.dependencies import require_module
from src.controllers.user_controller import UserController
from src.db.session import get_db


# Auxiliary Classes
class UserPost(BaseModel):
  name: str
  surname: str
  username: str
  password: str


class UserPatch(BaseModel):
  name: str | None = None
  surname: str | None = None
  username: str | None = None
  password: str | None = None


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
  status_code=status.HTTP_200_OK
)
def get_users(
  db: Session = Depends(get_db)
):
  return UserController.get_all(db)


@router.get(
  '/{user_id}',
  status_code=status.HTTP_200_OK
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
  status_code=status.HTTP_201_CREATED
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
  status_code=status.HTTP_200_OK
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
