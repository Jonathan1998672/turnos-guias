export default function Casilla({ etiqueta, className = "", disabled = false, ...props }) {
  return (
    <label
      className={`inline-flex select-none items-center gap-2 text-sm ${
        disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer"
      } ${className}`}
    >
      <input
        type="checkbox"
        disabled={disabled}
        className="size-[18px] shrink-0 cursor-pointer accent-primario disabled:cursor-not-allowed"
        {...props}
      />
      {etiqueta}
    </label>
  );
}
