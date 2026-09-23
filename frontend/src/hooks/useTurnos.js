import { useCallback, useEffect, useState } from "react";

import { obtenerTurnos } from "../api/turnos.js";

const CLAVE_POR_DEFECTO = "fin_de_semana";

/** Los turnos con sus bloques. Por ahora solo existe el de fin de semana. */
export function useTurnos() {
  const [turnos, setTurnos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const recargar = useCallback(async () => {
    setCargando(true);
    setError(null);

    try {
      setTurnos(await obtenerTurnos());
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    recargar();
  }, [recargar]);

  const turnoActivo = turnos.find((t) => t.clave === CLAVE_POR_DEFECTO) ?? turnos[0] ?? null;

  return { turnos, turnoActivo, bloques: turnoActivo?.bloques ?? [], cargando, error, recargar };
}
