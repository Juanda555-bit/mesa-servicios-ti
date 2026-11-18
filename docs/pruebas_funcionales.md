# Pruebas funcionales (Actividad 6)

> Nota: PF-API-NN son las pruebas funcionales de la API (spec 002); PF-01..PF-12 son las pruebas por la interfaz y la API de la Actividad 6 (PF-12 de la spec 003; PF-01..PF-11 de la spec 004).

Pruebas de la spec 002 (`specs/002-seguridad-y-capas/`): autenticación endurecida, capas y errores. Esta spec no incluye interfaz; el flujo se ejecutó de verdad contra la API real (uvicorn, puerto 8002) con SQLite sembrada (`python -m backend.seed`, datos ficticios) mediante peticiones HTTP, y se capturó Swagger (`/docs`) con Chrome DevTools. Entorno: fecha 2026-11-17, rama `feat/002-seguridad-y-capas` (cambios sin commit), `JWT_SECRET` y BD temporales de la sesión (no se publican). Las salidas completas (con el token reemplazado por `<TOKEN-OMITIDO>`) están en `evidencias/`. Las pruebas por la interfaz se documentan más abajo: PF-12 (spec 003, flujo completo) y PF-01..PF-11 (spec 004).

Pruebas de la spec 004 (`specs/004-pruebas-y-entrega/`): PF-01..PF-11 se ejecutaron seguidas el 18/11/2026 en el PC del equipo (compartido por Simón y Juan), contra la API real (uvicorn, puerto 8000) y la interfaz (Vite, puerto 5173), sobre una única base SQLite sembrada una sola vez con `python -m backend.seed` (datos ficticios), sin resembrar entre pruebas: cada PF parte del estado que dejó la anterior. El código probado es `main` `58c80e0`; la rama `feat/004-pruebas-y-entrega` solo añade documentación y evidencias. Canales: interfaz siempre que permita provocar la situación; API (peticiones HTTP) solo para lo que la interfaz no permite (por ejemplo el 404, los 403 y el segundo cierre), y cada PF indica el motivo. Las capturas de la pestaña Red las hizo el usuario (`PF-02-red-422.png`, `PF-09-red-400.png`, `PF-10-red.png`) y solo muestran la respuesta, sin token ni cabeceras; la PF-03 no tiene captura de Red (el caso 3 cambió en la PF-09 y ya no se podía repetir). Responsable de las PF-01..PF-11: Simón Herrera (las redacta y las sube). Todas están aprobadas.

Usuarios del seeder (contraseña de demostración `Mesa2026*`): `coordinador@mesa.edu.co`, `tecnico1@mesa.edu.co`, `tecnico2@mesa.edu.co`, `solicitante1@mesa.edu.co`, `solicitante2@mesa.edu.co`.

| ID | Prueba | Requisito | Estado |
|---|---|---|---|
| PF-01 | Registro válido de caso | CA-01 · RF-02 · RN-08 | ✅ |
| PF-02 | Registro con datos inválidos (422) | CA-01 · RN-08 | ✅ |
| PF-03 | Consulta de caso existente | CA-03 · RF-03 | ✅ |
| PF-04 | Consulta de caso inexistente (404) | RF-03 · RNF-04 | ✅ |
| PF-05 | Gestión por personal autorizado (evaluar y asignar) | CA-02 · RN-07 · RN-09 · RN-10 | ✅ |
| PF-06 | Gestión por actor no autorizado (403) | CA-02 · RN-02 · RN-06 · RN-07 | ✅ |
| PF-07 | Consulta de estado y responsable tras reasignar | CA-03 · RN-02 · RN-10 | ✅ |
| PF-08 | Historial de intervenciones | CA-04 · RN-05 | ✅ |
| PF-09 | Cierre de caso y consulta de resultado (400 en transiciones inválidas) | CA-05 · RN-01 · RN-03 · RN-04 | ✅ |
| PF-10 | Consulta consolidada de coordinación (403 a otros roles) | CA-06 · RN-07 | ✅ |
| PF-11 | Persistencia e integridad de relaciones tras reiniciar la API | CA-01 a CA-06 · RNF-03 | ✅ |
| PF-12 | Integración interfaz–API–base de datos: flujo completo | CA-01 a CA-06 · RF-18 · RF-21 (spec 003) | ✅ |
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

