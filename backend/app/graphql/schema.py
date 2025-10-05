"""GraphQL schema definition."""

import strawberry


@strawberry.type
class Query:
    """GraphQL Query operations."""

    @strawberry.field
    def hello(self) -> str:
        """Simple hello query for testing."""
        return "Hello, GraphQL!"


schema = strawberry.Schema(query=Query)
