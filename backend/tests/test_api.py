"""Pruebas de integración de la API (historias US-01 a US-10).

Cada prueba usa una base SQLite temporal creada desde schema.sql.
Ejecución (desde la carpeta backend):
    python -m pytest tests -v
"""

import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.seguridad import crear_token, hash_password
from db import Dependencia, Rol, Usuario, crear_engine, get_session, inicializar_base

PASSWORD = "Clave123*"


@pytest.fixture()
def entorno():
    ruta = Path(tempfile.mkdtemp(prefix="mesa_api_")) / "prueba.db"
    engine = crear_engine(f"sqlite:///{ruta.as_posix()}")
    inicializar_base(engine)
    Sesion = sessionmaker(bind=engine, expire_on_commit=False)

    def _sesion_prueba():
        with Sesion() as s:
            yield s

    app.dependency_overrides[get_session] = _sesion_prueba

    hash_ = hash_password(PASSWORD)
    with Sesion() as s:
        datos = {
            "coord": ("Coordinador", "coord@test.co", Rol.COORDINADOR, True),
            "tec1": ("Técnico Uno", "tec1@test.co", Rol.TECNICO, True),
            "tec2": ("Técnico Dos", "tec2@test.co", Rol.TECNICO, True),
            "tec_inactivo": ("Técnico Inactivo", "tec3@test.co", Rol.TECNICO, False),
            "sol1": ("Solicitante Uno", "sol1@test.co", Rol.SOLICITANTE, True),
            "sol2": ("Solicitante Dos", "sol2@test.co", Rol.SOLICITANTE, True),
        }
        usuarios = {}
        for clave, (nombre, correo, rol, activo) in datos.items():
            usuarios[clave] = Usuario(
                nombre=nombre, correo=correo, password_hash=hash_, rol=rol, activo=activo
            )
            s.add(usuarios[clave])
        s.add(Dependencia(nombre="Biblioteca"))
        s.add(Dependencia(nombre="Cerrada", activa=False))
        s.commit()
        ids = {clave: u.id for clave, u in usuarios.items()}
        roles = {clave: u.rol.value for clave, u in usuarios.items()}

    cliente = TestClient(app)
    encabezados = {
        clave: {"Authorization": f"Bearer {crear_token(ids[clave], roles[clave])}"}
        for clave in ids
    }
    yield cliente, encabezados, ids
    app.dependency_overrides.clear()
    engine.dispose()


def _reporte(**cambios):
    datos = {
        "placa_equipo": "ABC-123",
        "nombre_usuario": "Ana Pérez",
        "telefono": "3001234567",
        "fecha": date.today().isoformat(),
        "descripcion": "El computador no enciende desde la mañana",
        "dependencia_id": 1,
    }
    datos.update(cambios)
    return datos


def _crear(cliente, h, quien="sol1"):
    r = cliente.post("/casos", json=_reporte(), headers=h[quien])
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _hasta_atencion(cliente, h, ids):
    caso = _crear(cliente, h)
    assert cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Alta"}, headers=h["coord"]).status_code == 200
    assert cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec1"]}, headers=h["coord"]).status_code == 200
    assert cliente.post(f"/casos/{caso}/iniciar-atencion", headers=h["tec1"]).status_code == 200
    return caso


# ---------------------------------------------------------------- US-01

def test_login_correcto_devuelve_token_y_rol(entorno):
    cliente, _, _ = entorno
    r = cliente.post("/auth/login", data={"username": "COORD@test.co", "password": PASSWORD})
    assert r.status_code == 200
    assert r.json()["rol"] == "coordinador"
    token = r.json()["access_token"]
    me = cliente.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["correo"] == "coord@test.co"


def test_login_incorrecto_mismo_mensaje(entorno):
    cliente, _, _ = entorno
    mal_pass = cliente.post("/auth/login", data={"username": "coord@test.co", "password": "x"})
    mal_correo = cliente.post("/auth/login", data={"username": "nadie@test.co", "password": "x"})
    inactivo = cliente.post("/auth/login", data={"username": "tec3@test.co", "password": PASSWORD})
    assert mal_pass.status_code == mal_correo.status_code == inactivo.status_code == 401
    assert mal_pass.json() == mal_correo.json()


