import { useCallback, useEffect, useState } from "react";

import { actualizarGuia, crearGuia, darDeBajaGuia, obtenerGuias } from "../api/guias.js";

/** Catálogo de guías con las operaciones de alta, edición y baja.
 *
 * Después de cada mutación se vuelve a pedir la lista: es un viaje extra a la
 * API, pero garantiza que el orden y las reglas del backend se respeten.
 */
export function useGuias({ soloActivos = false } = {}) {
  const [guias, setGuias] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const recargar = useCallback(async () => {
    setCargando(true);
    setError(null);

    try {
      setGuias(await obtenerGuias({ soloActivos }));
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setCargando(false);
    }
  }, [soloActivos]);

  useEffect(() => {
    recargar();
  }, [recargar]);

  const agregar = useCallback(
    async (datos) => {
      const creado = await crearGuia(datos);
      await recargar();
      return creado;
    },
    [recargar],
  );

  const editar = useCallback(
    async (id, datos) => {
      const actualizado = await actualizarGuia(id, datos);
      await recargar();
      return actualizado;
    },
    [recargar],
  );

  const darDeBaja = useCallback(
    async (id) => {
      await darDeBajaGuia(id);
      await recargar();
    },
    [recargar],
  );

  const superGuia = guias.find((guia) => guia.es_super && guia.activo) ?? null;

  return { guias, superGuia, cargando, error, recargar, agregar, editar, darDeBaja };
}
