import random
from elementos import CatalogoElementos

class NivelDificultad:
    def __init__(self, elemento_correcto, elemento_distractor):
        self.elemento_correcto = elemento_correcto
        self.elemento_distractor = elemento_distractor
        
        opciones = [elemento_correcto, elemento_distractor]
        random.shuffle(opciones)
        
        self.opcion_a = opciones[0]
        self.opcion_b = opciones[1]

    def es_correcta(self, respuesta):
        if respuesta == 'A':
            return self.opcion_a == self.elemento_correcto
        elif respuesta == 'B':
            return self.opcion_b == self.elemento_correcto
        return False


class GeneradorNiveles:
    DIFICULTAD_AMISTOSA = 10
    DIFICULTAD_TEST = 20

    def __init__(self):
        self.catalogo = CatalogoElementos()

    def generar_partida(self, modo="amistosa"):
        cantidad_niveles = self.DIFICULTAD_TEST if modo.lower() == "test" else self.DIFICULTAD_AMISTOSA
        todos_los_elementos = self.catalogo.obtener_todos().copy()

        total_requerido = cantidad_niveles * 2
        
        if len(todos_los_elementos) >= total_requerido:
            elementos_seleccionados = random.sample(todos_los_elementos, total_requerido)
        else:
            elementos_seleccionados = random.choices(todos_los_elementos, k=total_requerido)

        partida = []
        for i in range(cantidad_niveles):
            correcto = elementos_seleccionados[i * 2]
            distractor = elementos_seleccionados[i * 2 + 1]
            
            nivel = NivelDificultad(correcto, distractor)
            partida.append(nivel)

        return partida