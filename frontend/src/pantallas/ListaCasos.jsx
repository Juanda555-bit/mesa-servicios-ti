import { useEffect, useState } from "react";
import { listarCasos } from "../api/mesa.js";
import Aviso from "../componentes/Aviso.jsx";
import Cargando from "../componentes/Cargando.jsx";
import { fechaDia, fechaHora } from "../util/formato.js";

export default function ListaCasos({ titulo, aviso, onAbrir }) {
  const [casos, setCasos] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const control = new AbortController();
    listarCasos(control.signal)
      .then(setCasos)
      .catch((e) => {
        if (e?.name !== "AbortError") setError(e.detalle ?? "No se pudo cargar la lista");
      });
    return () => control.abort();
  }, []);

  return (
    <section aria-labelledby="titulo-lista">
      <h1 id="titulo-lista">{titulo}</h1>
      <Aviso tipo="error">{aviso}</Aviso>
      {error ? (
        <Aviso tipo="error">{error}</Aviso>
      ) : !casos ? (
        <Cargando />
      ) : casos.length === 0 ? (
        <p className="vacio">No hay casos para mostrar</p>
      ) : (
        <div className="tabla-envoltura">
          <table className="tabla">
            <thead>
              <tr>
                <th scope="col">Caso</th>
                <th scope="col">Placa</th>
                <th scope="col">Estado</th>
                <th scope="col">Prioridad</th>
                <th scope="col">Responsable</th>
                <th scope="col">Fecha de la falla</th>
                <th scope="col">Registrado</th>
              </tr>
            </thead>
            <tbody>
              {casos.map((c) => (
                <tr key={c.id}>
                  <th scope="row">
                    <button type="button" className="enlace" onClick={() => onAbrir(c.id)}>
                      #{c.id}
                    </button>
                  </th>
                  <td>{c.placa_equipo}</td>
                  <td>
                    <span className={`estado estado-${c.estado.toLowerCase().replace(/\s+/g, "-")}`}>{c.estado}</span>
                  </td>
                  <td>{c.prioridad ?? "—"}</td>
                  <td>{c.tecnico ?? "Sin asignar"}</td>
                  <td>{fechaDia(c.fecha)}</td>
                  <td>{fechaHora(c.creado_en)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
