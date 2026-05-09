# Deploy a Producción (Railway + Vercel) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Llevar el MVP de Viajamos a producción con deploys automáticos desde GitHub usando Railway (backend + DB + Redis) y Vercel (frontend), con CI en GitHub Actions.

**Architecture:** Monorepo desplegado en dos plataformas: Railway hospeda backend FastAPI + PostgreSQL 15 + Redis 7 con migraciones automáticas via `releaseCommand`. Vercel hospeda el frontend Next.js 14 con build nativo. CI corre en GitHub Actions y bloquea deploys si fallan tests/lint.

**Tech Stack:** FastAPI, Strawberry GraphQL, SQLAlchemy 2.x async, Alembic, asyncpg, slowapi (rate limiting), Next.js 14, GitHub Actions, Railway, Vercel.

---

## File Structure

**Files to create:**
- `backend/.env.example` — template de variables del backend (commiteado, sin valores reales)
- `frontend/.env.example` — template de variables del frontend
- `backend/railway.json` — config de Railway con `releaseCommand: alembic upgrade head`
- `backend/app/core/rate_limit.py` — rate limiter con slowapi (Redis backend)
- `backend/tests/test_rate_limit.py` — tests del rate limiter
- `.github/workflows/ci.yml` — pipeline CI con jobs backend y frontend

**Files to modify:**
- `docker-compose.yml` — frontend usa `Dockerfile` (producción) en vez de `Dockerfile.dev`
- `frontend/next.config.js` — agregar dominio Railway en `images.remotePatterns`
- `backend/pyproject.toml` — agregar dependencia `slowapi`
- `backend/app/main.py` — wirear el rate limiter al app

**Phases (manuales, no son archivos):**
- Configuración de Railway, Vercel, GitHub Secrets y Branch Protection
- Carga de mock data y smoke tests

---

## Phase 1: Codebase Preparation

### Task 1: Corregir docker-compose.yml para usar Dockerfile de producción del frontend

**Files:**
- Modify: `docker-compose.yml:70`

**Why:** El `docker-compose.yml` actual usa `Dockerfile.dev` que monta el código en modo desarrollo. Para poder probar la build de producción local-like (mismo build que Vercel hace), apuntamos al `Dockerfile` de producción. Vercel ignora completamente este archivo — esto es solo para parity local.

- [ ] **Step 1: Modificar la línea del Dockerfile en docker-compose.yml**

Cambiar línea 70:

```yaml
    build:
      context: ./frontend
      dockerfile: Dockerfile
```

(antes era `Dockerfile.dev`)

- [ ] **Step 2: Verificar que la build funciona**

Run:
```bash
docker compose build frontend
```

Expected: Build exitoso con stages `deps`, `builder`, `runner`. La última línea debe ser similar a `=> exporting layers`.

- [ ] **Step 3: Commit**

```bash
git add docker-compose.yml
git commit -m "chore: usar Dockerfile de producción del frontend en docker-compose"
```

---

### Task 2: Crear backend/.env.example con plantilla de variables

**Files:**
- Create: `backend/.env.example`

**Why:** Documenta qué variables de entorno necesita el backend sin exponer valores reales. Sirve como referencia para quien clona el repo y para configurar Railway.

- [ ] **Step 1: Crear el archivo backend/.env.example**

Contenido completo:

```bash
# PostgreSQL Database Configuration
POSTGRES_USER=viaggiamo
POSTGRES_PASSWORD=changeme
POSTGRES_DB=viaggiamo_db

# Database URL (en producción Railway lo inyecta automáticamente)
DATABASE_URL=postgresql+asyncpg://viaggiamo:changeme@postgres:5432/viaggiamo_db

# Redis (en producción Railway lo inyecta automáticamente)
REDIS_URL=redis://redis:6379/0

# JWT — generar con: openssl rand -hex 32
SECRET_KEY=changeme-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_STR=/api/v1
PROJECT_NAME=Viajamos

# CORS — en producción debe contener solo el dominio canónico de Vercel
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000", "http://frontend:3000"]

# Environment: development | production
ENVIRONMENT=development
DEBUG=True

# OAuth
GOOGLE_CLIENT_ID=
```

