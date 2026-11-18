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
| PF-12 | Integración interfaz–API–base de datos: flujo completo desde la interfaz | CA-01..CA-06 · RF-18 · RF-21 (spec 003) | ✅ |

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

Observación menor (no es fallo): el motivo de la placa vacía dice "Debe tener al menos 1 caracteres" (concordancia de número); corregido en la spec 003 (RF-20).

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

### PF-12 — Integración interfaz–API–base de datos (flujo completo desde la interfaz)
| Campo | Valor |
|---|---|
| Requisito | CA-01..CA-06 · RF-18 y RF-21 (spec 003) · RN-01 · RN-02 · RN-03 · RN-06 · RN-07 · RN-10 · Actividad 6, prueba 12 |
| Precondiciones | BD SQLite temporal recién sembrada (`python -m backend.seed`, datos ficticios, 5 casos, 1 cerrado); API en `http://localhost:8000` (uvicorn) y Vite en `http://localhost:5173` (`npm run dev`); `JWT_SECRET` y `DATABASE_URL` por variables de entorno de la sesión; Chrome con DevTools; sin Swagger; contraseña de demostración `Mesa2026*`. Fecha de la ejecución: 18/11/2026; rama `local/003-trabajo`. |
| Pasos | 1. Iniciar sesión como `solicitante1`, abrir "Reportar caso", llenar el formulario y enviarlo. 2. Cerrar sesión; entrar como `coordinador`, ver el tablero inicial, abrir el caso #6, evaluarlo con prioridad Alta y asignarlo a Teresa Técnica. 3. Cerrar sesión; entrar como `tecnico2` (Teresa Técnica), abrir el caso #6, "Iniciar atención", registrar una intervención de 45 min y resolver con solución. 4. Cerrar sesión; entrar como `coordinador` y "Cerrar caso" (confirmando el aviso). 5. Ver el tablero: el caso #6 debe estar entre los cerrados. 6. Entrar como `solicitante1`, abrir "Mis casos" y el caso #6: estado, solución y línea de tiempo. 7. Revisar en la pestaña Red cada llamada y su código. 8. Detener y volver a arrancar la API con la misma base, iniciar sesión como `solicitante1` y comprobar que el caso #6 sigue `Cerrado`. |
| Entrada | Reporte: placa `PF12-001`, usuario `Sara Solicitante`, teléfono `3001234567`, fecha de la falla `17/11/2026`, dependencia `Laboratorio de sistemas`, descripción "El equipo no enciende después de un corte de energía en el laboratorio." · Evaluación: prioridad `Alta` · Asignación: `Teresa Técnica` · Intervención: "Se revisó la fuente de poder y se encontró el fusible quemado.", 45 min · Solución: "Fusible de la fuente de poder reemplazado y equipo probado." |
| Método y ruta (código HTTP obtenido) | `POST /auth/login` (200, cada rol) · `GET /dependencias` (200) · `POST /casos` (**201**) · `GET /coordinacion/resumen` (200) · `GET /casos`, `GET /casos/6`, `GET /casos/6/historial` (200) · `PATCH /casos/6/evaluacion` (200) · `GET /tecnicos` (200) · `PUT /casos/6/tecnico` (200) · `POST /casos/6/iniciar-atencion` (200) · `POST /casos/6/intervenciones` (**201**) · `POST /casos/6/resolver` (200) · `POST /casos/6/cerrar` (200) |
| Resultado esperado | Cada acción de la interfaz llama a la API real y recibe 200/201; el caso avanza Registrado → En evaluación → Asignado → En atención → Resuelto → Cerrado; cada rol ve solo sus pantallas y acciones; el solicitante ve la solución y la línea de tiempo completa; el tablero lo cuenta entre los cerrados; el caso persiste tras reiniciar la API. |
| Resultado obtenido | Conforme en los 8 pasos. (1) Mensaje "Caso #6 registrado (estado Registrado)"; `POST /casos` 201. (2) Tablero inicial: total 6, abiertos 5, cerrados 1, sin asignar 3; evaluación → "En evaluación", prioridad Alta; asignación → "Asignado", responsable Teresa Técnica. (3) La técnica ve el caso #6 en "Mis casos asignados"; "Atención iniciada" (En atención); "Intervención registrada" (201); resuelto con la solución escrita. (4) Cierre con aviso de confirmación; estado "Cerrado". (5) Tablero final: total 6, abiertos 4, cerrados 2, sin asignar 2; el caso #6 aparece entre los cerrados (técnica Teresa Técnica, cierre 10:16). (6) El solicitante ve "Caso #6 Cerrado", la solución y 8 eventos en la línea de tiempo, cada uno con autor y fecha: reporte, evaluación, asignación, cambio a Asignado, En atención, intervención (45 min), Resuelto y Cerrado. (7) Todas las peticiones fueron a `http://localhost:8000`, con 200/201; el encabezado `Authorization` no aparece en las capturas. (8) Tras reiniciar la API, el caso #6 sigue `Cerrado` (con un nuevo `JWT_SECRET`, la sesión anterior dio 401 controlado "No autenticado o token inválido" y se pidió iniciar sesión). |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-12-01-login.png` (formulario de inicio de sesión) · `PF-12-02-login-solicitante.png` (sesión del solicitante) · `PF-12-03-reporte-formulario.png` · `PF-12-04-reporte-registrado.png` · `PF-12-05-login-coordinador-tablero-inicial.png` (sesión del coordinador y tablero inicial) · `PF-12-06-evaluacion.png` · `PF-12-07-asignacion.png` · `PF-12-08-login-tecnico-lista.png` (sesión del técnico) · `PF-12-09-intervencion.png` · `PF-12-10-resolucion.png` · `PF-12-11-cierre.png` · `PF-12-12a-solicitante-mis-casos.png` · `PF-12-12-solicitante-resultado.png` (solución y línea de tiempo) · `PF-12-13-tablero-final.png` · `PF-12-14-red-peticiones.jpeg` · `PF-12-15-persistencia-tras-reinicio.png` |

Observaciones de PF-12 (no son fallos): (a) en la pestaña Red, cada primera carga de una pantalla aparece como `net::ERR_ABORTED` seguida de la misma petición con 200: es la doble ejecución del efecto de React en modo desarrollo (StrictMode) que cancela la primera; no ocurre en la compilación de producción. (b) `PF-12-14-red-peticiones.jpeg` es una captura real del panel Network de Chrome DevTools (filtro Fetch/XHR), tomada en una sesión distinta a la del caso #6: sesión del coordinador con el caso #1 evaluado (prioridad Alta, estado "En evaluación"). Muestra login, resumen, casos, 5, historial, 1, evaluacion y tecnicos, todas con 200 (varias filas "(canceled)" van seguidas de la misma petición con 200); no se ve ningún token ni encabezado `Authorization`. (c) La fecha del formulario se asignó mediante script porque el control nativo de fecha no admite el relleno automático; el valor llegó a la API como `2026-11-17`. (d) El seeder no trae casos Resueltos, por eso se recorrió un caso nuevo (#6) de principio a fin.
