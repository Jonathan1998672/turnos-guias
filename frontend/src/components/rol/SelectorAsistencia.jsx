import Boton from "../ui/Boton.jsx";
import Casilla from "../ui/Casilla.jsx";
import Etiqueta from "../ui/Etiqueta.jsx";

/** Regla 4: el rol se arma con quien sí vino hoy. */
export default function SelectorAsistencia({
  guias,
  presentes,
  onAlternar,
  onMarcarTodos,
  onLimpiar,
}) {
  if (guias.length === 0) {
    return (
      <p className="py-3 text-center text-sm italic text-tenue">
        Registra guías en la pestaña «Guías» para poder armar el rol.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm text-tenue">
          {presentes.size} de {guias.length} presentes
        </span>
        <span className="flex gap-1">
          <Boton variante="fantasma" className="px-2 py-1 text-xs" onClick={onMarcarTodos}>
            Todos
          </Boton>
          <Boton variante="fantasma" className="px-2 py-1 text-xs" onClick={onLimpiar}>
            Ninguno
          </Boton>
        </span>
      </div>

      <ul className="flex max-h-72 flex-col gap-1.5 overflow-y-auto pr-1">
        {guias.map((guia) => (
          <li
            key={guia.id}
            className="flex items-center justify-between gap-2 rounded-lg border border-borde bg-hondo px-3 py-2"
          >
            <Casilla
              etiqueta={guia.nombre}
              checked={presentes.has(guia.id)}
              onChange={() => onAlternar(guia.id)}
            />
            {guia.es_super && <Etiqueta tono="oro">Súper</Etiqueta>}
          </li>
        ))}
      </ul>
    </div>
  );
}
