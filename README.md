# Mesa de Servicios TI

Proyecto Final 02 (PF-02) · Aplicaciones y Servicios Web · Tecnología en Desarrollo de Software.
Aplicación web para registrar, atender, dar seguimiento y cerrar casos de soporte tecnológico de una institución educativa.

> **Estado del proyecto:** Actividad 2 (requisitos y entrevista) completada y aprobada por el docente. Las demás secciones se completarán conforme avance el desarrollo.

## 1. Información general

| Campo | Detalle |
|---|---|
| Proyecto | Mesa de servicios de soporte tecnológico (PF-02) |
| Problema | Los reportes de soporte llegan por correo, llamadas y mensajes directos, sin registro unificado, sin responsable claro y sin visibilidad del avance. |
| Asignatura | Aplicaciones y Servicios Web |
| Docente (cliente) | Juan Carlos Morales Guerra |
| Integrantes | Juan David Arias Ospina · Simón Herrera |
| Contribución de cada integrante | Por completar (se documentará con commits y pull requests) |
| Fecha de entrega | Por completar |
| Repositorio | https://github.com/Juanda555-bit/mesa-servicios-ti |

## 2. Descripción del sistema

**Actores**
- **Solicitante** (docente o administrativo): reporta casos y consulta el estado y resultado de los suyos.
- **Técnico:** atiende los casos que le asigna la coordinación, registra intervenciones y la solución.
- **Coordinador:** evalúa y prioriza, asigna y reasigna técnicos, cierra los casos y consulta el tablero consolidado.

**Alcance:** reporte, evaluación, atención, seguimiento y cierre de casos, con historial de intervenciones y resultado visible para el solicitante (condiciones CA-01 a CA-06 de la guía). Todo ocurre dentro de la aplicación web; no incluye correo, mensajería externa, adjuntos de archivos ni SLA.

**Restricciones del alcance aprobado**
- Incidentes y solicitudes comparten el mismo flujo de estados.
- Estados: `Registrado → En evaluación → Asignado → En atención → Resuelto → Cerrado`. Solo el coordinador cierra y un caso cerrado no se reabre. No existe cancelación.
- Asignación manual por el coordinador; la reasignación está permitida y queda en el historial.
- Reportes e intervenciones solo en texto. Todo lo registrado es visible para el solicitante del caso.

Requisitos completos: [`docs/requisitos.md`](docs/requisitos.md)

## 3. Requisitos y alcance

**Método de obtención de la información:** lectura de la guía PF-02 y entrevista con el docente en el rol de representante de la organización, a partir de una batería de 13 preguntas con propuesta del equipo.

**Evidencia de la entrevista y decisiones confirmadas**
- Registro de la entrevista con las respuestas del docente, las decisiones confirmadas y los cambios a los requisitos: [`docs/entrevista.md`](docs/entrevista.md)
- Especificación y guía de la entrevista (actores, permisos, RF, RN, RNF y supuestos): [`docs/especificacion_y_entrevista_docente.md`](docs/especificacion_y_entrevista_docente.md)
- Aprobación: el docente revisó la delimitación y respondió que la veía bien y que siguieran adelante. La fecha exacta de aprobación está pendiente de registrar.

