"""Resolver GraphQL para el catálogo de localidades argentinas."""

from __future__ import annotations

import strawberry
from sqlalchemy import case, func, select
from strawberry.types import Info

from app.graphql.context import Context
from app.graphql.types.locality import LocalitySuggestion, build_locality_suggestion
from app.models.locality import Locality


@strawberry.type
class LocalityQueries:
    @strawberry.field
    async def search_localities(
        self,
        info: Info[Context, None],
        q: str,
        limit: int = 10,
    ) -> list[LocalitySuggestion]:
        if len(q.strip()) < 2:
            return []

        ctx = info.context
        normalized = q.strip()

        stmt = (
            select(Locality)
            .where(func.unaccent(Locality.name).ilike(f"%{normalized}%"))
            .order_by(
                case(
                    (func.unaccent(Locality.name).ilike(f"{normalized}%"), 0), else_=1
                ),
                Locality.name,
            )
            .limit(limit)
        )
        result = await ctx.db.execute(stmt)
        rows = result.scalars().all()

        name_province_counts: dict[tuple[str, str], int] = {}
        for row in rows:
            key = (row.name.lower(), row.province_name.lower())
            name_province_counts[key] = name_province_counts.get(key, 0) + 1

        return [
            build_locality_suggestion(
                row,
                has_name_collision=name_province_counts[
                    (row.name.lower(), row.province_name.lower())
                ]
                > 1,
            )
            for row in rows
        ]