- [ ] **Step 2: Verificar que .env (con secrets reales) sigue ignorado por git**

Run:
```bash
git check-ignore backend/.env && echo "OK: .env está ignorado"
```

Expected: `backend/.env` aparece y luego `OK: .env está ignorado`.

- [ ] **Step 3: Commit**

```bash
git add backend/.env.example
git commit -m "docs: agregar backend/.env.example con plantilla de variables"
```

---

### Task 3: Crear frontend/.env.example con plantilla de variables

**Files:**
- Create: `frontend/.env.example`

**Why:** Misma razón que Task 2 pero para el frontend. Sirve también para configurar Vercel.

- [ ] **Step 1: Crear el archivo frontend/.env.example**

Contenido completo:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GRAPHQL_URL=http://localhost:8000/graphql
NEXT_PUBLIC_APP_URL=http://localhost:3000

# App Configuration
NEXT_PUBLIC_APP_NAME=Viajamos
NEXT_PUBLIC_APP_DESCRIPTION=MVP de Carpooling

# OAuth Configuration
NEXT_PUBLIC_GOOGLE_CLIENT_ID=

# Environment
NODE_ENV=development
```

- [ ] **Step 2: Commit**

```bash
git add frontend/.env.example
git commit -m "docs: agregar frontend/.env.example con plantilla de variables"
```

---

### Task 4: Crear backend/railway.json con releaseCommand para migraciones automáticas

**Files:**
- Create: `backend/railway.json`

**Why:** Sin este archivo, Railway usa heurísticas para detectar el comando de start y NO corre migraciones automáticamente. El `releaseCommand` corre `alembic upgrade head` en cada deploy antes de promover el nuevo build a producción.

- [ ] **Step 1: Crear backend/railway.json**

Contenido completo:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "preDeployCommand": "uv run alembic upgrade head"
  }
}
```

> Nota: Railway llama a este hook `preDeployCommand` (anteriormente `releaseCommand`). Se ejecuta luego del build pero antes de hacer healthcheck del nuevo deploy.

- [ ] **Step 2: Validar JSON**

Run:
```bash
python3 -m json.tool backend/railway.json > /dev/null && echo "OK: JSON válido"
```

Expected: `OK: JSON válido`.

- [ ] **Step 3: Commit**

```bash
git add backend/railway.json
git commit -m "chore: agregar railway.json con migraciones automáticas en cada deploy"
```

---

### Task 5: Actualizar frontend/next.config.js con dominio Railway en remotePatterns

**Files:**
- Modify: `frontend/next.config.js`

**Why:** El Next.js Image Optimizer bloquea imágenes de hosts no listados explícitamente. El backend en Railway puede servir imágenes (avatars de usuarios, fotos de vehículos via Google OAuth) y necesita estar autorizado.

- [ ] **Step 1: Localizar el bloque remotePatterns**

Run:
```bash
grep -n "remotePatterns" frontend/next.config.js
```

Expected: una línea similar a `remotePatterns: [`.

- [ ] **Step 2: Agregar el dominio de Railway**

Editar el bloque `remotePatterns` para que quede:

```javascript
    remotePatterns: [
      { protocol: 'http', hostname: 'localhost' },
      { protocol: 'https', hostname: 'api.viaggiamo.com' },
      { protocol: 'https', hostname: 'lh3.googleusercontent.com' },
      { protocol: 'https', hostname: 'viajamos-backend.up.railway.app' },
    ],
```

> Si el subdominio real de Railway termina siendo otro (ej. con sufijo aleatorio), actualizá esta línea cuando lo sepas.

- [ ] **Step 3: Verificar que el archivo es JS válido**

Run:
```bash
node -c frontend/next.config.js && echo "OK"
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add frontend/next.config.js
git commit -m "chore: agregar dominio Railway a remotePatterns de next.config"
```

---

### Task 6: Agregar dependencia slowapi al backend

