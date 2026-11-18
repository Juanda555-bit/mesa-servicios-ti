"""Traducción de errores a HTTP (RF-8, RNF-04).

Los servicios lanzan excepciones de dominio sin saber de HTTP; aquí se
convierten en respuestas.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .servicios.excepciones import (
    DatoInvalido,
    ErrorDominio,
    NoAutenticado,
    NoEncontrado,
    SinPermiso,
    TransicionInvalida,
)

log = logging.getLogger("mesa_ti")

CODIGOS: dict[type[ErrorDominio], int] = {
    NoEncontrado: status.HTTP_404_NOT_FOUND,
    SinPermiso: status.HTTP_403_FORBIDDEN,
    DatoInvalido: 422,
    TransicionInvalida: status.HTTP_400_BAD_REQUEST,
    NoAutenticado: status.HTTP_401_UNAUTHORIZED,
}


async def error_de_dominio(_request: Request, exc: ErrorDominio):
    codigo = next((c for t, c in CODIGOS.items() if isinstance(exc, t)), 400)
    cuerpo: dict = {"detalle": exc.mensaje}
    if isinstance(exc, DatoInvalido) and exc.campo:
        cuerpo["campos"] = [{"campo": exc.campo, "motivo": exc.mensaje}]
    cabeceras = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
    return JSONResponse(status_code=codigo, content=cuerpo, headers=cabeceras)


MENSAJES = {
    401: "No autenticado o token inválido",
    403: "No tiene permiso para esta acción",
    404: "Recurso no encontrado",
    405: "Método no permitido",
}
GENERICOS_EN_INGLES = {"Not Found", "Method Not Allowed", "Not authenticated", "Forbidden", "Unauthorized"}

# Partes de `loc` que indican de dónde viene el dato, no cuál es el campo.
ORIGENES = {"body", "query", "path", "header", "cookie", "form"}


async def error_http(_request: Request, exc: StarletteHTTPException):
    propio = isinstance(exc.detail, str) and exc.detail not in GENERICOS_EN_INGLES
    detalle = exc.detail if propio else MENSAJES.get(exc.status_code, "No se pudo completar la solicitud")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detalle": detalle},
        headers=getattr(exc, "headers", None),
    )


def _unidades(n) -> str:
    return f"{n} carácter" if n == 1 else f"{n} caracteres"


def _motivo(error: dict) -> str:
    tipo = error.get("type", "")
    ctx = error.get("ctx") or {}
    if tipo == "missing":
        return "Campo obligatorio"
    if tipo == "string_too_short":
        return f"Debe tener al menos {_unidades(ctx.get('min_length'))}"
    if tipo == "string_too_long":
        return f"Debe tener como máximo {_unidades(ctx.get('max_length'))}"
    if tipo == "greater_than":
        return f"Debe ser mayor que {ctx.get('gt')}"
    if tipo in ("int_parsing", "int_type"):
        return "Debe ser un número entero"
    if tipo.startswith("date"):
        return "Debe ser una fecha válida (AAAA-MM-DD)"
    if tipo in ("enum", "literal_error"):
        return "Valor no permitido"
    if tipo == "value_error" and ctx.get("error") is not None:
        return str(ctx["error"])
    return "Valor no válido"


async def error_validacion(_request: Request, exc: RequestValidationError):
    # Nunca se copia "input": podría ser la contraseña enviada al login.
    campos = [
        {
            "campo": ".".join(str(p) for p in e.get("loc", ()) if p not in ORIGENES),
            "motivo": _motivo(e),
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detalle": "Datos de entrada no válidos", "campos": campos},
    )


# RNF-04: errores controlados, sin trazas internas en la respuesta.
async def error_integridad(_request: Request, exc: IntegrityError):
    log.warning("Integridad rechazada por la base: %s", exc.orig)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detalle": "La operación no cumple las reglas de integridad de los datos"},
    )


async def error_inesperado(_request: Request, exc: Exception):
    log.exception("Error no controlado", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detalle": "Error interno del servidor"},
    )


def registrar_manejadores(app: FastAPI) -> None:
    app.add_exception_handler(ErrorDominio, error_de_dominio)
    app.add_exception_handler(StarletteHTTPException, error_http)
    app.add_exception_handler(RequestValidationError, error_validacion)
    app.add_exception_handler(IntegrityError, error_integridad)
    app.add_exception_handler(Exception, error_inesperado)
