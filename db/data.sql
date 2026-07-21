-- Users
-- Contraseña en texto plano para ambos: '1234' (hasheada con bcrypt, PasswordService.generate_crypted_password)
INSERT INTO "Users" (name_user, surname_user, username_user, password_user) VALUES
('Mateo', 'Sosa', 'msosa', '$2b$12$NTK2mDWqmcWVRB6jChKdj.2GU0sAxnXKDlv5N.222Aazod05ogqhK'),
('Admin', 'admin', 'admin', '$2b$12$NTK2mDWqmcWVRB6jChKdj.2GU0sAxnXKDlv5N.222Aazod05ogqhK');

-- Roles
INSERT INTO "Roles" (name_role) VALUES
('Vendedor'),
('Asistente'),
('Visitante'),
('Administrador');

INSERT INTO "Modules" (id_module, name_module, url_module, parent_id_module) VALUES 
(1, 'Menu', NULL, NULL),
(2, 'Submenu 1', NULL, 1),
(3, 'Submenu 2', NULL, 1),
(4, 'Item 1', '/item1', 2),
(5, 'Item 2', '/item2', 2),
(6, 'Item 3', '/item3', 3),
(7, 'Item 4', '/item4', 3),
(8, 'Item Invisible', '/item_inv', 3);

-- IDs insertados manualmente arriba; hay que adelantar la secuencia o el próximo INSERT sin id
-- explícito choca con un id ya existente (ej. intenta reusar id_module=2).
SELECT setval(pg_get_serial_sequence('"Modules"', 'id_module'), (SELECT MAX(id_module) FROM "Modules"));

-- Users - Roles
INSERT INTO "Users_Roles" (id_user, id_role) VALUES
(1, 1),
(1, 2),
(2, 1),
(2, 2),
(2, 3),
(2, 4);

-- Roles - Modules
INSERT INTO "Roles_Modules" (id_role, id_module) VALUES
-- Vendedor
(1, 4),
(1, 5),
(1, 6),
(1, 7),
-- Administrador
(4, 4),
(4, 5),
(4, 6),
(4, 7),
(4, 8);