**Files:**
- Modify: `backend/pyproject.toml`

**Why:** `slowapi` es una librería de rate limiting compatible con FastAPI. Tiene backend Redis (que ya tenemos) para rate limiting distribuido.

- [ ] **Step 1: Agregar dependencia con uv**

Run:
```bash
cd backend && uv add "slowapi>=0.1.9"
```

Expected: `slowapi` aparece en `pyproject.toml` dentro de `dependencies` y `uv.lock` se actualiza.

- [ ] **Step 2: Verificar que está instalada**

Run:
```bash
cd backend && uv run python -c "import slowapi; print(slowapi.__version__)"
```

Expected: imprime una versión (ej. `0.1.9`).

- [ ] **Step 3: Commit**

```bash
git add backend/pyproject.toml backend/uv.lock
git commit -m "deps: agregar slowapi para rate limiting"
```

---

### Task 7: Implementar rate limiter (TDD)

**Files:**
- Create: `backend/app/core/rate_limit.py`
- Create: `backend/tests/test_rate_limit.py`
- Modify: `backend/app/main.py`

**Why:** El endpoint `/graphql` es público y queremos protegerlo de abuso. Límite conservador: 100 requests por minuto por IP.

- [ ] **Step 1: Escribir el test (debería fallar)**

Crear `backend/tests/test_rate_limit.py`:

```python
"""Tests for rate limiting on /graphql endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_graphql_rate_limit_returns_429_when_exceeded(monkeypatch):
    """When the rate limit is exceeded, /graphql returns HTTP 429."""
    # Forzamos un límite bajo para testear sin hacer 100 requests
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "3")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        query = {"query": "{ __typename }"}
        # 3 requests dentro del límite
        for _ in range(3):
            response = await client.post("/graphql", json=query)
            assert response.status_code == 200

        # 4ta request debería fallar con 429
        response = await client.post("/graphql", json=query)
        assert response.status_code == 429
        assert "rate limit" in response.text.lower()
```

- [ ] **Step 2: Correr el test para verificar que falla**

Run:
```bash
cd backend && uv run pytest tests/test_rate_limit.py -v
```

Expected: FAIL — el test falla porque el rate limiter no existe todavía (todas las requests devuelven 200).

- [ ] **Step 3: Implementar el rate limiter**

Crear `backend/app/core/rate_limit.py`:

```python
"""Rate limiting configuration using slowapi."""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address


def _get_rate_limit() -> str:
    """Read rate limit from env var, default 100/minute."""
    per_minute = os.getenv("RATE_LIMIT_PER_MINUTE", "100")
    return f"{per_minute}/minute"


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_get_rate_limit()],
)
```

- [ ] **Step 4: Wirear el limiter en main.py**

Modificar `backend/app/main.py`:

Agregar imports al tope del archivo (después de los imports existentes):

```python
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.rate_limit import limiter
```

Dentro de `create_application()`, después de la creación del `app` y antes del CORS middleware:

```python
    # Rate limiting (must be configured before routes)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
```

El bloque completo de `create_application()` debe quedar así:

```python
def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        lifespan=lifespan,
    )

    # Rate limiting (must be configured before routes)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # CORS middleware - must be added BEFORE routes
    cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # GraphQL endpoint with dependency injection context
    graphql_app = GraphQLRouter(
        schema,
        context_getter=get_context,
        graphql_ide="graphiql",
    )
    app.include_router(graphql_app, prefix="/graphql")

    return app
```

- [ ] **Step 5: Correr el test para verificar que pasa**

Run:
```bash
cd backend && uv run pytest tests/test_rate_limit.py -v
```

Expected: PASS — las 3 primeras requests devuelven 200, la 4ta devuelve 429.

- [ ] **Step 6: Correr todo el test suite para verificar que no rompimos nada**

Run:
```bash
cd backend && uv run pytest
```

Expected: todos los tests pasan.

- [ ] **Step 7: Commit**

