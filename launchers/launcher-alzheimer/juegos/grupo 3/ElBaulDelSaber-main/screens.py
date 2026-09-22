"""Pantallas del juego. Cada pantalla hereda de Screen (ABSTRACCIÓN) y ofrece
una transición de entrada suave, fondo con degradado y componentes del tema moderno.

- WelcomeScreen: menú principal con partículas ambientales y tarjeta central.
- GameScreen: HUD (progreso, tema, puntos y racha) + tarjeta de refrán + botones.
- ReflectionScreen: refrán completo, tarjeta de conversación y refuerzo visual.
- AlbumScreen: álbum de recuerdos con tarjetas con sombra.
"""
from abc import ABC, abstractmethod
import math
import os
import random
import pygame

from config import (WIDTH, HEIGHT, BG_TOP, BG_BOTTOM, INK, MUTED, FAINT,
                    PANEL, PANEL_ALT, WHITE, PRIMARY, SECONDARY, SUCCESS, GOLD,
                    ACCENT, ROSE, SHADOW, OVERLAY, FADE_ENTER)
from ui import (Button, TextInput, Popup, Pill, ProgressBar,
                draw_text, draw_panel, draw_background, draw_soft_circle,
                draw_star, lerp_color, wrap, get_font, text_size)


class Ambient:
    """Partículas lentas de fondo: pequeños resplandores que flotan hacia arriba."""

    def __init__(self, count=22, colors=None):
        colors = colors or [GOLD, ROSE, SECONDARY, (255, 255, 255)]
        self._dots = []
        for _ in range(count):
            self._dots.append({
                "fx": random.random(),
                "fy": random.random(),
                "speed": random.uniform(8, 26),
                "radius": random.uniform(6, 22),
                "color": random.choice(colors),
                "phase": random.uniform(0, math.tau),
                "alpha": random.uniform(28, 72),
            })

    def draw(self, surface, time):
        for d in self._dots:
            y = (d["fy"] * HEIGHT - time * d["speed"]) % (HEIGHT + 80) - 40
            x = d["fx"] * WIDTH + math.sin(time * 0.6 + d["phase"]) * 46
            draw_soft_circle(surface, x, y, d["radius"], d["color"], d["alpha"])


class Screen(ABC):
    """ABSTRACCIÓN de una pantalla navegable con fundido de entrada."""

    def __init__(self, app, bg_top=BG_TOP, bg_bottom=BG_TOP):
        self._app = app
        self._fade = 1.0          # 1 → 0 (fundido de entrada)
        self._bg_top, self._bg_bottom = bg_top, bg_bottom

    @property
    def app(self):
        return self._app

    def update(self, dt):
        self._fade = max(0.0, self._fade - dt / FADE_ENTER)

    def draw_background(self, surface):
        draw_background(surface, self._bg_top, self._bg_bottom)

    def finish(self, surface):
        """Aplica el fundido de entrada por encima de todo lo dibujado."""
        if self._fade > 0:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((*OVERLAY, int(190 * self._fade)))
            surface.blit(ov, (0, 0))

    @abstractmethod
    def draw(self, surface): ...

    @abstractmethod
    def handle_event(self, event): ...


