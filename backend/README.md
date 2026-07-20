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

#### `POST /auth/set_role`

Obtiene los roles asociados a un usuario después de validar sus credenciales.

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
  "roles": [
    {
      "id": 1,
      "name": "Administrador"
    }
  ]
}

```

##### Respuesta de error

Si el usuario no existe o no tiene roles asignados:

```json
{
  "error": "Usuario no existe o no tiene roles"
}

```

#### `POST /auth/login`

Autentica al usuario utilizando sus credenciales y el rol seleccionado. Si la autenticación es exitosa, genera un token de acceso.

##### Request Body

```json
{
  "username": "usuario",
  "password": "contraseña",
  "actual_role_id": 1
}

```

##### Respuesta exitosa

```json
{
  "token": "token_jwt_generado"
}

```

##### Respuesta de error

Si las credenciales no son válidas:

```json
{
  "error": "Credenciales inválidas"
}
```


### Modules

#### `GET /modules/`

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

#### `GET /modules/{module_id}`

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

#### `POST /modules/`

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

#### `PATCH /modules/{module_id}`

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

#### `PUT /modules/{module_id}/roles`

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

#### `DELETE /modules/{module_id}`

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

#### `GET /roles/`

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

#### `GET /roles/{role_id}`

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

#### `POST /roles/`

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

#### `PATCH /roles/{role_id}`

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

#### `DELETE /roles/{role_id}`

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


### Users

#### `GET /users/`

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

#### `GET /users/{user_id}`

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

#### `POST /users/`

Crea un nuevo usuario.

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

#### `PATCH /users/{user_id}`

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

#### `DELETE /users/{user_id}`

Elimina un usuario mediante su identificador.

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
