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

Por completar (Actividad 3: `docs/diseno.md`).

## 5. Configuración del entorno

Por completar.

## 6. Servicios web implementados

| Método | Ruta | Descripción | Requisito relacionado |
|---|---|---|---|
| Por completar | Por completar | Por completar | Por completar |

## 7. Pruebas de API e integración y evidencias de funcionamiento

Por completar (evidencias en `evidencias/`).

## 8. Control de versiones

- El trabajo se integra mediante ramas y *pull requests* hacia `main`, con commits descriptivos (`docs:`, `feat:`, `fix:`, `chore:`, `test:`).
- Cada pull request documenta propósito, cambios, pruebas efectuadas y requisitos asociados.
- Resumen verificable de aportes por integrante: por completar.

## 9. Conclusiones y limitaciones

Por completar.