def test_rutas_protegidas(entorno):
    cliente, h, _ = entorno
    assert cliente.get("/casos").status_code == 401
    assert cliente.get("/casos", headers={"Authorization": "Bearer basura"}).status_code == 401
    assert cliente.get("/coordinacion/resumen", headers=h["tec1"]).status_code == 403
    assert cliente.post("/casos", json=_reporte(), headers=h["coord"]).status_code == 403


def test_password_no_en_texto_plano(entorno):
    from app.seguridad import verificar_password

    guardado = hash_password("secreto")
    assert "secreto" not in guardado
    assert verificar_password("secreto", guardado)
    assert not verificar_password("otro", guardado)


# ---------------------------------------------------------------- US-02

def test_registrar_caso(entorno):
    cliente, h, _ = entorno
    r = cliente.post("/casos", json=_reporte(), headers=h["sol1"])
    assert r.status_code == 201
    caso = r.json()
    assert caso["estado"] == "Registrado"
    assert caso["prioridad"] is None and caso["tecnico"] is None
    assert caso["dependencia"] == "Biblioteca"


@pytest.mark.parametrize(
    "cambio",
    [
        {"descripcion": "corta"},
        {"placa_equipo": "   "},
        {"telefono": "abc"},
        {"fecha": (date.today() + timedelta(days=1)).isoformat()},
        {"dependencia_id": 99},
        {"dependencia_id": 2},  # inactiva
    ],
)
def test_registro_invalido_422(entorno, cambio):
    cliente, h, _ = entorno
    r = cliente.post("/casos", json=_reporte(**cambio), headers=h["sol1"])
    assert r.status_code == 422
    assert cliente.get("/casos", headers=h["sol1"]).json() == []


# ---------------------------------------------------------------- US-03

def test_solicitante_solo_ve_sus_casos(entorno):
    cliente, h, _ = entorno
    propio = _crear(cliente, h, "sol1")
    ajeno = _crear(cliente, h, "sol2")
    lista = cliente.get("/casos", headers=h["sol1"]).json()
    assert [c["id"] for c in lista] == [propio]
    assert cliente.get(f"/casos/{ajeno}", headers=h["sol1"]).status_code == 403
    assert cliente.get(f"/casos/{ajeno}/historial", headers=h["sol1"]).status_code == 403
    assert cliente.get("/casos/999", headers=h["sol1"]).status_code == 404


def test_tecnico_solo_ve_asignados(entorno):
    cliente, h, ids = entorno
    caso = _hasta_atencion(cliente, h, ids)
    _crear(cliente, h)
    assert [c["id"] for c in cliente.get("/casos", headers=h["tec1"]).json()] == [caso]
    assert cliente.get("/casos", headers=h["tec2"]).json() == []
    assert len(cliente.get("/casos", headers=h["coord"]).json()) == 2


# ---------------------------------------------------------------- US-04 / US-05

def test_evaluar(entorno):
    cliente, h, _ = entorno
    caso = _crear(cliente, h)
    assert cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Urgente"}, headers=h["coord"]).status_code == 422
    assert cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Alta"}, headers=h["tec1"]).status_code == 403
    r = cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Alta"}, headers=h["coord"])
    assert r.json()["estado"] == "En evaluación" and r.json()["prioridad"] == "Alta"
    # No se evalúa dos veces
    assert cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Baja"}, headers=h["coord"]).status_code == 400


def test_asignar_y_reasignar(entorno):
    cliente, h, ids = entorno
    caso = _crear(cliente, h)
    # Antes de evaluar no se asigna
    assert cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec1"]}, headers=h["coord"]).status_code == 400
    cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Media"}, headers=h["coord"])
    for invalido in (ids["sol1"], ids["tec_inactivo"], 999):
        r = cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": invalido}, headers=h["coord"])
        assert r.status_code == 422
    assert cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec1"]}, headers=h["tec1"]).status_code == 403

    r = cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec1"]}, headers=h["coord"])
    assert r.json()["estado"] == "Asignado" and r.json()["tecnico"] == "Técnico Uno"
    # Mismo técnico: rechazado
    assert cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec1"]}, headers=h["coord"]).status_code == 400

    r = cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec2"]}, headers=h["coord"])
    assert r.status_code == 200
    assert r.json()["estado"] == "Asignado" and r.json()["tecnico"] == "Técnico Dos"
    historial = cliente.get(f"/casos/{caso}/historial", headers=h["coord"]).json()
    reasignacion = [e for e in historial if e["tipo"] == "reasignacion"]
    assert reasignacion and "antes: Técnico Uno" in reasignacion[0]["detalle"]
    assert reasignacion[0]["autor"] == "Coordinador"
    # El técnico anterior ya no actúa ni ve el caso
    assert cliente.post(f"/casos/{caso}/iniciar-atencion", headers=h["tec1"]).status_code == 403


