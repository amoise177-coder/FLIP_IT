from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from src.pantallas.base import Pantalla

if TYPE_CHECKING:
    from src.motor import JuegoLetrea

class PantallaInicio(Pantalla):
    """Maneja la portada, botón jugar y los tutoriales interactivos de ayuda."""
    def __init__(self, juego: JuegoLetrea):
        super().__init__(juego)
        self.estado_ayuda = 0  # 0: Principal, 1: Tutorial 1, 2: Tutorial 2

        self.rect_jugar = pygame.Rect(self.juego.ANCHO // 2 - 150, (self.juego.ALTO // 2) - 50, 300, 100)
        self.rect_ayuda_azul = pygame.Rect(1160, 30, 80, 80)
        self.rect_atras = pygame.Rect(40, 30, 80, 80)
        self.rect_btn_der_ayuda = pygame.Rect(self.juego.ANCHO - 160, self.juego.ALTO // 2 - 40, 80, 80)
        self.rect_btn_izq_ayuda = pygame.Rect(80, self.juego.ALTO // 2 - 40, 80, 80)

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.estado_ayuda == 0:
                if self.rect_jugar.collidepoint(pos):
                    self.juego.audio.reproducir("jugar")
                    from src.pantallas.categorias import PantallaCategorias
                    self.juego.cambiar_pantalla(PantallaCategorias(self.juego))
                elif self.rect_ayuda_azul.collidepoint(pos):
                    self.juego.audio.reproducir("botonayuda")
                    self.estado_ayuda = 1

            elif self.estado_ayuda == 1:
                if self.rect_atras.collidepoint(pos):
                    self.juego.audio.reproducir("atras")
                    self.estado_ayuda = 0
                elif self.rect_btn_der_ayuda.collidepoint(pos):
                    self.juego.audio.reproducir("deslizar")
                    self.estado_ayuda = 2

            elif self.estado_ayuda == 2:
                if self.rect_atras.collidepoint(pos):
                    self.juego.audio.reproducir("atras")
                    self.estado_ayuda = 0
                elif self.rect_btn_izq_ayuda.collidepoint(pos):
                    self.juego.audio.reproducir("deslizar")
                    self.estado_ayuda = 1

    def actualizar(self) -> None:
        pass

    def dibujar(self, superficie: pygame.Surface) -> None:
        rec = self.juego.recursos

        if self.estado_ayuda == 0:
            if rec.img_fondo1:
                superficie.blit(rec.img_fondo1, (0, 0))
            if rec.img_btn_jugar:
                superficie.blit(rec.img_btn_jugar, rec.img_btn_jugar.get_rect(center=self.rect_jugar.center))
            if rec.img_ayuda_azul:
                superficie.blit(rec.img_ayuda_azul, self.rect_ayuda_azul)

        elif self.estado_ayuda == 1:
            if rec.img_ayuda_inicio:
                superficie.blit(rec.img_ayuda_inicio, (0, 0))
            if rec.img_atras:
                superficie.blit(rec.img_atras, self.rect_atras)
            if rec.img_btn_der:
                superficie.blit(rec.img_btn_der, rec.img_btn_der.get_rect(center=self.rect_btn_der_ayuda.center))

        elif self.estado_ayuda == 2:
            if rec.img_ayuda_inicio2:
                superficie.blit(rec.img_ayuda_inicio2, (0, 0))
            if rec.img_atras:
                superficie.blit(rec.img_atras, self.rect_atras)
            if rec.img_btn_izq:
                superficie.blit(rec.img_btn_izq, rec.img_btn_izq.get_rect(center=self.rect_btn_izq_ayuda.center))
