# Viaggiamo Backend Documentation

This directory contains comprehensive documentation for the Viaggiamo backend API.

## 📚 Documentation Index

### 🏗️ Architecture & Structure
- **[GraphQL Architecture](GraphQL_Architecture.md)** - Modular GraphQL implementation overview
- **[Structure Overview](STRUCTURE_OVERVIEW.md)** - Complete project structure and organization
- **[Quick Reference](QUICK_REFERENCE.md)** - Fast API reference and common operations

### 🚗 Feature Documentation
- **[Vehicle Management](VEHICLE_MANAGEMENT.md)** - Complete vehicle management system documentation
- **[OAuth Setup](OAUTH_SETUP.md)** - OAuth/SSO configuration guide
- **[OAuth Examples](OAUTH_EXAMPLES.md)** - OAuth implementation examples
- **[OAuth Summary](OAUTH_SUMMARY.md)** - OAuth integration summary

### 🚀 Development & Deployment
- **[Docker README](DOCKER_README.md)** - Docker containerization guide
- **[Gradual Implementation Guide](GRADUAL_IMPLEMENTATION_GUIDE.md)** - Step-by-step implementation guide
- **[Tests README](README_TESTS.md)** - Testing documentation and examples

## 🎯 Quick Start

### For Developers
1. Start with [Structure Overview](STRUCTURE_OVERVIEW.md) to understand the project
2. Read [GraphQL Architecture](GraphQL_Architecture.md) for API design
3. Use [Quick Reference](QUICK_REFERENCE.md) for daily development
4. Check [Vehicle Management](VEHICLE_MANAGEMENT.md) for the latest feature

### For DevOps
1. Review [Docker README](DOCKER_README.md) for containerization
2. Follow [Gradual Implementation Guide](GRADUAL_IMPLEMENTATION_GUIDE.md) for deployment

### For Authentication Setup
1. Read [OAuth Summary](OAUTH_SUMMARY.md) for overview
2. Follow [OAuth Setup](OAUTH_SETUP.md) for configuration
3. Use [OAuth Examples](OAUTH_EXAMPLES.md) for implementation

## 🔧 API Features

### Core Features
- **User Management** - Registration, authentication, profile management
- **Vehicle Management** - Vehicle registration, ownership, legal compliance
- **Trip Management** - Trip creation, vehicle assignment, legal compliance
- **Booking System** - Trip reservations, passenger management
- **Rating System** - User and trip ratings

### Authentication
- **JWT Authentication** - Secure token-based authentication
- **OAuth/SSO Support** - Google, Facebook, GitHub integration
- **Multi-provider Support** - Local and external authentication

### Legal Compliance
- **Vehicle Compliance** - Legal acknowledgment for vehicle registration
- **Trip Compliance** - Legal acknowledgment for trip creation
- **Ownership Validation** - Strict ownership and access control

## 📊 Database Schema

### Core Entities
- **Users** - User accounts and profiles
- **Vehicles** - User-owned vehicles with legal compliance
- **Trips** - Carpooling trips with vehicle assignment
- **Bookings** - Trip reservations by passengers
- **Ratings** - User and trip ratings

### Key Relationships
- Users own multiple Vehicles
- Trips require a Vehicle assignment
- Bookings link Users to Trips
- Ratings connect Users and Trips

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose

### Quick Setup
```bash
# Clone repository
git clone <repository-url>
cd viaggiamo/backend

# Start services
docker compose up -d

# Run migrations
uv run alembic upgrade head

# Start development server
uv run fastapi dev app/main.py
```

### GraphQL Playground
Access the GraphQL playground at: http://localhost:8000/graphql

## 📝 Contributing

### Adding New Features
1. Create feature documentation in this directory
2. Update relevant architecture documents
3. Add examples to Quick Reference
4. Update this README index

### Documentation Standards
- Use clear, descriptive titles
- Include code examples
- Provide both GraphQL and REST examples where applicable
- Keep examples up-to-date with current API

## 🔗 External Links

- **Main README** - [../README.md](../README.md)
- **API Documentation** - http://localhost:8000/docs
- **GraphQL Playground** - http://localhost:8000/graphql
- **Health Check** - http://localhost:8000/health

## 📞 Support

For questions about the documentation or API:
1. Check the relevant feature documentation
2. Review the Quick Reference for common operations
3. Consult the GraphQL Architecture for design questions
4. Check the main README for setup issues

---

**Last Updated**: January 2024
**Version**: 1.0.0
**API Version**: GraphQL v1
