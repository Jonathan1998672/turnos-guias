import { api } from "./client.js";

export const generarRol = (datos) => api.post("/roles/generar", datos);

export const validarRol = (borrador, { signal } = {}) =>
  api.post("/roles/validar", { borrador }, { signal });

export const guardarRol = (rol) => api.post("/roles", rol);
export const obtenerRol = (id) => api.get(`/roles/${id}`);
export const actualizarRol = (id, borrador) => api.patch(`/roles/${id}`, borrador);
export const eliminarRol = (id) => api.delete(`/roles/${id}`);

export const obtenerRoles = ({ fecha } = {}) =>
  api.get(`/roles${fecha ? `?fecha=${fecha}` : ""}`);