### PF-01 — Registro válido de caso
| Campo | Valor |
|---|---|
| Requisito | CA-01 · RF-02 · RN-08 · US-02 (CA-US02.1) · Actividad 6, prueba 1 |
| Precondiciones | Base SQLite recién sembrada con `python -m backend.seed` (casos 1..5; sin volver a sembrar durante la sesión); API en `http://localhost:8000` y Vite en `http://localhost:5173`; `solicitante1` (Sara Solicitante) con 3 casos (1, 3 y 5). Partida de RF-1b: casos 1..5. |
| Pasos | 1. Iniciar sesión como `solicitante1` y abrir "Reportar caso". 2. Llenar el formulario con los datos de entrada y enviarlo. 3. Comprobar el aviso de registro. 4. Abrir "Mis casos" y el detalle del caso creado. 5. En la pestaña Red, revisar el método, la ruta y el código. |
| Entrada | Placa `PC-PF01-0001`; usuario `Usuario Prueba Uno`; teléfono `3001234567`; fecha de la falla `2026-11-17`; dependencia `Biblioteca` (id 1); descripción "El equipo no enciende tras el corte de energia de ayer." |
| Canal | Interfaz (no se necesita la API: el formulario permite provocar la situación). |
| Método y ruta (código HTTP obtenido) | `POST /casos` (**201**) · `GET /casos` (200) · `GET /casos/6` (200) |
| Resultado esperado | 201; el caso queda `Registrado`, sin prioridad ni técnico; es recuperable en "Mis casos" y en su detalle con los mismos datos enviados; el caso nuevo es el id 6. |
| Resultado obtenido | `POST /casos` 201. Caso id real = 6 (el previsto), estado `Registrado`, prioridad y técnico vacíos. Aviso "Caso #6 registrado (estado Registrado)" comprobado en la interfaz, sin captura propia (el screenshot expiró y no se repitió para no crear otro caso). "Mis casos" muestra #6, #5, #3 y #1. El detalle del #6 muestra los mismos datos enviados y la línea de tiempo "Inicio → Registrado" por Sara Solicitante. Persistencia tras reiniciar la API: el caso 6 conserva los datos del alta (comprobado en la PF-11; no se reinició la API dentro de esta PF). |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-01-01-formulario.png` (formulario lleno) · `evidencias/PF-01-03-mis-casos.png` (lista con el caso #6) · `evidencias/PF-01-04-detalle-caso-6.png` (detalle y línea de tiempo). No existe `PF-01-02`: no hay captura del aviso "Caso #6 registrado" (el screenshot del MCP expiró y no se repitió el envío para no crear otro caso); es una omisión justificada (D-10). El registro se verificó por snapshot y lo respaldan PF-01-03, PF-01-04 y la consulta del caso 6. Complementaria: PF-API-07 (registro por la API). |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras (sin "Curl" ni "Authorize" de Swagger, sin "Headers" de Red ni `sessionStorage`). |

