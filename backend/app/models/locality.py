"""Modelos georef-ar: provincias, departamentos, localidades."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.models.base import Base


class GeoBase(DeclarativeBase):
    # Comparte el mismo MetaData que Base → create_all del conftest crea estas tablas
    metadata = Base.metadata


class Province(GeoBase):
    __tablename__ = "provinces"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Department(GeoBase):
    __tablename__ = "departments"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    province_id: Mapped[str] = mapped_column(
        String(24), ForeignKey("provinces.id"), nullable=False
    )


class Locality(GeoBase):
    __tablename__ = "localities"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    province_id: Mapped[str] = mapped_column(
        String(24), ForeignKey("provinces.id"), nullable=False
    )
    department_id: Mapped[str] = mapped_column(
        String(24), ForeignKey("departments.id"), nullable=False
    )
    # Desnormalizados para evitar JOIN en el hot path del autocomplete
    province_name: Mapped[str] = mapped_column(String(100), nullable=False)
    department_name: Mapped[str] = mapped_column(String(100), nullable=False)
