const VARIANTES = {
  primario: "bg-primario text-hondo hover:bg-primario-fuerte",
  acento: "bg-acento text-white hover:bg-indigo-600",
  neutro: "bg-borde text-texto hover:bg-slate-600",
  peligro: "bg-peligro/10 text-peligro hover:bg-peligro/20",
  excel: "bg-green-700 text-white hover:bg-green-800",
  pdf: "bg-red-600 text-white hover:bg-red-700",
  fantasma: "border border-borde text-tenue hover:bg-white/5 hover:text-texto",
};

export default function Boton({ variante = "primario", className = "", type = "button", ...props }) {
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 ${VARIANTES[variante]} ${className}`}
      {...props}
    />
  );
}
