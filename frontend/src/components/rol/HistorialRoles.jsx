import { fechaLarga } from "../../lib/formato.js";
import Boton from "../ui/Boton.jsx";
import Etiqueta from "../ui/Etiqueta.jsx";

export default function HistorialRoles({ roles, cargando, rolAbiertoId, onAbrir, onBorrar }) {
  if (cargando) {
    return <p className="py-3 text-center text-sm italic text-tenue">Cargando historial…</p>;
  }

  if (roles.length === 0) {
    return (
      <p className="py-3 text-center text-sm italic text-tenue">
        Todavía no hay roles guardados.
      </p>
    );
  }

  return (
    <ul className="flex max-h-72 flex-col gap-2 overflow-y-auto pr-1">
      {roles.map((rol) => (
        <li
          key={rol.id}
          className={`flex items-center justify-between gap-2 rounded-lg border bg-hondo px-3 py-2.5 text-sm ${
            rol.id === rolAbiertoId ? "border-primario" : "border-borde"
          }`}
        >
          <span className="flex min-w-0 flex-col">
            <span className="truncate font-semibold capitalize">{fechaLarga(rol.fecha)}</span>
            <span className="text-xs text-tenue">
              {rol.total_participantes} guías ·{" "}
              {rol.estado === "publicado" ? (
                <Etiqueta tono="exito">Publicado</Etiqueta>
              ) : (
                <Etiqueta tono="tenue">Borrador</Etiqueta>
              )}
            </span>
          </span>

          <span className="flex shrink-0 gap-1">
            <Boton variante="fantasma" className="px-2 py-1" onClick={() => onAbrir(rol.id)}>
              Abrir
            </Boton>
            <Boton
              variante="peligro"
              className="px-2 py-1"
              title="Borrar rol"
              onClick={() => onBorrar(rol.id)}
            >
              ✕
            </Boton>
          </span>
        </li>
      ))}
    </ul>
  );
}
