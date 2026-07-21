from fastapi.testclient import TestClient

from sqlalchemy.orm import Session, sessionmaker

from src.controllers.auth_controller import AuthController
from src.db.conn import engine
from main import app


SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)


class TestMenuRoutes:
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

  def test_get_no_token(self):
    response = self.client.get('/api/menus/tree')

    assert response.status_code == 401

  def test_get_menu_tree_for_seeded_role(self):
    response = self.client.get(
      '/api/menus/tree',
      headers=self.headers
    )

    assert response.status_code == 200

    tree = response.json()

    assert isinstance(tree, list)
    assert len(tree) > 0

    # El seed asigna al rol 1 (Vendedor) los items 4-7, hijos de 'Submenu 1'/'Submenu 2',
    # a su vez hijos de 'Menu' (id 1) — debe verse el árbol completo, no solo las hojas.
    root = tree[0]
    assert root['id_module'] == 1
    assert len(root['children']) > 0

    leaf_ids = set()

    def collect_leaf_ids(node):
      if not node['children']:
        leaf_ids.add(node['id_module'])
      for child in node['children']:
        collect_leaf_ids(child)

    for node in tree:
      collect_leaf_ids(node)

    assert leaf_ids == {4, 5, 6, 7}

  def test_get_menu_tree_end_to_end_with_fresh_role(self):
    # Construye un árbol propio (Menu > Submenu > Item) y un rol con acceso solo al item,
    # para verificar el flujo completo sin depender de los IDs del seed.
    root_response = self.client.post(
      '/api/modules/',
      json={'name': 'Tree Root', 'url': '', 'parent_id': None},
      headers=self.headers
    )
    root_id = root_response.json()['id_module']

    child_response = self.client.post(
      '/api/modules/',
      json={'name': 'Tree Child', 'url': '', 'parent_id': root_id},
      headers=self.headers
    )
    child_id = child_response.json()['id_module']

    item_response = self.client.post(
      '/api/modules/',
      json={'name': 'Tree Item', 'url': '/tree-item', 'parent_id': child_id},
      headers=self.headers
    )
    item_id = item_response.json()['id_module']

    role_response = self.client.post(
      '/api/roles/',
      json={'name': 'Tree Role'},
      headers=self.headers
    )
    role_id = role_response.json()['id_role']

    self.client.post(
      f'/api/roles/{role_id}/modules',
      json={'module_id': item_id},
      headers=self.headers
    )

    user_response = self.client.post(
      '/api/users/',
      json={
        'name': 'Tree',
        'surname': 'User',
        'username': 'tree_user_test',
        'password': 'Str0ngPass!'
      },
      headers=self.headers
    )
    user_id = user_response.json()['id_user']

    self.client.post(
      f'/api/roles/{role_id}/users',
      json={'user_id': user_id},
      headers=self.headers
    )

    token = AuthController.login(self.db, 'tree_user_test', 'Str0ngPass!', role_id)

    response = self.client.get(
      '/api/menus/tree',
      headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

    tree = response.json()

    assert tree == [{
      'id_module': root_id,
      'name_module': 'Tree Root',
      'url_module': '',
      'parent_id_module': None,
      'children': [{
        'id_module': child_id,
        'name_module': 'Tree Child',
        'url_module': '',
        'parent_id_module': root_id,
        'children': [{
          'id_module': item_id,
          'name_module': 'Tree Item',
          'url_module': '/tree-item',
          'parent_id_module': child_id,
          'children': [],
        }],
      }],
    }]

  def test_get_menu_tree_hides_subtree_of_inactive_parent(self):
    root_response = self.client.post(
      '/api/modules/',
      json={'name': 'Prune Root', 'url': '', 'parent_id': None},
      headers=self.headers
    )
    root_id = root_response.json()['id_module']

    child_response = self.client.post(
      '/api/modules/',
      json={'name': 'Prune Child', 'url': '', 'parent_id': root_id},
      headers=self.headers
    )
    child_id = child_response.json()['id_module']

    item_response = self.client.post(
      '/api/modules/',
      json={'name': 'Prune Item', 'url': '/prune-item', 'parent_id': child_id},
      headers=self.headers
    )
    item_id = item_response.json()['id_module']

    role_response = self.client.post(
      '/api/roles/',
      json={'name': 'Prune Role'},
      headers=self.headers
    )
    role_id = role_response.json()['id_role']

    self.client.post(
      f'/api/roles/{role_id}/modules',
      json={'module_id': item_id},
      headers=self.headers
    )

    user_response = self.client.post(
      '/api/users/',
      json={
        'name': 'Prune',
        'surname': 'User',
        'username': 'prune_user_test',
        'password': 'Str0ngPass!'
      },
      headers=self.headers
    )
    user_id = user_response.json()['id_user']

    self.client.post(
      f'/api/roles/{role_id}/users',
      json={'user_id': user_id},
      headers=self.headers
    )

    token = AuthController.login(self.db, 'prune_user_test', 'Str0ngPass!', role_id)

    # Se "elimina" (soft delete) el nodo intermedio -> el item deja de renderizarse
    self.client.delete(
      f'/api/modules/{child_id}',
      headers=self.headers
    )

    response = self.client.get(
      '/api/menus/tree',
      headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert response.json() == []
