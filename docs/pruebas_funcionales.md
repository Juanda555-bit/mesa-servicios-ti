# Pruebas funcionales (Actividad 6)

> Nota: PF-API-NN: pruebas funcionales de la API (spec 002); PF-01..PF-12 se reservan para las pruebas por la interfaz (Actividad 6).

Pruebas de la spec 002 (`specs/002-seguridad-y-capas/`): autenticación endurecida, capas y errores. Esta spec no incluye interfaz; el flujo se ejecutó de verdad contra la API real (uvicorn, puerto 8002) con SQLite sembrada (`python -m backend.seed`, datos ficticios) mediante peticiones HTTP, y se capturó Swagger (`/docs`) con Chrome DevTools. Entorno: fecha 2026-11-17, rama `feat/002-seguridad-y-capas` (cambios sin commit), `JWT_SECRET` y BD temporales de la sesión (no se publican). Las salidas completas (con el token reemplazado por `<TOKEN-OMITIDO>`) están en `evidencias/`. Las pruebas de interfaz (p. ej. el flujo completo desde la pantalla) se documentarán con la spec 003.

Usuarios del seeder (contraseña de demostración `Mesa2026*`): `coordinador@mesa.edu.co`, `tecnico1@mesa.edu.co`, `tecnico2@mesa.edu.co`, `solicitante1@mesa.edu.co`, `solicitante2@mesa.edu.co`.

| ID | Prueba | Requisito | Estado |
|---|---|---|---|
| PF-API-01 | Login correcto: token y rol | CA-03 · RF-01 | ✅ |
| PF-API-02 | Login fallido indistinguible | CA-03 · RNF-04 | ✅ |
| PF-API-03 | Token manipulado | CA-03 · RN-06 | ✅ |
| PF-API-04 | Token vencido | CA-03 · RN-06 | ✅ |
| PF-API-05 | Sin token y rol sin permiso | CA-02 · CA-06 · RN-07 | ✅ |
| PF-API-06 | Registro inválido: 422 con `detalle` y `campos` | CA-01 · RN-08 | ✅ |
| PF-API-07 | Teléfono de 20 caracteres aceptado | CA-01 · RF-02 · RN-08 | ✅ |
| PF-API-08 | Caso inexistente (404) y caso ajeno (403) | CA-03 · RN-06 | ✅ |
| PF-API-09 | Recorrido completo de un caso por la API/Swagger | CA-01..CA-06 · RN-01..RN-05 | ✅ |
| PF-API-10 | Arranque rechazado con `JWT_SECRET` corto | RF-1 (spec 002) | ✅ |

### PF-API-01 — Login correcto devuelve token y rol; el token solo contiene sub/exp
| Campo | Valor |
|---|---|
| Requisito | CA-03 · RF-01 (autenticación) |
| Precondiciones | BD sembrada; `solicitante1` activo |
| Pasos | 1. `POST /auth/login` con credenciales válidas. 2. Decodificar el token sin verificar firma. 3. `GET /auth/me` con el token. |
| Entrada | Formulario `username=solicitante1@mesa.edu.co`, `password=Mesa2026*` |
| Método y ruta | POST /auth/login · GET /auth/me |
| Resultado esperado | 200 con `access_token`, `rol=solicitante`; payload con solo `sub` y `exp`; `/auth/me` 200 |
| Resultado obtenido | 200, `rol: "solicitante"`, `nombre: "Sara Solicitante"`; claims decodificados: `['exp', 'sub']` (`sub: "4"`); `/auth/me` 200 con el usuario correcto |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-01-login-correcto.json` |

### PF-API-02 — Correo inexistente y contraseña incorrecta dan el mismo 401
| Campo | Valor |
|---|---|
| Requisito | CA-03 · RNF-04 (no revelar qué dato falló) |
| Precondiciones | BD sembrada |
| Pasos | 1. Login con correo que no existe. 2. Login con correo válido y contraseña errónea. 3. Comparar respuestas. |
| Entrada | `noexiste@mesa.edu.co` / `Mesa2026*`; `solicitante1@mesa.edu.co` / `Incorrecta123` |
| Método y ruta | POST /auth/login |
| Resultado esperado | Ambos 401 con idéntico `detalle` |
| Resultado obtenido | Ambos 401, cuerpo idéntico: `{"detalle": "Correo o contraseña incorrectos"}` |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-02-login-fallido-indistinguible.json` (`identico: true`) |

