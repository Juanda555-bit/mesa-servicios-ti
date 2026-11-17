"""RF-5: autenticación sin revelar si el correo existe o está activo."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db import Usuario

from ..seguridad import HASH_FICTICIO, verificar_password
from .excepciones import NoAutenticado


def autenticar(sesion: Session, correo: str, password: str) -> Usuario:
    """Devuelve el usuario activo con esas credenciales o lanza NoAutenticado.

    Siempre hace una verificación de hash (contra uno ficticio si el correo no
    existe o el usuario está inactivo) para igualar el tiempo de respuesta.
    """
    usuario = sesion.scalar(
        select(Usuario).where(func.lower(Usuario.correo) == correo.strip().lower())
    )
    valido = usuario is not None and usuario.activo
    ok = verificar_password(password, usuario.password_hash if valido else HASH_FICTICIO)
    if not (valido and ok):
        raise NoAutenticado("Correo o contraseña incorrectos")
    return usuario
