# Diseño: Deploy a Producción — Viajamos MVP

**Fecha:** 2026-05-01
**Estado:** Aprobado

## Contexto

Viajamos es un monorepo con backend FastAPI + Strawberry GraphQL y frontend Next.js 14. El objetivo es llevar el MVP a producción con deploys automáticos desde GitHub, manteniendo el entorno local de desarrollo sin cambios.

## Arquitectura

```
GitHub (main branch)
       │
       ├── push → GitHub Actions CI
       │              ├── pytest + ruff (backend)
       │              ├── tsc --noEmit (frontend)
       │              └── ✅ verde → Railway y Vercel despliegan
       │
       ├── Railway
       │     ├── viajamos-backend  → viajamos-backend.up.railway.app
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
- Sin staging por ahora: un solo entorno de producción, apropiado para MVP en desarrollo individual

## Entornos

### Local (sin cambios)
- `docker-compose.yml` levanta PostgreSQL + Redis + backend + frontend
- Los archivos `.env` actuales quedan intactos
- Flujo: `docker compose up` o comandos uv/pnpm individuales

### Producción
- Variables de entorno configuradas exclusivamente en dashboards de Railway y Vercel
- Los `.env` del repo nunca llegan a producción
- `.env.example` documentan qué variables existen (commiteado, sin valores reales)

## Cambios necesarios en el codebase

### Críticos
1. **`docker-compose.yml`**: cambiar frontend de `Dockerfile.dev` → `Dockerfile`
2. **`railway.json`**: agregar config con start command del backend
3. **`next.config.js`**: agregar dominio Railway en `images.remotePatterns`
4. **`.github/workflows/ci.yml`**: pipeline CI con tests de backend y frontend

### Importantes
5. **`backend/.env.example`**: documentar variables requeridas sin valores reales
6. **`frontend/.env.example`**: ídem para frontend

## Variables de entorno en producción

### Railway (backend)
```
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
```
NEXT_PUBLIC_GRAPHQL_URL=https://viajamos-backend.up.railway.app/graphql
NEXT_PUBLIC_API_URL=https://viajamos-backend.up.railway.app
NEXT_PUBLIC_APP_URL=https://viajamos.vercel.app
NEXT_PUBLIC_APP_NAME=Viajamos
NEXT_PUBLIC_GOOGLE_CLIENT_ID=<client id de Google Console>
NODE_ENV=production
```

### GitHub Secrets (para CI)
```
SECRET_KEY=<cualquier valor, solo para tests>
```
> `DATABASE_URL` para CI usa el PostgreSQL service de GitHub Actions, no Railway.

## CI/CD — GitHub Actions

Archivo: `.github/workflows/ci.yml`

**Trigger:** push y pull_request a `main`

**Jobs:**
1. `backend-ci`:
   - Levanta PostgreSQL 15 como service
   - Instala uv y dependencias del backend
   - Corre `pytest` con cobertura
   - Corre `ruff check .`

2. `frontend-ci`:
   - Instala Node 18 y dependencias con `npm install`
   - Corre `tsc --noEmit` (type check)
   - Corre `npm run lint`

**Branch protection en GitHub:**
- `main` requiere que ambos jobs pasen antes de merge o deploy efectivo

## Pasos de implementación

### Fase 1 — Preparar el codebase
1. Corregir `docker-compose.yml`: `Dockerfile.dev` → `Dockerfile` en el frontend
2. Crear `backend/.env.example` con todas las variables (sin valores reales)
3. Crear `frontend/.env.example` con todas las variables (sin valores reales)
4. Crear `railway.json` en la raíz del backend
5. Actualizar `next.config.js` con dominio Railway en `remotePatterns`
6. Crear `.github/workflows/ci.yml`
7. Commitear y pushear todo a `main`

### Fase 2 — Configurar Railway
8. Crear cuenta en railway.app y nuevo proyecto "viajamos"
9. Agregar servicio "GitHub Repo" apuntando al monorepo, root directory: `backend/`
10. Agregar plugin PostgreSQL 15
11. Agregar plugin Redis 7
12. Configurar variables de entorno del backend en el dashboard
13. Verificar primer deploy exitoso: `GET /health` devuelve 200

### Fase 3 — Correr migraciones
14. En Railway → backend service → shell o deploy command: `alembic upgrade head`

### Fase 4 — Configurar Vercel
15. Crear proyecto en vercel.com desde el mismo repo GitHub
16. Configurar root directory: `frontend/`
17. Framework preset: Next.js
18. Configurar variables de entorno del frontend en el dashboard
19. Verificar primer deploy exitoso: app carga y conecta con backend

### Fase 5 — Configurar GitHub
20. Agregar secret `SECRET_KEY` en GitHub → Settings → Secrets → Actions
21. Activar branch protection en `main`: requerir status checks de CI

### Fase 6 — Post-deploy
22. Actualizar Google Console: agregar dominios de producción en "Authorized JavaScript origins" y "Authorized redirect URIs"
23. Smoke test manual: registro, login con email, login con Google, crear viaje

## Consideraciones futuras (fuera de scope del MVP)

- Dominio propio (ej. `viajamos.app`)
- Entorno de staging (`dev` branch → staging en Railway)
- Backups automáticos de PostgreSQL
- Monitoreo y alertas (Railway tiene métricas básicas integradas)