```bash
git add backend/app/core/rate_limit.py backend/app/main.py backend/tests/test_rate_limit.py
git commit -m "feat: agregar rate limiting básico al endpoint /graphql"
```

---

### Task 8: Crear .github/workflows/ci.yml con jobs de backend y frontend

**Files:**
- Create: `.github/workflows/ci.yml`

**Why:** El CI corre tests + lint en cada push y PR a `main`. Junto con branch protection, asegura que solo código verde llega a producción.

- [ ] **Step 1: Crear el archivo workflow**

Crear `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  backend-ci:
    name: Backend CI (lint + tests)
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: viaggiamo
          POSTGRES_PASSWORD: viaggiamo_password
          POSTGRES_DB: viaggiamo_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    env:
      DATABASE_URL: postgresql+asyncpg://viaggiamo:viaggiamo_password@localhost:5432/viaggiamo_test
      REDIS_URL: redis://localhost:6379/0
      SECRET_KEY: ${{ secrets.SECRET_KEY }}
      ENVIRONMENT: test
      DEBUG: "False"
      BACKEND_CORS_ORIGINS: '["http://localhost:3000"]'
      GOOGLE_CLIENT_ID: ""
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: "30"
      PROJECT_NAME: Viajamos
      API_V1_STR: /api/v1

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.11

      - name: Install backend dependencies
        working-directory: backend
        run: uv sync --frozen

      - name: Ruff check
        working-directory: backend
        run: uv run ruff check .

      - name: Ruff format check
        working-directory: backend
        run: uv run ruff format --check .

      - name: Run migrations
        working-directory: backend
        run: uv run alembic upgrade head

      - name: Run tests
        working-directory: backend
        run: uv run pytest --cov=app --cov-report=term

  frontend-ci:
    name: Frontend CI (type-check + lint)
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install pnpm
        uses: pnpm/action-setup@v3
        with:
          version: 9

      - name: Set up Node
        uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: pnpm
          cache-dependency-path: frontend/pnpm-lock.yaml

      - name: Install frontend dependencies
        working-directory: frontend
        run: pnpm install --frozen-lockfile

      - name: Type check
        working-directory: frontend
        run: pnpm run type-check

      - name: Lint
        working-directory: frontend
        run: pnpm run lint
```

- [ ] **Step 2: Validar la sintaxis YAML**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "OK: YAML válido"
```

Expected: `OK: YAML válido`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: agregar workflow de GitHub Actions para backend y frontend"
```

---

### Task 9: Push a main y verificar que CI corre

**Files:** ninguno (operación de git remoto)

- [ ] **Step 1: Push de la rama dev y crear PR a main**

Run:
```bash
git push origin dev
gh pr create --title "feat: preparar codebase para deploy a producción" --body "$(cat <<'EOF'
## Summary
- Configura Railway (railway.json con migraciones automáticas) y Vercel para deploy
- Agrega rate limiting al endpoint /graphql
- Agrega CI con tests y lint para backend y frontend
- Crea .env.example en backend y frontend
- Pone el frontend de docker-compose en modo producción

## Test plan
- [ ] CI verde en GitHub Actions
- [ ] Tests del backend pasan localmente con `cd backend && uv run pytest`
- [ ] Frontend type-check pasa con `cd frontend && npm run type-check`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 2: Verificar que el CI arrancó**

Run:
```bash
gh run list --branch dev --limit 1
```

Expected: aparece un run de "CI" en estado `queued`, `in_progress` o `completed`.

- [ ] **Step 3: Esperar que el CI termine y revisar resultado**

Run:
```bash
gh run watch
```

Expected: ambos jobs (`backend-ci` y `frontend-ci`) en verde.

- [ ] **Step 4: Mergear el PR a main**

Una vez verde, mergear desde GitHub UI o:

```bash
gh pr merge --squash --delete-branch=false
```

---

## Phase 2: Configurar Railway

> **Nota:** Esta fase es manual via dashboard de Railway. No hay código que escribir; solo seguir los pasos en orden.

### Task 10: Crear cuenta y proyecto en Railway

- [ ] **Step 1: Crear cuenta**

Ir a https://railway.app y registrarse con la cuenta de GitHub.

- [ ] **Step 2: Crear nuevo proyecto**

Click en "New Project" → "Deploy from GitHub repo" → seleccionar el repo `viaggiamo`.

- [ ] **Step 3: Configurar el servicio backend**

En el dashboard del proyecto:
1. Click en el servicio creado (Railway lo detecta automáticamente)
2. Settings → Source → Root Directory: `backend`
3. Settings → Build → Builder: `Dockerfile`
4. Settings → Networking → Generate Domain (esto genera `viajamos-backend-xxxx.up.railway.app`)
5. Anotar el dominio generado para configurar CORS y Vercel después.

---

### Task 11: Agregar PostgreSQL a Railway

- [ ] **Step 1: Agregar plugin**

En el dashboard del proyecto: New → Database → Add PostgreSQL.

- [ ] **Step 2: Configurar `DATABASE_URL` en formato asyncpg**

Railway expone variables individuales del Postgres (`PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`, `PGDATABASE`) pero su `DATABASE_URL` viene en formato `postgresql://...` y SQLAlchemy async necesita `postgresql+asyncpg://...`.

