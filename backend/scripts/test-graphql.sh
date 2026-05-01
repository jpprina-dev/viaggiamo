#!/bin/bash

# Test GraphQL API functionality
echo "🚀 Testing Viaggiamo GraphQL API..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Check if environment file exists
if [ ! -f "docker.env" ]; then
    print_warning "docker.env file not found. Using default environment variables."
else
    print_status "Using docker.env for environment configuration"
fi

# Start services
echo "📦 Starting backend services..."
docker compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if ! docker compose ps | grep -q "Up"; then
    print_error "Services failed to start. Check logs with: docker compose logs"
    exit 1
fi

print_status "Services are running"

# Test GraphQL endpoint
echo "🔍 Testing GraphQL endpoint..."

# Wait a bit more for the backend to fully start
sleep 5

# Test health endpoint first
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Health endpoint is responding"
else
    print_warning "Health endpoint not responding, but continuing with GraphQL test"
fi

# Test GraphQL endpoint
GRAPHQL_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}' \
  http://localhost:8000/graphql 2>/dev/null)

if echo "$GRAPHQL_RESPONSE" | grep -q "__schema"; then
    print_status "GraphQL endpoint is responding correctly"
    echo "📊 GraphQL Schema Response:"
    echo "$GRAPHQL_RESPONSE" | jq '.' 2>/dev/null || echo "$GRAPHQL_RESPONSE"
else
    print_error "GraphQL endpoint is not responding correctly"
    echo "Response: $GRAPHQL_RESPONSE"
fi

# Test GraphQL Playground (if available)
echo "🎮 Testing GraphQL Playground..."
if curl -f http://localhost:8000/graphql > /dev/null 2>&1; then
    print_status "GraphQL Playground is accessible at http://localhost:8000/graphql"
else
    print_warning "GraphQL Playground might not be available"
fi

echo ""
echo "🎉 Testing complete!"
echo ""
echo "📋 Available endpoints:"
echo "   • GraphQL Playground: http://localhost:8000/graphql"
echo "   • Health Check: http://localhost:8000/health"
echo "   • API Docs: http://localhost:8000/docs"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs: docker compose logs -f"
echo "   • Stop services: docker compose down"
echo "   • Restart services: docker compose restart"
echo "   • View service status: docker compose ps"
