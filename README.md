# Mesa de Servicios TI

Proyecto Final 02 (PF-02) · Aplicaciones y Servicios Web · Tecnología en Desarrollo de Software.
Aplicación web para registrar, atender, dar seguimiento y cerrar casos de soporte tecnológico de una institución educativa.

> **Estado del proyecto (18/11/2026):** requisitos aprobados por el docente (12/11/2026); diseño aprobado por el equipo e implementado. Capa de base de datos (`backend/db/`), API REST (16 endpoints con autenticación por rol, seguridad endurecida, seeder de datos ficticios y 85 pruebas pytest) e interfaz web React + Vite (spec 003) con el flujo completo por rol, integradas en `main` (PR #2 a #5). Pruebas funcionales PF-01 a PF-11 ejecutadas el 18/11/2026 sobre `main` `58c80e0` (todas aprobadas) más la PF-12 de la spec 003, con evidencias en `evidencias/`; matriz de trazabilidad completa en `docs/trazabilidad.md`. La documentación y las evidencias de la spec 004 viajan en el PR #6, pendiente de revisión y de merge.

## 1. Información general

| Campo | Detalle |
|---|---|
| Proyecto | Mesa de servicios de soporte tecnológico (PF-02) |
| Problema | Los reportes de soporte llegan por correo, llamadas y mensajes directos, sin registro unificado, sin responsable claro y sin visibilidad del avance. |
| Asignatura | Aplicaciones y Servicios Web |
| Docente (cliente) | Juan Carlos Morales Guerra |
| Integrantes | Juan David Arias Ospina · Simón Herrera |
| Contribución de cada integrante | Resumen por áreas según `git shortlog -sne main`, a fecha del 18/11/2026 y del commit `58c80e0` (39 commits; detalle en el apartado 8). **Juan David Arias** (19 commits, con autor `Juanda555-bit` en tres identidades): estructura inicial del repositorio y borrador de requisitos y de la plantilla de la entrevista (`db2ee87`, `2044e45`); backend de la API: autenticación, esquemas y reglas, endpoints, seeder y pruebas de integración (`62903fd`, `355c366`, `a4f376e`, `22b7291`, `50df7aa`); documentación de instalación y servicios en el README (`e31f000`); CORS y concordancia de mensajes 422 (`59efcdc`); interfaz web React + Vite de la spec 003 (`052b3b5`, `7fe357c`, `ea959f6`) y su documentación (`d893fed`). **Simón Herrera** (20 commits, con autor `Simonh003 [Herrera]` y `Simon Herrera`): especificación y registro de la entrevista, requisitos tras la entrevista e historias de usuario (`abf5e0b`, `e483b0a`, `8dffa61`); README inicial (`2939c27`); diseño, esquema SQL y modelos ORM con sus pruebas (`e5d1bea`, `19b8d6d`, `e606cb2`, `dbe9796`, `8ce53f5`); limpieza e integración de la API (`1e8b6d3`, `11543ca`); seguridad y capas de la spec 002 con sus pruebas funcionales de API (`16f6c4d`, `1c025d5`); trazabilidad de los PR y fusión de los PR #4 y #5 (`6acc782`, `25c67bc`, `bfb0810`, `58c80e0`). La documentación y las evidencias de la spec 004 (pruebas PF-01 a PF-11, README y trazabilidad) las redacta y sube Simón Herrera; no figuran en este recuento porque aún no están en `main` (PR #6, apartado 8). |
| Fecha de entrega | 18/11/2026 |
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
- Prototipos de interfaz: [descripción de las pantallas](docs/diseno.md#7-prototipos-de-interfaz-descripción); capturas reales de la interfaz por rol y del flujo completo en [`evidencias/PF-12-*.png`](evidencias/) (ver PF-12 en [`docs/pruebas_funcionales.md`](docs/pruebas_funcionales.md)).
- Justificación de tecnologías: [Decisiones técnicas](docs/diseno.md#1-decisiones-técnicas).

## 5. Configuración del entorno

Requisitos de software: Python 3.12, Git y, para el frontend (React + Vite), Node.js `^20.19.0 || >=22.12.0` (el mismo rango que `engines.node` de `frontend/package.json`) con npm.

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

**Variables de entorno.** Copiar `.env.example` a `.env` (`cp .env.example .env`; en Windows `copy .env.example .env`) y ajustar. El archivo `.env` no se versiona y no debe contener secretos compartidos. **`JWT_SECRET` es obligatorio:** sin un secreto válido no arrancan ni la API ni el seeder (terminan con un mensaje en español), y el valor de ejemplo de `.env.example` se rechaza. Para generar uno propio de 64 caracteres:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Quien tenga un `.env` de versiones anteriores debe renombrar sus variables de secreto y de duración del token a `JWT_SECRET` y `JWT_EXPIRA_MIN`; las anteriores ya no se leen.

| Variable | Uso |
|---|---|
| `JWT_SECRET` | Clave para firmar los tokens. Obligatoria, mínimo 32 caracteres; sin ella (o con el valor de ejemplo) no arrancan la API ni el seeder. |
| `JWT_EXPIRA_MIN` | Minutos de validez del token: entero mayor que 0 (480 = 8 horas, valor por defecto si se omite). |
| `CORS_ORIGINS` | Orígenes permitidos para el frontend, separados por coma (por defecto `http://localhost:5173`). No admite `*`: si se incluye, la API no arranca. La API no usa cookies ni credenciales en CORS. |
| `DATABASE_URL` | Opcional (comentada en `.env.example`): URL SQLite; si se omite se usa `backend/mesa_ti.db`. |

**Base de datos y datos de prueba.** `python -m backend.seed` crea la base (si no existe) y carga datos ficticios. Para empezar de cero, borrar `backend/mesa_ti.db` y volver a ejecutarlo.

- API: http://localhost:8000 · Documentación interactiva: http://localhost:8000/docs
- En `/docs`, botón **Authorize**: correo en *username* y la contraseña.

Usuarios de prueba del seeder (contraseña de demostración `Mesa2026*`, datos ficticios). **Aviso:** esa contraseña es ficticia y común a todos los usuarios del seeder; no debe reutilizarse ni usarse fuera del entorno local, y menos en un entorno real.

| Rol | Correo |
|---|---|
| Coordinador | coordinador@mesa.edu.co |
| Técnico | tecnico1@mesa.edu.co, tecnico2@mesa.edu.co |
| Solicitante | solicitante1@mesa.edu.co, solicitante2@mesa.edu.co |

**Frontend (React + Vite).** Orden de arranque: 1) API, 2) seeder, 3) frontend. Con la API y el seeder en marcha (comandos anteriores), en otra terminal desde la raíz:

