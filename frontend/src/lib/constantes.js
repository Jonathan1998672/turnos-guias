/** Las dos únicas horas de comida posibles (regla 3). */
export const HORAS_COMIDA = ["13:30:00", "14:00:00"];

/** El bloque donde cae la comida, normalmente el del mediodía. */
export function bloqueDeComida(bloques) {
  return (
    bloques.find(
      (bloque) => bloque.hora_inicio <= HORAS_COMIDA[0] && HORAS_COMIDA[0] < bloque.hora_fin,
    ) ?? null
  );
}

/** Valor del <select> cuando un guía no tiene sala en ese bloque. */
export const SIN_ASIGNAR = "";

export const FORMATOS_EXPORTACION = [
  { valor: "xlsx", texto: "Excel (.xlsx)", icono: "📊", variante: "excel" },
  { valor: "csv", texto: "CSV (.csv)", icono: "📋", variante: "neutro" },
  { valor: "pdf", texto: "PDF (.pdf)", icono: "📄", variante: "pdf" },
  { valor: "png", texto: "Imagen para WhatsApp (.png)", icono: "🖼️", variante: "acento" },
  { valor: "jpg", texto: "Imagen (.jpg)", icono: "🖼️", variante: "fantasma" },
];
