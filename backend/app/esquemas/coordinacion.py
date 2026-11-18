"""Esquemas del tablero del coordinador (RF-10)."""

from datetime import datetime

from pydantic import BaseModel

from backend.db import Estado, Prioridad

from .comun import Salida


class CasoResumido(Salida):
    id: int
    placa_equipo: str
    estado: Estado
    prioridad: Prioridad | None
    tecnico: str | None
    creado_en: datetime
    cerrado_en: datetime | None


class ResumenTecnico(BaseModel):
    tecnico_id: int
    tecnico: str
    abiertos: int
    cerrados: int


class Resumen(BaseModel):
    """RF-10 / CA-06: casos abiertos y cerrados con sus fechas y desglose por técnico."""

    total: int
    abiertos: int
    cerrados: int
    por_estado: dict[str, int]
    por_tecnico: list[ResumenTecnico]
    sin_asignar: int
    casos_abiertos: list[CasoResumido]
    casos_cerrados: list[CasoResumido]
