import { HORAS_COMIDA } from "../../lib/constantes.js";
import { formatearHora } from "../../lib/formato.js";

const COLORES = {
  "13:30:00": "border-alerta text-yellow-200",
  "14:00:00": "border-blue-500 text-blue-200",
};

export default function SelectorComida({ valor, onCambiar }) {
  return (
    <select
      className={`w-full min-w-24 rounded-md border bg-hondo px-2 py-2 text-xs font-semibold outline-none ${
        COLORES[valor] ?? "border-borde text-texto"
      }`}
      value={valor ?? HORAS_COMIDA[0]}
      onChange={(evento) => onCambiar(evento.target.value)}
    >
      {HORAS_COMIDA.map((hora) => (
        <option key={hora} value={hora}>
          {formatearHora(hora)}
        </option>
      ))}
    </select>
  );
}
