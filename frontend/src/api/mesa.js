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
