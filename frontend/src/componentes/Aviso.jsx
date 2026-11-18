// tipo: "error" | "exito" | "info". Los errores se anuncian de inmediato; el resto, sin interrumpir.
export default function Aviso({ tipo = "info", children }) {
  if (!children) return null;
  return (
    <p className={`aviso aviso-${tipo}`} role={tipo === "error" ? "alert" : "status"}>
      {children}
    </p>
  );
}
