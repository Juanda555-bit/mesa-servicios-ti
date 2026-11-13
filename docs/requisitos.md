# Requisitos – Gestión de Solicitudes de Servicio (Mesa de Servicios TI)

## 1. Actores y Roles
- **Solicitante** (docente / administrativo): reporta incidentes o solicitudes y consulta el estado y resultado de sus propios casos.
- **Técnico**: evalúa, diagnostica, atiende e interviene en los casos que le son asignados; registra la solución final.
- **Coordinador**: evalúa y clasifica casos, asigna y reasigna técnicos responsables, cierra los casos, supervisa el flujo y consulta el resumen consolidado.

---

## 2. Requisitos Funcionales (RF)

| ID | Requisito Funcional | CA Obligatoria | Criterio de Aceptación Verificable |
|---|---|---|---|
| **RF-01** | Autenticación y control de acceso por rol (RBAC) | Todas | Login retorna credencial con rol; rutas protegidas restringen acciones según rol (`401`/`403`). |
| **RF-02** | Registro de incidente o solicitud por el solicitante | **CA-01** | Formulario con placa del equipo, nombre del usuario, teléfono, fecha, descripción (>=15 chars) y dependencia (elegida de un catálogo); persiste con estado `Registrado`. La fecha es el día de la falla y no puede ser futura. Incidentes y solicitudes comparten el mismo flujo. |
| **RF-03** | Consulta de casos creados por el solicitante | **CA-03, CA-05** | Lista y detalle de casos propios con estado, responsable y resultado; acceso denegado a casos de terceros. |
| **RF-04** | Evaluación y clasificación técnica del caso | **CA-02** | El coordinador revisa el caso, fija la prioridad (solo etiqueta, sin SLA) y pasa estado a `En evaluación`. |
| **RF-05** | Asignación y reasignación de técnico responsable | **CA-02, CA-03** | Coordinador asigna un técnico activo pasando a `Asignado`; reasignaciones generan registro de auditoría. |
| **RF-06** | Registro de intervenciones técnicas secuenciales | **CA-04** | El técnico asignado registra fecha, detalle de intervención y duración; solo el asignado puede intervenir. |
| **RF-07** | Control de transiciones de estado | **CA-02, CA-03** | Solo se permiten transiciones válidas según la máquina de estados; saltos inválidos devuelven `400 Bad Request`. |
| **RF-08** | Resolución y cierre de caso con registro de solución | **CA-05** | Técnico pasa a `Resuelto` con detalle de solución; solo el coordinador cierra formalmente a `Cerrado`. Un caso cerrado no se puede reabrir. |
| **RF-09** | Consulta del historial de intervenciones | **CA-04** | Visualización en orden cronológico (línea de tiempo en el detalle del caso) de todo el proceso y las actuaciones registradas. Todo es visible para el solicitante; no hay notas privadas. |
| **RF-10** | Tablero consolidado de coordinación | **CA-06** | Coordinador consulta casos abiertos y casos cerrados, con sus fechas; se conserva el desglose por técnico responsable por exigencia de CA-06. |

---

## 3. Reglas de Negocio (RN)

- **RN-01 (Flujo de estados):** `Registrado → En evaluación → Asignado → En atención → Resuelto → Cerrado`.  
  No existe el estado `Cancelado`: el solicitante no puede cancelar casos (decisión del equipo).  
  `Resuelto` lo marca el técnico; `Cerrado` solo lo marca el coordinador y no se puede reabrir.
