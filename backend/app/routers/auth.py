"""RF-01: inicio de sesión y usuario autenticado."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from .. import esquemas, servicios
from ..deps import SesionBD, UsuarioActual
from ..seguridad import crear_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=esquemas.Token)
def login(sesion: SesionBD, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Recibe `username` (el correo) y `password` como formulario.

    Así funciona también el botón **Authorize** de esta página.
    """
    usuario = servicios.autenticar(sesion, form.username, form.password)
    return esquemas.Token(
        access_token=crear_token(usuario.id),
        rol=usuario.rol,
        nombre=usuario.nombre,
    )


@router.get("/me", response_model=esquemas.UsuarioSalida)
def yo(usuario: UsuarioActual):
    return usuario
