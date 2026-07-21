import pytest

from fastapi.testclient import TestClient

from sqlalchemy.orm import Session, sessionmaker

from src.controllers.auth_controller import AuthController
from src.db.conn import engine
from main import app


SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)


class TestUserRoutes:
  client = TestClient(app)

  def setup_method(self):
    self.db: Session = SessionLocal()

    token = AuthController.login(
      self.db,
      'msosa',
      '1234',
      1
    )

    self.headers = {
      'Authorization': f'Bearer {token}'
    }

  def teardown_method(self):
    self.db.close()


  # GET /
  def test_get_all_users(self):
    response = self.client.get(
      '/api/users/',
      headers=self.headers
    )

    assert response.status_code == 200

    users = response.json()

    assert isinstance(users, list)


  # GET /{user_id}
  def test_get_user_by_id(self):
    response = self.client.get(
      '/api/users/1',
      headers=self.headers
    )

    assert response.status_code == 200

    user = response.json()

    assert user['id_user'] == 1


  # GET /{user_id} - NOT FOUND
  def test_get_user_by_id_not_found(self):
    response = self.client.get(
      '/api/users/999999',
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'User not found'
    }


  # POST /
  def test_post_user(self):
    response = self.client.post(
      '/api/users/',
      json={
        'name': 'Test',
        'surname': 'User',
        'username': 'test_user_routes',
        'password': '1234'
      },
      headers=self.headers
    )

    assert response.status_code == 201

    user = response.json()

    assert user['id_user'] is not None
    assert user['name_user'] == 'Test'
    assert user['surname_user'] == 'User'
    assert user['username_user'] == 'test_user_routes'


  # PATCH /{user_id}
  def test_patch_user(self):
    create_response = self.client.post(
      '/api/users/',
      json={
        'name': 'User',
        'surname': 'Before Update',
        'username': 'user_before_update',
        'password': '1234'
      },
      headers=self.headers
    )

    assert create_response.status_code == 201

    user_id = create_response.json()['id_user']

    response = self.client.patch(
      f'/api/users/{user_id}',
      json={
        'name': 'Updated User'
      },
      headers=self.headers
    )

    assert response.status_code == 200

    user = response.json()

    assert user['id_user'] == user_id
    assert user['name_user'] == 'Updated User'


  # PATCH /{user_id} - NOT FOUND
  def test_patch_user_not_found(self):
    response = self.client.patch(
      '/api/users/999999',
      json={
        'name': 'Updated User'
      },
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'User not found'
    }


  # DELETE /{user_id}
  def test_delete_user(self):
    create_response = self.client.post(
      '/api/users/',
      json={
        'name': 'User',
        'surname': 'To Delete',
        'username': 'user_to_delete',
        'password': '1234'
      },
      headers=self.headers
    )

    assert create_response.status_code == 201

    user_id = create_response.json()['id_user']

    response = self.client.delete(
      f'/api/users/{user_id}',
      headers=self.headers
    )

    assert response.status_code == 204

    assert response.content == b''


  # DELETE /{user_id} - NOT FOUND
  def test_delete_user_not_found(self):
    response = self.client.delete(
      '/api/users/999999',
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'User not found'
    }