### PF-API-03 — Token manipulado devuelve 401
| Campo | Valor |
|---|---|
| Requisito | CA-03 · RN-06 (autenticación comprobada en el backend) |
| Precondiciones | Token válido de `solicitante1` (PF-API-01) |
| Pasos | `GET /casos` con: (a) firma alterada, (b) payload alterado (`sub=1`) conservando la firma original, (c) texto que no es JWT. |
| Entrada | Tres cabeceras `Authorization: Bearer ...` manipuladas |
| Método y ruta | GET /casos |
| Resultado esperado | 401 con `detalle` en español |
| Resultado obtenido | Las tres: 401 `{"detalle": "No autenticado o token inválido"}` |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-03-token-manipulado.json` |

### PF-API-04 — Token vencido devuelve 401
| Campo | Valor |
|---|---|
| Requisito | CA-03 · RN-06 |
| Precondiciones | Token con `exp` 5 minutos en el pasado, firmado con la clave de la sesión (generado fuera de la API para simular el vencimiento) |
| Pasos | `GET /casos` con ese token |
| Entrada | Token vencido de `solicitante1` |
| Método y ruta | GET /casos |
| Resultado esperado | 401 con `detalle` |
| Resultado obtenido | 401 `{"detalle": "No autenticado o token inválido"}` |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-04-token-vencido.json` |

### PF-API-05 — Sin token: 401; rol sin permiso: 403 con `detalle`
| Campo | Valor |
|---|---|
| Requisito | CA-02 · CA-06 · RN-06 · RN-07 |
| Precondiciones | Casos del seeder; sesiones de `solicitante1` y `tecnico1` |
| Pasos | 1. `GET /casos` sin token. 2. Solicitante evalúa un caso. 3. Solicitante consulta el resumen. 4. Técnico reporta un caso. 5. Solicitante con token de firma válida pero con un claim `rol=coordinador` añadido consulta el resumen. |
| Entrada | Ver archivo de evidencia (`{"prioridad":"Alta"}` y un caso válido) |
| Método y ruta | GET /casos · PATCH /casos/1/evaluacion · GET /coordinacion/resumen · POST /casos |
| Resultado esperado | 401 sin token; 403 en los demás, con `detalle`; el claim `rol` no concede permisos |
| Resultado obtenido | 401 `No autenticado o token inválido`; los cuatro restantes: 403 `{"detalle": "Su rol no permite esta acción"}` |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-05-sin-token-y-sin-permiso.json` |

### PF-API-06 — Datos inválidos: 422 con `detalle` y `campos`, sin guardar
| Campo | Valor |
|---|---|
| Requisito | CA-01 · RN-08 |
| Precondiciones | `solicitante1` autenticado; 3 casos visibles para él |
| Pasos | 1. `POST /casos` con teléfono de 21 caracteres. 2. `POST /casos` con varios campos inválidos. 3. Listar casos y comparar la cantidad. |
| Entrada | (1) teléfono de 21 dígitos. (2) placa vacía, descripción `corta`, fecha `2030-01-01`, teléfono de 21 |
| Método y ruta | POST /casos · GET /casos |
| Resultado esperado | 422 con `detalle` y `campos` (todos los campos erróneos); no se crea ningún caso |
| Resultado obtenido | (1) 422 `{"detalle": "Datos de entrada no válidos", "campos": [{"campo": "telefono", "motivo": "Debe tener como máximo 20 caracteres"}]}`. (2) 422 con 4 campos listados (`placa_equipo`, `telefono`, `fecha`, `descripcion`). Casos visibles antes y después: 3 y 3 |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-06-validacion-422.json` |

Observación menor (no es fallo): el motivo de la placa vacía dice "Debe tener al menos 1 caracteres" (concordancia de número).

