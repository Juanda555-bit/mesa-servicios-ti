# Mesa de Servicios TI

Proyecto Final 02 (PF-02) · Aplicaciones y Servicios Web · Tecnología en Desarrollo de Software.
Aplicación web para registrar, atender, dar seguimiento y cerrar casos de soporte tecnológico de una institución educativa.

> **Estado del proyecto (16/11/2026):** requisitos aprobados por el docente (12/11/2026); diseño aprobado por el equipo e implementado en la API (16/11/2026), en `docs/diseno.md`. Capa de base de datos (`backend/db/`) y API REST (16 endpoints con autenticación por rol, seeder de datos ficticios y pruebas) implementadas y probadas. Aún no hay interfaz web.

## 1. Información general

| Campo | Detalle |
|---|---|
| Proyecto | Mesa de servicios de soporte tecnológico (PF-02) |
| Problema | Los reportes de soporte llegan por correo, llamadas y mensajes directos, sin registro unificado, sin responsable claro y sin visibilidad del avance. |
| Asignatura | Aplicaciones y Servicios Web |
| Docente (cliente) | Juan Carlos Morales Guerra |
| Integrantes | Juan David Arias Ospina · Simón Herrera |
| Contribución de cada integrante | Resumen por áreas según `git shortlog -sne origin/fix/feat-api`, a fecha del commit `11543ca` (validado por ambos integrantes el 17/11/2026). **Juan David Arias** (11 commits): estructura inicial del repositorio, borrador de requisitos y plantilla de la entrevista; backend de la API (autenticación, esquemas y reglas, endpoints, seeder, pruebas de integración) y documentación de instalación y servicios en el README (p. ej. `2044e45`, `62903fd`, `50df7aa`). **Simón Herrera** (13 commits): especificación y registro de la entrevista, requisitos tras la entrevista e historias de usuario, README inicial, diseño, esquema SQL y modelos ORM con sus pruebas, limpieza e integración de la API (p. ej. `8dffa61`, `19b8d6d`, `e606cb2`, `11543ca`). |
| Fecha de entrega | Pendiente |
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
- 10 requisitos funcionales (RF-01 a RF-10), 10 reglas de negocio (RN-01 a RN-10) y 7 requisitos no funcionales (RNF-01 a RNF-07).
- 10 historias de usuario (US-01 a US-10), una por requisito funcional, con criterios de aceptación en formato *Dado / Cuando / Entonces* y una tabla que cruza las reglas de negocio con las historias que las verifican. Están en [`docs/requisitos.md`](docs/requisitos.md#6-historias-de-usuario-y-criterios-de-aceptación).

**Supuestos**
- 6 supuestos confirmados (S-01, S-03, S-04, S-05, S-06 y S-07; S-02 fue retirado tras la entrevista) y 6 supuestos del equipo no confirmados por el docente (EQ-01 a EQ-06). Definición en [`docs/requisitos.md`](docs/requisitos.md#5-supuestos-acordados-s); evidencia, estado, implementación y prueba de cada uno en la tabla "Supuestos: confirmación" de [`docs/entrevista.md`](docs/entrevista.md#supuestos-confirmación).
- `docs/requisitos.md` lista 5 supuestos del equipo (EQ-01 a EQ-05); EQ-06 (las intervenciones solo se registran con el caso en `En atención`) se añadió después y está documentado en la tabla de `docs/entrevista.md`.

## 4. Arquitectura, diseño de API y modelo de datos

Diseño de la Actividad 3, aprobado por el equipo e implementado en la API (16/11/2026): [`docs/diseno.md`](docs/diseno.md).

- Diagrama de componentes y responsabilidades: [Arquitectura](docs/diseno.md#2-arquitectura).
- Modelo de datos y relaciones: [Modelo de datos](docs/diseno.md#3-modelo-de-datos).
- Prototipos de interfaz: [descripción de las pantallas](docs/diseno.md#7-prototipos-de-interfaz-descripción); los prototipos gráficos y las capturas se agregarán cuando exista la interfaz.
- Justificación de tecnologías: [Decisiones técnicas](docs/diseno.md#1-decisiones-técnicas).

## 5. Configuración del entorno

Requisitos de software: Python 3.12 y Git. El frontend (React + Vite) aún no existe y se documentará cuando se implemente.

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

**Errores:** `400` transición de estado inválida, `401` sin token o credenciales inválidas, `403` rol o caso no autorizado, `404` caso inexistente, `409` regla de integridad de la base, `422` datos inválidos, `500` error interno genérico sin trazas. Las respuestas llevan `detail` y nunca trazas internas.

## 7. Pruebas de API e integración y evidencias de funcionamiento

Pruebas automáticas, desde la raíz y con el entorno activado:

```bash
python -m pytest backend -v
```

Resultado de la última ejecución (16/11/2026, `python -m pytest backend -q`): **30 pasan, 0 fallan**. Esquema de la base: `python -I backend/db/probar_esquema.py`.

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

Pruebas funcionales PF: Pendiente (se documentarán en un archivo enlazado desde este README, con evidencias en `evidencias/`).

Matriz de trazabilidad: [`docs/trazabilidad.md`](docs/trazabilidad.md).

## 8. Control de versiones

- Repositorio: https://github.com/Juanda555-bit/mesa-servicios-ti
- Ramas remotas: `main`, `docs/requisitos-y-entrevista`, `docs/diseno`, `feat/base-de-datos`, `feat/000-limpieza`, `feat/api` y `fix/feat-api` (esta última integra la API para ejecutarla desde la raíz; último commit `11543ca`).
- Pull requests: [#2](https://github.com/Juanda555-bit/mesa-servicios-ti/pull/2) (requisitos, diseño y capa de datos) y [#3](https://github.com/Juanda555-bit/mesa-servicios-ti/pull/3) (API REST e integración).
- Commits descriptivos (`docs:`, `feat:`, `fix:`, `chore:`, `test:`); cada pull request documentará propósito, cambios, pruebas y requisitos asociados.
- Resumen de aportes por áreas, a fecha del commit `11543ca` y según `git shortlog -sne origin/fix/feat-api` (validado por ambos integrantes el 17/11/2026): **Juan David Arias** (11 commits): estructura inicial del repositorio, borrador de requisitos y plantilla de la entrevista (`2044e45`); backend de la API: autenticación, esquemas y reglas, endpoints, seeder (`62903fd`) y pruebas de integración (`50df7aa`); documentación de instalación y servicios en el README. **Simón Herrera** (13 commits): especificación y registro de la entrevista, requisitos tras la entrevista e historias de usuario (`8dffa61`), README inicial, diseño, esquema SQL (`19b8d6d`) y modelos ORM con sus pruebas (`e606cb2`), limpieza e integración de la API (`11543ca`).

## 9. Conclusiones y limitaciones

Estado a 16/11/2026.

**Cumplimiento de las condiciones.** Según [`docs/trazabilidad.md`](docs/trazabilidad.md), CA-01 a CA-06 están implementadas en la API y probadas con pytest; sus pruebas funcionales y de interfaz y la columna "Pull request" siguen por completar.

| Condición | Estado |
|---|---|
| CA-01 | Implementada en la API y probada con pytest |
| CA-02 | Implementada en la API y probada con pytest |
| CA-03 | Implementada en la API y probada con pytest |
| CA-04 | Implementada en la API y probada con pytest |
| CA-05 | Implementada en la API y probada con pytest |
| CA-06 | Implementada en la API y probada con pytest |

**Dificultad resuelta.** La API de `feat/api` no se podía ejecutar desde la raíz del repositorio (fallaban las importaciones y faltaba una dependencia del login por formulario). Se corrigieron las importaciones y se fijó la dependencia; ahora las pruebas, el seeder y el servidor se ejecutan desde la raíz.

**Limitaciones y pendientes.**
- No hay interfaz web todavía.
- Las pruebas funcionales y sus evidencias están pendientes.
- Falta el endurecimiento de la seguridad de la API y alinear algunas validaciones y respuestas de error con lo acordado en el diseño.
