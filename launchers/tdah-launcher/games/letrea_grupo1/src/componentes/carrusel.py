import pygame

class CarruselBase:
    def __init__(self, x_centro: int, y_pos: int, espaciado: int = 260):
        self.x_centro = x_centro
        self.y_pos = y_pos
        self.espaciado = espaciado
        self.indice = 0.0
        self.pos_actual = 0.0

    def resetear_posicion(self, total_elementos: int) -> None:
        """Centra el carrusel en el elemento intermedio."""
        if total_elementos > 0:
            self.indice = (total_elementos - 1) / 2.0
            self.pos_actual = float(self.indice)
        else:
            self.indice = 0.0
            self.pos_actual = 0.0

    def mover_izq(self) -> bool:
        """Desplaza el carrusel una posición a la izquierda."""
        if self.indice > 0:
            self.indice = max(0.0, self.indice - 1.0)
            return True
        return False

    def mover_der(self, total_elementos: int) -> bool:
        """Desplaza el carrusel una posición a la derecha."""
        max_indice = float(total_elementos - 1)
        if self.indice < max_indice:
            self.indice = min(max_indice, self.indice + 1.0)
            return True
        return False

    def actualizar(self) -> None:
        """Interpolación suave hacia el índice objetivo (60 FPS)."""
        self.pos_actual += (self.indice - self.pos_actual) * 0.15

    def calcular_tarjetas_visibles(self, total_elementos: int, ancho_pantalla: int):
        """Genera solamente las tarjetas que caen dentro del área visible."""
        for i in range(total_elementos):
            x_pos = self.x_centro + ((i - self.pos_actual) * self.espaciado)
            if -300 < x_pos < ancho_pantalla + 100:
                yield i, pygame.Rect(x_pos - 125, self.y_pos, 250, 250)
