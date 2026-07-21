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


class TestRoleRoutes:
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
  def test_get_no_token(self):
    response = self.client.get(
      '/api/roles/'
    )

    assert response.status_code == 401

  def test_get_all_roles(self):
    response = self.client.get(
      '/api/roles/',
      headers=self.headers
    )

    assert response.status_code == 200

    roles = response.json()

    assert isinstance(roles, list)


  # GET /{role_id}
  def test_get_role_by_id(self):
    response = self.client.get(
      '/api/roles/1',
      headers=self.headers
    )

    assert response.status_code == 200

    role = response.json()

    assert role['id_role'] == 1


  # GET /{role_id} - NOT FOUND
  def test_get_role_by_id_not_found(self):
    response = self.client.get(
      '/api/roles/999999',
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'Role not found'
    }


  # POST /
  def test_post_role(self):
    response = self.client.post(
      '/api/roles/',
      json={
        'name': 'Test Role'
      },
      headers=self.headers
    )

    assert response.status_code == 201

    role = response.json()

    assert role['id_role'] is not None
    assert role['name_role'] == 'Test Role'


  # PATCH /{role_id}
  def test_patch_role(self):
    create_response = self.client.post(
      '/api/roles/',
      json={
        'name': 'Role Before Update'
      },
      headers=self.headers
    )

    assert create_response.status_code == 201

    role_id = create_response.json()['id_role']

    response = self.client.patch(
      f'/api/roles/{role_id}',
      json={
        'name': 'Updated Role'
      },
      headers=self.headers
    )

    assert response.status_code == 200

    role = response.json()

    assert role['id_role'] == role_id
    assert role['name_role'] == 'Updated Role'


  # PATCH /{role_id} - NOT FOUND
  def test_patch_role_not_found(self):
    response = self.client.patch(
      '/api/roles/999999',
      json={
        'name': 'Updated Role'
      },
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'Role not found'
    }


  # DELETE /{role_id}
  def test_delete_role(self):
    create_response = self.client.post(
      '/api/roles/',
      json={
        'name': 'Role to Delete'
      },
      headers=self.headers
    )

    assert create_response.status_code == 201

    role_id = create_response.json()['id_role']

    response = self.client.delete(
      f'/api/roles/{role_id}',
      headers=self.headers
    )

    assert response.status_code == 204

    assert response.content == b''


  # DELETE /{role_id} - NOT FOUND
  def test_delete_role_not_found(self):
    response = self.client.delete(
      '/api/roles/999999',
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'Role not found'
    }
