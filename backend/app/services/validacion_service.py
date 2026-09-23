"""Revisa un rol ya armado y describe todo lo que se rompe.

Trabaja sobre las dataclasses de `scheduling`, no sobre el ORM, así que se
puede probar sin base de datos. Es lo que alimenta el panel de advertencias.
"""

from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import time

from app.scheduling.comidas import HORAS_COMIDA, bloque_de_comida, es_hora_valida
from app.scheduling.dominio import (
    BloqueHorario,
    GuiaDisponible,
    ParDeComida,
    SalaDisponible,
    SlotAsignado,
)
from app.schemas.validacion import Advertencia, Nivel, Regla, ResultadoValidacion


class ValidacionService:
    def __init__(
        self,
        guias: Sequence[GuiaDisponible],
        salas: Sequence[SalaDisponible],
        bloques: Sequence[BloqueHorario],
        pares_comida: Sequence[ParDeComida] = (),
    ) -> None:
        self.guias = {guia.id: guia for guia in guias}
        self.salas = {sala.id: sala for sala in salas}
        self.bloques = {bloque.id: bloque for bloque in bloques}
        self.pares_comida = list(pares_comida)

    def validar(
        self,
        asignaciones: Sequence[SlotAsignado],
        comidas: Mapping[int, time],
    ) -> ResultadoValidacion:
        advertencias: list[Advertencia] = []

        advertencias += self._revisar_requisitos(asignaciones)
        advertencias += self._revisar_choques_por_bloque(asignaciones)
        advertencias += self._revisar_repeticiones(asignaciones)
        advertencias += self._revisar_salas_vacias(asignaciones)
        advertencias += self._revisar_sin_asignar(asignaciones)
        advertencias += self._revisar_comidas(asignaciones, comidas)

        return ResultadoValidacion.desde(advertencias)

    # --- Reglas -----------------------------------------------------------

    def _revisar_requisitos(self, asignaciones: Sequence[SlotAsignado]) -> list[Advertencia]:
        """Quién puede pararse en qué sala."""
        avisos: list[Advertencia] = []

        for slot in asignaciones:
            if slot.sala_id is None:
                continue

            guia = self.guias.get(slot.guia_id)
            sala = self.salas.get(slot.sala_id)
            if guia is None or sala is None:
                continue

            bloque = self._nombre_bloque(slot.bloque_id)

            if sala.solo_super and not guia.es_super:
                avisos.append(
                    Advertencia(
                        nivel=Nivel.ERROR,
                        regla=Regla.SOLO_SUPER,
                        mensaje=(
                            f"{guia.nombre} no es Súper Guía y tiene asignada "
                            f"{sala.codigo} en {bloque}."
                        ),
                        guia_id=guia.id,
                        bloque_id=slot.bloque_id,
                        sala_id=sala.id,
                    )
                )
            elif sala.es_funcion and sala.id not in guia.salas_certificadas:
                avisos.append(
                    Advertencia(
                        nivel=Nivel.ERROR,
                        regla=Regla.SIN_CERTIFICACION,
                        mensaje=(
                            f"{guia.nombre} no está certificado para {sala.etiqueta} "
                            f"y la tiene en {bloque}."
                        ),
                        guia_id=guia.id,
                        bloque_id=slot.bloque_id,
                        sala_id=sala.id,
                    )
                )

        return avisos

    def _revisar_choques_por_bloque(
        self, asignaciones: Sequence[SlotAsignado]
    ) -> list[Advertencia]:
        """Dos guías en una sala, o un guía en dos salas, dentro del mismo bloque."""
        avisos: list[Advertencia] = []
        por_sala: dict[tuple[int, int], list[int]] = defaultdict(list)
        por_guia: dict[tuple[int, int], list[int]] = defaultdict(list)

        for slot in asignaciones:
            if slot.sala_id is None:
                continue
            por_sala[(slot.bloque_id, slot.sala_id)].append(slot.guia_id)
            por_guia[(slot.bloque_id, slot.guia_id)].append(slot.sala_id)

        for (bloque_id, sala_id), guias_ids in por_sala.items():
            if len(guias_ids) < 2:
                continue
            avisos.append(
                Advertencia(
                    nivel=Nivel.ERROR,
                    regla=Regla.SALA_DUPLICADA,
                    mensaje=(
                        f"{self._nombres(guias_ids)} están al mismo tiempo en "
                        f"{self._codigo_sala(sala_id)} ({self._nombre_bloque(bloque_id)})."
                    ),
                    bloque_id=bloque_id,
                    sala_id=sala_id,
                )
            )

        for (bloque_id, guia_id), salas_ids in por_guia.items():
            if len(salas_ids) < 2:
                continue
            codigos = ", ".join(self._codigo_sala(s) for s in salas_ids)
            avisos.append(
                Advertencia(
                    nivel=Nivel.ERROR,
                    regla=Regla.GUIA_DUPLICADO,
                    mensaje=(
                        f"{self._nombre_guia(guia_id)} está en {codigos} a la vez "
                        f"({self._nombre_bloque(bloque_id)})."
                    ),
                    guia_id=guia_id,
                    bloque_id=bloque_id,
                )
            )

        return avisos

    def _revisar_repeticiones(self, asignaciones: Sequence[SlotAsignado]) -> list[Advertencia]:
        """Regla 1, con la excepción del Súper Guía en su sala exclusiva."""
        avisos: list[Advertencia] = []
        conteo: dict[tuple[int, int], int] = defaultdict(int)

        for slot in asignaciones:
            if slot.sala_id is not None:
                conteo[(slot.guia_id, slot.sala_id)] += 1

        for (guia_id, sala_id), veces in conteo.items():
            if veces < 2:
                continue

            guia = self.guias.get(guia_id)
            sala = self.salas.get(sala_id)
            if guia and sala and sala.solo_super and guia.es_super:
                continue

            avisos.append(
                Advertencia(
                    nivel=Nivel.AVISO,
                    regla=Regla.SALA_REPETIDA,
                    mensaje=(
                        f"{self._nombre_guia(guia_id)} repite "
                        f"{self._codigo_sala(sala_id)} {veces} veces en el turno."
                    ),
                    guia_id=guia_id,
                    sala_id=sala_id,
                )
            )

        return avisos

    def _revisar_salas_vacias(self, asignaciones: Sequence[SlotAsignado]) -> list[Advertencia]:
        """Una sala general vacía se aguanta; una función sin guía cancela el show."""
        avisos: list[Advertencia] = []
        ocupadas = {(s.bloque_id, s.sala_id) for s in asignaciones if s.sala_id is not None}

        for bloque_id in self.bloques:
            for sala in self.salas.values():
                if (bloque_id, sala.id) in ocupadas:
                    continue

                critica = sala.es_funcion or sala.solo_super
                avisos.append(
                    Advertencia(
                        nivel=Nivel.ERROR if critica else Nivel.AVISO,
                        regla=Regla.SALA_VACIA,
                        mensaje=(
                            f"Nadie cubre {sala.etiqueta} en {self._nombre_bloque(bloque_id)}."
                        ),
                        bloque_id=bloque_id,
                        sala_id=sala.id,
                    )
                )

        return avisos

    def _revisar_sin_asignar(self, asignaciones: Sequence[SlotAsignado]) -> list[Advertencia]:
        avisos: list[Advertencia] = []

        for slot in asignaciones:
            if slot.sala_id is not None:
                continue

            avisos.append(
                Advertencia(
                    nivel=Nivel.AVISO,
                    regla=Regla.SIN_ASIGNAR,
                    mensaje=(
                        f"{self._nombre_guia(slot.guia_id)} no tiene sala en "
                        f"{self._nombre_bloque(slot.bloque_id)}."
                    ),
                    guia_id=slot.guia_id,
                    bloque_id=slot.bloque_id,
                )
            )

        return avisos

    def _revisar_comidas(
        self,
        asignaciones: Sequence[SlotAsignado],
        comidas: Mapping[int, time],
    ) -> list[Advertencia]:
        """Reglas 2 y 3."""
        avisos: list[Advertencia] = []
        horas_validas = ", ".join(hora.strftime("%H:%M") for hora in HORAS_COMIDA)

        for guia_id, hora in comidas.items():
            if es_hora_valida(hora):
                continue
            avisos.append(
                Advertencia(
                    nivel=Nivel.ERROR,
                    regla=Regla.HORA_COMIDA_INVALIDA,
                    mensaje=(
                        f"{self._nombre_guia(guia_id)} tiene comida a las "
                        f"{hora.strftime('%H:%M')}; solo se permiten {horas_validas}."
                    ),
                    guia_id=guia_id,
                )
            )

        bloque_id = self._bloque_de_comida()
        if bloque_id is None:
            return avisos

        ocupantes = {
            slot.sala_id: slot.guia_id
            for slot in asignaciones
            if slot.bloque_id == bloque_id and slot.sala_id is not None
        }

        for par in self.pares_comida:
            guia_a = ocupantes.get(par.sala_a_id)
            guia_b = ocupantes.get(par.sala_b_id)

            if guia_a is None or guia_b is None:
                continue
            if comidas.get(guia_a) != comidas.get(guia_b):
                continue

            hora = comidas.get(guia_a)
            avisos.append(
                Advertencia(
                    nivel=Nivel.ERROR,
                    regla=Regla.COMIDA_EMPALMADA,
                    mensaje=(
                        f"{self._nombre_guia(guia_a)} ({self._codigo_sala(par.sala_a_id)}) y "
                        f"{self._nombre_guia(guia_b)} ({self._codigo_sala(par.sala_b_id)}) "
                        f"comen los dos a las {hora.strftime('%H:%M') if hora else '—'}."
                    ),
                    guia_id=guia_a,
                    bloque_id=bloque_id,
                    sala_id=par.sala_a_id,
                )
            )

        return avisos

    # --- Auxiliares -------------------------------------------------------

    def _bloque_de_comida(self) -> int | None:
        bloque = bloque_de_comida(list(self.bloques.values()))
        return bloque.id if bloque else None

    def _nombre_guia(self, guia_id: int) -> str:
        guia = self.guias.get(guia_id)
        return guia.nombre if guia else f"Guía {guia_id}"

    def _nombres(self, guias_ids: Sequence[int]) -> str:
        return ", ".join(self._nombre_guia(gid) for gid in guias_ids)

    def _codigo_sala(self, sala_id: int) -> str:
        sala = self.salas.get(sala_id)
        return sala.codigo if sala else f"sala {sala_id}"

    def _nombre_bloque(self, bloque_id: int) -> str:
        bloque = self.bloques.get(bloque_id)
        return bloque.etiqueta if bloque else f"bloque {bloque_id}"