### PF-02 — Registro con datos inválidos
| Campo | Valor |
|---|---|
| Requisito | CA-01 · RN-08 · RF-02 · US-02 (CA-US02.2) · Actividad 6, prueba 2 |
| Precondiciones | Estado que deja la PF-01: `solicitante1` con 4 casos (6, 5, 3 y 1); API y Vite en marcha sobre la misma base, sin resembrar. |
| Pasos | 1. Anotar los casos de `solicitante1` (antes). 2. Interfaz: en "Reportar caso", dejar la placa con 5 espacios y la descripción con 15 espacios, el resto válido, y enviar; revisar los motivos junto a cada campo y la respuesta `422` en la pestaña Red (Response). 3. API: `POST /casos` con teléfono de 21 caracteres; `POST /casos` con fecha futura. 4. Anotar de nuevo los casos de `solicitante1` (después). |
| Entrada | Interfaz: placa `     ` (5 espacios); descripción de 15 espacios; usuario `Usuario Prueba Dos`; teléfono `3009876543`; fecha `2026-11-17`; dependencia `Secretaría` (id 5). API: teléfono de 21 dígitos; fecha `2027-01-01` (resto de campos válidos). |
| Canal y motivo | Interfaz para espacios en blanco (el navegador permite enviarlos y los rechaza el backend, que recorta los espacios). API (petición HTTP con un script de Python, no con Swagger) para teléfono de más de 20 caracteres y fecha futura: el formulario los bloquea antes de enviar (`maxLength=20` en teléfono y `max=hoy` en fecha), así que por la interfaz nunca llegan al backend. |
| Método y ruta (código HTTP obtenido) | `POST /casos` interfaz (**422**) · `POST /casos` teléfono de 21 (**422**) · `POST /casos` fecha futura (**422**) · `GET /casos` antes y después (200) |
| Resultado esperado | 422 con `detalle` y `campos`, sin crear caso; la interfaz muestra cada motivo junto a su campo; `solicitante1` sigue con 4 casos. |
| Resultado obtenido | Interfaz: 422 `{"detalle": "Datos de entrada no válidos", "campos": [placa_equipo: "Debe tener al menos 1 carácter", descripcion: "Debe tener al menos 15 caracteres"]}`; la interfaz muestra cada motivo junto al campo y el aviso "Datos de entrada no válidos" (en la captura los campos placa y descripción se ven vacíos porque solo contienen espacios). API: teléfono de 21 → 422 `campos[telefono: "Debe tener como máximo 20 caracteres"]`; fecha `2027-01-01` → 422 `campos[fecha: "La fecha de la falla no puede ser futura"]`. Casos de `solicitante1` antes: 4 (6, 5, 3, 1); después: 4 (6, 5, 3, 1). No se creó ningún caso. |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-02-01-interfaz-422.png` (motivos en la interfaz) · `evidencias/PF-02-red-422.png` (pestaña Red del usuario: `POST /casos` 422, Response con `placa_equipo` y `descripcion`) · `evidencias/PF-02-06-interfaz-red-422-respuesta.json` (cuerpo de la respuesta 422 de la interfaz) · `evidencias/PF-02-03-api-422-telefono-21.json` · `evidencias/PF-02-04-api-422-fecha-futura.json` · `evidencias/PF-02-02-mis-casos-despues.png` (misma imagen, con el mismo contenido, que `PF-01-03`) · `evidencias/PF-02-05-api-casos-solicitante1-antes-despues.json` (el "después" lo demuestra este archivo: 4 casos antes y 4 después). Complementarias: PF-API-06 y PF-API-07. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras. En `PF-02-red-422.png` solo se muestra la respuesta (Response), sin "Headers" de Red; ninguna captura muestra "Curl", "Authorize" ni `sessionStorage`. |

### PF-03 — Consulta de caso existente
| Campo | Valor |
|---|---|
| Requisito | CA-03 · RF-03 · US-03 (CA-US03.2) · Actividad 6, prueba 3 |
| Precondiciones | Caso 3 (`Asignado` a tecnico1, con prioridad Alta, de `solicitante1`) tal como lo deja el seeder y la PF-02 (sin cambios); sesión de `solicitante1`. |
| Pasos | 1. Iniciar sesión como `solicitante1` y abrir el detalle del caso #3 desde "Mis casos". 2. Comparar lo mostrado con la respuesta de la API `GET /casos/3`. 3. Revisar en la pestaña Red `GET /casos/3` y `GET /casos/3/historial`. |
| Entrada | Caso #3 (placa `LAB-102`). |
| Canal | Interfaz y API (`GET /casos/3` con el token de `solicitante1`, para comparar los valores). |
| Método y ruta (código HTTP obtenido) | `GET /casos/3` (**200**) · `GET /casos/3/historial` (200) |
| Resultado esperado | 200; la interfaz muestra datos del reporte, estado, prioridad y responsable iguales a los de la respuesta de la API. |
| Resultado obtenido | La interfaz y la API coinciden: placa `LAB-102`, dependencia Laboratorio de sistemas, usuario Sara Solicitante (Pedro Díaz, 3001234567), fecha 16/11/2026, estado `Asignado`, prioridad Alta, responsable Tomás Técnico (tecnico1, `tecnico_id` 2), descripción "Tres equipos del laboratorio sin internet". Historial: Registrado, En evaluación (Prioridad: Alta), Asignado y Asignación a Tomás Técnico. |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-03-01-detalle-caso-3.png` (detalle en la interfaz) · `evidencias/PF-03-02-api-get-caso-3.json` (respuesta de la API). Observación: no hay captura de la pestaña Red (`PF-03-red.png`) por decisión del usuario, porque el caso 3 cambió a `En atención` en la sesión (PF-09) y ya no se podía repetir con el mismo estado; la prueba se apoya en las dos evidencias anteriores, tomadas en su momento. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras (sin "Curl", "Authorize", "Headers" de Red ni `sessionStorage`). |

### PF-04 — Consulta de caso inexistente
| Campo | Valor |
|---|---|
| Requisito | RF-03 · RNF-04 · US-03 (CA-US03.3) · Actividad 6, prueba 4 |
| Precondiciones | Sesión de `solicitante1`; no existe el caso 9999; los casos 1..6 no cambian. |
| Pasos | `GET /casos/9999` con el token de `solicitante1` y revisar el código y el cuerpo. |
| Entrada | Identificador `9999`. |
| Canal y motivo | API (petición HTTP): la interfaz no permite pedir un id arbitrario porque se navega por estado, sin URL por caso. |
| Método y ruta (código HTTP obtenido) | `GET /casos/9999` (**404**) |
| Resultado esperado | 404 con `{"detalle": "El caso no existe"}`, sin trazas. |
| Resultado obtenido | 404, cuerpo `{"detalle": "El caso no existe"}`, sin traza. |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-04-01-api-get-caso-9999.json`. Complementaria: PF-API-08. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Sin capturas de imagen (la evidencia es un `.json` sin token). |

### PF-05 — Gestión del caso por personal autorizado (evaluar y asignar)
| Campo | Valor |
|---|---|
| Requisito | CA-02 · RF-04 · RF-05 · RN-07 · RN-09 · RN-10 · US-04 · US-05 · Actividad 6, prueba 5 |
| Precondiciones | Caso 6 `Registrado` de `solicitante1` (lo dejó la PF-01); sesión de `coordinador`; técnicos `tecnico1` (Tomás Técnico) y `tecnico2` (Teresa Técnica) activos; API y Vite en marcha sobre la misma base, sin resembrar. |
| Pasos | 1. Iniciar sesión como `coordinador` y abrir el detalle del caso 6. 2. Evaluarlo con prioridad Alta. 3. Asignarlo a `tecnico1` (Tomás Técnico). 4. Revisar la línea de tiempo y, en la pestaña Red, el método, la ruta y el código de cada acción. |
| Entrada | Caso 6; prioridad `Alta`; técnico `tecnico1` (Tomás Técnico). |
| Canal | Interfaz (no se necesita la API: la interfaz ofrece las dos acciones al coordinador). |
| Método y ruta (código HTTP obtenido) | `PATCH /casos/6/evaluacion` (**200**) · `PUT /casos/6/tecnico` (**200**) |
| Resultado esperado | El caso pasa `Registrado` → `En evaluación` → `Asignado`, con prioridad Alta y Tomás Técnico como responsable; la línea de tiempo registra cada cambio con autor y fecha. |
| Resultado obtenido | `PATCH .../evaluacion` 200 (prioridad Alta; `Registrado` → `En evaluación`) y `PUT .../tecnico` 200 (Tomás Técnico; `En evaluación` → `Asignado`). El caso real es el 6 (el previsto). La línea de tiempo muestra la evaluación, la asignación y los cambios de estado con autor Carla Coordinadora y su fecha. |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-05-01-caso-6-asignado.png` (detalle del caso 6 `Asignado` con su línea de tiempo). El "antes" (caso 6 `Registrado`) es `evidencias/PF-01-04-detalle-caso-6.png`. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras (sin "Curl", "Authorize", "Headers" de Red ni `sessionStorage`). |

