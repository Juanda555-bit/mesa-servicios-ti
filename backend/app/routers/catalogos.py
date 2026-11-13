"""Catálogos para formularios: dependencias (RF-02) y técnicos (RF-05)."""

from fastapi import APIRouter
from sqlalchemy import select

from db import Dependencia

from .. import esquemas, servicios
from ..deps import Coordinador, SesionBD, UsuarioActual

router = APIRouter(tags=["Catálogos"])


@router.get("/dependencias", response_model=list[esquemas.DependenciaSalida])
def listar_dependencias(sesion: SesionBD, _usuario: UsuarioActual):
    consulta = select(Dependencia).where(Dependencia.activa.is_(True)).order_by(Dependencia.nombre)
    return list(sesion.scalars(consulta))


@router.get("/tecnicos", response_model=list[esquemas.TecnicoSalida])
def listar_tecnicos(sesion: SesionBD, _coordinador: Coordinador):
    return servicios.tecnicos_activos(sesion)
