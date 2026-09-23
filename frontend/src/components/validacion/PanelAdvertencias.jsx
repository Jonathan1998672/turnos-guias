import { useContextoRol } from "../../context/RolContext.jsx";
import Advertencia from "./Advertencia.jsx";

export default function PanelAdvertencias() {
  const { borrador, validacion, validando } = useContextoRol();

  if (borrador === null) {
    return <p className="py-3 text-center text-sm italic text-tenue">Sin rol que validar.</p>;
  }

  if (validacion === null) {
    return <p className="py-3 text-center text-sm italic text-tenue">Validando…</p>;
  }

  const errores = validacion.advertencias.filter((a) => a.nivel === "error");
  const avisos = validacion.advertencias.filter((a) => a.nivel !== "error");

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between text-xs text-tenue">
        <span>
          {errores.length} {errores.length === 1 ? "error" : "errores"} · {avisos.length}{" "}
          {avisos.length === 1 ? "aviso" : "avisos"}
        </span>
        {validando && <span className="italic">revisando…</span>}
      </div>

      {validacion.advertencias.length === 0 ? (
        <p className="rounded border-l-[3px] border-l-exito bg-exito/10 px-3 py-2.5 text-center text-sm font-medium text-emerald-200">
          Todo en orden. Sin advertencias.
        </p>
      ) : (
        <ul className="flex max-h-[26rem] flex-col gap-1.5 overflow-y-auto pr-1">
          {[...errores, ...avisos].map((advertencia, indice) => (
            <Advertencia key={`${advertencia.regla}-${indice}`} advertencia={advertencia} />
          ))}
        </ul>
      )}
    </div>
  );
}
