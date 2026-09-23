export default function Tarjeta({ titulo, acciones, children, className = "" }) {
  return (
    <section
      className={`flex flex-col gap-3 rounded-xl border border-borde bg-tarjeta p-4 ${className}`}
    >
      {(titulo || acciones) && (
        <header className="flex items-baseline justify-between gap-2 border-b border-borde pb-2">
          {titulo && <h2 className="text-base font-semibold">{titulo}</h2>}
          {acciones}
        </header>
      )}
      {children}
    </section>
  );
}
