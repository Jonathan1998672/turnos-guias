const ESTILOS = {
  error: "border-l-peligro bg-peligro/10 text-red-100",
  aviso: "border-l-alerta bg-alerta/10 text-amber-100",
};

export default function Advertencia({ advertencia }) {
  return (
    <li
      className={`rounded border-l-[3px] px-3 py-2 text-xs leading-relaxed ${
        ESTILOS[advertencia.nivel] ?? ESTILOS.aviso
      }`}
    >
      {advertencia.mensaje}
    </li>
  );
}
