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

Resultado de la última ejecución (18/11/2026, rama `local/003-trabajo`, `python -m pytest backend -v`): **85 pasan, 0 fallan** (59 en `test_api.py`, 3 en `test_capas.py`, 18 en `test_configuracion.py` y 5 en `test_modelos.py`). Las pruebas usan un secreto ficticio y una base en memoria definidos en `backend/tests/conftest.py`: no leen `.env` ni tocan `backend/mesa_ti.db`. Esquema de la base: `python -I backend/db/probar_esquema.py` (45 correctas, 0 fallidas).

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