class WelcomeScreen(Screen):
    def __init__(self, app):
        super().__init__(app, BG_TOP, BG_BOTTOM)
        self._start = Button((340, 512, 280, 72), "Comenzar", PRIMARY, app.start_game,
                             radius=24, size=28, icon="★")
        self._exit = Button((660, 512, 280, 72), "Salir", (220, 80, 80), app.stop,
                            radius=24, size=28)
        self._ambient = Ambient(24)
        self._time = 0.0
        chest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "assets", "Imagen", "cofre_final.png")
        chest_img = pygame.image.load(chest_path)
        self._chest_w = 150
        self._chest = pygame.transform.smoothscale(
            chest_img, (self._chest_w, int(self._chest_w * chest_img.get_height() / chest_img.get_width())))
        
        # Cargar y reproducir música de intro
        intro_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "assets", "Sonidos", "intro.mp3")
        pygame.mixer.music.load(intro_path)
        pygame.mixer.music.play(-1)  # -1 para loop infinito

    def update(self, dt):
        super().update(dt)
        self._time += dt
        self._start.update(dt)
        self._exit.update(dt)

    def draw(self, surface):
        self.draw_background(surface)
        self._ambient.draw(surface, self._time)
        cx = WIDTH // 2
        draw_soft_circle(surface, cx - 330, 150 + math.sin(self._time * 0.7) * 12, 240, GOLD, 24)
        draw_soft_circle(surface, cx + 330, 610 + math.cos(self._time * 0.6) * 10, 280, ROSE, 20)

        card = pygame.Rect(290, 140, 700, 470)
        draw_panel(surface, card, radius=36, top=PANEL, bottom=PANEL_ALT)

        em_y = 180 + math.sin(self._time * 2.2) * 4
        draw_soft_circle(surface, cx - 3, em_y + 5, 48, SHADOW, 42)
        surface.blit(self._chest, self._chest.get_rect(center=(cx, em_y)))

        draw_text(surface, "El Baúl del Saber", 52, INK, (cx, 272), True, bold=True)
        pygame.draw.rect(surface, GOLD, (cx - 210, 306, 420, 6), border_radius=3)
        draw_text(surface, "Un momento tranquilo para recordar, conversar y sonreír.",
                  26, MUTED, (cx, 350), True)
        pygame.draw.line(surface, FAINT, (cx - 280, 398), (cx + 280, 398), 2)

        tw = text_size("Recuerda · Conversa · Sonríe", 26, True)[0]
        draw_panel(surface, (cx - tw // 2 - 30, 424, tw + 60, 52), radius=26, fill=WHITE,
                   shadow=False, border=FAINT, border_width=2)
        draw_text(surface, "Recuerda · Conversa · Sonríe", 26, INK, (cx, 450), True, bold=True)
        draw_text(surface, "No hay prisa. Cada recuerdo es valioso.", 22, MUTED, (cx, 492), True)

        pulse = (math.sin(self._time * 2.4) + 1) / 2
        by_start = 556 + math.sin(self._time * 2.4) * 3
        draw_soft_circle(surface, cx - 160, by_start, 100 + pulse * 14, PRIMARY, int(34 + pulse * 22))
        self._start.draw(surface)
        
        by_exit = 556 + math.sin(self._time * 2.4 + 1) * 3
        draw_soft_circle(surface, cx + 160, by_exit, 100 + pulse * 14, (220, 80, 80), int(34 + pulse * 22))
        self._exit.draw(surface)

        self.finish(surface)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._app.stop()
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._app.stop()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Detectar click en el botón Comenzar para detener la música intro
            if self._start.rect.collidepoint(event.pos):
                pygame.mixer.music.stop()
        self._start.handle_event(event)
        self._exit.handle_event(event)


class GameScreen(Screen):
    def __init__(self, app):
        super().__init__(app, BG_TOP, BG_BOTTOM)
        self._message = ""
        self._message_timer = 0.0
        self._popup = None
        self._used_hints = set()
        self._time = 0.0

        # Cargar sonidos
        acertado_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "assets", "Sonidos", "acertado.mp3")
        self._sound_acertado = pygame.mixer.Sound(acertado_path)
        
        self._input = TextInput((200, 392, 880, 76), "Escribe la continuación que recuerdes…",
                                self._submit, label="Tu respuesta")
        self._check = Button((900, 520, 230, 70), "Comprobar", SUCCESS, self._submit_input,
                             radius=24, size=28)
        self._hint1 = Button((150, 520, 210, 70), "Pista 1", SECONDARY,
                             lambda: self._show_hint(1), radius=24, size=24)
        self._hint2 = Button((390, 520, 210, 70), "Pista 2", SECONDARY,
                             lambda: self._show_hint(2), radius=24, size=24)
        self._reveal = Button((630, 520, 210, 70), "Ver respuesta", ACCENT,
                              self._reveal_answer, radius=24, size=24)
        self._home = Button((36, 26, 140, 48), "← Inicio", (227, 205, 170),
                            app.go_home, radius=24, size=22, text_color=INK)
        self._terminar = Button((36, 520, 108, 70), "Terminar", (227, 205, 170),
                                app.show_album, radius=24, size=21, text_color=INK)
        self._bar = ProgressBar((40, 104, WIDTH - 80, 10))

    def update(self, dt):
        super().update(dt)
        self._time += dt
        if self._popup:
            self._popup.update(dt)
        self._input.update(dt)
        self._home.update(dt)
        self._terminar.update(dt)
        self._check.update(dt)
        self._hint1.update(dt)
        self._hint2.update(dt)
        self._reveal.update(dt)
        self._bar.update(dt)
        if self._message_timer > 0:
            self._message_timer = max(0.0, self._message_timer - dt)

    def _submit_input(self):
        self._submit(self._input.value)

    def _submit(self, answer):
        cx, cy = self._check.rect.center
        if self._app.current.es_respuesta_correcta(answer):
            self._app.register_hit()
            self._sound_acertado.play()
            self._app.celebrate(cx, cy, kind="hit")
            self._app.flash(GOLD, 90)
            self._app.show_reflection("¡Qué bonito recordarlo! Sigamos cuando quieras.")
        else:
            self._app.register_miss()
            self._message = "Aún no es la respuesta esperada. Inténtalo de nuevo o usa una pista."
            self._message_timer = 3.2
            self._app.shake(3, 0.24)
            self._app.fx.burst(cx, cy, [ROSE, FAINT], n=8, speed=150)

    def _show_hint(self, number):
        self._used_hints.add(number)
        r = self._app.current
        content = (f"La respuesta comienza con: {r.letra_inicial}"
                   if number == 1 else f"Pista: {r.significado}")
        self._popup = Popup(f"Pista {number}", content, lambda: setattr(self, "_popup", None))

    def _reveal_answer(self):
        self._app.show_reflection("La respuesta está aquí para acompañarte.")

    def _draw_hud(self, surface):
        band = pygame.Surface((WIDTH, 96), pygame.SRCALPHA)
        band.fill((*PANEL, 210))
        surface.blit(band, (0, 0))
        pygame.draw.line(surface, FAINT, (0, 95), (WIDTH, 95), 2)

        prog_txt = f"Refrán {self._app.position + 1} de {self._app.total}"
        pw = text_size(prog_txt, 22, True)[0]
        self._home.draw(surface)
        Pill((184, 26, pw + 54, 48), prog_txt,
             fill=PANEL, color=INK, size=22, bold=True, icon="◆", border=FAINT).draw(surface)

        tema = self._app.current.tema
        tw = text_size(tema, 24, True)[0]
        draw_panel(surface, (640 - tw // 2 - 30, 26, tw + 60, 48), radius=24, fill=SECONDARY,
                   shadow=False, border=lerp_color(SECONDARY, WHITE, 0.35), border_width=2)
        draw_text(surface, tema, 24, WHITE, (640, 50), True, bold=True)

        score_txt = f"Puntos {self._app.score}"
        if self._app.streak:
            score_txt += f"  ·  Racha {self._app.streak}"
        draw_panel(surface, (1012, 26, 232, 48), radius=24, fill=PANEL,
                   shadow=False, border=FAINT, border_width=2)
        draw_star(surface, (1036, 50), 12, 5, GOLD)
        draw_text(surface, score_txt, 21, INK, (1150, 50), True)

        self._bar.set(self._app.position / self._app.total if self._app.total else 0)
        self._bar.draw(surface)

    def draw(self, surface):
        self.draw_background(surface)
        self._draw_hud(surface)

        card = pygame.Rect(140, 140, 1000, 200)
        draw_panel(surface, card, radius=28, top=WHITE, bottom=PANEL_ALT)

        cw = text_size("Completa el refrán", 22, True)[0]
        draw_panel(surface, (640 - cw // 2 - 22, 152, cw + 44, 40), radius=20,
                   fill=lerp_color(GOLD, WHITE, 0.82), shadow=False, border=GOLD, border_width=2)
        draw_text(surface, "Completa el refrán", 22, lerp_color(GOLD, (60, 40, 10), 0.55),
                  (640, 172), True, bold=True)

        inicio = self._app.current.inicio
        size = 46 if len(inicio) <= 24 else 38
        draw_text(surface, inicio, size, INK, (640, 262), True, bold=True)

        self._input.draw(surface)
        self._terminar.draw(surface)
        self._hint1.draw(surface)
        self._hint2.draw(surface)
        if self._used_hints == {1, 2}:
            self._reveal.draw(surface)
        self._check.draw(surface)

        if self._message and self._message_timer > 0:
            alpha = min(255, int(self._message_timer * 170))
            draw_text(surface, self._message, 24, ROSE, (640, 622), True, alpha=alpha)

        if self._popup:
            self._popup.draw(surface)

        self.finish(surface)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._app.stop()
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._app.stop()
            return
        if self._popup:
            self._popup.handle_event(event)
            return
        for widget in (self._input, self._home, self._terminar, self._hint1, self._hint2, self._reveal, self._check):
            widget.handle_event(event)


class ReflectionScreen(Screen):
    def __init__(self, app, message):
        super().__init__(app, BG_TOP, BG_BOTTOM)
        self._message = message
        self._last = app.position >= app.total - 1
        label = "Ver mis recuerdos" if self._last else "Siguiente refrán"
        action = app.show_album if self._last else app.next_refran
        self._next = Button((460, 566, 360, 74), label, SUCCESS, action,
                            radius=26, size=28, icon="→")
        
        # Cargar sonido de victoria
        victory_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "assets", "Sonidos", "victory.mp3")
        self._sound_victory = pygame.mixer.Sound(victory_path)
        self._victory_played = False  # Bandera para controlar reproducción única

    def on_enter(self):
        """Se llama cuando la pantalla se vuelve activa"""
        # Reproducir solo si no se ha reproducido aún en esta visita
        if self._sound_victory and not self._victory_played:
            self._victory_played = True
            self._sound_victory.play()

    def on_leave(self):
        """Se llama cuando la pantalla deja de ser activa"""
        # Detener el sonido al salir
        if self._sound_victory:
            self._sound_victory.stop()
        # Resetear la bandera para permitir reproducción en una futura visita legítima
        self._victory_played = False

    def update(self, dt):
        super().update(dt)
        self._next.update(dt)

    def draw(self, surface):
        self.draw_background(surface)
        cx = WIDTH // 2
        draw_soft_circle(surface, cx, 150, 250, GOLD, 24)
        draw_soft_circle(surface, 160, 620, 220, ROSE, 18)

        draw_text(surface, "Un recuerdo para compartir", 40, INK, (cx, 92), True, bold=True)
        tw = text_size("Un recuerdo para compartir", 40, True)[0]
        pygame.draw.rect(surface, GOLD, (cx - tw // 2 - 60, 116, tw + 120, 5), border_radius=3)

        r = self._app.current

        card = pygame.Rect(140, 148, 1000, 150)
        draw_panel(surface, card, radius=28, top=WHITE, bottom=PANEL_ALT)

        w_i = text_size(r.inicio, 34, True)[0]
        w_r = text_size(r.respuesta, 34, True)[0]
        total = w_i + 18 + w_r
        if total <= 820:
            # Una sola línea: inicio y píldora comparten el mismo centro vertical.
            line_center = 192
            x = cx - total // 2
            draw_text(surface, r.inicio, 34, INK, (x + w_i // 2, line_center), True, bold=True)
            px = x + w_i + 8
            pygame.draw.rect(surface, GOLD, (px, line_center - 24, w_r + 22, 48), border_radius=24)
            draw_text(surface, r.respuesta, 32, WHITE, (px + 11 + w_r // 2, line_center), True, bold=True)
        else:
            draw_text(surface, r.inicio, 34, INK, (cx, 182), True, bold=True)
            w2 = text_size(r.respuesta, 30, True)[0]
            pygame.draw.rect(surface, GOLD, (cx - w2 // 2 - 18, 216, w2 + 36, 46), border_radius=23)
            draw_text(surface, r.respuesta, 28, WHITE, (cx, 238), True, bold=True)

        draw_text(surface, self._message, 26, SUCCESS, (cx, 332), True, bold=True)

        font = get_font(26)
        for i, q in enumerate(r.preguntas):
            panel_x = 140 + i * 520
            draw_panel(surface, (panel_x, 360, 480, 168), radius=24, fill=PANEL)
            draw_panel(surface, (panel_x + 18, 378, 150, 36), radius=18,
                       fill=lerp_color(SECONDARY, WHITE, 0.78), shadow=False,
                       border=SECONDARY, border_width=2)
            draw_text(surface, "Para conversar", 18, INK, (panel_x + 93, 396), True, bold=True)
            lines = wrap(q, font, 436)
            yy = 428
            for line in lines[:3]:
                draw_text(surface, line, 26, INK, (panel_x + 240, yy), True)
                yy += 36

        draw_text(surface, "Puedes conversar sobre ello o simplemente disfrutar del recuerdo.",
                  22, MUTED, (cx, 544), True)
        self._next.draw(surface)
        self.finish(surface)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._app.stop()
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._app.stop()
            return
        # Detener el sonido de victoria cuando se hace click en "Siguiente refrán" o "Ver mis recuerdos"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._next.rect.collidepoint(event.pos):
                if self._sound_victory:
                    self._sound_victory.stop()
        self._next.handle_event(event)


class AlbumScreen(Screen):
    def __init__(self, app):
        super().__init__(app, PANEL_ALT, BG_TOP)
        self._close = Button((944, 620, 300, 64), "Cerrar juego", SECONDARY, app.stop,
                             radius=24, size=28)
        self._menu = Button((36, 620, 300, 64), "Volver al menú", SUCCESS, app.go_home,
                            radius=24, size=24)
        self._ambient = Ambient(14, colors=[GOLD, ROSE])
        self._time = 0.0
        self._row = 0
        self._up = Button((1188, 220, 50, 50), "▲", (227, 205, 170),
                          self._scroll_up, radius=18, size=20, text_color=INK)
        self._down = Button((1188, 310, 50, 50), "▼", (227, 205, 170),
                            self._scroll_down, radius=18, size=20, text_color=INK)

    def _total_rows(self):
        return (len(self._app.album) + 1) // 2

    def _scroll_up(self):
        self._row -= 1

    def _scroll_down(self):
        self._row += 1

    def update(self, dt):
        super().update(dt)
        self._time += dt
        self._close.update(dt)
        self._menu.update(dt)
        self._up.update(dt)
        self._down.update(dt)
        self._row = max(0, min(max(0, self._total_rows() - 3), self._row))

    def draw(self, surface):
        self.draw_background(surface)
        self._ambient.draw(surface, self._time)
        cx = WIDTH // 2

        draw_text(surface, "Álbum de Recuerdos", 46, INK, (cx, 74), True, bold=True)
        tw = text_size("Álbum de Recuerdos", 46, True)[0]
        pygame.draw.rect(surface, GOLD, (cx - tw // 2 - 70, 100, tw + 140, 5), border_radius=3)
        draw_text(surface, "Gracias por compartir este momento. Puedes releerlo cuando quieras.",
                  24, MUTED, (cx, 130), True)

        cards = list(self._app.album)
        if not cards:
            draw_panel(surface, (340, 240, 600, 200), radius=26, fill=PANEL)
            draw_text(surface, "Todavía no hay recuerdos aquí.", 28, INK, (cx, 320), True, bold=True)
            draw_text(surface, "Completa o revela un refrán para guardar tu álbum.", 22, MUTED, (cx, 360), True)

        total_rows = self._total_rows()
        for local_row in range(3):
            real_row = self._row + local_row
            if real_row >= total_rows:
                break
            for col in range(2):
                idx = real_row * 2 + col
                if idx >= len(cards):
                    break
                refran = cards[idx]
                x = 110 + col * 540
                y = 168 + local_row * 134
                draw_panel(surface, (x, y, 510, 122), radius=22, fill=PANEL)

                tema = refran.tema
                tw_t = text_size(tema, 17, True)[0]
                draw_panel(surface, (x + 16, y + 12, tw_t + 26, 30), radius=15,
                           fill=lerp_color(SECONDARY, WHITE, 0.8), shadow=False)
                draw_text(surface, tema, 17, INK, (x + 16 + (tw_t + 26) // 2, y + 27), True, bold=True)

                font = get_font(22, True)
                inicio_lines = wrap(refran.inicio, font, 470)
                iy = y + 56
                for line in inicio_lines[:2]:
                    draw_text(surface, line, 22, INK, (x + 22, iy), bold=True)
                    iy += 26
                draw_text(surface, refran.respuesta, 20, lerp_color(GOLD, (60, 40, 10), 0.5),
                          (x + 26, y + 94), bold=True)

        if total_rows > 3:
            draw_text(surface, f"Fila {self._row + 1}–{min(self._row + 3, total_rows)} de {total_rows} · "
                               "desliza con la rueda del ratón", 20, MUTED, (cx, 592), True)
            self._up.draw(surface)
            self._down.draw(surface)

        self._menu.draw(surface)
        self._close.draw(surface)
        self.finish(surface)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._app.stop()
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._app.stop()
            return
        self._close.handle_event(event)
        self._menu.handle_event(event)
        self._up.handle_event(event)
        self._down.handle_event(event)
        if event.type == pygame.MOUSEWHEEL:
            self._row -= event.y