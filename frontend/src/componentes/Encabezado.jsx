import { ETIQUETA_ROL } from "../secciones.js";

export default function Encabezado({ usuario, secciones, seccion, onSeccion, onCerrarSesion }) {
  return (
    <header className="encabezado">
      <div className="encabezado-barra">
        <p className="marca">Mesa de Servicios TI</p>
        <p className="usuario">
          <span className="usuario-nombre">{usuario.nombre}</span>
          <span className="usuario-rol">{ETIQUETA_ROL[usuario.rol] ?? usuario.rol}</span>
        </p>
        <button type="button" className="boton boton-secundario" onClick={onCerrarSesion}>
          Cerrar sesión
        </button>
      </div>
      <nav className="navegacion" aria-label="Secciones">
        {secciones.map((s) => (
          <button
            key={s.clave}
            type="button"
            className="navegacion-enlace"
            aria-current={s.clave === seccion ? "page" : undefined}
            onClick={() => onSeccion(s.clave)}
          >
            {s.titulo}
          </button>
        ))}
      </nav>
    </header>
  );
}
