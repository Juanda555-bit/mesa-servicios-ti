"""Modelos ORM que describen el esquema de `schema.sql`.

El esquema SQL es la fuente de verdad de la estructura. Estos modelos deben
coincidir con él; `tests/test_modelos.py` lo verifica.
Las fechas y horas se guardan en UTC como texto ISO-8601 y aquí se leen como
`datetime` con zona horaria UTC.
"""

import enum
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    types,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import FetchedValue


class Base(DeclarativeBase):
    pass


# ------------------------------------------------------------------
# Enumeraciones (los valores son exactamente los del CHECK de la base)
# ------------------------------------------------------------------

class Rol(str, enum.Enum):
    SOLICITANTE = "solicitante"
    TECNICO = "tecnico"
    COORDINADOR = "coordinador"


class Estado(str, enum.Enum):
    REGISTRADO = "Registrado"
    EN_EVALUACION = "En evaluación"
    ASIGNADO = "Asignado"
    EN_ATENCION = "En atención"
    RESUELTO = "Resuelto"
    CERRADO = "Cerrado"


class Prioridad(str, enum.Enum):
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"
    CRITICA = "Crítica"


def _enum(clase: type[enum.Enum]) -> Enum:
    """Guarda el *valor* del enum (no el nombre), sin crear restricciones propias."""
    return Enum(
        clase,
        values_callable=lambda e: [m.value for m in e],
        native_enum=False,
        create_constraint=False,
        validate_strings=True,
        length=20,
    )


# ------------------------------------------------------------------
# Tipo para fechas y horas UTC guardadas como texto ISO-8601
# ------------------------------------------------------------------

class FechaHoraUTC(types.TypeDecorator):
    """datetime con zona UTC <-> 'YYYY-MM-DDTHH:MM:SS.sssZ'."""

    impl = String
    cache_ok = True

    def process_bind_param(self, valor: datetime | None, dialecto) -> str | None:
        if valor is None:
            return None
        if valor.tzinfo is None:
            raise ValueError("La fecha y hora debe tener zona horaria (use UTC).")
        utc = valor.astimezone(timezone.utc)
        return utc.strftime("%Y-%m-%dT%H:%M:%S.") + f"{utc.microsecond // 1000:03d}Z"

    def process_result_value(self, valor: str | None, dialecto) -> datetime | None:
        if valor is None:
            return None
        return datetime.strptime(valor, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def ahora_utc() -> datetime:
    return datetime.now(timezone.utc)


# ------------------------------------------------------------------
# Tablas
# ------------------------------------------------------------------

class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String)
    correo: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    rol: Mapped[Rol] = mapped_column(_enum(Rol))
    activo: Mapped[bool] = mapped_column(Boolean, server_default=FetchedValue())
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC, server_default=FetchedValue())


class Dependencia(Base):
    __tablename__ = "dependencia"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String, unique=True)
    activa: Mapped[bool] = mapped_column(Boolean, server_default=FetchedValue())


class Caso(Base):
    __tablename__ = "caso"

    id: Mapped[int] = mapped_column(primary_key=True)
    placa_equipo: Mapped[str] = mapped_column(String)
    nombre_usuario: Mapped[str] = mapped_column(String)
    telefono: Mapped[str] = mapped_column(String)
    fecha: Mapped[date] = mapped_column(Date)
    descripcion: Mapped[str] = mapped_column(Text)
    dependencia_id: Mapped[int] = mapped_column(ForeignKey("dependencia.id"))
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    estado: Mapped[Estado] = mapped_column(_enum(Estado), server_default=FetchedValue())
    prioridad: Mapped[Prioridad | None] = mapped_column(_enum(Prioridad), nullable=True)
    solucion: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC, server_default=FetchedValue())
    resuelto_en: Mapped[datetime | None] = mapped_column(FechaHoraUTC, nullable=True)
    cerrado_en: Mapped[datetime | None] = mapped_column(FechaHoraUTC, nullable=True)

    dependencia: Mapped[Dependencia] = relationship()
    solicitante: Mapped[Usuario] = relationship()
    asignaciones: Mapped[list["Asignacion"]] = relationship(
        back_populates="caso", order_by="Asignacion.id"
    )
    intervenciones: Mapped[list["Intervencion"]] = relationship(
        back_populates="caso", order_by="Intervencion.id"
    )
    historial: Mapped[list["HistorialEstado"]] = relationship(
        back_populates="caso", order_by="HistorialEstado.id"
    )
    # Responsable actual: la asignación sin fecha de retiro (como máximo una).
    asignacion_activa: Mapped["Asignacion | None"] = relationship(
        primaryjoin="and_(Caso.id == Asignacion.caso_id, Asignacion.retirado_en.is_(None))",
        uselist=False,
        viewonly=True,
    )


