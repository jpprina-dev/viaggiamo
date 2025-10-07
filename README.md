# 🚗 Viaggiamo - Carpooling Platform

> **Una plataforma moderna de carpooling con autenticación OAuth y diseño inspirado en Viatik**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![GraphQL](https://img.shields.io/badge/GraphQL-Strawberry-ff1493.svg)](https://strawberry.rocks/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-blue.svg)](https://www.typescriptlang.org/)

## 🌟 Características Principales

- 🔐 **OAuth 2.0** - Login con Google (extensible a Facebook, GitHub)
- 🎨 **Diseño Verde** - Tema inspirado en [Viatik](https://www.viatik.com/ar)
- ⚡ **GraphQL API** - API moderna y flexible con Strawberry
- 🚀 **FastAPI Backend** - Alto rendimiento y async/await
- 💚 **Next.js Frontend** - React con Server Components y App Router
- 🔒 **Seguro** - JWT tokens, OAuth verification, Argon2 hashing
- 📱 **Responsive** - Diseño adaptable a todos los dispositivos
- 🐳 **Docker** - Containerizado y listo para producción

## 📸 Vista Previa

### Home Page (Green Theme)
- Buscador de viajes (origen, destino, fecha, pasajeros)
- Viajes destacados con precios
- Estadísticas de la comunidad
- Sección "¿Cómo funciona?"

### Login con OAuth
- Botón "Sign in with Google"
- Formulario tradicional email/password
- Diseño moderno en verde

### Dashboard
- Perfil del usuario con foto de Google
- Badge especial para usuarios OAuth
- Quick actions y estadísticas

## 🚀 Inicio Rápido

### Opción 1: Script Interactivo (Recomendado)

```bash
./quick-start.sh
```

Selecciona tu método preferido (ASDF, Docker, o solo bases de datos).

### Opción 2: Manual con ASDF

```bash
# 1. Instalar versiones con ASDF
asdf install

# 2. Configurar variables de entorno
cp backend/env.example backend/.env
cp frontend/env.example frontend/.env.local
# Editar archivos .env con credenciales de Google

# 3. Iniciar bases de datos
docker run -d --name viaggiamo-postgres \
  -e POSTGRES_DB=viaggiamo_db \
  -e POSTGRES_USER=viaggiamo \
  -e POSTGRES_PASSWORD=viaggiamo_password \
  -p 5432:5432 postgres:15-alpine

docker run -d --name viaggiamo-redis \
  -p 6379:6379 redis:7-alpine

# 4. Iniciar backend (terminal 1)
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# 5. Iniciar frontend (terminal 2)
cd frontend
npm install
npm run dev
```

### Opción 3: Docker Compose

```bash
docker compose up -d
```

## 🌐 URLs de la Aplicación

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:3000 | Home page verde inspirado en Viatik |
| **Login** | http://localhost:3000/auth/login | Login con Google OAuth |
| **Dashboard** | http://localhost:3000/dashboard | Panel de usuario |
| **GraphQL** | http://localhost:8000/graphql | GraphQL Playground |
| **API Docs** | http://localhost:8000/docs | Documentación automática |

## 🔐 Configurar Google OAuth

### 1. Obtener Credenciales

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo
3. Habilita Google+ API
4. Crea OAuth 2.0 Client ID
5. Agrega orígenes autorizados:
   - `http://localhost:3000`
   - `http://localhost:8000`

### 2. Configurar Backend

Edita `backend/.env`:
```bash
GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu-client-secret
```

### 3. Configurar Frontend

Edita `frontend/.env.local`:
```bash
NEXT_PUBLIC_GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
```

## 📁 Estructura del Proyecto

```
viaggiamo/
├── backend/                    # FastAPI + GraphQL backend
│   ├── app/
│   │   ├── core/              # Configuración, seguridad, OAuth
│   │   ├── models/            # Modelos SQLAlchemy
│   │   ├── graphql/           # Schema, resolvers, types
│   │   └── main.py
│   ├── docs/                  # Documentación OAuth
│   ├── migrations/            # Migraciones Alembic
│   └── pyproject.toml
│
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # Pages (App Router)
│   │   └── lib/              # Auth, GraphQL client
│   ├── public/
│   └── package.json
│
├── .tool-versions             # ASDF configuration
├── docker-compose.yml         # Docker setup
├── START_GUIDE.md            # Guía completa de inicio
├── IMPLEMENTATION_SUMMARY.md # Resumen de implementación
└── quick-start.sh            # Script de inicio rápido
```

## 🎨 Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Strawberry GraphQL** - GraphQL para Python
- **SQLAlchemy 2.0** - ORM con soporte async
- **PostgreSQL** - Base de datos relacional
- **Redis** - Cache y sesiones
- **Alembic** - Migraciones de base de datos
- **Pydantic v2** - Validación de datos
- **uv** - Gestor de dependencias ultra-rápido

### Frontend
- **Next.js 14** - React framework con App Router
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Utility-first CSS
- **React Hook Form** - Manejo de formularios
- **Zod** - Validación de esquemas
- **@react-oauth/google** - Integración con Google
- **graphql-request** - Cliente GraphQL

## 🔑 Funcionalidades de OAuth

### Flujo de Autenticación
1. Usuario hace click en "Sign in with Google"
2. Popup de Google se abre
3. Usuario autoriza la aplicación
4. Frontend recibe el token de Google
5. Backend verifica el token con la API de Google
6. Backend crea o encuentra el usuario
7. Backend retorna JWT token
8. Usuario es redirigido al dashboard

### Características de OAuth
- ✅ Auto-registro de nuevos usuarios
- ✅ Vinculación automática de cuentas existentes
- ✅ Importación de foto de perfil
- ✅ Verificación automática de email
- ✅ Sin necesidad de contraseña
- ✅ Username único generado automáticamente

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [START_GUIDE.md](START_GUIDE.md) | Guía completa de configuración e inicio |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Resumen de lo implementado |
| [backend/docs/OAUTH_SETUP.md](backend/docs/OAUTH_SETUP.md) | Configuración detallada de OAuth |
| [backend/docs/OAUTH_EXAMPLES.md](backend/docs/OAUTH_EXAMPLES.md) | Ejemplos de código y uso |
| [backend/README.md](backend/README.md) | Documentación del backend |

## 🧪 Probar OAuth

```bash
# 1. Iniciar la aplicación
./quick-start.sh

# 2. Abrir el navegador
open http://localhost:3000

# 3. Click en "Iniciar Sesión"
# 4. Click en "Sign in with Google"
# 5. Autorizar con tu cuenta de Google
# 6. ¡Listo! Estarás en el dashboard
```

## 🎨 Tema de Colores (Verde)

Inspirado en [Viatik](https://www.viatik.com/ar), usamos una paleta verde:

```css
Primary Green:
- 50:  #f0fdf4  /* Fondo claro */
- 500: #22c55e  /* Principal - botones, links */
- 600: #16a34a  /* Hover */
- 900: #14532d  /* Oscuro */
```

## 📊 GraphQL API

### Queries Principales

```graphql
query {
  me {
    id
    email
    fullName
    authProvider
    profilePicture
  }

  trips {
    id
    origin
    destination
    pricePerSeat
  }
}
```

### Mutations Principales

```graphql
# Login tradicional
mutation {
  login(loginInput: {
    email: "user@example.com"
    password: "password123"
  }) {
    accessToken
    tokenType
  }
}

# Login con Google
mutation {
  loginWithOauth(oauthInput: {
    provider: "google"
    token: "google-id-token..."
  }) {
    accessToken
    tokenType
  }
}
```

## 🛠️ Comandos Útiles

```bash
# Backend
cd backend
uv sync                          # Instalar dependencias
uv run alembic upgrade head      # Aplicar migraciones
uv run uvicorn app.main:app --reload  # Iniciar servidor

# Frontend
cd frontend
npm install                      # Instalar dependencias
npm run dev                      # Servidor de desarrollo
npm run build                    # Build para producción

# Docker
docker compose up -d             # Iniciar todos los servicios
docker compose logs -f           # Ver logs
docker compose down              # Detener servicios
```

## 🐛 Solución de Problemas

Ver [START_GUIDE.md](START_GUIDE.md#-solución-de-problemas) para soluciones a problemas comunes.

## 🚢 Deployment

### Backend
- Configurar variables de entorno de producción
- Cambiar `SECRET_KEY` a valor seguro
- Configurar HTTPS
- Usar PostgreSQL y Redis en la nube

### Frontend
- Configurar dominio en Google OAuth
- Actualizar `NEXT_PUBLIC_API_URL`
- Deploy en Vercel, Netlify, o similar

## 📝 Licencia

Este proyecto es un MVP de carpooling desarrollado con fines educativos.

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📞 Soporte

- 📧 Email: contacto@viaggiamo.com
- 📱 WhatsApp: +54 9 11 2862 0965
- 📚 Docs: Ver [START_GUIDE.md](START_GUIDE.md)

## 🎉 ¡Listo para Empezar!

```bash
# Inicio rápido en 3 pasos:
./quick-start.sh                 # 1. Ejecutar script
# Configurar Google OAuth          2. Obtener credenciales
# Abrir http://localhost:3000      3. ¡Disfrutar!
```

---

**Hecho con 💚 usando FastAPI, Next.js, y GraphQL**

**Inspirado en:** [Viatik.com](https://www.viatik.com/ar)

**Referencias:**
- [ASDF Version Manager](https://asdf-vm.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Strawberry GraphQL](https://strawberry.rocks/)
