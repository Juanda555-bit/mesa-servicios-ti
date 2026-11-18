import { useState } from "react";
import Aviso from "./Aviso.jsx";
import Campo from "./Campo.jsx";
import { camposPorNombre } from "../util/errores.js";

const ETIQUETAS = { username: "Correo", password: "Contraseña" };

export default function InicioSesion({ aviso, onIniciar }) {
  const [correo, setCorreo] = useState("");
  const [clave, setClave] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState(null);

  async function enviar(evento) {
    evento.preventDefault();
    if (enviando) return;
    setEnviando(true);
    setError(null);
    try {
      await onIniciar(correo.trim(), clave);
    } catch (e) {
      setError(e);
      setEnviando(false);
    }
  }

  const { porCampo, sinEtiqueta } = camposPorNombre(error, ETIQUETAS);
  const mensaje = error ? (error.estado === 422 ? sinEtiqueta.join(". ") : error.detalle) : null;

  return (
    <main className="acceso">
      <section className="acceso-panel" aria-labelledby="titulo-acceso">
        <h1 id="titulo-acceso">Mesa de Servicios TI</h1>
        <p className="acceso-subtitulo">Inicie sesión para reportar y dar seguimiento a los casos.</p>
        {!error && <Aviso tipo="info">{aviso}</Aviso>}
        <form onSubmit={enviar}>
          <Campo etiqueta="Correo" motivos={porCampo.username}>
            {(props) => (
              <input
                {...props}
                type="email"
                name="username"
                autoComplete="username"
                required
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
              />
            )}
          </Campo>
          <Campo etiqueta="Contraseña" motivos={porCampo.password}>
            {(props) => (
              <input
                {...props}
                type="password"
                name="password"
                autoComplete="current-password"
                required
                value={clave}
                onChange={(e) => setClave(e.target.value)}
              />
            )}
          </Campo>
          <Aviso tipo="error">{mensaje}</Aviso>
          <button type="submit" className="boton" disabled={enviando}>
            {enviando ? "Entrando…" : "Iniciar sesión"}
          </button>
        </form>
      </section>
    </main>
  );
}
