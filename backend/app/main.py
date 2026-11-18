"""Aplicación FastAPI de la Mesa de Servicios TI.

Ejecutar desde la raíz del repositorio:
    .venv/Scripts/python.exe -m uvicorn backend.app.main:app --reload
Documentación interactiva (RNF-05): http://localhost:8000/docs
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.database import engine, inicializar_base

from . import config
from .errores import registrar_manejadores
from .routers import auth, casos, catalogos, coordinacion

log = logging.getLogger("mesa_ti")


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    if inicializar_base(engine):
        log.info("Base de datos creada desde schema.sql. Ejecute 'python -m backend.seed' para datos de prueba.")
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
    allow_origins=config.ajustes.cors_origenes,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


registrar_manejadores(app)


@app.get("/salud", tags=["Sistema"])
def salud():
    return {"estado": "ok"}


app.include_router(auth.router)
app.include_router(catalogos.router)
app.include_router(casos.router)
app.include_router(coordinacion.router)
