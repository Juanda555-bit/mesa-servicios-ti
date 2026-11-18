"""Pruebas de integración de la API (historias US-01 a US-10).

Cada prueba usa una base SQLite temporal creada desde schema.sql.
Ejecución (desde la raíz del repositorio):
    .venv/Scripts/python.exe -m pytest backend -q
"""

import re
from datetime import date, datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from backend.app import config
from backend.app.main import app
from backend.app.seguridad import crear_token, hash_password
from backend.db import Dependencia, Prioridad, Rol, Usuario, crear_engine, get_session, inicializar_base

PASSWORD = "Clave123*"


@pytest.fixture()
def entorno(tmp_path):
    ruta = tmp_path / "prueba.db"
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

    cliente = TestClient(app)
    encabezados = {
        clave: {"Authorization": f"Bearer {crear_token(ids[clave])}"}
        for clave in ids
    }
    yield cliente, encabezados, ids
    app.dependency_overrides.clear()
    engine.dispose()


PARES_ESPERADOS = {
    ("GET", "/salud"),
    ("POST", "/auth/login"),
    ("GET", "/auth/me"),
    ("GET", "/dependencias"),
    ("POST", "/casos"),
    ("GET", "/casos"),
    ("GET", "/casos/{id}"),
    ("PATCH", "/casos/{id}/evaluacion"),
    ("PUT", "/casos/{id}/tecnico"),
    ("POST", "/casos/{id}/iniciar-atencion"),
    ("POST", "/casos/{id}/intervenciones"),
    ("POST", "/casos/{id}/resolver"),
    ("POST", "/casos/{id}/cerrar"),
    ("GET", "/casos/{id}/historial"),
    ("GET", "/tecnicos"),
    ("GET", "/coordinacion/resumen"),
}


def test_salud_y_openapi_exponen_los_16_pares():
    cliente = TestClient(app)  # sin "with": no dispara el lifespan
    assert cliente.get("/salud").status_code == 200
    r = cliente.get("/openapi.json")
    assert r.status_code == 200
    metodos = {"get", "post", "put", "patch", "delete"}
    obtenidos = {
        (m.upper(), re.sub(r"\{[^}]+\}", "{id}", ruta))
        for ruta, ops in r.json()["paths"].items()
        for m in ops
        if m in metodos
    }
    assert obtenidos == PARES_ESPERADOS


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

# ------------------------------------------------- token estricto (RF-3, RF-4)

def _firmar(datos, clave=None, algoritmo="HS256"):
    clave = clave if clave is not None else config.ajustes.jwt_secret
    return jwt.encode(datos, clave, algorithm=algoritmo)


def _ts(minutos):
    return datetime.now(timezone.utc) + timedelta(minutes=minutos)


def _token_alg_none(datos):
    import base64
    import json

    def b64(d):
        return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()

    return f"{b64({'alg': 'none', 'typ': 'JWT'})}.{b64(datos)}."


def _tokens_invalidos(uid):
    base = {"sub": str(uid), "exp": _ts(30)}
    return {
        "vencido": _firmar({"sub": str(uid), "exp": _ts(-5)}),
        "sin_exp": _firmar({"sub": str(uid)}),
        "sin_sub": _firmar({"exp": _ts(30)}),
        "alg_none": _token_alg_none({"sub": str(uid), "exp": int(_ts(30).timestamp())}),
        "otra_firma": _firmar(base, clave="otra-clave-distinta-0123456789abcdefghij"),
    }


@pytest.mark.parametrize("caso", ["vencido", "sin_exp", "sin_sub", "alg_none", "otra_firma"])
def test_token_invalido_401(entorno, caso):
    cliente, h, ids = entorno
    cab = {"Authorization": f"Bearer {_tokens_invalidos(ids['sol1'])[caso]}"}
    assert cliente.get("/auth/me", headers=cab).status_code == 401
    assert cliente.post("/casos", json=_reporte(), headers=cab).status_code == 401
    r = cliente.get("/casos", headers=h["coord"])
    assert r.status_code == 200 and len(r.json()) == 0


def test_token_solo_sub_y_exp(entorno):
    _, _, ids = entorno
    datos = jwt.decode(
        crear_token(ids["coord"]), config.ajustes.jwt_secret, algorithms=["HS256"]
    )
    assert set(datos) == {"sub", "exp"}


