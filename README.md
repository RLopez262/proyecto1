# proyecto1 — Tres en raya

Juego de tres en raya para la terminal, sin dependencias (Python 3.8+).

## Cómo jugar

```bash
python3 tres_en_raya.py
```

- **Modo 1 – Dos jugadores en local:** os turnáis en el mismo ordenador. Lleva marcador y alterna quién empieza.
- **Modo 2 – Contra la IA:** elige nivel:
  - Fácil, Medio, Difícil o Imbatible (minimax perfecto: como mucho empatas).
  - **Adaptativa** (recomendado): empieza en Medio; si le ganas sube de nivel y si te gana baja, para llevarte el ritmo.

Las casillas se numeran del 1 al 9 como un teclado de teléfono. Escribe `q` para salir.

## Tests

```bash
python3 -m unittest -v
```
