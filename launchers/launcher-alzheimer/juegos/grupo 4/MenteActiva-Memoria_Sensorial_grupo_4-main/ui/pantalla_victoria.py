"""
MenteActiva — Pantalla de Victoria
Celebración con partículas, refuerzo positivo y estadísticas de la partida.
"""
import random
import math
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, Colors, ScreenName,
)
from ui.renderer import (
    draw_text, draw_text_shadow, draw_background,
    draw_panel, Boton, SistemaParticulas, reset_cursor,
)


# Mensajes de refuerzo positivo para la pantalla de victoria
VICTORY_MESSAGES = [
    "Lo lograste!",
    "Felicidades!",
    "Excelente trabajo!",
    "Eres increible!",
    "Muy bien hecho!",
    "Maravilloso!",
]

VICTORY_SUBMESSAGES = [
    "Tu memoria es asombrosa",
    "Cada dia eres mas fuerte!",
    "Que gran logro!",
    "Sigue asi, campeon!",
    "Tu esfuerzo da frutos",
]


class PantallaVictoria:
    """
    Pantalla de celebración mostrada al completar todas las parejas.
    Incluye partículas, estadísticas y botones de acción.
    """

    def __init__(self, datos):
        """
        Args:
            datos (dict): Estadísticas de la partida finalizada.
        """
        self._datos = datos or {}
        self._timer = 0.0
        self._particulas = SistemaParticulas()
        self._mensaje = random.choice(VICTORY_MESSAGES)
        self._submensaje = random.choice(VICTORY_SUBMESSAGES)

        # Emitir celebración inicial
        self._particulas.emitir_lluvia(WINDOW_WIDTH, 60)
        self._next_burst = 1.5

        # Botones
        btn_w = 280
        btn_h = 60
        center_x = WINDOW_WIDTH // 2
        btn_y = 520

        self._botones = {
            "repetir": Boton(
                center_x - btn_w - 15, btn_y, btn_w, btn_h,
                "Jugar de nuevo",
                color=(80, 210, 120),
                text_color=Colors.SOFT_BLACK,
            ),
            "menu": Boton(
                center_x + 15, btn_y, btn_w, btn_h,
                "Volver al menu",
                color=Colors.SKY_BLUE,
                text_color=Colors.SOFT_BLACK,
            ),
        }

    def handle_event(self, event):
        """Procesa eventos. Retorna transición o None."""
        for key, btn in self._botones.items():
            if btn.handle_event(event):
                if key == "repetir":
                    return (ScreenName.GAME, "repetir")
                elif key == "menu":
                    return (ScreenName.MENU, None)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return (ScreenName.MENU, None)
            elif event.key == pygame.K_r:
                return (ScreenName.GAME, "repetir")

        return None

    def update(self, dt):
        """Actualiza animaciones y partículas."""
        self._timer += dt
        mouse_pos = pygame.mouse.get_pos()

        reset_cursor()

        for btn in self._botones.values():
            btn.update(dt, mouse_pos)

        self._particulas.update(dt)

        # Ráfagas periódicas de celebración
        self._next_burst -= dt
        if self._next_burst <= 0:
            self._particulas.emitir_lluvia(WINDOW_WIDTH, 25)
            self._next_burst = 3.0

        return None

    def draw(self, surface):
        """Dibuja la pantalla de victoria."""
        draw_background(surface)

        # ── Partículas de fondo ──
        self._particulas.draw(surface)

        # ── Panel central ──
        panel_w = 700
        panel_h = 350
        panel_x = (WINDOW_WIDTH - panel_w) // 2
        panel_y = 110
        draw_panel(surface, pygame.Rect(panel_x, panel_y, panel_w, panel_h),
                   color=Colors.WHITE, alpha=240)

        # ── Título con animación ──
        scale = 1.0 + 0.03 * math.sin(self._timer * 2)
        title_y = panel_y + 60

        draw_text_shadow(surface, self._mensaje,
                         WINDOW_WIDTH // 2, title_y,
                         "title", Colors.CORAL, bold=True)
        draw_text(surface, self._submensaje,
                  WINDOW_WIDTH // 2, title_y + 55,
                  "body", Colors.DARK_TEXT)

        # ── Estadísticas ──
        stats_y = title_y + 110
        datos = self._datos

        stats = [
            f"Parejas encontradas: {datos.get('parejas', 0)}",
            f"Intentos realizados: {datos.get('intentos', 0)}",
            f"Aciertos: {datos.get('aciertos', 0)}  -  Fallos: {datos.get('fallos', 0)}",
        ]

        for i, stat in enumerate(stats):
            draw_text(surface, stat,
                      WINDOW_WIDTH // 2, stats_y + i * 35,
                      "body", Colors.DARK_TEXT)

        # ── Decoración: estrellas ──
        star_positions = [
            (panel_x + 50, panel_y + 40),
            (panel_x + panel_w - 50, panel_y + 40),
            (panel_x + 30, panel_y + panel_h - 40),
            (panel_x + panel_w - 30, panel_y + panel_h - 40),
        ]
        for i, (sx, sy) in enumerate(star_positions):
            offset = math.sin(self._timer * 1.5 + i) * 5
            from utils.icon_drawer import draw_icon
            draw_icon(surface, "estrella", sx, int(sy + offset), 15, Colors.GOLD)

        # ── Botones ──
        for btn in self._botones.values():
            btn.draw(surface)
