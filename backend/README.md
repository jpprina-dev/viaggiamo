# Viaggiamo Backend - FastAPI

Backend API para el MVP de carpooling Viaggiamo, desarrollado con FastAPI, SQLAlchemy 2.0 y PostgreSQL.

## 🚀 Características

- **FastAPI** con documentación automática
- **SQLAlchemy 2.0** con soporte async
- **PostgreSQL** como base de datos principal
- **Redis** para caché y sesiones
- **JWT Authentication** con tokens seguros
- **Alembic** para migraciones de base de datos
- **Pydantic v2** para validación de datos
- **uv** como gestor de dependencias
- **Docker** para containerización

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── api/                    # Endpoints de la API
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # Router principal de la API
│   │       └── endpoints/      # Endpoints específicos
│   │           ├── __init__.py
│   │           ├── auth.py     # Autenticación
│   │           ├── users.py    # Gestión de usuarios
│   │           ├── trips.py    # Gestión de viajes
│   │           └── bookings.py # Gestión de reservas
│   ├── core/                   # Configuración core
│   │   ├── __init__.py
│   │   ├── config.py          # Configuración de la aplicación
│   │   ├── database.py        # Configuración de base de datos
│   │   └── security.py        # Utilidades de seguridad
│   ├── models/                # Modelos de SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py           # Modelo base
│   │   ├── user.py           # Modelo de usuario
│   │   ├── trip.py           # Modelo de viaje
│   │   └── booking.py        # Modelo de reserva
│   └── schemas/              # Esquemas de Pydantic
│       ├── __init__.py
│       ├── user.py          # Esquemas de usuario
│       ├── trip.py          # Esquemas de viaje
│       └── booking.py       # Esquemas de reserva
├── alembic/                  # Migraciones de base de datos
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/                   # Tests unitarios
├── alembic.ini             # Configuración de Alembic
├── pyproject.toml          # Dependencias y configuración
├── env.example             # Variables de entorno de ejemplo
└── Dockerfile              # Container de Docker
```

## 🛠️ Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (gestor de dependencias)
- PostgreSQL 15+
- Redis 7+

### Instalación Local

1. **Clonar el repositorio y navegar al backend:**
   ```bash
   cd backend
   ```

2. **Instalar uv (si no lo tienes):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Instalar dependencias:**
   ```bash
   uv sync
   ```

4. **Configurar variables de entorno:**
   ```bash
   cp env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Configurar la base de datos:**
   ```bash
   # Crear base de datos PostgreSQL
   createdb viaggiamo_db
   
   # Ejecutar migraciones
   uv run alembic upgrade head
   ```

6. **Ejecutar el servidor de desarrollo:**
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Instalación con Docker

```bash
# Desde la raíz del proyecto
docker-compose up -d backend
```

## 🔧 Variables de Entorno

