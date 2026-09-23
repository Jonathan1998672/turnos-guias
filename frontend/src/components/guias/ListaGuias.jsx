import ItemGuia from "./ItemGuia.jsx";

export default function ListaGuias({
  guias,
  salasDeFuncion,
  superGuia,
  onEditar,
  onDarDeBaja,
}) {
  if (guias.length === 0) {
    return (
      <p className="py-3 text-center text-sm italic text-tenue">No hay guías registrados.</p>
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {guias.map((guia) => (
        <ItemGuia
          key={guia.id}
          guia={guia}
          salasDeFuncion={salasDeFuncion}
          superBloqueado={Boolean(superGuia) && superGuia.id !== guia.id}
          onEditar={onEditar}
          onDarDeBaja={onDarDeBaja}
        />
      ))}
    </ul>
  );
}
