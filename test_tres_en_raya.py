import random
import unittest

from tres_en_raya import (VACIO, IAAdaptativa, colocar, ganador,
                          movimiento_ia, movimientos_libres, rival)


class TestTablero(unittest.TestCase):
    def test_ganador_fila(self):
        t = tuple("XXXOO    ")
        self.assertEqual(ganador(t), "X")

    def test_empate(self):
        t = tuple("XOXXOOOXX")
        self.assertEqual(ganador(t), "empate")

    def test_en_curso(self):
        self.assertIsNone(ganador((VACIO,) * 9))


class TestIA(unittest.TestCase):
    def _nunca_pierde(self, tablero, turno, ficha_ia):
        """Explora TODAS las respuestas posibles del rival contra la IA imbatible."""
        res = ganador(tablero)
        if res:
            self.assertNotEqual(res, rival(ficha_ia), f"La IA perdió: {tablero}")
            return
        if turno == ficha_ia:
            m = movimiento_ia(tablero, ficha_ia, 4, random.Random(0))
            self._nunca_pierde(colocar(tablero, m, turno), rival(turno), ficha_ia)
        else:
            for m in movimientos_libres(tablero):
                self._nunca_pierde(colocar(tablero, m, turno), rival(turno), ficha_ia)

    def test_imbatible_empezando(self):
        self._nunca_pierde((VACIO,) * 9, "X", "X")

    def test_imbatible_segundo(self):
        self._nunca_pierde((VACIO,) * 9, "X", "O")

    def test_remata(self):
        t = tuple("OO XX    ")
        for semilla in range(20):
            self.assertEqual(movimiento_ia(t, "O", 4, random.Random(semilla)), 2)

    def test_medio_tapa_siempre(self):
        t = tuple("XX  O    ")
        for semilla in range(50):
            self.assertEqual(movimiento_ia(t, "O", 2, random.Random(semilla)), 2)


class TestAdaptativa(unittest.TestCase):
    def test_sube_y_baja(self):
        ia = IAAdaptativa(2)
        ia.registrar("X", "O")  # gana el humano
        self.assertEqual(ia.nivel, 3)
        ia.registrar("empate", "O")
        self.assertEqual(ia.nivel, 3)
        ia.registrar("O", "O")  # gana la IA
        self.assertEqual(ia.nivel, 2)

    def test_limites(self):
        ia = IAAdaptativa(4)
        ia.registrar("X", "O")
        self.assertEqual(ia.nivel, 4)
        ia = IAAdaptativa(1)
        ia.registrar("O", "O")
        self.assertEqual(ia.nivel, 1)


if __name__ == "__main__":
    unittest.main()
