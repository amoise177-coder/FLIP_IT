"""Pantalla de resultado final: muestra la puntuación de forma
motivacional, sin transmitir que equivocarse sea un fracaso."""

import pygame

from juego.configuracion import ANCHO_VENTANA, COLOR_TEXTO, COLOR_TEXTO_SUAVE, COLOR_TITULO
from juego.juego import MENU
from . import iconos
from .pantalla import Pantalla
from .boton import Boton
from .utilidades import dibujar_texto_centrado, dibujar_panel
from juego.configuracion import COLOR_FONDO_PANEL, COLOR_BORDE, COLOR_BOTON_SECUNDARIO, COLOR_BOTON_SECUNDARIO_HOVER, COLOR_BOTON_SECUNDARIO_TEXTO


def _mensaje_motivacional(correctas, total):
    proporcion = correctas / total if total else 0
    if proporcion >= 0.99:
        return "¡Excelente memoria! Recordaste todo a la perfección."
    if proporcion >= 0.6:
        return "¡Muy bien hecho! Cada vez conoces mejor a la familia."
    return "¡Buen intento! Sigamos conociéndonos un poco más."


class PantallaResultado(Pantalla):
    def __init__(self, juego):
        super().__init__(juego)

        def con_clic(accion):
            def envoltura():
                self._juego.audio.reproducir_clic()
                accion()
            return envoltura

        ancho_boton, alto_boton = 300, 62
        separacion = 30
        ancho_total = ancho_boton * 2 + separacion
        x_inicial = (ANCHO_VENTANA - ancho_total) // 2
        y = 500

        self._boton_jugar_de_nuevo = Boton(
            juego,
            (x_inicial, y, ancho_boton, alto_boton),
            "JUGAR DE NUEVO",
            icono=iconos.reiniciar,
            enfatizado=True,
            al_hacer_clic=con_clic(self._juego.iniciar_partida),
        )
        self._boton_volver_menu = Boton(
            juego,
            (x_inicial + ancho_boton + separacion, y, ancho_boton, alto_boton),
            "VOLVER AL MENÚ",
            icono=iconos.volver,
            color_normal=COLOR_BOTON_SECUNDARIO,
            color_hover=COLOR_BOTON_SECUNDARIO_HOVER,
            color_texto=COLOR_BOTON_SECUNDARIO_TEXTO,
            al_hacer_clic=con_clic(lambda: self._juego.cambiar_pantalla(MENU)),
        )

    def procesar_evento(self, evento):
        self._boton_jugar_de_nuevo.procesar_evento(evento)
        self._boton_volver_menu.procesar_evento(evento)

    def actualizar(self):
        pos_mouse = pygame.mouse.get_pos()
        self._boton_jugar_de_nuevo.actualizar(pos_mouse)
        self._boton_volver_menu.actualizar(pos_mouse)

    def dibujar(self, superficie):
        jugador = self._juego.jugador
        total = self._juego.total_preguntas()

        fuente_titulo = self._juego.fuente("titulo")
        fuente_subtitulo = self._juego.fuente("subtitulo")
        fuente_texto = self._juego.fuente("texto")

        panel = pygame.Rect(0, 0, 640, 320)
        panel.center = (ANCHO_VENTANA // 2, 300)
        dibujar_panel(superficie, panel, COLOR_FONDO_PANEL, COLOR_BORDE)

        dibujar_texto_centrado(
            superficie,
            _mensaje_motivacional(jugador.respuestas_correctas, total),
            fuente_subtitulo,
            COLOR_TITULO,
            (ANCHO_VENTANA // 2, panel.top + 60),
        )
        dibujar_texto_centrado(
            superficie,
            f"Puntuación: {jugador.puntuacion} puntos",
            fuente_titulo,
            COLOR_TEXTO,
            (ANCHO_VENTANA // 2, panel.top + 150),
        )
        dibujar_texto_centrado(
            superficie,
            f"Respuestas correctas: {jugador.respuestas_correctas} de {total}",
            fuente_texto,
            COLOR_TEXTO_SUAVE,
            (ANCHO_VENTANA // 2, panel.top + 220),
        )

        self._boton_jugar_de_nuevo.dibujar(superficie)
        self._boton_volver_menu.dibujar(superficie)
