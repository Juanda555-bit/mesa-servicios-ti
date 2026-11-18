// Único lugar que toca sessionStorage. El token es una cadena opaca.
const CLAVE = "mesa_ti_token";

export function leerToken() {
  try {
    return sessionStorage.getItem(CLAVE);
  } catch {
    return null;
  }
}

export function guardarToken(token) {
  try {
    sessionStorage.setItem(CLAVE, token);
  } catch {
    /* sin almacenamiento: la sesión dura lo que dure la página */
  }
}

export function borrarToken() {
  try {
    sessionStorage.removeItem(CLAVE);
  } catch {
    /* nada que borrar */
  }
}