```bash
cd frontend
npm ci                      # o npm install
copy .env.example .env      # Windows (en Linux/Mac: cp .env.example .env)
npm run dev
```

- Interfaz: http://localhost:5173 (inicio de sesión con los usuarios del seeder).
- `frontend/.env.example` define `VITE_API_URL=http://localhost:8000`, la dirección de la API; el navegador la llama directamente, sin proxy de Vite. Si se cambia el origen del frontend, debe coincidir con `CORS_ORIGINS` del backend.
- `npm run build` genera el empaquetado en `frontend/dist` (no se versiona).

**Requisitos del repositorio.** Elementos que acompañan el código (sin credenciales reales; `.env` no se versiona):

- [`README.md`](README.md) (este documento) y [`.gitignore`](.gitignore)
- [`.env.example`](.env.example) (backend) y [`frontend/.env.example`](frontend/.env.example) (frontend)
- [`docs/requisitos.md`](docs/requisitos.md), [`docs/diseno.md`](docs/diseno.md), [`docs/trazabilidad.md`](docs/trazabilidad.md) y [`docs/pruebas_funcionales.md`](docs/pruebas_funcionales.md)
- [`evidencias/`](evidencias/): capturas y respuestas de las pruebas

## 6. Servicios web implementados

Documentación interactiva (Swagger): http://localhost:8000/docs

