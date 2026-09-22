"""
Pantalla de Opciones.

Permite ajustar el volumen de la música de fondo y de los efectos del juego
con deslizadores visuales estilo pastel, coherentes con el resto del juego.
"""

import pygame

import constantes
import ui
from audio import play_efecto, reproducir_musica, aplicar_volumen_musica


class Deslizador:
    """Barra deslizante horizontal para ajustar un valor entre 0.0 y 1.0."""

    def __init__(self, x, y, ancho, valor_inicial, paleta=ui.AZUL, etiqueta=""):
        self.x = x
        self.y = y
        self.ancho = ancho
        self.alto = 14
        self.radio_pomo = 18
        self.valor = max(0.0, min(1.0, valor_inicial))
        self.paleta = paleta
        self.etiqueta = etiqueta
        self.arrastrando = False
        self.f_etiqueta = ui.fuente(24, negrita=True)
        self.f_valor = ui.fuente(20, negrita=False)

    @property
    def rect_barra(self):
        return pygame.Rect(self.x, self.y - self.alto // 2,
                           self.ancho, self.alto)

    @property
    def pos_pomo(self):
        return (int(self.x + self.valor * self.ancho), self.y)

    def _zona_interaccion(self):
        """Zona amplia alrededor del pomo y la barra para facilitar el clic."""
        return pygame.Rect(self.x - self.radio_pomo,
                           self.y - self.radio_pomo - 4,
                           self.ancho + self.radio_pomo * 2,
                           self.radio_pomo * 2 + 8)

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self._zona_interaccion().collidepoint(evento.pos):
                self.arrastrando = True
                self._actualizar_valor(evento.pos[0])
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastrando = False
        elif evento.type == pygame.MOUSEMOTION and self.arrastrando:
            self._actualizar_valor(evento.pos[0])

    def _actualizar_valor(self, mx):
        self.valor = max(0.0, min(1.0, (mx - self.x) / self.ancho))

    def dibujar(self, destino):
        # Etiqueta
        ui.texto_centrado(destino, self.etiqueta, self.f_etiqueta,
                          ui.TEXTO, (self.x + self.ancho // 2, self.y - 40))

        # Pista de fondo (gris)
        pygame.draw.rect(destino, (210, 206, 218),
                         self.rect_barra, border_radius=self.alto // 2)

        # Pista rellena (color)
        relleno = pygame.Rect(self.x, self.y - self.alto // 2,
                              int(self.valor * self.ancho), self.alto)
        if relleno.width > 0:
            pygame.draw.rect(destino, self.paleta[1],
                             relleno, border_radius=self.alto // 2)

        # Pomo
        px, py = self.pos_pomo
        pygame.draw.circle(destino, ui.BLANCO, (px, py), self.radio_pomo + 3)
        pygame.draw.circle(destino, self.paleta[1], (px, py), self.radio_pomo)
        pygame.draw.circle(destino, ui.BLANCO, (px, py), self.radio_pomo, 3)

        # Porcentaje
        pct = f"{int(self.valor * 100)}%"
        ui.texto_centrado(destino, pct, self.f_valor, ui.TEXTO_SUAVE,
                          (self.x + self.ancho + 50, self.y))


def ejecutar_opciones(ventana, reloj):
    """Pantalla de opciones con deslizadores de volumen."""
    fondo = pygame.transform.smoothscale(
        constantes.get_fondo_menu(), (constantes.ANCHO, constantes.ALTO)
    )
    reproducir_musica(constantes.MUSICA_MENU)

    f_titulo = ui.fuente(52, negrita=True)

    panel_rect = pygame.Rect(0, 0, 700, 320)
    panel_rect.center = (constantes.ANCHO // 2, 370)

    cx = constantes.ANCHO // 2
    slider_ancho = 400
    slider_x = cx - slider_ancho // 2

    slider_musica = Deslizador(
        slider_x, panel_rect.y + 100, slider_ancho,
        constantes.VOLUMEN_MUSICA, paleta=ui.LAVANDA,
        etiqueta="Música de fondo"
    )
    slider_efectos = Deslizador(
        slider_x, panel_rect.y + 220, slider_ancho,
        constantes.VOLUMEN_EFECTOS, paleta=ui.AZUL,
        etiqueta="Efectos del juego"
    )

    btn_volver = ui.Boton(cx, panel_rect.bottom + 60, 260, 60, "Volver",
                          ui.NEUTRO, tam_texto=26)

    fundido = 1.0

    while True:
        dt = reloj.tick(constantes.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        presionando = pygame.mouse.get_pressed()[0]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE,
                                                                 pygame.K_RETURN):
                return
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_volver.rect.collidepoint(evento.pos):
                    play_efecto("boton")
                    return

            slider_musica.manejar_evento(evento)
            slider_efectos.manejar_evento(evento)

        # Aplicar cambios de volumen en tiempo real
        constantes.VOLUMEN_MUSICA = slider_musica.valor
        constantes.VOLUMEN_EFECTOS = slider_efectos.valor
        aplicar_volumen_musica()

        # Dibujar
        ventana.blit(fondo, (0, 0))
        ui.texto_centrado(ventana, "Opciones", f_titulo, ui.TEXTO,
                          (cx, 130), sombra=ui.BLANCO)

        ui.panel(ventana, panel_rect, radio=30)

        slider_musica.dibujar(ventana)
        slider_efectos.dibujar(ventana)

        btn_volver.actualizar(mouse_pos, presionando)
        btn_volver.dibujar(ventana)

        if fundido > 0.01:
            fundido = max(0.0, fundido - dt * 4.5)
            velo = pygame.Surface((constantes.ANCHO, constantes.ALTO), pygame.SRCALPHA)
            velo.fill((255, 255, 255, int(200 * fundido)))
            ventana.blit(velo, (0, 0))

        pygame.display.update()
