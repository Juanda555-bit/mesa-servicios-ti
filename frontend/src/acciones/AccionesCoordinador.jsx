import { useEffect, useRef, useState } from "react";
import { asignarTecnico, cerrarCaso, evaluarCaso, listarTecnicos } from "../api/mesa.js";
import Aviso from "../componentes/Aviso.jsx";
import Campo from "../componentes/Campo.jsx";
import { camposPorNombre } from "../util/errores.js";

const PRIORIDADES = ["Baja", "Media", "Alta", "Crítica"];
const ETIQUETAS = { prioridad: "Prioridad", tecnico_id: "Técnico" };
const ESTADOS_CON_ACCION = ["Registrado", "En evaluación", "Asignado", "En atención", "Resuelto"];

// Acciones del coordinador según el estado del caso. El permiso real lo comprueba la API (403).
export default function AccionesCoordinador({ caso, recargar }) {
  const [prioridad, setPrioridad] = useState("");
  const [tecnicoId, setTecnicoId] = useState("");
  const [tecnicos, setTecnicos] = useState(null);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const enCurso = useRef(false); // evita peticiones duplicadas por doble clic

  const asigna = ["En evaluación", "Asignado", "En atención"].includes(caso.estado);

  useEffect(() => {
    if (!asigna) return undefined;
    const control = new AbortController();
    listarTecnicos(control.signal)
      .then(setTecnicos)
      .catch((e) => {
        if (e?.name !== "AbortError") setError(e);
      });
    return () => control.abort();
  }, [asigna]);

  if (!ESTADOS_CON_ACCION.includes(caso.estado)) return null;

  async function ejecutar(peticion, alExito, mensaje) {
    if (enCurso.current) return;
    enCurso.current = true;
    setOcupado(true);
    setError(null);
    setExito(null);
    try {
      await peticion();
      alExito?.();
      setExito(mensaje);
      recargar();
    } catch (e) {
      setError(e);
      // Con 422 no cambió nada en el servidor: se conserva lo escrito sin recargar.
      if (e?.estado !== 422) recargar();
    } finally {
      enCurso.current = false;
      setOcupado(false);
    }
  }

  const evaluar = (evento) => {
    evento.preventDefault();
    ejecutar(() => evaluarCaso(caso.id, prioridad), () => setPrioridad(""), "Caso evaluado");
  };

  const reasignando = caso.estado !== "En evaluación";
  const asignar = (evento) => {
    evento.preventDefault();
    ejecutar(
      () => asignarTecnico(caso.id, Number(tecnicoId)),
      () => setTecnicoId(""),
      reasignando ? "Técnico reasignado" : "Técnico asignado",
    );
  };

  const cerrar = () => {
    if (!window.confirm(`¿Cerrar el caso #${caso.id}? Un caso cerrado ya no se puede modificar.`)) return;
    ejecutar(() => cerrarCaso(caso.id), null, "Caso cerrado");
  };

  const { porCampo, sinEtiqueta } = camposPorNombre(error, ETIQUETAS);
  const mensaje = error ? [error.detalle, ...sinEtiqueta].filter(Boolean).join(". ") : null;
  // D-c: el responsable actual no se ofrece al reasignar.
  const opciones = (tecnicos ?? []).filter((t) => t.id !== caso.tecnico_id);

  return (
    <section className="acciones" aria-labelledby="titulo-acciones">
      <h2 id="titulo-acciones">Acciones del coordinador</h2>
      <Aviso tipo="exito">{exito}</Aviso>
      <Aviso tipo="error">{mensaje}</Aviso>
      {caso.estado === "Registrado" && (
        <form className="formulario" onSubmit={evaluar}>
          <h3>Evaluar caso</h3>
          <Campo etiqueta={ETIQUETAS.prioridad} motivos={porCampo.prioridad}>
            {(p) => (
              <select {...p} name="prioridad" required value={prioridad} onChange={(e) => setPrioridad(e.target.value)}>
                <option value="">Seleccione una prioridad</option>
                {PRIORIDADES.map((x) => (
                  <option key={x} value={x}>{x}</option>
                ))}
              </select>
            )}
          </Campo>
          <button type="submit" className="boton" disabled={ocupado}>Evaluar</button>
        </form>
      )}
      {asigna && (
        <form className="formulario" onSubmit={asignar}>
          <h3>{reasignando ? "Reasignar técnico" : "Asignar técnico"}</h3>
          <Campo etiqueta={ETIQUETAS.tecnico_id} motivos={porCampo.tecnico_id}>
            {(p) => (
              <select {...p} name="tecnico_id" required value={tecnicoId} onChange={(e) => setTecnicoId(e.target.value)}>
                <option value="">Seleccione un técnico</option>
                {opciones.map((t) => (
                  <option key={t.id} value={t.id}>{t.nombre}</option>
                ))}
              </select>
            )}
          </Campo>
          <button type="submit" className="boton" disabled={ocupado || !tecnicos}>
            {reasignando ? "Reasignar técnico" : "Asignar técnico"}
          </button>
        </form>
      )}
      {caso.estado === "Resuelto" && (
        <button type="button" className="boton" disabled={ocupado} onClick={cerrar}>Cerrar caso</button>
      )}
    </section>
  );
}
