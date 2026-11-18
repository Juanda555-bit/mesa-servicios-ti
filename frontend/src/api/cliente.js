import { borrarToken, leerToken } from "../sesion/almacen.js";

const BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");

export class ErrorApi extends Error {
  constructor(estado, detalle, campos = []) {
    super(detalle);
    this.estado = estado;
    this.detalle = detalle;
    this.campos = campos;
  }
}

let alSesionInvalida = null;

export function registrarSesionInvalida(fn) {
  alSesionInvalida = fn;
}

// Único punto de acceso a la API: añade Bearer, traduce errores y trata el 401 global.
export async function pedir(ruta, { metodo = "GET", json, formulario, publico = false, senal } = {}) {
  const cabeceras = {};
  const token = leerToken();
  if (!publico && token) cabeceras.Authorization = `Bearer ${token}`;

  let cuerpo;
  if (json !== undefined) {
    cabeceras["Content-Type"] = "application/json";
    cuerpo = JSON.stringify(json);
  } else if (formulario) {
    cuerpo = new URLSearchParams(formulario);
  }

  let respuesta;
  try {
    respuesta = await fetch(BASE + ruta, { method: metodo, headers: cabeceras, body: cuerpo, signal: senal });
  } catch (e) {
    if (e?.name === "AbortError") throw e;
    throw new ErrorApi(0, "No se pudo conectar con el servidor");
  }

  const datos = respuesta.status === 204 ? null : await respuesta.json().catch(() => null);
  if (respuesta.ok) return datos;

  const detalle = typeof datos?.detalle === "string" ? datos.detalle : "No se pudo completar la solicitud";
  const error = new ErrorApi(respuesta.status, detalle, Array.isArray(datos?.campos) ? datos.campos : []);
  if (respuesta.status === 401 && !publico) {
    borrarToken();
    if (alSesionInvalida) alSesionInvalida(detalle);
  }
  throw error;
}