# ---------------------------------------------------------------- US-06 / US-07 / US-08

def test_flujo_completo(entorno):
    cliente, h, ids = entorno
    caso = _hasta_atencion(cliente, h, ids)

    # RN-03: no se resuelve sin intervención
    assert cliente.post(f"/casos/{caso}/resolver", json={"solucion": "Listo"}, headers=h["tec1"]).status_code == 400

    # RN-02: otro técnico no interviene
    datos = {"descripcion": "Se cambia la fuente de poder", "duracion_min": 40}
    assert cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec2"]).status_code == 403
    assert cliente.post(f"/casos/{caso}/intervenciones", json={**datos, "duracion_min": 0}, headers=h["tec1"]).status_code == 422
    r = cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec1"])
    assert r.status_code == 201 and r.json()["tecnico_id"] == ids["tec1"]

    # Solución vacía rechazada; luego se resuelve
    assert cliente.post(f"/casos/{caso}/resolver", json={"solucion": "  "}, headers=h["tec1"]).status_code == 422
    r = cliente.post(f"/casos/{caso}/resolver", json={"solucion": "Fuente reemplazada"}, headers=h["tec1"])
    assert r.json()["estado"] == "Resuelto" and r.json()["resuelto_en"]

    # Solo el coordinador cierra
    assert cliente.post(f"/casos/{caso}/cerrar", headers=h["tec1"]).status_code == 403
    r = cliente.post(f"/casos/{caso}/cerrar", headers=h["coord"])
    assert r.json()["estado"] == "Cerrado" and r.json()["cerrado_en"]

    # RN-04: cerrado no admite nada más
    assert cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec1"]).status_code == 400
    assert cliente.post(f"/casos/{caso}/cerrar", headers=h["coord"]).status_code == 400
    assert cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec2"]}, headers=h["coord"]).status_code == 400

    # CA-05: el solicitante ve la solución; CA-04: línea de tiempo completa
    detalle = cliente.get(f"/casos/{caso}", headers=h["sol1"]).json()
    assert detalle["solucion"] == "Fuente reemplazada"
    tipos = [e["tipo"] for e in cliente.get(f"/casos/{caso}/historial", headers=h["sol1"]).json()]
    assert tipos.count("cambio_estado") == 6
    assert "asignacion" in tipos and "intervencion" in tipos


def test_saltos_invalidos(entorno):
    cliente, h, ids = entorno
    caso = _crear(cliente, h)
    assert cliente.post(f"/casos/{caso}/cerrar", headers=h["coord"]).status_code == 400
    assert cliente.get(f"/casos/{caso}", headers=h["coord"]).json()["estado"] == "Registrado"
    caso2 = _hasta_atencion(cliente, h, ids)
    assert cliente.post(f"/casos/{caso2}/iniciar-atencion", headers=h["tec1"]).status_code == 400


# ---------------------------------------------------------------- US-10

def test_resumen_coordinador(entorno):
    cliente, h, ids = entorno
    _crear(cliente, h)
    _hasta_atencion(cliente, h, ids)
    r = cliente.get("/coordinacion/resumen", headers=h["coord"])
    assert r.status_code == 200
    resumen = r.json()
    assert resumen["total"] == 2 and resumen["abiertos"] == 2 and resumen["cerrados"] == 0
    assert resumen["por_estado"]["Registrado"] == 1 and resumen["por_estado"]["En atención"] == 1
    assert resumen["sin_asignar"] == 1
    tec1 = next(t for t in resumen["por_tecnico"] if t["tecnico_id"] == ids["tec1"])
    assert tec1["abiertos"] == 1


def test_catalogos(entorno):
    cliente, h, _ = entorno
    assert [d["nombre"] for d in cliente.get("/dependencias", headers=h["sol1"]).json()] == ["Biblioteca"]
    nombres = [t["nombre"] for t in cliente.get("/tecnicos", headers=h["coord"]).json()]
    assert nombres == ["Técnico Dos", "Técnico Uno"]
    assert cliente.get("/tecnicos", headers=h["sol1"]).status_code == 403
