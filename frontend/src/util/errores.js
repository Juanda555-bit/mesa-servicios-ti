export const MENSAJE_CONEXION = "No se pudo conectar con el servidor";

// Reparte los motivos del 422 entre los campos conocidos y los que no tienen etiqueta.
export function camposPorNombre(error, etiquetas) {
  const porCampo = {};
  const sinEtiqueta = [];
  for (const { campo, motivo } of error?.campos ?? []) {
    if (Object.hasOwn(etiquetas, campo)) {
      (porCampo[campo] ??= []).push(motivo);
    } else {
      sinEtiqueta.push(motivo);
    }
  }
  return { porCampo, sinEtiqueta };
}
