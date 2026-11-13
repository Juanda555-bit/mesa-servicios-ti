"""Aplicación FastAPI de la Mesa de Servicios TI.

Ejecutar desde la carpeta backend:
    uvicorn app.main:app --reload
Documentación interactiva (RNF-05): http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from db.database import engine, inicializar_base

from . import config
from .routers import auth, casos, catalogos, coordinacion

log = logging.getLogger("mesa_ti")


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    if inicializar_base(engine):
        log.info("Base de datos creada desde schema.sql. Ejecute 'python seed.py' para datos de prueba.")
    yield


app = FastAPI(
    title="Mesa de Servicios TI",
    description=(
        "API REST para registrar, asignar, atender y cerrar casos de soporte.\n\n"
        "Para probar: **Authorize** con el correo y la contraseña de un usuario del seeder."
    ),
    version="1.0.0",
    lifespan=ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# RNF-04: errores controlados, sin trazas internas en la respuesta.
@app.exception_handler(IntegrityError)
async def error_integridad(_request: Request, exc: IntegrityError):
    log.warning("Integridad rechazada por la base: %s", exc.orig)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "La operación viola una regla de integridad de los datos"},
    )


@app.exception_handler(Exception)
async def error_inesperado(_request: Request, exc: Exception):
    log.exception("Error no controlado", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"},
    )


@app.get("/salud", tags=["Sistema"])
def salud():
    return {"estado": "ok"}


app.include_router(auth.router)
app.include_router(catalogos.router)
app.include_router(casos.router)
app.include_router(coordinacion.router)
