-- Users
INSERT INTO "Users" (name_user, surname_user, username_user, password_user) VALUES
('Mateo', 'Sosa', 'msosa', '1234'),
('Admin', 'admin', 'admin', '1234');

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

-- Users - Roles
INSERT INTO "Users_Roles" VALUES
(1, 1),
(1, 2),
(2, 1),
(2, 2),
(2, 3),
(2, 4);

-- Roles - Modules
INSERT INTO "Roles_Modules" VALUES
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
