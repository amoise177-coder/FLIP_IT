from __future__ import annotations
from typing import TYPE_CHECKING
import random
import pygame
from src.pantallas.base import Pantalla
from src.componentes.carrusel import CarruselBase
from src.componentes.animador import AnimadorMaestraD
from src.configuracion import (
    TEXTOS_LETRAS_TITULO,
    COLOR_AZUL_BOBEO,
    COLOR_BOTON,
    VERDE_PRINCIPAL,
    COLOR_FEEDBACK_CERCA,
    COLOR_FEEDBACK_ERROR,
    MARGEN_X,
    MARGEN_Y,
    ANCHO_OVER,
    ALTO_OVER,
)

if TYPE_CHECKING:
    from src.motor import JuegoLetrea
    from src.modelos import Categoria

class PantallaEscritura(Pantalla):
    """Maneja el carrusel de pistas, escritura por teclado y retroalimentación."""
    def __init__(self, juego: JuegoLetrea, categoria: Categoria, letra: str):
        super().__init__(juego)
        self.categoria = categoria
        self.letra = letra
        self.palabra_escrita = letra
        self.mensaje_feedback = ""  # "", "cerca", "error"

        self.pistas = self.juego.recursos.cargar_pistas_por_letra(self.categoria.nombre, self.letra)
        self.total_pistas = len(self.pistas)

        x_centro = (self.juego.ANCHO // 2) + 5
        y_pos = (self.juego.ALTO // 2) - 125
        self.carrusel = CarruselBase(x_centro, y_pos, 260)
        self.carrusel.resetear_posicion(self.total_pistas)

        # Animador de Maestra D con rebote
        self.anim_maestra = AnimadorMaestraD(self.juego, x_base=25, y_bottom=710, alto_base=330)

        self.borrando_lentamente = False
        self.contador_borrado = 0
        self.intervalo_borrado = 10  # fotogramas entre borrado de cada letra

        self.rect_atras = pygame.Rect(40, 30, 80, 80)
        self.rect_btn_izq = pygame.Rect(80, self.juego.ALTO // 2 - 40, 80, 80)
        self.rect_btn_der = pygame.Rect(self.juego.ANCHO - 160, self.juego.ALTO // 2 - 40, 80, 80)

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.rect_atras.collidepoint(pos):
                self.juego.audio.reproducir("atras")
                from src.pantallas.letras import PantallaLetras
                self.juego.cambiar_pantalla(PantallaLetras(self.juego, self.categoria, es_regreso=True))
                return

            if self.borrando_lentamente:
                return

            if self.rect_btn_izq.collidepoint(pos):
                if self.carrusel.mover_izq():
                    self.juego.audio.reproducir("deslizar")
                return

            if self.rect_btn_der.collidepoint(pos):
                if self.carrusel.mover_der(self.total_pistas):
                    self.juego.audio.reproducir("deslizar")
                return

        elif evento.type == pygame.KEYDOWN:
            if self.borrando_lentamente:
                return

            if evento.key == pygame.K_RETURN:
                es_valida, _ = self.categoria.validar_palabra(self.palabra_escrita, self.letra)
                if es_valida:
                    self.juego.audio.reproducir("correcto")
                    self.categoria.marcar_completada(self.letra)
                    self.juego.recursos.liberar_pistas(self.categoria.nombre, self.letra)
                    self.juego.reproducir_video_celebracion()
                    if self.juego.ejecutando:
                        from src.pantallas.letras import PantallaLetras
                        self.juego.cambiar_pantalla(PantallaLetras(self.juego, self.categoria, es_regreso=True))
                else:
                    if self.categoria.es_palabra_cercana(self.palabra_escrita, self.letra):
                        self.mensaje_feedback = "cerca"
                        sonido_amarillo = random.choice(["amarillo1", "amarillo2"])
                        self.anim_maestra.activar("MD1", sonido_amarillo, delay_frames=5)
                    else:
                        self.mensaje_feedback = "error"
                        self.anim_maestra.activar("MD3", "intentalodenuevo", delay_frames=5)
                        if len(self.palabra_escrita) > 1:
                            self.borrando_lentamente = True
                            self.contador_borrado = 0

            elif evento.key == pygame.K_BACKSPACE:
                if len(self.palabra_escrita) > 1:
                    self.juego.audio.reproducir("borrar")
                    self.palabra_escrita = self.palabra_escrita[:-1]

            else:
                if evento.unicode and evento.unicode.isalpha():
                    self.palabra_escrita += evento.unicode.upper()
                    self.mensaje_feedback = ""

    def actualizar(self) -> None:
        self.carrusel.actualizar()
        self.anim_maestra.actualizar()

        if self.borrando_lentamente:
            self.contador_borrado += 1
            if self.contador_borrado >= self.intervalo_borrado:
                self.contador_borrado = 0
                if len(self.palabra_escrita) > 1:
                    self.palabra_escrita = self.palabra_escrita[:-1]
                    self.juego.audio.reproducir("borrar")
                if len(self.palabra_escrita) <= 1:
                    self.borrando_lentamente = False

    def dibujar(self, superficie: pygame.Surface) -> None:
        rec = self.juego.recursos
        if rec.img_fondo4:
            superficie.blit(rec.img_fondo4, (0, 0))

        # Título superior (letra en mayúscula/minúscula)
        texto_sup = TEXTOS_LETRAS_TITULO.get(self.letra, self.letra)
        obj_txt_sup = rec.fuente_titulo.render(texto_sup, True, COLOR_AZUL_BOBEO)
        superficie.blit(obj_txt_sup, obj_txt_sup.get_rect(center=(self.juego.ANCHO // 2, 85)))

        # Tarjetas de pistas
        for i, rect_tarjeta in self.carrusel.calcular_tarjetas_visibles(self.total_pistas, self.juego.ANCHO):
            img_pista = self.pistas[i]
            rect_inner = pygame.Rect(rect_tarjeta.x + MARGEN_X, rect_tarjeta.y + MARGEN_Y, ANCHO_OVER, ALTO_OVER)

            pygame.draw.rect(superficie, COLOR_BOTON, rect_inner)
            superficie.set_clip(rect_inner)

            if img_pista.get_width() == 250:
                superficie.blit(img_pista, (rect_tarjeta.x, rect_tarjeta.y))
            else:
                centro_x = rect_inner.x + (rect_inner.width - img_pista.get_width()) // 2
                centro_y = rect_inner.y + (rect_inner.height - img_pista.get_height()) // 2
                superficie.blit(img_pista, (centro_x, centro_y))

            superficie.set_clip(None)

            if rec.img_marco_pista:
                superficie.blit(rec.img_marco_pista, (rect_tarjeta.x, rect_tarjeta.y))

        # Flechas de navegación de pistas si hay más de 4
        if self.total_pistas > 4:
            if rec.img_btn_izq:
                superficie.blit(rec.img_btn_izq, rec.img_btn_izq.get_rect(center=self.rect_btn_izq.center))
            if rec.img_btn_der:
                superficie.blit(rec.img_btn_der, rec.img_btn_der.get_rect(center=self.rect_btn_der.center))

        # Zona de escritura de texto y barra de feedback
        texto_a_mostrar = self.palabra_escrita if self.palabra_escrita else self.letra
        obj_txt_escrito = rec.fuente_grande.render(texto_a_mostrar, True, VERDE_PRINCIPAL)
        superficie.blit(obj_txt_escrito, obj_txt_escrito.get_rect(center=(self.juego.ANCHO // 2, 575)))

        ancho_barra = max(70, obj_txt_escrito.get_width() + 20)
        color_barra = VERDE_PRINCIPAL
        if self.mensaje_feedback == "cerca":
            color_barra = COLOR_FEEDBACK_CERCA
        elif self.mensaje_feedback == "error":
            color_barra = COLOR_FEEDBACK_ERROR

        rect_barra = pygame.Rect(0, 0, ancho_barra, 15)
        rect_barra.center = (self.juego.ANCHO // 2, 630)
        pygame.draw.rect(superficie, color_barra, rect_barra, border_radius=6)

        # Botones UI superiores (sin botón de ayuda)
        if rec.img_atras:
            superficie.blit(rec.img_atras, self.rect_atras)

        # Maestra D animada con rebote
        self.anim_maestra.dibujar(superficie)
