from pydantic import BaseModel, ConfigDict, Field


class GuiaBase(BaseModel):
    nombre: str = Field(min_length=1, max_length=150, examples=["Ana Torres"])
    es_super: bool = False
    activo: bool = True


class GuiaCrear(GuiaBase):
    salas_certificadas: list[int] = Field(
        default_factory=list,
        description="Ids de las salas de función que el guía puede dar.",
    )


class GuiaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=150)
    es_super: bool | None = None
    activo: bool | None = None
    salas_certificadas: list[int] | None = None


class CertificacionesActualizar(BaseModel):
    salas_certificadas: list[int] = Field(default_factory=list)


class GuiaOut(GuiaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    salas_certificadas: list[int] = Field(default_factory=list)
