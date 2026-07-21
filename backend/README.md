# Backend Proyecto Desarrollo Seguro 3er Parcial

## Requisitos Funcionales

Generar un CRUD completo para Usuarios y Roles. Las contraseñas deben estar cifradas.

## Instalación

Para poder ejecutar el backend, deben seguirse estos pasos:

### Variables de Entorno

```sh
# Copiar las variables de entorno de ejemplo
cp example.env .env

# De ser necesario, cambiar las variables de acuerdo a su entorno

```

### Dependencias Python

Se recomienda realizar toda la instalación en un entorno virtual de python (_venv_):

```sh
# Crear entorno
python -m venv <virtal_env_name>

# Entrar a entorno
source venv/bin/activate  # Dependerá de tu terminal

# Desactivar entorno
deactivate

```

Para poder instalar las dependencias, ejecute:

```sh
pip install -r requirements.txt

```

## Ejecución

Para poder ejecutar este increible backend espectacular realizado en Python y FastAPI, ejecuta:

```sh
uvicorn main:app

# O, si deseas hacer cambios y verlos en tiempo de ejecución
uvicorn main:app --reload

```

Esto abrirá el backend en el puerto 8000.

## Endpoints

### Auth

El login es un flujo de dos pasos (Workspace Selector): primero se validan credenciales y se elige el rol
después, en una segunda llamada. El JWT de sesión final solo contiene el rol elegido (Least Privilege) —
nunca todos los roles del usuario. `POST /api/auth/login` reemplaza al antiguo `POST /api/auth/set_role`
(eliminado); `POST /api/auth/select-role` reemplaza al antiguo `POST /api/auth/login` de un solo paso.

#### `POST /api/auth/login`

Valida credenciales (usuario + contraseña). Si son correctas, devuelve un `TempToken` de vida muy corta
(no habilita ningún acceso por sí solo) y la lista de roles del usuario. Sujeto a rate limiting (5 por
minuto por IP). El mensaje de error es genérico: no distingue si falló el usuario o la contraseña.

##### Request Body

