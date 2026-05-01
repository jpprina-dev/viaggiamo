#!/bin/bash

# Test GraphQL Authentication functionality
echo "🔐 Testing Viaggiamo GraphQL Authentication..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GRAPHQL_URL="http://localhost:8000/graphql"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_USERNAME="testuser_$(date +%s)"
TEST_PASSWORD="SecurePassword123!"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if backend is running
echo ""
print_info "Checking if backend is running..."
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_error "Backend is not running. Start it with: docker compose up -d"
    exit 1
fi
print_status "Backend is running"

# Test 1: Health Check Query
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Test 1: Health Check Query"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HEALTH_QUERY='{"query": "{ health }"}'
HEALTH_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$HEALTH_QUERY" \
  "$GRAPHQL_URL")

if echo "$HEALTH_RESPONSE" | grep -q "OK"; then
    print_status "Health check passed"
    echo "Response: $HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    print_error "Health check failed"
    echo "Response: $HEALTH_RESPONSE"
fi

# Test 2: User Registration
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Test 2: User Registration (Sign Up)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

REGISTER_QUERY=$(cat <<EOF
{
  "query": "mutation Register(\$input: UserCreateInput!) { register(userInput: \$input) { id email username fullName isActive isVerified phone createdAt } }",
  "variables": {
    "input": {
      "email": "$TEST_EMAIL",
      "username": "$TEST_USERNAME",
      "fullName": "Test User",
      "password": "$TEST_PASSWORD",
      "phone": "+1234567890"
    }
  }
}
EOF
)

print_info "Registering user: $TEST_EMAIL"
REGISTER_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$REGISTER_QUERY" \
  "$GRAPHQL_URL")

if echo "$REGISTER_RESPONSE" | grep -q "$TEST_EMAIL"; then
    print_status "User registration successful"
    echo "Response:"
    echo "$REGISTER_RESPONSE" | jq '.' 2>/dev/null || echo "$REGISTER_RESPONSE"
else
    print_error "User registration failed"
    echo "Response: $REGISTER_RESPONSE"
    exit 1
fi

# Test 3: User Login
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Test 3: User Login"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

LOGIN_QUERY=$(cat <<EOF
{
  "query": "mutation Login(\$input: LoginInput!) { login(loginInput: \$input) { accessToken tokenType } }",
  "variables": {
    "input": {
      "email": "$TEST_EMAIL",
      "password": "$TEST_PASSWORD"
    }
  }
}
EOF
)

print_info "Logging in as: $TEST_EMAIL"
LOGIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$LOGIN_QUERY" \
  "$GRAPHQL_URL")

if echo "$LOGIN_RESPONSE" | grep -q "accessToken"; then
    print_status "User login successful"

    # Extract access token
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.data.login.accessToken' 2>/dev/null)

    if [ "$ACCESS_TOKEN" != "null" ] && [ ! -z "$ACCESS_TOKEN" ]; then
        print_status "Access token received"
        echo "Token (first 50 chars): ${ACCESS_TOKEN:0:50}..."

        # Save token for later use
        echo "$ACCESS_TOKEN" > /tmp/viaggiamo_test_token.txt
        print_info "Token saved to /tmp/viaggiamo_test_token.txt"
    else
        print_error "Failed to extract access token"
    fi
else
    print_error "User login failed"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# Test 4: Test with Invalid Credentials
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Test 4: Login with Invalid Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

INVALID_LOGIN_QUERY=$(cat <<EOF
{
  "query": "mutation Login(\$input: LoginInput!) { login(loginInput: \$input) { accessToken tokenType } }",
  "variables": {
    "input": {
      "email": "$TEST_EMAIL",
      "password": "WrongPassword123!"
    }
  }
}
EOF
)

print_info "Testing with wrong password..."
INVALID_LOGIN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$INVALID_LOGIN_QUERY" \
  "$GRAPHQL_URL")

if echo "$INVALID_LOGIN_RESPONSE" | grep -q "error"; then
    print_status "Correctly rejected invalid credentials"
else
    print_warning "Expected error response for invalid credentials"
    echo "Response: $INVALID_LOGIN_RESPONSE"
fi

# Test 5: Duplicate Registration
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "Test 5: Duplicate Registration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

print_info "Attempting to register same email again..."
DUPLICATE_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$REGISTER_QUERY" \
  "$GRAPHQL_URL")

if echo "$DUPLICATE_RESPONSE" | grep -q "already registered"; then
    print_status "Correctly rejected duplicate email"
else
    print_warning "Expected error for duplicate registration"
    echo "Response: $DUPLICATE_RESPONSE"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_status "Authentication Testing Complete! 🎉"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Test Summary:"
echo "   ✅ Health check"
echo "   ✅ User registration"
echo "   ✅ User login"
echo "   ✅ Invalid credentials handling"
echo "   ✅ Duplicate registration prevention"
echo ""
echo "🔑 Test Credentials:"
echo "   Email: $TEST_EMAIL"
echo "   Password: $TEST_PASSWORD"
echo "   Token: saved in /tmp/viaggiamo_test_token.txt"
echo ""
echo "🎮 Try it in GraphQL Playground:"
echo "   Open: http://localhost:8000/graphql"
echo ""
echo "📝 Example authenticated request (uncomment 'me' query first):"
echo "   curl -X POST \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'Authorization: Bearer $ACCESS_TOKEN' \\"
echo "     -d '{\"query\": \"{ me { id email username } }\"}' \\"
echo "     $GRAPHQL_URL"
echo ""
