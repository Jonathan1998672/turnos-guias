const TONOS = {
  error: "border-peligro bg-peligro/15 text-red-200",
  alerta: "border-alerta bg-alerta/10 text-amber-100",
  exito: "border-exito bg-exito/10 text-emerald-200",
  info: "border-borde bg-white/5 text-tenue",
};

export default function Aviso({ tono = "error", titulo, detalles = [], children }) {
  return (
    <div className={`rounded-lg border px-4 py-3 text-sm leading-snug ${TONOS[tono]}`}>
      {titulo && <strong className="mr-1">{titulo}</strong>}
      {children}
      {detalles.length > 0 && (
        <ul className="mt-1 list-inside list-disc text-xs opacity-80">
          {detalles.map((detalle) => (
            <li key={detalle}>{detalle}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
