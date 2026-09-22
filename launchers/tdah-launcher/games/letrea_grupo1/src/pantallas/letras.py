from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from src.pantallas.base import Pantalla
from src.componentes.animador import AnimadorMaestraD
from src.configuracion import TAMANO_BOTON_LETRA, COLOR_BOTON, COLOR_BOTON_HOVER, COLOR_TEXTO

if TYPE_CHECKING:
    from src.motor import JuegoLetrea
    from src.modelos import Categoria

class PantallaLetras(Pantalla):
    """Maneja la cuadrícula de botones de letras con renderizado optimizado y caché de texturas."""
    def __init__(self, juego: JuegoLetrea, categoria: Categoria, es_regreso: bool = False):
        super().__init__(juego)
        self.categoria = categoria
        self.letras_disponibles = self.categoria.obtener_letras_disponibles()

        # Animador de Maestra D con delay de 60 fotogramas (1.0s) y rebote
        self.anim_maestra = AnimadorMaestraD(self.juego, x_base=25, y_bottom=710, alto_base=330)
        # Solo aparece al entrar por primera vez (no al volver tras completar o cancelar una letra)
        if not getattr(self.juego, "intro_letras_mostrada", False) and not es_regreso:
            self.anim_maestra.activar("MD1", "letraselec", delay_frames=60)
            self.juego.intro_letras_mostrada = True

        self.rect_atras = pygame.Rect(40, 30, 80, 80)
        self.rect_ayuda = pygame.Rect(1160, 30, 80, 80)

        # Configuración de columnas según categoría
        nombre_cat = self.categoria.nombre
        if nombre_cat == "Animales":
            self.cols, self.esp_x, self.ini_y = 7, 100, 230
        elif nombre_cat == "Frutas y Comida":
            self.cols, self.esp_x, self.ini_y = 6, 110, 230
        elif nombre_cat == "Colores":
            self.cols, self.esp_x, self.ini_y = 5, 120, 280
        else:
            self.cols, self.esp_x, self.ini_y = 5, 120, 240

        self.filas = [
            self.letras_disponibles[i:i + self.cols]
            for i in range(0, len(self.letras_disponibles), self.cols)
        ]

    def _obtener_rect_letra(self, num_fila: int, col: int, total_en_fila: int) -> pygame.Rect:
        ancho_fila = (total_en_fila - 1) * self.esp_x + TAMANO_BOTON_LETRA
        inicio_x = (self.juego.ANCHO - ancho_fila) // 2
        pos_y = self.ini_y + (num_fila * 100)
        pos_x = inicio_x + (col * self.esp_x)
        return pygame.Rect(pos_x, pos_y, TAMANO_BOTON_LETRA, TAMANO_BOTON_LETRA)

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos

            if self.rect_atras.collidepoint(pos):
                self.juego.audio.reproducir("atras")
                from src.pantallas.categorias import PantallaCategorias
                self.juego.cambiar_pantalla(PantallaCategorias(self.juego))
                return

            if self.rect_ayuda.collidepoint(pos):
                self.anim_maestra.activar("MD1", "letraselec", delay_frames=5)
                return

            # Clic en letra activa
            for num_fila, fila_letras in enumerate(self.filas):
                for col, letra in enumerate(fila_letras):
                    if self.categoria.esta_activa(letra):
                        rect_letra = self._obtener_rect_letra(num_fila, col, len(fila_letras))
                        if rect_letra.collidepoint(pos):
                            self.juego.audio.reproducir("letra")
                            from src.pantallas.escritura import PantallaEscritura
                            self.juego.cambiar_pantalla(PantallaEscritura(self.juego, self.categoria, letra))
                            return

    def actualizar(self) -> None:
        self.anim_maestra.actualizar()

    def dibujar(self, superficie: pygame.Surface) -> None:
        rec = self.juego.recursos
        fondo = rec.fondos_categorias.get(self.categoria.nombre)
        if fondo:
            superficie.blit(fondo, (0, 0))

        pos_mouse = pygame.mouse.get_pos()

        for num_fila, fila_letras in enumerate(self.filas):
            for col, letra in enumerate(fila_letras):
                rect_letra = self._obtener_rect_letra(num_fila, col, len(fila_letras))
                letra_activa = self.categoria.esta_activa(letra)

                esta_hover = rect_letra.collidepoint(pos_mouse) and letra_activa
                dibujo_y = rect_letra.y - 6 if esta_hover else rect_letra.y

                img_letra = rec.imagenes_letras.get(letra)
                if img_letra:
                    if not letra_activa:
                        # Textura transparente pre-calculada en caché (sin re-crear superficies a 60 FPS)
                        img_desc = rec.imagenes_letras_desactivadas.get(letra, img_letra)
                        superficie.blit(img_desc, (rect_letra.x, dibujo_y))
                    else:
                        superficie.blit(img_letra, (rect_letra.x, dibujo_y))
                else:
                    color_circ = COLOR_BOTON_HOVER if esta_hover else COLOR_BOTON
                    pygame.draw.circle(superficie, color_circ, (rect_letra.centerx, dibujo_y + TAMANO_BOTON_LETRA // 2), TAMANO_BOTON_LETRA // 2)
                    self.juego.dibujar_texto(letra, rec.fuente_media, COLOR_TEXTO, superficie, rect_letra.centerx, dibujo_y + 40)

        # Botón atrás azul característico de esta pantalla
        img_atras = rec.img_atras_azul if rec.img_atras_azul else rec.img_atras
        if img_atras:
            superficie.blit(img_atras, self.rect_atras)
        if rec.img_ayuda:
            superficie.blit(rec.img_ayuda, self.rect_ayuda)

        # Maestra D animada con rebote y sincronización
        self.anim_maestra.dibujar(superficie)
