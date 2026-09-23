import { NavLink } from "react-router-dom";

const ENLACES = [
  { a: "/", texto: "Rol del día" },
  { a: "/guias", texto: "Guías" },
  { a: "/salas", texto: "Salas" },
];

export default function Navegacion() {
  return (
    <nav className="flex gap-1 rounded-xl border border-borde bg-tarjeta p-1">
      {ENLACES.map((enlace) => (
        <NavLink
          key={enlace.a}
          to={enlace.a}
          end={enlace.a === "/"}
          className={({ isActive }) =>
            `flex-1 rounded-lg px-3 py-2 text-center text-sm font-semibold transition ${
              isActive ? "bg-primario text-hondo" : "text-tenue hover:bg-white/5 hover:text-texto"
            }`
          }
        >
          {enlace.texto}
        </NavLink>
      ))}
    </nav>
  );
}
