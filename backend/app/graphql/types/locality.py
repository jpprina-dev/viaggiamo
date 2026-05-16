"""Tipos Strawberry para el catálogo georef-ar."""

from __future__ import annotations

import strawberry


@strawberry.type
class LocalitySuggestion:
    id: str
    name: str
    province: str
    department: str
    display_name: str


def build_locality_suggestion(loc: object) -> LocalitySuggestion:
    display = f"{loc.name}, {loc.department_name}, {loc.province_name}"
    return LocalitySuggestion(
        id=loc.id,
        name=loc.name,
        province=loc.province_name,
        department=loc.department_name,
        display_name=display,
    )
