const FORMATO_FECHA_HORA = new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short" });

// Fecha y hora UTC (ISO-8601) de la API, en hora local.
export function fechaHora(iso) {
  if (!iso) return "—";
  const fecha = new Date(iso);
  return Number.isNaN(fecha.getTime()) ? "—" : FORMATO_FECHA_HORA.format(fecha);
}

// Fecha AAAA-MM-DD de la API: se parte la cadena, sin Date (evita el desfase por zona horaria).
export function fechaDia(texto) {
  const partes = /^(\d{4})-(\d{2})-(\d{2})$/.exec(texto ?? "");
  return partes ? `${partes[3]}/${partes[2]}/${partes[1]}` : "—";
}

// Hoy en hora local como AAAA-MM-DD (solo para la ayuda `max` del formulario).
export function hoyLocal() {
  const d = new Date();
  const dos = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`;
}

const ETIQUETAS_EVENTO = {
  cambio_estado: "Cambio de estado",
  asignacion: "Asignación",
  reasignacion: "Reasignación",
  intervencion: "Intervención",
};

// Etiqueta legible del tipo de evento de la línea de tiempo; un tipo no previsto se muestra tal cual (RF-11).
export function etiquetaEvento(tipo) {
  return ETIQUETAS_EVENTO[tipo] ?? tipo;
}