### PF-06 — Gestión del caso por un actor no autorizado
| Campo | Valor |
|---|---|
| Requisito | CA-02 · RN-02 · RN-06 · RN-07 · US-04 · US-05 · Actividad 6, prueba 6 |
| Precondiciones | Estado que deja la PF-05: caso 6 `Asignado` a `tecnico1`; caso 4 de `solicitante2`; sesiones de `solicitante1` y `tecnico2` (que no es responsable del caso 6 en este momento). |
| Pasos | 1. Interfaz: `solicitante1` abre su caso 6 y comprueba que no hay formularios ni botones para evaluar, asignar ni cerrar. 2. API: `solicitante1` intenta evaluar, asignar y cerrar el caso 6; `tecnico2` (no responsable) intenta iniciar la atención y registrar una intervención en el caso 6; `solicitante1` consulta el caso 4 (ajeno) y su historial. 3. Comparar el estado y el historial de los casos 4 y 6 antes y después. |
| Entrada | Caso 6 y caso 4; cuerpos válidos de cada acción (prioridad Alta, asignación a un técnico, intervención con descripción y duración). |
| Canal y motivo | Interfaz para comprobar que el solicitante no ve las acciones. API para los `403`: la interfaz no ofrece esas acciones al rol, así que no se pueden provocar desde ella. |
| Método y ruta (código HTTP obtenido) | `PATCH /casos/6/evaluacion` (**403**) · `PUT /casos/6/tecnico` (**403**) · `POST /casos/6/cerrar` (**403**) · `POST /casos/6/iniciar-atencion` con `tecnico2` (**403**) · `POST /casos/6/intervenciones` con `tecnico2` (**403**) · `GET /casos/4` con `solicitante1` (**403**) · `GET /casos/4/historial` (**403**) |
| Resultado esperado | 403 con `detalle` en español en todos los intentos y ningún cambio en los casos 4 y 6; la interfaz no muestra al solicitante las acciones de coordinación. |
| Resultado obtenido | Los siete intentos respondieron 403, con `detalle` "Su rol no permite esta acción" o "No tiene acceso a este caso". Los casos 4 y 6 quedaron sin cambios (eventos de historial: 7 y 4 antes y después). El solicitante no ve formularios ni botones de evaluar, asignar o cerrar. Una primera corrida del script usó un nombre de campo erróneo en la intervención (422); se repitió con el campo correcto (403) y el JSON guardado es el de la repetición. |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-06-01-api-403-no-autorizados.json` · `evidencias/PF-06-02-solicitante-sin-acciones.png`. Complementarias: PF-API-05 y PF-API-08. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras (sin "Curl", "Authorize", "Headers" de Red ni `sessionStorage`). Los `.json` y `.txt` no contienen token. |

### PF-07 — Consulta de estado y responsable tras reasignar
| Campo | Valor |
|---|---|
| Requisito | CA-03 · RF-05 · RF-07 · RN-02 · RN-10 · US-05 · US-07 · Actividad 6, prueba 7 |
| Precondiciones | Estado que deja la PF-06: caso 6 `Asignado` a `tecnico1` (Tomás Técnico); `tecnico1` con el caso 3 asignado; sesiones de `coordinador`, `tecnico1` y `tecnico2`. |
| Pasos | 1. `coordinador` reasigna el caso 6 a `tecnico2` (Teresa Técnica). 2. `tecnico2` abre el caso y pulsa "Iniciar atención". 3. Revisar la línea de tiempo. 4. Iniciar sesión como `tecnico1` y abrir "Mis casos asignados". 5. API: `tecnico1` consulta `GET /casos/6`. |
| Entrada | Caso 6; nuevo responsable `tecnico2` (Teresa Técnica). |
| Canal | Interfaz para la reasignación, el inicio de atención y las listas; API para comprobar que el responsable anterior ya no accede al caso. |
| Método y ruta (código HTTP obtenido) | `PUT /casos/6/tecnico` (**200**) · `POST /casos/6/iniciar-atencion` (**200**) · `GET /casos` de `tecnico1` (200) · `GET /casos/6` con `tecnico1` (**403**) |
| Resultado esperado | La reasignación no cambia el estado (`Asignado`) y queda en el historial con el responsable anterior; Teresa Técnica inicia la atención (`En atención`); la lista de Tomás Técnico ya no incluye el caso 6; solo hay un responsable activo. |
| Resultado obtenido | `PUT .../tecnico` 200 sin cambio de estado (`Asignado`); `POST .../iniciar-atencion` 200 (`En atención`). La línea de tiempo muestra "Reasignación: Responsable: Teresa Técnica (antes: Tomás Técnico)" y "Asignado → En atención" por Teresa Técnica. "Mis casos asignados" de `tecnico1` solo muestra el caso 3. `GET /casos/6` con `tecnico1` → 403. |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-07-01-caso-6-reasignado-en-atencion.png` (tomada con la página al 60 % de zoom para ver la línea de tiempo completa; se tomó después de la PF-08: muestra las 2 intervenciones y el aviso "Intervención registrada"; es la misma imagen que `PF-08-01`) · `evidencias/PF-07-02-tecnico1-lista-sin-caso-6.png` · `evidencias/PF-07-03-api-caso6-historial-y-tecnico1.json`. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras (sin "Curl", "Authorize", "Headers" de Red ni `sessionStorage`). Los `.json` y `.txt` no contienen token. |

