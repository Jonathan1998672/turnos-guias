from sqlalchemy.orm import Session

from app.core.exceptions import ConflictoDeDatos, RecursoNoEncontrado
from app.models import Guia
from app.repositories.guia_repository import GuiaRepositorio
from app.repositories.sala_repository import SalaRepositorio
from app.schemas.guia import GuiaActualizar, GuiaCrear


class GuiaService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = GuiaRepositorio(db)
        self.salas = SalaRepositorio(db)

    def listar(self, *, solo_activos: bool = False) -> list[Guia]:
        return self.repo.listar(solo_activos=solo_activos)

    def obtener(self, guia_id: int) -> Guia:
        guia = self.repo.obtener(guia_id)
        if guia is None:
            raise RecursoNoEncontrado(f"No existe el guía {guia_id}.")
        return guia

    def crear(self, datos: GuiaCrear) -> Guia:
        if datos.es_super and datos.activo:
            self._verificar_super_unico()

        self._verificar_salas_de_funcion(datos.salas_certificadas)

        guia = self.repo.agregar(
            Guia(nombre=datos.nombre.strip(), es_super=datos.es_super, activo=datos.activo)
        )
        self.repo.reemplazar_certificaciones(guia, datos.salas_certificadas)
        self.db.commit()
        return guia

    def actualizar(self, guia_id: int, datos: GuiaActualizar) -> Guia:
        guia = self.obtener(guia_id)
        cambios = datos.model_dump(exclude_unset=True)
        certificaciones = cambios.pop("salas_certificadas", None)

        sera_super = cambios.get("es_super", guia.es_super)
        sera_activo = cambios.get("activo", guia.activo)
        if sera_super and sera_activo:
            self._verificar_super_unico(excluir_id=guia.id)

        if "nombre" in cambios:
            cambios["nombre"] = cambios["nombre"].strip()

        for campo, valor in cambios.items():
            setattr(guia, campo, valor)

        if certificaciones is not None:
            self._verificar_salas_de_funcion(certificaciones)
            self.repo.reemplazar_certificaciones(guia, certificaciones)

        self.db.flush()
        self.db.commit()
        return guia

    def reemplazar_certificaciones(self, guia_id: int, salas_ids: list[int]) -> Guia:
        guia = self.obtener(guia_id)
        self._verificar_salas_de_funcion(salas_ids)
        self.repo.reemplazar_certificaciones(guia, salas_ids)
        self.db.commit()
        return guia

    def dar_de_baja(self, guia_id: int) -> None:
        """Baja lógica: los roles históricos siguen apuntando al guía."""
        guia = self.obtener(guia_id)
        guia.activo = False
        self.db.flush()
        self.db.commit()

    def _verificar_super_unico(self, *, excluir_id: int | None = None) -> None:
        existente = self.repo.obtener_super_activo(excluir_id=excluir_id)
        if existente is not None:
            raise ConflictoDeDatos(
                f"Ya hay un Súper Guía activo: {existente.nombre}.",
                detalles=["Solo puede haber un Súper Guía activo a la vez."],
            )

    def _verificar_salas_de_funcion(self, salas_ids: list[int]) -> None:
        if not salas_ids:
            return

        encontradas = {sala.id: sala for sala in self.salas.listar_por_ids(salas_ids)}

        faltantes = [str(i) for i in salas_ids if i not in encontradas]
        if faltantes:
            raise RecursoNoEncontrado(f"No existen las salas: {', '.join(faltantes)}.")

        # Certificar una sala general no significa nada: cualquier guía la cubre.
        no_son_funcion = [s.codigo for s in encontradas.values() if not s.es_funcion]
        if no_son_funcion:
            raise ConflictoDeDatos(
                f"Estas salas no son de función: {', '.join(sorted(no_son_funcion))}.",
                detalles=["Solo las salas de función requieren certificación."],
            )