| Método | Ruta | Descripción | Requisito relacionado |
|---|---|---|---|
| GET | `/salud` | Estado del servicio | – |
| POST | `/auth/login` | Devuelve el token y, junto a él, el rol y el nombre | RF-01 |
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

El token es un JWT firmado con `JWT_SECRET` que contiene solo `sub` (id del usuario) y `exp`; **no lleva el rol**: este va en la respuesta del login y el backend lo consulta en la base en cada petición. Con correo o contraseña incorrectos responde `401` con `{"detalle": "Correo o contraseña incorrectos"}`.

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

**Validaciones.** Descripción de al menos 15 caracteres, placa y nombre no vacíos, teléfono no vacío de hasta 20 caracteres (sin patrón de formato), fecha no futura y dependencia existente y activa; en las intervenciones, descripción no vacía y duración mayor que 0 (sin máximo). Si algo falla responde `422` y no se crea el caso.

**Errores.** Todas las respuestas de error usan el cuerpo `{"detalle": "<mensaje en español>"}`, sin trazas internas. Códigos: `400` transición de estado inválida o regla de integridad rechazada por la base (con mensaje genérico, sin detalles de SQL), `401` sin token, token inválido o credenciales incorrectas, `403` rol o caso no autorizado, `404` caso o ruta inexistente, `405` método no permitido, `422` datos inválidos y `500` error interno genérico. En `422` el cuerpo añade `campos`, una lista de `{"campo": ..., "motivo": ...}` con todos los campos inválidos:

```json
{"detalle": "Datos de entrada no válidos", "campos": [{"campo": "descripcion", "motivo": "..."}]}
```

## 7. Pruebas de API e integración y evidencias de funcionamiento

Pruebas automáticas, desde la raíz y con el entorno activado:

```bash
python -m pytest backend -v
```

Resultado de la última ejecución (18/11/2026, `main` en el commit `58c80e0`, `python -m pytest backend -v`): **85 pasan, 0 fallan** (59 en `test_api.py`, 3 en `test_capas.py`, 18 en `test_configuracion.py` y 5 en `test_modelos.py`). Las pruebas usan un secreto ficticio y una base en memoria definidos en `backend/tests/conftest.py`: no leen `.env` ni tocan `backend/mesa_ti.db`. Esquema de la base: `python -I backend/db/probar_esquema.py` (45 correctas, 0 fallidas).

