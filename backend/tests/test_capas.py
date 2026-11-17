"""Pruebas estructurales de capas (RF-8)."""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "app"
PROHIBIDO = re.compile(r"fastapi|HTTPException|status_code")


def test_servicios_sin_fastapi():
    archivos = list((RAIZ / "servicios").glob("*.py"))
    assert archivos, "el paquete servicios/ debe existir"
    for archivo in archivos:
        texto = archivo.read_text(encoding="utf-8")
        assert not PROHIBIDO.search(texto), f"{archivo.name} usa FastAPI/HTTP"


def test_routers_sin_reglas():
    patron = re.compile(r"Rol\.|Estado\.|Counter|VLineaTiempo|_filtrar|HTTPException")
    for archivo in (RAIZ / "routers").glob("*.py"):
        texto = archivo.read_text(encoding="utf-8")
        assert not patron.search(texto), f"{archivo.name} contiene reglas de negocio"


def test_listar_casos_servicio_filtra_por_rol(tmp_path):
    from datetime import date

    from sqlalchemy.orm import sessionmaker

    from backend.app import esquemas, servicios
    from backend.db import (
        Dependencia,
        Estado,
        Prioridad,
        Rol,
        Usuario,
        crear_engine,
        inicializar_base,
    )

    engine = crear_engine(f"sqlite:///{(tmp_path / 'capas.db').as_posix()}")
    inicializar_base(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as s:
        sol1, sol2, tec1, tec2, coord = (
            Usuario(nombre=n, correo=f"{n}@t.co", password_hash="x", rol=r)
            for n, r in [
                ("sol1", Rol.SOLICITANTE),
                ("sol2", Rol.SOLICITANTE),
                ("tec1", Rol.TECNICO),
                ("tec2", Rol.TECNICO),
                ("coord", Rol.COORDINADOR),
            ]
        )
        dep = Dependencia(nombre="Biblioteca")
        s.add_all([sol1, sol2, tec1, tec2, coord, dep])
        s.commit()

        def nuevo(solicitante):
            return servicios.registrar_caso(
                s,
                solicitante,
                esquemas.CasoNuevo(
                    placa_equipo="P-1",
                    nombre_usuario="Ana",
                    telefono="3001234567",
                    fecha=date.today(),
                    descripcion="Descripción suficientemente larga",
                    dependencia_id=dep.id,
                ),
            )

        c1, c2 = nuevo(sol1), nuevo(sol2)
        servicios.evaluar(s, c1, coord, Prioridad.ALTA)
        servicios.asignar_tecnico(s, c1, coord, tec1.id)
        s.commit()

        ids = lambda u, **kw: {c.id for c in servicios.listar_casos(s, u, **kw)}  # noqa: E731
        assert ids(sol1) == {c1.id}
        assert ids(sol2) == {c2.id}
        assert ids(tec1) == {c1.id}
        assert ids(tec2) == set()
        assert ids(coord) == {c1.id, c2.id}
        assert ids(coord, estado=Estado.ASIGNADO) == {c1.id}
    engine.dispose()
