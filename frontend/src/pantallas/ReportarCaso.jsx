import { useEffect, useState } from "react";
import { listarDependencias, reportarCaso } from "../api/mesa.js";
import Aviso from "../componentes/Aviso.jsx";
import Campo from "../componentes/Campo.jsx";
import Cargando from "../componentes/Cargando.jsx";
import { camposPorNombre } from "../util/errores.js";
import { hoyLocal } from "../util/formato.js";

const ETIQUETAS = {
  placa_equipo: "Placa del equipo",
  nombre_usuario: "Nombre del usuario",
  telefono: "Teléfono",
  fecha: "Fecha de la falla",
  descripcion: "Descripción",
  dependencia_id: "Dependencia",
};

const VACIO = { placa_equipo: "", nombre_usuario: "", telefono: "", fecha: "", descripcion: "", dependencia_id: "" };

export default function ReportarCaso() {
  const [dependencias, setDependencias] = useState(null);
  const [errorCarga, setErrorCarga] = useState(null);
  const [valores, setValores] = useState(VACIO);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);
  const [creado, setCreado] = useState(null);

  useEffect(() => {
    const control = new AbortController();
    listarDependencias(control.signal)
      .then(setDependencias)
      .catch((e) => {
        if (e?.name !== "AbortError") setErrorCarga(e.detalle ?? "No se pudo cargar el catálogo");
      });
    return () => control.abort();
  }, []);

  const cambiar = (campo) => (e) => {
    const valor = e.target.value;
    setValores((v) => ({ ...v, [campo]: valor }));
  };

  async function enviar(evento) {
    evento.preventDefault();
    if (enviando) return;
    setEnviando(true);
    setError(null);
    setCreado(null);
    try {
      const caso = await reportarCaso({ ...valores, dependencia_id: Number(valores.dependencia_id) });
      setCreado(caso);
      setValores(VACIO);
    } catch (e) {
      setError(e);
    } finally {
      setEnviando(false);
    }
  }

  if (errorCarga) return <Aviso tipo="error">{errorCarga}</Aviso>;
  if (!dependencias) return <Cargando texto="Cargando dependencias…" />;

  const { porCampo, sinEtiqueta } = camposPorNombre(error, ETIQUETAS);
  const mensaje = error ? [error.detalle, ...sinEtiqueta].filter(Boolean).join(". ") : null;

  return (
    <section aria-labelledby="titulo-reportar">
      <h1 id="titulo-reportar">Reportar caso</h1>
      {creado && <Aviso tipo="exito">{`Caso #${creado.id} registrado (estado ${creado.estado})`}</Aviso>}
      <form className="formulario" onSubmit={enviar}>
        <Campo etiqueta={ETIQUETAS.placa_equipo} motivos={porCampo.placa_equipo}>
          {(p) => <input {...p} name="placa_equipo" required maxLength={50} value={valores.placa_equipo} onChange={cambiar("placa_equipo")} />}
        </Campo>
        <Campo etiqueta={ETIQUETAS.nombre_usuario} motivos={porCampo.nombre_usuario}>
          {(p) => <input {...p} name="nombre_usuario" required maxLength={200} value={valores.nombre_usuario} onChange={cambiar("nombre_usuario")} />}
        </Campo>
        <Campo etiqueta={ETIQUETAS.telefono} motivos={porCampo.telefono}>
          {(p) => <input {...p} name="telefono" type="tel" required maxLength={20} value={valores.telefono} onChange={cambiar("telefono")} />}
        </Campo>
        <Campo etiqueta={ETIQUETAS.fecha} motivos={porCampo.fecha}>
          {(p) => <input {...p} name="fecha" type="date" required max={hoyLocal()} value={valores.fecha} onChange={cambiar("fecha")} />}
        </Campo>
        <Campo etiqueta={ETIQUETAS.dependencia_id} motivos={porCampo.dependencia_id}>
          {(p) => (
            <select {...p} name="dependencia_id" required value={valores.dependencia_id} onChange={cambiar("dependencia_id")}>
              <option value="">Seleccione una dependencia</option>
              {dependencias.map((d) => (
                <option key={d.id} value={d.id}>{d.nombre}</option>
              ))}
            </select>
          )}
        </Campo>
        <Campo etiqueta={ETIQUETAS.descripcion} motivos={porCampo.descripcion}>
          {(p) => <textarea {...p} name="descripcion" rows={5} required minLength={15} maxLength={4000} value={valores.descripcion} onChange={cambiar("descripcion")} />}
        </Campo>
        <Aviso tipo="error">{mensaje}</Aviso>
        <button type="submit" className="boton" disabled={enviando}>
          {enviando ? "Enviando…" : "Reportar caso"}
        </button>
      </form>
    </section>
  );
}