| Prueba | Tipo | Requisito | Resultado |
|---|---|---|---|
| `test_salud_y_openapi_exponen_los_16_pares` | endpoint | RNF-05 | Pasa |
| `test_login_correcto_devuelve_token_y_rol` | endpoint | RF-01 | Pasa |
| `test_token_invalido_401` (5 casos: vencido, sin `exp`, sin `sub`, `alg` none, otra firma) | regla | RF-01, RNF-02 | Pasa (5/5) |
| `test_token_solo_sub_y_exp` | regla | RF-01, RNF-02 | Pasa |
| `test_login_devuelve_rol_correcto` | endpoint | RF-01 | Pasa |
| `test_claim_rol_manipulado_403` | regla | RF-01, RN-07 | Pasa |
| `test_login_incorrecto_mismo_mensaje` | endpoint | RF-01 | Pasa |
| `test_login_verifica_hash_siempre` | regla | RF-01, RNF-02 | Pasa |
| `test_rutas_protegidas` | regla | RF-01, RN-07 | Pasa |
| `test_password_no_en_texto_plano` | regla | RF-01, RNF-02 | Pasa |
| `test_registrar_caso` | endpoint | RF-02, CA-01 | Pasa |
| `test_registro_invalido_422` (8 casos) | regla | RF-02, RN-08 | Pasa (8/8) |
| `test_telefono_sin_patron` | regla | RF-02, RN-08 | Pasa |
| `test_solicitante_solo_ve_sus_casos` | regla | RF-03, RN-06 | Pasa |
| `test_tecnico_solo_ve_asignados` | regla | RF-03, RN-06 | Pasa |
| `test_evaluar` | endpoint | RF-04, RN-09 | Pasa |
| `test_asignar_y_reasignar` | regla | RF-05, RN-02, RN-10 | Pasa |
| `test_flujo_completo` | integración | RF-02 a RF-09, CA-01 a CA-05 | Pasa |
| `test_duracion_sin_maximo` | regla | RF-06 | Pasa |
| `test_intervencion_fuera_de_atencion_400` (2 casos: `Asignado`, `Resuelto`) | regla | RF-06, RN-01 | Pasa (2/2) |
| `test_resolver_cerrar_invalidos_sin_efectos_http` | regla | RF-08, RN-01, RN-03, RN-04 | Pasa |
| `test_resolver_cerrar_invalidos_sin_efectos_servicio` | regla | RF-08, RN-01, RN-03, RN-04 | Pasa |
| `test_saltos_invalidos` | regla | RN-01, RN-03, RN-04 | Pasa |
| `test_resumen_coordinador` | endpoint | RF-10, CA-06 | Pasa |
| `test_catalogos` | endpoint | RF-02, RF-05 | Pasa |
| `test_solicitante_403_en_acciones_de_coordinador` | regla | RN-07 | Pasa |
| `test_404_con_rol_permitido_sobre_caso_inexistente` | endpoint | RN-06 | Pasa |
| `test_intervencion_no_editable_ni_borrable` (3 casos) | regla | RF-06, RN-05 | Pasa (3/3) |
| `test_servicio_lanza_excepciones_de_dominio` | regla | RNF-04 | Pasa |
| `test_error_de_dominio_usa_detalle` | regla | RNF-04 | Pasa |
| `test_errores_usan_detalle` (11 casos: 400, 401, 403, 404, 405, 422, 500) | regla | RNF-04 | Pasa (11/11) |
| `test_422_lista_todos_los_campos` | regla | RNF-04, RN-08 | Pasa |
| `test_integridad_400_sin_detalles_internos` | regla | RNF-04 | Pasa |
| `test_servicios_sin_fastapi` | estructura | RNF-04 | Pasa |
| `test_routers_sin_reglas` | estructura | RNF-04 | Pasa |
| `test_listar_casos_servicio_filtra_por_rol` | regla | RF-03, RN-06 | Pasa |
| `test_jwt_secret_invalido_no_carga` (4 casos) | regla | RNF-02 | Pasa (4/4) |
| `test_jwt_secret_de_32_carga` | regla | RNF-02 | Pasa |
| `test_jwt_expira_min_invalido` (3 casos) | regla | RNF-02 | Pasa (3/3) |
| `test_jwt_expira_min_por_defecto_480` | regla | RNF-02 | Pasa |
| `test_env_example_sin_valores_reales` | regla | RNF-02 | Pasa |
| `test_pruebas_aisladas_del_env_local` | regla | RNF-02 | Pasa |
| `test_inicializar_base_es_idempotente` | integración | RNF-03 | Pasa |
| `test_modelos_coinciden_con_el_esquema` | integración | RNF-03 | Pasa |
| `test_claves_foraneas_activas_en_cada_conexion` | integración | RNF-03 | Pasa |
| `test_flujo_completo_con_el_orm` | integración | RF-02 a RF-09 | Pasa |
| `test_protecciones_de_la_base_a_traves_del_orm` | integración | RN-02, RN-04, RN-05 | Pasa |

### Pruebas funcionales (PF)

Las 22 pruebas funcionales (PF-01 a PF-12 por la interfaz y la API; PF-API-01 a PF-API-10 contra la API) están documentadas con todos sus campos (requisito, precondiciones, pasos, entrada, método y ruta con código HTTP, resultado esperado y obtenido, estado y evidencia) en [`docs/pruebas_funcionales.md`](docs/pruebas_funcionales.md). Las capturas y salidas están en [`evidencias/`](evidencias/) y la relación con los criterios de aceptación en la matriz de trazabilidad: [`docs/trazabilidad.md`](docs/trazabilidad.md). Las PF-01 a PF-11 se ejecutaron seguidas el 18/11/2026 sobre una sola base sembrada y sobre el código de `main` en el commit `58c80e0`; las capturas de la pestaña Red solo muestran la respuesta, sin token ni cabeceras.

