"""RF-10 / CA-06: tablero consolidado del coordinador."""

from fastapi import APIRouter

from .. import esquemas, servicios
from ..deps import Coordinador, SesionBD

router = APIRouter(prefix="/coordinacion", tags=["Coordinación"])


@router.get("/resumen", response_model=esquemas.Resumen)
def resumen(sesion: SesionBD, _coordinador: Coordinador):
    return servicios.resumen(sesion)
