# GraphQL Test Suite

This directory contains a comprehensive, modular test suite for the GraphQL API.

## 📁 Test Structure

### Core Schema Tests
- **`test_schema_base.py`** - Basic schema structure and creation tests
- **`test_schema_introspection.py`** - Schema introspection and type validation tests
- **`test_schema.py`** - Legacy tests for backward compatibility

### Feature-Specific Tests
- **`test_vehicle_resolvers.py`** - Vehicle resolver unit tests
- **`test_trip_resolvers.py`** - Trip resolver unit tests with vehicle integration
- **`test_vehicle_integration.py`** - Vehicle feature integration tests

## 🎯 Test Coverage

### Vehicle Management Feature
- ✅ Vehicle CRUD operations (Create, Read, Update, Delete)
- ✅ Vehicle ownership validation
- ✅ Legal compliance acknowledgment validation
- ✅ Vehicle-trip relationship validation
- ✅ Authentication and authorization tests
- ✅ Error handling and edge cases

### Trip Integration
- ✅ Trip creation with vehicle assignment
- ✅ Vehicle ownership validation for trips
- ✅ Legal compliance for trips
- ✅ Trip-vehicle relationship queries
- ✅ Vehicle information retrieval for trips

### Schema Validation
- ✅ GraphQL type definitions
- ✅ Input/output type consistency
- ✅ Field type validation
- ✅ Schema introspection
- ✅ SDL generation

## 🧪 Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Individual resolver function testing
- Mock-based testing for isolated components
- Business logic validation
- Error handling verification

### Integration Tests (`@pytest.mark.integration`)
- End-to-end feature testing
- Schema consistency validation
- Type relationship verification
- Cross-feature integration

## 🚀 Running Tests

### Prerequisites
```bash
# Install test dependencies
uv add pytest pytest-asyncio

# Start test database (if needed)
docker compose up -d postgres
```

### Run All GraphQL Tests
```bash
# Run all GraphQL tests
uv run python -m pytest tests/test_graphql/ -v

# Run with coverage
uv run python -m pytest tests/test_graphql/ --cov=app.graphql --cov-report=html
```

### Run Specific Test Categories
```bash
# Run only unit tests
uv run python -m pytest tests/test_graphql/ -m unit -v

# Run only integration tests
uv run python -m pytest tests/test_graphql/ -m integration -v

# Run vehicle-specific tests
uv run python -m pytest tests/test_graphql/test_vehicle* -v
```

### Run Individual Test Files
```bash
# Test vehicle resolvers
uv run python -m pytest tests/test_graphql/test_vehicle_resolvers.py -v

# Test trip resolvers
uv run python -m pytest tests/test_graphql/test_trip_resolvers.py -v

# Test schema introspection
uv run python -m pytest tests/test_graphql/test_schema_introspection.py -v
```

## 📋 Test Examples

### Vehicle Creation Test
```python
@pytest.mark.asyncio
async def test_create_vehicle_creates_vehicle_successfully(self):
    """Test that createVehicle creates a vehicle successfully."""
    # Mock user and context
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    # Test vehicle creation with legal compliance
    vehicle_input = VehicleCreateInput(
        make="Toyota",
        model="Corolla",
        year=2020,
        license_plate="ABC-123",
        seats=5,
        vehicle_legal_compliance_ack=True,
    )

    # Verify successful creation
    result = await mutations.create_vehicle(mock_info, vehicle_input)
    assert result is not None
    assert result.make == "Toyota"
```

### Trip-Vehicle Integration Test
```python
@pytest.mark.asyncio
async def test_create_trip_requires_vehicle_ownership(self):
    """Test that createTrip requires vehicle ownership."""
    # Mock user and vehicle owned by different user
    mock_user = MagicMock(spec=User)
    mock_user.id = 1

    mock_vehicle = MagicMock(spec=Vehicle)
    mock_vehicle.user_id = 2  # Different user

    # Test that unauthorized vehicle usage raises error
    with pytest.raises(ValueError, match="Not authorized to use this vehicle"):
        await mutations.create_trip(mock_info, trip_input)
```

