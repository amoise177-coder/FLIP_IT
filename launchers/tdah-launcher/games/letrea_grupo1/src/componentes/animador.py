from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.motor import JuegoLetrea

class AnimadorMaestraD:
    ESTADO_INACTIVA = 0
    ESTADO_DELAY = 1
    ESTADO_ENTRANDO = 2
    ESTADO_VISIBLE = 3
    ESTADO_SALIENDO = 4

    def __init__(self, juego: JuegoLetrea, x_base: int = 25, y_bottom: int = 710, alto_base: int = 330):
        self.juego = juego
        self.x_base = x_base
        self.y_bottom = y_bottom
        self.alto_base = alto_base
        self.estado = self.ESTADO_INACTIVA

        self.pose = "MD1"
        self.audio_id: str | None = None
        self.canal_audio: pygame.mixer.Channel | None = None
        self.contador = 0
        self.duracion_delay = 0
        self.duracion_anim_entrada = 16  # fotogramas (~0.27s)
        self.duracion_anim_salida = 14   # fotogramas (~0.23s)
        self.timer_espera = 0
        self.escala_actual = 0.0

    def activar(self, pose: str, audio_id: str | None = None, delay_frames: int = 0) -> None:
        """Activa la aparición de la Maestra D con una pose, audio opcional y delay configurable."""
        self.pose = pose
        self.audio_id = audio_id
        self.duracion_delay = delay_frames
        self.contador = 0
        if delay_frames > 0:
            self.estado = self.ESTADO_DELAY
            self.escala_actual = 0.0
        else:
            self._iniciar_entrada()

    def _iniciar_entrada(self) -> None:
        self.estado = self.ESTADO_ENTRANDO
        self.contador = 0
        self.canal_audio = None
        if self.audio_id:
            self.canal_audio = self.juego.audio.reproducir(self.audio_id)
        self.timer_espera = int(self.juego.FPS * 2.2)

    def _ease_out_back(self, t: float) -> float:
        """Función matemática de rebote (overshoot) al entrar."""
        s = 1.6
        t = t - 1.0
        return t * t * ((s + 1) * t + s) + 1.0

    def _ease_in_back(self, t: float) -> float:
        """Función matemática de rebote al desaparecer."""
        s = 1.4
        return t * t * ((s + 1) * t - s)

    def actualizar(self) -> None:
        """Actualiza la máquina de estados y las escalas de interpolación de la Maestra D."""
        if self.estado == self.ESTADO_INACTIVA:
            return

        if self.estado == self.ESTADO_DELAY:
            self.contador += 1
            if self.contador >= self.duracion_delay:
                self._iniciar_entrada()

        elif self.estado == self.ESTADO_ENTRANDO:
            self.contador += 1
            t = min(1.0, self.contador / self.duracion_anim_entrada)
            self.escala_actual = max(0.0, self._ease_out_back(t))
            if t >= 1.0:
                self.escala_actual = 1.0
                self.estado = self.ESTADO_VISIBLE

        elif self.estado == self.ESTADO_VISIBLE:
            self.escala_actual = 1.0
            if self.timer_espera > 0:
                self.timer_espera -= 1

            audio_reproduciendo = self.canal_audio is not None and self.canal_audio.get_busy()
            if not audio_reproduciendo and (self.canal_audio is not None or self.timer_espera <= 0):
                self.estado = self.ESTADO_SALIENDO
                self.contador = 0

        elif self.estado == self.ESTADO_SALIENDO:
            self.contador += 1
            t = min(1.0, self.contador / self.duracion_anim_salida)
            self.escala_actual = max(0.0, 1.0 - self._ease_in_back(t))
            if t >= 1.0:
                self.escala_actual = 0.0
                self.estado = self.ESTADO_INACTIVA

    def dibujar(self, superficie: pygame.Surface) -> None:
        """Renderiza la Maestra D en su posición inferior escalada suavemente."""
        if self.estado == self.ESTADO_INACTIVA or self.escala_actual <= 0.02:
            return

        img_base = self.juego.recursos.obtener_maestra_d(self.pose)
        if not img_base:
            return

        ancho_orig, alto_orig = img_base.get_size()
        w = max(1, int(ancho_orig * self.escala_actual))
        h = max(1, int(alto_orig * self.escala_actual))

        blit_x = self.x_base - (w - ancho_orig) // 2
        blit_y = self.y_bottom - h

        try:
            img_escalada = pygame.transform.smoothscale(img_base, (w, h))
            superficie.blit(img_escalada, (blit_x, blit_y))
        except pygame.error:
            pass
