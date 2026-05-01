# Diseño: Deploy a Producción — Viajamos MVP

**Fecha:** 2026-05-01
**Estado:** Aprobado

## Contexto

Viajamos es un monorepo con backend FastAPI + Strawberry GraphQL y frontend Next.js 14. El objetivo es llevar el MVP a producción con deploys automáticos desde GitHub, manteniendo el entorno local de desarrollo sin cambios. Esta primera versión es una **beta cerrada** — solo los desarrolladores van a interactuar con la app, no usuarios reales.

## Arquitectura

```text
GitHub (main branch)
       │
       ├── push → GitHub Actions CI
       │              ├── pytest + ruff (backend)
       │              ├── tsc --noEmit + lint (frontend)
       │              └── ✅ verde → Railway y Vercel despliegan
       │
       ├── Railway
       │     ├── viajamos-backend  → viajamos-backend.up.railway.app
       │     │     └── releaseCommand: alembic upgrade head (corre en cada deploy)
       │     ├── PostgreSQL 15     → managed, URL inyectada automáticamente
       │     └── Redis 7           → managed, URL inyectada automáticamente
       │
       └── Vercel
             └── viajamos.vercel.app
                   └── se comunica con backend via NEXT_PUBLIC_GRAPHQL_URL
```

**Decisiones clave:**

- Railway para backend/DB/Redis: latencia cero entre servicios, integración nativa
- Vercel para frontend: plataforma nativa de Next.js, mejor SSR y edge caching
- Railway PostgreSQL sobre Supabase: backend y DB en el mismo datacenter, sin overhead de features no usados
- Sin staging por ahora: un solo entorno de producción, apropiado para MVP en beta cerrada
- CORS estricto: solo el dominio canónico de Vercel se permite (los preview deployments no podrán llamar al backend de producción — aceptado como trade-off de seguridad)

## Costo estimado mensual

| Servicio | Plan | Costo aproximado |
|---|---|---|
| Railway | Hobby ($5 base + uso) | ~$10–20 USD/mes (backend + PostgreSQL + Redis) |
| Vercel | Hobby (free) | $0 |
| Sentry (futuro) | Developer (free tier) | $0 (hasta 5k errors/mes) |
| **Total** | | **~$10–20 USD/mes** |

## Entornos

### Local (sin cambios)

- `docker-compose.yml` levanta PostgreSQL + Redis + backend + frontend
- Los archivos `.env` actuales quedan intactos
- Flujo: `docker compose up` o comandos uv/pnpm individuales

### Producción

- Variables de entorno configuradas exclusivamente en dashboards de Railway y Vercel
- Los `.env` del repo nunca llegan a producción
- `.env.example` documenta qué variables existen (commiteado, sin valores reales)

## Cambios necesarios en el codebase

### Críticos

1. **`docker-compose.yml`**: cambiar frontend de `Dockerfile.dev` → `Dockerfile`
   > Aclaración: este cambio sirve solo para poder probar producción local-like vía Docker. **Vercel ignora completamente el `Dockerfile`** y usa su propio build de Next.js — el deploy real no pasa por Docker.
2. **`railway.json`**: agregar config con start command y `releaseCommand: alembic upgrade head` para correr migraciones automáticamente en cada deploy
3. **`next.config.js`**: agregar dominio Railway en `images.remotePatterns`
4. **`.github/workflows/ci.yml`**: pipeline CI con tests de backend y frontend, alineado con `.pre-commit-config.yaml`

### Importantes

5. **`backend/.env.example`**: documentar variables requeridas sin valores reales
6. **`frontend/.env.example`**: ídem para frontend
7. **Rate limiting básico** en el endpoint `/graphql` (ej. `slowapi` con Redis): protege de abuso y queries pesadas. Límite por IP, valores conservadores (ej. 100 req/min).

## Verificaciones previas (ya hechas)

- ✅ `/health` endpoint existe en `backend/app/main.py:69`
- ✅ `alembic/env.py` lee `DATABASE_URL` desde `settings` (pydantic-settings → variable de entorno) — funciona en Railway sin cambios
- ✅ `next.config.js` ya tiene `output: 'standalone'`
- ✅ Existe `backend/scripts/load_sample_data.py` para seed de mock data desde `data/*.json`

## Variables de entorno en producción

### Railway (backend)

```text
SECRET_KEY=<valor fuerte, generar con: openssl rand -hex 32>
DATABASE_URL=<inyectado automáticamente por Railway PostgreSQL>
REDIS_URL=<inyectado automáticamente por Railway Redis>
ENVIRONMENT=production
DEBUG=False
BACKEND_CORS_ORIGINS=["https://viajamos.vercel.app"]
GOOGLE_CLIENT_ID=<client id de Google Console>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME=Viajamos
API_V1_STR=/api/v1
```

### Vercel (frontend)

```text
NEXT_PUBLIC_GRAPHQL_URL=https://viajamos-backend.up.railway.app/graphql
NEXT_PUBLIC_API_URL=https://viajamos-backend.up.railway.app
NEXT_PUBLIC_APP_URL=https://viajamos.vercel.app
NEXT_PUBLIC_APP_NAME=Viajamos
NEXT_PUBLIC_GOOGLE_CLIENT_ID=<client id de Google Console>
NODE_ENV=production
```

### GitHub Secrets (para CI)

```text
SECRET_KEY=<cualquier valor, solo para tests>
```

> `DATABASE_URL` para CI usa el PostgreSQL service de GitHub Actions, no Railway.

### ⚠️ Importante: variables `NEXT_PUBLIC_*` se bakean en build time

Las variables que empiezan con `NEXT_PUBLIC_*` no se inyectan en runtime — Next.js las **embebe en el bundle durante el build**. Si cambiás cualquiera de estas variables en el dashboard de Vercel:

1. Ir a Vercel → Project → Deployments
2. Encontrar el último deploy exitoso
3. Click en el menú "..." → "Redeploy"
4. **Desmarcar** "Use existing Build Cache" (importante para que tome los nuevos valores)
5. Confirmar redeploy

Variables de backend (Railway) sí toman efecto al reiniciar el servicio sin rebuild.

## CI/CD — GitHub Actions

Archivo: `.github/workflows/ci.yml`

**Trigger:** push y pull_request a `main`

**Jobs:**

1. `backend-ci`:
   - Levanta PostgreSQL 15 como service
   - Instala uv y dependencias del backend
   - Corre `pytest` con cobertura
   - Corre `ruff check .`
   - (alineado con lo que corre `.pre-commit-config.yaml` — el CI replica lo que valida pre-commit local para evitar divergencia)

2. `frontend-ci`:
   - Instala Node 18 y dependencias con `npm install`
   - Corre `tsc --noEmit` (type check)
   - Corre `npm run lint`

**Branch protection en GitHub:**

- `main` requiere que ambos jobs pasen antes de merge o deploy efectivo

## Observabilidad y logs

**Hoy (MVP):**

- Usar logs de **uvicorn** por defecto. Railway captura stdout/stderr automáticamente y los muestra en su dashboard.
- Para debugging puntual: Railway → backend service → Logs tab.

**Futuro (a verificar/implementar después):**

- Integrar **Sentry** (free tier: 5k errores/mes) para tracking de excepciones automatizado y alertas por email.
- Logs estructurados (JSON) si el volumen crece.

## Backups de PostgreSQL

**Hoy (beta cerrada, solo desarrolladores):**

- Sin backups automáticos. Aceptado porque no hay usuarios reales y los datos se pueden regenerar desde mocks.

**Futuro (cuando se abra a usuarios reales):**

- Definir cadencia (mínimo: backup semanal manual desde dashboard de Railway).
- Evaluar `pg_dump` programado vía GitHub Actions o servicio externo.
- **Importante**: este punto es bloqueante antes de aceptar usuarios reales — no lanzar a producción real sin esto resuelto.

## Storage del directorio `data/`

El directorio `data/` contiene **mock datasets JSON** (`users.json`, `vehicles.json`, `trips.json`, `bookings.json`, `ratings.json`) usados para seed local. **No se necesita persistencia en Railway** porque:

- Los JSON son fuente, no datos generados en runtime
- El backend los lee solo cuando se ejecuta el script de seed
- Para ejecutar el seed en producción se usa `backend/scripts/load_sample_data.py`

Si en el futuro aparecen archivos generados en runtime (uploads de usuarios, exports), habrá que mover esos a almacenamiento externo (S3 / Cloudflare R2 / Railway Volumes).

## Pasos de implementación

### Fase 1 — Preparar el codebase

1. Corregir `docker-compose.yml`: `Dockerfile.dev` → `Dockerfile` en el frontend
2. Crear `backend/.env.example` con todas las variables (sin valores reales)
3. Crear `frontend/.env.example` con todas las variables (sin valores reales)
4. Crear `railway.json` en `backend/` con start command y `releaseCommand: alembic upgrade head`
5. Actualizar `next.config.js` con dominio Railway en `remotePatterns`
6. Implementar rate limiting básico en `/graphql` (slowapi + Redis)
7. Crear `.github/workflows/ci.yml` (alineado con `.pre-commit-config.yaml`)
8. Commitear y pushear todo a `main`

### Fase 2 — Configurar Railway

9. Crear cuenta en railway.app y nuevo proyecto "viajamos"
10. Agregar servicio "GitHub Repo" apuntando al monorepo, root directory: `backend/`
11. Agregar plugin PostgreSQL 15
12. Agregar plugin Redis 7
13. Configurar variables de entorno del backend en el dashboard
14. Verificar primer deploy exitoso: `GET /health` devuelve 200
    > Las migraciones se corren solas via `releaseCommand` — no hace falta paso manual.

### Fase 3 — Configurar Vercel

15. Crear proyecto en vercel.com desde el mismo repo GitHub
16. Configurar root directory: `frontend/`
17. Framework preset: Next.js
18. Configurar variables de entorno del frontend en el dashboard
19. Verificar primer deploy exitoso: app carga y conecta con backend

### Fase 4 — Configurar GitHub

20. Agregar secret `SECRET_KEY` en GitHub → Settings → Secrets → Actions
21. Activar branch protection en `main`: requerir status checks de CI

### Fase 5 — Cargar datos mock para probar el MVP

22. Conectar al backend de Railway (vía `railway run` CLI o shell del dashboard)
23. Ejecutar: `uv run python scripts/load_sample_data.py`
24. Verificar carga: hacer query GraphQL pidiendo `users`, `trips`, etc.

### Fase 6 — Post-deploy

25. Actualizar Google Console: agregar dominios de producción en "Authorized JavaScript origins" y "Authorized redirect URIs"
26. Smoke test manual: registro, login con email, login con Google, crear viaje, reservar viaje

## Consideraciones futuras (fuera de scope del MVP)

- **Dominio propio** (ej. `viajamos.app`)
- **Entorno de staging** (`dev` branch → staging en Railway)
- **Sentry** para error tracking (verificar e implementar)
- **Backups automáticos de PostgreSQL** — bloqueante antes de aceptar usuarios reales
- **Vercel preview deployments con CORS dinámico** o staging separado para previews
- **Monitoreo y alertas de uptime** (Railway tiene métricas básicas; UptimeRobot free tier como complemento)
- **Rotación de `SECRET_KEY`** y estrategia de invalidación de JWTs viejos