class Asignacion(Base):
    __tablename__ = "asignacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    caso_id: Mapped[int] = mapped_column(ForeignKey("caso.id"))
    tecnico_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    asignado_por: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    asignado_en: Mapped[datetime] = mapped_column(FechaHoraUTC, server_default=FetchedValue())
    retirado_en: Mapped[datetime | None] = mapped_column(FechaHoraUTC, nullable=True)

    caso: Mapped[Caso] = relationship(back_populates="asignaciones")
    tecnico: Mapped[Usuario] = relationship(foreign_keys=[tecnico_id])
    coordinador: Mapped[Usuario] = relationship(foreign_keys=[asignado_por])


class Intervencion(Base):
    __tablename__ = "intervencion"

    id: Mapped[int] = mapped_column(primary_key=True)
    caso_id: Mapped[int] = mapped_column(ForeignKey("caso.id"))
    tecnico_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    descripcion: Mapped[str] = mapped_column(Text)
    duracion_min: Mapped[int] = mapped_column(Integer)
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC, server_default=FetchedValue())

    caso: Mapped[Caso] = relationship(back_populates="intervenciones")
    tecnico: Mapped[Usuario] = relationship()


class HistorialEstado(Base):
    __tablename__ = "historial_estado"

    id: Mapped[int] = mapped_column(primary_key=True)
    caso_id: Mapped[int] = mapped_column(ForeignKey("caso.id"))
    estado_anterior: Mapped[Estado | None] = mapped_column(_enum(Estado), nullable=True)
    estado_nuevo: Mapped[Estado] = mapped_column(_enum(Estado))
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(FechaHoraUTC, server_default=FetchedValue())

    caso: Mapped[Caso] = relationship(back_populates="historial")
    autor: Mapped[Usuario] = relationship()


# ------------------------------------------------------------------
# Vistas (solo lectura). No se crean con create_all(): las crea schema.sql.
# ------------------------------------------------------------------

_VISTA = {"is_view": True}


class VCasoDetalle(Base):
    __table__ = Table(
        "v_caso_detalle",
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("placa_equipo", String),
        Column("nombre_usuario", String),
        Column("telefono", String),
        Column("fecha", Date),
        Column("descripcion", Text),
        Column("estado", _enum(Estado)),
        Column("prioridad", _enum(Prioridad)),
        Column("solucion", Text),
        Column("creado_en", FechaHoraUTC),
        Column("resuelto_en", FechaHoraUTC),
        Column("cerrado_en", FechaHoraUTC),
        Column("dependencia", String),
        Column("solicitante_id", Integer),
        Column("solicitante", String),
        Column("tecnico_id", Integer),
        Column("tecnico", String),
        info=_VISTA,
    )


class VLineaTiempo(Base):
    __table__ = Table(
        "v_linea_tiempo",
        Base.metadata,
        Column("caso_id", Integer, primary_key=True),
        Column("momento", FechaHoraUTC),
        Column("orden", Integer, primary_key=True),
        Column("ref_id", Integer, primary_key=True),
        Column("tipo", String),
        Column("autor_id", Integer),
        Column("autor", String),
        Column("detalle", Text),
        info=_VISTA,
    )
