from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker

from fastapi.testclient import TestClient

from src.controllers.auth_controller import AuthController
from src.db.conn import engine
from main import app


SessionLocal = sessionmaker(
  bind=engine,
  expire_on_commit=False,
)


class TestMenuTreePerformance:
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

  # Crea una cadena lineal Modulo -> Modulo -> ... -> hoja de profundidad `depth`; retorna el id
  # de la hoja (unico nodo con url_module, para que el rol pueda apuntarle al menu real).
  def _build_chain(self, depth: int, prefix: str) -> int:
    parent_id = None
    leaf_id = None

    for level in range(depth):
      is_leaf = level == depth - 1

      response = self.client.post(
        '/api/modules/',
        json={
          'name': f'{prefix}-{level}',
          'url': f'/{prefix}-leaf' if is_leaf else '',
          'parent_id': parent_id,
        },
        headers=self.headers
      )
      leaf_id = response.json()['id_module']
      parent_id = leaf_id

    return leaf_id

  def _role_with_access(self, name: str, module_id: int) -> str:
    role_response = self.client.post(
      '/api/roles/',
      json={'name': name},
      headers=self.headers
    )
    role_id = role_response.json()['id_role']

    self.client.post(
      f'/api/roles/{role_id}/modules',
      json={'module_id': module_id},
      headers=self.headers
    )

    username = f"perf_{name.lower().replace(' ', '_')}"

    user_response = self.client.post(
      '/api/users/',
      json={
        'name': 'Perf',
        'surname': 'User',
        'username': username,
        'password': 'Str0ngPass!',
      },
      headers=self.headers
    )
    user_id = user_response.json()['id_user']

    self.client.post(
      f'/api/roles/{role_id}/users',
      json={'user_id': user_id},
      headers=self.headers
    )

    return AuthController.login(self.db, username, 'Str0ngPass!', role_id)

  def _count_queries_for_menu_tree(self, token: str) -> int:
    queries: list[str] = []

    def _listener(conn, cursor, statement, parameters, context, executemany):
      queries.append(statement)

    event.listen(engine, 'before_cursor_execute', _listener)

    try:
      response = self.client.get(
        '/api/menus/tree',
        headers={'Authorization': f'Bearer {token}'}
      )
      assert response.status_code == 200
      assert response.json() != []
    finally:
      event.remove(engine, 'before_cursor_execute', _listener)

    return len(queries)

  # Regresion de performance (§6.4): GET /api/menus/tree usa una unica CTE recursiva
  # (ModuleService.get_menu_ancestor_closure), no recorre la cadena de ancestros nodo por nodo.
  # Si alguien lo reescribiera con un loop en Python haciendo un SELECT por nivel (N+1), este test
  # lo detectaria porque la cantidad de queries dejaria de ser constante frente a la profundidad.
  def test_menu_tree_query_count_does_not_grow_with_depth(self):
    shallow_leaf = self._build_chain(depth=3, prefix='shallow')
    deep_leaf = self._build_chain(depth=25, prefix='deep')

    shallow_token = self._role_with_access('Perf Shallow', shallow_leaf)
    deep_token = self._role_with_access('Perf Deep', deep_leaf)

    shallow_query_count = self._count_queries_for_menu_tree(shallow_token)
    deep_query_count = self._count_queries_for_menu_tree(deep_token)

    assert shallow_query_count == deep_query_count
    assert shallow_query_count <= 5
