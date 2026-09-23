import { useCallback, useEffect, useState } from "react";

import { eliminarRol, obtenerRol, obtenerRoles } from "../api/roles.js";

/** Los últimos roles guardados, para poder reabrirlos o borrarlos. */
export function useHistorial() {
  const [roles, setRoles] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const recargar = useCallback(async () => {
    setCargando(true);
    setError(null);

    try {
      setRoles(await obtenerRoles());
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    recargar();
  }, [recargar]);

  const abrir = useCallback((rolId) => obtenerRol(rolId), []);

  const borrar = useCallback(
    async (rolId) => {
      await eliminarRol(rolId);
      await recargar();
    },
    [recargar],
  );

  return { roles, cargando, error, recargar, abrir, borrar };
}
