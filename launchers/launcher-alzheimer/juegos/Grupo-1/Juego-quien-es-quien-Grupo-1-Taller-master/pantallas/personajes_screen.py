"""Pantalla de presentación de personajes: el jugador conoce a la familia
antes de que empiecen las preguntas."""

import pygame

from juego.configuracion import (
    ANCHO_VENTANA,
    COLOR_BOTON_SECUNDARIO,
    COLOR_BOTON_SECUNDARIO_HOVER,
    COLOR_BOTON_SECUNDARIO_TEXTO,
    COLOR_FONDO_PANEL,
    COLOR_BORDE,
    COLOR_TEXTO,
    COLOR_TEXTO_SUAVE,
    COLOR_TITULO,
    TAMANO_FAMILIA_PARTIDA,
)
from juego.juego import MENU
from . import iconos
from .pantalla import Pantalla
from .boton import Boton
from .avatar import dibujar_avatar
from .utilidades import (
    dibujar_texto_centrado,
    dibujar_texto_con_sombra,
    dibujar_panel,
    dibujar_texto_multilinea_centrado,
)


class PantallaPersonajes(Pantalla):
    def __init__(self, juego):
        super().__init__(juego)

        def con_clic(accion):
            def envoltura():
                self._juego.audio.reproducir_clic()
                accion()
            return envoltura

        self._boton_continuar = Boton(
            juego,
            (ANCHO_VENTANA // 2 - 130, 640, 260, 58),
            "CONTINUAR",
            icono=iconos.continuar,
            enfatizado=True,
            al_hacer_clic=con_clic(self._juego.comenzar_preguntas),
        )
        self._boton_volver = Boton(
            juego,
            (40, 30, 210, 48),
            "Volver al menú",
            clave_fuente="pequeno",
            icono=iconos.volver,
            color_normal=COLOR_BOTON_SECUNDARIO,
            color_hover=COLOR_BOTON_SECUNDARIO_HOVER,
            color_texto=COLOR_BOTON_SECUNDARIO_TEXTO,
            al_hacer_clic=con_clic(lambda: self._juego.cambiar_pantalla(MENU)),
        )

        margen_lateral = 60
        separacion = 26
        cantidad = TAMANO_FAMILIA_PARTIDA
        ancho_disponible = ANCHO_VENTANA - 2 * margen_lateral
        self._ancho_tarjeta = (ancho_disponible - separacion * (cantidad - 1)) // cantidad
        self._alto_tarjeta = 380
        self._y_tarjeta = 190
        self._margen_lateral = margen_lateral
        self._separacion = separacion

    def al_entrar(self):
        pass

    def procesar_evento(self, evento):
        self._boton_continuar.procesar_evento(evento)
        self._boton_volver.procesar_evento(evento)

    def actualizar(self):
        pos_mouse = pygame.mouse.get_pos()
        self._boton_continuar.actualizar(pos_mouse)
        self._boton_volver.actualizar(pos_mouse)

    def dibujar(self, superficie):
        fuente_titulo = self._juego.fuente("subtitulo")
        fuente_nombre = self._juego.fuente("texto")
        fuente_texto = self._juego.fuente("pequeno")

        dibujar_texto_con_sombra(
            superficie, "Conoce a la familia", fuente_titulo, COLOR_TITULO, (ANCHO_VENTANA // 2, 110)
        )

        for indice, personaje in enumerate(self._juego.familia_actual):
            x = self._margen_lateral + indice * (self._ancho_tarjeta + self._separacion)
            rect = pygame.Rect(x, self._y_tarjeta, self._ancho_tarjeta, self._alto_tarjeta)
            dibujar_panel(superficie, rect, COLOR_FONDO_PANEL, COLOR_BORDE)

            centro_avatar = (rect.centerx, rect.top + 90)
            dibujar_avatar(superficie, personaje, centro_avatar, 60, flotante=True)

            dibujar_texto_centrado(
                superficie, personaje.nombre, fuente_nombre, COLOR_TEXTO, (rect.centerx, rect.top + 190)
            )
            dibujar_texto_centrado(
                superficie, personaje.rol, fuente_texto, COLOR_TEXTO_SUAVE, (rect.centerx, rect.top + 222)
            )
            dibujar_texto_multilinea_centrado(
                superficie,
                personaje.caracteristica,
                fuente_texto,
                COLOR_TEXTO,
                rect.centerx,
                rect.top + 262,
                self._ancho_tarjeta - 24,
            )

        self._boton_continuar.dibujar(superficie)
        self._boton_volver.dibujar(superficie)
