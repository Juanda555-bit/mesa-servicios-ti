// Secciones de navegación por rol (docs/diseno.md §7). Solo configuración.
export const SECCIONES_POR_ROL = {
  solicitante: [
    { clave: "reportar", titulo: "Reportar caso" },
    { clave: "mis-casos", titulo: "Mis casos" },
  ],
  tecnico: [{ clave: "asignados", titulo: "Mis casos asignados" }],
  coordinador: [
    { clave: "tablero", titulo: "Tablero" },
    { clave: "todos", titulo: "Todos los casos" },
  ],
};

export const ETIQUETA_ROL = {
  solicitante: "Solicitante",
  tecnico: "Técnico",
  coordinador: "Coordinador",
};
