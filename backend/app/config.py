"""Configuración leída del archivo .env (ver .env.example).

`JWT_SECRET` es obligatorio (RF-1) y `JWT_EXPIRA_MIN` se valida (RF-2): si algo
no es válido, la API y el seeder terminan con un mensaje en español.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass

from dotenv import load_dotenv

from backend.db.database import BACKEND_DIR

# Valor de .env.example: se rechaza por ser el ejemplo aunque tenga 32 caracteres o más.
VALOR_EJEMPLO = "cambiar-por-una-clave-aleatoria-de-64-caracteres-hex"
LONGITUD_MINIMA_SECRETO = 32
EXPIRA_MIN_POR_DEFECTO = 480


class ErrorConfiguracion(ValueError):
    """La configuración del entorno no es válida."""


@dataclass(frozen=True)
class Configuracion:
    jwt_secret: str
    jwt_expira_min: int
    cors_origenes: list[str]


def cargar_configuracion(entorno: Mapping[str, str]) -> Configuracion:
    secreto = (entorno.get("JWT_SECRET") or "").strip()
    if len(secreto) < LONGITUD_MINIMA_SECRETO or secreto == VALOR_EJEMPLO:
        raise ErrorConfiguracion(
            f"JWT_SECRET falta, tiene menos de {LONGITUD_MINIMA_SECRETO} caracteres o es el valor de ejemplo. "
            'Genere una con: python -c "import secrets; print(secrets.token_hex(32))" '
            "y guárdela en el archivo .env"
        )

    bruto = entorno.get("JWT_EXPIRA_MIN")
    if bruto is None:
        expira_min = EXPIRA_MIN_POR_DEFECTO
    else:
        try:
            expira_min = int(bruto.strip())
        except ValueError:
            expira_min = 0
        if expira_min <= 0:
            raise ErrorConfiguracion("JWT_EXPIRA_MIN debe ser un número entero de minutos mayor que 0")

    cors = [
        origen.strip()
        for origen in (entorno.get("CORS_ORIGINS") or "http://localhost:5173").split(",")
        if origen.strip()
    ]
    return Configuracion(jwt_secret=secreto, jwt_expira_min=expira_min, cors_origenes=cors)


load_dotenv(BACKEND_DIR.parent / ".env")

try:
    ajustes = cargar_configuracion(os.environ)
except ErrorConfiguracion as error:
    raise SystemExit(f"Configuración no válida: {error}") from None
