import { useCallback, useState } from "react";
import AccionesTecnico from "./acciones/AccionesTecnico.jsx";
import DetalleCaso from "./pantallas/DetalleCaso.jsx";
import Cargando from "./componentes/Cargando.jsx";
import Encabezado from "./componentes/Encabezado.jsx";
import InicioSesion from "./componentes/InicioSesion.jsx";
import ListaCasos from "./pantallas/ListaCasos.jsx";
import ReportarCaso from "./pantallas/ReportarCaso.jsx";
import { SECCIONES_POR_ROL } from "./secciones.js";
import { useSesion } from "./sesion/useSesion.js";

function Contenido({ usuario, onCerrarSesion }) {
  const secciones = SECCIONES_POR_ROL[usuario.rol] ?? [];
  const [seleccion, setSeleccion] = useState(null);
  const actual = secciones.find((s) => s.clave === seleccion) ?? secciones[0];
  const [casoId, setCasoId] = useState(null);
  const [avisoLista, setAvisoLista] = useState(null);

  const cambiarSeccion = (clave) => {
    setSeleccion(clave);
    setCasoId(null);
    setAvisoLista(null);
  };
  const volver = () => setCasoId(null);
  // Solo por rol: la API decide si el técnico es el responsable (403). Se sustituye en T7.
  const acciones =
    usuario.rol === "tecnico"
      ? (caso, recargar) => <AccionesTecnico caso={caso} recargar={recargar} />
      : undefined;
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
        {["mis-casos", "asignados", "todos"].includes(actual?.clave) &&
          (casoId ? (
            <DetalleCaso casoId={casoId} onVolver={volver} onPerderAcceso={perderAcceso} acciones={acciones} />
          ) : (
            <ListaCasos key={actual.clave} titulo={actual.titulo} aviso={avisoLista} onAbrir={setCasoId} />
          ))}
        {actual?.clave === "tablero" && <h1>{actual.titulo}</h1>}
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