### PF-API-07 — Teléfono de 20 caracteres es aceptado
| Campo | Valor |
|---|---|
| Requisito | CA-01 · RF-02 · RN-08 |
| Precondiciones | `solicitante1` autenticado |
| Pasos | 1. `POST /casos` con teléfono de exactamente 20 caracteres. 2. `GET /casos/{id}` del caso creado. |
| Entrada | Caso ficticio con `telefono` de 20 dígitos, `dependencia_id=1` |
| Método y ruta | POST /casos · GET /casos/6 |
| Resultado esperado | 201, estado `Registrado`; recuperable con el mismo teléfono |
| Resultado obtenido | 201 (id 6, estado `Registrado`, teléfono de 20 caracteres); `GET /casos/6` 200 con los mismos datos |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-07-telefono-20-aceptado.json` |

### PF-API-08 — Caso inexistente (404) y caso ajeno (403)
| Campo | Valor |
|---|---|
| Requisito | CA-03 · RN-06 |
| Precondiciones | Caso 6 de `solicitante1`; no existe el caso 999999 |
| Pasos | 1. `GET /casos/999999` como solicitante y como coordinador. 2. `solicitante2` consulta el caso 6 y su historial. |
| Entrada | Ids indicados |
| Método y ruta | GET /casos/{id} · GET /casos/{id}/historial |
| Resultado esperado | 404 controlado para inexistente; 403 para caso ajeno |
| Resultado obtenido | 404 `{"detalle": "El caso no existe"}` (ambos roles); 403 `{"detalle": "No tiene acceso a este caso"}` (detalle e historial) |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-08-caso-inexistente-y-ajeno.json` |

### PF-API-09 — Recorrido completo de un caso (reporte → cierre) por la API
| Campo | Valor |
|---|---|
| Requisito | CA-01..CA-06 · RN-01 · RN-02 · RN-03 · RN-04 · RN-05 · RN-10 |
| Precondiciones | BD sembrada; usuarios del seeder; Swagger disponible en `/docs` |
| Pasos | 1. Solicitante reporta (201, Registrado). 2. Técnico intenta resolver sin ser responsable (403). 3. Coordinador evalúa con prioridad Alta (En evaluación). 4. Coordinador asigna a `tecnico1` (Asignado). 5. Técnico inicia atención (En atención). 6. Técnico resuelve sin intervención (400). 7. Técnico registra intervención de 45 min (201). 8. Coordinador cierra en En atención (400). 9. Técnico resuelve con solución (Resuelto). 10. Coordinador cierra (Cerrado). 11. Cerrar de nuevo (400). 12. Solicitante consulta caso e historial; coordinador consulta el resumen. 13. `PUT`/`DELETE` sobre intervenciones. |
| Entrada | Caso ficticio (placa LAB-077, dependencia Laboratorio de sistemas); prioridad `Alta`; solución "Fuente de poder reemplazada y equipo probado" |
| Método y ruta | POST /casos · PATCH .../evaluacion · PUT .../tecnico · POST .../iniciar-atencion · POST .../intervenciones · POST .../resolver · POST .../cerrar · GET /casos/{id} · GET .../historial · GET /coordinacion/resumen |
| Resultado esperado | Transiciones válidas 200/201; inválidas 400 sin efecto; ajeno 403; solicitante ve la solución; historial con autor y fecha; resumen coherente; sin edición ni borrado de intervenciones |
| Resultado obtenido | Todo conforme: 201, 403, 200 (En evaluación), 200 (Asignado, Tomás Técnico), 200 (En atención), 400 `Registre al menos una intervención antes de resolver el caso`, 201, 400 `Transición no permitida: En atención → Cerrado`, 200 (Resuelto), 200 (Cerrado), 400 `El caso está cerrado y no admite cambios`. El solicitante recupera estado `Cerrado` y la solución. El historial lista cambios de estado, asignación e intervención con autor y fecha. Resumen: total 7, abiertos 5, cerrados 2, por estado y por técnico. `PUT`/`DELETE` sobre intervenciones: 404 `Recurso no encontrado` (no existen esas rutas) |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-09-flujo-completo-caso.json`, `evidencias/PF-API-09-swagger-docs.png` (Swagger con las rutas) |

### PF-API-10 — Arranque rechazado con `JWT_SECRET` corto
| Campo | Valor |
|---|---|
| Requisito | RF-1 de la spec 002 (secreto obligatorio, mínimo 32 caracteres) |
| Precondiciones | Sin `.env`; variable de entorno `JWT_SECRET` de 5 caracteres |
| Pasos | Arrancar uvicorn con esa variable |
| Entrada | `JWT_SECRET` de 5 caracteres |
| Método y ruta | `python -m uvicorn backend.app.main:app --port 8003` |
| Resultado esperado | El proceso termina con mensaje en español; no queda escuchando |
| Resultado obtenido | Terminó con código 1: "Configuración no válida: JWT_SECRET falta, tiene menos de 32 caracteres o es el valor de ejemplo. Genere una con: python -c ..." |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-API-10-arranque-secreto-corto.txt` |