En el servicio backend → Variables → New Variable → agregar **exactamente** esta línea (Railway resuelve los placeholders `${{...}}` automáticamente):

```
DATABASE_URL=postgresql+asyncpg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}
```

- [ ] **Step 3: Verificar que la variable se resuelve correctamente**

En el servicio backend → Variables → click en el ícono de "Show" al lado de `DATABASE_URL`. Expected: ver una URL como `postgresql+asyncpg://postgres:abc123@viaduct.proxy.rlwy.net:12345/railway` (con valores reales).

---

### Task 12: Agregar Redis a Railway

- [ ] **Step 1: Agregar plugin**

En el dashboard del proyecto: New → Database → Add Redis.

- [ ] **Step 2: Linkear REDIS_URL al backend**

En el servicio backend → Variables → agregar `REDIS_URL=${{Redis.REDIS_URL}}`.

---

### Task 13: Configurar variables de entorno del backend

- [ ] **Step 1: Generar SECRET_KEY**

Run localmente:
```bash
openssl rand -hex 32
```

Copiar el valor generado.

- [ ] **Step 2: Configurar todas las variables del backend en Railway dashboard**

En el servicio backend → Variables, agregar:

```
SECRET_KEY=<el valor generado en Step 1>
ENVIRONMENT=production
DEBUG=False
BACKEND_CORS_ORIGINS=["https://viajamos.vercel.app"]
GOOGLE_CLIENT_ID=<el client id real de Google Console>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME=Viajamos
API_V1_STR=/api/v1
RATE_LIMIT_PER_MINUTE=100
```

> El dominio de Vercel (`viajamos.vercel.app`) puede no existir aún — actualizá `BACKEND_CORS_ORIGINS` después de Phase 3.

---

### Task 14: Verificar primer deploy del backend

- [ ] **Step 1: Trigger del deploy**

Railway debería deployar automáticamente. Si no: en el servicio backend → Deployments → "Trigger Deploy".

- [ ] **Step 2: Ver logs del deploy**

En Deployments → click en el deploy en curso → Logs.

Expected: ver en orden:
1. Build de Docker exitoso
2. `preDeployCommand` corriendo: `alembic upgrade head` aplicando migraciones
3. Start de uvicorn: `Application startup complete`
4. Healthcheck a `/health` exitoso

- [ ] **Step 3: Probar el endpoint /health desde curl**

Run:
```bash
curl https://<tu-dominio-railway>.up.railway.app/health
```

Expected: `{"status":"healthy"}`

- [ ] **Step 4: Probar GraphQL básico**

Run:
```bash
curl -X POST https://<tu-dominio-railway>.up.railway.app/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'
```

Expected: `{"data":{"__typename":"Query"}}`

---

## Phase 3: Configurar Vercel

> **Nota:** Esta fase es manual via dashboard de Vercel.

### Task 15: Crear proyecto en Vercel

