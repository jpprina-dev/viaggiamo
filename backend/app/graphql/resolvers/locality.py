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

        name_q = func.unaccent(Locality.name).ilike(f"%{normalized}%")
        dept_q = func.unaccent(Locality.department_name).ilike(f"%{normalized}%")

        stmt = (
            select(Locality)
            .where(name_q | dept_q)
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

        return [build_locality_suggestion(row) for row in rows]
