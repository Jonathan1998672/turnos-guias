export default function Campo({ etiqueta, id, className = "", ...props }) {
  return (
    <label className="flex flex-col gap-1.5 text-sm" htmlFor={id}>
      {etiqueta && <span className="text-tenue">{etiqueta}</span>}
      <input
        id={id}
        className={`w-full rounded-lg border border-borde bg-hondo px-3 py-2.5 text-sm text-texto outline-none placeholder:text-tenue/70 focus:border-primario ${className}`}
        {...props}
      />
    </label>
  );
}
