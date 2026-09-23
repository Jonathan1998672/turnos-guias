const TONOS = {
  neutro: "bg-borde text-acento",
  oro: "border border-oro/30 bg-oro/15 text-oro",
  primario: "bg-primario/15 text-primario",
  morado: "bg-purple-500/15 text-purple-400",
  exito: "bg-exito/15 text-exito",
  tenue: "bg-white/5 text-tenue",
};

export default function Etiqueta({ tono = "neutro", children }) {
  return (
    <span
      className={`whitespace-nowrap rounded px-1.5 py-0.5 text-xs font-medium ${TONOS[tono]}`}
    >
      {children}
    </span>
  );
}
