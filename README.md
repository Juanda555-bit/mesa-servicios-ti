# Mesa de Servicios TI

Proyecto Final 02 (PF-02) · Aplicaciones y Servicios Web · Tecnología en Desarrollo de Software.
Aplicación web para registrar, atender, dar seguimiento y cerrar casos de soporte tecnológico de una institución educativa.

> **Estado del proyecto:** requisitos aprobados por el docente (12/11/2026); diseño en borrador para revisión del equipo (Actividad 3, `docs/diseno.md`); capa de base de datos implementada y probada (`backend/db/` con `schema.sql`, `models.py` y `database.py`; pruebas `backend/db/probar_esquema.py` y `backend/tests/test_modelos.py`). API REST implementada y probada (16 endpoints con autenticación por rol, seeder de datos ficticios y pruebas de API). Aún no hay interfaz.

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
- Aprobación: el docente revisó la delimitación y respondió que la veía bien y que siguieran adelante. La entrevista y la aprobación son del 12/11/2026.

**Requisitos priorizados, historias de usuario y criterios de aceptación**
- 10 requisitos funcionales (RF-01 a RF-10), 10 reglas de negocio (RN-01 a RN-10), 7 requisitos no funcionales (RNF-01 a RNF-07) y 7 supuestos.
- 10 historias de usuario (US-01 a US-10), una por requisito funcional, con criterios de aceptación en formato *Dado / Cuando / Entonces* y una tabla que cruza las reglas de negocio con las historias que las verifican. Están en [`docs/requisitos.md`](docs/requisitos.md#6-historias-de-usuario-y-criterios-de-aceptación).

## 4. Arquitectura, diseño de API y modelo de datos

Borrador de la Actividad 3, en revisión del equipo: [`docs/diseno.md`](docs/diseno.md).

## 5. Configuración del entorno

Requisitos de software: Python 3.12 y Git. El frontend (React + Vite) se documentará cuando exista (spec 003).

Todos los comandos se ejecutan desde la raíz del repositorio:

```bash
git clone https://github.com/Juanda555-bit/mesa-servicios-ti.git
cd mesa-servicios-ti
python -m venv .venv
.venv\Scripts\activate          # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r backend/requirements.txt
python -m backend.seed          # crea la base y carga datos de prueba
python -m uvicorn backend.app.main:app --reload
```

**Variables de entorno.** Copiar `.env.example` a `.env` (`cp .env.example .env`; en Windows `copy .env.example .env`) y ajustar. El archivo `.env` no se versiona y no debe contener secretos compartidos. Si no existe, la API arranca con una clave temporal y lo avisa.

| Variable | Uso |
|---|---|
| `SECRET_KEY` | Clave para firmar los tokens; generar una propia. |
| `TOKEN_MINUTOS` | Minutos de validez del token (480 = 8 horas). |
| `CORS_ORIGINS` | Orígenes permitidos para el frontend, separados por coma. |
| `DATABASE_URL` | Opcional (comentada en `.env.example`): URL SQLite; si se omite se usa `backend/mesa_ti.db`. |

**Base de datos y datos de prueba.** `python -m backend.seed` crea la base (si no existe) y carga datos ficticios. Para empezar de cero, borrar `backend/mesa_ti.db` y volver a ejecutarlo.

- API: http://localhost:8000 · Documentación interactiva: http://localhost:8000/docs
- En `/docs`, botón **Authorize**: correo en *username* y la contraseña.

Usuarios de prueba del seeder (contraseña de demostración `Mesa2026*`, datos ficticios):

| Rol | Correo |
|---|---|
| Coordinador | coordinador@mesa.edu.co |
| Técnico | tecnico1@mesa.edu.co, tecnico2@mesa.edu.co |
| Solicitante | solicitante1@mesa.edu.co, solicitante2@mesa.edu.co |

## 6. Servicios web implementados

Documentación interactiva (Swagger): http://localhost:8000/docs

| Método | Ruta | Descripción | Requisito relacionado |
|---|---|---|---|
| GET | `/salud` | Estado del servicio | – |
| POST | `/auth/login` | Devuelve token con el rol | RF-01 |
| GET | `/auth/me` | Usuario autenticado | RF-01 |
| GET | `/dependencias` | Catálogo para el formulario | RF-02 |
| POST | `/casos` | Registrar caso | RF-02, CA-01 |
| GET | `/casos` | Listar casos según rol (filtro `estado`) | RF-03, CA-03 |
| GET | `/casos/{id}` | Detalle con responsable y estado | RF-03, CA-03, CA-05 |
| PATCH | `/casos/{id}/evaluacion` | Fijar prioridad; pasa a `En evaluación` | RF-04, CA-02 |
| PUT | `/casos/{id}/tecnico` | Asignar o reasignar técnico | RF-05, CA-02 |
| POST | `/casos/{id}/iniciar-atencion` | Pasa a `En atención` | RF-07, CA-02 |
| POST | `/casos/{id}/intervenciones` | Registrar intervención | RF-06, CA-04 |
| POST | `/casos/{id}/resolver` | Registrar solución; pasa a `Resuelto` | RF-08, CA-05 |
| POST | `/casos/{id}/cerrar` | Cerrar caso | RF-08, CA-05 |
| GET | `/casos/{id}/historial` | Línea de tiempo del caso | RF-09, CA-04 |
| GET | `/tecnicos` | Técnicos activos | RF-05 |
| GET | `/coordinacion/resumen` | Casos abiertos, cerrados, fechas y desglose por técnico | RF-10, CA-06 |

Las rutas, salvo `/salud` y `/auth/login`, exigen la cabecera `Authorization: Bearer <token>`. Los permisos por rol se comprueban en el backend.

**Ejemplo: iniciar sesión.** `POST /auth/login` recibe un formulario (`username` es el correo):

```bash
curl -X POST http://localhost:8000/auth/login -d "username=solicitante1@mesa.edu.co&password=Mesa2026*"
```

Respuesta `200`:

```json
{"access_token": "<token>", "token_type": "bearer", "rol": "solicitante", "nombre": "Sara Solicitante"}
```

Con correo o contraseña incorrectos responde `401` con `{"detail": "Correo o contraseña incorrectos"}`.

**Ejemplo: registrar un caso** (rol solicitante):

```json
POST /casos
Authorization: Bearer <token>
{
  "placa_equipo": "ABC-123",
  "nombre_usuario": "Ana Pérez",
  "telefono": "3001234567",
  "fecha": "2026-11-15",
  "descripcion": "El computador no enciende desde la mañana",
  "dependencia_id": 1
}
```

Respuesta `201`: el caso con `estado: "Registrado"`, `prioridad: null` y `tecnico: null`.

**Validaciones.** Descripción de al menos 15 caracteres, placa y nombre no vacíos, teléfono de 7 a 20 caracteres (dígitos, +, ( ), - y espacios), fecha no futura y dependencia existente y activa; si algo falla responde `422` y no se crea el caso.

**Errores:** `400` transición de estado inválida, `401` sin token o credenciales inválidas, `403` rol o caso no autorizado, `404` caso inexistente, `409` regla de integridad de la base, `422` datos inválidos. Las respuestas llevan `detail` y nunca trazas internas.

## 7. Pruebas de API e integración y evidencias de funcionamiento

Pruebas automáticas, desde la raíz y con el entorno activado:

```bash
python -m pytest backend -v
```

Resultado de la última ejecución: **30 pasan, 0 fallan**. Esquema de la base: `python -I backend/db/probar_esquema.py`.

| Prueba | Tipo | Requisito | Resultado |
|---|---|---|---|
| `test_salud_y_openapi_exponen_los_16_pares` | endpoint | RNF-05 | Pasa |
| `test_login_correcto_devuelve_token_y_rol` | endpoint | RF-01 | Pasa |
| `test_login_incorrecto_mismo_mensaje` | endpoint | RF-01 | Pasa |
| `test_rutas_protegidas` | regla | RF-01, RN-07 | Pasa |
| `test_password_no_en_texto_plano` | regla | RF-01, RNF-02 | Pasa |
| `test_registrar_caso` | endpoint | RF-02, CA-01 | Pasa |
| `test_registro_invalido_422` (6 casos) | regla | RF-02, RN-08 | Pasa (6/6) |
| `test_solicitante_solo_ve_sus_casos` | regla | RF-03, RN-06 | Pasa |
| `test_tecnico_solo_ve_asignados` | regla | RF-03, RN-06 | Pasa |
| `test_evaluar` | endpoint | RF-04, RN-09 | Pasa |
| `test_asignar_y_reasignar` | regla | RF-05, RN-02, RN-10 | Pasa |
| `test_flujo_completo` | integración | RF-02 a RF-09, CA-01 a CA-05 | Pasa |
| `test_saltos_invalidos` | regla | RN-01, RN-03, RN-04 | Pasa |
| `test_resumen_coordinador` | endpoint | RF-10, CA-06 | Pasa |
| `test_catalogos` | endpoint | RF-02, RF-05 | Pasa |
| `test_solicitante_403_en_acciones_de_coordinador` | regla | RN-07 | Pasa |
| `test_404_con_rol_permitido_sobre_caso_inexistente` | endpoint | RN-06 | Pasa |
| `test_intervencion_no_editable_ni_borrable` (3 casos) | regla | RF-06, RN-05 | Pasa (3/3) |
| `test_inicializar_base_es_idempotente` | integración | RNF-03 | Pasa |
| `test_modelos_coinciden_con_el_esquema` | integración | RNF-03 | Pasa |
| `test_claves_foraneas_activas_en_cada_conexion` | integración | RNF-03 | Pasa |
| `test_flujo_completo_con_el_orm` | integración | RF-02 a RF-09 | Pasa |
| `test_protecciones_de_la_base_a_traves_del_orm` | integración | RN-02, RN-04, RN-05 | Pasa |

Pruebas funcionales PF: Por completar (004).

Matriz de trazabilidad: [`docs/trazabilidad.md`](docs/trazabilidad.md).

## 8. Control de versiones

- El trabajo se integra mediante ramas y *pull requests* hacia `main`, con commits descriptivos (`docs:`, `feat:`, `fix:`, `chore:`, `test:`).
- Cada pull request documenta propósito, cambios, pruebas efectuadas y requisitos asociados.
- Resumen verificable de aportes por integrante: por completar.

## 9. Conclusiones y limitaciones

Por completar.
