#!/usr/bin/env python3
"""Tres en raya para terminal.

Modos:
  1. Dos jugadores en local (mismo ordenador).
  2. Un jugador contra la IA.

La IA usa minimax con poda alfa-beta. Tiene niveles fijos (fácil, medio,
difícil/imbatible) y un nivel "adaptativo" que ajusta su fuerza según cómo
vaya la partida: si ganas, sube de nivel; si pierdes, baja. Así te lleva el
ritmo sin aburrirte ni machacarte siempre.

Solo usa la biblioteca estándar de Python 3.8+.
"""

from __future__ import annotations

import random
import sys
from functools import lru_cache
from typing import List, Optional, Tuple

VACIO = " "
LINEAS = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # filas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columnas
    (0, 4, 8), (2, 4, 6),             # diagonales
)


# --------------------------------------------------------------------------
# Lógica del tablero
# --------------------------------------------------------------------------

def ganador(tablero: Tuple[str, ...]) -> Optional[str]:
    """Devuelve 'X' u 'O' si alguien ha ganado, 'empate' si está lleno, o None."""
    for a, b, c in LINEAS:
        if tablero[a] != VACIO and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a]
    if VACIO not in tablero:
        return "empate"
    return None


def movimientos_libres(tablero: Tuple[str, ...]) -> List[int]:
    return [i for i, c in enumerate(tablero) if c == VACIO]


def colocar(tablero: Tuple[str, ...], pos: int, ficha: str) -> Tuple[str, ...]:
    t = list(tablero)
    t[pos] = ficha
    return tuple(t)


def rival(ficha: str) -> str:
    return "O" if ficha == "X" else "X"


# --------------------------------------------------------------------------
# IA: minimax con poda alfa-beta
# --------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _minimax(tablero: Tuple[str, ...], turno: str, yo: str,
             alfa: int, beta: int) -> int:
    """Puntuación desde el punto de vista de `yo`.

    Ganar pronto vale más que ganar tarde; perder tarde es mejor que perder
    pronto. Así la IA remata en cuanto puede y resiste todo lo posible.
    """
    res = ganador(tablero)
    libres = tablero.count(VACIO)
    if res == yo:
        return 10 + libres
    if res == rival(yo):
        return -10 - libres
    if res == "empate":
        return 0

    if turno == yo:
        mejor = -100
        for m in movimientos_libres(tablero):
            mejor = max(mejor, _minimax(colocar(tablero, m, turno), rival(turno), yo, alfa, beta))
            alfa = max(alfa, mejor)
            if alfa >= beta:
                break
        return mejor
    peor = 100
    for m in movimientos_libres(tablero):
        peor = min(peor, _minimax(colocar(tablero, m, turno), rival(turno), yo, alfa, beta))
        beta = min(beta, peor)
        if alfa >= beta:
            break
    return peor


def puntuar_movimientos(tablero: Tuple[str, ...], ficha: str) -> List[Tuple[int, int]]:
    """Lista de (movimiento, puntuación exacta) para `ficha`."""
    return [
        (m, _minimax(colocar(tablero, m, ficha), rival(ficha), ficha, -100, 100))
        for m in movimientos_libres(tablero)
    ]


def mejor_movimiento(tablero: Tuple[str, ...], ficha: str) -> int:
    puntuados = puntuar_movimientos(tablero, ficha)
    mejor = max(p for _, p in puntuados)
    # Entre los movimientos igual de buenos, elige al azar para variar.
    return random.choice([m for m, p in puntuados if p == mejor])


# Probabilidad de que la IA juegue el movimiento perfecto en cada nivel.
# En el resto de jugadas elige un movimiento "humano": no óptimo pero que
# al menos no regala la partida de forma absurda (salvo en fácil).
NIVELES = {
    1: ("Fácil", 0.25),
    2: ("Medio", 0.60),
    3: ("Difícil", 0.85),
    4: ("Imbatible", 1.00),
}


def movimiento_ia(tablero: Tuple[str, ...], ficha: str, nivel: int,
                  rng: random.Random = random) -> int:
    nombre, precision = NIVELES[nivel]
    libres = movimientos_libres(tablero)
    if len(libres) == 9:
        # Primera jugada: cualquier apertura vale; da variedad.
        return rng.choice([4, 0, 2, 6, 8] if nivel >= 3 else libres)

    if rng.random() < precision:
        puntuados = puntuar_movimientos(tablero, ficha)
        mejor = max(p for _, p in puntuados)
        return rng.choice([m for m, p in puntuados if p == mejor])

    # Jugada imperfecta.
    if nivel >= 2:
        # Aun fallando, remata si puede ganar ya y tapa si va a perder ya:
        # es lo que haría cualquier persona atenta.
        for m in libres:
            if ganador(colocar(tablero, m, ficha)) == ficha:
                return m
        for m in libres:
            if ganador(colocar(tablero, m, rival(ficha))) == rival(ficha):
                return m
    return rng.choice(libres)


class IAAdaptativa:
    """Ajusta el nivel según los resultados para llevarle el ritmo al jugador."""

    def __init__(self, nivel_inicial: int = 2):
        self.nivel = nivel_inicial

    def registrar(self, resultado: str, ficha_ia: str) -> Optional[str]:
        """Actualiza el nivel tras una partida. Devuelve un mensaje si cambia."""
        anterior = self.nivel
        if resultado == rival(ficha_ia):        # ganó el humano
            self.nivel = min(4, self.nivel + 1)
        elif resultado == ficha_ia:             # ganó la IA
            self.nivel = max(1, self.nivel - 1)
        # En empate se mantiene: el ritmo está igualado.
        if self.nivel > anterior:
            return f"¡Buena partida! La IA sube a nivel {NIVELES[self.nivel][0]}."
        if self.nivel < anterior:
            return f"La IA baja a nivel {NIVELES[self.nivel][0]} para ponértelo más justo."
        return None


