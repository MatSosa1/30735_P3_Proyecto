# Tema

Sistema de Autenticación y Autorización Centralizado (Master Gateway)

# Descripción General

En la actualidad, el desarrollo de aplicaciones empresariales ha evolucionado hacia
arquitecturas de microservicios para garantizar escalabilidad, independencia de despliegue y diversidad tecnológica. Sin embargo, esta descentralización trae consigo un desafı́o crı́tico: la fragmentación de la identidad y el control de acceso.

Cuando cada microservicio implementa su propio mecanismo de autenticación y autorización, se generan silos de seguridad, duplicación de código, inconsistencias en la gestión de roles y una experiencia de usuario fragmentada. Además, la integración de nuevos módulos al ecosistema se vuelve lenta y propensa a errores de configuración, exponiendo vulnerabilidades crı́ticas (como Broken Access Control).

El problema fundamental radica en la falta de un ”Microservicio Maestro (Master)”que actúe como el eje centralizador de la identidad. Se necesita un sistema que no solo valide ”quién es el usuario (Autenticación), sino ”qué" puede hacer y ”dónde" puede ir (Autorización dinámica), basándose en una estructura de menús recursiva que se adapte intrı́nsecamente a los módulos asignados a sus roles.

Para solventar esto, el proyecto exige la construcción de un módulo Full-Stack bajo los principios de Shift-Left (integración de seguridad desde las primeras fases de diseño y codificación) y Zero Trust (”Nunca confiar, siempre verificar”; asumiendo que la red interna es hostil y requiriendo validación continua).

# Objetivo General

Desarrollar un microservicio maestro de autenticación y autorización Full-Stack que
centralice la gestión de identidades, roles y navegación, sirviendo como gateway de seguridad y enrutamiento para un ecosistema de microservicios.

## Objetivos Específicos

1. Implementar un modelo de datos relacional que soporte relaciones Many-to-Many entre Usuarios y Roles.
2. Diseñar una estructura de menús dinámica y recursiva (almacenada en una sola tabla) que represente Módulos, Submenús e Items, asociada directamente a roles.
3. Desarrollar el flujo de inicio de sesión donde el usuario seleccione activamente el rol con el que desea operar, cargando únicamente el módulo y menú asociados a dicha elección.
4. Configurar una arquitectura preparada para la integración de futuros microservicios (ej. Módulo de Ventas), donde el microservicio maestro emita y valide tokens (JWT/OAuth2 ) bajo el modelo Zero Trust.
5. Aplicar el enfoque Shift-Left mediante pruebas de seguridad unitarias, validación de entradas (sanitización), protección contra inyección SQL (vı́a ORM) y cifrado de contraseñas.
