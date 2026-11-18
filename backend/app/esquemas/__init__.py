"""Esquemas Pydantic de entrada y salida, agrupados por tema.

Reexporta las clases para que `esquemas.<Clase>` siga funcionando (seeder, routers).
"""

from .auth import Token, UsuarioSalida  # noqa: F401
from .casos import (  # noqa: F401
    AsignacionTecnico,
    CasoNuevo,
    CasoSalida,
    Evaluacion,
    EventoLineaTiempo,
    IntervencionNueva,
    IntervencionSalida,
    Resolucion,
)
from .catalogos import DependenciaSalida, TecnicoSalida  # noqa: F401
from .comun import Salida, Texto, TextoLargo  # noqa: F401
from .coordinacion import CasoResumido, Resumen, ResumenTecnico  # noqa: F401
