# Registro de entrevista con el cliente (docente)

- **Fecha:** 12/11/2026
- **Participantes:** Juan David Arias Ospina, Simón Herrera, Docente Juan Carlos Morales Guerra
- **Medio:** Presencial / Asesoría de clase
- **Objetivo:** Validar y aprobar el alcance, flujo de atención y reglas del sistema según la Actividad 2 de la Guía PF-02.

---

## Preguntas y Respuestas para el Docente

| # | Pregunta | Propuesta del equipo | Respuesta del docente | Requisito / RN Afectado |
|---|---|---|---|---|
| **1** | ¿Hay diferencia funcional en el flujo entre *incidente* y *solicitud*, o comparten el mismo ciclo de vida? | Comparten el mismo flujo de estados para mantener la API coherente, diferenciándose por categoría y prioridad. | Es el mismo flujo. | RF-02, RN-01 |
| **2** | ¿Qué datos mínimos debe tener un reporte inicial? | Título, tipo, categoría, prioridad sugerida y descripción detallada (mínimo 15 caracteres). | Placa del equipo, nombre del usuario, teléfono, fecha, descripción y dependencia. | RF-02, RN-08 |
| **3** | ¿Quién asigna: el coordinador a mano o algún criterio automático? | Asignación manual directa por el coordinador desde su panel. | Manual. | RF-05, S-03 |
| **4** | En el ciclo de vida, ¿se manejan dos estados finales (*Resuelto* por técnico y *Cerrado* por coordinación/usuario) o se cierra directamente? | Mantener `Resuelto` (técnico) y `Cerrado` (confirmación de usuario/coordinador). | Resuelve el técnico. Solo el coordinador puede cerrar. | RN-01, RF-08 |
| **5** | ¿Puede el solicitante cancelar un caso? ¿Se puede reabrir un caso cerrado? | Cancelar solo si está en `Registrado`. Casos cerrados no se reabren (se abre nuevo caso referenciado). | Solo el coordinador puede cerrar y no se puede reabrir. El docente no mencionó la cancelación; el equipo decidió no incluirla. | RN-01, RN-04, S-04 |
| **6** | ¿Hay tiempos máximos de atención formalizados (SLA) o solo la etiqueta de prioridad? | Solo etiquetado de prioridad (`Baja/Media/Alta/Crítica`), sin temporizadores de SLA. | Solo etiqueta. | S-01, RF-04 |
| **7** | ¿Un caso puede reasignarse a otro técnico? ¿Se guarda ese cambio? | Sí, solo por el coordinador, y queda registrado en el historial del caso para trazabilidad. | Sí se puede. | RN-02, RN-10 |
| **8** | ¿El solicitante ve todas las intervenciones o solo el resultado final? | Ve todas las intervenciones públicas y la solución final para garantizar transparencia. | Todo el proceso puede verlo, con una línea de tiempo en los detalles. | RF-03, RF-09 |
| **9** | ¿Qué debe mostrar exactamente el consolidado de la coordinación (`CA-06`)? | Contadores totales, casos agrupados por estado y casos agrupados por técnico responsable. | Casos abiertos, casos cerrados y fechas. | RF-10, CA-06 |
| **10** | ¿Los usuarios se registran solos o se pueden precargar con un *seeder*? | Se incluirá un *seeder* con usuarios demo de cada rol (`solicitante`, `tecnico`, `coordinador`) para pruebas fáciles. | Lo más fácil para los usuarios: usuarios predeterminados (seeder) por rol (solicitante, técnico, coordinador) para pruebas. | RF-01, S-06 |
| **11** | ¿El reporte e intervenciones serán solo de texto o deben permitir subir imágenes/capturas? | Se propone limitar a texto estructurado en el alcance base para concentrar el esfuerzo en la API REST. | Solo texto (texto estructurado). | RF-02, RF-06, S-07 |
| **12** | ¿Se requieren notas técnicas privadas (invisibles al usuario) o todo es público en el caso? | Todas las intervenciones son públicas para el usuario del caso. | No es necesario. | RF-06, RF-09 |
| **13** | ¿El docente valida y aprueba esta delimitación para dar paso a la Actividad 3 (Diseño de API y Base de Datos)? | Aprobación formal para avanzar a `docs/diseno.md`. | Aprobado. Tras su revisión el docente dijo: "yo lo veo bien hasta el momento, sigan adelante". | Hito Actividad 2 |

---

## Decisiones confirmadas
- Incidentes y solicitudes comparten el mismo flujo.
- Datos del reporte: placa del equipo, nombre del usuario, teléfono, fecha, descripción y dependencia.
- Asignación manual por el coordinador; la reasignación está permitida.
- El técnico resuelve; solo el coordinador cierra y un caso cerrado no se reabre.
- Prioridad solo como etiqueta, sin SLA.
- Todo el proceso es visible para el solicitante, con línea de tiempo en el detalle.
- Consolidado de coordinación: casos abiertos, casos cerrados y fechas.
- Usuarios: lo más fácil para los usuarios, con usuarios predeterminados (seeder) por rol.
- Solo texto; no se necesitan notas privadas.
- El docente aprobó la delimitación.

---

