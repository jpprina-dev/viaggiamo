# Infraestructura - Viaggiamo

Este directorio contiene los archivos de configuración de infraestructura para el MVP de Viaggiamo.

## Servicios

### PostgreSQL
- **Puerto**: 5432
- **Base de datos**: viaggiamo_db
- **Usuario**: viaggiamo
- **Contraseña**: viaggiamo_password

### Redis
- **Puerto**: 6379
- **Base de datos**: 0

## Configuración

### Variables de Entorno

#### Backend
```bash
DATABASE_URL=postgresql+asyncpg://viaggiamo:viaggiamo_password@postgres:5432/viaggiamo_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1
PROJECT_NAME=Viaggiamo
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
ENVIRONMENT=development
DEBUG=True
```

#### Frontend
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=production
```

## Comandos Útiles

### Levantar todos los servicios
```bash
docker compose up -d
```

### Ver logs
```bash
docker compose logs -f [service-name]
```

### Reiniciar un servicio
```bash
docker compose restart [service-name]
```

### Detener todos los servicios
```bash
docker compose down
```

### Limpiar volúmenes (¡CUIDADO! Borra datos)
```bash
docker compose down -v
```

### Acceder a la base de datos
```bash
docker compose exec postgres psql -U viaggiamo -d viaggiamo_db
```

### Acceder a Redis
```bash
docker compose exec redis redis-cli
```

## Migraciones

Para ejecutar las migraciones de la base de datos:

```bash
cd backend
docker compose exec backend uv run alembic upgrade head
```

## Monitoreo

### Health Checks
Todos los servicios incluyen health checks:
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Backend: `curl http://localhost:8000/health`
- Frontend: Verificación de puerto

### Logs
Los logs están disponibles a través de Docker Compose:
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f redis
```
