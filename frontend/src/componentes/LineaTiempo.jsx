import { etiquetaEvento, fechaHora } from "../util/formato.js";

export default function LineaTiempo({ eventos }) {
  if (eventos.length === 0) return <p className="vacio">Este caso aún no tiene eventos</p>;
  return (
    <ol className="tiempo">
      {eventos.map((e, i) => (
        <li key={i} className={`tiempo-evento tiempo-${e.tipo}`}>
          <p className="tiempo-titulo">
            <strong>{etiquetaEvento(e.tipo)}</strong>
            <time dateTime={e.momento}>{fechaHora(e.momento)}</time>
          </p>
          <p className="tiempo-detalle">{e.detalle}</p>
          <p className="tiempo-autor">Por {e.autor}</p>
        </li>
      ))}
    </ol>
  );
}
