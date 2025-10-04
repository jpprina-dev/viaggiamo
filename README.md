# Viaggiamo - MVP de Carpooling

Un MVP de carpooling desarrollado con FastAPI (backend), Next.js PWA (frontend) y Docker.

## Estructura del Proyecto

```
viaggiamo/
├── backend/          # API FastAPI
├── frontend/         # Next.js PWA
├── infra/           # Configuración de infraestructura
├── docker-compose.yml
├── pyproject.toml   # Configuración de uv
└── README.md
```

## Requisitos Previos

- Docker y Docker Compose
- [uv](https://github.com/astral-sh/uv) (gestor de dependencias Python)
- Node.js 18+ (para desarrollo frontend)

## Instalación y Arranque

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd viaggiamo
```

### 2. Instalar dependencias Python con uv

```bash
# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Instalar dependencias del backend
cd backend
uv sync
```

### 3. Instalar dependencias del frontend

```bash
cd frontend
npm install
```

### 4. Configurar variables de entorno

Copia los archivos de ejemplo y configura las variables:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

### 5. Arrancar con Docker Compose

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

Esto levantará:
- PostgreSQL (puerto 5432)
- Redis (puerto 6379)
- Backend FastAPI (puerto 8000)
- Frontend Next.js (puerto 3000)

### 6. Acceder a la aplicación

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Desarrollo

### Backend (FastAPI)

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Next.js)

```bash
cd frontend
npm run dev
```

### Base de datos

Para ejecutar migraciones:

```bash
cd backend
uv run alembic upgrade head
```

## Comandos Útiles

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Reiniciar un servicio específico
docker-compose restart backend

# Detener todos los servicios
docker-compose down

# Limpiar volúmenes (¡CUIDADO! Borra datos)
docker-compose down -v
```

## Tecnologías Utilizadas

### Backend
- FastAPI
- SQLAlchemy 2.0
- Alembic (migraciones)
- PostgreSQL
- Redis
- Pydantic v2

### Frontend
- Next.js 14
- TypeScript
- PWA
- Tailwind CSS

### Infraestructura
- Docker & Docker Compose
- PostgreSQL
- Redis
- uv (gestor de dependencias Python)

## Estructura de la API

La API incluye endpoints para:
- Autenticación de usuarios
- Gestión de viajes
- Búsqueda de carpooling
- Reservas de asientos
- Perfil de usuario

Documentación completa disponible en `/docs` cuando el servidor esté ejecutándose.
