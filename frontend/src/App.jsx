import { useCallback, useState } from "react";
import AccionesCaso from "./acciones/AccionesCaso.jsx";
import DetalleCaso from "./pantallas/DetalleCaso.jsx";
import Cargando from "./componentes/Cargando.jsx";
import Encabezado from "./componentes/Encabezado.jsx";
import InicioSesion from "./componentes/InicioSesion.jsx";
import ListaCasos from "./pantallas/ListaCasos.jsx";
import ReportarCaso from "./pantallas/ReportarCaso.jsx";
import Tablero from "./pantallas/Tablero.jsx";
import { SECCIONES_POR_ROL } from "./secciones.js";
import { useSesion } from "./sesion/useSesion.js";

function Contenido({ usuario, onCerrarSesion }) {
  const secciones = SECCIONES_POR_ROL[usuario.rol] ?? [];
  const [seleccion, setSeleccion] = useState(null);
  const actual = secciones.find((s) => s.clave === seleccion) ?? secciones[0];
  const [casoId, setCasoId] = useState(null);
  const [avisoLista, setAvisoLista] = useState(null);
  const Vista = actual?.clave === "tablero" ? Tablero : ListaCasos;

  const cambiarSeccion = (clave) => {
    setSeleccion(clave);
    setCasoId(null);
    setAvisoLista(null);
  };
  const volver = () => setCasoId(null);
  // Selección por rol y estado; la API decide los permisos reales (403/400).
  const acciones = (caso, recargar) => <AccionesCaso rol={usuario.rol} caso={caso} recargar={recargar} />;
  // Perdió el acceso (403/404): se muestra el detalle de la API y se vuelve a la lista.
  const perderAcceso = useCallback((detalle) => {
    setCasoId(null);
    setAvisoLista(detalle);
  }, []);

  return (
    <>
      <Encabezado
        usuario={usuario}
        secciones={secciones}
        seccion={actual?.clave}
        onSeccion={cambiarSeccion}
        onCerrarSesion={onCerrarSesion}
      />
      <main className="contenido">
        {actual?.clave === "reportar" && <ReportarCaso />}
        {["mis-casos", "asignados", "todos", "tablero"].includes(actual?.clave) &&
          (casoId ? (
            <DetalleCaso casoId={casoId} onVolver={volver} onPerderAcceso={perderAcceso} acciones={acciones} />
          ) : (
            <Vista key={actual.clave} titulo={actual.titulo} aviso={avisoLista} onAbrir={setCasoId} />
          ))}
      </main>
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
