import { useId } from "react";

// Etiqueta + control + motivos del 422 bajo el campo. `children` recibe las props de accesibilidad.
export default function Campo({ etiqueta, motivos = [], children }) {
  const id = useId();
  const idError = `${id}-error`;
  const hayError = motivos.length > 0;
  return (
    <div className={`campo${hayError ? " campo-error" : ""}`}>
      <label htmlFor={id}>{etiqueta}</label>
      {children({ id, "aria-invalid": hayError || undefined, "aria-describedby": hayError ? idError : undefined })}
      {hayError && (
        <p className="campo-motivo" id={idError}>
          {motivos.join(". ")}
        </p>
      )}
    </div>
  );
}
