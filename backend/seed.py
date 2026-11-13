"""Datos iniciales de prueba (S-06). Todos los datos son ficticios.

Ejecutar desde la carpeta backend:
    python seed.py

Crea la base si no existe y, si aún no hay usuarios, carga:
- un coordinador, dos técnicos y dos solicitantes (contraseña: Mesa2026*),
- el catálogo de dependencias,
- casos de ejemplo en distintos estados, creados con las mismas reglas de la API.
"""

from datetime import date, timedelta

from sqlalchemy import func, select

from app import esquemas, servicios
from app.seguridad import hash_password
from db import Dependencia, Prioridad, Rol, SessionLocal, Usuario
from db.database import engine, inicializar_base

PASSWORD_DEMO = "Mesa2026*"

USUARIOS = [
    ("Carla Coordinadora", "coordinador@mesa.edu.co", Rol.COORDINADOR),
    ("Tomás Técnico", "tecnico1@mesa.edu.co", Rol.TECNICO),
    ("Teresa Técnica", "tecnico2@mesa.edu.co", Rol.TECNICO),
    ("Sara Solicitante", "solicitante1@mesa.edu.co", Rol.SOLICITANTE),
    ("Samuel Solicitante", "solicitante2@mesa.edu.co", Rol.SOLICITANTE),
]

DEPENDENCIAS = [
    "Biblioteca",
    "Coordinación académica",
    "Laboratorio de sistemas",
    "Rectoría",
    "Secretaría",
    "Tesorería",
]


def _caso(placa: str, nombre: str, dias_atras: int, descripcion: str, dep: int):
    return esquemas.CasoNuevo(
        placa_equipo=placa,
        nombre_usuario=nombre,
        telefono="3001234567",
        fecha=date.today() - timedelta(days=dias_atras),
        descripcion=descripcion,
        dependencia_id=dep,
    )


def cargar() -> None:
    inicializar_base(engine)
    with SessionLocal() as s:
        if s.scalar(select(func.count()).select_from(Usuario)):
            print("La base ya tiene usuarios; no se cargó nada.")
            return

        hash_demo = hash_password(PASSWORD_DEMO)
        u = {}
        for nombre, correo, rol in USUARIOS:
            u[correo.split("@")[0]] = usuario = Usuario(
                nombre=nombre, correo=correo, password_hash=hash_demo, rol=rol
            )
            s.add(usuario)
        deps = [Dependencia(nombre=n) for n in DEPENDENCIAS]
        s.add_all(deps)
        s.flush()
        coord, t1, t2 = u["coordinador"], u["tecnico1"], u["tecnico2"]
        sol1, sol2 = u["solicitante1"], u["solicitante2"]

        # 1. Registrado (sin evaluar)
        servicios.registrar_caso(
            s, sol1, _caso("BIB-014", "Luis Gómez", 0, "La impresora de préstamo no imprime", deps[0].id)
        )

        # 2. En evaluación
        c = servicios.registrar_caso(
            s, sol2, _caso("SEC-031", "Marta Ruiz", 1, "Solicito instalar el programa de nómina", deps[4].id)
        )
        servicios.evaluar(s, c, coord, Prioridad.MEDIA)

        # 3. Asignado
        c = servicios.registrar_caso(
            s, sol1, _caso("LAB-102", "Pedro Díaz", 2, "Tres equipos del laboratorio sin internet", deps[2].id)
        )
        servicios.evaluar(s, c, coord, Prioridad.ALTA)
        servicios.asignar_tecnico(s, c, coord, t1.id)

        # 4. En atención, con reasignación e intervención
        c = servicios.registrar_caso(
            s, sol2, _caso("REC-007", "Elena Mora", 3, "El correo institucional no sincroniza", deps[3].id)
        )
        servicios.evaluar(s, c, coord, Prioridad.CRITICA)
        servicios.asignar_tecnico(s, c, coord, t1.id)
        servicios.asignar_tecnico(s, c, coord, t2.id)
        servicios.iniciar_atencion(s, c, t2)
        servicios.registrar_intervencion(
            s, c, t2, esquemas.IntervencionNueva(descripcion="Se revisa la configuración de la cuenta", duracion_min=30)
        )

        # 5. Cerrado
        c = servicios.registrar_caso(
            s, sol1, _caso("TES-020", "Andrés Rojas", 5, "El monitor parpadea y se apaga solo", deps[5].id)
        )
        servicios.evaluar(s, c, coord, Prioridad.BAJA)
        servicios.asignar_tecnico(s, c, coord, t2.id)
        servicios.iniciar_atencion(s, c, t2)
        servicios.registrar_intervencion(
            s, c, t2, esquemas.IntervencionNueva(descripcion="Se prueba con otro cable de video", duracion_min=15)
        )
        servicios.resolver(s, c, t2, "Se reemplazó el cable de video dañado")
        servicios.cerrar(s, c, coord)

        s.commit()

    print("Datos de prueba cargados. Usuarios (contraseña " + PASSWORD_DEMO + "):")
    for _nombre, correo, rol in USUARIOS:
        print(f"  {rol.value:<12} {correo}")


if __name__ == "__main__":
    cargar()
