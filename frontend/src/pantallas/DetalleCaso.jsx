import { useCallback, useEffect, useState } from "react";
import { obtenerCaso, obtenerHistorial } from "../api/mesa.js";
import Aviso from "../componentes/Aviso.jsx";
import Cargando from "../componentes/Cargando.jsx";
import DatosCaso from "../componentes/DatosCaso.jsx";
import LineaTiempo from "../componentes/LineaTiempo.jsx";

// `acciones(caso, recargar)`: espacio para las acciones por rol (T6/T7); vacío por ahora.
export default function DetalleCaso({ casoId, onVolver, onPerderAcceso, acciones }) {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState(null);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    const control = new AbortController();
    // Las dos lecturas son independientes: se lanzan a la vez.
    Promise.all([obtenerCaso(casoId, control.signal), obtenerHistorial(casoId, control.signal)])
      .then(([caso, historial]) => {
        setDatos({ caso, historial });
        setError(null);
      })
      .catch((e) => {
        if (e?.name === "AbortError") return;
        if (e?.estado === 403 || e?.estado === 404) onPerderAcceso(e.detalle);
        else setError(e.detalle ?? "No se pudo cargar el caso");
      });
    return () => control.abort();
  }, [casoId, version, onPerderAcceso]);

  const recargar = useCallback(() => setVersion((v) => v + 1), []);

  return (
    <section aria-labelledby="titulo-caso">
      <p>
        <button type="button" className="boton boton-secundario" onClick={onVolver}>
          Volver a la lista
        </button>{" "}
        <button type="button" className="boton boton-secundario" onClick={recargar}>
          Actualizar
        </button>
      </p>
      {error && <Aviso tipo="error">{error}</Aviso>}
      {!datos ? (
        !error && <Cargando />
      ) : (
        <>
          <h1 id="titulo-caso">
            Caso #{datos.caso.id}{" "}
            <span className={`estado estado-${datos.caso.estado.toLowerCase().replace(/\s+/g, "-")}`}>{datos.caso.estado}</span>
          </h1>
          <div className="detalle-rejilla">
            <div>
              <DatosCaso caso={datos.caso} />
              {acciones?.(datos.caso, recargar)}
            </div>
            <div>
              <h2>Línea de tiempo</h2>
              <LineaTiempo eventos={datos.historial} />
            </div>
          </div>
        </>
      )}
    </section>
  );
}
