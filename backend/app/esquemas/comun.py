"""Tipos y bases comunes de los esquemas (RNF-01: validación en el servidor)."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
TextoLargo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class Salida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
