import { formatearHora } from "../../lib/formato.js";
import Etiqueta from "../ui/Etiqueta.jsx";

function etiquetaDeRequisito(sala) {
  if (sala.solo_super) return <Etiqueta tono="oro">Exclusiva Súper</Etiqueta>;
  if (sala.es_funcion) return <Etiqueta tono="morado">Función</Etiqueta>;
  return <Etiqueta tono="neutro">Guía General</Etiqueta>;
}

/** Construye sala_id -> sala pareja, a partir de la lista de pares del backend. */
function mapearParejas(paresComida, salas) {
  const porId = new Map(salas.map((sala) => [sala.id, sala]));
  const parejas = new Map();

  for (const par of paresComida) {
    parejas.set(par.sala_a_id, porId.get(par.sala_b_id));
    parejas.set(par.sala_b_id, porId.get(par.sala_a_id));
  }

  return parejas;
}

export default function ListaSalas({ salas, paresComida = [] }) {
  const parejas = mapearParejas(paresComida, salas);

  if (salas.length === 0) {
    return (
      <p className="py-3 text-center text-sm italic text-tenue">
        No hay salas registradas. Corre el seed del backend.
      </p>
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {salas.map((sala) => {
        const pareja = parejas.get(sala.id);

        return (
          <li
            key={sala.id}
            className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-borde bg-hondo px-3 py-2.5 text-sm"
          >
            <div className="flex min-w-0 flex-col">
              <span className="font-semibold">
                {sala.codigo} · {sala.nombre}
              </span>
              <span className="text-xs text-tenue">
                Comida {formatearHora(sala.comida_default)}
                {pareja && ` · no empalma con ${pareja.codigo}`}
              </span>
            </div>
            {etiquetaDeRequisito(sala)}
          </li>
        );
      })}
    </ul>
  );
}
