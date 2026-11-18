"""Capa de servicios: reglas RN-01..RN-10 sin dependencia de FastAPI (RF-8).

Reexporta las funciones públicas para que routers y seeder sigan usando
`servicios.<función>`.
"""

from . import auth, casos, catalogos, coordinacion, excepciones  # noqa: F401
from .casos import (  # noqa: F401
    asignar_tecnico,
    cerrar,
    detalle_caso,
    evaluar,
    iniciar_atencion,
    linea_de_tiempo,
    listar_casos,
    obtener_caso_visible,
    puede_ver,
    registrar_caso,
    registrar_intervencion,
    resolver,
    tecnico_responsable_id,
)
from .auth import autenticar  # noqa: F401
from .catalogos import dependencias_activas, tecnicos_activos  # noqa: F401
from .coordinacion import resumen  # noqa: F401