| Prueba | Descripción | Requisito | Resultado |
|---|---|---|---|
| PF-01 | Registro válido de caso | CA-01 · RF-02 · RN-08 | Aprobada |
| PF-02 | Registro con datos inválidos (422) | CA-01 · RN-08 | Aprobada |
| PF-03 | Consulta de caso existente | CA-03 · RF-03 | Aprobada |
| PF-04 | Consulta de caso inexistente (404) | RF-03 · RNF-04 | Aprobada |
| PF-05 | Gestión por personal autorizado (evaluar y asignar) | CA-02 · RN-07 · RN-09 · RN-10 | Aprobada |
| PF-06 | Gestión por actor no autorizado (403) | CA-02 · RN-02 · RN-06 · RN-07 | Aprobada |
| PF-07 | Consulta de estado y responsable tras reasignar | CA-03 · RN-02 · RN-10 | Aprobada |
| PF-08 | Historial de intervenciones | CA-04 · RN-05 | Aprobada |
| PF-09 | Cierre de caso y consulta de resultado (400 en transiciones inválidas) | CA-05 · RN-01 · RN-03 · RN-04 | Aprobada |
| PF-10 | Consulta consolidada de coordinación (403 a otros roles) | CA-06 · RN-07 | Aprobada |
| PF-11 | Persistencia e integridad de relaciones tras reiniciar la API | CA-01 a CA-06 · RNF-03 | Aprobada |
| PF-12 | Integración interfaz–API–base de datos: flujo completo | CA-01 a CA-06 | Aprobada |
| PF-API-01 | Login correcto: token y rol | CA-03 · RF-01 | Aprobada |
| PF-API-02 | Login fallido indistinguible | CA-03 · RNF-04 | Aprobada |
| PF-API-03 | Token manipulado | CA-03 · RN-06 | Aprobada |
| PF-API-04 | Token vencido | CA-03 · RN-06 | Aprobada |
| PF-API-05 | Sin token y rol sin permiso | CA-02 · CA-06 · RN-07 | Aprobada |
| PF-API-06 | Registro inválido: 422 con `detalle` y `campos` | CA-01 · RN-08 | Aprobada |
| PF-API-07 | Teléfono de 20 caracteres aceptado | CA-01 · RF-02 · RN-08 | Aprobada |
| PF-API-08 | Caso inexistente (404) y caso ajeno (403) | CA-03 · RN-06 | Aprobada |
| PF-API-09 | Recorrido completo de un caso por la API | CA-01 a CA-06 · RN-01 a RN-05 | Aprobada |
| PF-API-10 | Arranque rechazado con `JWT_SECRET` corto | RF-1 (spec 002) | Aprobada |

**Cómo reproducirlas.**

