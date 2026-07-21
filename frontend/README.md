# Master Gateway — Frontend

SPA del microservicio maestro de autenticación/autorización (Vue 3 + Vite + Tailwind CSS v4). Ver
`docs/internal/UI_Design.md` en la raíz del repo para el sistema de diseño (colores, tipografía, componentes).

## Requisitos

El backend (`../backend`) debe estar corriendo en `http://localhost:8000` (con su base de datos Postgres
seedeada — ver `../backend/README.md`).

## Instalación y ejecución

```sh
cp .env.example .env   # ajustar VITE_API_BASE_URL si el backend no corre en localhost:8000
npm install
npm run dev            # http://localhost:5173
```

```sh
npm run build           # build de producción en dist/
npm run preview         # sirve el build de producción localmente
```

## Arquitectura

- **Sesión en memoria únicamente** (`src/stores/auth.js`, Pinia): el JWT y el refresh token nunca se
  persisten en `localStorage`/`sessionStorage` — un refresh de página cierra la sesión. Es la opción más
  simple y segura para este MVP sin requerir soporte de cookies `httpOnly` en el backend todavía.
- **Login en dos pasos**: `LoginView` → `POST /api/auth/login` (credenciales → `TempToken` + roles) →
  `SelectRoleView` → `POST /api/auth/select-role` (`TempToken` + rol → JWT + refresh token).
- **Interceptor HTTP** (`src/api/client.js`): adjunta el `Authorization: Bearer` a cada request; ante un
  401 intenta refrescar una sola vez vía `/api/auth/refresh-token` y reintenta la request original.
- **Rutas dinámicas** (`src/router/dynamicRoutes.js`): tras seleccionar rol se consulta
  `GET /api/menus/tree` y se registran las rutas hijas de `/app` en runtime con `router.addRoute(...)` —
  el árbol de navegación real siempre viene del backend, nunca está hardcodeado. La única lista fija en
  el cliente es qué **componente** renderiza cada `url_module` ya conocido (`/users`, `/roles`,
  `/modules`); cualquier `url_module` no reconocido cae a una pantalla placeholder en vez de romper.
