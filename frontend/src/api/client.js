const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

export class ErrorApi extends Error {
  constructor(mensaje, { status = 0, detalles = [] } = {}) {
    super(mensaje);
    this.name = "ErrorApi";
    this.status = status;
    this.detalles = detalles;
  }
}

async function leerError(respuesta) {
  try {
    const datos = await respuesta.json();
    return new ErrorApi(datos.mensaje ?? `Error ${respuesta.status}`, {
      status: respuesta.status,
      detalles: datos.detalles ?? [],
    });
  } catch {
    return new ErrorApi(`Error ${respuesta.status} al llamar a la API.`, {
      status: respuesta.status,
    });
  }
}

async function solicitar(ruta, { metodo = "GET", cuerpo, signal } = {}) {
  const respuesta = await fetch(`${BASE_URL}${ruta}`, {
    method: metodo,
    headers: cuerpo === undefined ? undefined : { "Content-Type": "application/json" },
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
    signal,
  });

  if (!respuesta.ok) throw await leerError(respuesta);
  if (respuesta.status === 204) return null;

  return respuesta.json();
}

export const api = {
  get: (ruta, opciones) => solicitar(ruta, opciones),
  post: (ruta, cuerpo, opciones) => solicitar(ruta, { ...opciones, metodo: "POST", cuerpo }),
  put: (ruta, cuerpo, opciones) => solicitar(ruta, { ...opciones, metodo: "PUT", cuerpo }),
  patch: (ruta, cuerpo, opciones) => solicitar(ruta, { ...opciones, metodo: "PATCH", cuerpo }),
  delete: (ruta, opciones) => solicitar(ruta, { ...opciones, metodo: "DELETE" }),
};

function nombreDesdeCabecera(cabecera, respaldo) {
  const coincidencia = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(cabecera ?? "");
  return coincidencia ? decodeURIComponent(coincidencia[1]) : respaldo;
}

/** Descarga binaria. Devuelve el blob y el nombre que propuso el backend. */
export async function solicitarArchivo(ruta, { metodo = "GET", cuerpo, respaldo = "rol" } = {}) {
  const respuesta = await fetch(`${BASE_URL}${ruta}`, {
    method: metodo,
    headers: cuerpo === undefined ? undefined : { "Content-Type": "application/json" },
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
  });

  if (!respuesta.ok) throw await leerError(respuesta);

  return {
    blob: await respuesta.blob(),
    nombreArchivo: nombreDesdeCabecera(respuesta.headers.get("Content-Disposition"), respaldo),
  };
}
