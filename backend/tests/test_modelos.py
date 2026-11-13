"""Verifica que los modelos ORM coinciden con schema.sql y que el flujo básico
funciona de punta a punta sobre una base temporal.

Ejecución (desde la carpeta backend):
    python -m tests.test_modelos          # sin dependencias extra
    python -m pytest tests                # si pytest está instalado
"""

import sqlite3
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from db import (
    Asignacion,
    Base,
    Caso,
    Dependencia,
    Estado,
    HistorialEstado,
    Intervencion,
    Prioridad,
    Rol,
    Usuario,
    VCasoDetalle,
    VLineaTiempo,
    crear_engine,
    inicializar_base,
)


def _motor_temporal():
    carpeta = Path(tempfile.mkdtemp(prefix="mesa_ti_"))
    ruta = carpeta / "prueba.db"
    engine = crear_engine(f"sqlite:///{ruta.as_posix()}")
    assert inicializar_base(engine) is True
    return engine, ruta


def test_inicializar_base_es_idempotente():
    engine, _ = _motor_temporal()
    assert inicializar_base(engine) is False


def test_modelos_coinciden_con_el_esquema():
    """Columnas, nulabilidad, claves primarias y foráneas de cada modelo frente
    al esquema real creado por schema.sql."""
    engine, ruta = _motor_temporal()
    bd = sqlite3.connect(ruta)
    for tabla in Base.metadata.sorted_tables:
        real = {
            f[1]: {"notnull": bool(f[3]), "pk": bool(f[5])}
            for f in bd.execute(f"PRAGMA table_info({tabla.name})")
        }
        assert real, f"{tabla.name} no existe en la base"
        assert set(tabla.columns.keys()) == set(real), (
            f"{tabla.name}: columnas distintas. "
            f"Modelo={sorted(tabla.columns.keys())} Base={sorted(real)}"
        )
        if tabla.info.get("is_view"):
            continue
        for col in tabla.columns:
            assert col.primary_key == real[col.name]["pk"], f"{tabla.name}.{col.name}: clave primaria"
            if not col.primary_key:
                assert (not col.nullable) == real[col.name]["notnull"], f"{tabla.name}.{col.name}: nulabilidad"
        fks_real = {(f[3], f[2], f[4]) for f in bd.execute(f"PRAGMA foreign_key_list({tabla.name})")}
        fks_modelo = {
            (fk.parent.name, fk.column.table.name, fk.column.name)
            for fk in tabla.foreign_keys
        }
        assert fks_modelo == fks_real, f"{tabla.name}: claves foráneas distintas"
    bd.close()


def test_claves_foraneas_activas_en_cada_conexion():
    engine, _ = _motor_temporal()
    with engine.connect() as con:
        assert con.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1


def test_flujo_completo_con_el_orm():
    engine, _ = _motor_temporal()
    with Session(engine) as s:
        ana = Usuario(nombre="Ana", correo="ana@x.co", password_hash="h", rol=Rol.SOLICITANTE)
        tomas = Usuario(nombre="Tomás", correo="tomas@x.co", password_hash="h", rol=Rol.TECNICO)
        tania = Usuario(nombre="Tania", correo="tania@x.co", password_hash="h", rol=Rol.TECNICO)
        carla = Usuario(nombre="Carla", correo="carla@x.co", password_hash="h", rol=Rol.COORDINADOR)
        dep = Dependencia(nombre="Secretaría académica")
        s.add_all([ana, tomas, tania, carla, dep])
        s.commit()

        # Los valores por defecto de la base llegan al objeto
        assert ana.activo is True and ana.creado_en.tzinfo is not None

        caso = Caso(
            placa_equipo="ABC-123", nombre_usuario="Ana Pérez", telefono="3001234567",
            fecha=date(2026, 11, 15), descripcion="El computador no enciende desde la mañana",
            dependencia=dep, solicitante=ana,
        )
        s.add(caso)
        s.flush()
        s.add(HistorialEstado(caso_id=caso.id, estado_anterior=None,
                              estado_nuevo=Estado.REGISTRADO, autor_id=ana.id))
        s.commit()
        assert caso.estado is Estado.REGISTRADO and caso.prioridad is None
        assert caso.asignacion_activa is None

        # Evaluación, asignación e inicio de atención (la lógica real irá en el backend)
        caso.prioridad, caso.estado = Prioridad.CRITICA, Estado.EN_EVALUACION
        s.add(HistorialEstado(caso_id=caso.id, estado_anterior=Estado.REGISTRADO,
                              estado_nuevo=Estado.EN_EVALUACION, autor_id=carla.id))
        s.add(Asignacion(caso_id=caso.id, tecnico_id=tomas.id, asignado_por=carla.id))
        caso.estado = Estado.ASIGNADO
        s.commit()
        s.refresh(caso)
        assert caso.asignacion_activa.tecnico.nombre == "Tomás"
        assert caso.prioridad is Prioridad.CRITICA

        caso.estado = Estado.EN_ATENCION
        s.add(Intervencion(caso_id=caso.id, tecnico_id=tomas.id,
                           descripcion="Revisé la fuente de poder", duracion_min=30))
        s.commit()

        # Reasignación: se retira la asignación activa y se crea otra
        caso.asignacion_activa.retirado_en = datetime.now(timezone.utc)
        s.add(Asignacion(caso_id=caso.id, tecnico_id=tania.id, asignado_por=carla.id))
        s.commit()
        s.refresh(caso)
        assert caso.asignacion_activa.tecnico.nombre == "Tania"
        assert len(caso.asignaciones) == 2

        # Vistas
        detalle = s.get(VCasoDetalle, caso.id)
        assert detalle.tecnico == "Tania" and detalle.dependencia == "Secretaría académica"
        assert detalle.estado is Estado.EN_ATENCION and detalle.fecha == date(2026, 11, 15)
        linea = s.scalars(
            select(VLineaTiempo).where(VLineaTiempo.caso_id == caso.id)
            .order_by(VLineaTiempo.momento, VLineaTiempo.orden, VLineaTiempo.ref_id)
        ).all()
        tipos = [e.tipo for e in linea]
        assert "reasignacion" in tipos and "intervencion" in tipos and "cambio_estado" in tipos

        # Resolver y cerrar
        caso.estado, caso.solucion = Estado.RESUELTO, "Fuente reemplazada"
        caso.resuelto_en = datetime.now(timezone.utc)
        s.commit()
        caso.estado, caso.cerrado_en = Estado.CERRADO, datetime.now(timezone.utc)
        s.commit()
        assert caso.cerrado_en.tzinfo is not None


