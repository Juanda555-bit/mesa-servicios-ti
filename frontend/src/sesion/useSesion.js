import { useCallback, useEffect, useState } from "react";
import { ErrorApi, registrarSesionInvalida } from "../api/cliente.js";
import { iniciarSesion as apiIniciarSesion, usuarioActual } from "../api/mesa.js";
import { MENSAJE_CONEXION } from "../util/errores.js";
import { borrarToken, guardarToken, leerToken } from "./almacen.js";

const AVISO_VENCIDA = "Su sesión expiró o no es válida; inicie sesión de nuevo";

export function useSesion() {
  const [estado, setEstado] = useState(() => ({
    fase: leerToken() ? "comprobando" : "anonima",
    usuario: null,
    aviso: null,
  }));

  // Arranque: con token guardado, /auth/me decide la vista antes de pintar nada.
  useEffect(() => {
    if (!leerToken()) return undefined;
    const control = new AbortController();
    usuarioActual(control.signal)
      .then((u) => setEstado({ fase: "activa", usuario: { nombre: u.nombre, rol: u.rol }, aviso: null }))
      .catch((e) => {
        if (e?.name === "AbortError") return;
        // El 401 ya borró el token y avisó por registrarSesionInvalida; otros errores conservan el token.
        setEstado((previo) =>
          e instanceof ErrorApi && e.estado === 401
            ? previo
            : { fase: "anonima", usuario: null, aviso: MENSAJE_CONEXION },
        );
      });
    return () => control.abort();
  }, []);

  useEffect(() => {
    registrarSesionInvalida((detalle) =>
      setEstado({ fase: "anonima", usuario: null, aviso: detalle || AVISO_VENCIDA }),
    );
    return () => registrarSesionInvalida(null);
  }, []);

  const iniciarSesion = useCallback(async (correo, clave) => {
    const r = await apiIniciarSesion(correo, clave);
    guardarToken(r.access_token);
    setEstado({ fase: "activa", usuario: { nombre: r.nombre, rol: r.rol }, aviso: null });
  }, []);

  const cerrarSesion = useCallback(() => {
    borrarToken();
    setEstado({ fase: "anonima", usuario: null, aviso: null });
  }, []);

  return { ...estado, iniciarSesion, cerrarSesion };
}
