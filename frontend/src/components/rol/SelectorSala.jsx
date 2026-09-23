import { SIN_ASIGNAR } from "../../lib/constantes.js";

/** Solo ofrece las salas que ese guía puede cubrir, igual que el prototipo. */
function salasPermitidas(salas, guia) {
  return salas.filter((sala) => {
    if (sala.solo_super) return guia.es_super;
    if (sala.es_funcion) return guia.salas_certificadas.includes(sala.id);
    return true;
  });
}

export default function SelectorSala({ salas, guia, valor, onCambiar }) {
  const permitidas = salasPermitidas(salas, guia);

  return (
    <select
      className="w-full min-w-36 rounded-md border border-borde bg-hondo px-2 py-2 text-xs text-texto outline-none focus:border-primario"
      value={valor ?? SIN_ASIGNAR}
      onChange={(evento) =>
        onCambiar(evento.target.value === SIN_ASIGNAR ? null : Number(evento.target.value))
      }
    >
      <option value={SIN_ASIGNAR}>— Sin asignar —</option>
      {permitidas.map((sala) => (
        <option key={sala.id} value={sala.id}>
          {sala.codigo} · {sala.nombre}
        </option>
      ))}
    </select>
  );
}