- **RN-02 (Responsable único):** Un caso solo tiene un técnico responsable activo a la vez; únicamente ese técnico puede registrar intervenciones y marcar solución.
- **RN-03 (Condición de resolución):** No se permite resolver un caso sin al menos una intervención registrada y el detalle de la solución.
- **RN-04 (Inmutabilidad de casos cerrados):** Casos en `Cerrado` quedan bloqueados contra nuevas intervenciones o modificaciones.
- **RN-05 (Inviolabilidad de intervenciones):** Las intervenciones no se editan ni se eliminan (política *append-only* para trazabilidad).
- **RN-06 (Privacidad del solicitante):** El solicitante solo puede visualizar y consultar sus propios reportes.
- **RN-07 (Exclusividad de coordinación):** Solo el coordinador asigna/reasigna técnicos y accede al tablero consolidado de métricas.
- **RN-08 (Validación de entrada):** Placa del equipo, nombre del usuario, teléfono, fecha, descripción (mínimo 15 caracteres) y dependencia son campos obligatorios al registrar el caso.
- **RN-09 (Determinación de prioridad):** El solicitante no indica prioridad al reportar; la prioridad se asigna como etiqueta durante la evaluación.
- **RN-10 (Auditoría de asignación):** Toda asignación o reasignación de técnico genera una entrada automática en el historial del caso.

---

## 4. Requisitos No Funcionales (RNF)

- **RNF-01:** Validación de esquemas en servidor mediante Pydantic en FastAPI.
- **RNF-02:** Contraseñas protegidas con algoritmos de hash; variables sensibles aisladas en `.env` (con `.env.example`).
- **RNF-03:** Persistencia en base de datos relacional con claves foráneas e integridad referencial.
- **RNF-04:** Manejo centralizado de excepciones con respuestas de error HTTP estándar (sin filtrar trazas internas).
- **RNF-05:** API REST documentada interactivamente mediante OpenAPI/Swagger UI en `/docs`.
- **RNF-06:** Interfaz web intuitiva y usable en navegadores web de escritorio.
- **RNF-07:** Instalación y ejecución reproducible documentada en `README.md`.

---

## 5. Supuestos Acordados (S)

- **S-01:** Prioridades estándar: `Baja`, `Media`, `Alta`, `Crítica`.
- **S-02:** Categorías iniciales: Hardware, Software, Conectividad/Redes, Cuentas/Accesos. *(Sin uso en el reporte tras la entrevista; pendiente de retirar o reubicar.)*
- **S-03:** Asignación manual de técnicos por parte del coordinador.
- **S-04:** Casos cerrados no se reabren.
- **S-05:** Interacción y notificaciones 100% web dentro de la aplicación (sin dependencias de email o SMS).
- **S-06:** Usuarios predeterminados (seeder) por rol para pruebas y evaluación.
- **S-07:** Reportes e intervenciones estructurados en texto (sin carga de archivos binarios en el alcance base).

---

## 6. Historias de Usuario y Criterios de Aceptación

Se eligieron **historias de usuario** (metodología ágil) porque cada requisito funcional describe una acción de un rol concreto con un resultado verificable. Hay una historia por cada RF (US-01 ↔ RF-01, … US-10 ↔ RF-10) y cada una cita las reglas de negocio (RN) y las condiciones de aceptación (CA) que cubre. Los criterios usan el formato *Dado / Cuando / Entonces*.

### US-01 · Iniciar sesión según mi rol (RF-01 · RN-06, RN-07 · todas las CA)
**Como** usuario de la mesa de servicios, **quiero** iniciar sesión con mi correo y contraseña, **para** acceder solo a las funciones de mi rol.
- **CA-US01.1** Dado un usuario del *seeder*, cuando envía credenciales correctas, entonces recibe un token que indica su rol (`solicitante`, `tecnico` o `coordinador`).
- **CA-US01.2** Dado un usuario, cuando envía credenciales incorrectas, entonces recibe `401` sin indicar si falló el correo o la contraseña.
- **CA-US01.3** Dada una ruta protegida, cuando se llama sin token o con un rol no autorizado, entonces la respuesta es `401` o `403` y no se modifica nada.
- **CA-US01.4** Dada la base de datos, entonces ninguna contraseña está guardada en texto plano.