**Requisitos priorizados, historias de usuario y criterios de aceptación**
- 10 requisitos funcionales (RF-01 a RF-10), 10 reglas de negocio (RN-01 a RN-10), 7 requisitos no funcionales (RNF-01 a RNF-07) y 7 supuestos.
- 10 historias de usuario (US-01 a US-10), una por requisito funcional, con criterios de aceptación en formato *Dado / Cuando / Entonces* y una tabla que cruza las reglas de negocio con las historias que las verifican. Están en [`docs/requisitos.md`](docs/requisitos.md#6-historias-de-usuario-y-criterios-de-aceptación).

## 4. Arquitectura, diseño de API y modelo de datos

- **Backend:** Python + FastAPI, con validación Pydantic y documentación automática en `/docs`.
- **Base de datos:** SQLite con SQLAlchemy; esquema, índices, triggers y vistas en `backend/db/schema.sql`.
- **Autenticación:** token JWT; contraseñas con hash PBKDF2-SHA256 y sal por usuario.
- **Frontend:** React + Vite (pendiente).

Arquitectura, modelo entidad-relación, máquina de estados, permisos por rol y especificación de la API: [`docs/diseno.md`](docs/diseno.md).

Estructura del backend:

```
backend/
├── app/
│   ├── main.py          # aplicación, CORS y manejo de errores
│   ├── config.py        # variables del .env
│   ├── seguridad.py     # hash de contraseñas y tokens
│   ├── deps.py          # usuario autenticado y control por rol
│   ├── esquemas.py      # validación de entrada y salida
│   ├── servicios.py     # reglas de negocio y flujo de estados
│   └── routers/         # auth, catálogos, casos, coordinación
├── db/                  # esquema SQL, conexión y modelos ORM
├── tests/               # pruebas del esquema, modelos y API
└── seed.py              # datos de prueba
```

## 5. Configuración del entorno

Requisitos: Python 3.11 o superior y Git.

```bash
git clone https://github.com/Juanda555-bit/mesa-servicios-ti.git
cd mesa-servicios-ti
cp .env.example .env            # en Windows: copy .env.example .env
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python seed.py                  # crea la base y carga datos de prueba
uvicorn app.main:app --reload
```

- API: http://localhost:8000 · Documentación interactiva: http://localhost:8000/docs
- En `/docs`, botón **Authorize**: correo en *username* y la contraseña.

Usuarios de prueba (contraseña `Mesa2026*`, datos ficticios):

| Rol | Correo |
|---|---|
| Coordinador | coordinador@mesa.edu.co |
| Técnico | tecnico1@mesa.edu.co, tecnico2@mesa.edu.co |
| Solicitante | solicitante1@mesa.edu.co, solicitante2@mesa.edu.co |

Para empezar de cero, borrar `backend/mesa_ti.db` y volver a ejecutar `python seed.py`.

## 6. Servicios web implementados

| Método | Ruta | Descripción | Requisito relacionado |
|---|---|---|---|
| GET | `/salud` | Estado del servicio | – |
| POST | `/auth/login` | Inicia sesión y devuelve el token con el rol | RF-01 |
| GET | `/auth/me` | Usuario autenticado | RF-01 |
| GET | `/dependencias` | Catálogo de dependencias | RF-02 |
| POST | `/casos` | Registrar caso (solicitante) | RF-02 |
| GET | `/casos` | Listar casos según el rol (filtro `estado`) | RF-03 |
| GET | `/casos/{id}` | Detalle con estado, responsable y solución | RF-03, RF-08 |
| PATCH | `/casos/{id}/evaluacion` | Fijar prioridad (coordinador) | RF-04 |
| PUT | `/casos/{id}/tecnico` | Asignar o reasignar técnico (coordinador) | RF-05 |
| POST | `/casos/{id}/iniciar-atencion` | Iniciar atención (técnico responsable) | RF-07 |
| POST | `/casos/{id}/intervenciones` | Registrar intervención (técnico responsable) | RF-06 |
| POST | `/casos/{id}/resolver` | Registrar solución (técnico responsable) | RF-08 |
| POST | `/casos/{id}/cerrar` | Cerrar caso (coordinador) | RF-08 |
| GET | `/casos/{id}/historial` | Línea de tiempo del caso | RF-09 |
| GET | `/tecnicos` | Técnicos activos (coordinador) | RF-05 |
| GET | `/coordinacion/resumen` | Tablero consolidado (coordinador) | RF-10 |

Errores: `400` transición inválida, `401` sin sesión, `403` rol o caso no autorizado, `404` caso inexistente, `409` regla de integridad, `422` datos inválidos.

## 7. Pruebas de API e integración y evidencias de funcionamiento

Pruebas automáticas (desde `backend`, con el entorno activado):

```bash
python -m pytest tests -v
```

- `tests/test_modelos.py`: los modelos ORM coinciden con el esquema y la base protege sus reglas.
- `tests/test_api.py`: las historias US-01 a US-10 sobre la API: login y permisos, validación del reporte, privacidad de casos, flujo completo de estados, reasignación, reglas RN-02 a RN-04 y tablero.

Capturas y evidencias de funcionamiento: carpeta `evidencias/` (por completar).

## 8. Control de versiones

- El trabajo se integra mediante ramas y *pull requests* hacia `main`, con commits descriptivos (`docs:`, `feat:`, `fix:`, `chore:`, `test:`).
- Cada pull request documenta propósito, cambios, pruebas efectuadas y requisitos asociados.
- Resumen verificable de aportes por integrante: por completar.

## 9. Conclusiones y limitaciones

Por completar.
