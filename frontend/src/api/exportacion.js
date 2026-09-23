import { solicitarArchivo } from "./client.js";

export const exportarBorrador = (formato, borrador) =>
  solicitarArchivo("/roles/exportar", {
    metodo: "POST",
    cuerpo: { formato, borrador },
    respaldo: `rol.${formato}`,
  });

export const exportarRolGuardado = (rolId, formato) =>
  solicitarArchivo(`/roles/${rolId}/exportar?formato=${formato}`, {
    respaldo: `rol.${formato}`,
  });
