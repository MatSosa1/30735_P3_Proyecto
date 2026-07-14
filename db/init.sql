-- CREATE DATABASE MasterGateway;

CREATE TABLE IF NOT EXISTS Users (
    id_user SERIAL NOT NULL PRIMARY KEY,
    name_user VARCHAR(20) NOT NULL,  -- Nombre
    surname_user VARCHAR(20) NOT NULL,  -- Apellido
    username_user VARCHAR(20) NOT NULL,  -- Usuario login
    password_user TEXT NOT NULL  -- Crypted
);

CREATE TABLE IF NOT EXISTS Roles (
    id_role SERIAL NOT NULL PRIMARY KEY,
    name_role VARCHAR(20) NOT NULL
);

-- Menú
CREATE TABLE IF NOT EXISTS Modules (
    id_module SERIAL NOT NULL PRIMARY KEY,
    name_module VARCHAR(20) NOT NULL,
    url_module TEXT,  -- Solo nodos hoja
    parent_id_module INTEGER,  -- Nodo padre (recursividad)
    FOREIGN KEY (parent_id_module) REFERENCES Modules(id_module)
);

-- Usuarios a Roles N:M
CREATE TABLE IF NOT EXISTS Users_Roles (
    id_user INTEGER NOT NULL,
    id_role INTEGER NOT NULL,

    FOREIGN KEY (id_user) REFERENCES Users (id_user),
    FOREIGN KEY (id_role) REFERENCES Roles (id_role)
);

-- Roles a Módulos N:M
-- Permisos por módulo
CREATE TABLE IF NOT EXISTS Roles_Modules (
    id_role INTEGER NOT NULL,
    id_module INTEGER NOT NULL,

    FOREIGN KEY (id_role) REFERENCES Roles (id_role),
    FOREIGN KEY (id_module) REFERENCES Modules (id_module)
);