### US-02 · Reportar un incidente o solicitud (RF-02 · RN-08 · CA-01)
**Como** solicitante, **quiero** registrar un reporte con los datos del equipo y del problema, **para** que soporte técnico lo atienda.
- **CA-US02.1** Dado un solicitante autenticado, cuando envía placa del equipo, nombre del usuario, teléfono, fecha, dependencia del catálogo y descripción de 15 caracteres o más, entonces se crea el caso con estado `Registrado`, sin prioridad ni responsable, y puede consultarse después.
- **CA-US02.2** Dado un formulario con un campo vacío, una descripción de menos de 15 caracteres, una fecha futura o una dependencia inexistente, cuando se envía, entonces se responde `422` y no se guarda ningún caso.
- **CA-US02.3** Dado un incidente o una solicitud, entonces ambos siguen el mismo flujo de estados.

### US-03 · Consultar mis casos (RF-03 · RN-06 · CA-03, CA-05)
**Como** solicitante, **quiero** ver mis casos con su estado, responsable y resultado, **para** saber cómo avanza mi reporte.
- **CA-US03.1** Dado un solicitante con casos, cuando abre "Mis casos", entonces ve solo los suyos con identificador, estado, responsable (si existe) y fecha.
- **CA-US03.2** Dado un caso cerrado propio, cuando abre su detalle, entonces ve la solución registrada.
- **CA-US03.3** Dado un caso de otro solicitante, cuando intenta abrirlo, entonces recibe `403`; si el caso no existe, recibe `404`.

### US-04 · Evaluar y priorizar un caso (RF-04 · RN-07, RN-09 · CA-02)
**Como** coordinador, **quiero** revisar un caso nuevo y asignarle una prioridad, **para** ordenar la atención.
- **CA-US04.1** Dado un caso `Registrado`, cuando el coordinador fija prioridad `Baja`, `Media`, `Alta` o `Crítica`, entonces el caso pasa a `En evaluación` y queda registrado quién y cuándo.
- **CA-US04.2** Dado un valor de prioridad fuera de la lista, cuando se envía, entonces se responde `422` y el caso no cambia.
- **CA-US04.3** Dado un técnico o un solicitante, cuando intenta evaluar un caso, entonces recibe `403`.

### US-05 · Asignar y reasignar al responsable (RF-05 · RN-02, RN-07, RN-10 · CA-02, CA-03)
**Como** coordinador, **quiero** asignar un técnico a un caso y poder cambiarlo, **para** repartir la carga y dejar claro quién responde.
- **CA-US05.1** Dado un caso `En evaluación`, cuando el coordinador elige un técnico activo, entonces el caso pasa a `Asignado` y ese técnico es el único responsable.
- **CA-US05.2** Dado un caso `Asignado` o `En atención`, cuando el coordinador elige otro técnico, entonces el responsable cambia, el estado se mantiene y la línea de tiempo muestra quién reasignó, cuándo y el técnico anterior.
- **CA-US05.3** Dado un usuario sin rol de técnico, o un técnico inactivo, cuando se intenta asignar, entonces se rechaza y el caso no cambia.
- **CA-US05.4** Dado un técnico o un solicitante, cuando intenta asignar, entonces recibe `403`.

### US-06 · Registrar mis intervenciones (RF-06 · RN-02, RN-04, RN-05 · CA-04)
**Como** técnico, **quiero** registrar lo que hice en un caso asignado a mí, **para** dejar constancia de cada actuación.
- **CA-US06.1** Dado un caso asignado a mí, cuando registro una intervención con descripción y duración en minutos mayor a 0, entonces queda vinculada al caso con mi nombre y la fecha.
- **CA-US06.2** Dado un caso asignado a otro técnico, o un caso cerrado, cuando intento registrar una intervención, entonces recibe `403` o `400` y no se guarda.
- **CA-US06.3** Dada una intervención ya registrada, cuando se intenta editarla o eliminarla, entonces la operación se rechaza.

