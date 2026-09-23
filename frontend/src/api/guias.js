import { api } from "./client.js";

export const obtenerGuias = ({ soloActivos = false, signal } = {}) =>
  api.get(`/guias${soloActivos ? "?solo_activos=true" : ""}`, { signal });

export const crearGuia = (datos) => api.post("/guias", datos);
export const actualizarGuia = (id, datos) => api.patch(`/guias/${id}`, datos);
export const darDeBajaGuia = (id) => api.delete(`/guias/${id}`);

export const reemplazarCertificaciones = (id, salasCertificadas) =>
  api.put(`/guias/${id}/certificaciones`, { salas_certificadas: salasCertificadas });
