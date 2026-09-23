import { Route, Routes } from "react-router-dom";

import Encabezado from "./components/layout/Encabezado.jsx";
import Navegacion from "./components/layout/Navegacion.jsx";
import PaginaGuias from "./pages/PaginaGuias.jsx";
import PaginaRol from "./pages/PaginaRol.jsx";
import PaginaSalas from "./pages/PaginaSalas.jsx";

export default function App() {
  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-3 pb-12 pt-4 md:gap-6 md:px-6 md:pt-8">
      <Encabezado />
      <Navegacion />

      <main>
        <Routes>
          <Route path="/" element={<PaginaRol />} />
          <Route path="/guias" element={<PaginaGuias />} />
          <Route path="/salas" element={<PaginaSalas />} />
          <Route path="*" element={<PaginaRol />} />
        </Routes>
      </main>
    </div>
  );
}
