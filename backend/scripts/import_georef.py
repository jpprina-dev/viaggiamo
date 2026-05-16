"""Importa el catálogo georef-ar desde CSVs a la base de datos.

Uso:
    cd backend && uv run python scripts/import_georef.py

Idempotente: usa ON CONFLICT DO NOTHING, se puede ejecutar múltiples veces.
CSVs fuente: backend/data/georef/ (descargados de apis.datos.gob.ar/georef).
"""

import asyncio
import csv
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

GEOREF_DIR = Path(__file__).parent.parent / "data" / "georef"


async def import_provinces(db: AsyncSession, csv_path: Path) -> int:
    count = 0
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await db.execute(
                text(
                    "INSERT INTO provinces (id, name) VALUES (:id, :name) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": row["provincia_id"], "name": row["provincia_nombre"]},
            )
            count += 1
    await db.commit()
    return count


async def import_departments(db: AsyncSession, csv_path: Path) -> int:
    count = 0
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await db.execute(
                text(
                    "INSERT INTO departments (id, name, province_id) "
                    "VALUES (:id, :name, :province_id) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": row["departamento_id"],
                    "name": row["departamento_nombre"],
                    "province_id": row["provincia_id"],
                },
            )
            count += 1
    await db.commit()
    return count


async def import_localities(db: AsyncSession, csv_path: Path) -> int:
    count = 0
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["localidad_categoria"] == "Entidad":
                continue
            await db.execute(
                text(
                    "INSERT INTO localities "
                    "(id, name, province_id, department_id, province_name, department_name) "
                    "VALUES (:id, :name, :province_id, :department_id, :province_name, :department_name) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {
                    "id": row["localidad_id"],
                    "name": row["localidad_nombre"],
                    "province_id": row["provincia_id"],
                    "department_id": row["departamento_id"],
                    "province_name": row["provincia_nombre"],
                    "department_name": row["departamento_nombre"],
                },
            )
            count += 1
    await db.commit()
    return count


async def main() -> None:
    import os

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        from app.core.config import settings

        database_url = settings.DATABASE_URL

    engine = create_async_engine(database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        print("Importando provincias...")
        n = await import_provinces(db, GEOREF_DIR / "provincias.csv")
        print(f"  {n} filas procesadas")

        print("Importando departamentos...")
        n = await import_departments(db, GEOREF_DIR / "departamentos.csv")
        print(f"  {n} filas procesadas")

        print("Importando localidades...")
        n = await import_localities(db, GEOREF_DIR / "localidades.csv")
        print(f"  {n} filas procesadas")

    await engine.dispose()
    print("Importación completa.")


if __name__ == "__main__":
    asyncio.run(main())
