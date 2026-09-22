"""Pantalla de créditos: integrantes, materia, docente y recursos."""

import pygame

from juego.configuracion import (
    ANCHO_VENTANA,
    COLOR_BOTON_SECUNDARIO,
    COLOR_BOTON_SECUNDARIO_HOVER,
    COLOR_BOTON_SECUNDARIO_TEXTO,
    COLOR_BORDE,
    COLOR_FONDO_PANEL,
    COLOR_TEXTO,
    COLOR_TEXTO_SUAVE,
    COLOR_TITULO,
)
from juego.juego import MENU
from . import iconos
from .pantalla import Pantalla
from .boton import Boton
from .utilidades import dibujar_texto_con_sombra, dibujar_panel

INTEGRANTES = ["SALVADOR CORDOVA", "YONATHAN GUAINA"]
MATERIA = "Objetos y Abstracción de Datos"
DOCENTE = "ING PLACIDO MALAVE"
RECURSOS_EXTERNOS = [
    "Pygame (biblioteca libre, https://www.pygame.org)",
    "Assets de imagen, música y efectos proporcionados y modificables por el equipo",
]


class PantallaCreditos(Pantalla):
    def __init__(self, juego):
        super().__init__(juego)

        def con_clic(accion):
            def envoltura():
                self._juego.audio.reproducir_clic()
                accion()
            return envoltura

        self._boton_volver = Boton(
            juego,
            (ANCHO_VENTANA // 2 - 130, 640, 260, 58),
            "VOLVER AL MENÚ",
            icono=iconos.volver,
            color_normal=COLOR_BOTON_SECUNDARIO,
            color_hover=COLOR_BOTON_SECUNDARIO_HOVER,
            color_texto=COLOR_BOTON_SECUNDARIO_TEXTO,
            al_hacer_clic=con_clic(lambda: self._juego.cambiar_pantalla(MENU)),
        )

    def procesar_evento(self, evento):
        self._boton_volver.procesar_evento(evento)

    def actualizar(self):
        self._boton_volver.actualizar(pygame.mouse.get_pos())

    def dibujar(self, superficie):
        fuente_titulo = self._juego.fuente("subtitulo")
        fuente_texto = self._juego.fuente("texto")
        fuente_pequena = self._juego.fuente("pequeno")

        dibujar_texto_con_sombra(
            superficie,
            "Créditos",
            fuente_titulo,
            COLOR_TITULO,
            (ANCHO_VENTANA // 2, 100),
        )

        panel = pygame.Rect(0, 0, 760, 460)
        panel.center = (ANCHO_VENTANA // 2, 380)
        dibujar_panel(superficie, panel, COLOR_FONDO_PANEL, COLOR_BORDE)

        y = panel.top + 40
        texto = fuente_texto.render("Realizado por:", True, COLOR_TEXTO)
        superficie.blit(texto, (panel.left + 50, y))
        y += 40
        for nombre in INTEGRANTES:
            texto = fuente_pequena.render(f"• {nombre}", True, COLOR_TEXTO_SUAVE)
            superficie.blit(texto, (panel.left + 70, y))
            y += 32

        y += 20
        texto = fuente_texto.render(f"Materia: {MATERIA}", True, COLOR_TEXTO)
        superficie.blit(texto, (panel.left + 50, y))
        y += 44
        texto = fuente_texto.render(f"Docente: {DOCENTE}", True, COLOR_TEXTO)
        superficie.blit(texto, (panel.left + 50, y))

        y += 56
        texto = fuente_texto.render("Recursos utilizados:", True, COLOR_TEXTO)
        superficie.blit(texto, (panel.left + 50, y))
        y += 40
        for recurso in RECURSOS_EXTERNOS:
            texto = fuente_pequena.render(f"• {recurso}", True, COLOR_TEXTO_SUAVE)
            superficie.blit(texto, (panel.left + 70, y))
            y += 30

        self._boton_volver.dibujar(superficie)
