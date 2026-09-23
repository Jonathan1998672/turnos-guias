import { api } from "./client.js";

export const obtenerSalas = (opciones) => api.get("/salas", opciones);
export const obtenerParesComida = (opciones) => api.get("/salas/pares-comida", opciones);
