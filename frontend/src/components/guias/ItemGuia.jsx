import { useState } from "react";

import Boton from "../ui/Boton.jsx";
import Etiqueta from "../ui/Etiqueta.jsx";
import FormularioGuia from "./FormularioGuia.jsx";

function Etiquetas({ guia, salasDeFuncion }) {
  const certificadas = salasDeFuncion.filter((sala) =>
    guia.salas_certificadas.includes(sala.id),
  );

  return (
    <span className="ml-1 inline-flex flex-wrap gap-1">
      {guia.es_super && <Etiqueta tono="oro">Súper Guía</Etiqueta>}
      {certificadas.map((sala) => (
        <Etiqueta key={sala.id} tono="morado">
          {sala.nombre}
        </Etiqueta>
      ))}
      {!guia.es_super && certificadas.length === 0 && (
        <Etiqueta tono="neutro">Guía General</Etiqueta>
      )}
      {!guia.activo && <Etiqueta tono="tenue">Inactivo</Etiqueta>}
    </span>
  );
}

export default function ItemGuia({ guia, salasDeFuncion, superBloqueado, onEditar, onDarDeBaja }) {
  const [editando, setEditando] = useState(false);

  if (editando) {
    return (
      <li className="rounded-lg border border-primario/50 bg-hondo p-3">
        <FormularioGuia
          salasDeFuncion={salasDeFuncion}
          valorInicial={guia}
          superBloqueado={superBloqueado}
          textoBoton="Guardar cambios"
          onGuardar={async (datos) => {
            await onEditar(guia.id, datos);
            setEditando(false);
          }}
          onCancelar={() => setEditando(false)}
        />
      </li>
    );
  }

  return (
    <li className="flex items-center justify-between gap-2 rounded-lg border border-borde bg-hondo px-3 py-2.5 text-sm">
      <span className={`min-w-0 ${guia.activo ? "" : "opacity-60"}`}>
        <strong>{guia.nombre}</strong>
        <Etiquetas guia={guia} salasDeFuncion={salasDeFuncion} />
      </span>

      <span className="flex shrink-0 gap-1">
        <Boton variante="fantasma" className="px-2 py-1" onClick={() => setEditando(true)}>
          Editar
        </Boton>
        {guia.activo && (
          <Boton
            variante="peligro"
            className="px-2 py-1"
            title="Dar de baja"
            onClick={() => onDarDeBaja(guia.id)}
          >
            ✕
          </Boton>
        )}
      </span>
    </li>
  );
}
