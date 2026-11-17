"""Conexión a SQLite, sesiones y creación de la base desde schema.sql.

La base se crea con `schema.sql` (tablas, índices, triggers y vistas). Los modelos
de `models.py` solo la describen para consultarla; nunca se usa `create_all()`,
porque no crearía los triggers ni las vistas.
"""

import os
from collections.abc import Iterator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, event, inspect
from sqlalchemy.orm import Session, sessionmaker

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
BACKEND_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BACKEND_DIR.parent / ".env")


def url_por_defecto() -> str:
    """URL de la base: variable DATABASE_URL o el archivo backend/mesa_ti.db."""
    return os.getenv("DATABASE_URL") or f"sqlite:///{(BACKEND_DIR / 'mesa_ti.db').as_posix()}"


def crear_engine(url: str | None = None) -> Engine:
    """Crea el engine y activa las claves foráneas en cada conexión (SQLite las
    trae desactivadas por defecto)."""
    engine = create_engine(url or url_por_defecto())

    @event.listens_for(engine, "connect")
    def _activar_claves_foraneas(dbapi_connection, _registro):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    return engine


def inicializar_base(engine: Engine) -> bool:
    """Crea la base ejecutando schema.sql si aún no existe la tabla `caso`.

    Devuelve True si la creó y False si ya existía (no toca datos existentes).
    """
    if inspect(engine).has_table("caso"):
        return False
    script = SCHEMA_PATH.read_text(encoding="utf-8")
    conexion = engine.raw_connection()
    try:
        conexion.driver_connection.executescript(script)
        conexion.commit()
    finally:
        conexion.close()
    return True


engine = crear_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    """Dependencia de FastAPI: una sesión por solicitud."""
    with SessionLocal() as sesion:
        yield sesion
