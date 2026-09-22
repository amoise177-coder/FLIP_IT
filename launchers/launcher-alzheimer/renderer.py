import pygame
import math
from settings import *

def crear_fondo_degradado(ancho, alto, color_arriba, color_abajo):
    superficie = pygame.Surface((ancho, alto))
    for y in range(alto):
        t = y / max(alto - 1, 1)
        color = tuple(
            int(color_arriba[i] + (color_abajo[i] - color_arriba[i]) * t)
            for i in range(3)
        )
        pygame.draw.line(superficie, color, (0, y), (ancho, y))
    return superficie

class Renderer:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fondo = crear_fondo_degradado(ANCHO, ALTO, FONDO_ARRIBA, FONDO_ABAJO)

    def dibujar_fondo(self):
        self.pantalla.blit(self.fondo, (0, 0))

    def dibujar_estrella(self, superficie, centro, radio_externo, radio_interno, color):
        puntos = []
        for i in range(10):
            angulo = math.pi / 5 * i - math.pi / 2
            radio = radio_externo if i % 2 == 0 else radio_interno
            puntos.append(
                (centro[0] + math.cos(angulo) * radio, centro[1] + math.sin(angulo) * radio)
            )
        pygame.draw.polygon(superficie, color, puntos)

    def dibujar_rect_redondeado_sombra(self, superficie, rect, radio, color, color_sombra, desplazamiento=6):
        sombra = rect.copy()
        sombra.x += desplazamiento
        sombra.y += desplazamiento
        pygame.draw.rect(superficie, color_sombra, sombra, border_radius=radio)
        pygame.draw.rect(superficie, color, rect, border_radius=radio)

    def dibujar_palabra_animada(self, superficie, texto, fuente, x_centro, y_centro, paleta, t,
                                amplitud=7, velocidad=2.4, espacio_extra=3, sombra=True):
        anchos = [fuente.size(ch)[0] for ch in texto]
        ancho_total = sum(anchos) + espacio_extra * (len(texto) - 1)
        x = x_centro - ancho_total / 2

        for i, ch in enumerate(texto):
            color = paleta[i % len(paleta)]
            offset_y = math.sin(t * velocidad + i * 0.5) * amplitud
            superficie_letra = fuente.render(ch, True, color)
            pos_y = y_centro - superficie_letra.get_height() / 2 + offset_y

            if sombra and ch != " ":
                sombra_letra = fuente.render(ch, True, (0, 0, 0))
                sombra_letra.set_alpha(35)
                superficie.blit(sombra_letra, (x + 3, pos_y + 5))

            superficie.blit(superficie_letra, (x, pos_y))
            x += anchos[i] + espacio_extra