1. Preparar el entorno y el `.env` con un `JWT_SECRET` propio (apartado 5).
2. Arrancar la API: `python -m uvicorn backend.app.main:app` (documentación Swagger en http://localhost:8000/docs).
3. Sembrar la base una sola vez: `python -m backend.seed` (datos ficticios; para repetir desde cero, borrar `backend/mesa_ti.db` y sembrar de nuevo).
4. Arrancar el frontend: `cd frontend` y `npm run dev` (http://localhost:5173).
5. Iniciar sesión con los usuarios del seeder (apartado 5; contraseña de demostración `Mesa2026*`): `solicitante1` para PF-01 a PF-04, `coordinador` y `tecnico1` o `tecnico2` para PF-05 a PF-12.
6. Seguir los pasos de cada prueba en [`docs/pruebas_funcionales.md`](docs/pruebas_funcionales.md) en orden numérico, sin volver a sembrar entre ellas: cada PF parte del estado que dejó la anterior. Los casos de error que la interfaz no permite provocar (por ejemplo `404`, `403` y el segundo cierre) se hacen por la API, con Swagger en `/docs` (botón **Authorize**) o con peticiones HTTP.

Verificación automática de esta versión (`main`, commit `58c80e0`): `python -m pytest backend -q` da 85 pasan y 0 fallan, y `python -I backend/db/probar_esquema.py` da 45 correctas y 0 fallidas.

Matriz de trazabilidad: [`docs/trazabilidad.md`](docs/trazabilidad.md).

## 8. Control de versiones

- Repositorio: https://github.com/Juanda555-bit/mesa-servicios-ti
- Ramas: `main`; ramas remotas `docs/requisitos-y-entrevista`, `docs/diseno`, `feat/base-de-datos`, `feat/002-seguridad-y-capas` y `feat/003-frontend`; ramas de los PR #2 y #3 (`feat/000-limpieza`, `fix/feat-api`, ya fusionadas) y rama de la spec 004 `feat/004-pruebas-y-entrega` (PR #6).
- Pull requests (todos con merge commit):
  - [#2](https://github.com/Juanda555-bit/mesa-servicios-ti/pull/2): requisitos, diseño y capa de datos, con la limpieza del repositorio. Fusionado el 17/11/2026 (`741e234`).
  - [#3](https://github.com/Juanda555-bit/mesa-servicios-ti/pull/3): API REST integrada y ejecutable desde la raíz. Fusionado el 17/11/2026 (`14901ff`).
  - [#4](https://github.com/Juanda555-bit/mesa-servicios-ti/pull/4): seguridad y capas de la API (spec 002). Fusionado el 18/11/2026 (`bfb0810`).
  - [#5](https://github.com/Juanda555-bit/mesa-servicios-ti/pull/5): interfaz web React + Vite con el flujo completo por rol (spec 003). Fusionado el 18/11/2026 (`58c80e0`).
  - [#6](https://github.com/Juanda555-bit/mesa-servicios-ti/pull/6): pruebas funcionales PF-01 a PF-11, evidencias, README y trazabilidad finales (spec 004, rama `feat/004-pruebas-y-entrega`). Lo abre Simón Herrera; queda pendiente la revisión de Juan David Arias y del merge.
- Commits descriptivos (`docs:`, `feat:`, `fix:`, `chore:`, `test:`); cada pull request documenta propósito, cambios, pruebas y requisitos asociados.
- Revisión entre integrantes, tal como ocurrió: Juan David Arias revisó el PR #2 (revisión con comentarios), aprobó el PR #3 y comentó el PR #4; el PR #5 reúne commits de ambos integrantes. En el PR #4 la aprobación fue un comentario y no incluyó un commit propio del revisor, aunque el flujo acordado lo pedía; se deja constancia de lo ocurrido sin presentarlo como cumplido. En el PR #6 todos los commits son de Simón Herrera y Juan David Arias lo revisa en GitHub sin commit propio (decisión D-9 de la spec 004).
- Resumen de aportes, según `git shortlog -sne main` a fecha del 18/11/2026 (commit `58c80e0`, 39 commits), tal cual lo cuenta Git por identidad de autor:

| Identidad de autor | Commits |
|---|---|
| Simonh003 [Herrera] | 18 |
| Juanda555-bit [Arias] | 8 |
| Juanda555-bit (sin corchetes, correo de GitHub) | 7 |
| Juanda555-bit (sin corchetes, otro correo) | 4 |
| Simon Herrera (correo de GitHub) | 2 |

  Sumando las identidades de cada persona: **Simón Herrera 20 commits** y **Juan David Arias 19 commits**. Áreas de cada uno: Juan David Arias, estructura inicial, backend de la API (autenticación, esquemas, endpoints, seeder y pruebas de integración, `62903fd`, `355c366`, `a4f376e`, `22b7291`, `50df7aa`), documentación de instalación y la interfaz web de la spec 003 (`052b3b5`, `7fe357c`, `ea959f6`, `d893fed`); Simón Herrera, entrevista y requisitos (`abf5e0b`, `e483b0a`, `8dffa61`), diseño, esquema SQL y modelos ORM (`e5d1bea`, `19b8d6d`, `e606cb2`), integración de la API (`11543ca`), spec 002 (`16f6c4d`, `1c025d5`), trazabilidad y fusión de los PR #4 y #5.
- Los commits de la spec 004 (PR #6) todavía no están en `main`, por eso no figuran en el recuento anterior: los commits de esa rama los hace Simón Herrera y Juan David Arias participa solo con la revisión del PR #6; no se le atribuye trabajo de la spec 004.


## 9. Conclusiones y limitaciones

Estado a 18/11/2026.

**Cumplimiento de las condiciones.** Según [`docs/trazabilidad.md`](docs/trazabilidad.md), CA-01 a CA-06 están implementadas en la API y en la interfaz web, integradas en `main` (PR #2 a #5), probadas con pytest (85 pasan, 0 fallan) y demostradas con pruebas funcionales por la interfaz y la API, todas aprobadas el 18/11/2026 sobre `main` `58c80e0`. PF-11 (persistencia tras reiniciar la API) y PF-12 (flujo completo de un caso) cubren las seis condiciones.

| Condición | Estado | Pruebas funcionales |
|---|---|---|
| CA-01 | Implementada (API e interfaz) y probada | PF-01, PF-02, PF-11, PF-12 |
| CA-02 | Implementada (API e interfaz) y probada | PF-05, PF-06, PF-11, PF-12 |
| CA-03 | Implementada (API e interfaz) y probada | PF-03, PF-04, PF-07, PF-11, PF-12 |
| CA-04 | Implementada (API e interfaz) y probada | PF-08, PF-11, PF-12 |
| CA-05 | Implementada (API e interfaz) y probada | PF-09, PF-11, PF-12 |
| CA-06 | Implementada (API e interfaz) y probada | PF-10, PF-11, PF-12 |

**Dificultades resueltas.**
- La API de `feat/api` no se podía ejecutar desde la raíz del repositorio (fallaban las importaciones y faltaba una dependencia del login por formulario). Se corrigieron las importaciones y se fijó la dependencia (commit `11543ca`, PR #3).
- La API de la primera versión no cumplía el endurecimiento de seguridad acordado (secreto JWT obligatorio, token solo con `sub` y `exp`, capas separadas, errores unificados en `detalle`). Se resolvió en la spec 002 (commit `16f6c4d`, PR #4).
- Antes de conectar la interfaz se quitaron las credenciales y el comodín de CORS y se corrigió la concordancia de los mensajes 422 de la API (commit `59efcdc`, spec 003, PR #5).
- La PF-12 se ejecutó antes de que el código estuviera en `main`; para que las pruebas de la spec 004 fueran verificables, las PF-01 a PF-11 se ejecutaron directamente sobre `main` `58c80e0` (spec 004, PR #6).

**Limitaciones y pendientes (dentro del alcance aprobado).**
- No hay pruebas automáticas del frontend: la interfaz se verifica con las pruebas funcionales y con Chrome DevTools.
- El seeder no incluye casos en estado `Resuelto`; por eso la PF-12 recorre un caso nuevo de principio a fin.
- En modo desarrollo, la pestaña Red muestra peticiones duplicadas o canceladas (`net::ERR_ABORTED`): es la doble ejecución de efectos de React (StrictMode) y no ocurre en la compilación de producción.
- La fecha de la intervención (RF-06) es la fecha y hora automática del servidor (`creado_en`): interpretación del equipo C-3 de la spec 003, documentada en [`docs/entrevista.md`](docs/entrevista.md#supuestos-confirmación); no se modificó `docs/requisitos.md`.
- Los comentarios opcionales del auditor de seguridad quedan como mejoras futuras; la contraseña de demostración del seeder es ficticia y común, solo para uso local.
- El PR #6 aún no está fusionado: el apartado 8 recoge lo ocurrido hasta el 18/11/2026.
