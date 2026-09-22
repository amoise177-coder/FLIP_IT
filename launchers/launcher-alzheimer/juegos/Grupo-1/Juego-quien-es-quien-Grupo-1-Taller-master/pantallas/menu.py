"""Pantalla de menú principal: navegación y fondo multimedia del juego."""

import pygame

from juego.configuracion import (
    ALTO_VENTANA,
    ANCHO_VENTANA,
    COLOR_BORDE,
    COLOR_FONDO_PANEL,
    COLOR_TEXTO_SUAVE,
    COLOR_TITULO,
    RUTA_IMAGEN_MENU,
)
from juego.juego import CREDITOS, OPCIONES_PANTALLA
from . import iconos
from .pantalla import Pantalla
from .boton import Boton
from .avatar import dibujar_avatar
from .imagen_fondo import FondoImagen
from .utilidades import dibujar_panel, dibujar_texto_centrado, dibujar_texto_con_sombra


class MenuPrincipal(Pantalla):
    """Pantalla principal que compone UI + fondo de imagen."""

    def __init__(self, juego):
        super().__init__(juego)
        self._fondo_imagen = FondoImagen(RUTA_IMAGEN_MENU, (ANCHO_VENTANA, ALTO_VENTANA))

        ancho_boton, alto_boton = 380, 66
        x = (ANCHO_VENTANA - ancho_boton) // 2
        y_inicial = 360
        separacion = 78

        def con_clic(accion):
            def envoltura():
                self._juego.audio.reproducir_clic()
                accion()
            return envoltura

        padding_panel = 30
        y_superior_botones = y_inicial
        y_inferior_botones = y_inicial + separacion * 3 + alto_boton
        self._panel = pygame.Rect(
            0,
            0,
            ancho_boton + 120,
            (y_inferior_botones - y_superior_botones) + padding_panel * 2,
        )
        self._panel.center = (
            ANCHO_VENTANA // 2,
            (y_superior_botones + y_inferior_botones) // 2,
        )

        self._botones = [
            Boton(
                juego,
                (x, y_inicial, ancho_boton, alto_boton),
                "JUGAR",
                icono=iconos.jugar,
                enfatizado=True,
                al_hacer_clic=con_clic(self._juego.iniciar_partida),
            ),
            Boton(
                juego,
                (x, y_inicial + separacion, ancho_boton, alto_boton),
                "OPCIONES",
                icono=iconos.opciones,
                al_hacer_clic=con_clic(lambda: self._juego.cambiar_pantalla(OPCIONES_PANTALLA)),
            ),
            Boton(
                juego,
                (x, y_inicial + separacion * 2, ancho_boton, alto_boton),
                "CRÉDITOS",
                icono=iconos.creditos,
                al_hacer_clic=con_clic(lambda: self._juego.cambiar_pantalla(CREDITOS)),
            ),
            Boton(
                juego,
                (x, y_inicial + separacion * 3, ancho_boton, alto_boton),
                "SALIR",
                icono=iconos.salir,
                color_normal=COLOR_BORDE,
                color_hover=(198, 184, 164),
                color_texto=(70, 60, 50),
                al_hacer_clic=con_clic(self._juego.salir),
            ),
        ]

    def procesar_evento(self, evento):
        for boton in self._botones:
            boton.procesar_evento(evento)

    def actualizar(self):
        self._fondo_imagen.actualizar()
        pos_mouse = pygame.mouse.get_pos()
        for boton in self._botones:
            boton.actualizar(pos_mouse)

    def dibujar(self, superficie):
        # Si el asset de imagen está disponible, reemplaza visualmente el
        # fondo generado por Juego.dibujar(). Si falta, se conserva el
        # degradado existente como fallback seguro.
        if self._fondo_imagen.disponible:
            self._fondo_imagen.dibujar(superficie)

        fuente_titulo = self._juego.fuente("titulo_menu")
        fuente_subtitulo = self._juego.fuente("subtitulo")

        # Cabecera translúcida para separar el título del video y garantizar
        # que las animaciones de los personajes no oculten el texto.
        cabecera = pygame.Surface((920, 150), pygame.SRCALPHA)
        pygame.draw.rect(cabecera, (255, 255, 255, 180), cabecera.get_rect(), border_radius=34)
        pygame.draw.rect(cabecera, (210, 200, 185, 170), cabecera.get_rect(), width=2, border_radius=34)
        superficie.blit(cabecera, cabecera.get_rect(center=(ANCHO_VENTANA // 2, 105)))

        dibujar_texto_con_sombra(
            superficie,
            "¿Quién es quién?",
            fuente_titulo,
            COLOR_TITULO,
            (ANCHO_VENTANA // 2, 72),
        )
        dibujar_texto_centrado(
            superficie,
            "Conoce a la familia y pon a prueba tu memoria",
            fuente_subtitulo,
            COLOR_TEXTO_SUAVE,
            (ANCHO_VENTANA // 2, 136),
        )

        # La hilera de avatares se baja respecto al título para evitar
        # cualquier solapamiento durante la animación de flotación.
        personajes = self._juego.personajes
        n = len(personajes)
        radio_avatar = 44 if n <= 5 else 34
        separacion_avatares = 118 if n <= 5 else 92
        x_inicial = ANCHO_VENTANA // 2 - separacion_avatares * (n - 1) // 2
        for indice, personaje in enumerate(personajes):
            offset_y = -8 if indice % 2 == 0 else 8
            centro = (
                x_inicial + indice * separacion_avatares,
                242 + offset_y,
            )
            dibujar_avatar(superficie, personaje, centro, radio_avatar, flotante=True)

        dibujar_panel(superficie, self._panel, COLOR_FONDO_PANEL, COLOR_BORDE, radio_borde=26)

        for boton in self._botones:
            boton.dibujar(superficie)

    def al_cerrar(self):
        self._fondo_imagen.al_cerrar()