### PF-08 — Historial de intervenciones
| Campo | Valor |
|---|---|
| Requisito | CA-04 · RF-06 · RF-09 · RN-02 · RN-05 · US-06 · US-09 · Actividad 6, prueba 8 |
| Precondiciones | Estado que deja la PF-07: caso 6 `En atención` con `tecnico2` (Teresa Técnica) como responsable y sin intervenciones; el caso 4 tiene una intervención sembrada ("Se revisa la configuración de la cuenta", 30 min). |
| Pasos | 1. Iniciar sesión como `tecnico2` y abrir el caso 6. 2. Registrar dos intervenciones con descripción y duración. 3. Revisar la línea de tiempo (orden, autor, fecha, duración; ausencia de botones para editar o borrar). 4. API: comparar el historial del caso 6 con el del caso 4. |
| Entrada | Intervención 1: "Se revisa la fuente de poder del equipo.", 30 min. Intervención 2: "Se reemplaza la fuente de poder y se prueba el arranque.", 45 min. |
| Canal | Interfaz para registrar y ver; API para comparar el historial con el de otro caso. |
| Método y ruta (código HTTP obtenido) | `POST /casos/6/intervenciones` (**201**, dos veces) · `GET /casos/6/historial` (200) · `GET /casos/4/historial` (200) |
| Resultado esperado | 201 en cada registro; las intervenciones aparecen en orden cronológico con autor, fecha y duración, sin edición ni borrado; el caso 4 no recibe ninguna de las dos. |
| Resultado obtenido | Dos `POST` con 201. Las dos intervenciones aparecen en orden cronológico con autor Teresa Técnica, fecha y duración; no hay botones de editar ni borrar. El historial del caso 4 conserva solo su intervención sembrada: ninguna de las dos nuevas. |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-08-01-caso-6-intervenciones.png` (misma imagen, al 60 % de zoom, que `PF-07-01`) · `evidencias/PF-08-02-api-historial-caso6-vs-caso4.json`. Omisión justificada (D-10): no se recapturó la comparación con el caso 4 (que conserva solo su intervención sembrada); se hizo por la API en `PF-08-02-api-historial-caso6-vs-caso4.json`. Complementaria: PF-API-09. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras (sin "Curl", "Authorize", "Headers" de Red ni `sessionStorage`). Los `.json` y `.txt` no contienen token. |

### PF-09 — Cierre de caso y consulta de resultado
| Campo | Valor |
|---|---|
| Requisito | CA-05 · RF-08 · RN-01 · RN-03 · RN-04 · US-08 (CA-US08.1..CA-US08.4) · Actividad 6, prueba 9 |
| Precondiciones | Estado que dejan las PF-01..PF-08 en la misma base: caso 6 `En atención` (tecnico2) con 2 intervenciones; caso 3 `Asignado` a tecnico1 sin intervenciones. |
| Pasos | 1. Caso 6: tecnico2 "Resolver" con solución; coordinador "Cerrar caso" (aceptando el aviso); `solicitante1` abre el caso 6. 2. Caso 3: tecnico1 "Iniciar atención" y "Resolver" con solución sin registrar intervención; revisar el `400` en la interfaz y en la pestaña Red (Response). 3. API: el coordinador cierra de nuevo el caso 6. |
| Entrada | Caso 6: solución "Se reemplazó la fuente de poder; el equipo enciende y opera con normalidad." Caso 3: solución con texto y sin intervenciones. Segundo cierre del caso 6 por el coordinador. |
| Canal y motivo | Interfaz para el cierre del caso 6 y para "resolver sin intervención" (caso 3), porque el formulario de resolver se ofrece en `En atención` aunque no haya intervenciones. API para "volver a cerrar" el caso 6: la interfaz no ofrece acciones sobre un caso `Cerrado`. |
| Método y ruta (código HTTP obtenido) | `POST /casos/6/resolver` (200) · `POST /casos/6/cerrar` (200) · `POST /casos/3/iniciar-atencion` (200) · `POST /casos/3/resolver` (**400**) · `POST /casos/6/cerrar` por la API (**400**) |
| Resultado esperado | El caso 6 queda `Cerrado` y el solicitante ve la solución y la finalización; resolver sin intervención → 400; volver a cerrar → 400; el caso 3 sigue `En atención` y el caso 6 sigue `Cerrado`, ambos sin cambios. |
| Resultado obtenido | Caso 6: `Resuelto` (200) y `Cerrado` (200); `solicitante1` ve estado `Cerrado`, la solución, Resuelto 12:51 y Cerrado 12:52. Caso 3: iniciar atención 200; resolver sin intervención → 400 `{"detalle": "Registre al menos una intervención antes de resolver el caso"}`; el caso 3 queda `En atención` sin intervenciones. API: segundo cierre del caso 6 → 400 `{"detalle": "El caso está cerrado y no admite cambios"}`; el caso 6 quedó con 10 eventos de historial antes y después. |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-09-02-solicitante-ve-solucion-caso-6.png` (resultado visto por el solicitante) · `evidencias/PF-09-03-interfaz-resolver-sin-intervencion-400.png` (error en la interfaz) · `evidencias/PF-09-red-400.png` (pestaña Red del usuario: `POST /casos/3/resolver` 400, Response "Registre al menos una intervención antes de resolver el caso") · `evidencias/PF-09-01-interfaz-resolver-sin-intervencion-400.json` · `evidencias/PF-09-04-api-segundo-cierre-400.json`. Complementaria: PF-API-09. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras. En `PF-09-red-400.png` solo se ve la respuesta (Response), sin "Headers"; sin "Curl", "Authorize" ni `sessionStorage`. |

