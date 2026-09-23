import { useState } from "react";

import Aviso from "../ui/Aviso.jsx";
import Boton from "../ui/Boton.jsx";
import Campo from "../ui/Campo.jsx";
import Casilla from "../ui/Casilla.jsx";

const VACIO = { nombre: "", es_super: false, salas_certificadas: [] };

/** Sirve para dar de alta y para editar: cambia solo `valorInicial`. */
export default function FormularioGuia({
  salasDeFuncion,
  valorInicial = VACIO,
  superBloqueado = false,
  textoBoton = "Agregar guía",
  limpiarAlGuardar = false,
  onGuardar,
  onCancelar,
}) {
  const [nombre, setNombre] = useState(valorInicial.nombre);
  const [esSuper, setEsSuper] = useState(valorInicial.es_super);
  const [certificadas, setCertificadas] = useState(valorInicial.salas_certificadas);
  const [error, setError] = useState(null);
  const [guardando, setGuardando] = useState(false);

  const alternarSala = (salaId) => {
    setCertificadas((previas) =>
      previas.includes(salaId) ? previas.filter((id) => id !== salaId) : [...previas, salaId],
    );
  };

  const alEnviar = async (evento) => {
    evento.preventDefault();
    setError(null);

    if (!nombre.trim()) {
      setError({ mensaje: "Escribe el nombre del guía." });
      return;
    }

    setGuardando(true);
    try {
      await onGuardar({
        nombre: nombre.trim(),
        es_super: esSuper,
        salas_certificadas: certificadas,
      });

      if (limpiarAlGuardar) {
        setNombre("");
        setEsSuper(false);
        setCertificadas([]);
      }
    } catch (fallo) {
      setError({ mensaje: fallo.message, detalles: fallo.detalles ?? [] });
    } finally {
      setGuardando(false);
    }
  };

  return (
    <form className="flex flex-col gap-3" onSubmit={alEnviar}>
      <Campo
        etiqueta="Nombre completo"
        value={nombre}
        onChange={(evento) => setNombre(evento.target.value)}
        placeholder="Ana Torres"
        autoComplete="off"
      />

      <div className="flex flex-col gap-2 rounded-lg border border-borde bg-hondo px-3 py-2.5">
        <Casilla
          etiqueta="Súper Guía"
          checked={esSuper}
          disabled={superBloqueado && !valorInicial.es_super}
          onChange={(evento) => setEsSuper(evento.target.checked)}
        />
        <span className="text-xs text-tenue">
          {superBloqueado && !valorInicial.es_super
            ? "Ya hay un Súper Guía activo."
            : "El Súper Guía se queda en H-20 los tres bloques."}
        </span>

        <hr className="border-borde" />

        <span className="text-xs text-tenue">Salas de función que puede dar:</span>
        <div className="flex flex-wrap gap-x-4 gap-y-1.5">
          {salasDeFuncion.map((sala) => (
            <Casilla
              key={sala.id}
              etiqueta={`${sala.codigo} · ${sala.nombre}`}
              checked={certificadas.includes(sala.id)}
              onChange={() => alternarSala(sala.id)}
            />
          ))}
        </div>
      </div>

      {error && (
        <Aviso titulo="No se pudo guardar:" detalles={error.detalles}>
          {error.mensaje}
        </Aviso>
      )}

      <div className="flex gap-2">
        <Boton type="submit" className="flex-1" disabled={guardando}>
          {guardando ? "Guardando…" : textoBoton}
        </Boton>
        {onCancelar && (
          <Boton variante="fantasma" onClick={onCancelar}>
            Cancelar
          </Boton>
        )}
      </div>
    </form>
  );
}
