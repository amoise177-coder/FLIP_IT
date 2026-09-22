"""Pantalla de pregunta: núcleo de la mecánica de juego.

Funciona igual sin importar el tipo concreto de ``Pregunta`` que esté
activa (identificación, característica, relación o reconocimiento
visual): consulta a la pregunta actual mediante los métodos comunes de
su clase base (``opciones``, ``imagen_personaje``, ``usa_opciones_visuales``,
``comprobar_respuesta``) sin necesidad de preguntar de qué subclase se
trata.
"""

import random

import pygame

from juego.configuracion import (
    ANCHO_VENTANA,
    COLOR_CORRECTO,
    COLOR_FONDO_PANEL,
    COLOR_INCORRECTO,
    COLOR_TEXTO_SUAVE,
    COLOR_TITULO,
)
from . import iconos
from .pantalla import Pantalla
from .boton import Boton
from .avatar import dibujar_avatar
from .utilidades import (
    dibujar_texto_centrado,
    dibujar_texto_multilinea_centrado,
    dibujar_panel,
)


class PantallaPregunta(Pantalla):
    def __init__(self, juego):
        super().__init__(juego)
        self._boton_continuar = Boton(
            juego,
            (ANCHO_VENTANA // 2 - 130, 636, 260, 56),
            "CONTINUAR",
            icono=iconos.continuar,
            enfatizado=True,
            al_hacer_clic=self._continuar,
        )
        self._botones_opciones = []  # lista de (Boton, texto_opcion)
        self._respondida = False
        self._opcion_seleccionada = None
        self._fue_correcta = None

    # --- Ciclo de vida de la pantalla -------------------------------------
    def al_entrar(self):
        self._respondida = False
        self._opcion_seleccionada = None
        self._fue_correcta = None
        self._construir_botones_opciones()

    def _construir_botones_opciones(self):
        pregunta = self._juego.pregunta_actual()
        opciones = pregunta.opciones
        random.shuffle(opciones)

        self._botones_opciones = []

        def con_clic(opcion):
            def envoltura():
                self._elegir_opcion(opcion)
            return envoltura

        if pregunta.usa_opciones_visuales():
            lado = 168
            separacion = 56
            ancho_total = lado * len(opciones) + separacion * (len(opciones) - 1)
            x_inicial = (ANCHO_VENTANA - ancho_total) // 2
            y = 380
            for indice, nombre_opcion in enumerate(opciones):
                personaje = self._juego.obtener_personaje(nombre_opcion)
                x = x_inicial + indice * (lado + separacion)
                boton = Boton(
                    self._juego,
                    (x, y, lado, lado),
                    personaje=personaje,
                    al_hacer_clic=con_clic(nombre_opcion),
                    radio_borde=lado // 2,
                    color_normal=COLOR_FONDO_PANEL,
                    color_hover=COLOR_FONDO_PANEL,
                )
                self._botones_opciones.append((boton, nombre_opcion))
        else:
            ancho_boton = 340
            alto_boton = 72
            separacion = 40
            ancho_total = ancho_boton * len(opciones) + separacion * (len(opciones) - 1)
            x_inicial = (ANCHO_VENTANA - ancho_total) // 2
            y = 410
            for indice, texto_opcion in enumerate(opciones):
                x = x_inicial + indice * (ancho_boton + separacion)
                boton = Boton(
                    self._juego,
                    (x, y, ancho_boton, alto_boton),
                    texto_opcion,
                    al_hacer_clic=con_clic(texto_opcion),
                )
                self._botones_opciones.append((boton, texto_opcion))

    # --- Lógica de interacción ---------------------------------------------
    def _elegir_opcion(self, opcion):
        if self._respondida:
            return
        self._juego.audio.reproducir_clic()
        self._respondida = True
        self._opcion_seleccionada = opcion
        self._fue_correcta = self._juego.responder_pregunta(opcion)

        pregunta = self._juego.pregunta_actual()
        for boton, texto_opcion in self._botones_opciones:
            boton.establecer_deshabilitado(True)
            if texto_opcion == pregunta.respuesta_correcta:
                boton.color_normal = COLOR_CORRECTO
                boton.color_hover = COLOR_CORRECTO
            elif texto_opcion == opcion:
                boton.color_normal = COLOR_INCORRECTO
                boton.color_hover = COLOR_INCORRECTO

    def _continuar(self):
        if not self._respondida:
            return
        self._juego.audio.reproducir_clic()
        self._juego.avanzar_pregunta()

    def procesar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self._respondida:
                self._continuar()
            return

        for boton, _ in self._botones_opciones:
            boton.procesar_evento(evento)
        if self._respondida:
            self._boton_continuar.procesar_evento(evento)

    def actualizar(self):
        pos_mouse = pygame.mouse.get_pos()
        for boton, _ in self._botones_opciones:
            boton.actualizar(pos_mouse)
        if self._respondida:
            self._boton_continuar.actualizar(pos_mouse)

    def dibujar(self, superficie):
        juego = self._juego
        pregunta = juego.pregunta_actual()
        fuente_pequena = juego.fuente("pequeno")
        fuente_texto = juego.fuente("texto")
        fuente_subtitulo = juego.fuente("subtitulo")

        panel_izquierdo = pygame.Rect(0, 0, 230, 50)
        panel_izquierdo.topleft = (50, 22)
        dibujar_panel(superficie, panel_izquierdo, (255, 255, 255), (210, 200, 185), radio_borde=25, grosor_borde=1)
        dibujar_texto_centrado(
            superficie,
            f"Pregunta {juego.numero_pregunta_actual()} de {juego.total_preguntas()}",
            fuente_pequena,
            COLOR_TEXTO_SUAVE,
            panel_izquierdo.center,
        )

        panel_derecho = pygame.Rect(0, 0, 190, 50)
        panel_derecho.topright = (ANCHO_VENTANA - 50, 22)
        dibujar_panel(superficie, panel_derecho, (255, 255, 255), (210, 200, 185), radio_borde=25, grosor_borde=1)
        dibujar_texto_centrado(
            superficie,
            f"Puntos: {juego.jugador.puntuacion}",
            fuente_pequena,
            COLOR_TEXTO_SUAVE,
            panel_derecho.center,
        )

        y_siguiente = dibujar_texto_multilinea_centrado(
            superficie,
            pregunta.enunciado,
            fuente_subtitulo,
            COLOR_TITULO,
            ANCHO_VENTANA // 2,
            110,
            860,
        )

        if pregunta.imagen_personaje():
            personaje = juego.obtener_personaje(pregunta.imagen_personaje())
            dibujar_avatar(superficie, personaje, (ANCHO_VENTANA // 2, max(y_siguiente + 60, 260)), 75)

        for boton, _ in self._botones_opciones:
            boton.dibujar(superficie)

        if self._respondida:
            if self._fue_correcta:
                mensaje = "¡Muy bien! Esa es la respuesta correcta."
                color_mensaje = COLOR_CORRECTO
            else:
                mensaje = f"Tranquilo/a, la respuesta correcta era: {pregunta.respuesta_correcta}"
                color_mensaje = COLOR_INCORRECTO
            dibujar_texto_centrado(
                superficie, mensaje, fuente_texto, color_mensaje, (ANCHO_VENTANA // 2, 590)
            )
            self._boton_continuar.dibujar(superficie)
