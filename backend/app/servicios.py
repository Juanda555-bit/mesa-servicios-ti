"""Reglas de negocio de los casos (RN-01 a RN-10).

Esta es la única fuente de verdad del flujo de estados y de los permisos sobre
un caso. Los routers solo traducen HTTP; el seeder usa estas mismas funciones.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import (
    Asignacion,
    Caso,
    Dependencia,
    Estado,
    HistorialEstado,
    Intervencion,
    Prioridad,
    Rol,
    Usuario,
)
from db.models import ahora_utc

from . import esquemas

# RN-01: transiciones permitidas (estado actual -> siguiente).
TRANSICIONES: dict[Estado, Estado] = {
    Estado.REGISTRADO: Estado.EN_EVALUACION,
    Estado.EN_EVALUACION: Estado.ASIGNADO,
    Estado.ASIGNADO: Estado.EN_ATENCION,
    Estado.EN_ATENCION: Estado.RESUELTO,
    Estado.RESUELTO: Estado.CERRADO,
}
ESTADOS_REASIGNABLES = {Estado.ASIGNADO, Estado.EN_ATENCION}


def _error(codigo: int, mensaje: str) -> HTTPException:
    return HTTPException(status_code=codigo, detail=mensaje)


# ---------------------------------------------------------------- Consultas

def tecnico_responsable_id(caso: Caso) -> int | None:
    activa = caso.asignacion_activa
    return activa.tecnico_id if activa else None


def puede_ver(usuario: Usuario, caso: Caso) -> bool:
    """RN-06: el solicitante ve los suyos; el técnico, los asignados; el coordinador, todos."""
    if usuario.rol == Rol.COORDINADOR:
        return True
    if usuario.rol == Rol.SOLICITANTE:
        return caso.solicitante_id == usuario.id
    return tecnico_responsable_id(caso) == usuario.id


def obtener_caso_visible(sesion: Session, usuario: Usuario, caso_id: int) -> Caso:
    caso = sesion.get(Caso, caso_id)
    if caso is None:
        raise _error(status.HTTP_404_NOT_FOUND, "El caso no existe")
    if not puede_ver(usuario, caso):
        raise _error(status.HTTP_403_FORBIDDEN, "No tiene acceso a este caso")
    return caso


def _cambiar_estado(
    sesion: Session, caso: Caso, nuevo: Estado, autor: Usuario, comentario: str | None = None
) -> None:
    """Aplica RN-01 y deja el cambio en el historial (quién y cuándo)."""
    if caso.estado == Estado.CERRADO:
        raise _error(status.HTTP_400_BAD_REQUEST, "El caso está cerrado y no admite cambios")
    if TRANSICIONES.get(caso.estado) != nuevo:
        raise _error(
            status.HTTP_400_BAD_REQUEST,
            f"Transición no permitida: {caso.estado.value} → {nuevo.value}",
        )
    anterior = caso.estado
    caso.estado = nuevo
    sesion.add(
        HistorialEstado(
            caso=caso,
            estado_anterior=anterior,
            estado_nuevo=nuevo,
            autor_id=autor.id,
            comentario=comentario,
        )
    )


def _exigir_responsable(caso: Caso, tecnico: Usuario) -> None:
    """RN-02: solo el técnico responsable actúa sobre el caso."""
    if tecnico_responsable_id(caso) != tecnico.id:
        raise _error(status.HTTP_403_FORBIDDEN, "Solo el técnico responsable puede hacer esto")


# ---------------------------------------------------------------- Acciones

def registrar_caso(sesion: Session, solicitante: Usuario, datos: esquemas.CasoNuevo) -> Caso:
    """RF-02 / CA-01: el caso nace en Registrado, sin prioridad ni responsable."""
    dependencia = sesion.get(Dependencia, datos.dependencia_id)
    if dependencia is None or not dependencia.activa:
        raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "La dependencia no existe")
    caso = Caso(**datos.model_dump(), solicitante_id=solicitante.id, estado=Estado.REGISTRADO)
    sesion.add(caso)
    sesion.add(
        HistorialEstado(
            caso=caso,
            estado_anterior=None,
            estado_nuevo=Estado.REGISTRADO,
            autor_id=solicitante.id,
            comentario="Caso reportado",
        )
    )
    sesion.flush()
    return caso


def evaluar(sesion: Session, caso: Caso, coordinador: Usuario, prioridad: Prioridad) -> None:
    """RF-04 / RN-09: el coordinador fija la prioridad y el caso pasa a En evaluación."""
    if caso.estado != Estado.REGISTRADO:
        raise _error(status.HTTP_400_BAD_REQUEST, "Solo se evalúan casos en estado Registrado")
    caso.prioridad = prioridad
    _cambiar_estado(
        sesion, caso, Estado.EN_EVALUACION, coordinador, f"Prioridad: {prioridad.value}"
    )


def asignar_tecnico(sesion: Session, caso: Caso, coordinador: Usuario, tecnico_id: int) -> None:
    """RF-05 / RN-02 / RN-10: asignación inicial o reasignación.

    - En evaluación: se asigna y el caso pasa a Asignado.
    - Asignado o En atención: se reasigna; el estado no cambia y la línea de
      tiempo muestra quién reasignó, cuándo y el técnico anterior.
    """
    tecnico = sesion.get(Usuario, tecnico_id)
    if tecnico is None or tecnico.rol != Rol.TECNICO or not tecnico.activo:
        raise _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "El usuario no es un técnico activo")

    if caso.estado == Estado.EN_EVALUACION:
        sesion.add(Asignacion(caso=caso, tecnico_id=tecnico.id, asignado_por=coordinador.id))
        _cambiar_estado(sesion, caso, Estado.ASIGNADO, coordinador)
    elif caso.estado in ESTADOS_REASIGNABLES:
        activa = caso.asignacion_activa
        if activa is not None and activa.tecnico_id == tecnico.id:
            raise _error(status.HTTP_400_BAD_REQUEST, "Ese técnico ya es el responsable del caso")
        if activa is not None:
            activa.retirado_en = ahora_utc()
            sesion.flush()  # retirar antes de insertar: solo una asignación activa
        sesion.add(Asignacion(caso=caso, tecnico_id=tecnico.id, asignado_por=coordinador.id))
    else:
        raise _error(
            status.HTTP_400_BAD_REQUEST,
            f"No se puede asignar un técnico en estado {caso.estado.value}",
        )
    sesion.flush()
    sesion.expire(caso, ["asignacion_activa"])


def iniciar_atencion(sesion: Session, caso: Caso, tecnico: Usuario) -> None:
    _exigir_responsable(caso, tecnico)
    _cambiar_estado(sesion, caso, Estado.EN_ATENCION, tecnico)


def registrar_intervencion(
    sesion: Session, caso: Caso, tecnico: Usuario, datos: esquemas.IntervencionNueva
) -> Intervencion:
    """RF-06 / RN-02 / RN-04: solo el responsable, con el caso En atención."""
    _exigir_responsable(caso, tecnico)
    if caso.estado != Estado.EN_ATENCION:
        raise _error(
            status.HTTP_400_BAD_REQUEST,
            "Solo se registran intervenciones con el caso En atención",
        )
    intervencion = Intervencion(
        caso=caso,
        tecnico_id=tecnico.id,
        descripcion=datos.descripcion,
        duracion_min=datos.duracion_min,
    )
    sesion.add(intervencion)
    sesion.flush()
    return intervencion


def resolver(sesion: Session, caso: Caso, tecnico: Usuario, solucion: str) -> None:
    """RF-08 / RN-03: exige al menos una intervención y el texto de la solución."""
    _exigir_responsable(caso, tecnico)
    if caso.estado == Estado.EN_ATENCION and not caso.intervenciones:
        raise _error(
            status.HTTP_400_BAD_REQUEST,
            "Registre al menos una intervención antes de resolver el caso",
        )
    caso.solucion = solucion
    caso.resuelto_en = ahora_utc()
    _cambiar_estado(sesion, caso, Estado.RESUELTO, tecnico)


def cerrar(sesion: Session, caso: Caso, coordinador: Usuario) -> None:
    """RF-08 / RN-04: solo el coordinador cierra; un caso cerrado no se reabre."""
    caso.cerrado_en = ahora_utc()
    _cambiar_estado(sesion, caso, Estado.CERRADO, coordinador)


def tecnicos_activos(sesion: Session) -> list[Usuario]:
    consulta = (
        select(Usuario)
        .where(Usuario.rol == Rol.TECNICO, Usuario.activo.is_(True))
        .order_by(Usuario.nombre)
    )
    return list(sesion.scalars(consulta))
