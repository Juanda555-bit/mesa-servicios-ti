"""Catálogos para formularios: dependencias activas (RF-02) y técnicos activos (RF-05)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db import Dependencia, Rol, Usuario


def dependencias_activas(sesion: Session) -> list[Dependencia]:
    consulta = select(Dependencia).where(Dependencia.activa.is_(True)).order_by(Dependencia.nombre)
    return list(sesion.scalars(consulta))


def tecnicos_activos(sesion: Session) -> list[Usuario]:
    consulta = (
        select(Usuario)
        .where(Usuario.rol == Rol.TECNICO, Usuario.activo.is_(True))
        .order_by(Usuario.nombre)
    )
    return list(sesion.scalars(consulta))
