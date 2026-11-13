"""RF-01: inicio de sesión y usuario autenticado."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select

from db import Usuario

from .. import esquemas
from ..deps import SesionBD, UsuarioActual
from ..seguridad import crear_token, verificar_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=esquemas.Token)
def login(sesion: SesionBD, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Recibe `username` (el correo) y `password` como formulario.

    Así funciona también el botón **Authorize** de esta página.
    """
    usuario = sesion.scalar(
        select(Usuario).where(func.lower(Usuario.correo) == form.username.strip().lower())
    )
    # Mismo mensaje si falla el correo o la contraseña (CA-US01.2).
    if usuario is None or not usuario.activo or not verificar_password(
        form.password, usuario.password_hash
    ):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return esquemas.Token(
        access_token=crear_token(usuario.id, usuario.rol.value),
        rol=usuario.rol,
        nombre=usuario.nombre,
    )


@router.get("/me", response_model=esquemas.UsuarioSalida)
def yo(usuario: UsuarioActual):
    return usuario
