"""Dependencias comunes: sesión de base de datos, usuario autenticado y roles."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db import Rol, Usuario, get_session

from .seguridad import leer_token

# tokenUrl hace que el botón "Authorize" de Swagger (/docs) use /auth/login.
oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

SesionBD = Annotated[Session, Depends(get_session)]


def usuario_actual(sesion: SesionBD, token: Annotated[str | None, Depends(oauth2)]) -> Usuario:
    no_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado o token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise no_autenticado
    usuario_id = leer_token(token)
    usuario = sesion.get(Usuario, usuario_id) if usuario_id is not None else None
    if usuario is None or not usuario.activo:
        raise no_autenticado
    return usuario


UsuarioActual = Annotated[Usuario, Depends(usuario_actual)]


def requiere_rol(*roles: Rol):
    """Dependencia que deja pasar solo a los roles indicados (403 en otro caso)."""

    def _verificar(usuario: UsuarioActual) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Su rol no permite esta acción")
        return usuario

    return _verificar


Solicitante = Annotated[Usuario, Depends(requiere_rol(Rol.SOLICITANTE))]
Tecnico = Annotated[Usuario, Depends(requiere_rol(Rol.TECNICO))]
Coordinador = Annotated[Usuario, Depends(requiere_rol(Rol.COORDINADOR))]
