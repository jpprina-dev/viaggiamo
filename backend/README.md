# Viaggiamo Backend - GraphQL API

Backend API para el MVP de carpooling Viaggiamo, desarrollado con FastAPI, GraphQL (Strawberry), SQLAlchemy 2.0 y PostgreSQL.

## 🚀 Características

- **FastAPI** con documentación automática
- **GraphQL** con Strawberry para API moderna y flexible
- **SQLAlchemy 2.0** con soporte async
- **PostgreSQL** como base de datos principal
- **Redis** para caché y sesiones
- **JWT Authentication** con tokens seguros
- **OAuth/SSO Support** - Google, Facebook, GitHub (extensible)
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
│   ├── graphql/                # GraphQL API
│   │   ├── __init__.py
│   │   ├── auth.py            # Autenticación para GraphQL
│   │   ├── context.py         # Contexto de GraphQL
│   │   ├── resolvers.py       # Resolvers de GraphQL
│   │   ├── schema.py          # Schema de GraphQL
│   │   └── types.py           # Tipos de GraphQL
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
PROJECT_NAME=Viaggiamo

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Environment
ENVIRONMENT=development
DEBUG=True
```

## 📚 GraphQL API

### Endpoint Principal
- **GraphQL Playground**: http://localhost:8000/graphql

### Queries Disponibles

#### Autenticación y Usuarios
- `me` - Información del usuario actual autenticado
- `user(userId: Int!)` - Obtener usuario por ID

#### Gestión de Vehículos
- `myVehicles` - Mis vehículos registrados
- `vehicle(vehicleId: Int!)` - Obtener vehículo por ID
- `vehicle(tripId: Int!)` - Obtener vehículo asociado a un viaje

#### Viajes
- `trips(origin: String, destination: String, limit: Int, offset: Int)` - Listar viajes disponibles con filtros
- `trip(tripId: Int!)` - Obtener viaje por ID
- `myTrips` - Mis viajes como conductor

#### Reservas
- `myBookings` - Mis reservas como pasajero

### Mutations Disponibles

#### Autenticación
- `register(userInput: UserCreateInput!)` - Registro de nuevo usuario
- `login(loginInput: LoginInput!)` - Inicio de sesión (devuelve JWT token)
- `loginWithOauth(oauthInput: OAuthLoginInput!)` - Login/registro con OAuth (Google, Facebook, GitHub)

#### Gestión de Vehículos
- `createVehicle(vehicleInput: VehicleCreateInput!)` - Registrar nuevo vehículo (requiere autenticación)
- `updateVehicle(vehicleId: Int!, vehicleInput: VehicleUpdateInput!)` - Actualizar vehículo (requiere autenticación)
- `deleteVehicle(vehicleId: Int!)` - Eliminar vehículo (requiere autenticación)

#### Gestión de Viajes
- `createTrip(tripInput: TripCreateInput!)` - Crear nuevo viaje (requiere autenticación y vehículo)
- `updateTrip(tripId: Int!, tripInput: TripUpdateInput!)` - Actualizar viaje (requiere autenticación)
- `deleteTrip(tripId: Int!)` - Eliminar viaje (requiere autenticación)

#### Gestión de Reservas
- `createBooking(bookingInput: BookingCreateInput!)` - Crear nueva reserva (requiere autenticación)
- `updateBooking(bookingId: Int!, bookingInput: BookingUpdateInput!)` - Actualizar reserva (requiere autenticación)

### Ventajas de GraphQL

- **Flexibilidad**: Solicita exactamente los campos que necesitas
- **Una sola solicitud**: Obtén datos relacionados en una sola consulta
- **Tipado fuerte**: Schema auto-documentado con tipos estrictos
- **Introspection**: Explora el schema directamente en GraphQL Playground
- **Versionado**: No necesitas versionar endpoints, evoluciona el schema gradualmente

### Ejemplo de Query Compleja

```graphql
query GetTripWithBookings($tripId: Int!) {
  trip(tripId: $tripId) {
    id
    origin
    destination
    departureTime
    availableSeats
    pricePerSeat
    description
    driver {
      id
      username
      name
      lastName
    }
  }
  myBookings {
    id
    seatsRequested
    totalPrice
    status
    trip {
      id
      origin
      destination
      departureTime
    }
  }
}
```

### Ejemplo de Query con Vehículos

```graphql
query GetTripWithVehicle($tripId: Int!) {
  trip(tripId: $tripId) {
    id
    origin
    destination
    departureTime
    vehicleId
    tripLegalComplianceAck
  }
  vehicle(tripId: $tripId) {
    id
    make
    model
    year
    licensePlate
    seats
    isActive
  }
}
```

### Ejemplo de Gestión de Vehículos

```graphql
# Crear vehículo
mutation {
  createVehicle(vehicleInput: {
    make: "Toyota"
    model: "Corolla"
    year: 2020
    licensePlate: "ABC-123"
    seats: 5
    color: "Blue"
    vehicleLegalComplianceAck: true
  }) {
    id
    make
    model
    licensePlate
  }
}

