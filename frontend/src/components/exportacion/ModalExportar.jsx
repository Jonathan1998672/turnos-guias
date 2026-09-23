import { exportarBorrador } from "../../api/exportacion.js";
import { useContextoRol } from "../../context/RolContext.jsx";
import { useDescarga } from "../../hooks/useDescarga.js";
import { FORMATOS_EXPORTACION } from "../../lib/constantes.js";
import Aviso from "../ui/Aviso.jsx";
import Boton from "../ui/Boton.jsx";
import Modal from "../ui/Modal.jsx";

export default function ModalExportar({ abierto, onCerrar }) {
  const { borrador } = useContextoRol();
  const { descargar, descargando, error } = useDescarga();

  const alElegir = async (formato) => {
    await descargar(formato, () => exportarBorrador(formato, borrador));
    onCerrar();
  };

  return (
    <Modal
      abierto={abierto}
      titulo="Exportar rol"
      descripcion="El archivo se arma en el servidor con lo que está en pantalla, aunque todavía no lo hayas guardado."
      onCerrar={onCerrar}
    >
      {error && <Aviso titulo="No se pudo exportar:">{error}</Aviso>}

      <div className="flex flex-col gap-2">
        {FORMATOS_EXPORTACION.map((formato) => (
          <Boton
            key={formato.valor}
            variante={formato.variante}
            disabled={descargando !== null}
            onClick={() => alElegir(formato.valor)}
          >
            <span>{formato.icono}</span>
            {descargando === formato.valor ? "Preparando…" : formato.texto}
          </Boton>
        ))}
      </div>

      <Boton variante="fantasma" onClick={onCerrar}>
        Cancelar
      </Boton>
    </Modal>
  );
}
