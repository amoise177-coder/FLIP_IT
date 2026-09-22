"""
MenteActiva — Pantalla de Juego
Renderiza el tablero, la barra de estado superior, los controles inferiores
y los mensajes de retroalimentación durante la partida.
"""
import math
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, Colors, ScreenName,
)
from ui.renderer import (
    draw_text, draw_text_shadow, draw_background,
    draw_panel, Boton, reset_cursor, SistemaParticulas,
)
from core.game_manager import GameManager, GameState


class PantallaJuego:
    """
    Pantalla principal de juego.
    Muestra el tablero, información de la partida y botones de acción.
    """

    def __init__(self, game_manager):
        """
        Args:
            game_manager (GameManager): Instancia del orquestador del juego.
        """
        self._gm = game_manager
        self._particulas = SistemaParticulas()

        # Botones de la barra inferior
        self._botones = self._crear_botones()

        self._preview_msg_alpha = 255
        self._match_particle_emitted = set()

    def _crear_botones(self):
        """Crea los botones de la barra inferior."""
        btn_h = 40
        btn_y = WINDOW_HEIGHT - 60
        botones = {}

        # Botón Pausa
        botones["pausa"] = Boton(
            20, btn_y, 110, btn_h, "Pausa",
            color=Colors.LAVENDER,
            text_color=Colors.DARK_TEXT,
            font_key="small",
            on_click=lambda: self._gm.toggle_pausa(),
        )

        # Botón Reiniciar
        botones["reiniciar"] = Boton(
            145, btn_y, 130, btn_h, "Reiniciar",
            color=Colors.WARM_ROSE,
            text_color=Colors.DARK_TEXT,
            font_key="small",
            on_click=lambda: self._gm.reiniciar(),
        )

        # Botón Menú
        botones["menu"] = Boton(
            290, btn_y, 110, btn_h, "Menu",
            color=Colors.TEAL,
            text_color=Colors.DARK_TEXT,
            font_key="small",
        )

        return botones

    # ── Interfaz de pantalla ─────────────────────────────────────────────

    def handle_event(self, event):
        """
        Procesa eventos. Retorna transición de pantalla o None.
        """
        # Botones de interfaz
        reset_cursor()

        for key, btn in self._botones.items():
            if btn.handle_event(event):
                if key == "menu":
                    return (ScreenName.MENU, None)

        # Teclas especiales
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self._gm.toggle_pausa()
                return None
            elif event.key == pygame.K_r:
                self._gm.reiniciar()
                self._particulas.clear()
                self._match_particle_emitted.clear()
                return None
            elif event.key == pygame.K_ESCAPE:
                return (ScreenName.MENU, None)

        # Eventos del juego
        self._gm.manejar_evento(event)

        return None

    def update(self, dt):
        """Actualiza la lógica del juego y la interfaz."""
        mouse_pos = pygame.mouse.get_pos()

        # Actualizar botones
        for btn in self._botones.values():
            btn.update(dt, mouse_pos)

        # Actualizar juego
        result = self._gm.actualizar(dt)

        # Partículas de acierto
        if self._gm.estado == GameState.SHOWING_MATCH:
            # Emitir partículas en la posición de las cartas emparejadas
            for carta in self._gm.tablero.cartas:
                if (carta and carta.estado.value == "emparejada"
                        and carta.pair_id not in self._match_particle_emitted):
                    self._particulas.emitir(
                        carta.rect.centerx, carta.rect.centery, 12
                    )
            if self._gm.tablero.primera_seleccion:
                pid = self._gm.tablero.primera_seleccion.pair_id
                self._match_particle_emitted.add(pid)

        # Partículas
        self._particulas.update(dt)

        # Victoria
        if result == "victoria":
            self._particulas.emitir_lluvia(WINDOW_WIDTH, 50)
            return (ScreenName.VICTORY, {
                "intentos": self._gm.intentos,
                "aciertos": self._gm.aciertos,
                "fallos": self._gm.fallos,
                "parejas": self._gm.total_parejas,
                "dificultad": self._gm.dificultad,
            })

        return None

    def draw(self, surface):
        """Dibuja toda la pantalla de juego."""
        draw_background(surface)

        # ── Barra superior ──
        self._draw_header(surface)

        # ── Tablero ──
        self._gm.dibujar(surface)

        # ── Mensaje de retroalimentación ──
        if self._gm.mensaje:
            self._draw_message(surface)

        # ── Mensaje de previsualización ──
        if self._gm.estado == GameState.PREVIEW:
            self._draw_preview_message(surface)

        # ── Partículas ──
        self._particulas.draw(surface)

        # ── Barra inferior ──
        self._draw_footer(surface)

        # ── Overlay de pausa ──
        if self._gm.pausado:
            self._draw_pause_overlay(surface)

    # ── Componentes de dibujo ────────────────────────────────────────────

    def _draw_header(self, surface):
        """Dibuja la barra de información superior."""
        # Panel semi-transparente
        draw_panel(surface, pygame.Rect(0, 0, WINDOW_WIDTH, 75),
                   color=(235, 245, 251), alpha=230)

        # Información izquierda: nivel
        nivel_txt = self._gm.config.name
        draw_text(surface, f"Nivel: {nivel_txt}",
                  15, 25, "body", Colors.DARK_TEXT, bold=True, center=False)

        # Centro: parejas encontradas
        parejas = self._gm.parejas_encontradas
        total = self._gm.total_parejas
        draw_text(surface, f"Parejas: {parejas} / {total}",
                  WINDOW_WIDTH // 2, 25, "body", Colors.DARK_TEXT, bold=True)

        # Barra de progreso
        bar_w = 200
        bar_h = 10
        bar_x = WINDOW_WIDTH // 2 - bar_w // 2
        bar_y = 45
        # Fondo
        pygame.draw.rect(surface, (200, 200, 210),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        # Progreso
        progress = parejas / max(total, 1)
        fill_w = int(bar_w * progress)
        if fill_w > 0:
            pygame.draw.rect(surface, Colors.SUCCESS,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=5)

        # Derecha: intentos
        draw_text(surface, f"Intentos: {self._gm.intentos}",
                  WINDOW_WIDTH - 15, 25, "body", Colors.DARK_TEXT, center=False)

        # Línea separadora
        pygame.draw.line(surface, (210, 210, 220), (0, 74), (WINDOW_WIDTH, 74), 1)

    def _draw_footer(self, surface):
        """Dibuja la barra inferior con botones."""
        # Panel
        draw_panel(surface, pygame.Rect(0, WINDOW_HEIGHT - 70, WINDOW_WIDTH, 70),
                   color=(235, 245, 251), alpha=230)
        pygame.draw.line(surface, (210, 210, 220),
                         (0, WINDOW_HEIGHT - 70), (WINDOW_WIDTH, WINDOW_HEIGHT - 70), 1)

        # Botones
        for btn in self._botones.values():
            btn.draw(surface)

    def _draw_message(self, surface):
        """Dibuja el mensaje de retroalimentación animado (solo texto, sin recuadro)."""
        msg = self._gm.mensaje
        timer = self._gm.mensaje_timer
        color = self._gm.mensaje_color

        # Fade out en el último 30% del tiempo
        alpha = min(255, int(255 * timer / 0.5)) if timer < 0.5 else 255

        # Posición centrada, ligeramente arriba del tablero
        y = WINDOW_HEIGHT // 2 - 10
        # Escala de entrada
        scale = min(1.0, (1.5 - timer) * 3) if timer < 1.5 else 1.0

        font_size = 38
        font = pygame.font.SysFont("segoeui", font_size, bold=True)

        # Sombra del texto para legibilidad
        shadow_surf = font.render(msg, True, (40, 40, 50))
        shadow_surf.set_alpha(alpha)
        shadow_rect = shadow_surf.get_rect(center=(WINDOW_WIDTH // 2 + 2, y + 2))
        surface.blit(shadow_surf, shadow_rect)

        # Texto principal con el color del mensaje
        txt_surf = font.render(msg, True, color)
        txt_surf.set_alpha(alpha)
        txt_rect = txt_surf.get_rect(center=(WINDOW_WIDTH // 2, y))
        surface.blit(txt_surf, txt_rect)

    def _draw_preview_message(self, surface):
        """Dibuja el mensaje de previsualización."""
        draw_text_shadow(surface, "Memoriza las posiciones!",
                         WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                         "heading", Colors.CORAL, bold=True)
        draw_text(surface, "Clic o tecla para comenzar",
                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40,
                  "small", Colors.DARK_TEXT)

    def _draw_pause_overlay(self, surface):
        """Dibuja el overlay de pausa."""
        from ui.pantalla_pausa import dibujar_pausa
        dibujar_pausa(surface)
