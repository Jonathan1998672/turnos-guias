import { useCallback, useEffect, useState } from "react";

import { obtenerParesComida, obtenerSalas } from "../api/salas.js";

/** Catálogo de salas y las parejas que no pueden empalmar comida. */
export function useSalas() {
  const [salas, setSalas] = useState([]);
  const [paresComida, setParesComida] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const recargar = useCallback(async () => {
    setCargando(true);
    setError(null);

    try {
      const [listaSalas, listaPares] = await Promise.all([
        obtenerSalas(),
        obtenerParesComida(),
      ]);
      setSalas(listaSalas);
      setParesComida(listaPares);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setCargando(false);
    }
  }, []);

  useEffect(() => {
    recargar();
  }, [recargar]);

  return { salas, paresComida, cargando, error, recargar };
}
