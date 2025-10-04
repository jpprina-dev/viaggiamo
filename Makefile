# Viaggiamo MVP - Makefile
# Comandos útiles para desarrollo

.PHONY: help install dev build start stop clean logs test lint format

# Variables
DOCKER_COMPOSE = docker-compose
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help: ## Mostrar esta ayuda
	@echo "$(GREEN)Viaggiamo MVP - Comandos disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Instalar dependencias
	@echo "$(GREEN)Instalando dependencias...$(NC)"
	@cd $(BACKEND_DIR) && uv sync
	@cd $(FRONTEND_DIR) && npm install

dev: ## Levantar entorno de desarrollo
	@echo "$(GREEN)Levantando entorno de desarrollo...$(NC)"
	$(DOCKER_COMPOSE) up -d postgres redis
	@echo "$(GREEN)Esperando que los servicios estén listos...$(NC)"
	@sleep 10
	@echo "$(GREEN)Ejecutando migraciones...$(NC)"
	@cd $(BACKEND_DIR) && uv run alembic upgrade head
	@echo "$(GREEN)Backend: http://localhost:8000$(NC)"
	@echo "$(GREEN)Frontend: http://localhost:3000$(NC)"
	@echo "$(GREEN)API Docs: http://localhost:8000/docs$(NC)"

build: ## Construir imágenes Docker
	@echo "$(GREEN)Construyendo imágenes Docker...$(NC)"
	$(DOCKER_COMPOSE) build

start: ## Iniciar todos los servicios
	@echo "$(GREEN)Iniciando servicios...$(NC)"
	$(DOCKER_COMPOSE) up -d

stop: ## Detener todos los servicios
	@echo "$(GREEN)Deteniendo servicios...$(NC)"
	$(DOCKER_COMPOSE) down

restart: ## Reiniciar todos los servicios
	@echo "$(GREEN)Reiniciando servicios...$(NC)"
	$(DOCKER_COMPOSE) restart

clean: ## Limpiar contenedores, volúmenes e imágenes
	@echo "$(GREEN)Limpieza completa...$(NC)"
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans
	docker system prune -f

logs: ## Ver logs de todos los servicios
	$(DOCKER_COMPOSE) logs -f

logs-backend: ## Ver logs del backend
	$(DOCKER_COMPOSE) logs -f backend

logs-frontend: ## Ver logs del frontend
	$(DOCKER_COMPOSE) logs -f frontend

logs-db: ## Ver logs de la base de datos
	$(DOCKER_COMPOSE) logs -f postgres

logs-redis: ## Ver logs de Redis
	$(DOCKER_COMPOSE) logs -f redis

shell-backend: ## Acceder al shell del backend
	$(DOCKER_COMPOSE) exec backend /bin/bash

shell-db: ## Acceder a PostgreSQL
	$(DOCKER_COMPOSE) exec postgres psql -U viaggiamo -d viaggiamo_db

shell-redis: ## Acceder a Redis CLI
	$(DOCKER_COMPOSE) exec redis redis-cli

migrate: ## Ejecutar migraciones de base de datos
	@echo "$(GREEN)Ejecutando migraciones...$(NC)"
	@cd $(BACKEND_DIR) && uv run alembic upgrade head

migrate-create: ## Crear nueva migración (uso: make migrate-create MESSAGE="descripción")
	@echo "$(GREEN)Creando migración: $(MESSAGE)$(NC)"
	@cd $(BACKEND_DIR) && uv run alembic revision --autogenerate -m "$(MESSAGE)"

test: ## Ejecutar tests
	@echo "$(GREEN)Ejecutando tests del backend...$(NC)"
	@cd $(BACKEND_DIR) && uv run pytest
	@echo "$(GREEN)Ejecutando tests del frontend...$(NC)"
	@cd $(FRONTEND_DIR) && npm test

lint: ## Ejecutar linters
	@echo "$(GREEN)Linting backend...$(NC)"
	@cd $(BACKEND_DIR) && uv run black . && uv run isort . && uv run flake8 .
	@echo "$(GREEN)Linting frontend...$(NC)"
	@cd $(FRONTEND_DIR) && npm run lint

format: ## Formatear código
	@echo "$(GREEN)Formateando backend...$(NC)"
	@cd $(BACKEND_DIR) && uv run black . && uv run isort .
	@echo "$(GREEN)Formateando frontend...$(NC)"
	@cd $(FRONTEND_DIR) && npm run format

health: ## Verificar estado de los servicios
	@echo "$(GREEN)Verificando estado de los servicios...$(NC)"
	@echo "Backend: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health || echo 'No disponible')"
	@echo "Frontend: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 || echo 'No disponible')"
	@echo "PostgreSQL: $$(docker-compose exec -T postgres pg_isready -U viaggiamo || echo 'No disponible')"
	@echo "Redis: $$(docker-compose exec -T redis redis-cli ping || echo 'No disponible')"

backup-db: ## Crear backup de la base de datos
	@echo "$(GREEN)Creando backup de la base de datos...$(NC)"
	@mkdir -p backups
	@docker-compose exec -T postgres pg_dump -U viaggiamo viaggiamo_db > backups/viaggiamo_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup creado en backups/$(NC)"

restore-db: ## Restaurar backup de la base de datos (uso: make restore-db FILE=backup.sql)
	@echo "$(GREEN)Restaurando backup: $(FILE)$(NC)"
	@docker-compose exec -T postgres psql -U viaggiamo -d viaggiamo_db < $(FILE)

status: ## Mostrar estado de los servicios
	@echo "$(GREEN)Estado de los servicios:$(NC)"
	$(DOCKER_COMPOSE) ps

# Comandos de desarrollo local (sin Docker)
dev-local-backend: ## Ejecutar backend localmente
	@echo "$(GREEN)Ejecutando backend localmente...$(NC)"
	@cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-local-frontend: ## Ejecutar frontend localmente
	@echo "$(GREEN)Ejecutando frontend localmente...$(NC)"
	@cd $(FRONTEND_DIR) && npm run dev

# Comandos de producción
prod-build: ## Construir para producción
	@echo "$(GREEN)Construyendo para producción...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml build

prod-start: ## Iniciar en producción
	@echo "$(GREEN)Iniciando en producción...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-stop: ## Detener producción
	@echo "$(GREEN)Deteniendo producción...$(NC)"
	$(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.prod.yml down
