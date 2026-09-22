import os
import unittest
from funtions import GestorSecuencia # Importar la clase

class GameLogicTests(unittest.TestCase):
    def setUp(self):
        self.original_level_file = os.path.join(os.getcwd(), 'niveles.txt')
        with open(self.original_level_file, 'w', encoding='utf-8') as fh:
            fh.write('')
        # Instanciar el gestor para usarlo en las pruebas
        self.gestor = GestorSecuencia()

    def test_consult_level_defaults_to_one_when_file_is_empty(self):
        self.assertEqual(self.gestor.consultar_nivel(), 1) # Ahora retorna int, no str

    def test_generate_color_creates_sequence_for_current_level(self):
        self.gestor.iniciar_juego() # iniciar_juego ya genera los colores
        self.assertEqual(len(self.gestor.colores_secuencia), 1)
        self.assertTrue(all(numero_color in (1, 2, 3, 4) for numero_color in self.gestor.colores_secuencia))

if __name__ == '__main__':
    unittest.main()