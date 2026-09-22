import unittest

from app import App
from personajes import Gumi, Miku, Teto, Neru
from score import GestorPuntuacion


class EstadoFalso:
    def __init__(self):
        self.t_total = 10.0
        self.t_restante = 8.0
        self.actualizaciones = 0

    def actualizar_interfaz_tiempo(self):
        self.actualizaciones += 1


class PersonajesTests(unittest.TestCase):
    def test_miku_agrega_cinco_segundos_una_sola_vez(self):
        estado = EstadoFalso()
        miku = Miku()

        miku.aplicar_habilidad(estado)
        miku.aplicar_habilidad(estado)

        self.assertEqual(estado.t_total, 15.0)
        self.assertEqual(estado.t_restante, 13.0)
        
    def test_teto_aplica_multiplicador_de_puntaje(self):
        estado = EstadoFalso()
        teto = Teto()
        gestor = GestorPuntuacion()

        teto.aplicar_habilidad(estado)
        puntos = gestor.agregar_por_ronda(5.0, 1, teto.multiplicador_puntaje)

        self.assertEqual(puntos, 1100)

    def test_neru_bloquea_el_primer_error(self):
        app = object.__new__(App)
        app.personaje_actual = Neru()
        app.bloquear_penalizacion = True
        app.primer_error_protegido = True
        app.t_restante = 10.0
        app.mensaje = "Listo"

        self.assertFalse(app.error_debe_penalizar())
        self.assertFalse(getattr(app, "bloquear_penalizacion", False))
        self.assertEqual(app.t_restante, 10.0)

    def test_gumi_reduce_la_penalizacion_a_un_segundo(self):
        self.assertEqual(Gumi().penalizacion_error, 1.0)


if __name__ == "__main__":
    unittest.main()