### PF-10 — Consulta consolidada de coordinación
| Campo | Valor |
|---|---|
| Requisito | CA-06 · RF-10 · RN-07 · US-10 (CA-US10.1, CA-US10.2) · Actividad 6, prueba 10 |
| Precondiciones | Casos 1..6 tal como los dejó la PF-09 (1 `Registrado`, 1 `En evaluación`, 2 `En atención`, 2 `Cerrado`); sesiones de `coordinador`, `solicitante1` y `tecnico1`. |
| Pasos | 1. Iniciar sesión como `coordinador` y abrir el tablero; comparar con la respuesta en la pestaña Red (Response). 2. API: `GET /coordinacion/resumen` con `solicitante1` y con `tecnico1`. |
| Entrada | Ninguna (consulta). |
| Canal y motivo | Interfaz para el tablero. API para el `403`: la interfaz no ofrece el tablero a otros roles. |
| Método y ruta (código HTTP obtenido) | `GET /coordinacion/resumen` coordinador (**200**) · mismo recurso con `solicitante1` (**403**) y con `tecnico1` (**403**) |
| Resultado esperado | 200 con 6 casos: 1 `Registrado`, 1 `En evaluación`, 2 `En atención`, 2 `Cerrado`; totales, conteo por estado y desglose por técnico coincidentes con el tablero; otro rol → 403. |
| Resultado obtenido | 200: total 6, abiertos 4, cerrados 2, sin asignar 2; Registrado 1, En evaluación 1, Asignado 0, En atención 2, Resuelto 0, Cerrado 2; por técnico: Teresa Técnica 1 abierto y 2 cerrados, Tomás Técnico 1 abierto y 0 cerrados. El tablero coincide con la respuesta. `solicitante1` y `tecnico1` → 403 "Su rol no permite esta acción". |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-10-03-tablero-coordinacion.png` (tablero) · `evidencias/PF-10-red.png` (pestaña Red del usuario: `GET /coordinacion/resumen` 200, Response con total 6, 4 abiertos, 2 cerrados y 2 sin asignar) · `evidencias/PF-10-01-api-resumen-200.json` · `evidencias/PF-10-02-api-resumen-403-solicitante-tecnico.json`. |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras. En `PF-10-red.png` solo se ve la respuesta (Response), sin "Headers"; sin "Curl", "Authorize" ni `sessionStorage`. |

### PF-11 — Persistencia e integridad de relaciones tras reiniciar la API
| Campo | Valor |
|---|---|
| Requisito | CA-01 a CA-06 · RNF-03 · RN-02 · RN-04 · RN-05 · Actividad 6, prueba 11 |
| Precondiciones | Estado final de las PF-01..PF-10 en la misma base: casos 1..6 (1 `Registrado`, 2 `En evaluación`, 3 y 4 `En atención`, 5 y 6 `Cerrado`); el caso 6 con 2 intervenciones de Teresa Técnica; sin resembrar. |
| Pasos | 1. Con la API en marcha, guardar por la API los casos 1..6, sus historiales y sus relaciones (solicitante, dependencia, técnico activo, intervenciones). 2. Detener solo la API y volver a arrancarla (sin `--reload`) sobre la misma base. 3. Repetir la consulta y comparar. 4. En la interfaz, comprobar el tablero y el detalle del caso 6. 5. Ejecutar `python -I backend/db/probar_esquema.py`. Sin consultas directas a SQLite. |
| Entrada | Ninguna (consultas tras el reinicio). |
| Canal y motivo | API e interfaz para la persistencia tras el reinicio. `probar_esquema.py` aparte: usa su propia base en memoria (`sqlite3.connect(":memory:")`), no la del entorno; demuestra las protecciones del esquema (RN-02, RN-04, RN-05, RN-08, RN-09), no los datos de estas PF. La persistencia de los datos de las PF se demuestra con el reinicio de la API. |
| Método y ruta (código HTTP obtenido) | `GET /casos`, `GET /casos/{id}`, `GET /casos/{id}/historial` y `GET /coordinacion/resumen` (**200**) antes y después del reinicio · `python -I backend/db/probar_esquema.py` |
| Resultado esperado | Los datos y los historiales de los casos 1..6 son idénticos antes y después del reinicio; cada caso conserva su solicitante, dependencia, técnico activo e intervenciones con su autor; la interfaz muestra lo mismo; el esquema cumple sus 45 comprobaciones. |
| Resultado obtenido | La comparación completa por la API antes y después del reinicio dio datos idénticos. Relaciones coherentes: cada caso con su solicitante y su dependencia; técnico activo del caso 3 = Tomás Técnico y de los casos 4, 5 y 6 = Teresa Técnica; intervenciones con su autor (caso 4: 1, caso 5: 1, caso 6: 2, de Teresa Técnica). La interfaz tras el reinicio muestra el tablero (6 casos, 4 abiertos, 2 cerrados) y el detalle del caso 6 `Cerrado` con su solución y su línea de tiempo. El caso 6 conserva los datos de su alta (persistencia de la PF-01). `probar_esquema.py`: "Resultado: 45 correctas, 0 fallidas". |
| Estado | ✅ Aprobada |
| Evidencia | `evidencias/PF-11-01-api-relaciones-tras-reinicio.json` · `evidencias/PF-11-02-interfaz-caso-6-tras-reinicio.png` · `evidencias/PF-11-probar-esquema.txt`. Complementaria: PF-12 (paso 8, persistencia tras reiniciar la API). |
| Fecha de ejecución | 18/11/2026 |
| Código probado | `main` `58c80e0` (sin cambios de código en la rama `feat/004-pruebas-y-entrega`) |
| Responsable | Simón Herrera |
| Equipo de ejecución | PC del equipo (compartido por Simón y Juan) |
| Revisión visual | Capturas revisadas: sin token ni cabeceras (sin "Curl", "Authorize", "Headers" de Red ni `sessionStorage`). Los `.json` y `.txt` no contienen token. |

### PF-12 — Integración interfaz–API–base de datos (flujo completo desde la interfaz)
| Campo | Valor |
|---|---|
| Requisito | CA-01..CA-06 · RF-18 y RF-21 (spec 003) · RN-01 · RN-02 · RN-03 · RN-06 · RN-07 · RN-10 · Actividad 6, prueba 12 |
| Precondiciones | BD SQLite temporal recién sembrada (`python -m backend.seed`, datos ficticios, 5 casos, 1 cerrado); API en `http://localhost:8000` (uvicorn) y Vite en `http://localhost:5173` (`npm run dev`); `JWT_SECRET` y `DATABASE_URL` por variables de entorno de la sesión; Chrome con DevTools; sin Swagger; contraseña de demostración `Mesa2026*`. Fecha de la ejecución: 18/11/2026. El código probado equivale a `main` `58c80e0` (PR #5). |
| Pasos | 1. Iniciar sesión como `solicitante1`, abrir "Reportar caso", llenar el formulario y enviarlo. 2. Cerrar sesión; entrar como `coordinador`, ver el tablero inicial, abrir el caso #6, evaluarlo con prioridad Alta y asignarlo a Teresa Técnica. 3. Cerrar sesión; entrar como `tecnico2` (Teresa Técnica), abrir el caso #6, "Iniciar atención", registrar una intervención de 45 min y resolver con solución. 4. Cerrar sesión; entrar como `coordinador` y "Cerrar caso" (confirmando el aviso). 5. Ver el tablero: el caso #6 debe estar entre los cerrados. 6. Entrar como `solicitante1`, abrir "Mis casos" y el caso #6: estado, solución y línea de tiempo. 7. Revisar en la pestaña Red cada llamada y su código. 8. Detener y volver a arrancar la API con la misma base, iniciar sesión como `solicitante1` y comprobar que el caso #6 sigue `Cerrado`. |
| Entrada | Reporte: placa `PF12-001`, usuario `Sara Solicitante`, teléfono `3001234567`, fecha de la falla `17/11/2026`, dependencia `Laboratorio de sistemas`, descripción "El equipo no enciende después de un corte de energía en el laboratorio." · Evaluación: prioridad `Alta` · Asignación: `Teresa Técnica` · Intervención: "Se revisó la fuente de poder y se encontró el fusible quemado.", 45 min · Solución: "Fusible de la fuente de poder reemplazado y equipo probado." |
| Método y ruta (código HTTP obtenido) | `POST /auth/login` (200, cada rol) · `GET /dependencias` (200) · `POST /casos` (**201**) · `GET /coordinacion/resumen` (200) · `GET /casos`, `GET /casos/6`, `GET /casos/6/historial` (200) · `PATCH /casos/6/evaluacion` (200) · `GET /tecnicos` (200) · `PUT /casos/6/tecnico` (200) · `POST /casos/6/iniciar-atencion` (200) · `POST /casos/6/intervenciones` (**201**) · `POST /casos/6/resolver` (200) · `POST /casos/6/cerrar` (200) |
| Resultado esperado | Cada acción de la interfaz llama a la API real y recibe 200/201; el caso avanza Registrado → En evaluación → Asignado → En atención → Resuelto → Cerrado; cada rol ve solo sus pantallas y acciones; el solicitante ve la solución y la línea de tiempo completa; el tablero lo cuenta entre los cerrados; el caso persiste tras reiniciar la API. |
| Resultado obtenido | Conforme en los 8 pasos. (1) Mensaje "Caso #6 registrado (estado Registrado)"; `POST /casos` 201. (2) Tablero inicial: total 6, abiertos 5, cerrados 1, sin asignar 3; evaluación → "En evaluación", prioridad Alta; asignación → "Asignado", responsable Teresa Técnica. (3) La técnica ve el caso #6 en "Mis casos asignados"; "Atención iniciada" (En atención); "Intervención registrada" (201); resuelto con la solución escrita. (4) Cierre con aviso de confirmación; estado "Cerrado". (5) Tablero final: total 6, abiertos 4, cerrados 2, sin asignar 2; el caso #6 aparece entre los cerrados (técnica Teresa Técnica, cierre 10:16). (6) El solicitante ve "Caso #6 Cerrado", la solución y 8 eventos en la línea de tiempo, cada uno con autor y fecha: reporte, evaluación, asignación, cambio a Asignado, En atención, intervención (45 min), Resuelto y Cerrado. (7) Todas las peticiones fueron a `http://localhost:8000`, con 200/201; el encabezado `Authorization` no aparece en las capturas. (8) Tras reiniciar la API, el caso #6 sigue `Cerrado` (con un nuevo `JWT_SECRET`, la sesión anterior dio 401 controlado "No autenticado o token inválido" y se pidió iniciar sesión). |
| Estado | ✅ Pasa |
| Evidencia | `evidencias/PF-12-01-login.png` (formulario de inicio de sesión) · `PF-12-02-login-solicitante.png` (sesión del solicitante) · `PF-12-03-reporte-formulario.png` · `PF-12-04-reporte-registrado.png` · `PF-12-05-login-coordinador-tablero-inicial.png` (sesión del coordinador y tablero inicial) · `PF-12-06-evaluacion.png` · `PF-12-07-asignacion.png` · `PF-12-08-login-tecnico-lista.png` (sesión del técnico) · `PF-12-09-intervencion.png` · `PF-12-10-resolucion.png` · `PF-12-11-cierre.png` · `PF-12-12a-solicitante-mis-casos.png` · `PF-12-12-solicitante-resultado.png` (solución y línea de tiempo) · `PF-12-13-tablero-final.png` · `PF-12-14-red-peticiones.jpeg` · `PF-12-15-persistencia-tras-reinicio.png` |

Observaciones de PF-12 (no son fallos): (a) en la pestaña Red, cada primera carga de una pantalla aparece como `net::ERR_ABORTED` seguida de la misma petición con 200: es la doble ejecución del efecto de React en modo desarrollo (StrictMode) que cancela la primera; no ocurre en la compilación de producción. (b) `PF-12-14-red-peticiones.jpeg` es una captura real del panel Network de Chrome DevTools (filtro Fetch/XHR), tomada en una sesión distinta a la del caso #6: sesión del coordinador con el caso #1 evaluado (prioridad Alta, estado "En evaluación"). Muestra login, resumen, casos, 5, historial, 1, evaluacion y tecnicos, todas con 200 (varias filas "(canceled)" van seguidas de la misma petición con 200); no se ve ningún token ni encabezado `Authorization`. (c) La fecha del formulario se asignó mediante script porque el control nativo de fecha no admite el relleno automático; el valor llegó a la API como `2026-11-17`. (d) El seeder no trae casos Resueltos, por eso se recorrió un caso nuevo (#6) de principio a fin.
