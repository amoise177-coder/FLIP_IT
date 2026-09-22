"""Botón reutilizable: encapsula su apariencia (con sombra, brillo tipo
"cristal" y un resplandor suave al pasar el mouse) y su interacción con
el mouse. Puede mostrar texto, un ícono vectorial junto al texto, o un
avatar de personaje en lugar de texto (preguntas de reconocimiento
visual)."""

import math

import pygame

from juego.configuracion import (
    COLOR_BOTON,
    COLOR_BOTON_HOVER,
    COLOR_BOTON_TEXTO,
)
from .avatar import dibujar_avatar
from .utilidades import dibujar_resplandor, dibujar_sombra_panel


def _oscurecer(color, factor=0.72):
    return tuple(max(0, int(c * factor)) for c in color)


class Boton:
    def __init__(
        self,
        juego,
        rect,
        texto="",
        clave_fuente="boton",
        al_hacer_clic=None,
        color_normal=None,
        color_hover=None,
        color_texto=None,
        personaje=None,
        icono=None,
        enfatizado=False,
        radio_borde=14,
    ):
        self._juego = juego
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self._clave_fuente = clave_fuente
        self.al_hacer_clic = al_hacer_clic
        self.color_normal = color_normal or COLOR_BOTON
        self.color_hover = color_hover or COLOR_BOTON_HOVER
        self.color_texto = color_texto or COLOR_BOTON_TEXTO
        self.personaje = personaje
        self.icono = icono
        self.enfatizado = enfatizado
        self.radio_borde = radio_borde
        self._hover = False
        self._deshabilitado = False

    def establecer_deshabilitado(self, valor):
        self._deshabilitado = valor

    def actualizar(self, pos_mouse):
        self._hover = (not self._deshabilitado) and self.rect.collidepoint(pos_mouse)

    def procesar_evento(self, evento):
        if self._deshabilitado:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if self.al_hacer_clic:
                    self.al_hacer_clic()
                return True
        return False

    def dibujar(self, superficie):
        if self._deshabilitado:
            color = tuple(min(255, c + 35) for c in self.color_normal)
        else:
            color = self.color_hover if self._hover else self.color_normal

        # Pequeño "levantamiento" visual al pasar el mouse (sin mover el
        # área real de clic, que sigue siendo self.rect).
        desplazamiento_y = -3 if (self._hover and not self._deshabilitado) else 0
        rect_dibujo = self.rect.move(0, desplazamiento_y)

        if self.enfatizado and not self._deshabilitado:
            pulso = (math.sin(pygame.time.get_ticks() / 320.0) + 1) / 2  # 0..1
            radio_glow = int(max(rect_dibujo.width, rect_dibujo.height) * (0.62 + 0.06 * pulso))
            dibujar_resplandor(superficie, rect_dibujo.center, radio_glow, self.color_normal, alpha_max=55)
        elif self._hover and not self._deshabilitado:
            radio_glow = int(max(rect_dibujo.width, rect_dibujo.height) * 0.6)
            dibujar_resplandor(superficie, rect_dibujo.center, radio_glow, color, alpha_max=45)

        dibujar_sombra_panel(superficie, rect_dibujo, radio_borde=self.radio_borde, desplazamiento=(0, 5), difuminado=8, alpha=65)

        pygame.draw.rect(superficie, color, rect_dibujo, border_radius=self.radio_borde)

        # Brillo superior tipo "cristal" para que no se vea plano.
        alto_brillo = max(1, rect_dibujo.height // 2)
        brillo = pygame.Surface((rect_dibujo.width, alto_brillo), pygame.SRCALPHA)
        pygame.draw.rect(
            brillo, (255, 255, 255, 55), brillo.get_rect(),
            border_top_left_radius=self.radio_borde, border_top_right_radius=self.radio_borde,
        )
        superficie.blit(brillo, rect_dibujo.topleft)

        pygame.draw.rect(superficie, _oscurecer(color), rect_dibujo, width=2, border_radius=self.radio_borde)

        if self.personaje is not None:
            radio_base = min(rect_dibujo.width, rect_dibujo.height) // 2 - 12
            # Un pequeño "pop" (agrandado sutil) al pasar el mouse, además
            # del levantamiento y el resplandor, para que la opción se
            # sienta interactiva antes de hacer clic.
            hover_activo = self._hover and not self._deshabilitado
            radio = int(radio_base * 1.07) if hover_activo else radio_base
            dibujar_avatar(superficie, self.personaje, rect_dibujo.center, radio, resaltado=self._hover)
            return

        fuente = self._juego.fuente(self._clave_fuente)
        ancho_texto, alto_texto = (fuente.size(self.texto) if self.texto else (0, 0))
        tamano_icono = int(rect_dibujo.height * 0.42)
        espacio = 12 if (self.icono and self.texto) else 0
        ancho_total = (tamano_icono if self.icono else 0) + espacio + ancho_texto
        x_inicio = rect_dibujo.centerx - ancho_total // 2

        if self.icono:
            centro_icono = (x_inicio + tamano_icono // 2, rect_dibujo.centery)
            self.icono(superficie, centro_icono, tamano_icono, self.color_texto)
            x_inicio += tamano_icono + espacio

        if self.texto:
            superficie_texto = fuente.render(self.texto, True, self.color_texto)
            rect_texto = superficie_texto.get_rect(midleft=(x_inicio, rect_dibujo.centery))
            superficie.blit(superficie_texto, rect_texto)