- [ ] **Step 1: Crear cuenta**

Ir a https://vercel.com e iniciar sesión con GitHub.

- [ ] **Step 2: Importar el repo**

Click en "Add New" → "Project" → seleccionar el repo `viaggiamo`.

- [ ] **Step 3: Configurar el proyecto**

- Project Name: `viajamos`
- Framework Preset: `Next.js`
- Root Directory: `frontend`
- Build Command: dejar default (`next build`)
- Output Directory: dejar default (`.next`)
- Install Command: dejar default (`npm install`)

> NO hacer click en "Deploy" todavía — primero configurar variables.

---

### Task 16: Configurar variables de entorno del frontend

- [ ] **Step 1: Agregar variables en Vercel**

En la pantalla de Configure Project (o luego en Settings → Environment Variables), agregar:

```
NEXT_PUBLIC_GRAPHQL_URL=https://<tu-dominio-railway>.up.railway.app/graphql
NEXT_PUBLIC_API_URL=https://<tu-dominio-railway>.up.railway.app
NEXT_PUBLIC_APP_URL=https://viajamos.vercel.app
NEXT_PUBLIC_APP_NAME=Viajamos
NEXT_PUBLIC_GOOGLE_CLIENT_ID=<el client id real de Google Console>
NODE_ENV=production
```

> Reemplazar `<tu-dominio-railway>` con el subdominio anotado en Task 10.

- [ ] **Step 2: Lanzar el deploy**

Click en "Deploy". Esperar que termine (3-5 min).

- [ ] **Step 3: Anotar el dominio asignado por Vercel**

En Settings → Domains, anotar el dominio (ej. `viajamos.vercel.app`).

---

### Task 17: Actualizar BACKEND_CORS_ORIGINS en Railway con el dominio real de Vercel

- [ ] **Step 1: Editar la variable en Railway**

En Railway → backend → Variables → editar `BACKEND_CORS_ORIGINS`:

```
BACKEND_CORS_ORIGINS=["https://viajamos.vercel.app"]
```

(Reemplazar con el dominio real anotado en Task 16 si difiere.)

#### ⚠️ Importante: El dominio va sin el / final

- [ ] **Step 2: Esperar redeploy automático**

Railway redeploya automáticamente al cambiar variables. Verificar en Deployments.

- [ ] **Step 3: Verificar que el frontend conecta**

Abrir `https://<dominio-vercel>` en el browser. Abrir DevTools → Network. Hacer cualquier acción que dispare una request a `/graphql`.

Expected: la request al backend devuelve 200 sin error CORS.

---

## Phase 4: Configurar GitHub

### Task 18: Agregar SECRET_KEY a GitHub Secrets

- [ ] **Step 1: Generar un valor para tests**

Cualquier valor (no necesita ser el de producción). Por ejemplo:

```bash
openssl rand -hex 32
```

- [ ] **Step 2: Agregar el secret**

Run:
```bash
gh secret set SECRET_KEY --body "<el valor generado>"
```

Expected: `✓ Set Actions secret SECRET_KEY for <usuario>/<repo>`

---

### Task 19: Activar branch protection en main

- [ ] **Step 1: Ir a configuración de branch protection**

GitHub → Settings → Branches → "Add branch protection rule".

- [ ] **Step 2: Configurar la regla**

- Branch name pattern: `main`
- ✅ Require a pull request before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- En "Status checks that are required": agregar `Backend CI (lint + tests)` y `Frontend CI (type-check + lint)` (deben aparecer porque ya corrieron al menos una vez)

Click en "Create" / "Save changes".

- [ ] **Step 3: Verificar que la regla está activa**

Run:
```bash
gh api repos/:owner/:repo/branches/main/protection | python3 -m json.tool | head -30
```

Expected: el output incluye `required_status_checks` con los dos jobs listados.

---

## Phase 5: Cargar mock data para probar el MVP

### Task 20: Ejecutar el script de seed en Railway

**Why:** Para tener datos de prueba en producción y poder validar el flujo end-to-end de la beta cerrada.

