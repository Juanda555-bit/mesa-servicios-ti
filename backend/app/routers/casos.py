"""Casos: registro, consulta, flujo de estados e intervenciones (RF-02 a RF-09)."""

from fastapi import APIRouter, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import Estado, Rol, Usuario, VCasoDetalle, VLineaTiempo

from .. import esquemas, servicios
from ..deps import Coordinador, SesionBD, Solicitante, Tecnico, UsuarioActual

router = APIRouter(prefix="/casos", tags=["Casos"])


def _detalle(sesion: Session, caso_id: int) -> VCasoDetalle:
    consulta = (
        select(VCasoDetalle)
        .where(VCasoDetalle.id == caso_id)
        .execution_options(populate_existing=True)
    )
    return sesion.scalars(consulta).one()


def _filtrar_por_rol(consulta, usuario: Usuario):
    """RN-06: cada rol ve solo los casos que le corresponden."""
    if usuario.rol == Rol.SOLICITANTE:
        return consulta.where(VCasoDetalle.solicitante_id == usuario.id)
    if usuario.rol == Rol.TECNICO:
        return consulta.where(VCasoDetalle.tecnico_id == usuario.id)
    return consulta


@router.post("", response_model=esquemas.CasoSalida, status_code=status.HTTP_201_CREATED)
def registrar_caso(datos: esquemas.CasoNuevo, sesion: SesionBD, solicitante: Solicitante):
    """RF-02 / CA-01: el solicitante reporta un incidente o solicitud."""
    caso = servicios.registrar_caso(sesion, solicitante, datos)
    sesion.commit()
    return _detalle(sesion, caso.id)


@router.get("", response_model=list[esquemas.CasoSalida])
def listar_casos(sesion: SesionBD, usuario: UsuarioActual, estado: Estado | None = None):
    """RF-03 / CA-03: lista según el rol, con filtro opcional por estado."""
    consulta = _filtrar_por_rol(select(VCasoDetalle), usuario)
    if estado is not None:
        consulta = consulta.where(VCasoDetalle.estado == estado)
    consulta = consulta.order_by(VCasoDetalle.creado_en.desc(), VCasoDetalle.id.desc())
    return list(sesion.scalars(consulta.execution_options(populate_existing=True)))


@router.get("/{caso_id}", response_model=esquemas.CasoSalida)
def ver_caso(caso_id: int, sesion: SesionBD, usuario: UsuarioActual):
    """RF-03 / CA-03 / CA-05: detalle con estado, responsable y solución."""
    servicios.obtener_caso_visible(sesion, usuario, caso_id)
    return _detalle(sesion, caso_id)


@router.patch("/{caso_id}/evaluacion", response_model=esquemas.CasoSalida)
def evaluar_caso(
    caso_id: int, datos: esquemas.Evaluacion, sesion: SesionBD, coordinador: Coordinador
):
    """RF-04 / CA-02: fija la prioridad y pasa a En evaluación."""
    caso = servicios.obtener_caso_visible(sesion, coordinador, caso_id)
    servicios.evaluar(sesion, caso, coordinador, datos.prioridad)
    sesion.commit()
    return _detalle(sesion, caso_id)


@router.put("/{caso_id}/tecnico", response_model=esquemas.CasoSalida)
def asignar_tecnico(
    caso_id: int, datos: esquemas.AsignacionTecnico, sesion: SesionBD, coordinador: Coordinador
):
    """RF-05 / CA-02: asigna (En evaluación → Asignado) o reasigna sin cambiar el estado."""
    caso = servicios.obtener_caso_visible(sesion, coordinador, caso_id)
    servicios.asignar_tecnico(sesion, caso, coordinador, datos.tecnico_id)
    sesion.commit()
    return _detalle(sesion, caso_id)


@router.post("/{caso_id}/iniciar-atencion", response_model=esquemas.CasoSalida)
def iniciar_atencion(caso_id: int, sesion: SesionBD, tecnico: Tecnico):
    """RF-07 / CA-02: el técnico responsable pasa el caso a En atención."""
    caso = servicios.obtener_caso_visible(sesion, tecnico, caso_id)
    servicios.iniciar_atencion(sesion, caso, tecnico)
    sesion.commit()
    return _detalle(sesion, caso_id)


@router.post(
    "/{caso_id}/intervenciones",
    response_model=esquemas.IntervencionSalida,
    status_code=status.HTTP_201_CREATED,
)
def registrar_intervencion(
    caso_id: int, datos: esquemas.IntervencionNueva, sesion: SesionBD, tecnico: Tecnico
):
    """RF-06 / CA-04: el técnico responsable registra una intervención."""
    caso = servicios.obtener_caso_visible(sesion, tecnico, caso_id)
    intervencion = servicios.registrar_intervencion(sesion, caso, tecnico, datos)
    sesion.commit()
    sesion.refresh(intervencion)
    return intervencion


@router.post("/{caso_id}/resolver", response_model=esquemas.CasoSalida)
def resolver_caso(caso_id: int, datos: esquemas.Resolucion, sesion: SesionBD, tecnico: Tecnico):
    """RF-08 / CA-05: registra la solución y pasa a Resuelto."""
    caso = servicios.obtener_caso_visible(sesion, tecnico, caso_id)
    servicios.resolver(sesion, caso, tecnico, datos.solucion)
    sesion.commit()
    return _detalle(sesion, caso_id)


@router.post("/{caso_id}/cerrar", response_model=esquemas.CasoSalida)
def cerrar_caso(caso_id: int, sesion: SesionBD, coordinador: Coordinador):
    """RF-08 / CA-05: solo el coordinador cierra; no se puede reabrir."""
    caso = servicios.obtener_caso_visible(sesion, coordinador, caso_id)
    servicios.cerrar(sesion, caso, coordinador)
    sesion.commit()
    return _detalle(sesion, caso_id)


@router.get("/{caso_id}/historial", response_model=list[esquemas.EventoLineaTiempo])
def linea_de_tiempo(caso_id: int, sesion: SesionBD, usuario: UsuarioActual):
    """RF-09 / CA-04: cambios de estado, asignaciones e intervenciones en orden."""
    servicios.obtener_caso_visible(sesion, usuario, caso_id)
    consulta = (
        select(VLineaTiempo)
        .where(VLineaTiempo.caso_id == caso_id)
        .order_by(VLineaTiempo.momento, VLineaTiempo.orden, VLineaTiempo.ref_id)
    )
    return list(sesion.scalars(consulta))