def test_login_devuelve_rol_correcto(entorno):
    cliente, _, _ = entorno
    for correo, rol in [("coord@test.co", "coordinador"), ("tec1@test.co", "tecnico"), ("sol1@test.co", "solicitante")]:
        r = cliente.post("/auth/login", data={"username": correo, "password": PASSWORD})
        assert r.status_code == 200
        assert r.json()["rol"] == rol
        assert "rol" not in jwt.decode(r.json()["access_token"], config.ajustes.jwt_secret, algorithms=["HS256"])


def test_claim_rol_manipulado_403(entorno):
    cliente, _, ids = entorno
    token = _firmar({"sub": str(ids["sol1"]), "rol": "coordinador", "exp": _ts(30)})
    cab = {"Authorization": f"Bearer {token}"}
    assert cliente.get("/coordinacion/resumen", headers=cab).status_code == 403
    assert cliente.patch("/casos/1/evaluacion", json={"prioridad": "Alta"}, headers=cab).status_code == 403



def test_login_incorrecto_mismo_mensaje(entorno):
    cliente, _, _ = entorno
    mal_pass = cliente.post("/auth/login", data={"username": "coord@test.co", "password": "x"})
    mal_correo = cliente.post("/auth/login", data={"username": "nadie@test.co", "password": "x"})
    inactivo = cliente.post("/auth/login", data={"username": "tec3@test.co", "password": PASSWORD})
    assert mal_pass.status_code == mal_correo.status_code == inactivo.status_code == 401
    assert mal_pass.json() == mal_correo.json()


def test_login_verifica_hash_siempre(entorno, monkeypatch):
    from backend.app.servicios import auth as servicio_auth

    cliente, _, _ = entorno
    llamadas = []
    original = servicio_auth.verificar_password

    def espia(password, guardado):
        llamadas.append(guardado)
        return original(password, guardado)

    monkeypatch.setattr("backend.app.servicios.auth.verificar_password", espia)
    casos = [
        ("nadie@test.co", "x"),  # correo inexistente
        ("tec3@test.co", PASSWORD),  # usuario inactivo
        ("coord@test.co", "incorrecta"),  # contraseña incorrecta
    ]
    respuestas = []
    for correo, clave in casos:
        antes = len(llamadas)
        r = cliente.post("/auth/login", data={"username": correo, "password": clave})
        assert len(llamadas) - antes == 1, correo
        respuestas.append(r)
    assert all(r.status_code == 401 for r in respuestas)
    assert respuestas[0].json() == respuestas[1].json() == respuestas[2].json()


def test_rutas_protegidas(entorno):
    cliente, h, _ = entorno
    assert cliente.get("/casos").status_code == 401
    assert cliente.get("/casos", headers={"Authorization": "Bearer basura"}).status_code == 401
    assert cliente.get("/coordinacion/resumen", headers=h["tec1"]).status_code == 403
    assert cliente.post("/casos", json=_reporte(), headers=h["coord"]).status_code == 403


def test_password_no_en_texto_plano(entorno):
    from backend.app.seguridad import verificar_password

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
        {"telefono": ""},
        {"telefono": "   "},
        {"telefono": "1" * 21},
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


def test_telefono_sin_patron(entorno):
    """RF-12: el teléfono solo exige 1-20 caracteres; sin patrón."""
    cliente, h, _ = entorno
    assert cliente.post("/casos", json=_reporte(telefono="abc"), headers=h["sol1"]).status_code == 201
    assert cliente.post("/casos", json=_reporte(telefono="1" * 20), headers=h["sol1"]).status_code == 201
    assert cliente.post("/casos", json=_reporte(telefono="1" * 21), headers=h["sol1"]).status_code == 422


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


def test_duracion_sin_maximo(entorno):
    """RF-12: la duración solo exige ser mayor a 0 (sin tope de 1440)."""
    cliente, h, ids = entorno
    caso = _hasta_atencion(cliente, h, ids)
    datos = {"descripcion": "Trabajo de varios días en sitio", "duracion_min": 1441}
    assert cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec1"]).status_code == 201


