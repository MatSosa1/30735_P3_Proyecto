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

#### `GET /api/modules/`

Obtiene la lista de todos los módulos registrados.

##### Respuesta exitosa

```json
[
  {
    "id": 1,
    "name": "Usuarios",
    "url": "/users",
    "parent_id": null
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
  "id": 1,
  "name": "Usuarios",
  "url": "/users",
  "parent_id": null
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

##### Respuesta exitosa

```json
{
  "id": 1,
  "name": "Usuarios",
  "url": "/users",
  "parent_id": null
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

```json
{
  "id": 1,
  "name": "Gestión de Usuarios",
  "url": "/users",
  "parent_id": 2
}
```

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

Asigna una lista de roles a un módulo.

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

```json
{
  "id": 1,
  "name": "Usuarios",
  "url": "/users",
  "parent_id": null
}
```

##### Respuesta de error

Si el módulo no existe:

```json
{
  "detail": "Module not found"
}
```

#### `DELETE /api/modules/{module_id}`

Elimina un módulo mediante su identificador.

##### Parámetros de ruta

| Parámetro   | Tipo  | Descripción              |
| ----------- | ----- | ------------------------ |
| `module_id` | `int` | Identificador del módulo |

##### Respuesta exitosa

```json
{
  "message": "Module deleted successfully"
}
```

##### Respuesta de error

Si el módulo no existe:

```json
{
  "detail": "Module not found"
}
```


### Roles

#### `GET /api/roles/`

Obtiene la lista de todos los roles registrados.

##### Respuesta exitosa

```json
[
  {
    "id": 1,
    "name": "Administrador"
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

```json
{
  "id": 1,
  "name": "Administrador"
}
```

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

##### Respuesta exitosa

```json
{
  "id": 1,
  "name": "Administrador"
}
```

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

```json
{
  "id": 1,
  "name": "Administrador del sistema"
}
```

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

#### `GET /api/users/`

Obtiene la lista de todos los usuarios registrados.

##### Respuesta exitosa

```json
[
  {
    "id": 1,
    "name": "Mateo",
    "surname": "Sosa",
    "username": "msosa"
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

```json
{
  "id": 1,
  "name": "Mateo",
  "surname": "Sosa",
  "username": "msosa"
}
```

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
hash de la contraseña (`password_user`).

##### Request Body

```json
{
  "name": "Mateo",
  "surname": "Sosa",
  "username": "msosa",
  "password": "contraseña"
}
```

##### Respuesta exitosa

```json
{
  "id": 1,
  "name": "Mateo",
  "surname": "Sosa",
  "username": "msosa"
}
```

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

```json
{
  "id": 1,
  "name": "Mateo",
  "surname": "Sosa",
  "username": "mateo.sosa"
}
```

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
