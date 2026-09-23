/** "13:30:00" -> "1:30 PM". El backend siempre manda HH:MM:SS. */
export function formatearHora(hora) {
  if (!hora) return "";

  const [horasTexto, minutos] = hora.split(":");
  const horas = Number(horasTexto);
  const sufijo = horas >= 12 ? "PM" : "AM";
  const doce = horas % 12 === 0 ? 12 : horas % 12;

  return `${doce}:${minutos} ${sufijo}`;
}

/** Date -> "2026-09-21", que es lo que espera el backend. */
export function fechaISO(fecha = new Date()) {
  const desfase = fecha.getTimezoneOffset() * 60_000;
  return new Date(fecha.getTime() - desfase).toISOString().slice(0, 10);
}

/** "2026-09-21" -> "sábado, 21 de septiembre de 2026". */
export function fechaLarga(iso) {
  if (!iso) return "";

  const [anio, mes, dia] = iso.split("-").map(Number);
  return new Date(anio, mes - 1, dia).toLocaleDateString("es-MX", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

export function nombreSala(sala) {
  if (!sala) return "Sin asignar";
  return sala.codigo === sala.nombre ? sala.codigo : `${sala.codigo} · ${sala.nombre}`;
}