### US-07 · Avanzar el caso solo por pasos válidos (RF-07 · RN-01, RN-02, RN-04 · CA-02, CA-03)
**Como** coordinador o técnico, **quiero** que el sistema solo permita pasos de estado válidos, **para** que el proceso sea coherente.
- **CA-US07.1** Dado un caso `Asignado`, cuando el técnico responsable inicia la atención, entonces pasa a `En atención`.
- **CA-US07.2** Dado cualquier caso, cuando se intenta un salto no permitido (por ejemplo `Registrado` a `Cerrado`), entonces se responde `400` y el estado no cambia.
- **CA-US07.3** Dado un caso `Cerrado`, cuando se intenta cualquier cambio, entonces se rechaza.
- **CA-US07.4** Dado un cambio de estado válido, entonces queda registrado quién lo hizo y cuándo.

### US-08 · Resolver y cerrar un caso (RF-08 · RN-01, RN-03, RN-04 · CA-05)
**Como** técnico responsable, **quiero** registrar la solución de un caso, y **como** coordinador, **quiero** cerrarlo, **para** terminar la atención con un resultado visible para el solicitante.
- **CA-US08.1** Dado un caso `En atención` con al menos una intervención, cuando el técnico responsable registra el texto de la solución, entonces pasa a `Resuelto`.
- **CA-US08.2** Dado un caso sin intervenciones o una solución vacía, cuando se intenta resolver, entonces se rechaza y el caso no cambia.
- **CA-US08.3** Dado un caso `Resuelto`, cuando el coordinador lo cierra, entonces pasa a `Cerrado` y el solicitante ve la solución.
- **CA-US08.4** Dado un técnico o un solicitante, cuando intenta cerrar un caso, entonces recibe `403`; y un caso cerrado no puede reabrirse.

### US-09 · Ver la línea de tiempo del caso (RF-09 · RN-05, RN-06, RN-10 · CA-04)
**Como** solicitante, técnico o coordinador, **quiero** ver todo el proceso del caso en orden, **para** entender qué pasó y quién lo hizo.
- **CA-US09.1** Dado un caso con cambios de estado, asignaciones e intervenciones, cuando abro su detalle, entonces veo una línea de tiempo ordenada por fecha con tipo, autor y detalle.
- **CA-US09.2** Dado un caso reasignado, entonces la línea de tiempo muestra la reasignación con el técnico anterior y el nuevo.
- **CA-US09.3** Dado un solicitante, cuando abre el historial de un caso que no es suyo, entonces recibe `403`; no existen notas privadas, todo lo registrado es visible para el solicitante del caso.

### US-10 · Consultar el tablero de coordinación (RF-10 · RN-07 · CA-06)
**Como** coordinador, **quiero** ver los casos abiertos y cerrados con sus fechas y responsables, **para** supervisar el trabajo de la mesa.
- **CA-US10.1** Dados varios casos en distintos estados, cuando el coordinador abre el tablero, entonces ve los casos abiertos y los cerrados con sus fechas.
- **CA-US10.2** Dado el tablero, entonces muestra el desglose de casos por técnico responsable.
- **CA-US10.3** Dado un solicitante o un técnico, cuando intenta consultar el tablero, entonces recibe `403`.

### Cobertura de reglas de negocio

| RN | Historias que la verifican |
|---|---|
| RN-01 Flujo de estados | US-07, US-08 |
| RN-02 Responsable único | US-05, US-06, US-07 |
| RN-03 Condición de resolución | US-08 |
| RN-04 Caso cerrado inmutable | US-06, US-07, US-08 |
| RN-05 Historial *append-only* | US-06, US-09 |
| RN-06 Privacidad del solicitante | US-01, US-03, US-09 |
| RN-07 Exclusividad de coordinación | US-01, US-04, US-05, US-10 |
| RN-08 Validación de entrada | US-02 |
| RN-09 Prioridad en la evaluación | US-04 |
| RN-10 Auditoría de asignación | US-05, US-09 |

### Orden de desarrollo sugerido

Las historias dependen unas de otras, así que se construyen en este orden: US-01 → US-02 → US-03 → US-04 → US-05 → US-07 → US-06 → US-08 → US-09 → US-10.
