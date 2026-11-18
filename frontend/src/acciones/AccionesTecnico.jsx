import { useRef, useState } from "react";
import { iniciarAtencion, registrarIntervencion, resolverCaso } from "../api/mesa.js";
import Aviso from "../componentes/Aviso.jsx";
import Campo from "../componentes/Campo.jsx";
import { camposPorNombre } from "../util/errores.js";

const ETIQUETAS = { descripcion: "Descripción", duracion_min: "Duración (min)", solucion: "Solución" };
const VACIO = { descripcion: "", duracion_min: "", solucion: "" };

// Acciones del técnico según el estado del caso. El permiso real lo comprueba la API (403).
export default function AccionesTecnico({ caso, recargar }) {
  const [valores, setValores] = useState(VACIO);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const enCurso = useRef(false); // evita peticiones duplicadas por doble clic

  if (caso.estado !== "Asignado" && caso.estado !== "En atención") return null;

  const cambiar = (campo) => (e) => {
    const valor = e.target.value;
    setValores((v) => ({ ...v, [campo]: valor }));
  };

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

  const iniciar = () => ejecutar(() => iniciarAtencion(caso.id), null, "Atención iniciada");

  const intervenir = (evento) => {
    evento.preventDefault();
    ejecutar(
      () => registrarIntervencion(caso.id, { descripcion: valores.descripcion, duracion_min: Number(valores.duracion_min) }),
      () => setValores((v) => ({ ...v, descripcion: "", duracion_min: "" })),
      "Intervención registrada",
    );
  };

  const resolver = (evento) => {
    evento.preventDefault();
    ejecutar(
      () => resolverCaso(caso.id, { solucion: valores.solucion }),
      () => setValores(VACIO),
      "Caso resuelto",
    );
  };

  const { porCampo, sinEtiqueta } = camposPorNombre(error, ETIQUETAS);
  const mensaje = error ? [error.detalle, ...sinEtiqueta].filter(Boolean).join(". ") : null;

  return (
    <section className="acciones" aria-labelledby="titulo-acciones">
      <h2 id="titulo-acciones">Acciones del técnico</h2>
      <Aviso tipo="exito">{exito}</Aviso>
      <Aviso tipo="error">{mensaje}</Aviso>
      {caso.estado === "Asignado" && (
        <button type="button" className="boton" disabled={ocupado} onClick={iniciar}>
          Iniciar atención
        </button>
      )}
      {caso.estado === "En atención" && (
        <>
          <form className="formulario" onSubmit={intervenir}>
            <h3>Registrar intervención</h3>
            <Campo etiqueta={ETIQUETAS.descripcion} motivos={porCampo.descripcion}>
              {(p) => <textarea {...p} name="descripcion" rows={3} required maxLength={4000} value={valores.descripcion} onChange={cambiar("descripcion")} />}
            </Campo>
            <Campo etiqueta={ETIQUETAS.duracion_min} motivos={porCampo.duracion_min}>
              {(p) => <input {...p} name="duracion_min" type="number" min={1} step={1} required value={valores.duracion_min} onChange={cambiar("duracion_min")} />}
            </Campo>
            <button type="submit" className="boton" disabled={ocupado}>Registrar intervención</button>
          </form>
          <form className="formulario" onSubmit={resolver}>
            <h3>Resolver caso</h3>
            <Campo etiqueta={ETIQUETAS.solucion} motivos={porCampo.solucion}>
              {(p) => <textarea {...p} name="solucion" rows={3} required maxLength={4000} value={valores.solucion} onChange={cambiar("solucion")} />}
            </Campo>
            <button type="submit" className="boton" disabled={ocupado}>Resolver</button>
          </form>
        </>
      )}
    </section>
  );
}
