"""Esquemas de autenticación (RF-01)."""

from pydantic import BaseModel

from backend.db import Rol

from .comun import Salida


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: Rol
    nombre: str


class UsuarioSalida(Salida):
    id: int
    nombre: str
    correo: str
    rol: Rol
