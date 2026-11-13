import sqlite3, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
schema = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).with_name("schema.sql")).read_text(encoding="utf-8")
db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.executescript(schema)
print("sqlite", sqlite3.sqlite_version)

ok = fail = 0

def debe_funcionar(nombre, sql, args=()):
    global ok, fail
    try:
        db.execute(sql, args)
        ok += 1
        print("OK   ", nombre)
    except sqlite3.Error as e:
        fail += 1
        print("FALLA", nombre, "->", e)

def debe_rechazar(nombre, sql, args=()):
    global ok, fail
    try:
        db.execute(sql, args)
        fail += 1
        print("FALLA (se aceptó)", nombre)
    except sqlite3.Error as e:
        ok += 1
        print("OK   rechazó:", nombre, "->", e)

U = "INSERT INTO usuario(id,nombre,correo,password_hash,rol) VALUES (?,?,?,?,?)"
debe_funcionar("usuario solicitante", U, (1, "Ana", "ana@x.co", "h", "solicitante"))
debe_funcionar("usuario tecnico", U, (2, "Tomas", "tomas@x.co", "h", "tecnico"))
debe_funcionar("usuario tecnico 2", U, (3, "Tania", "tania@x.co", "h", "tecnico"))
debe_funcionar("usuario coordinador", U, (4, "Carla", "carla@x.co", "h", "coordinador"))
debe_rechazar("rol invalido", U, (5, "X", "x@x.co", "h", "admin"))
debe_rechazar("correo duplicado (sin distinguir mayúsculas)", U, (5, "X", "ANA@X.CO", "h", "solicitante"))
debe_rechazar("correo mal formado", U, (5, "X", "sinarroba", "h", "solicitante"))
debe_funcionar("dependencia", "INSERT INTO dependencia(id,nombre) VALUES (1,'Secretaría académica')")
debe_rechazar("dependencia duplicada", "INSERT INTO dependencia(nombre) VALUES ('secretaría académica')")

C = ("INSERT INTO caso(id,placa_equipo,nombre_usuario,telefono,fecha,descripcion,"
     "dependencia_id,solicitante_id) VALUES (?,?,?,?,?,?,?,?)")
buena = (1, "ABC-123", "Ana Pérez", "3001234567", "2026-11-15",
         "El computador no enciende desde la mañana", 1, 1)
debe_funcionar("registrar caso válido", C, buena)
debe_rechazar("descripcion corta", C, (2, "A", "N", "1", "2026-11-15", "corta", 1, 1))
debe_rechazar("fecha inválida", C, (2, "A", "N", "1", "15/11/2026", "x" * 20, 1, 1))
debe_rechazar("fecha inexistente", C, (2, "A", "N", "1", "2026-02-31", "x" * 20, 1, 1))
debe_rechazar("dependencia inexistente", C, (2, "A", "N", "1", "2026-11-15", "x" * 20, 99, 1))
debe_rechazar("placa vacía", C, (2, "  ", "N", "1", "2026-11-15", "x" * 20, 1, 1))
debe_rechazar("estado inicial distinto de Registrado sin prioridad",
              "INSERT INTO caso(placa_equipo,nombre_usuario,telefono,fecha,descripcion,dependencia_id,"
              "solicitante_id,estado) VALUES ('A','N','1','2026-11-15','" + "x" * 20 + "',1,1,'Asignado')")

debe_rechazar("evaluar sin prioridad", "UPDATE caso SET estado='En evaluación' WHERE id=1")
debe_funcionar("evaluar con prioridad",
               "UPDATE caso SET estado='En evaluación', prioridad='Alta' WHERE id=1")
debe_rechazar("prioridad inválida", "UPDATE caso SET prioridad='Urgente' WHERE id=1")

A = "INSERT INTO asignacion(caso_id,tecnico_id,asignado_por) VALUES (?,?,?)"
debe_funcionar("asignar técnico", A, (1, 2, 4))
debe_rechazar("segunda asignación activa", A, (1, 3, 4))
debe_funcionar("pasar a Asignado", "UPDATE caso SET estado='Asignado' WHERE id=1")

I = "INSERT INTO intervencion(caso_id,tecnico_id,descripcion,duracion_min) VALUES (?,?,?,?)"
debe_rechazar("intervención con duración 0", I, (1, 2, "x", 0))
debe_funcionar("pasar a En atención", "UPDATE caso SET estado='En atención' WHERE id=1")
debe_funcionar("registrar intervención", I, (1, 2, "Revisé la fuente de poder", 30))
debe_rechazar("editar intervención", "UPDATE intervencion SET descripcion='otra' WHERE id=1")
debe_rechazar("borrar intervención", "DELETE FROM intervencion WHERE id=1")

debe_funcionar("retirar asignación (reasignar)",
               "UPDATE asignacion SET retirado_en=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=1")
debe_funcionar("nueva asignación (reasignar)", A, (1, 3, 4))
debe_rechazar("reescribir una asignación", "UPDATE asignacion SET tecnico_id=2 WHERE id=2")
debe_rechazar("borrar asignación", "DELETE FROM asignacion WHERE id=2")
debe_funcionar("intervención del nuevo responsable", I, (1, 3, "Cambié la fuente", 45))

debe_rechazar("resolver sin solución", "UPDATE caso SET estado='Resuelto' WHERE id=1")
debe_funcionar("resolver con solución",
               "UPDATE caso SET estado='Resuelto', solucion='Fuente reemplazada', "
               "resuelto_en=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=1")
debe_rechazar("cerrar sin cerrado_en", "UPDATE caso SET estado='Cerrado' WHERE id=1")
debe_funcionar("cerrar caso",
               "UPDATE caso SET estado='Cerrado', cerrado_en=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=1")
debe_rechazar("modificar caso cerrado", "UPDATE caso SET prioridad='Baja' WHERE id=1")
debe_rechazar("borrar caso", "DELETE FROM caso WHERE id=1")
debe_rechazar("borrar usuario con casos", "DELETE FROM usuario WHERE id=1")

H = "INSERT INTO historial_estado(caso_id,estado_anterior,estado_nuevo,autor_id) VALUES (?,?,?,?)"
debe_funcionar("historial inicial", H, (1, None, "Registrado", 1))
debe_funcionar("historial cambio", H, (1, "Registrado", "En evaluación", 4))
debe_rechazar("historial mismo estado", H, (1, "Asignado", "Asignado", 4))
debe_rechazar("historial estado inválido", H, (1, "Registrado", "Cancelado", 4))
debe_rechazar("editar historial", "UPDATE historial_estado SET comentario='x' WHERE id=1")
debe_rechazar("borrar historial", "DELETE FROM historial_estado WHERE id=1")

print("\n--- v_caso_detalle ---")
for r in db.execute("SELECT id, estado, prioridad, dependencia, solicitante, tecnico FROM v_caso_detalle"):
    print(r)
print("\n--- v_linea_tiempo ---")
for r in db.execute("SELECT momento, tipo, autor, detalle FROM v_linea_tiempo WHERE caso_id=1 "
                    "ORDER BY momento, orden, ref_id"):
    print(r)
print("\n--- plan de consulta (casos del técnico) ---")
for r in db.execute("EXPLAIN QUERY PLAN SELECT caso_id FROM asignacion WHERE tecnico_id=3 AND retirado_en IS NULL"):
    print(r)

print(f"\nResultado: {ok} correctas, {fail} fallidas")
sys.exit(1 if fail else 0)
