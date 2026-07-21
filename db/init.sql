-- CREATE DATABASE MasterGateway;

-- Identificadores entre comillas dobles para preservar mayusculas: deben coincidir exactamente
-- con __tablename__ del ORM (SQLAlchemy) y con las referencias en data.sql.

CREATE TYPE estado_enum AS ENUM ('ACTIVO', 'INACTIVO');

CREATE TABLE IF NOT EXISTS "Users" (
    id_user SERIAL NOT NULL PRIMARY KEY,
    name_user VARCHAR(20) NOT NULL,  -- Nombre
    surname_user VARCHAR(20) NOT NULL,  -- Apellido
    username_user VARCHAR(20) NOT NULL,  -- Usuario login
    password_user TEXT NOT NULL,  -- Crypted
    estado estado_enum NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT now(),
    creado_por INTEGER REFERENCES "Users" (id_user),
    actualizado_por INTEGER REFERENCES "Users" (id_user)
);

CREATE TABLE IF NOT EXISTS "Roles" (
    id_role SERIAL NOT NULL PRIMARY KEY,
    name_role VARCHAR(20) NOT NULL,
    estado estado_enum NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT now(),
    creado_por INTEGER REFERENCES "Users" (id_user),
    actualizado_por INTEGER REFERENCES "Users" (id_user)
);

-- Menú
CREATE TABLE IF NOT EXISTS "Modules" (
    id_module SERIAL NOT NULL PRIMARY KEY,
    name_module VARCHAR(20) NOT NULL,
    url_module TEXT,  -- Solo nodos hoja
    parent_id_module INTEGER,  -- Nodo padre (recursividad)
    estado estado_enum NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now(),
    fecha_actualizacion TIMESTAMPTZ NOT NULL DEFAULT now(),
    creado_por INTEGER REFERENCES "Users" (id_user),
    actualizado_por INTEGER REFERENCES "Users" (id_user),
    FOREIGN KEY (parent_id_module) REFERENCES "Modules" (id_module)
);

-- Usuarios a Roles N:M (tabla pivote con su propia auditoria: estado + fecha_creacion)
CREATE TABLE IF NOT EXISTS "Users_Roles" (
    id_user INTEGER NOT NULL,
    id_role INTEGER NOT NULL,
    estado estado_enum NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id_user, id_role),
    FOREIGN KEY (id_user) REFERENCES "Users" (id_user),
    FOREIGN KEY (id_role) REFERENCES "Roles" (id_role)
);

-- Roles a Módulos N:M (tabla pivote con su propia auditoria: estado + fecha_creacion)
-- Permisos por módulo
CREATE TABLE IF NOT EXISTS "Roles_Modules" (
    id_role INTEGER NOT NULL,
    id_module INTEGER NOT NULL,
    estado estado_enum NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id_role, id_module),
    FOREIGN KEY (id_role) REFERENCES "Roles" (id_role),
    FOREIGN KEY (id_module) REFERENCES "Modules" (id_module)
);