```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

##### Respuesta exitosa

```json
{
  "temp_token": "temp_token_jwt",
  "roles": [
    { "id_role": 1, "name_role": "Administrador" }
  ]
}
```

##### Respuesta de error

`401` con `{ "detail": "Credenciales inválidas" }`.

#### `POST /api/auth/select-role`

Recibe el `TempToken` del paso anterior y el `role_id` elegido (debe pertenecer al usuario del `TempToken`).
Devuelve el JWT de sesión definitivo (corta duración) y un refresh token (de mayor duración, para renovar
sin volver a pedir contraseña).

##### Request Body

```json
{
  "temp_token": "temp_token_jwt",
  "role_id": 1
}
```

##### Respuesta exitosa

```json
{
  "token": "jwt_de_sesion",
  "refresh_token": "refresh_token_opaco"
}
```

##### Respuesta de error

`401` con `{ "detail": "Selección de rol inválida" }` (TempToken inválido/expirado o rol no asignado al usuario).

#### `POST /api/auth/refresh-token`

Genera un nuevo JWT de sesión (mismo rol) a partir de un refresh token válido. Cada uso rota el refresh
token (el anterior queda revocado). Si un refresh token ya revocado se reutiliza, se asume compromiso de
sesión y se revocan **todos** los refresh tokens del usuario.

##### Request Body

```json
{ "refresh_token": "refresh_token_opaco" }
```

##### Respuesta exitosa

```json
{
  "token": "jwt_de_sesion_nuevo",
  "refresh_token": "refresh_token_nuevo"
}
```

##### Respuesta de error

`401` con `{ "detail": "Refresh token inválido" }`.

#### `POST /api/auth/logout`

Requiere `Authorization: Bearer <jwt>`. Revoca todos los refresh tokens del usuario autenticado, cortando
la sesión de inmediato en caso de compromiso.

##### Respuesta exitosa

```json
{ "message": "Sesión cerrada" }
```

### Internals

#### `POST /api/internals/validate-token`

Endpoint privado para que otros microservicios (ej. futuro módulo de Ventas) validen un JWT emitido por
este Master, bajo el modelo Zero Trust. Requiere el header `X-Internal-Secret` con el secreto compartido
configurado en `INTERNAL_SERVICES_SECRET`. No expone datos sensibles del usuario.

##### Request Body

```json
{ "token": "jwt_a_validar" }
```

##### Respuesta exitosa

```json
{ "valid": true, "user_id": 1, "role_id": 1 }
```

Si el token es inválido: `{ "valid": false }` (siempre `200`, ya que "inválido" es una respuesta legítima
para el microservicio consumidor). Si falta o no coincide el secreto compartido: `403`.


### Modules

Todas las rutas de este router están gateadas por `require_module(4)` (requieren un JWT de sesión cuyo
rol tenga acceso al módulo id 4). Ninguna ruta define `response_model`: se serializa el ORM `Module` tal
cual, incluyendo los campos de auditoría (`estado`, `fecha_creacion`, `fecha_actualizacion`, `creado_por`,
`actualizado_por`) — a diferencia de `Users`, que sí filtra su respuesta con `UserOut`.

#### `GET /api/modules/`

Obtiene la lista de todos los módulos registrados (activos, por el filtro global de soft delete).

##### Respuesta exitosa

```json
[
  {
    "id_module": 1,
    "name_module": "Menu",
    "url_module": null,
    "parent_id_module": null,
    "estado": "ACTIVO",
    "fecha_creacion": "2026-07-21T03:26:46.095122+00:00",
    "fecha_actualizacion": "2026-07-21T03:26:46.095122+00:00",
    "creado_por": null,
    "actualizado_por": null
  }
]
```

#### `GET /api/modules/{module_id}`

Obtiene la información de un módulo específico mediante su identificador.

##### Parámetros de ruta

| Parámetro   | Tipo  | Descripción              |
| ----------- | ----- | ------------------------ |
| `module_id` | `int` | Identificador del módulo |

##### Respuesta exitosa

```json
{
  "id_module": 1,
  "name_module": "Menu",
  "url_module": null,
  "parent_id_module": null,
  "estado": "ACTIVO",
  "fecha_creacion": "2026-07-21T03:26:46.095122+00:00",
  "fecha_actualizacion": "2026-07-21T03:26:46.095122+00:00",
  "creado_por": null,
  "actualizado_por": null
}
```

##### Respuesta de error

Si el módulo no existe:

```json
{
  "detail": "Module not found"
}
```

#### `POST /api/modules/`

Crea un nuevo módulo.

##### Request Body

```json
{
  "name": "Usuarios",
  "url": "/users",
  "parent_id": null
}
```

##### Respuesta exitosa (`201`)

```json
{
  "id_module": 10,
  "name_module": "Usuarios",
  "url_module": "/users",
  "parent_id_module": null,
  "estado": "ACTIVO",
  "fecha_creacion": "2026-07-21T04:30:15.203032+00:00",
  "fecha_actualizacion": "2026-07-21T04:30:15.203032+00:00",
  "creado_por": null,
  "actualizado_por": null
}
```

#### `PATCH /api/modules/{module_id}`

Actualiza parcialmente la información de un módulo existente.

##### Parámetros de ruta

| Parámetro   | Tipo  | Descripción              |
| ----------- | ----- | ------------------------ |
| `module_id` | `int` | Identificador del módulo |

##### Request Body

```json
{
  "name": "Gestión de Usuarios",
  "url": "/users",
  "parent_id": 2
}
```

Los campos son opcionales, por lo que se pueden actualizar únicamente los valores necesarios.

##### Respuesta exitosa

Mismo formato que `POST /api/modules/`, con los campos actualizados.

##### Respuesta de error

Si el módulo no existe:

```json
{
  "detail": "Module not found"
}
```

Si el nuevo `parent_id` generaría una referencia cíclica (el propio módulo apareciendo en su
cadena de ancestros): `400`.

```json
{
  "detail": "El nuevo parent_id generaría una referencia cíclica"
}
```

#### `PUT /api/modules/{module_id}/roles`

Asigna una lista de roles a un módulo (reemplaza por completo las asignaciones previas de ese módulo).

##### Parámetros de ruta

| Parámetro   | Tipo  | Descripción              |
| ----------- | ----- | ------------------------ |
| `module_id` | `int` | Identificador del módulo |

##### Request Body

```json
{
  "roles_id": [1, 2, 3]
}
```

##### Respuesta exitosa

Mismo formato que `GET /api/modules/{module_id}` (el módulo, no la lista de asignaciones).

##### Respuesta de error

Si el módulo no existe:

```json
{
  "detail": "Module not found"
}
```

#### `DELETE /api/modules/{module_id}`

Elimina un módulo mediante su identificador (soft delete: se marca `estado=INACTIVO`, no es DELETE
físico).

##### Parámetros de ruta

| Parámetro   | Tipo  | Descripción              |
| ----------- | ----- | ------------------------ |
| `module_id` | `int` | Identificador del módulo |

##### Respuesta exitosa

`204`, sin contenido.

##### Respuesta de error

Si el módulo no existe:

```json
{
  "detail": "Module not found"
}
```


### Roles

Todas las rutas de este router están gateadas por `require_module(4)`. Al igual que `Modules`, no define
`response_model`: se serializa el ORM `Role` tal cual, incluyendo los campos de auditoría.

#### `GET /api/roles/`

Obtiene la lista de todos los roles registrados (activos, por el filtro global de soft delete).

##### Respuesta exitosa

```json
[
  {
    "id_role": 1,
    "name_role": "Vendedor",
    "estado": "ACTIVO",
    "fecha_creacion": "2026-07-21T03:26:46.086810+00:00",
    "fecha_actualizacion": "2026-07-21T03:26:46.086810+00:00",
    "creado_por": null,
    "actualizado_por": null
  }
]
```

#### `GET /api/roles/{role_id}`

Obtiene la información de un rol específico mediante su identificador.

##### Parámetros de ruta

| Parámetro | Tipo  | Descripción           |
| --------- | ----- | --------------------- |
| `role_id` | `int` | Identificador del rol |

##### Respuesta exitosa

Mismo formato que un elemento de `GET /api/roles/`.

##### Respuesta de error

Si el rol no existe:

```json
{
  "detail": "Role not found"
}
```

#### `POST /api/roles/`

Crea un nuevo rol.

##### Request Body

```json
{
  "name": "Administrador"
}
```

##### Respuesta exitosa (`201`)

Mismo formato que un elemento de `GET /api/roles/`.

#### `PATCH /api/roles/{role_id}`

Actualiza parcialmente la información de un rol existente.

##### Parámetros de ruta

| Parámetro | Tipo  | Descripción           |
| --------- | ----- | --------------------- |
| `role_id` | `int` | Identificador del rol |

##### Request Body

```json
{
  "name": "Administrador del sistema"
}
```

El campo `name` es opcional, por lo que se puede actualizar únicamente el valor necesario.

##### Respuesta exitosa

Mismo formato que un elemento de `GET /api/roles/`, con el nombre actualizado.

##### Respuesta de error

Si el rol no existe:

```json
{
  "detail": "Role not found"
}
```

#### `DELETE /api/roles/{role_id}`

Elimina un rol mediante su identificador.

##### Parámetros de ruta

| Parámetro | Tipo  | Descripción           |
| --------- | ----- | --------------------- |
| `role_id` | `int` | Identificador del rol |

##### Respuesta exitosa

No retorna contenido en el cuerpo de la respuesta.

##### Respuesta de error

Si el rol no existe:

```json
{
  "detail": "Role not found"
}
```

#### `POST /api/roles/{role_id}/users`

Asigna un usuario existente a un rol (tabla pivote `Users_Roles`). Si la asignación ya existía pero
estaba inactiva, la reactiva.

##### Request Body

```json
{ "user_id": 1 }
```

##### Respuesta exitosa (`201`)

```json
{ "id_role": 1, "id_user": 1, "estado": "ACTIVO", "fecha_creacion": "..." }
```

##### Respuesta de error

`404` si el rol o el usuario no existen.

#### `DELETE /api/roles/{role_id}/users/{user_id}`

Desasigna un usuario de un rol. A diferencia del resto de entidades, esta operación es una
**eliminación física** de la fila en la tabla pivote (así lo exige el spec para este caso puntual).

##### Respuesta exitosa

`204`, sin contenido.

##### Respuesta de error

`404` si la asignación no existe.

#### `POST /api/roles/{role_id}/modules`

Vincula un módulo completo a un rol, desde el lado de "roles" (simétrico a
`PUT /api/modules/{module_id}/roles`).

##### Request Body

```json
{ "module_id": 4 }
```

##### Respuesta exitosa (`201`)

```json
{ "id_role": 1, "id_module": 4, "estado": "ACTIVO", "fecha_creacion": "..." }
```

#### `POST /api/roles/{role_id}/menus`

Asigna un ítem/submenú puntual a un rol. Mismo mecanismo que `POST /api/roles/{role_id}/modules`
(ambos son filas de `Module`); el endpoint existe por separado porque el spec lo nombra así.

##### Request Body

```json
{ "module_id": 8 }
```

##### Respuesta exitosa (`201`)

Igual formato que `POST /api/roles/{role_id}/modules`.


### Users

Ruta gateada por `require_module(4)`. A diferencia de `Modules`/`Roles`, sí define `response_model=UserOut`
(o `list[UserOut]`), que deliberadamente excluye `password_user` y los campos `creado_por`/`actualizado_por`.

#### `GET /api/users/`

Obtiene la lista de todos los usuarios registrados (activos, por el filtro global de soft delete).

##### Respuesta exitosa

```json
[
  {
    "id_user": 1,
    "name_user": "Mateo",
    "surname_user": "Sosa",
    "username_user": "msosa",
    "estado": "ACTIVO",
    "fecha_creacion": "2026-07-21T03:26:46.080139Z",
    "fecha_actualizacion": "2026-07-21T03:26:46.080139Z"
  }
]
```

#### `GET /api/users/{user_id}`

Obtiene la información de un usuario específico mediante su identificador.

##### Parámetros de ruta

| Parámetro | Tipo  | Descripción               |
| --------- | ----- | ------------------------- |
| `user_id` | `int` | Identificador del usuario |

##### Respuesta exitosa

Mismo formato que un elemento de `GET /api/users/`.

##### Respuesta de error

Si el usuario no existe:

```json
{
  "detail": "User not found"
}
```

#### `POST /api/users/`

Crea un nuevo usuario. La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un
número; si no cumple, responde `422`. Las respuestas de `/users` (`GET`/`POST`/`PATCH`) nunca incluyen el
hash de la contraseña (`password_user`), gracias al `response_model=UserOut`.

##### Request Body

```json
{
  "name": "Mateo",
  "surname": "Sosa",
  "username": "msosa",
  "password": "contraseña"
}
```

##### Respuesta exitosa (`201`)

Mismo formato que un elemento de `GET /api/users/`.

#### `PATCH /api/users/{user_id}`

Actualiza parcialmente la información de un usuario existente.

##### Parámetros de ruta

| Parámetro | Tipo  | Descripción               |
| --------- | ----- | ------------------------- |
| `user_id` | `int` | Identificador del usuario |

##### Request Body

```json
{
  "name": "Mateo",
  "surname": "Sosa",
  "username": "mateo.sosa",
  "password": "nueva_contraseña"
}
```

Los campos son opcionales, por lo que se pueden actualizar únicamente los valores necesarios.

##### Respuesta exitosa

Mismo formato que un elemento de `GET /api/users/`, con los campos actualizados.

##### Respuesta de error

Si el usuario no existe:

```json
{
  "detail": "User not found"
}
```

#### `DELETE /api/users/{user_id}`

Elimina un usuario mediante su identificador (soft delete: se marca `estado=INACTIVO`, no es DELETE físico).

##### Parámetros de ruta

| Parámetro | Tipo  | Descripción               |
| --------- | ----- | ------------------------- |
| `user_id` | `int` | Identificador del usuario |

##### Respuesta exitosa

No retorna contenido en el cuerpo de la respuesta.

##### Respuesta de error

Si el usuario no existe:

```json
{
  "detail": "User not found"
}
```


### Menús

#### `GET /api/menus/tree`

Devuelve el árbol jerárquico completo de módulos/submenús/ítems accesibles al **rol del JWT actual**
(no requiere `require_module`, cualquier token válido puede consultar su propio menú). Se resuelve con
una única consulta recursiva (CTE, `WITH RECURSIVE`) para evitar el problema N+1 sin importar la
profundidad del árbol.

Si un módulo intermedio está `INACTIVO`, todo su subárbol deja de aparecer, aunque los módulos hijos
sigan individualmente `ACTIVO`.

##### Respuesta exitosa

```json
[
  {
    "id_module": 1,
    "name_module": "Menu",
    "url_module": null,
    "parent_id_module": null,
    "children": [
      {
        "id_module": 2,
        "name_module": "Submenu 1",
        "url_module": null,
        "parent_id_module": 1,
        "children": [
          { "id_module": 4, "name_module": "Item 1", "url_module": "/item1", "parent_id_module": 2, "children": [] }
        ]
      }
    ]
  }
]
```

##### Respuesta de error

`403` si el rol del token ya no existe o está inactivo.