@pytest.mark.parametrize("hasta", ["asignado", "resuelto"])
def test_intervencion_fuera_de_atencion_400(entorno, hasta):
    """EQ-06 / RF-13: intervenir solo es posible En atención."""
    cliente, h, ids = entorno
    caso = _crear(cliente, h)
    cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Alta"}, headers=h["coord"])
    cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec1"]}, headers=h["coord"])
    datos = {"descripcion": "Se revisa el equipo en sitio", "duracion_min": 15}
    if hasta == "resuelto":
        cliente.post(f"/casos/{caso}/iniciar-atencion", headers=h["tec1"])
        assert cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec1"]).status_code == 201
        assert cliente.post(f"/casos/{caso}/resolver", json={"solucion": "Listo"}, headers=h["tec1"]).status_code == 200
    r = cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec1"])
    assert r.status_code == 400
    n = [e for e in cliente.get(f"/casos/{caso}/historial", headers=h["coord"]).json() if e["tipo"] == "intervencion"]
    assert len(n) == (1 if hasta == "resuelto" else 0)


def test_resolver_cerrar_invalidos_sin_efectos_http(entorno):
    """RF-9 (a): una petición rechazada no cambia el caso ni su historial."""
    cliente, h, ids = entorno

    def _estado(caso):
        return (
            cliente.get(f"/casos/{caso}", headers=h["coord"]).json(),
            cliente.get(f"/casos/{caso}/historial", headers=h["coord"]).json(),
        )

    def _rechazada(metodo_url, quien, caso, **kw):
        antes = _estado(caso)
        assert cliente.post(metodo_url, headers=h[quien], **kw).status_code == 400
        assert _estado(caso) == antes

    caso = _crear(cliente, h)
    _rechazada(f"/casos/{caso}/cerrar", "coord", caso)
    cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Alta"}, headers=h["coord"])
    cliente.put(f"/casos/{caso}/tecnico", json={"tecnico_id": ids["tec1"]}, headers=h["coord"])
    _rechazada(f"/casos/{caso}/resolver", "tec1", caso, json={"solucion": "Listo"})
    # Resuelto: resolver de nuevo es inválido
    cliente.post(f"/casos/{caso}/iniciar-atencion", headers=h["tec1"])
    datos = {"descripcion": "Se revisa el equipo en sitio", "duracion_min": 15}
    cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec1"])
    # En atención: cerrar es inválido
    _rechazada(f"/casos/{caso}/cerrar", "coord", caso)
    cliente.post(f"/casos/{caso}/resolver", json={"solucion": "Listo"}, headers=h["tec1"])
    _rechazada(f"/casos/{caso}/resolver", "tec1", caso, json={"solucion": "Otra"})
    # Cerrado: resolver y cerrar son inválidos
    assert cliente.post(f"/casos/{caso}/cerrar", headers=h["coord"]).status_code == 200
    _rechazada(f"/casos/{caso}/cerrar", "coord", caso)
    _rechazada(f"/casos/{caso}/resolver", "tec1", caso, json={"solucion": "Otra"})


def test_resolver_cerrar_invalidos_sin_efectos_servicio(entorno):
    """RF-9 (b): el servicio valida antes de asignar solucion/resuelto_en/cerrado_en."""
    from backend.app import servicios
    from backend.db import HistorialEstado
    from backend.app.servicios.excepciones import TransicionInvalida

    cliente, h, ids = entorno
    caso_id = _crear(cliente, h)
    sesion = next(app.dependency_overrides[get_session]())
    coord, tec1 = sesion.get(Usuario, ids["coord"]), sesion.get(Usuario, ids["tec1"])
    caso = servicios.obtener_caso_visible(sesion, coord, caso_id)

    def _sin_historial_nuevo():
        return not any(isinstance(o, HistorialEstado) for o in sesion.new)

    estado = caso.estado
    with pytest.raises(TransicionInvalida):
        servicios.cerrar(sesion, caso, coord)
    assert caso.cerrado_en is None and caso.estado == estado and _sin_historial_nuevo()

    servicios.evaluar(sesion, caso, coord, Prioridad.ALTA)
    servicios.asignar_tecnico(sesion, caso, coord, ids["tec1"])
    sesion.flush()
    estado = caso.estado
    with pytest.raises(TransicionInvalida):
        servicios.resolver(sesion, caso, tec1, "Listo")
    assert caso.solucion is None and caso.resuelto_en is None
    assert caso.estado == estado and _sin_historial_nuevo()


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


