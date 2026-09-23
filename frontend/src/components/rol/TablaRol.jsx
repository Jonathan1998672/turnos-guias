import { useContextoRol } from "../../context/RolContext.jsx";
import FilaRol from "./FilaRol.jsx";

/** guia_id -> (bloque_id -> sala_id), para que cada fila lea lo suyo de un tirón. */
function indexarAsignaciones(asignaciones) {
  const indice = new Map();

  for (const asignacion of asignaciones) {
    if (!indice.has(asignacion.guia_id)) indice.set(asignacion.guia_id, new Map());
    indice.get(asignacion.guia_id).set(asignacion.bloque_id, asignacion.sala_id);
  }

  return indice;
}

export default function TablaRol() {
  const { borrador, bloques, salas, guiasDelBorrador, validacion, asignarSala, cambiarComida } =
    useContextoRol();

  if (borrador === null) {
    return (
      <p className="py-6 text-center text-sm italic text-tenue">
        Marca quién asistió y genera el rol para empezar.
      </p>
    );
  }

  const asignaciones = indexarAsignaciones(borrador.asignaciones);
  const comidas = new Map(borrador.participantes.map((p) => [p.guia_id, p.hora_comida]));
  const conProblema = new Set(
    (validacion?.advertencias ?? [])
      .filter((a) => a.nivel === "error" && a.guia_id !== null)
      .map((a) => a.guia_id),
  );

  return (
    <>
      <span className="text-xs italic text-tenue md:hidden">⇄ Desliza la tabla</span>

      <div className="w-full overflow-x-auto rounded-lg border border-borde">
        <table className="w-full min-w-[640px] border-collapse text-sm">
          <thead>
            <tr>
              <th className="sticky top-0 z-10 border border-borde bg-[#111c44] px-2 py-2.5 text-left font-semibold text-primario">
                Guía
              </th>
              {bloques.map((bloque) => (
                <th
                  key={bloque.id}
                  className="sticky top-0 z-10 whitespace-nowrap border border-borde bg-[#111c44] px-2 py-2.5 text-left font-semibold text-primario"
                >
                  {bloque.etiqueta}
                </th>
              ))}
              <th className="sticky top-0 z-10 whitespace-nowrap border border-borde bg-[#111c44] px-2 py-2.5 text-left font-semibold text-primario">
                Hora de comida
              </th>
            </tr>
          </thead>

          <tbody>
            {guiasDelBorrador.map((guia) => (
              <FilaRol
                key={guia.id}
                guia={guia}
                bloques={bloques}
                salas={salas}
                salaPorBloque={asignaciones.get(guia.id) ?? new Map()}
                horaComida={comidas.get(guia.id)}
                conProblema={conProblema.has(guia.id)}
                onAsignarSala={asignarSala}
                onCambiarComida={cambiarComida}
              />
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
