import { fechaDia, fechaHora } from "../util/formato.js";

export default function DatosCaso({ caso }) {
  const filas = [
    ["Placa del equipo", caso.placa_equipo],
    ["Dependencia", caso.dependencia],
    ["Solicitante", `${caso.solicitante} (${caso.nombre_usuario}, ${caso.telefono})`],
    ["Fecha de la falla", fechaDia(caso.fecha)],
    ["Registrado", fechaHora(caso.creado_en)],
    ["Prioridad", caso.prioridad ?? "Sin definir"],
    ["Responsable", caso.tecnico ?? "Sin asignar"],
  ];
  if (caso.resuelto_en) filas.push(["Resuelto", fechaHora(caso.resuelto_en)]);
  if (caso.cerrado_en) filas.push(["Cerrado", fechaHora(caso.cerrado_en)]);

  return (
    <>
      <dl className="datos">
        {filas.map(([nombre, valor]) => (
          <div key={nombre} className="datos-fila">
            <dt>{nombre}</dt>
            <dd>{valor}</dd>
          </div>
        ))}
      </dl>
      <h2>Descripción de la falla</h2>
      <p className="texto-largo">{caso.descripcion}</p>
      {caso.solucion && (
        <>
          <h2>Solución</h2>
          <p className="texto-largo">{caso.solucion}</p>
        </>
      )}
    </>
  );
}
