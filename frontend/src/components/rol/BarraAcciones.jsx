import { useContextoRol } from "../../context/RolContext.jsx";
import Boton from "../ui/Boton.jsx";

export default function BarraAcciones({ onExportar, onGuardar, guardando }) {
  const {
    fecha,
    setFecha,
    presentes,
    borrador,
    generando,
    generar,
    limpiarAsignaciones,
    descartar,
  } = useContextoRol();

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end">
      <label className="flex flex-col gap-1.5 text-sm" htmlFor="fecha-rol">
        <span className="text-tenue">Fecha del rol</span>
        <input
          id="fecha-rol"
          type="date"
          value={fecha}
          onChange={(evento) => setFecha(evento.target.value)}
          className="rounded-lg border border-borde bg-hondo px-3 py-2.5 text-sm text-texto outline-none focus:border-primario"
        />
      </label>

      <div className="flex flex-1 flex-wrap gap-2">
        <Boton
          variante="acento"
          className="flex-1 sm:flex-none"
          disabled={generando || presentes.size === 0}
          onClick={() => generar([...presentes])}
        >
          {generando ? "Generando…" : "Generar rol"}
        </Boton>

        <Boton
          variante="neutro"
          disabled={borrador === null}
          onClick={limpiarAsignaciones}
          title="Deja a todos sin sala, sin perder la lista de presentes"
        >
          Limpiar asignaciones
        </Boton>

        <Boton variante="fantasma" disabled={borrador === null} onClick={descartar}>
          Descartar
        </Boton>

        <Boton
          variante="primario"
          disabled={borrador === null || guardando}
          onClick={onGuardar}
        >
          {guardando ? "Guardando…" : "Guardar"}
        </Boton>

        <Boton variante="excel" disabled={borrador === null} onClick={onExportar}>
          Exportar
        </Boton>
      </div>
    </div>
  );
}
