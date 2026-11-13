# Registro de entrevista con el cliente (docente)

- **Fecha:** Pendiente por definir
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
- **Pendientes:** las categorías (S-02) ya no se usan en el reporte.
