import { useCallback, useState } from "react";

/** Empuja un blob al disco del usuario a través de un <a download> temporal. */
function guardarEnDisco(blob, nombreArchivo) {
  const url = URL.createObjectURL(blob);
  const enlace = document.createElement("a");

  enlace.href = url;
  enlace.download = nombreArchivo;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();

  URL.revokeObjectURL(url);
}

export function useDescarga() {
  const [descargando, setDescargando] = useState(null);
  const [error, setError] = useState(null);

  const descargar = useCallback(async (formato, pedirArchivo) => {
    setError(null);
    setDescargando(formato);

    try {
      const { blob, nombreArchivo } = await pedirArchivo();
      guardarEnDisco(blob, nombreArchivo);
    } catch (fallo) {
      setError(fallo.message);
    } finally {
      setDescargando(null);
    }
  }, []);

  return { descargar, descargando, error };
}
