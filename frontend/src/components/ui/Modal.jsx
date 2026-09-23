import { useEffect } from "react";

export default function Modal({ abierto, titulo, descripcion, onCerrar, children }) {
  useEffect(() => {
    if (!abierto) return undefined;

    const alPresionar = (evento) => {
      if (evento.key === "Escape") onCerrar();
    };

    window.addEventListener("keydown", alPresionar);
    return () => window.removeEventListener("keydown", alPresionar);
  }, [abierto, onCerrar]);

  if (!abierto) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-fondo/80 p-4 backdrop-blur-sm"
      onClick={onCerrar}
    >
      <div
        className="flex w-full max-w-sm flex-col gap-4 rounded-xl border border-borde bg-tarjeta p-6 shadow-2xl"
        onClick={(evento) => evento.stopPropagation()}
      >
        <h3 className="text-lg font-semibold text-primario">{titulo}</h3>
        {descripcion && <p className="text-sm leading-snug text-tenue">{descripcion}</p>}
        {children}
      </div>
    </div>
  );
}