## Cambios a los requisitos tras la entrevista
- **RF-02 y RN-08:** el reporte pasa a pedir placa del equipo, nombre del usuario, teléfono, fecha, descripción (mínimo 15 caracteres, se mantiene) y dependencia. Tipo, categoría y prioridad sugerida salen del reporte.
- **RF-04 y RN-09:** la prioridad la fija como etiqueta quien evalúa; ya no hay prioridad sugerida por el solicitante.
- **RF-08, RN-01, rol Coordinador:** solo el coordinador cierra; se quita el cierre por el solicitante. Los casos cerrados no se reabren.
- **S-04:** se quita la frase "casos recurrentes se registran como un nuevo caso referenciado", que el docente no confirmó.
- **RF-09:** el historial se muestra como línea de tiempo en el detalle del caso; no hay notas privadas.
- **RF-10:** el consolidado muestra casos abiertos, casos cerrados y fechas. Se conservó el desglose por técnico porque CA-06 de la guía pide responsables.
- **S-06:** usuarios predeterminados (seeder) por rol.
- **Cancelación (decisión del equipo, posterior a la entrevista):** se elimina el estado `Cancelado` y la cancelación por el solicitante, porque el docente no la mencionó.
- **Pendientes:** ~~las categorías (S-02) ya no se usan en el reporte.~~ *RESUELTO: S-02 retirado en `docs/requisitos.md` (RF-3).*


---

## Supuestos: confirmación

Según la guía PF-02 (Actividad 2, línea 165): "Los supuestos no confirmados deben identificarse". Esta tabla indica, para cada supuesto de `docs/requisitos.md` §5 (que no se modifica), en qué pregunta de esta entrevista se confirma, y separa los supuestos del equipo que el docente no confirmó (EQ-01..EQ-06). EQ-06 se añade el 16/11/2026, después de la aprobación de `docs/requisitos.md` (que cuenta cinco EQ).

Referencias de código a fecha de la rama `feat/002-seguridad-y-capas`.

| Id | Texto | Evidencia | Estado | Implementación (archivo:línea, función o clase) | Prueba (`backend/tests/`) |
|---|---|---|---|---|---|
| S-01 | Prioridades Baja/Media/Alta/Crítica | P6 (línea 19): "Solo etiqueta." | Confirmado por el docente | `backend/db/schema.sql:46-47` (tabla `caso`); `backend/app/esquemas/casos.py:49-50` (`Evaluacion.prioridad`) | Ninguna específica |
| S-02 | Categorías | P2 (línea 15): el reporte no pide categoría | Retirado | No aplica | No aplica |
| S-03 | Asignación manual | P3 (línea 16): "Manual." | Confirmado por el docente | `backend/app/servicios/casos.py:169-194` (`asignar_tecnico`) | Ninguna específica |
| S-04 | Casos cerrados no se reabren | P5 (línea 18): "no se puede reabrir" | Confirmado por el docente | `backend/app/servicios/casos.py:105-110` (`_validar_transicion`); `backend/db/schema.sql:128-133` (`trg_caso_cerrado_inmutable`) | Ninguna específica (el caso `Cerrado` se ejerce en `test_flujo_completo`) |
| S-05 | Todo dentro de la web, sin correo ni mensajería | Guía, alcance (línea 140) | Confirmado por la guía | Sin envío de mensajes en `backend/` | No aplica |
| S-06 | Usuarios del seeder por rol | P10 (línea 23) | Confirmado por el docente | `backend/seed.py:52` (`cargar`) | Ninguna específica |
| S-07 | Solo texto | P11 (línea 24) | Confirmado por el docente | Sin carga de archivos; `backend/app/esquemas/comun.py:7-8` (`Texto`, `TextoLargo`) | Ninguna específica |
| EQ-01 | Solo el coordinador evalúa y fija prioridad | Sin respuesta del docente | Supuesto del equipo no confirmado por el docente, implementado | `backend/app/routers/casos.py:33-41` (`evaluar_caso`); `backend/app/deps.py:50` (`Coordinador`) | `test_evaluar`, `test_solicitante_403_en_acciones_de_coordinador` |
| EQ-02 | Dependencia tomada de un catálogo | P2 pide "dependencia", no un catálogo | Supuesto del equipo no confirmado por el docente, implementado | `backend/app/servicios/casos.py:141-143` (`registrar_caso`); `backend/app/routers/catalogos.py:10-12` (`listar_dependencias`) | `test_registro_invalido_422` (dependencia inexistente (99) e inactiva), `test_catalogos` |
| EQ-03 | Fecha = día de la falla, no futura | P2 pide "fecha" sin más | Supuesto del equipo no confirmado por el docente, implementado | `backend/app/esquemas/casos.py:22,41-46` (`CasoNuevo.fecha`, `CasoNuevo._fecha_no_futura`) | `test_registro_invalido_422` (fecha futura) |
| EQ-04 | Intervención con duración | Sin respuesta del docente | Supuesto del equipo no confirmado por el docente, implementado | `backend/app/esquemas/casos.py:59` (`IntervencionNueva.duracion_min`, solo `gt=0`); `backend/db/schema.sql:93` (tabla `intervencion`) | `test_flujo_completo` (`duracion_min` 0 devuelve 422) |
| EQ-05 | Descripción de al menos 15 caracteres | P2: propuesta del equipo; el docente no la menciona | Supuesto del equipo no confirmado por el docente, implementado | `backend/app/esquemas/casos.py:23-25` (`CasoNuevo.descripcion`); `backend/db/schema.sql:39` (tabla `caso`) | `test_registro_invalido_422` (descripción corta) |
| EQ-06 | Las intervenciones solo se registran con el caso en `En atención` | Sin respuesta del docente; RN-04 solo prohíbe `Cerrado` y `schema.sql` no la impone | Supuesto del equipo no confirmado por el docente, implementado | `backend/app/servicios/casos.py:202-208` (`registrar_intervencion`) | `test_intervencion_fuera_de_atencion_400` (casos `Asignado` y `Resuelto`) |

Notas:
- Las referencias "S-0x" del resto de este documento remiten a `docs/requisitos.md` §5.
