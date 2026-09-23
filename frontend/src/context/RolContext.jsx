import { createContext, useContext } from "react";

/** Comparte catálogos, borrador y validación entre la tabla y los paneles,
 *  para no ir pasando quince props por cada nivel. */
const RolContext = createContext(null);

export function ProveedorRol({ valor, children }) {
  return <RolContext.Provider value={valor}>{children}</RolContext.Provider>;
}

export function useContextoRol() {
  const contexto = useContext(RolContext);

  if (contexto === null) {
    throw new Error("useContextoRol solo funciona dentro de <ProveedorRol>.");
  }

  return contexto;
}
