from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from src.pantallas.base import Pantalla
from src.componentes.carrusel import CarruselBase
from src.componentes.animador import AnimadorMaestraD
from src.configuracion import ALTO_OVER, ANCHO_OVER, MARGEN_X, MARGEN_Y, COLOR_BOTON

if TYPE_CHECKING:
    from src.motor import JuegoLetrea

class PantallaCategorias(Pantalla):
    def __init__(self, juego: JuegoLetrea):
        super().__init__(juego)
        self.nombres_categorias = list(self.juego.base_categorias.keys())
        self.total_cats = len(self.nombres_categorias)

        x_centro = (self.juego.ANCHO // 2) + 5
        y_pos = (self.juego.ALTO // 2) - 125
        self.carrusel = CarruselBase(x_centro, y_pos, 260)
        self.carrusel.resetear_posicion(self.total_cats)

        self.animacion_hover = {cat: ALTO_OVER for cat in self.nombres_categorias}
        self.categoria_hover_actual: str | None = None
        self.sonidos_hover = {
            "Animales": "animaleshover",
            "Colores": "coloreshover",
            "Frutas y Comida": "frutasycomidahover",
            "Objetos de la Casa": "hogarhover",
            "Partes del Cuerpo": "ropaypdchover",
        }

        # Animador con efecto rebote y delay de 60 fotogramas (1.0s) solo la primera vez
        self.anim_maestra = AnimadorMaestraD(self.juego, x_base=25, y_bottom=710, alto_base=330)
        if not getattr(self.juego, "intro_categorias_mostrada", False):
            self.anim_maestra.activar("MD2", "categoriaselec", delay_frames=60)
            self.juego.intro_categorias_mostrada = True

        self.rect_atras = pygame.Rect(40, 30, 80, 80)
        self.rect_ayuda = pygame.Rect(1160, 30, 80, 80)
        self.rect_btn_izq = pygame.Rect(80, self.juego.ALTO // 2 - 40, 80, 80)
        self.rect_btn_der = pygame.Rect(self.juego.ANCHO - 160, self.juego.ALTO // 2 - 40, 80, 80)

    def esta_tarjeta_disponible(self, rect_cat: pygame.Rect) -> bool:
        """Una tarjeta solo es seleccionable si no queda superpuesta debajo de los botones de deslizar."""
        return not rect_cat.colliderect(self.rect_btn_izq) and not rect_cat.colliderect(self.rect_btn_der)

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.rect_atras.collidepoint(pos):
                self.juego.audio.reproducir("atras")
                from src.pantallas.inicio import PantallaInicio
                self.juego.cambiar_pantalla(PantallaInicio(self.juego))
                return

            if self.rect_ayuda.collidepoint(pos):
                self.anim_maestra.activar("MD2", "categoriaselec", delay_frames=5)
                return

            if self.rect_btn_izq.collidepoint(pos):
                if self.carrusel.mover_izq():
                    self.juego.audio.reproducir("deslizar")
                return

            if self.rect_btn_der.collidepoint(pos):
                if self.carrusel.mover_der(self.total_cats):
                    self.juego.audio.reproducir("deslizar")
                return

            # Clic en alguna tarjeta del carrusel: sólo disponible si no está superpuesta debajo de las flechas
            for i, rect_cat in self.carrusel.calcular_tarjetas_visibles(self.total_cats, self.juego.ANCHO):
                if self.esta_tarjeta_disponible(rect_cat) and rect_cat.collidepoint(pos):
                    self.juego.audio.reproducir("categoria")
                    categoria_sel = self.juego.base_categorias[self.nombres_categorias[i]]
                    from src.pantallas.letras import PantallaLetras
                    self.juego.cambiar_pantalla(PantallaLetras(self.juego, categoria_sel))
                    return

    def actualizar(self) -> None:
        self.carrusel.actualizar()
        self.anim_maestra.actualizar()
        pos_mouse = pygame.mouse.get_pos()

        cat_hover_detectada = None
        # Actualiza animación de hover en las tarjetas visibles (solo si no están debajo de las flechas)
        for i, rect_cat in self.carrusel.calcular_tarjetas_visibles(self.total_cats, self.juego.ANCHO):
            nombre_cat = self.nombres_categorias[i]
            if self.esta_tarjeta_disponible(rect_cat) and rect_cat.collidepoint(pos_mouse):
                cat_hover_detectada = nombre_cat
                self.animacion_hover[nombre_cat] = max(0, self.animacion_hover[nombre_cat] - 25)
            else:
                self.animacion_hover[nombre_cat] = min(ALTO_OVER, self.animacion_hover[nombre_cat] + 25)

        if cat_hover_detectada != self.categoria_hover_actual:
            if cat_hover_detectada and cat_hover_detectada in self.sonidos_hover:
                self.juego.audio.reproducir(self.sonidos_hover[cat_hover_detectada])
            self.categoria_hover_actual = cat_hover_detectada

    def dibujar(self, superficie: pygame.Surface) -> None:
        rec = self.juego.recursos
        if rec.img_fondo2:
            superficie.blit(rec.img_fondo2, (0, 0))

        # Tarjetas del carrusel en su distribución simétrica original
        for i, rect_cat in self.carrusel.calcular_tarjetas_visibles(self.total_cats, self.juego.ANCHO):
            nombre_cat = self.nombres_categorias[i]
            rect_inner = pygame.Rect(rect_cat.x + MARGEN_X, rect_cat.y + MARGEN_Y, ANCHO_OVER, ALTO_OVER)

            img_portada = rec.portadas_carrusel.get(nombre_cat)
            img_over = rec.portadas_over.get(nombre_cat)

            if img_portada:
                superficie.blit(img_portada, (rect_cat.x, rect_cat.y))
            else:
                pygame.draw.rect(superficie, COLOR_BOTON, rect_cat, border_radius=10)

            # Efecto persiana animada
            if img_over and self.animacion_hover[nombre_cat] < ALTO_OVER:
                superficie.set_clip(rect_inner)
                superficie.blit(img_over, (rect_inner.x, rect_inner.y + self.animacion_hover[nombre_cat]))
                superficie.set_clip(None)

        # Flechas de navegación (por encima en su posición original si hay más de 4 categorías)
        if self.total_cats > 4:
            if rec.img_btn_izq:
                superficie.blit(rec.img_btn_izq, rec.img_btn_izq.get_rect(center=self.rect_btn_izq.center))
            if rec.img_btn_der:
                superficie.blit(rec.img_btn_der, rec.img_btn_der.get_rect(center=self.rect_btn_der.center))

        # Botones UI superiores
        if rec.img_atras:
            superficie.blit(rec.img_atras, self.rect_atras)
        if rec.img_ayuda:
            superficie.blit(rec.img_ayuda, self.rect_ayuda)

        # Maestra D animada con rebote
        self.anim_maestra.dibujar(superficie)