# Listar mis vehículos
query {
  myVehicles {
    id
    make
    model
    year
    licensePlate
    seats
    isActive
  }
}
```

## 🗄️ Modelos de Base de Datos

### User
- `id` - ID único del usuario
- `email` - Email único
- `username` - Nombre de usuario único
- `name` - Nombre
- `last_name` - Apellido
- `hashed_password` - Contraseña hasheada (opcional, null para usuarios OAuth)
- `identification` - Número de identificación (opcional)
- `identification_type` - Tipo de identificación (passport, national_id, drivers_license)
- `phone` - Teléfono (opcional)
- `phone_verified` - Teléfono verificado
- `email_verified` - Email verificado
- `profile_picture` - URL de foto de perfil
- `profile_short_bio` - Biografía corta del perfil
- `status` - Estado del usuario (active, suspended, under_review)
- `trip_preferences` - Preferencias de viaje (JSON: pets, children, smoking, etc.)
- `auth_provider` - Proveedor de autenticación ('local', 'google', 'facebook', 'github')
- `provider_user_id` - ID del usuario en el proveedor OAuth
- `created_at` - Fecha de creación
- `updated_at` - Fecha de actualización
- **Relationships**: trips (como conductor), bookings (como pasajero), vehicles, ratings

### Trip
- `id` - ID único del viaje
- `driver_id` - ID del conductor (FK a User)
- `vehicle_id` - ID del vehículo (FK a Vehicle) - **REQUERIDO**
- `origin` - Origen del viaje
- `destination` - Destino del viaje
- `departure_time` - Fecha y hora de salida
- `available_seats` - Asientos disponibles
- `total_seats` - Total de asientos
- `price_per_seat` - Precio por asiento
- `description` - Descripción del viaje
- `is_active` - Estado activo/inactivo
- `is_completed` - Estado completado
- `trip_legal_compliance_ack` - Aceptación de cumplimiento legal del viaje
- `created_at` - Fecha de creación
- `updated_at` - Fecha de actualización
- **Relationships**: driver (User), vehicle (Vehicle), bookings, ratings

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

### Vehicle
- `id` - ID único del vehículo
- `user_id` - ID del propietario (FK a User)
- `make` - Marca del vehículo (ej: Toyota)
- `model` - Modelo del vehículo (ej: Corolla)
- `year` - Año del vehículo
- `color` - Color del vehículo (opcional)
- `license_plate` - Placa/matrícula (único)
- `seats` - Número total de asientos
- `is_active` - Si el vehículo está disponible para viajes
- `vehicle_legal_compliance_ack` - Aceptación de cumplimiento legal del vehículo
- `created_at` - Fecha de creación
- `updated_at` - Fecha de actualización
- **Relationships**: owner (User), trips (viajes asociados)

### Rating
- `id` - ID único de la calificación
- `trip_id` - ID del viaje (FK a Trip)
- `rater_id` - ID del usuario que califica (FK a User)
- `rated_user_id` - ID del usuario calificado (FK a User)
- `role` - Rol del usuario calificado (driver o passenger)
- `rating` - Calificación (1-5 estrellas)
- `comment` - Comentario sobre la calificación (opcional)
- `created_at` - Fecha de creación
- `updated_at` - Fecha de actualización

## 🔐 Autenticación

El sistema soporta dos métodos de autenticación:

### 1. Autenticación Tradicional (Email/Password)

Utiliza JWT (JSON Web Tokens):

1. **Registro/Login**: El usuario se autentica con email y contraseña
2. **Token JWT**: Se genera un token con expiración configurable
3. **Headers**: Incluir el token en el header `Authorization: Bearer <token>`
4. **Protección**: Los endpoints protegidos requieren token válido

```graphql
# Mutation para registro
mutation RegisterUser {
  register(userInput: {
    email: "user@example.com"
    username: "testuser"
    name: "Test"
    lastName: "User"
    password: "password123"
    phone: "+1234567890"
  }) {
    id
    email
    username
    name
    lastName
    status
    emailVerified
  }
}

# Mutation para login
mutation LoginUser {
  login(loginInput: {
    email: "user@example.com"
    password: "password123"
  }) {
    accessToken
    tokenType
  }
}
```

### 2. OAuth/SSO Authentication

Soporta múltiples proveedores OAuth con arquitectura extensible:

- ✅ **Google OAuth 2.0** (implementado)
- 🚧 **Facebook OAuth** (próximamente)
- 🚧 **GitHub OAuth** (próximamente)

```graphql
# Login/Registro con Google
mutation LoginWithGoogle {
  loginWithOauth(oauthInput: {
    provider: "google"
    token: "eyJhbGciOiJSUzI1NiIsImtpZCI6..."  # Google ID token
  }) {
    accessToken
    tokenType
  }
}
```

**Características de OAuth:**
- Login automático si el usuario no existe (auto-registro)
- Vinculación de cuentas locales con OAuth
- Verificación automática de email
- Foto de perfil desde el proveedor OAuth
- Sin necesidad de contraseña

**Documentación completa:**
- [Configuración OAuth](docs/OAUTH_SETUP.md) - Guía de configuración
- [Ejemplos OAuth](docs/OAUTH_EXAMPLES.md) - Ejemplos de integración

**Variables de entorno necesarias:**
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

Ver `env.example` para configuración completa

# Query para obtener usuario actual (requiere token en header)
query GetCurrentUser {
  me {
    id
    email
    username
    name
    lastName
    status
    emailVerified
    phoneVerified
  }
}

# Query para obtener viajes
query GetTrips {
  trips(origin: "Madrid", limit: 10) {
    id
    origin
    destination
    departureTime
    availableSeats
    pricePerSeat
  }
}
```

### Headers para autenticación:
```json
{
  "Authorization": "Bearer <your-jwt-token>"
}
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

- **GraphQL Playground**: http://localhost:8000/graphql (interfaz interactiva para probar queries y mutations)
- **Health Check**: http://localhost:8000/health

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

# Probar GraphQL endpoint
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
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

1. Revisa la documentación de la API en GraphQL Playground: http://localhost:8000/graphql
2. Consulta los issues existentes
3. Crea un nuevo issue con detalles del problema
4. Contacta al equipo en jpprina@gmail.com