# ---------------------------------------------------------------- RF-8 (cobertura 001)

def test_solicitante_403_en_acciones_de_coordinador(entorno):
    # RN-07 / CA-US04.3, CA-US08.4, CA-US10.3
    cliente, h, _ = entorno
    caso = _crear(cliente, h)
    r = cliente.patch(f"/casos/{caso}/evaluacion", json={"prioridad": "Alta"}, headers=h["sol1"])
    assert r.status_code == 403
    assert cliente.post(f"/casos/{caso}/cerrar", headers=h["sol1"]).status_code == 403
    assert cliente.get("/coordinacion/resumen", headers=h["sol1"]).status_code == 403
    assert cliente.get(f"/casos/{caso}", headers=h["coord"]).json()["estado"] == "Registrado"


def test_404_con_rol_permitido_sobre_caso_inexistente(entorno):
    # CA-US03.3, CA-US06.3 / RN-06: el 404 se evalúa con el rol permitido y cuerpo válido
    cliente, h, ids = entorno
    inexistente = 999
    intervencion = {"descripcion": "Se revisa el equipo en sitio", "duracion_min": 15}
    peticiones = [
        ("PATCH", "evaluacion", {"prioridad": "Alta"}, "coord"),
        ("PUT", "tecnico", {"tecnico_id": ids["tec1"]}, "coord"),
        ("POST", "iniciar-atencion", None, "tec1"),
        ("POST", "intervenciones", intervencion, "tec1"),
        ("POST", "resolver", {"solucion": "Equipo reparado"}, "tec1"),
        ("POST", "cerrar", None, "coord"),
        ("GET", "historial", None, "coord"),
    ]
    for metodo, accion, cuerpo, quien in peticiones:
        kwargs = {"headers": h[quien]}
        if cuerpo is not None:
            kwargs["json"] = cuerpo
        r = cliente.request(metodo, f"/casos/{inexistente}/{accion}", **kwargs)
        assert r.status_code == 404, f"{metodo} {accion}: {r.status_code} {r.text}"


@pytest.mark.parametrize("metodo", ["PUT", "PATCH", "DELETE"])
def test_intervencion_no_editable_ni_borrable(entorno, metodo):
    # RN-05 / CA-US06.3: no existen rutas de edición ni borrado de intervenciones
    cliente, h, ids = entorno
    caso = _hasta_atencion(cliente, h, ids)
    datos = {"descripcion": "Se cambia la fuente de poder", "duracion_min": 40}
    creada = cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec1"])
    assert creada.status_code == 201
    inter_id = creada.json()["id"]
    antes = cliente.get(f"/casos/{caso}/historial", headers=h["coord"]).json()
    assert any(e["tipo"] == "intervencion" for e in antes)

    rutas = [f"/casos/{caso}/intervenciones", f"/casos/{caso}/intervenciones/{inter_id}"]
    for ruta in rutas:
        for quien in ("tec1", "coord"):
            kwargs = {"headers": h[quien]}
            if metodo != "DELETE":
                kwargs["json"] = {"descripcion": "Texto alterado", "duracion_min": 1}
            r = cliente.request(metodo, ruta, **kwargs)
            assert not (200 <= r.status_code < 300), f"{metodo} {ruta}: {r.status_code}"

    despues = cliente.get(f"/casos/{caso}/historial", headers=h["coord"]).json()
    assert despues == antes


# ---------------------------------------------------------------- RF-8 (capas)

