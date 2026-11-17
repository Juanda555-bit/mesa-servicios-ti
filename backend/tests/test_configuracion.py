"""Pruebas de la configuración estricta (RF-1, RF-2) y del aislamiento del .env (RF-14).

Ejecución (desde la raíz del repositorio):
    .venv/Scripts/python.exe -m pytest backend/tests/test_configuracion.py -q
"""

import secrets
from pathlib import Path

import pytest

from backend.app import config
from backend.app.config import VALOR_EJEMPLO, ErrorConfiguracion, cargar_configuracion

RAIZ = Path(__file__).resolve().parents[2]
SECRETO_32 = "a" * 32


@pytest.mark.parametrize(
    "entorno",
    [
        {},
        {"JWT_SECRET": ""},
        {"JWT_SECRET": "a" * 31},
        {"JWT_SECRET": VALOR_EJEMPLO},
    ],
    ids=["ausente", "vacio", "31_caracteres", "valor_de_ejemplo"],
)
def test_jwt_secret_invalido_no_carga(entorno):
    with pytest.raises(ErrorConfiguracion) as error:
        cargar_configuracion(entorno)
    mensaje = str(error.value)
    assert "JWT_SECRET" in mensaje
    assert "secrets.token_hex(32)" in mensaje
    assert "Genere" in mensaje


def test_jwt_secret_de_32_carga():
    ajustes = cargar_configuracion({"JWT_SECRET": SECRETO_32})
    assert ajustes.jwt_secret == SECRETO_32
    assert ajustes.cors_origenes == ["http://localhost:5173"]


@pytest.mark.parametrize("valor", ["abc", "0", "-5"])
def test_jwt_expira_min_invalido(valor):
    with pytest.raises(ErrorConfiguracion) as error:
        cargar_configuracion({"JWT_SECRET": SECRETO_32, "JWT_EXPIRA_MIN": valor})
    assert "JWT_EXPIRA_MIN" in str(error.value)


def test_jwt_expira_min_por_defecto_480():
    assert cargar_configuracion({"JWT_SECRET": SECRETO_32}).jwt_expira_min == 480


def test_env_example_sin_valores_reales():
    texto = (RAIZ / ".env.example").read_text(encoding="utf-8")
    assert f"JWT_SECRET={VALOR_EJEMPLO}" in texto
    assert "JWT_EXPIRA_MIN" in texto
    assert "secrets.token_hex(32)" in texto
    assert "SECRET" + "_KEY" not in texto
    assert "TOKEN" + "_MINUTOS" not in texto
    # El ejemplo nunca debe ser aceptado como secreto real.
    with pytest.raises(ErrorConfiguracion):
        cargar_configuracion({"JWT_SECRET": VALOR_EJEMPLO})
    assert secrets.token_hex(32) != VALOR_EJEMPLO


def test_pruebas_aisladas_del_env_local(valores_de_prueba):
    from backend.db import database

    assert config.ajustes.jwt_secret == valores_de_prueba["JWT_SECRET"]
    assert config.ajustes.jwt_expira_min == int(valores_de_prueba["JWT_EXPIRA_MIN"])
    assert database.url_por_defecto() == valores_de_prueba["DATABASE_URL"]
    assert database.engine.url.database == ":memory:"  # str(url) escapa los dos puntos