### Schema Introspection Test
```python
def test_schema_has_vehicle_type(self):
    """Test that schema includes VehicleType."""
    query = """
    {
        __type(name: "VehicleType") {
            name
            kind
            fields {
                name
            }
        }
    }
    """

    result = schema.execute_sync(query)
    assert result.errors is None
    assert result.data["__type"]["name"] == "VehicleType"
```

## 🔧 Test Configuration

### Mock Strategy
- **Database Operations**: Mocked using `AsyncMock` and `MagicMock`
- **Authentication**: Mock user context for testing authorization
- **External Dependencies**: All external services mocked
- **Database Models**: Mock model instances with realistic data

### Test Data
- **Users**: Mock user instances with different IDs and roles
- **Vehicles**: Mock vehicle instances with various configurations
- **Trips**: Mock trip instances with vehicle associations
- **Edge Cases**: Invalid data, missing fields, unauthorized access

## 📊 Test Metrics

### Coverage Goals
- **Unit Tests**: 90%+ coverage for resolver functions
- **Integration Tests**: 100% coverage for schema types
- **Error Handling**: 100% coverage for error scenarios
- **Business Logic**: 100% coverage for validation rules

### Performance
- **Unit Tests**: < 1ms per test
- **Integration Tests**: < 10ms per test
- **Schema Tests**: < 5ms per test

## 🐛 Debugging Tests

### Common Issues
1. **Import Errors**: Ensure all modules are properly imported
2. **Mock Issues**: Verify mock setup and return values
3. **Async Issues**: Use `@pytest.mark.asyncio` for async tests
4. **Schema Issues**: Check GraphQL type definitions

### Debug Commands
```bash
# Run with detailed output
uv run python -m pytest tests/test_graphql/ -v -s

# Run single test with debugging
uv run python -m pytest tests/test_graphql/test_vehicle_resolvers.py::TestVehicleMutations::test_create_vehicle_creates_vehicle_successfully -v -s

# Run with pdb debugging
uv run python -m pytest tests/test_graphql/ --pdb
```

## 🔄 Adding New Tests

### For New Features
1. Create feature-specific test file (e.g., `test_new_feature.py`)
2. Add unit tests for individual resolvers
3. Add integration tests for schema validation
4. Update this README with new test coverage

### Test Template
```python
"""Tests for new feature."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.resolvers.new_feature import NewFeatureQueries, NewFeatureMutations


@pytest.mark.unit
class TestNewFeatureQueries:
    """Tests for NewFeatureQueries class."""

    def test_new_feature_queries_is_strawberry_type(self):
        """Test that NewFeatureQueries is a Strawberry type."""
        assert hasattr(NewFeatureQueries, "__strawberry_definition__")

    @pytest.mark.asyncio
    async def test_new_feature_query_works(self):
        """Test that new feature query works correctly."""
        # Test implementation
        pass


@pytest.mark.unit
class TestNewFeatureMutations:
    """Tests for NewFeatureMutations class."""

    def test_new_feature_mutations_is_strawberry_type(self):
        """Test that NewFeatureMutations is a Strawberry type."""
        assert hasattr(NewFeatureMutations, "__strawberry_definition__")

    @pytest.mark.asyncio
    async def test_new_feature_mutation_works(self):
        """Test that new feature mutation works correctly."""
        # Test implementation
        pass
```

## 📚 Related Documentation

- [Vehicle Management Documentation](../../docs/VEHICLE_MANAGEMENT.md)
- [GraphQL Architecture Documentation](../../docs/GraphQL_Architecture.md)
- [API Quick Reference](../../docs/QUICK_REFERENCE.md)
- [Main README](../../README.md)

---

**Last Updated**: January 2024
**Test Framework**: pytest + pytest-asyncio
**Coverage Target**: 90%+ for all GraphQL components