def test_servicio_lanza_excepciones_de_dominio(entorno):
    from sqlalchemy.orm import sessionmaker  # noqa: F401
    from backend.app import esquemas, servicios
    from backend.app.servicios.excepciones import (
        DatoInvalido,
        ErrorDominio,
        NoEncontrado,
        SinPermiso,
        TransicionInvalida,
    )

    cliente, h, ids = entorno
    caso_id = _crear(cliente, h)
    sesion = next(app.dependency_overrides[get_session]())
    sol1, sol2, coord, tec1 = (sesion.get(Usuario, ids[k]) for k in ("sol1", "sol2", "coord", "tec1"))

    with pytest.raises(NoEncontrado):
        servicios.obtener_caso_visible(sesion, coord, 9999)
    with pytest.raises(SinPermiso):
        servicios.obtener_caso_visible(sesion, sol2, caso_id)
    caso = servicios.obtener_caso_visible(sesion, coord, caso_id)
    servicios.evaluar(sesion, caso, coord, Prioridad.ALTA)
    with pytest.raises(TransicionInvalida):
        servicios.evaluar(sesion, caso, coord, Prioridad.ALTA)
    with pytest.raises(SinPermiso):
        servicios.iniciar_atencion(sesion, caso, tec1)
    with pytest.raises(DatoInvalido) as exc:
        servicios.registrar_caso(sesion, sol1, esquemas.CasoNuevo(**_reporte(dependencia_id=99)))
    assert exc.value.campo == "dependencia_id"
    assert isinstance(exc.value, ErrorDominio)


def test_error_de_dominio_usa_detalle(entorno):
    cliente, h, ids = entorno
    caso = _crear(cliente, h)
    r404 = cliente.get("/casos/9999", headers=h["coord"])
    r403 = cliente.get(f"/casos/{caso}", headers=h["sol2"])
    r400 = cliente.post(f"/casos/{caso}/cerrar", headers=h["coord"])
    r422 = cliente.post("/casos", json=_reporte(dependencia_id=99), headers=h["sol1"])
    for r, codigo in ((r404, 404), (r403, 403), (r400, 400), (r422, 422)):
        assert r.status_code == codigo
        assert isinstance(r.json()["detalle"], str) and "detail" not in r.json()
    assert any(c["campo"] == "dependencia_id" for c in r422.json()["campos"])


# ---------------------------------------------------------------- RF-10, RF-11 (errores)

def _peticion_de_error(caso_error, cliente, h, ids, monkeypatch):
    """Devuelve (respuesta, código esperado) para cada tipo de error."""
    caso = _crear(cliente, h)
    if caso_error == "400":
        return cliente.post(f"/casos/{caso}/cerrar", headers=h["coord"]), 400
    if caso_error == "401":
        return cliente.get("/casos"), 401
    if caso_error == "403":
        return cliente.get("/coordinacion/resumen", headers=h["sol1"]), 403
    if caso_error == "404-dominio":
        return cliente.get("/casos/9999", headers=h["coord"]), 404
    if caso_error == "404-ruta":
        return cliente.get("/no-existe", headers=h["coord"]), 404
    if caso_error == "404-intervencion":
        return cliente.get(f"/casos/{caso}/intervenciones/1", headers=h["coord"]), 404
    if caso_error.startswith("405-"):
        metodo = caso_error.split("-")[1]
        return cliente.request(metodo, f"/casos/{caso}/intervenciones", headers=h["coord"]), 405
    if caso_error == "422":
        return cliente.post("/casos", json=_reporte(telefono=""), headers=h["sol1"]), 422
    if caso_error == "500":
        def _falla(_sesion):
            raise RuntimeError("fallo interno con ruta C:/secreto/app.py")

        monkeypatch.setattr("backend.app.servicios.tecnicos_activos", _falla)
        sin_relanzar = TestClient(app, raise_server_exceptions=False)
        return sin_relanzar.get("/tecnicos", headers=h["coord"]), 500
    raise AssertionError(caso_error)


@pytest.mark.parametrize(
    "caso_error",
    ["400", "401", "403", "404-dominio", "404-ruta", "404-intervencion",
     "405-PUT", "405-PATCH", "405-DELETE", "422", "500"],
)
def test_errores_usan_detalle(entorno, monkeypatch, caso_error):
    # RF-10 / RF-11, RNF-04: mismo cuerpo en todos los errores, en español y sin trazas
    cliente, h, ids = entorno
    r, codigo = _peticion_de_error(caso_error, cliente, h, ids, monkeypatch)
    assert r.status_code == codigo, r.text
    cuerpo = r.json()
    assert isinstance(cuerpo["detalle"], str) and cuerpo["detalle"]
    assert "detail" not in cuerpo
    assert ("campos" in cuerpo) == (codigo == 422)
    if codigo == 500:
        assert "secreto" not in r.text and "Traceback" not in r.text
    if codigo == 401:
        assert r.headers["www-authenticate"] == "Bearer"
    # los mensajes del framework se traducen
    assert cuerpo["detalle"] not in {"Not Found", "Method Not Allowed", "Not authenticated"}


