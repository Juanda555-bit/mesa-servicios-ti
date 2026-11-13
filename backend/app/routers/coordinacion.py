"""RF-10 / CA-06: tablero consolidado del coordinador."""

from collections import Counter

from fastapi import APIRouter
from sqlalchemy import select

from db import Estado, VCasoDetalle

from .. import esquemas, servicios
from ..deps import Coordinador, SesionBD

router = APIRouter(prefix="/coordinacion", tags=["Coordinación"])


@router.get("/resumen", response_model=esquemas.Resumen)
def resumen(sesion: SesionBD, _coordinador: Coordinador):
    casos = list(
        sesion.scalars(
            select(VCasoDetalle)
            .order_by(VCasoDetalle.creado_en.desc())
            .execution_options(populate_existing=True)
        )
    )
    abiertos = [c for c in casos if c.estado != Estado.CERRADO]
    cerrados = [c for c in casos if c.estado == Estado.CERRADO]

    conteo_estados = Counter(c.estado for c in casos)
    por_estado = {estado.value: conteo_estados.get(estado, 0) for estado in Estado}

    # Desglose por técnico responsable (incluye técnicos activos sin casos).
    tecnicos = {t.id: t.nombre for t in servicios.tecnicos_activos(sesion)}
    for c in casos:
        if c.tecnico_id is not None:
            tecnicos.setdefault(c.tecnico_id, c.tecnico)
    por_tecnico = [
        esquemas.ResumenTecnico(
            tecnico_id=tid,
            tecnico=nombre,
            abiertos=sum(1 for c in abiertos if c.tecnico_id == tid),
            cerrados=sum(1 for c in cerrados if c.tecnico_id == tid),
        )
        for tid, nombre in sorted(tecnicos.items(), key=lambda par: par[1])
    ]

    return esquemas.Resumen(
        total=len(casos),
        abiertos=len(abiertos),
        cerrados=len(cerrados),
        por_estado=por_estado,
        por_tecnico=por_tecnico,
        sin_asignar=sum(1 for c in abiertos if c.tecnico_id is None),
        casos_abiertos=abiertos,
        casos_cerrados=cerrados,
    )
