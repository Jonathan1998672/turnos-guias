import { useEffect, useState } from "react";

import { validarRol } from "../api/roles.js";

const RETRASO_MS = 300;

/** Revalida el borrador en el backend cada vez que se edita.
 *
 * Dos detalles importantes: el `setTimeout` evita disparar una petición por
 * cada tecla, y el `AbortController` cancela la petición anterior para que una
 * respuesta lenta no pise a una más reciente. La función que devuelve el
 * `useEffect` es la que limpia ambas cosas.
 */
export function useValidacion(borrador) {
  const [validacion, setValidacion] = useState(null);
  const [validando, setValidando] = useState(false);

  useEffect(() => {
    if (borrador === null) {
      setValidacion(null);
      return undefined;
    }

    const controlador = new AbortController();

    const temporizador = setTimeout(async () => {
      setValidando(true);

      try {
        const resultado = await validarRol(borrador, { signal: controlador.signal });
        if (!controlador.signal.aborted) setValidacion(resultado);
      } catch (fallo) {
        if (fallo.name !== "AbortError") {
          setValidacion({
            valido: false,
            advertencias: [
              { nivel: "error", regla: "sin_asignar", mensaje: `No se pudo validar: ${fallo.message}` },
            ],
          });
        }
      } finally {
        if (!controlador.signal.aborted) setValidando(false);
      }
    }, RETRASO_MS);

    return () => {
      clearTimeout(temporizador);
      controlador.abort();
    };
  }, [borrador]);

  return { validacion, validando };
}
