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


def hash_password(password: str) -> str:
    sal = secrets.token_bytes(16)
    resumen = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), sal, _ITERACIONES)
    return f"{_ALGORITMO}${_ITERACIONES}${sal.hex()}${resumen.hex()}"


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


def crear_token(usuario_id: int, rol: str) -> str:
    ahora = datetime.now(timezone.utc)
    datos = {
        "sub": str(usuario_id),
        "rol": rol,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=config.TOKEN_MINUTOS),
    }
    return jwt.encode(datos, config.SECRET_KEY, algorithm=config.ALGORITMO_JWT)


def leer_token(token: str) -> int | None:
    """Devuelve el id del usuario del token, o None si no es válido o venció."""
    try:
        datos = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITMO_JWT])
        return int(datos["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
