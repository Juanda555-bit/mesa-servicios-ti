"""Hash de contraseñas y tokens JWT (RF-01, RNF-02).

El hash usa PBKDF2-SHA256 de la biblioteca estándar, con sal aleatoria por
usuario, así no hace falta instalar nada extra. Formato guardado:
    pbkdf2_sha256$<iteraciones>$<sal hex>$<hash hex>
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from . import config

_ALGORITMO = "pbkdf2_sha256"
_ITERACIONES = 600_000
_ALGORITMO_JWT = "HS256"  # fijo: no se toma del entorno ni del token


def hash_password(password: str) -> str:
    sal = secrets.token_bytes(16)
    resumen = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, _ITERACIONES)
    return f"{_ALGORITMO}${_ITERACIONES}${sal.hex()}${resumen.hex()}"


# Hash de una clave aleatoria, mismo formato y coste que uno real (RF-5);
# se calcula al importar para no añadir latencia al primer login fallido.
HASH_FICTICIO = hash_password(secrets.token_hex(16))


def verificar_password(password: str, guardado: str) -> bool:
    try:
        algoritmo, iteraciones, sal_hex, resumen_hex = guardado.split("$")
        if algoritmo != _ALGORITMO:
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(sal_hex), int(iteraciones)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(calculado.hex(), resumen_hex)


def crear_token(usuario_id: int) -> str:
    """Token con solo `sub` y `exp`; el rol se lee siempre de la BD (RF-4)."""
    datos = {
        "sub": str(usuario_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=config.ajustes.jwt_expira_min),
    }
    return jwt.encode(datos, config.ajustes.jwt_secret, algorithm=_ALGORITMO_JWT)


def leer_token(token: str) -> int | None:
    """Devuelve el id del usuario del token, o None si no es válido o venció."""
    try:
        datos = jwt.decode(
            token,
            config.ajustes.jwt_secret,
            algorithms=[_ALGORITMO_JWT],
            options={"require": ["exp", "sub"]},
        )
        return int(datos["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        return None
