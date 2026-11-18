import AccionesCoordinador from "./AccionesCoordinador.jsx";
import AccionesTecnico from "./AccionesTecnico.jsx";

// Elige las acciones por rol y estado. No decide permisos: la API valida (403/400).
export default function AccionesCaso({ rol, caso, recargar }) {
  if (caso.estado === "Cerrado") return null;
  if (rol === "tecnico") return <AccionesTecnico caso={caso} recargar={recargar} />;
  if (rol === "coordinador") return <AccionesCoordinador caso={caso} recargar={recargar} />;
  return null;
}
