"""Esquemas de casos, intervenciones y línea de tiempo (RF-02 a RF-09)."""

from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from backend.db import Estado, Prioridad

from .comun import Salida, Texto, TextoLargo

# ---------------------------------------------------------------- Casos (entrada)

class CasoNuevo(BaseModel):
    """RF-02 / RN-08: todos los campos son obligatorios."""

    placa_equipo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    nombre_usuario: Texto
    telefono: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)
    ]
    fecha: date = Field(description="Día de la falla; no puede ser futura")
    descripcion: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=15, max_length=4000)
    ]
    dependencia_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "placa_equipo": "ABC-123",
                "nombre_usuario": "Ana Pérez",
                "telefono": "3001234567",
                "fecha": "2026-11-12",
                "descripcion": "El computador no enciende desde la mañana",
                "dependencia_id": 1,
            }
        }
    )

    @field_validator("fecha")
    @classmethod
    def _fecha_no_futura(cls, valor: date) -> date:
        if valor > date.today():
            raise ValueError("La fecha de la falla no puede ser futura")
        return valor


class Evaluacion(BaseModel):
    prioridad: Prioridad


class AsignacionTecnico(BaseModel):
    tecnico_id: int


class IntervencionNueva(BaseModel):
    descripcion: TextoLargo
    duracion_min: int = Field(gt=0, description="Minutos dedicados (mayor a 0)")


class Resolucion(BaseModel):
    solucion: TextoLargo


# ---------------------------------------------------------------- Casos (salida)

class CasoSalida(Salida):
    """Fila de la vista v_caso_detalle (CA-03, CA-05)."""

    id: int
    placa_equipo: str
    nombre_usuario: str
    telefono: str
    fecha: date
    descripcion: str
    estado: Estado
    prioridad: Prioridad | None
    solucion: str | None
    creado_en: datetime
    resuelto_en: datetime | None
    cerrado_en: datetime | None
    dependencia: str
    solicitante_id: int
    solicitante: str
    tecnico_id: int | None
    tecnico: str | None


class IntervencionSalida(Salida):
    id: int
    caso_id: int
    tecnico_id: int
    descripcion: str
    duracion_min: int
    creado_en: datetime


class EventoLineaTiempo(Salida):
    """Fila de la vista v_linea_tiempo (RF-09, CA-04)."""

    momento: datetime
    tipo: str
    autor_id: int
    autor: str
    detalle: str
