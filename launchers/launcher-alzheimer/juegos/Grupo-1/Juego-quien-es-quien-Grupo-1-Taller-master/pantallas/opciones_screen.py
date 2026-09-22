"""Pantalla de opciones: volumen de música y efectos, activar/desactivar
audio y tamaño de texto (accesibilidad)."""

import pygame

from juego.configuracion import (
    ANCHO_VENTANA,
    COLOR_BOTON_SECUNDARIO,
    COLOR_BOTON_SECUNDARIO_HOVER,
    COLOR_BOTON_SECUNDARIO_TEXTO,
    COLOR_BORDE,
    COLOR_FONDO_PANEL,
    COLOR_TEXTO,
    COLOR_TITULO,
    COLOR_BOTON,
)
from juego.juego import MENU
from . import iconos
from .pantalla import Pantalla
from .boton import Boton
from .utilidades import dibujar_texto_con_sombra, dibujar_panel


class PantallaOpciones(Pantalla):
    def __init__(self, juego):
        super().__init__(juego)
        opciones = juego.opciones

        def con_clic(accion):
            def envoltura():
                self._juego.audio.reproducir_clic()
                accion()
            return envoltura

        x_etiqueta = 230
        x_control = 640
        ancho_barra = 260
        self._x_control = x_control
        self._ancho_barra = ancho_barra

        y_musica = 210
        y_efectos = 290
        y_activar_musica = 370
        y_activar_efectos = 440
        y_tamano_texto = 510
        self._filas = {
            "musica": y_musica,
            "efectos": y_efectos,
        }

        self._boton_menos_musica = Boton(
            juego, (x_control, y_musica - 22, 44, 44), "-",
            al_hacer_clic=con_clic(opciones.bajar_volumen_musica),
        )
        self._boton_mas_musica = Boton(
            juego, (x_control + ancho_barra + 56, y_musica - 22, 44, 44), "+",
            al_hacer_clic=con_clic(opciones.subir_volumen_musica),
        )
        self._boton_menos_efectos = Boton(
            juego, (x_control, y_efectos - 22, 44, 44), "-",
            al_hacer_clic=con_clic(opciones.bajar_volumen_efectos),
        )
        self._boton_mas_efectos = Boton(
            juego, (x_control + ancho_barra + 56, y_efectos - 22, 44, 44), "+",
            al_hacer_clic=con_clic(opciones.subir_volumen_efectos),
        )

        ancho_toggle = 200
        self._boton_musica_activa = Boton(
            juego, (x_control, y_activar_musica - 24, ancho_toggle, 48), "",
            al_hacer_clic=con_clic(opciones.alternar_musica),
        )
        self._boton_efectos_activos = Boton(
            juego, (x_control, y_activar_efectos - 24, ancho_toggle, 48), "",
            al_hacer_clic=con_clic(opciones.alternar_efectos),
        )
        self._boton_tamano_texto = Boton(
            juego, (x_control, y_tamano_texto - 24, ancho_toggle, 48), "",
            al_hacer_clic=con_clic(opciones.alternar_tamano_texto),
        )

        self._y_activar_musica = y_activar_musica
        self._y_activar_efectos = y_activar_efectos
        self._y_tamano_texto = y_tamano_texto
        self._x_etiqueta = x_etiqueta

        self._boton_volver = Boton(
            juego,
            (ANCHO_VENTANA // 2 - 130, 650, 260, 58),
            "VOLVER AL MENÚ",
            icono=iconos.volver,
            color_normal=COLOR_BOTON_SECUNDARIO,
            color_hover=COLOR_BOTON_SECUNDARIO_HOVER,
            color_texto=COLOR_BOTON_SECUNDARIO_TEXTO,
            al_hacer_clic=con_clic(lambda: self._juego.cambiar_pantalla(MENU)),
        )

        self._botones = [
            self._boton_menos_musica,
            self._boton_mas_musica,
            self._boton_menos_efectos,
            self._boton_mas_efectos,
            self._boton_musica_activa,
            self._boton_efectos_activos,
            self._boton_tamano_texto,
            self._boton_volver,
        ]

    def _actualizar_textos_toggle(self):
        opciones = self._juego.opciones
        self._boton_musica_activa.texto = "Activada" if opciones.musica_activa else "Desactivada"
        self._boton_efectos_activos.texto = "Activados" if opciones.efectos_activos else "Desactivados"
        self._boton_tamano_texto.texto = "Grande" if opciones.tamano_texto == "grande" else "Normal"

    def procesar_evento(self, evento):
        for boton in self._botones:
            boton.procesar_evento(evento)

    def actualizar(self):
        self._actualizar_textos_toggle()
        pos_mouse = pygame.mouse.get_pos()
        for boton in self._botones:
            boton.actualizar(pos_mouse)

    def _dibujar_barra_volumen(self, superficie, y, nivel):
        rect_fondo = pygame.Rect(self._x_control, y - 10, self._ancho_barra, 20)
        pygame.draw.rect(superficie, COLOR_BORDE, rect_fondo, border_radius=10)
        ancho_relleno = max(20, int(self._ancho_barra * nivel))
        rect_relleno = pygame.Rect(self._x_control, y - 10, ancho_relleno, 20)
        pygame.draw.rect(superficie, COLOR_BOTON, rect_relleno, border_radius=10)
        pygame.draw.circle(superficie, (255, 255, 255), (self._x_control + ancho_relleno - 10, y), 11)
        pygame.draw.circle(superficie, COLOR_BOTON, (self._x_control + ancho_relleno - 10, y), 11, width=3)

    def dibujar(self, superficie):
        juego = self._juego
        opciones = juego.opciones
        fuente_titulo = juego.fuente("subtitulo")
        fuente_texto = juego.fuente("texto")

        dibujar_texto_con_sombra(superficie, "Opciones", fuente_titulo, COLOR_TITULO, (ANCHO_VENTANA // 2, 110))

        panel = pygame.Rect(0, 0, 900, 480)
        panel.center = (ANCHO_VENTANA // 2, 390)
        dibujar_panel(superficie, panel, COLOR_FONDO_PANEL, COLOR_BORDE)

        fuente_etiqueta = fuente_texto
        superficie_texto = fuente_etiqueta.render("Volumen de música", True, COLOR_TEXTO)
        superficie.blit(superficie_texto, (self._x_etiqueta, self._filas["musica"] - superficie_texto.get_height() // 2))
        superficie_texto = fuente_etiqueta.render("Volumen de efectos", True, COLOR_TEXTO)
        superficie.blit(superficie_texto, (self._x_etiqueta, self._filas["efectos"] - superficie_texto.get_height() // 2))
        superficie_texto = fuente_etiqueta.render("Música de fondo", True, COLOR_TEXTO)
        superficie.blit(superficie_texto, (self._x_etiqueta, self._y_activar_musica - superficie_texto.get_height() // 2))
        superficie_texto = fuente_etiqueta.render("Efectos de sonido", True, COLOR_TEXTO)
        superficie.blit(superficie_texto, (self._x_etiqueta, self._y_activar_efectos - superficie_texto.get_height() // 2))
        superficie_texto = fuente_etiqueta.render("Tamaño de texto", True, COLOR_TEXTO)
        superficie.blit(superficie_texto, (self._x_etiqueta, self._y_tamano_texto - superficie_texto.get_height() // 2))

        self._dibujar_barra_volumen(superficie, self._filas["musica"], opciones.volumen_musica)
        self._dibujar_barra_volumen(superficie, self._filas["efectos"], opciones.volumen_efectos)

        for boton in self._botones:
            boton.dibujar(superficie)
