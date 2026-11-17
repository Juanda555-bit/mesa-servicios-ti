"""Excepciones de dominio (RF-8). Python puro: no dependen de FastAPI.

La traducción a HTTP vive en `backend/app/errores.py`.
"""


class ErrorDominio(Exception):
    """Base de los errores que lanzan las reglas de negocio."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontrado(ErrorDominio):
    """El recurso no existe."""


class SinPermiso(ErrorDominio):
    """Permiso que depende del dato (caso ajeno, no es el responsable)."""


class DatoInvalido(ErrorDominio):
    """Dato que incumple una regla detectada en el servicio; `campo` lo nombra."""

    def __init__(self, mensaje: str, campo: str | None = None):
        super().__init__(mensaje)
        self.campo = campo


class TransicionInvalida(ErrorDominio):
    """Transición o estado no permitido (RN-01, RN-03, RN-04)."""


class NoAutenticado(ErrorDominio):
    """Credenciales no válidas."""