def _debe_fallar(sesion: Session, accion):
    try:
        accion()
        sesion.commit()
    except DBAPIError:
        sesion.rollback()
        return
    raise AssertionError("la base debía rechazar la operación")


def test_protecciones_de_la_base_a_traves_del_orm():
    engine, _ = _motor_temporal()
    with Session(engine) as s:
        ana = Usuario(nombre="Ana", correo="ana@x.co", password_hash="h", rol=Rol.SOLICITANTE)
        tomas = Usuario(nombre="Tomás", correo="tomas@x.co", password_hash="h", rol=Rol.TECNICO)
        tania = Usuario(nombre="Tania", correo="tania@x.co", password_hash="h", rol=Rol.TECNICO)
        carla = Usuario(nombre="Carla", correo="carla@x.co", password_hash="h", rol=Rol.COORDINADOR)
        dep = Dependencia(nombre="Rectoría")
        s.add_all([ana, tomas, tania, carla, dep])
        s.commit()

        def nuevo_caso(**cambios):
            datos = dict(placa_equipo="A-1", nombre_usuario="Ana", telefono="300",
                         fecha=date(2026, 11, 15), descripcion="x" * 20,
                         dependencia_id=dep.id, solicitante_id=ana.id)
            datos.update(cambios)
            return Caso(**datos)

        _debe_fallar(s, lambda: s.add(nuevo_caso(descripcion="corta")))
        _debe_fallar(s, lambda: s.add(nuevo_caso(dependencia_id=999)))

        caso = nuevo_caso()
        s.add(caso)
        s.commit()
        caso.prioridad, caso.estado = Prioridad.ALTA, Estado.EN_EVALUACION
        s.add(Asignacion(caso_id=caso.id, tecnico_id=tomas.id, asignado_por=carla.id))
        s.commit()

        # Un solo responsable activo por caso
        _debe_fallar(s, lambda: s.add(
            Asignacion(caso_id=caso.id, tecnico_id=tania.id, asignado_por=carla.id)))

        caso.estado = Estado.ASIGNADO
        s.commit()
        s.add(Intervencion(caso_id=caso.id, tecnico_id=tomas.id, descripcion="x", duracion_min=5))
        s.commit()

        # Intervenciones: sin edición ni borrado
        interv = s.scalars(select(Intervencion)).first()
        _debe_fallar(s, lambda: setattr(interv, "descripcion", "otra"))
        _debe_fallar(s, lambda: s.delete(interv))

        # Estado y datos coherentes: no se resuelve sin solución
        _debe_fallar(s, lambda: setattr(caso, "estado", Estado.RESUELTO))

        caso.estado = Estado.EN_ATENCION
        s.commit()
        caso.estado, caso.solucion = Estado.RESUELTO, "ok"
        caso.resuelto_en = datetime.now(timezone.utc)
        s.commit()
        caso.estado, caso.cerrado_en = Estado.CERRADO, datetime.now(timezone.utc)
        s.commit()

        # Caso cerrado: inmutable y sin borrado
        _debe_fallar(s, lambda: setattr(caso, "prioridad", Prioridad.BAJA))
        _debe_fallar(s, lambda: s.delete(caso))


def _ejecutar_todo() -> int:
    pruebas = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    fallidas = 0
    for nombre, prueba in pruebas:
        try:
            prueba()
            print("OK   ", nombre)
        except Exception as e:  # noqa: BLE001
            fallidas += 1
            print("FALLA", nombre, "->", repr(e))
    print(f"\nResultado: {len(pruebas) - fallidas} correctas, {fallidas} fallidas")
    return 1 if fallidas else 0


if __name__ == "__main__":
    sys.exit(_ejecutar_todo())
