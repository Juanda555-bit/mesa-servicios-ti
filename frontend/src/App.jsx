import { useState } from "react";
import Cargando from "./componentes/Cargando.jsx";
import Encabezado from "./componentes/Encabezado.jsx";
import InicioSesion from "./componentes/InicioSesion.jsx";
import { SECCIONES_POR_ROL } from "./secciones.js";
import { useSesion } from "./sesion/useSesion.js";

function Contenido({ usuario, onCerrarSesion }) {
  const secciones = SECCIONES_POR_ROL[usuario.rol] ?? [];
  const [seleccion, setSeleccion] = useState(null);
  const actual = secciones.find((s) => s.clave === seleccion) ?? secciones[0];

  return (
    <>
      <Encabezado
        usuario={usuario}
        secciones={secciones}
        seccion={actual?.clave}
        onSeccion={setSeleccion}
        onCerrarSesion={onCerrarSesion}
      />
      <main className="contenido">{actual && <h1>{actual.titulo}</h1>}</main>
    </>
  );
}

export default function App() {
  const { fase, usuario, aviso, iniciarSesion, cerrarSesion } = useSesion();

  if (fase === "comprobando") return <Cargando texto="Comprobando la sesión…" />;
  if (fase !== "activa") return <InicioSesion aviso={aviso} onIniciar={iniciarSesion} />;
  // key por rol: al cambiar de usuario se descartan sección y estado de la sesión anterior.
  return <Contenido key={usuario.rol} usuario={usuario} onCerrarSesion={cerrarSesion} />;
}
