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


class TestModuleRoutes:
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

  # GET /{module_id}
  def test_get_module_by_id(self):
    response = self.client.get(
      '/api/modules/4',
      headers=self.headers
    )

    assert response.status_code == 200

    module = response.json()

    assert module['id_module'] == 4


  # GET /{module_id} - NOT FOUND
  def test_get_module_by_id_not_found(self):
    response = self.client.get(
      '/api/modules/999999',
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'Module not found'
    }


  # POST /
  def test_post_module(self):
    response = self.client.post(
      '/api/modules/',
      json={
        'name': 'Test Module',
        'url': '/test-module',
        'parent_id': None
      },
      headers=self.headers
    )

    assert response.status_code == 201

    module = response.json()

    assert module['name_module'] == 'Test Module'
    assert module['url_module'] == '/test-module'
    assert module['parent_id_module'] is None


  # PATCH /{module_id}
  def test_patch_module(self):
    response = self.client.patch(
      '/api/modules/4',
      json={
        'name': 'Updated Module'
      },
      headers=self.headers
    )

    assert response.status_code == 200

    module = response.json()

    assert module['id_module'] == 4
    assert module['name_module'] == 'Updated Module'


  # PATCH /{module_id} - NOT FOUND
  def test_patch_module_not_found(self):
    response = self.client.patch(
      '/api/modules/999999',
      json={
        'name': 'Updated Module'
      },
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'Module not found'
    }


  # PUT /{module_id}/roles
  def test_put_module_roles(self):
    response = self.client.put(
      '/api/modules/4/roles',
      json={
        'roles_id': [1]
      },
      headers=self.headers
    )

    assert response.status_code == 200

    module = response.json()

    assert module['id_module'] == 4


  # PUT /{module_id}/roles - NOT FOUND
  def test_put_module_roles_not_found(self):
    response = self.client.put(
      '/api/modules/999999/roles',
      json={
        'roles_id': [1]
      },
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'Module not found'
    }


  # DELETE /{module_id}
  def test_delete_module(self):
    create_response = self.client.post(
      '/api/modules/',
      json={
        'name': 'Module to Delete',
        'url': '/module-to-delete',
        'parent_id': None
      },
      headers=self.headers
    )

    assert create_response.status_code == 201

    module_id = create_response.json()['id_module']

    response = self.client.delete(
      f'/api/modules/{module_id}',
      headers=self.headers
    )

    assert response.status_code == 204

    assert response.content == b''


  # DELETE /{module_id} - NOT FOUND
  def test_delete_module_not_found(self):
    response = self.client.delete(
      '/api/modules/999999',
      headers=self.headers
    )

    assert response.status_code == 404

    assert response.json() == {
      'detail': 'Module not found'
    }
