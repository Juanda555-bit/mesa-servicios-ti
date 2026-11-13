"""Esquemas Pydantic de entrada y salida (RNF-01: validación en el servidor)."""

from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from db import Estado, Prioridad, Rol

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TextoLargo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------- Autenticación

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: Rol
    nombre: str


class UsuarioSalida(Salida):
    id: int
    nombre: str
    correo: str
    rol: Rol


# ---------------------------------------------------------------- Catálogos

class DependenciaSalida(Salida):
    id: int
    nombre: str


class TecnicoSalida(Salida):
    id: int
    nombre: str
    correo: str


# ---------------------------------------------------------------- Casos (entrada)

class CasoNuevo(BaseModel):
    """RF-02 / RN-08: todos los campos son obligatorios."""

    placa_equipo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=50)]
    nombre_usuario: Texto
    telefono: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=r"^[0-9+()\- ]{7,20}$")
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
    duracion_min: int = Field(gt=0, le=24 * 60, description="Minutos dedicados (mayor a 0)")


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


# ---------------------------------------------------------------- Coordinación

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
