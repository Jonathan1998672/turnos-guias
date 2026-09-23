import { api } from "./client.js";

export const obtenerTurnos = (opciones) => api.get("/turnos", opciones);
export const obtenerBloques = (turnoId, opciones) =>
  api.get(`/turnos/${turnoId}/bloques`, opciones);
