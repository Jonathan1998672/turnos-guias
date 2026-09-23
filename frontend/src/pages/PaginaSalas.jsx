import ListaSalas from "../components/salas/ListaSalas.jsx";
import Aviso from "../components/ui/Aviso.jsx";
import Tarjeta from "../components/ui/Tarjeta.jsx";
import { useSalas } from "../hooks/useSalas.js";
import { useTurnos } from "../hooks/useTurnos.js";
import { formatearHora } from "../lib/formato.js";

export default function PaginaSalas() {
  const { salas, paresComida, cargando, error } = useSalas();
  const { turnoActivo, bloques } = useTurnos();

  return (
    <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
      <Tarjeta titulo="Catálogo de salas">
        {error && <Aviso titulo="No se pudieron cargar las salas:">{error}</Aviso>}
        {cargando ? (
          <p className="py-3 text-center text-sm italic text-tenue">Cargando…</p>
        ) : (
          <ListaSalas salas={salas} paresComida={paresComida} />
        )}
      </Tarjeta>

      <Tarjeta titulo={`Bloques · ${turnoActivo?.nombre ?? "turno"}`}>
        {bloques.length === 0 ? (
          <p className="py-3 text-center text-sm italic text-tenue">Sin bloques configurados.</p>
        ) : (
          <ol className="flex flex-col gap-2">
            {bloques.map((bloque) => (
              <li
                key={bloque.id}
                className="flex items-center justify-between rounded-lg border border-borde bg-hondo px-3 py-2.5 text-sm"
              >
                <span className="font-semibold">{bloque.etiqueta}</span>
                <span className="text-xs text-tenue">
                  {formatearHora(bloque.hora_inicio)} – {formatearHora(bloque.hora_fin)}
                </span>
              </li>
            ))}
          </ol>
        )}

        <p className="text-xs leading-relaxed text-tenue">
          La comida cae dentro del bloque del mediodía y dura 30 minutos. Solo hay dos horarios
          posibles: 1:30 PM y 2:00 PM.
        </p>
      </Tarjeta>
    </div>
  );
}
