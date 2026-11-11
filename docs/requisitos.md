# Requisitos – Gestión de Solicitudes de Servicio (Mesa de Servicios TI)

## Actores
- **Solicitante** (docente/administrativo): reporta y consulta sus casos.
- **Técnico**: evalúa y atiende los casos que le asignan.
- **Coordinador**: asigna, supervisa y consulta el consolidado.

## Requisitos funcionales
| ID | Requisito | CA |
|---|---|---|
| RF-01 | Autenticación y control de acceso por rol | todos |
| RF-02 | El solicitante reporta un incidente o solicitud (tipo, categoría, descripción, prioridad) | CA-01 |
| RF-03 | El solicitante consulta sus casos, estado y responsable | CA-03 |
| RF-04 | Técnico/coordinador evalúa y clasifica el caso | CA-02 |
| RF-05 | El coordinador asigna un técnico responsable | CA-02, CA-03 |
| RF-06 | El técnico registra intervenciones (fecha, autor, descripción) | CA-04 |
| RF-07 | Cambio de estado según el flujo permitido | CA-03 |
| RF-08 | El técnico cierra el caso con resultado/solución | CA-05 |
| RF-09 | Consulta del historial de intervenciones de un caso | CA-04 |
| RF-10 | Resumen consolidado: casos por estado y por responsable | CA-06 |

## Reglas de negocio
- RN-01 Flujo de estados: Registrado → En evaluación → Asignado → En atención → Resuelto → Cerrado (Cancelado desde Registrado).
- RN-02 Un caso solo tiene un responsable a la vez; solo ese técnico registra intervenciones.
- RN-03 No se cierra un caso sin resultado y sin al menos una intervención.
- RN-04 Un caso cerrado no admite nuevas intervenciones.
- RN-05 Las intervenciones no se editan ni se eliminan (trazabilidad).
- RN-06 El solicitante solo ve sus propios casos.
- RN-07 Solo el coordinador asigna/reasigna y ve el consolidado.
- RN-08 Descripción y categoría obligatorias al reportar.

## Requisitos no funcionales
- RNF-01 Validación de datos en el servidor.
- RNF-02 Contraseñas con hash; sin secretos en el repo (`.env` + `.env.example`).
- RNF-03 Persistencia en BD relacional con llaves foráneas.
- RNF-04 Errores controlados sin revelar info sensible.
- RNF-05 API REST documentada (OpenAPI/Swagger).
- RNF-06 Interfaz usable en navegador de escritorio.
- RNF-07 Instalación reproducible vía README.

## Supuestos (por confirmar con el profe)
- S-01 Prioridades: Baja/Media/Alta/Crítica.
- S-02 Categorías: hardware, software, conectividad, accesos.
- S-03 La asignación la hace manualmente el coordinador.
- S-04 Un caso cerrado no se reabre.
- S-05 Sin notificaciones por correo/WhatsApp.