import { useEffect, useState } from "react";
import { obtenerResumen } from "../api/mesa.js";
import Aviso from "../componentes/Aviso.jsx";
import Cargando from "../componentes/Cargando.jsx";
import { fechaHora } from "../util/formato.js";

function ListaResumen({ titulo, casos, vacio, onAbrir }) {
  return (
    <section aria-label={titulo}>
      <h2>{titulo}</h2>
      {casos.length === 0 ? (
        <p className="vacio">{vacio}</p>
      ) : (
        <div className="tabla-envoltura">
          <table className="tabla">
            <thead>
              <tr>
                <th scope="col">Caso</th>
                <th scope="col">Placa</th>
                <th scope="col">Estado</th>
                <th scope="col">Prioridad</th>
                <th scope="col">Técnico</th>
                <th scope="col">Registrado</th>
                <th scope="col">Cerrado</th>
              </tr>
            </thead>
            <tbody>
              {casos.map((c) => (
                <tr key={c.id}>
                  <th scope="row">
                    <button type="button" className="enlace" onClick={() => onAbrir(c.id)}>
                      Ver detalle #{c.id}
                    </button>
                  </th>
                  <td>{c.placa_equipo}</td>
                  <td>
                    <span className={`estado estado-${c.estado.toLowerCase().replace(/\s+/g, "-")}`}>{c.estado}</span>
                  </td>
                  <td>{c.prioridad ?? "—"}</td>
                  <td>{c.tecnico ?? "Sin asignar"}</td>
                  <td>{fechaHora(c.creado_en)}</td>
                  <td>{fechaHora(c.cerrado_en)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default function Tablero({ titulo, aviso, onAbrir }) {
  const [resumen, setResumen] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const control = new AbortController();
    obtenerResumen(control.signal)
      .then(setResumen)
      .catch((e) => {
        if (e?.name !== "AbortError") setError(e.detalle ?? "No se pudo cargar el tablero");
      });
    return () => control.abort();
  }, []);

  return (
    <section aria-labelledby="titulo-tablero">
      <h1 id="titulo-tablero">{titulo}</h1>
      <Aviso tipo="error">{aviso}</Aviso>
      {error ? (
        <Aviso tipo="error">{error}</Aviso>
      ) : !resumen ? (
        <Cargando />
      ) : (
        <>
          <dl className="cifras">
            {[
              ["Total", resumen.total],
              ["Abiertos", resumen.abiertos],
              ["Cerrados", resumen.cerrados],
              ["Sin asignar", resumen.sin_asignar],
            ].map(([nombre, valor]) => (
              <div className="cifra" key={nombre}>
                <dt>{nombre}</dt>
                <dd>{valor}</dd>
              </div>
            ))}
          </dl>
          <div className="tablero-tablas">
            <section aria-label="Casos por estado">
              <h2>Casos por estado</h2>
              <div className="tabla-envoltura">
                <table className="tabla">
                  <thead>
                    <tr>
                      <th scope="col">Estado</th>
                      <th scope="col">Casos</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(resumen.por_estado).map(([estado, n]) => (
                      <tr key={estado}>
                        <th scope="row">{estado}</th>
                        <td>{n}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
            <section aria-label="Casos por técnico">
              <h2>Casos por técnico</h2>
              {resumen.por_tecnico.length === 0 ? (
                <p className="vacio">Ningún técnico tiene casos asignados</p>
              ) : (
                <div className="tabla-envoltura">
                  <table className="tabla">
                    <thead>
                      <tr>
                        <th scope="col">Técnico</th>
                        <th scope="col">Abiertos</th>
                        <th scope="col">Cerrados</th>
                      </tr>
                    </thead>
                    <tbody>
                      {resumen.por_tecnico.map((t) => (
                        <tr key={t.tecnico_id}>
                          <th scope="row">{t.tecnico}</th>
                          <td>{t.abiertos}</td>
                          <td>{t.cerrados}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
          <ListaResumen titulo="Casos abiertos" casos={resumen.casos_abiertos} vacio="No hay casos abiertos" onAbrir={onAbrir} />
          <ListaResumen titulo="Casos cerrados" casos={resumen.casos_cerrados} vacio="No hay casos cerrados" onAbrir={onAbrir} />
        </>
      )}
    </section>
  );
}
