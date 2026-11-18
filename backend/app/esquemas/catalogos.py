"""Esquemas de catálogos (RF-02, RF-05)."""

from .comun import Salida


class DependenciaSalida(Salida):
    id: int
    nombre: str


class TecnicoSalida(Salida):
    id: int
    nombre: str
    correo: str
