import { useCallback, useMemo, useState } from "react";

import { actualizarRol, guardarRol } from "../api/roles.js";
import ModalExportar from "../components/exportacion/ModalExportar.jsx";
import BarraAcciones from "../components/rol/BarraAcciones.jsx";
import HistorialRoles from "../components/rol/HistorialRoles.jsx";
import SelectorAsistencia from "../components/rol/SelectorAsistencia.jsx";
import TablaRol from "../components/rol/TablaRol.jsx";
import Aviso from "../components/ui/Aviso.jsx";
import Tarjeta from "../components/ui/Tarjeta.jsx";
import PanelAdvertencias from "../components/validacion/PanelAdvertencias.jsx";
import { ProveedorRol } from "../context/RolContext.jsx";
import { useGuias } from "../hooks/useGuias.js";
import { useHistorial } from "../hooks/useHistorial.js";
import { useRol } from "../hooks/useRol.js";
import { useSalas } from "../hooks/useSalas.js";
import { useTurnos } from "../hooks/useTurnos.js";
import { useValidacion } from "../hooks/useValidacion.js";
import { bloqueDeComida } from "../lib/constantes.js";
import { fechaLarga } from "../lib/formato.js";

export default function PaginaRol() {
  const { salas, cargando: cargandoSalas, error: errorSalas } = useSalas();
  const { guias, cargando: cargandoGuias } = useGuias({ soloActivos: true });
  const { turnoActivo, bloques, cargando: cargandoTurnos } = useTurnos();
  const historial = useHistorial();

  const [presentes, setPresentes] = useState(() => new Set());
  const [modalAbierto, setModalAbierto] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState(null);

  const bloqueComida = bloqueDeComida(bloques);
  const rol = useRol({
    turnoId: turnoActivo?.id,
    salas,
    bloqueComidaId: bloqueComida?.id,
  });
  const { validacion, validando } = useValidacion(rol.borrador);

  const alternarPresente = useCallback((guiaId) => {
    setPresentes((actuales) => {
      const copia = new Set(actuales);
      if (copia.has(guiaId)) copia.delete(guiaId);
      else copia.add(guiaId);
      return copia;
    });
  }, []);

  const guiasDelBorrador = useMemo(() => {
    if (rol.borrador === null) return [];
    const enElRol = new Set(rol.borrador.participantes.map((p) => p.guia_id));
    return guias.filter((guia) => enElRol.has(guia.id));
  }, [rol.borrador, guias]);

  const abrirDelHistorial = async (rolId) => {
    setMensaje(null);
    try {
      const detalle = await historial.abrir(rolId);
      rol.cargar(detalle);
      setPresentes(new Set(detalle.participantes.map((p) => p.guia_id)));
    } catch (fallo) {
      setMensaje({ tono: "error", texto: fallo.message });
    }
  };

  const borrarDelHistorial = async (rolId) => {
    try {
      await historial.borrar(rolId);
      if (rol.rolId === rolId) rol.descartar();
    } catch (fallo) {
      setMensaje({ tono: "error", texto: fallo.message });
    }
  };

  const guardar = async () => {
    if (rol.borrador === null) return;

    setGuardando(true);
    setMensaje(null);

    try {
      if (rol.rolId === null) {
        const creado = await guardarRol({ ...rol.borrador, estado: "publicado" });
        rol.setRolId(creado.id);
        setMensaje({ tono: "exito", texto: "Rol guardado." });
      } else {
        await actualizarRol(rol.rolId, rol.borrador);
        setMensaje({ tono: "exito", texto: "Cambios guardados." });
      }
      await historial.recargar();
    } catch (fallo) {
      setMensaje({ tono: "error", texto: fallo.message, detalles: fallo.detalles ?? [] });
    } finally {
      setGuardando(false);
    }
  };

  const contexto = {
    ...rol,
    salas,
    bloques,
    guias,
    guiasDelBorrador,
    presentes,
    validacion,
    validando,
  };

  if (cargandoSalas || cargandoGuias || cargandoTurnos) {
    return (
      <Tarjeta>
        <p className="py-6 text-center text-sm italic text-tenue">Cargando catálogos…</p>
      </Tarjeta>
    );
  }

  if (errorSalas || turnoActivo === null) {
    return (
      <Aviso titulo="No se pudo cargar el catálogo:" detalles={["Revisa que el backend esté corriendo y que hayas ejecutado el seed."]}>
        {errorSalas ?? "No hay ningún turno configurado."}
      </Aviso>
    );
  }

  return (
    <ProveedorRol valor={contexto}>
      <div className="flex flex-col gap-4">
        <Tarjeta>
          <BarraAcciones
            onExportar={() => setModalAbierto(true)}
            onGuardar={guardar}
            guardando={guardando}
          />

          {rol.error && (
            <Aviso titulo="No se pudo generar:" detalles={rol.error.detalles}>
              {rol.error.mensaje}
            </Aviso>
          )}

          {mensaje && (
            <Aviso tono={mensaje.tono} detalles={mensaje.detalles}>
              {mensaje.texto}
            </Aviso>
          )}
        </Tarjeta>

        <div className="grid gap-4 xl:grid-cols-[18rem_1fr_20rem]">
          <div className="flex flex-col gap-4">
            <Tarjeta titulo="¿Quién vino hoy?">
              <SelectorAsistencia
                guias={guias}
                presentes={presentes}
                onAlternar={alternarPresente}
                onMarcarTodos={() => setPresentes(new Set(guias.map((g) => g.id)))}
                onLimpiar={() => setPresentes(new Set())}
              />
            </Tarjeta>

            <Tarjeta titulo="Historial">
              <HistorialRoles
                roles={historial.roles}
                cargando={historial.cargando}
                rolAbiertoId={rol.rolId}
                onAbrir={abrirDelHistorial}
                onBorrar={borrarDelHistorial}
              />
            </Tarjeta>
          </div>

          <Tarjeta
            titulo={`Rol · ${fechaLarga(rol.fecha)}`}
            acciones={
              rol.rolId !== null && (
                <span className="text-xs text-tenue">guardado #{rol.rolId}</span>
              )
            }
          >
            <TablaRol />
          </Tarjeta>

          <Tarjeta titulo="Validación">
            <PanelAdvertencias />
          </Tarjeta>
        </div>
      </div>

      <ModalExportar abierto={modalAbierto} onCerrar={() => setModalAbierto(false)} />
    </ProveedorRol>
  );
}