Crea un archivo `.env` basado en `env.example`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://viaggiamo:password@localhost:5432/viaggiamo_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_STR=/api/v1
PROJECT_NAME=Viaggiamo

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Environment
ENVIRONMENT=development
DEBUG=True
```

## 📚 API Endpoints

### Autenticación (`/api/v1/auth`)

- `POST /register` - Registro de usuario
- `POST /login` - Inicio de sesión
- `GET /me` - Información del usuario actual

### Usuarios (`/api/v1/users`)

- `GET /me` - Perfil del usuario actual
- `PUT /me` - Actualizar perfil
- `GET /{user_id}` - Obtener usuario por ID

### Viajes (`/api/v1/trips`)

- `POST /` - Crear nuevo viaje
- `GET /` - Listar viajes disponibles (con filtros)
- `GET /{trip_id}` - Obtener viaje por ID
- `PUT /{trip_id}` - Actualizar viaje
- `DELETE /{trip_id}` - Eliminar viaje
- `GET /my/trips` - Mis viajes como conductor

### Reservas (`/api/v1/bookings`)

- `POST /` - Crear nueva reserva
- `GET /` - Mis reservas como pasajero
- `GET /{booking_id}` - Obtener reserva por ID
- `PUT /{booking_id}` - Actualizar reserva
- `DELETE /{booking_id}` - Cancelar reserva
- `GET /trip/{trip_id}/bookings` - Reservas de un viaje (solo conductor)

## 🗄️ Modelos de Base de Datos

### User
- `id` - ID único del usuario
- `email` - Email único
- `username` - Nombre de usuario único
- `full_name` - Nombre completo
- `hashed_password` - Contraseña hasheada
- `is_active` - Estado activo/inactivo
- `is_verified` - Estado verificado
- `phone` - Teléfono (opcional)
- `profile_picture` - URL de foto de perfil
- `created_at` - Fecha de creación
- `updated_at` - Fecha de actualización

### Trip
- `id` - ID único del viaje
- `driver_id` - ID del conductor (FK a User)
- `origin` - Origen del viaje
- `destination` - Destino del viaje
- `departure_time` - Fecha y hora de salida
- `available_seats` - Asientos disponibles
- `total_seats` - Total de asientos
- `price_per_seat` - Precio por asiento
- `description` - Descripción del viaje
- `is_active` - Estado activo/inactivo
- `is_completed` - Estado completado
- `created_at` - Fecha de creación
- `updated_at` - Fecha de actualización

### Booking
- `id` - ID único de la reserva
- `trip_id` - ID del viaje (FK a Trip)
- `passenger_id` - ID del pasajero (FK a User)
- `seats_requested` - Asientos solicitados
- `total_price` - Precio total
- `status` - Estado (pending, confirmed, cancelled)
- `notes` - Notas adicionales
- `booking_time` - Fecha y hora de la reserva
- `created_at` - Fecha de creación
- `updated_at` - Fecha de actualización

## 🔐 Autenticación

El sistema utiliza JWT (JSON Web Tokens) para la autenticación:

1. **Registro/Login**: El usuario se autentica con email y contraseña
2. **Token JWT**: Se genera un token con expiración configurable
3. **Headers**: Incluir el token en el header `Authorization: Bearer <token>`
4. **Protección**: Los endpoints protegidos requieren token válido

### Ejemplo de uso:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"

# Usar token en requests
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <your-jwt-token>"
```

## 🗃️ Migraciones de Base de Datos

### Comandos de Alembic:

```bash
# Crear nueva migración
uv run alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
uv run alembic upgrade head

# Revertir migración
uv run alembic downgrade -1

# Ver historial
uv run alembic history

# Ver estado actual
uv run alembic current
```

### Crear migración inicial:

```bash
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
uv run pytest

# Ejecutar tests con coverage
uv run pytest --cov=app

# Ejecutar tests específicos
uv run pytest tests/test_auth.py

# Ejecutar tests en modo verbose
uv run pytest -v
```

## 📊 Documentación de la API

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🚀 Comandos de Desarrollo

```bash
# Ejecutar servidor de desarrollo
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ejecutar con debug
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

# Ejecutar en modo producción
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Linting y formateo
uv run black .
uv run isort .
uv run flake8 .

# Type checking
uv run mypy app/
```

## 🐳 Docker

### Construir imagen:

```bash
docker build -t viaggiamo-backend .
```

### Ejecutar contenedor:

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db \
  -e SECRET_KEY=your-secret-key \
  viaggiamo-backend
```

### Con docker-compose:

```bash
# Desde la raíz del proyecto
docker-compose up -d backend
```

## 🔍 Debugging

### Logs en desarrollo:

```bash
# Ejecutar con logs detallados
uv run uvicorn app.main:app --reload --log-level debug
```

### Base de datos:

```bash
# Acceder a PostgreSQL
psql -U viaggiamo -d viaggiamo_db -h localhost

# Conectar a Redis
redis-cli -h localhost -p 6379
```

## 📈 Performance

### Optimizaciones incluidas:

- **Async/await** para operaciones I/O
- **Connection pooling** para PostgreSQL
- **Redis caching** para sesiones
- **Pydantic v2** para serialización rápida
- **Health checks** para monitoreo

### Monitoreo:

```bash
# Health check
curl http://localhost:8000/health

# Métricas de la aplicación
curl http://localhost:8000/metrics
```

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

### Estándares de código:

- Seguir PEP 8 para Python
- Usar type hints en todas las funciones
- Documentar funciones públicas
- Escribir tests para nuevas funcionalidades
- Usar commits convencionales

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación de la API en `/docs`
2. Consulta los issues existentes
3. Crea un nuevo issue con detalles del problema
4. Contacta al equipo en jpprina@gmail.com