def test_422_lista_todos_los_campos(entorno):
    cliente, h, _ = entorno
    r = cliente.post("/casos", json=_reporte(telefono="", descripcion="corta"), headers=h["sol1"])
    assert r.status_code == 422
    campos = {c["campo"]: c["motivo"] for c in r.json()["campos"]}
    assert {"telefono", "descripcion"} <= set(campos)
    assert all(isinstance(m, str) and m for m in campos.values())
    assert "corta" not in r.text and "input" not in r.text
    # login: no filtra la contraseña enviada
    r = cliente.post("/auth/login", data={"username": "sol1@test.co"})
    assert r.status_code == 422
    assert "password" in {c["campo"] for c in r.json()["campos"]}


def test_motivo_longitud_singular_y_plural():
    """RF-20: concordancia carácter/caracteres en los motivos de longitud."""
    from backend.app.errores import _motivo

    corto = lambda n: {"type": "string_too_short", "ctx": {"min_length": n}}
    largo = lambda n: {"type": "string_too_long", "ctx": {"max_length": n}}
    assert _motivo(corto(1)) == "Debe tener al menos 1 carácter"
    assert _motivo(corto(15)) == "Debe tener al menos 15 caracteres"
    assert _motivo(largo(1)) == "Debe tener como máximo 1 carácter"
    assert _motivo(largo(20)) == "Debe tener como máximo 20 caracteres"


def test_422_motivos_de_longitud(entorno):
    cliente, h, _ = entorno
    r = cliente.post(
        "/casos",
        json=_reporte(placa_equipo="", descripcion="corta", telefono="1" * 21),
        headers=h["sol1"],
    )
    assert r.status_code == 422
    campos = {c["campo"]: c["motivo"] for c in r.json()["campos"]}
    assert campos["placa_equipo"] == "Debe tener al menos 1 carácter"
    assert campos["descripcion"] == "Debe tener al menos 15 caracteres"
    assert campos["telefono"] == "Debe tener como máximo 20 caracteres"


def test_integridad_400_sin_detalles_internos(entorno, monkeypatch):
    # RF-10: IntegrityError -> 400, sin SQL ni nombres de tabla en el cuerpo
    from sqlalchemy.exc import IntegrityError

    from backend.app.errores import error_integridad
    from backend.app.servicios import casos as servicios_casos
    import asyncio

    exc = IntegrityError("INSERT INTO caso (secreto) VALUES (?)", {}, Exception("UNIQUE constraint failed: caso.placa"))
    r = asyncio.run(error_integridad(None, exc))
    assert r.status_code == 400
    texto = r.body.decode()
    assert "detalle" in texto and "detail" not in texto
    assert "INSERT" not in texto and "placa" not in texto and "UNIQUE" not in texto

    # IntegrityError real de la BD: se salta la validación del servicio y
    # el trigger de caso cerrado inmutable rechaza el UPDATE.
    cliente, h, ids = entorno
    caso = _hasta_atencion(cliente, h, ids)
    datos = {"descripcion": "Se revisa el equipo en sitio", "duracion_min": 15}
    cliente.post(f"/casos/{caso}/intervenciones", json=datos, headers=h["tec1"])
    cliente.post(f"/casos/{caso}/resolver", json={"solucion": "Listo"}, headers=h["tec1"])
    assert cliente.post(f"/casos/{caso}/cerrar", headers=h["coord"]).status_code == 200
    monkeypatch.setattr(servicios_casos, "_validar_transicion", lambda caso, nuevo: None)
    r = cliente.post(f"/casos/{caso}/cerrar", headers=h["coord"])
    assert r.status_code == 400
    assert r.json() == {"detalle": r.json()["detalle"]}
    minusculas = r.text.lower()
    for prohibido in ("sqlite", "insert", "update", "traceback", "historial_estado", "asignacion", "intervencion", "usuario"):
        assert prohibido not in minusculas
    assert not re.search(r"caso", minusculas.replace(r.json()["detalle"].lower(), ""))
