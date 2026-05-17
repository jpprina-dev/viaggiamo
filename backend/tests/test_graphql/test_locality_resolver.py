"""Tests TDD para el resolver searchLocalities y modelos georef."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from strawberry.types import Info

from app.graphql.context import Context
from app.models.user import User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_info(db: AsyncMock | None = None) -> Info:
    info = MagicMock(spec=Info)
    info.context = MagicMock(spec=Context)
    info.context.db = db or AsyncMock()
    info.context.user = MagicMock(spec=User)
    return info


def _make_locality(
    id: str,
    name: str,
    province_name: str,
    department_name: str,
) -> MagicMock:
    from app.models.locality import Locality

    loc = MagicMock(spec=Locality)
    loc.id = id
    loc.name = name
    loc.province_name = province_name
    loc.department_name = department_name
    return loc


def _mock_db_result(db: AsyncMock, rows: list) -> None:
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = rows
    db.execute = AsyncMock(return_value=result_mock)


# ---------------------------------------------------------------------------
# Ciclo 1: Modelos con PK string
# ---------------------------------------------------------------------------


def test_locality_models_have_string_pk() -> None:
    from app.models.locality import Locality

    cols = {c.key: c for c in Locality.__table__.columns}
    assert cols["id"].type.python_type is str
    assert "province_id" in cols
    assert "department_id" in cols
    assert "province_name" in cols
    assert "department_name" in cols


def test_locality_model_has_lat_lng() -> None:
    from app.models.locality import Locality

    cols = {c.key: c for c in Locality.__table__.columns}
    assert "lat" in cols
    assert "lng" in cols
    assert not cols["lat"].nullable
    assert not cols["lng"].nullable


def test_province_pk_is_string() -> None:
    from app.models.locality import Province

    cols = {c.key: c for c in Province.__table__.columns}
    assert cols["id"].type.python_type is str
    assert "name" in cols


def test_department_has_province_fk() -> None:
    from app.models.locality import Department

    cols = {c.key: c for c in Department.__table__.columns}
    assert "province_id" in cols


# ---------------------------------------------------------------------------
# Ciclo 2: Query corta → lista vacía
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_localities_empty_for_one_char() -> None:
    from app.graphql.resolvers.locality import LocalityQueries

    info = _make_info()
    result = await LocalityQueries().search_localities(info, q="B")
    assert result == []
    info.context.db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_search_localities_empty_for_blank() -> None:
    from app.graphql.resolvers.locality import LocalityQueries

    info = _make_info()
    result = await LocalityQueries().search_localities(info, q="  ")
    assert result == []
    info.context.db.execute.assert_not_called()


# ---------------------------------------------------------------------------
# Ciclo 3: Devuelve resultados y respeta limit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_localities_returns_matching_result() -> None:
    from app.graphql.resolvers.locality import LocalityQueries

    db = AsyncMock()
    info = _make_info(db)
    loc = _make_locality("001", "Rosario", "Santa Fe", "Rosario")
    _mock_db_result(db, [loc])

    results = await LocalityQueries().search_localities(info, q="Rosa", limit=5)
    assert len(results) == 1
    assert results[0].name == "Rosario"
    assert results[0].province == "Santa Fe"


@pytest.mark.asyncio
async def test_search_localities_respects_limit() -> None:
    from app.graphql.resolvers.locality import LocalityQueries

    db = AsyncMock()
    info = _make_info(db)
    locs = [_make_locality(str(i), f"Ciudad {i}", "Prov", "Dep") for i in range(5)]
    _mock_db_result(db, locs)

    results = await LocalityQueries().search_localities(info, q="Ciudad", limit=5)
    assert len(results) == 5


@pytest.mark.asyncio
async def test_search_localities_by_department_name() -> None:
    """Localidades encontradas por partido/departamento aparecen en resultados."""
    from app.graphql.resolvers.locality import LocalityQueries

    db = AsyncMock()
    info = _make_info(db)
    loc = _make_locality("001", "La Emilia", "Buenos Aires", "San Nicolás")
    _mock_db_result(db, [loc])

    results = await LocalityQueries().search_localities(info, q="San Nico", limit=10)
    assert len(results) == 1
    assert results[0].department == "San Nicolás"
    assert results[0].display_name == "La Emilia, Buenos Aires"


# ---------------------------------------------------------------------------
# Ciclo 4: displayName con y sin colisión
# ---------------------------------------------------------------------------


def test_display_name_without_collision_omits_department() -> None:
    from app.graphql.types.locality import build_locality_suggestion

    loc = _make_locality("001", "Bahía Blanca", "Buenos Aires", "Bahía Blanca")
    result = build_locality_suggestion(loc)
    assert result.display_name == "Bahía Blanca, Buenos Aires"


def test_display_name_with_department_flag_includes_department() -> None:
    from app.graphql.types.locality import build_locality_suggestion

    loc = _make_locality("002", "San Martín", "Córdoba", "Gral. San Martín")
    result = build_locality_suggestion(loc, with_department=True)
    assert result.display_name == "San Martín, Gral. San Martín, Córdoba"


def test_display_name_unique_locality_shows_only_province() -> None:
    from app.graphql.types.locality import build_locality_suggestion

    loc = _make_locality("003", "Mendoza", "Mendoza", "Capital")
    result = build_locality_suggestion(loc)
    assert result.display_name == "Mendoza, Mendoza"


@pytest.mark.asyncio
async def test_display_name_shows_department_on_name_collision() -> None:
    """Dos localidades con mismo nombre y provincia reciben el departamento en displayName."""
    from app.graphql.resolvers.locality import LocalityQueries

    db = AsyncMock()
    info = _make_info(db)
    loc1 = _make_locality("001", "San Martín", "Buenos Aires", "Gral. San Martín")
    loc2 = _make_locality("002", "San Martín", "Buenos Aires", "La Matanza")
    _mock_db_result(db, [loc1, loc2])

    results = await LocalityQueries().search_localities(info, q="San Mart", limit=10)
    assert results[0].display_name == "San Martín, Gral. San Martín, Buenos Aires"
    assert results[1].display_name == "San Martín, La Matanza, Buenos Aires"


@pytest.mark.asyncio
async def test_display_name_no_department_when_no_collision() -> None:
    """Localidad sin colisión de nombre+provincia no muestra departamento."""
    from app.graphql.resolvers.locality import LocalityQueries

    db = AsyncMock()
    info = _make_info(db)
    loc = _make_locality("001", "Rosario", "Santa Fe", "Rosario")
    _mock_db_result(db, [loc])

    results = await LocalityQueries().search_localities(info, q="Rosari", limit=10)
    assert results[0].display_name == "Rosario, Santa Fe"


# ---------------------------------------------------------------------------
# Ciclo 5: Normalización de acentos en el query
# ---------------------------------------------------------------------------


def test_strip_accents_removes_diacritics() -> None:
    from app.graphql.resolvers.locality import _strip_accents

    assert _strip_accents("córdo") == "cordo"
    assert _strip_accents("Córdoba") == "Cordoba"
    assert _strip_accents("bahía") == "bahia"
    assert _strip_accents("Martín") == "Martin"
    assert _strip_accents("sin acentos") == "sin acentos"


# ---------------------------------------------------------------------------
# Ciclo 6: Schema expone searchLocalities
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Ciclo 7: Script de importación idempotente
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_import_provinces_idempotent(tmp_path: Path) -> None:
    from unittest.mock import AsyncMock

    from scripts.import_georef import import_provinces

    csv_file = tmp_path / "provincias.csv"
    csv_file.write_text(
        '"provincia_id","provincia_nombre","lat","lon"\n'
        '"06","Buenos Aires",-34.6,-58.4\n'
        '"14","Córdoba",-31.4,-64.1\n',
        encoding="utf-8",
    )
    db = AsyncMock()
    await import_provinces(db, csv_file)
    first_call_count = db.execute.call_count
    await import_provinces(db, csv_file)
    assert db.execute.call_count == first_call_count * 2  # mismo número de inserts


@pytest.mark.asyncio
async def test_import_localities_idempotent(tmp_path: Path) -> None:
    from unittest.mock import AsyncMock

    from scripts.import_georef import import_localities

    csv_file = tmp_path / "localidades.csv"
    csv_file.write_text(
        '"localidad_id","localidad_nombre","localidad_centroide_lat","localidad_centroide_lon",'
        '"provincia_id","provincia_nombre","departamento_id","departamento_nombre",'
        '"municipio_id","municipio_nombre","localidad_censal_id","localidad_censal_nombre","localidad_categoria"\n'
        '"0600700010000","Mar del Plata",-38.0,-57.5,"06","Buenos Aires","06070","General Pueyrredón",'
        '"","","","",""\n',
        encoding="utf-8",
    )
    db = AsyncMock()
    await import_localities(db, csv_file)
    first_call_count = db.execute.call_count
    await import_localities(db, csv_file)
    assert db.execute.call_count == first_call_count * 2


# ---------------------------------------------------------------------------
# Ciclo 5: Schema expone searchLocalities
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_schema_exposes_search_localities() -> None:
    from app.graphql.schema import schema

    result = await schema.execute('{ __type(name: "Query") { fields { name } } }')
    assert result.errors is None
    names = [f["name"] for f in result.data["__type"]["fields"]]
    assert "searchLocalities" in names