# --------------------------------------------------------------------------
# Interfaz de terminal
# --------------------------------------------------------------------------

def dibujar(tablero: Tuple[str, ...]) -> str:
    celdas = [c if c != VACIO else str(i + 1) for i, c in enumerate(tablero)]
    filas = [f" {celdas[i]} │ {celdas[i + 1]} │ {celdas[i + 2]} " for i in (0, 3, 6)]
    return "\n" + "\n───┼───┼───\n".join(filas) + "\n"


def pedir_opcion(texto: str, validas: List[str]) -> str:
    while True:
        r = input(texto).strip().lower()
        if r in validas:
            return r
        print(f"  Opción no válida. Elige entre: {', '.join(validas)}")


def pedir_movimiento(tablero: Tuple[str, ...], ficha: str, nombre: str) -> int:
    while True:
        r = input(f"{nombre} ({ficha}), elige casilla [1-9]: ").strip().lower()
        if r in ("q", "salir"):
            raise KeyboardInterrupt
        if r.isdigit() and 1 <= int(r) <= 9:
            pos = int(r) - 1
            if tablero[pos] == VACIO:
                return pos
            print("  Esa casilla ya está ocupada.")
        else:
            print("  Escribe un número del 1 al 9 (o 'q' para salir).")


def jugar_partida(jugadores: dict, empieza: str = "X",
                  nivel_ia: Optional[int] = None) -> str:
    """jugadores: {'X': nombre o None si es la IA, 'O': ...}"""
    tablero: Tuple[str, ...] = (VACIO,) * 9
    turno = empieza
    while True:
        print(dibujar(tablero))
        res = ganador(tablero)
        if res:
            return res
        nombre = jugadores[turno]
        if nombre is None:
            pos = movimiento_ia(tablero, turno, nivel_ia)
            print(f"La IA ({turno}) juega en la casilla {pos + 1}.")
        else:
            pos = pedir_movimiento(tablero, turno, nombre)
        tablero = colocar(tablero, pos, turno)
        turno = rival(turno)


def anunciar(res: str, jugadores: dict) -> None:
    if res == "empate":
        print("🤝 ¡Empate!")
    elif jugadores[res] is None:
        print(f"🤖 Gana la IA ({res}).")
    else:
        print(f"🎉 ¡Gana {jugadores[res]} ({res})!")


def modo_local() -> None:
    n1 = input("Nombre del jugador 1 (X): ").strip() or "Jugador 1"
    n2 = input("Nombre del jugador 2 (O): ").strip() or "Jugador 2"
    jugadores = {"X": n1, "O": n2}
    marcador = {n1: 0, n2: 0, "empates": 0}
    empieza = "X"
    while True:
        res = jugar_partida(jugadores, empieza)
        anunciar(res, jugadores)
        marcador["empates" if res == "empate" else jugadores[res]] += 1
        print(f"Marcador → {n1}: {marcador[n1]} | {n2}: {marcador[n2]} | "
              f"Empates: {marcador['empates']}")
        if pedir_opcion("¿Otra partida? (s/n): ", ["s", "n"]) == "n":
            return
        empieza = rival(empieza)  # alternar quién empieza


def modo_ia() -> None:
    print("\nNivel de la IA:")
    print("  1) Fácil   2) Medio   3) Difícil   4) Imbatible")
    print("  5) Adaptativa (se ajusta a tu ritmo)  ← recomendado")
    op = int(pedir_opcion("Elige [1-5]: ", ["1", "2", "3", "4", "5"]))
    adaptativa = IAAdaptativa() if op == 5 else None
    nivel = adaptativa.nivel if adaptativa else op

    nombre = input("Tu nombre: ").strip() or "Jugador"
    ficha = pedir_opcion("¿Quieres jugar con X u O? (X empieza la 1ª partida) [x/o]: ",
                         ["x", "o"]).upper()
    jugadores = {ficha: nombre, rival(ficha): None}
    marcador = {"tú": 0, "ia": 0, "empates": 0}
    empieza = "X"
    while True:
        print(f"\n— Nivel de la IA: {NIVELES[nivel][0]} —")
        res = jugar_partida(jugadores, empieza, nivel)
        anunciar(res, jugadores)
        if res == "empate":
            marcador["empates"] += 1
        elif res == ficha:
            marcador["tú"] += 1
        else:
            marcador["ia"] += 1
        print(f"Marcador → {nombre}: {marcador['tú']} | IA: {marcador['ia']} | "
              f"Empates: {marcador['empates']}")
        if adaptativa:
            msg = adaptativa.registrar(res, rival(ficha))
            if msg:
                print(msg)
            nivel = adaptativa.nivel
        if pedir_opcion("¿Otra partida? (s/n): ", ["s", "n"]) == "n":
            return
        empieza = rival(empieza)


def main() -> None:
    print("=" * 30)
    print("       TRES EN RAYA")
    print("=" * 30)
    try:
        while True:
            print("\n1) Dos jugadores (local)")
            print("2) Contra la IA")
            print("3) Salir")
            op = pedir_opcion("Elige modo [1-3]: ", ["1", "2", "3"])
            if op == "1":
                modo_local()
            elif op == "2":
                modo_ia()
            else:
                break
    except (KeyboardInterrupt, EOFError):
        print()
    print("¡Hasta la próxima!")


if __name__ == "__main__":
    sys.exit(main())
