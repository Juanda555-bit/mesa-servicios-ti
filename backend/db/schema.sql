-- Esquema de la Mesa de Servicios TI (SQLite)
-- Debe ejecutarse con: PRAGMA foreign_keys = ON; (por cada conexión)
-- Fechas y horas en UTC, texto ISO-8601 (YYYY-MM-DDTHH:MM:SS.sssZ).

PRAGMA foreign_keys = ON;

-- ============================================================
-- Catálogos y usuarios
-- ============================================================

CREATE TABLE usuario (
    id            INTEGER PRIMARY KEY,
    nombre        TEXT    NOT NULL CHECK (length(trim(nombre)) > 0),
    correo        TEXT    NOT NULL UNIQUE COLLATE NOCASE
                          CHECK (correo LIKE '_%@_%._%'),
    password_hash TEXT    NOT NULL CHECK (length(password_hash) > 0),
    rol           TEXT    NOT NULL CHECK (rol IN ('solicitante', 'tecnico', 'coordinador')),
    activo        INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    creado_en     TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE TABLE dependencia (
    id     INTEGER PRIMARY KEY,
    nombre TEXT    NOT NULL UNIQUE COLLATE NOCASE CHECK (length(trim(nombre)) > 0),
    activa INTEGER NOT NULL DEFAULT 1 CHECK (activa IN (0, 1))
);

-- ============================================================
-- Caso (RF-02, RF-03, RF-04, RF-07, RF-08)
-- ============================================================

CREATE TABLE caso (
    id             INTEGER PRIMARY KEY,
    -- Datos del reporte (inmutables después del registro)
    placa_equipo   TEXT    NOT NULL CHECK (length(trim(placa_equipo)) > 0),
    nombre_usuario TEXT    NOT NULL CHECK (length(trim(nombre_usuario)) > 0),
    telefono       TEXT    NOT NULL CHECK (length(trim(telefono)) > 0),
    fecha          TEXT    NOT NULL CHECK (date(fecha) IS NOT NULL AND date(fecha) = fecha),
    descripcion    TEXT    NOT NULL CHECK (length(trim(descripcion)) >= 15),
    dependencia_id INTEGER NOT NULL REFERENCES dependencia (id) ON DELETE RESTRICT,
    solicitante_id INTEGER NOT NULL REFERENCES usuario (id) ON DELETE RESTRICT,
    -- Gestión
    estado         TEXT    NOT NULL DEFAULT 'Registrado'
                           CHECK (estado IN ('Registrado', 'En evaluación', 'Asignado',
                                             'En atención', 'Resuelto', 'Cerrado')),
    prioridad      TEXT    CHECK (prioridad IS NULL
                                  OR prioridad IN ('Baja', 'Media', 'Alta', 'Crítica')),
    solucion       TEXT    CHECK (solucion IS NULL OR length(trim(solucion)) > 0),
    creado_en      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    resuelto_en    TEXT,
    cerrado_en     TEXT,
    -- Coherencia entre estado y datos
    CHECK (estado = 'Registrado' OR prioridad IS NOT NULL),
    CHECK ((estado IN ('Resuelto', 'Cerrado')) = (solucion IS NOT NULL)),
    CHECK ((estado IN ('Resuelto', 'Cerrado')) = (resuelto_en IS NOT NULL)),
    CHECK ((estado = 'Cerrado') = (cerrado_en IS NOT NULL))
);

CREATE INDEX ix_caso_solicitante ON caso (solicitante_id, creado_en);
CREATE INDEX ix_caso_estado      ON caso (estado, creado_en);
CREATE INDEX ix_caso_placa       ON caso (placa_equipo);
CREATE INDEX ix_caso_dependencia ON caso (dependencia_id);

-- ============================================================
-- Asignación de responsable (RF-05, RN-02, RN-10)
-- Un caso tiene como máximo UNA asignación activa (retirado_en NULL).
-- ============================================================

CREATE TABLE asignacion (
    id           INTEGER PRIMARY KEY,
    caso_id      INTEGER NOT NULL REFERENCES caso (id)    ON DELETE RESTRICT,
    tecnico_id   INTEGER NOT NULL REFERENCES usuario (id) ON DELETE RESTRICT,
    asignado_por INTEGER NOT NULL REFERENCES usuario (id) ON DELETE RESTRICT,
    asignado_en  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    retirado_en  TEXT,
    CHECK (retirado_en IS NULL OR retirado_en >= asignado_en)
);

CREATE UNIQUE INDEX ux_asignacion_activa
    ON asignacion (caso_id) WHERE retirado_en IS NULL;
CREATE INDEX ix_asignacion_tecnico_activa
    ON asignacion (tecnico_id) WHERE retirado_en IS NULL;

-- ============================================================
-- Intervenciones técnicas (RF-06, RN-05)
-- ============================================================

CREATE TABLE intervencion (
    id           INTEGER PRIMARY KEY,
    caso_id      INTEGER NOT NULL REFERENCES caso (id)    ON DELETE RESTRICT,
    tecnico_id   INTEGER NOT NULL REFERENCES usuario (id) ON DELETE RESTRICT,
    descripcion  TEXT    NOT NULL CHECK (length(trim(descripcion)) > 0),
    duracion_min INTEGER NOT NULL CHECK (duracion_min > 0),
    creado_en    TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX ix_intervencion_caso ON intervencion (caso_id, creado_en);

-- ============================================================
-- Historial de estados (RF-07, RF-09, RN-05)
-- ============================================================

CREATE TABLE historial_estado (
    id              INTEGER PRIMARY KEY,
    caso_id         INTEGER NOT NULL REFERENCES caso (id)    ON DELETE RESTRICT,
    estado_anterior TEXT,
    estado_nuevo    TEXT    NOT NULL,
    autor_id        INTEGER NOT NULL REFERENCES usuario (id) ON DELETE RESTRICT,
    comentario      TEXT,
    creado_en       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    CHECK (estado_nuevo IN ('Registrado', 'En evaluación', 'Asignado',
                            'En atención', 'Resuelto', 'Cerrado')),
    CHECK (estado_anterior IS NULL
           OR estado_anterior IN ('Registrado', 'En evaluación', 'Asignado',
                                  'En atención', 'Resuelto', 'Cerrado')),
    CHECK (estado_anterior IS NULL OR estado_anterior <> estado_nuevo)
);

CREATE INDEX ix_historial_caso ON historial_estado (caso_id, creado_en);

-- ============================================================
-- Triggers de protección (solo tres grupos): caso cerrado inmutable,
-- historial sin edición ni borrado y un único responsable activo (índice).
-- Las transiciones de estado y sus precondiciones (RN-01, RN-03) viven en el backend.
-- ============================================================

-- RN-04: un caso cerrado no se modifica ni se elimina nunca.
CREATE TRIGGER trg_caso_cerrado_inmutable
BEFORE UPDATE ON caso
WHEN OLD.estado = 'Cerrado'
BEGIN
    SELECT RAISE(ABORT, 'RN-04: un caso cerrado no puede modificarse');
END;

CREATE TRIGGER trg_caso_sin_borrado
BEFORE DELETE ON caso
BEGIN
    SELECT RAISE(ABORT, 'los casos no se eliminan');
END;

-- Una asignación solo puede cerrarse (retirado_en), nunca reescribirse ni borrarse.
CREATE TRIGGER trg_asignacion_solo_retiro
BEFORE UPDATE ON asignacion
WHEN OLD.retirado_en IS NOT NULL
  OR NEW.caso_id <> OLD.caso_id
  OR NEW.tecnico_id <> OLD.tecnico_id
  OR NEW.asignado_por <> OLD.asignado_por
  OR NEW.asignado_en <> OLD.asignado_en
BEGIN
    SELECT RAISE(ABORT, 'una asignación solo puede retirarse una vez');
END;

CREATE TRIGGER trg_asignacion_sin_borrado
BEFORE DELETE ON asignacion
BEGIN
    SELECT RAISE(ABORT, 'las asignaciones no se eliminan');
END;

-- RN-05: intervenciones e historial son solo de inserción (append-only).
CREATE TRIGGER trg_intervencion_sin_update
BEFORE UPDATE ON intervencion
BEGIN
    SELECT RAISE(ABORT, 'RN-05: las intervenciones no se editan');
END;

CREATE TRIGGER trg_intervencion_sin_delete
BEFORE DELETE ON intervencion
BEGIN
    SELECT RAISE(ABORT, 'RN-05: las intervenciones no se eliminan');
END;

CREATE TRIGGER trg_historial_sin_update
BEFORE UPDATE ON historial_estado
BEGIN
    SELECT RAISE(ABORT, 'RN-05: el historial no se edita');
END;

CREATE TRIGGER trg_historial_sin_delete
BEFORE DELETE ON historial_estado
BEGIN
    SELECT RAISE(ABORT, 'RN-05: el historial no se elimina');
END;

-- ============================================================
-- Vistas de consulta
-- ============================================================

-- Caso con dependencia, solicitante y responsable activo (RF-03, CA-03).
CREATE VIEW v_caso_detalle AS
SELECT c.id, c.placa_equipo, c.nombre_usuario, c.telefono, c.fecha,
       c.descripcion, c.estado, c.prioridad, c.solucion,
       c.creado_en, c.resuelto_en, c.cerrado_en,
       d.nombre  AS dependencia,
       c.solicitante_id, s.nombre AS solicitante,
       a.tecnico_id,     t.nombre AS tecnico
FROM caso c
JOIN dependencia d ON d.id = c.dependencia_id
JOIN usuario s     ON s.id = c.solicitante_id
LEFT JOIN asignacion a ON a.caso_id = c.id AND a.retirado_en IS NULL
LEFT JOIN usuario t    ON t.id = a.tecnico_id;

-- Línea de tiempo del caso (RF-09, CA-04). Consultar siempre con:
--   SELECT * FROM v_linea_tiempo WHERE caso_id = ? ORDER BY momento, orden, ref_id;
CREATE VIEW v_linea_tiempo AS
SELECT h.caso_id, h.creado_en AS momento, 1 AS orden, h.id AS ref_id,
       'cambio_estado' AS tipo, h.autor_id, u.nombre AS autor,
       coalesce(h.estado_anterior, 'Inicio') || ' → ' || h.estado_nuevo ||
           coalesce(': ' || h.comentario, '') AS detalle
FROM historial_estado h JOIN usuario u ON u.id = h.autor_id
UNION ALL
SELECT a.caso_id, a.asignado_en, 2, a.id,
       CASE WHEN EXISTS (SELECT 1 FROM asignacion p
                         WHERE p.caso_id = a.caso_id AND p.id < a.id)
            THEN 'reasignacion' ELSE 'asignacion' END,
       a.asignado_por, u.nombre,
       'Responsable: ' || t.nombre ||
       coalesce(' (antes: ' || (SELECT tp.nombre FROM asignacion p
                                JOIN usuario tp ON tp.id = p.tecnico_id
                                WHERE p.caso_id = a.caso_id AND p.id < a.id
                                ORDER BY p.id DESC LIMIT 1) || ')', '')
FROM asignacion a
JOIN usuario u ON u.id = a.asignado_por
JOIN usuario t ON t.id = a.tecnico_id
UNION ALL
SELECT i.caso_id, i.creado_en, 3, i.id, 'intervencion', i.tecnico_id, u.nombre,
       i.descripcion || ' (' || i.duracion_min || ' min)'
FROM intervencion i JOIN usuario u ON u.id = i.tecnico_id;
