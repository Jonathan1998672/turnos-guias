# Reglas de negocio del rol de guías

## Catálogo de salas

| Código | Nombre                | Es función | Solo Súper Guía | Comida por defecto |
| ------ | --------------------- | ---------- | --------------- | ------------------ |
| H-20   | Súper Guía            | No         | Sí              | 13:30              |
| H-21   | Planetario            | Sí         | No              | 13:30              |
| H-22   | Come bien, juega bien | No         | No              | 13:30              |
| H-23   | Física y astronomía   | No         | No              | 14:00              |
| H-25   | Jardín de la ciencia  | No         | No              | 13:30              |
| H-26   | MI-YO                 | No         | No              | 14:00              |
| H-27   | Plasma                | Sí         | No              | 14:00              |

Una sala marcada como **función** (`es_funcion = true`) exige que el guía tenga
certificación explícita para esa sala. H-20 es exclusiva del Súper Guía.

## Pares de comida

Los guías asignados a estas parejas de salas no pueden comer a la misma hora:

- H-21 (Planetario) y H-27 (Plasma)
- H-22 (Come bien, juega bien) y H-23 (Física y astronomía)
- H-25 (Jardín de la ciencia) y H-26 (MI-YO)

## Turno de fin de semana

Un solo turno con tres bloques:

1. 10:00 - 12:30
2. 12:30 - 15:00 (bloque que contiene la comida)
3. 15:00 - 17:00

## Las cuatro reglas

1. **Sin repetir sala.** Un guía no puede repetir sala a lo largo del turno.
   Única excepción: el Súper Guía permanece en H-20 los tres bloques.
2. **Comidas sin empalme.** Los guías de un mismo par de salas no pueden tener
   la misma hora de comida.
3. **Horas de comida fijas.** Solo existen dos: 13:30 y 14:00, de 30 minutos.
4. **Asistencia variable.** No siempre asisten todos los guías. El rol se genera
   con los presentes y las reglas anteriores se deben seguir cumpliendo.

## Degradación cuando falta personal

Cuando no hay suficientes guías certificados para cubrir las salas de función sin
repetir, el solver relaja la regla 1 **solo** para esas salas y lo reporta como
advertencia, en lugar de fallar. El rol nunca se rechaza por ser subóptimo.

Solo se rechaza la generación cuando falta algo estructural:

- No hay Súper Guía entre los presentes.
- Nadie certificado para Planetario (H-21).
- Nadie certificado para Plasma (H-27).
