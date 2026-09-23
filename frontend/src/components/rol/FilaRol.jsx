import Etiqueta from "../ui/Etiqueta.jsx";
import SelectorComida from "./SelectorComida.jsx";
import SelectorSala from "./SelectorSala.jsx";

export default function FilaRol({
  guia,
  bloques,
  salas,
  salaPorBloque,
  horaComida,
  conProblema,
  onAsignarSala,
  onCambiarComida,
}) {
  return (
    <tr className={conProblema ? "bg-peligro/5" : "odd:bg-white/[0.02]"}>
      <th
        scope="row"
        className="border border-borde px-2 py-2 text-left align-middle text-sm font-semibold"
      >
        {guia.nombre}
        {guia.es_super && (
          <span className="ml-1">
            <Etiqueta tono="oro">Súper</Etiqueta>
          </span>
        )}
      </th>

      {bloques.map((bloque) => (
        <td key={bloque.id} className="border border-borde px-2 py-2 align-middle">
          <SelectorSala
            salas={salas}
            guia={guia}
            valor={salaPorBloque.get(bloque.id)}
            onCambiar={(salaId) => onAsignarSala(guia.id, bloque.id, salaId)}
          />
        </td>
      ))}

      <td className="border border-borde px-2 py-2 align-middle">
        <SelectorComida
          valor={horaComida}
          onCambiar={(hora) => onCambiarComida(guia.id, hora)}
        />
      </td>
    </tr>
  );
}
