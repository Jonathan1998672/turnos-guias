class ErrorDeDominio(Exception):
    """Base de los errores de negocio que la API traduce a respuestas HTTP."""

    codigo_http = 400

    def __init__(self, mensaje: str, detalles: list[str] | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.detalles = detalles or []


class RecursoNoEncontrado(ErrorDeDominio):
    codigo_http = 404


class ConflictoDeDatos(ErrorDeDominio):
    """Choca con una regla de unicidad, por ejemplo dos Súper Guías activos."""

    codigo_http = 409


class RolNoFactible(ErrorDeDominio):
    """Falta algo estructural para poder armar el rol."""

    codigo_http = 422


class FormatoNoSoportado(ErrorDeDominio):
    codigo_http = 400
