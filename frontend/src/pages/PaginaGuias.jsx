import FormularioGuia from "../components/guias/FormularioGuia.jsx";
import ListaGuias from "../components/guias/ListaGuias.jsx";
import Aviso from "../components/ui/Aviso.jsx";
import Tarjeta from "../components/ui/Tarjeta.jsx";
import { useGuias } from "../hooks/useGuias.js";
import { useSalas } from "../hooks/useSalas.js";

export default function PaginaGuias() {
  const { salas, cargando: cargandoSalas } = useSalas();
  const { guias, superGuia, cargando, error, agregar, editar, darDeBaja } = useGuias();

  const salasDeFuncion = salas.filter((sala) => sala.es_funcion);

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_1.2fr]">
      <Tarjeta titulo="Registrar guía">
        {cargandoSalas ? (
          <p className="py-3 text-center text-sm italic text-tenue">Cargando salas…</p>
        ) : (
          <FormularioGuia
            salasDeFuncion={salasDeFuncion}
            superBloqueado={Boolean(superGuia)}
            limpiarAlGuardar
            onGuardar={agregar}
          />
        )}
      </Tarjeta>

      <Tarjeta titulo={`Guías registrados (${guias.length})`}>
        {error && <Aviso titulo="No se pudieron cargar los guías:">{error}</Aviso>}
        {cargando ? (
          <p className="py-3 text-center text-sm italic text-tenue">Cargando…</p>
        ) : (
          <ListaGuias
            guias={guias}
            salasDeFuncion={salasDeFuncion}
            superGuia={superGuia}
            onEditar={editar}
            onDarDeBaja={darDeBaja}
          />
        )}

        <p className="text-xs leading-relaxed text-tenue">
          Dar de baja es una baja lógica: el guía deja de aparecer al armar el rol, pero los roles
          anteriores conservan su historial.
        </p>
      </Tarjeta>
    </div>
  );
}
