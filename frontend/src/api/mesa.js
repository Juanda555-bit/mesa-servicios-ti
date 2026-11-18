import { pedir } from "./cliente.js";

// El login es público: su 401 lo muestra la pantalla de inicio, no el manejo global.
export function iniciarSesion(correo, clave) {
  return pedir("/auth/login", {
    metodo: "POST",
    formulario: { username: correo, password: clave },
    publico: true,
  });
}

export function usuarioActual(senal) {
  return pedir("/auth/me", { senal });
}

export function listarDependencias(senal) {
  return pedir("/dependencias", { senal });
}

export function reportarCaso(datos) {
  return pedir("/casos", { metodo: "POST", json: datos });
}

export function listarCasos(senal) {
  return pedir("/casos", { senal });
}

export function obtenerCaso(id, senal) {
  return pedir(`/casos/${id}`, { senal });
}

export function obtenerHistorial(id, senal) {
  return pedir(`/casos/${id}/historial`, { senal });
}

export function iniciarAtencion(id) {
  return pedir(`/casos/${id}/iniciar-atencion`, { metodo: "POST" });
}

export function registrarIntervencion(id, datos) {
  return pedir(`/casos/${id}/intervenciones`, { metodo: "POST", json: datos });
}

export function resolverCaso(id, datos) {
  return pedir(`/casos/${id}/resolver`, { metodo: "POST", json: datos });
}
