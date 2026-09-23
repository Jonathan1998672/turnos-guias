import { useCallback, useState } from "react";

import { generarRol } from "../api/roles.js";
import { fechaISO } from "../lib/formato.js";

/** El borrador del rol que se está editando en pantalla.
 *
 * Vive solo en memoria hasta que se guarda o se exporta. Todas las ediciones
 * son inmutables: se construye un borrador nuevo en vez de mutar el actual,
 * que es lo que le permite a React saber que tiene que volver a pintar.
 */
export function useRol({ turnoId, salas, bloqueComidaId }) {
  const [fecha, setFecha] = useState(fechaISO());
  const [borrador, setBorrador] = useState(null);
  const [rolId, setRolId] = useState(null);
  const [generando, setGenerando] = useState(false);
  const [error, setError] = useState(null);

  const generar = useCallback(
    async (guiasPresentes) => {
      setError(null);

      if (guiasPresentes.length === 0) {
        setError({ mensaje: "Marca al menos un guía presente." });
        return;
      }

      setGenerando(true);
      try {
        const { borrador: nuevo } = await generarRol({
          fecha,
          turno_id: turnoId,
          guias_presentes: guiasPresentes,
        });
        setBorrador(nuevo);
        setRolId(null);
      } catch (fallo) {
        setError({ mensaje: fallo.message, detalles: fallo.detalles ?? [] });
        setBorrador(null);
      } finally {
        setGenerando(false);
      }
    },
    [fecha, turnoId],
  );

  /** Trae un rol del historial a la mesa de edición. */
  const cargar = useCallback((detalle) => {
    setRolId(detalle.id);
    setFecha(detalle.fecha);
    setError(null);
    setBorrador({
      fecha: detalle.fecha,
      turno_id: detalle.turno_id,
      participantes: detalle.participantes,
      asignaciones: detalle.asignaciones,
      notas: detalle.notas ?? null,
    });
  }, []);

  const asignarSala = useCallback(
    (guiaId, bloqueId, salaId) => {
      setBorrador((actual) => {
        if (actual === null) return actual;

        const existe = actual.asignaciones.some(
          (a) => a.guia_id === guiaId && a.bloque_id === bloqueId,
        );

        // Un rol recuperado del historial no trae las celdas vacías, así que
        // la primera edición de una celda así tiene que crearla.
        const asignaciones = existe
          ? actual.asignaciones.map((asignacion) =>
              asignacion.guia_id === guiaId && asignacion.bloque_id === bloqueId
                ? { ...asignacion, sala_id: salaId }
                : asignacion,
            )
          : [
              ...actual.asignaciones,
              { guia_id: guiaId, bloque_id: bloqueId, sala_id: salaId },
            ];

        // Igual que en el prototipo: cambiar de sala en el bloque de la comida
        // arrastra la hora sugerida de esa sala.
        const sala = salas.find((s) => s.id === salaId);
        const participantes =
          bloqueId === bloqueComidaId && sala
            ? actual.participantes.map((participante) =>
                participante.guia_id === guiaId
                  ? { ...participante, hora_comida: sala.comida_default }
                  : participante,
              )
            : actual.participantes;

        return { ...actual, asignaciones, participantes };
      });
    },
    [salas, bloqueComidaId],
  );

  const cambiarComida = useCallback((guiaId, hora) => {
    setBorrador((actual) =>
      actual === null
        ? actual
        : {
            ...actual,
            participantes: actual.participantes.map((participante) =>
              participante.guia_id === guiaId
                ? { ...participante, hora_comida: hora }
                : participante,
            ),
          },
    );
  }, []);

  const limpiarAsignaciones = useCallback(() => {
    setBorrador((actual) =>
      actual === null
        ? actual
        : {
            ...actual,
            asignaciones: actual.asignaciones.map((asignacion) => ({
              ...asignacion,
              sala_id: null,
            })),
          },
    );
  }, []);

  const descartar = useCallback(() => {
    setBorrador(null);
    setRolId(null);
    setError(null);
  }, []);

  return {
    fecha,
    setFecha,
    borrador,
    setBorrador,
    rolId,
    setRolId,
    generando,
    error,
    generar,
    cargar,
    asignarSala,
    cambiarComida,
    limpiarAsignaciones,
    descartar,
  };
}