- [ ] **Step 1: Instalar Railway CLI localmente**

Run:
```bash
npm install -g @railway/cli
railway login
```

Expected: navegador se abre, autenticación exitosa.

- [ ] **Step 2: Linkear el proyecto local a Railway**

Run:
```bash
cd backend && railway link
```

Seleccionar el proyecto `viajamos` y el servicio `backend`.

- [ ] **Step 3: Verificar que el script existe y es ejecutable**

Run:
```bash
ls -la backend/scripts/load_sample_data.py
```

Expected: archivo existe.

- [ ] **Step 4: Ejecutar el seed contra la DB de Railway**

Run:
```bash
cd backend && railway run uv run python scripts/load_sample_data.py
```

Expected: el script imprime mensajes de carga de users, vehicles, trips, bookings, ratings y termina sin errores.

- [ ] **Step 5: Verificar que los datos cargaron**

Run:
```bash
curl -X POST https://<tu-dominio-railway>.up.railway.app/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ users { id email firstName } }"}'
```

> Si la query `users` requiere auth, usar otra query pública o conectarse a la DB con `railway connect postgres`.

Expected: lista de usuarios cargados.

---

## Phase 6: Post-deploy

### Task 21: Actualizar Google Console con dominios de producción

- [ ] **Step 1: Ir a Google Cloud Console**

https://console.cloud.google.com → APIs & Services → Credentials → click en el OAuth 2.0 Client ID existente.

- [ ] **Step 2: Agregar Authorized JavaScript origins**

Agregar:
- `https://<dominio-vercel>` (ej. `https://viajamos.vercel.app`)

- [ ] **Step 3: Agregar Authorized redirect URIs**

Agregar (si la app las usa):
- `https://<dominio-vercel>/auth/callback`
- `https://<dominio-vercel>/login`

- [ ] **Step 4: Guardar cambios**

Click en "Save". Esperar ~5 minutos a que propague.

---

### Task 22: Smoke test manual end-to-end

- [ ] **Step 1: Registro con email**

1. Abrir `https://<dominio-vercel>`
2. Click en "Registrarse"
3. Completar el formulario y enviar
4. Expected: usuario creado, redirect a página principal autenticada

- [ ] **Step 2: Login con email**

1. Logout
2. Click en "Iniciar sesión"
3. Login con las credenciales de Step 1
4. Expected: sesión iniciada

- [ ] **Step 3: Login con Google**

1. Logout
2. Click en "Login con Google"
3. Completar flujo OAuth
4. Expected: sesión iniciada con cuenta Google

- [ ] **Step 4: Crear un viaje**

1. Ir a "Crear viaje"
2. Completar formulario con datos válidos
3. Submit
4. Expected: viaje creado, aparece en el listado

- [ ] **Step 5: Reservar un viaje**

1. Logout y login con otro usuario (de los seedeados)
2. Buscar un viaje disponible
3. Reservarlo
4. Expected: booking creado, aparece en "Mis reservas"

- [ ] **Step 6: Verificar logs en Railway**

Railway → backend → Logs. Buscar errores 5xx o tracebacks. Expected: ninguno.

- [ ] **Step 7: Verificar logs en Vercel**

Vercel → project → Logs / Runtime Logs. Expected: ninguno crítico.

---

## Plan complete

**Resumen de lo que queda en producción:**
- ✅ Backend FastAPI + GraphQL + rate limiting en Railway con migraciones automáticas
- ✅ PostgreSQL 15 y Redis 7 managed por Railway
- ✅ Frontend Next.js en Vercel con deploy automático
- ✅ CI en GitHub Actions bloqueando merges con tests/lint rojos
- ✅ Branch protection en `main`
- ✅ Mock data cargada para validación
- ✅ Google OAuth funcionando contra dominios de producción

**Pendientes documentados como "futuro" en el spec:**
- Sentry para error tracking
- Backups automáticos de PostgreSQL (bloqueante antes de aceptar usuarios reales)
- Dominio propio
- Entorno de staging
