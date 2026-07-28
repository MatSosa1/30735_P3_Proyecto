# Cómo levantar el proyecto en local

El repositorio contiene dos aplicaciones independientes (`backend/` y `frontend/`) más los scripts de
base de datos en `db/`. Pueden levantarse manualmente paso a paso (backend → base de datos → frontend,
como se detalla abajo) o todas juntas con Docker Compose.

## Backend

Requiere Python y una base de datos PostgreSQL accesible (ver sección de Base de Datos más abajo).

### Variables de Entorno

```sh
cd backend
cp example.env .env

# De ser necesario, cambiar las variables de acuerdo a su entorno
```

### Dependencias Python

Se recomienda realizar toda la instalación en un entorno virtual de Python (_venv_):

```sh
# Crear entorno
python -m venv venv

# Entrar al entorno
source venv/bin/activate  # Dependerá de tu terminal

# Instalar dependencias
pip install -r requirements.txt

# Desactivar entorno (cuando termines)
deactivate
```

### Ejecución

```sh
uvicorn main:app --reload
```

Esto abrirá el backend en `http://localhost:8000`.

## Base de Datos

El backend necesita una instancia de PostgreSQL con el esquema y los datos semilla cargados
(`db/init.sql` y `db/data.sql`, en la raíz del repo). Dos formas de conseguirlo:

- **Solo la base de datos vía Docker Compose** (recomendado si el backend se corre manualmente):

    ```sh
    docker-compose up db
    ```

    Esto levanta Postgres en `localhost:5432` con el esquema y los datos ya cargados, listo para que el
    backend (`.env` con los valores por defecto) se conecte.

- **PostgreSQL local propio**: crear la base de datos y ejecutar `db/init.sql` seguido de `db/data.sql`
  manualmente, y ajustar las variables `DB_*` del `.env` del backend para que coincidan.

## Frontend

Requiere el backend corriendo en `http://localhost:8000` (con la base de datos ya seedeada).

```sh
cd frontend
cp .env.example .env   # ajustar VITE_API_BASE_URL si el backend no corre en localhost:8000
npm install
npm run dev            # http://localhost:5173
```

```sh
npm run build           # build de producción en dist/
npm run preview         # sirve el build de producción localmente
```

## Todo junto con Docker Compose

Para levantar base de datos, backend y frontend de una sola vez:

```sh
docker-compose up
```

Las variables de entorno (`DB_USERNAME`, `JWT_SECRET`, `INTERNAL_SERVICES_SECRET`, `CORS_ORIGINS`, etc.)
tienen valores por defecto definidos en `docker-compose.yml` para uso local; pueden sobreescribirse con un
`.env` en la raíz del repo o variables exportadas en el entorno.

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

# Estrategia de Ramas (Git)

El repositorio se rige por el siguiente modelo de ramas:

- **`main`**: Rama de producción. Inmutable excepto mediante Pull Requests desde `test`. Únicamente los
  merges en esta rama disparan el despliegue automático.
- **`test`**: Rama de pruebas/QA. Aquí se integran las funcionalidades para ser validadas antes de pasar a
  producción. Los Pull Requests hacia `main` nacen de aquí.
- **`dev`**: Rama de desarrollo. Los desarrolladores crean ramas `feature/*` (ej. `feature/auth-login`) a
  partir de `dev` y hacen Pull Requests de vuelta a `dev` para integración continua.

# CI/CD

El pipeline está repartido en 3 etapas que escalan en rigor a medida que el código avanza por el flujo de
ramas (`dev` → `test` → `main`), en vez de repetir los mismos chequeos en cada etapa:

- **`dev`** (`.github/workflows/dev-checks.yml`): el gate más rápido — SAST (**Bandit**) y auditoría de
  dependencias (**pip-audit** + **npm audit**). No corre Postgres ni la suite de tests; es el filtro de
  entrada para integrar features.
- **`test`** (`.github/workflows/test-checks.yml`): la suite funcional completa — build + tests con
  cobertura (**pytest**, con Postgres real como servicio) y build del frontend, más **Bandit** de nuevo
  (barato, vale la pena reconfirmarlo). No repite pip-audit/npm audit: las dependencias ya se auditaron al
  entrar a `dev` y el código en `test` es el mismo que pasó ese gate.
- **`main`** (`.github/workflows/ci-cd.yml`, push o Pull Request): el gate de producción, con todo lo
  anterior más análisis de calidad con **SonarQube self-hosted** (Community, levantado como contenedor
  efímero dentro del propio job — no SonarCloud, para poder configurar un Quality Gate a medida) y escaneo
  de vulnerabilidades en dependencias con **Trivy**. Si todo pasa y el push fue a `main`, se dispara el
  despliegue en Render.

Cada etapa notifica su resultado a un grupo de Telegram — `main` con inicio de pipeline + resumen final
completo; `dev`/`test` con un resumen liviano de solo lo que esa etapa efectivamente corrió.

Para que el pipeline funcione hace falta configurar estos secrets en
**Settings → Secrets and variables → Actions**:

| Secret                    | Para qué                                                                                                                                                                                                                                             |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `TELEGRAM_BOT_TOKEN`      | Token del bot de Telegram (BotFather). Notificaciones obligatorias — el job falla si no se puede notificar.                                                                                                                                          |
| `TELEGRAM_CHAT_ID`        | ID del chat/grupo de Telegram donde se notifica.                                                                                                                                                                                                     |
| `RENDER_DEPLOY_HOOK_URL`  | Deploy Hook del servicio en Render (Dashboard → el servicio → Settings → Deploy Hook). Si falta, el despliegue se omite (no rompe el pipeline) pero no despliega nada — hay que configurarlo antes de depender del deploy automático.                |
| `SONAR_CI_ADMIN_PASSWORD` | Opcional. Contraseña que el pipeline le pone al admin de SonarQube dentro del contenedor efímero (no es un secreto de un servicio externo, es autocontenido al propio pipeline). Si no se define, usa un valor por defecto documentado en el script. |

**Importante:** en Render, deshabilitar el auto-deploy nativo de GitHub del servicio (el que dispara con
cada push al repo) — el despliegue debe depender únicamente de que el pipeline (tests + Quality Gate +
Bandit + Trivy) haya pasado, no de un webhook directo del repositorio.
