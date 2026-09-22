"""
Módulo de la Pantalla de Inicio (StartScreen), Lluvia de Serpientes y Modales.
"""
import math
import random
from typing import List, Tuple, Optional
import pygame

from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_BG, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_CARD_BG, COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED,
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_GOLD,
    COLOR_SNAKE, COLOR_SNAKE_HEAD, COLOR_SNAKE_BELLY,
    COLOR_LADDER_RAIL, COLOR_LADDER_RUNG
)
from assets import AssetManager, AudioManager
from ui import Button


class FallingSnake:
    """
    Serpiente animada que cae suavemente como lluvia en el fondo,
    con movimiento ondulante idéntico al estilo del juego principal.
    """
    def __init__(self, x: float, y: float, speed: float, length: float, scale: float = 1.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.length = length
        self.scale = scale
        self.wave_phase = random.uniform(0, math.pi * 2)
        self.wave_speed = random.uniform(0.04, 0.08)
        self.wave_amp = random.uniform(14.0, 22.0) * scale

    def reset_to_top(self):
        self.x = random.uniform(30, WINDOW_WIDTH - 30)
        self.y = -random.uniform(80, 250)
        self.speed = random.uniform(1.2, 2.8)
        self.length = random.uniform(90, 160)

    def update(self):
        self.y += self.speed
        self.wave_phase += self.wave_speed
        if self.y - self.length > WINDOW_HEIGHT:
            self.reset_to_top()

    def draw(self, surface: pygame.Surface):
        segments = 18
        points: List[Tuple[float, float]] = []

        for i in range(segments + 1):
            t = i / segments
            base_y = self.y - self.length * t
            # Ondulación senoidal a lo largo del cuerpo
            envelope = math.sin(t * math.pi)
            offset_x = math.sin(self.wave_phase + t * math.pi * 2.8) * self.wave_amp * envelope
            points.append((self.x + offset_x, base_y))

        if len(points) < 2:
            return

        # Sombra sutil
        shadow_pts = [(p[0] + 2, p[1] + 3) for p in points]
        pygame.draw.lines(surface, (10, 14, 22, 60), False, shadow_pts, max(4, int(9 * self.scale)))

        # Cuerpo principal de la serpiente
        body_width = max(3, int(8 * self.scale))
        pygame.draw.lines(surface, COLOR_SNAKE, False, points, body_width)

        # Línea central de vientre
        belly_width = max(1, int(3 * self.scale))
        pygame.draw.lines(surface, COLOR_SNAKE_BELLY, False, points, belly_width)

        # Cabeza (en la parte inferior ya que va cayendo)
        head_x, head_y = points[0]
        head_radius = max(5, int(9 * self.scale))
        pygame.draw.circle(surface, COLOR_SNAKE_HEAD, (int(head_x), int(head_y)), head_radius)
        pygame.draw.circle(surface, (255, 230, 230), (int(head_x), int(head_y)), max(2, int(4 * self.scale)))

        # Ojos
        eye_rad = max(1, int(2 * self.scale))
        pygame.draw.circle(surface, (255, 255, 255), (int(head_x - 3), int(head_y + 1)), eye_rad + 1)
        pygame.draw.circle(surface, (255, 255, 255), (int(head_x + 3), int(head_y + 1)), eye_rad + 1)
        pygame.draw.circle(surface, (20, 20, 30), (int(head_x - 3), int(head_y + 1)), eye_rad)
        pygame.draw.circle(surface, (20, 20, 30), (int(head_x + 3), int(head_y + 1)), eye_rad)


class FallingSnakeManager:
    """Administra la lluvia de serpientes en el fondo de la pantalla de inicio."""
    def __init__(self, count: int = 14):
        self.snakes: List[FallingSnake] = []
        for _ in range(count):
            x = random.uniform(20, WINDOW_WIDTH - 20)
            y = random.uniform(-100, WINDOW_HEIGHT + 100)
            speed = random.uniform(1.2, 2.6)
            length = random.uniform(90, 160)
            scale = random.uniform(0.7, 1.1)
            self.snakes.append(FallingSnake(x, y, speed, length, scale))

    def update(self):
        for s in self.snakes:
            s.update()

    def draw(self, surface: pygame.Surface):
        for s in self.snakes:
            s.draw(surface)


class FallingLadder:
    """
    Escalera animada que cae suavemente en el fondo de la pantalla de inicio,
    con inclinación sutil, rieles dorados y peldaños detallados.
    """
    def __init__(self, x: float, y: float, speed: float, length: float, scale: float = 1.0, angle: float = 0.0):
        self.x = x
        self.y = y
        self.speed = speed
        self.length = length
        self.scale = scale
        self.angle = angle
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sway_speed = random.uniform(0.02, 0.04)

    def reset_to_top(self):
        self.x = random.uniform(40, WINDOW_WIDTH - 40)
        self.y = -random.uniform(100, 260)
        self.speed = random.uniform(1.0, 2.3)
        self.length = random.uniform(110, 180)
        self.scale = random.uniform(0.7, 1.05)
        self.angle = random.uniform(-0.15, 0.15)

    def update(self):
        self.y += self.speed
        self.sway_phase += self.sway_speed
        if self.y - self.length > WINDOW_HEIGHT:
            self.reset_to_top()

    def draw(self, surface: pygame.Surface):
        curr_angle = self.angle + math.sin(self.sway_phase) * 0.04
        dx = math.sin(curr_angle) * self.length
        dy = math.cos(curr_angle) * self.length

        top_x, top_y = self.x, self.y - self.length
        bot_x, bot_y = self.x + dx, self.y

        rail_spacing = 11.0 * self.scale
        seg_len = math.hypot(dx, dy)
        if seg_len == 0:
            return
        perp_x = (-dy / seg_len) * rail_spacing
        perp_y = (dx / seg_len) * rail_spacing

        r1_top = (top_x + perp_x, top_y + perp_y)
        r1_bot = (bot_x + perp_x, bot_y + perp_y)
        r2_top = (top_x - perp_x, top_y - perp_y)
        r2_bot = (bot_x - perp_x, bot_y - perp_y)

        # Sombra sutil
        shadow_offset = (3, 4)
        s1_top = (r1_top[0] + shadow_offset[0], r1_top[1] + shadow_offset[1])
        s1_bot = (r1_bot[0] + shadow_offset[0], r1_bot[1] + shadow_offset[1])
        s2_top = (r2_top[0] + shadow_offset[0], r2_top[1] + shadow_offset[1])
        s2_bot = (r2_bot[0] + shadow_offset[0], r2_bot[1] + shadow_offset[1])
        pygame.draw.line(surface, (10, 14, 22, 60), s1_top, s1_bot, max(2, int(5 * self.scale)))
        pygame.draw.line(surface, (10, 14, 22, 60), s2_top, s2_bot, max(2, int(5 * self.scale)))

        # Rieles principales
        rail_width = max(2, int(4 * self.scale))
        pygame.draw.line(surface, COLOR_LADDER_RAIL, r1_top, r1_bot, rail_width)
        pygame.draw.line(surface, COLOR_LADDER_RAIL, r2_top, r2_bot, rail_width)
        pygame.draw.line(surface, (255, 235, 170), r1_top, r1_bot, 1)
        pygame.draw.line(surface, (255, 235, 170), r2_top, r2_bot, 1)

        # Peldaños
        rung_spacing = 22.0 * self.scale
        num_rungs = max(3, int(seg_len // rung_spacing))
        for i in range(1, num_rungs):
            t = i / num_rungs
            rx = top_x + dx * t
            ry = top_y + dy * t
            p1 = (rx + perp_x, ry + perp_y)
            p2 = (rx - perp_x, ry - perp_y)
            pygame.draw.line(surface, (10, 14, 22), (p1[0] + 1, p1[1] + 2), (p2[0] + 1, p2[1] + 2), max(2, int(3 * self.scale)))
            pygame.draw.line(surface, COLOR_LADDER_RUNG, p1, p2, max(2, int(3 * self.scale)))
            pygame.draw.line(surface, (255, 255, 210), (p1[0], p1[1] - 1), (p2[0], p2[1] - 1), 1)


class FallingLadderManager:
    """Administra la lluvia de escaleras en el fondo de la pantalla de inicio."""
    def __init__(self, count: int = 10):
        self.ladders: List[FallingLadder] = []
        for _ in range(count):
            x = random.uniform(30, WINDOW_WIDTH - 30)
            y = random.uniform(-150, WINDOW_HEIGHT + 100)
            speed = random.uniform(1.0, 2.2)
            length = random.uniform(110, 180)
            scale = random.uniform(0.7, 1.05)
            angle = random.uniform(-0.15, 0.15)
            self.ladders.append(FallingLadder(x, y, speed, length, scale, angle))

    def update(self):
        for ladder in self.ladders:
            ladder.update()

    def draw(self, surface: pygame.Surface):
        for ladder in self.ladders:
            ladder.draw(surface)


class ModalDialog:
    """Ventana modal emergente centrada con fondo oscurecido y botón de cierre."""
    def __init__(self, title: str, width: int = 680, height: int = 460):
        self.width = width
        self.height = height
        self.rect = pygame.Rect((WINDOW_WIDTH - width) // 2, (WINDOW_HEIGHT - height) // 2, width, height)
        self.title = title
        self.is_open = False

        btn_w, btn_h = 160, 42
        btn_x = self.rect.centerx - btn_w // 2
        btn_y = self.rect.bottom - btn_h - 22
        self.btn_close = Button(pygame.Rect(btn_x, btn_y, btn_w, btn_h), "CERRAR", (60, 70, 95), (80, 95, 125))

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Retorna True si el modal absorbió el evento o se cerró."""
        if not self.is_open:
            return False

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN):
            self.close()
            return True

        if self.btn_close.is_clicked(event):
            self.close()
            return True

        # Absorbe cualquier clic fuera para que no traspase a los botones de abajo
        if event.type == pygame.MOUSEBUTTONDOWN:
            return True

        return True

    def update(self, mouse_pos: Tuple[int, int]):
        if self.is_open:
            self.btn_close.update(mouse_pos)

    def draw_frame(self, surface: pygame.Surface, asset_mgr: AssetManager):
        if not self.is_open:
            return

        # Capa de oscurecimiento exterior (Overlay)
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 12, 20, 180))
        surface.blit(overlay, (0, 0))

        # Caja del modal
        pygame.draw.rect(surface, (12, 16, 26), (self.rect.x + 4, self.rect.y + 6, self.rect.w, self.rect.h), border_radius=16)
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, 2, border_radius=16)

        # Título del modal
        font_title = asset_mgr.get_font("subtitle")
        t_surf = font_title.render(self.title, True, COLOR_GOLD)
        surface.blit(t_surf, t_surf.get_rect(center=(self.rect.centerx, self.rect.y + 36)))

        # Línea divisoria
        pygame.draw.line(surface, COLOR_PANEL_BORDER,
                         (self.rect.x + 30, self.rect.y + 62),
                         (self.rect.right - 30, self.rect.y + 62), 1)

        # Botón de cerrar
        self.btn_close.draw(surface, asset_mgr)


class InfoModal(ModalDialog):
    """Modal para mostrar la información académica e institucional del proyecto."""
    def __init__(self):
        super().__init__("MAS INFORMACION", width=620, height=440)
        self.university = "Universidad De Oriente"
        self.subject = "Objetos y Abstraccion de Datos"
        self.heading = "Bachilleres:"
        self.students = [
            "Valiant Molero",
            "Lidia Perez",
            "Pedro Gallardo",
            "Luis Esparragoza"
        ]

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager):
        if not self.is_open:
            return
        self.draw_frame(surface, asset_mgr)

        font_title = asset_mgr.get_font("subtitle")
        font_bold = asset_mgr.get_font("bold")
        font_body = asset_mgr.get_font("body")

        # 1. Universidad De Oriente
        uni_surf = font_title.render(self.university, True, COLOR_GOLD)
        surface.blit(uni_surf, uni_surf.get_rect(center=(self.rect.centerx, self.rect.y + 90)))

        # 2. Objetos y Abstracción de Datos
        subj_surf = font_bold.render(self.subject, True, COLOR_ACCENT_HOVER)
        surface.blit(subj_surf, subj_surf.get_rect(center=(self.rect.centerx, self.rect.y + 126)))

        # Línea divisoria decorativa
        pygame.draw.line(surface, COLOR_PANEL_BORDER,
                         (self.rect.centerx - 180, self.rect.y + 154),
                         (self.rect.centerx + 180, self.rect.y + 154), 1)

        # 3. Encabezado Bachilleres:
        head_surf = font_bold.render(self.heading, True, COLOR_TEXT_LIGHT)
        surface.blit(head_surf, (self.rect.centerx - 140, self.rect.y + 174))

        # 4. Lista de Bachilleres
        y_offset = self.rect.y + 208
        for student in self.students:
            # Viñeta circular dorada
            pygame.draw.circle(surface, COLOR_GOLD, (self.rect.centerx - 132, y_offset + 9), 3)
            st_surf = font_body.render(student, True, COLOR_TEXT_LIGHT)
            surface.blit(st_surf, (self.rect.centerx - 116, y_offset))
            y_offset += 32


class ConfigModal(ModalDialog):
    """Modal de configuración de sonido, música y opciones de volumen."""
    def __init__(self, audio_mgr: AudioManager):
        super().__init__("CONFIGURACION", width=560, height=420)
        self.audio_mgr = audio_mgr

        btn_sound_w = 240
        btn_sound_x = self.rect.centerx - btn_sound_w // 2
        self.btn_toggle_sound = Button(
            pygame.Rect(btn_sound_x, self.rect.y + 115, btn_sound_w, 42),
            "SONIDO: ACTIVADO", COLOR_ACCENT, COLOR_ACCENT_HOVER, "bold"
        )

        # Controles de volumen de música interactivos
        slider_w = 200
        slider_h = 16
        slider_x = self.rect.centerx - slider_w // 2
        slider_y = self.rect.y + 232
        self.slider_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
        self.is_dragging_slider = False

        btn_step_size = 38
        self.btn_vol_down = Button(
            pygame.Rect(slider_x - btn_step_size - 14, slider_y - 11, btn_step_size, btn_step_size),
            "-", (40, 52, 78), (60, 75, 110), "subtitle"
        )
        self.btn_vol_up = Button(
            pygame.Rect(slider_x + slider_w + 14, slider_y - 11, btn_step_size, btn_step_size),
            "+", (40, 52, 78), (60, 75, 110), "subtitle"
        )

        # Botón de cierre "LISTO"
        btn_done_w = 160
        self.btn_done = Button(
            pygame.Rect(self.rect.centerx - btn_done_w // 2, self.rect.y + 345, btn_done_w, 42),
            "LISTO", (42, 54, 82), COLOR_ACCENT, "bold"
        )

    def update(self, mouse_pos: Tuple[int, int]):
        if self.is_open:
            super().update(mouse_pos)
            self.btn_toggle_sound.text = "SONIDO: SILENCIADO" if self.audio_mgr.is_muted else "SONIDO: ACTIVADO"
            self.btn_toggle_sound.color_bg = (140, 50, 60) if self.audio_mgr.is_muted else COLOR_ACCENT
            self.btn_toggle_sound.update(mouse_pos)
            self.btn_vol_down.update(mouse_pos)
            self.btn_vol_up.update(mouse_pos)
            self.btn_done.update(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.is_open:
            return False

        # 1. Interacción con la barra deslizadora de volumen (clic o arrastre)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            track_pad = pygame.Rect(self.slider_rect.x - 6, self.slider_rect.y - 10,
                                    self.slider_rect.w + 12, self.slider_rect.h + 20)
            if track_pad.collidepoint(event.pos):
                self.is_dragging_slider = True
                norm_pos = max(0.0, min(1.0, (event.pos[0] - self.slider_rect.x) / self.slider_rect.w))
                self.audio_mgr.set_music_volume(round(norm_pos, 2))
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_dragging_slider:
                self.is_dragging_slider = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging_slider:
                norm_pos = max(0.0, min(1.0, (event.pos[0] - self.slider_rect.x) / self.slider_rect.w))
                self.audio_mgr.set_music_volume(round(norm_pos, 2))
                return True

        # 2. Clics en botones interactivos
        if self.btn_toggle_sound.is_clicked(event):
            self.audio_mgr.toggle_mute()
            return True

        if self.btn_vol_down.is_clicked(event):
            self.audio_mgr.change_music_volume(-0.05)
            return True

        if self.btn_vol_up.is_clicked(event):
            self.audio_mgr.change_music_volume(0.05)
            return True

        if self.btn_done.is_clicked(event):
            self.close()
            return True

        return super().handle_event(event)

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager):
        if not self.is_open:
            return
        self.draw_frame(surface, asset_mgr)

        font_bold = asset_mgr.get_font("bold")
        font_body = asset_mgr.get_font("body")
        font_small = asset_mgr.get_font("small")

        # 1. Sección Silenciado
        lbl_sound = font_body.render("Estado de audio general:", True, COLOR_TEXT_LIGHT)
        surface.blit(lbl_sound, lbl_sound.get_rect(center=(self.rect.centerx, self.rect.y + 92)))
        self.btn_toggle_sound.draw(surface, asset_mgr)

        # Línea divisoria suave
        div_y = self.rect.y + 178
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (self.rect.x + 40, div_y), (self.rect.right - 40, div_y), 1)

        # 2. Sección Volumen de Música
        vol = self.audio_mgr.get_music_volume()
        pct = int(round(vol * 100))
        status_suffix = " (Silenciado)" if self.audio_mgr.is_muted else ""
        lbl_vol = font_bold.render(
            f"Volumen de la musica: {pct}%{status_suffix}",
            True,
            (220, 130, 130) if self.audio_mgr.is_muted else COLOR_TEXT_LIGHT
        )
        surface.blit(lbl_vol, lbl_vol.get_rect(center=(self.rect.centerx, self.rect.y + 202)))

        # Botones - y +
        self.btn_vol_down.draw(surface, asset_mgr)
        self.btn_vol_up.draw(surface, asset_mgr)

        # Barra deslizadora (Slider Track)
        pygame.draw.rect(surface, (20, 26, 42), self.slider_rect, border_radius=8)
        pygame.draw.rect(surface, (45, 58, 88), self.slider_rect, 1, border_radius=8)

        # Relleno activo de volumen
        fill_width = int(self.slider_rect.w * vol)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.slider_rect.x, self.slider_rect.y, fill_width, self.slider_rect.h)
            fill_color = (130, 60, 70) if self.audio_mgr.is_muted else COLOR_ACCENT
            pygame.draw.rect(surface, fill_color, fill_rect, border_radius=8)

        # Perilla circular / Knob indicador
        knob_x = self.slider_rect.x + fill_width
        knob_y = self.slider_rect.centery
        knob_color = (160, 160, 170) if self.audio_mgr.is_muted else COLOR_GOLD
        pygame.draw.circle(surface, (15, 20, 30), (knob_x, knob_y), 10)
        pygame.draw.circle(surface, knob_color, (knob_x, knob_y), 8)
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, knob_y), 3)

        # Texto de ayuda
        hint_text = font_small.render("Arrastra o haz clic en la barra para regular el volumen", True, COLOR_TEXT_MUTED)
        surface.blit(hint_text, hint_text.get_rect(center=(self.rect.centerx, self.rect.y + 276)))

        # Botón Listo
        self.btn_done.draw(surface, asset_mgr)


class StartScreen:
    """
    Pantalla de inicio completa:
    - Fondo de lluvia de serpientes animados.
    - Título centrado en la parte superior.
    - Botones centrales: 'Iniciar juego' y 'Configuración'.
    - Botón inferior izquierdo: Silenciar sonidos.
    - Botón inferior derecho: Información (con ventana modal centrada).
    """
    def __init__(self, asset_mgr: AssetManager, audio_mgr: AudioManager):
        self.asset_mgr = asset_mgr
        self.audio_mgr = audio_mgr

        # Lluvia animada de fondo: serpientes y escaleras
        self.snake_rain = FallingSnakeManager(count=12)
        self.ladder_rain = FallingLadderManager(count=10)

        # Botones centrales
        btn_w, btn_h = 280, 54
        center_x = (WINDOW_WIDTH - btn_w) // 2

        self.btn_start = Button(
            pygame.Rect(center_x, 320, btn_w, btn_h),
            "INICIAR JUEGO", COLOR_ACCENT, COLOR_ACCENT_HOVER, "subtitle"
        )
        self.btn_config = Button(
            pygame.Rect(center_x, 395, btn_w, btn_h),
            "CONFIGURACION", (42, 54, 82), (58, 74, 110), "subtitle"
        )

        # Botón inferior izquierdo (Silenciar sonido)
        self.btn_mute = Button(
            pygame.Rect(40, WINDOW_HEIGHT - 64, 190, 44),
            "SONIDO: ON", (35, 45, 68), (50, 65, 95), "body"
        )

        # Botón inferior derecho (Más información)
        self.btn_info = Button(
            pygame.Rect(WINDOW_WIDTH - 230, WINDOW_HEIGHT - 64, 190, 44),
            "Mas informacion", (35, 45, 68), (50, 65, 95), "body"
        )

        # Ventanas emergentes (Modales)
        self.modal_info = InfoModal()
        self.modal_config = ConfigModal(self.audio_mgr)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Procesa eventos y retorna 'START_GAME' si se inicia la partida."""
        # 1. Si algún modal está abierto, absorbe o procesa el evento
        if self.modal_info.is_open:
            self.modal_info.handle_event(event)
            return None

        if self.modal_config.is_open:
            self.modal_config.handle_event(event)
            return None

        # 2. Eventos normales de la pantalla de inicio
        if self.btn_start.is_clicked(event):
            return "START_GAME"

        if self.btn_config.is_clicked(event):
            self.modal_config.open()
            return None

        if self.btn_mute.is_clicked(event):
            self.audio_mgr.toggle_mute()
            return None

        if self.btn_info.is_clicked(event):
            self.modal_info.open()
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return "START_GAME"
            elif event.key == pygame.K_m:
                self.audio_mgr.toggle_mute()
                return None

        return None

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        # Actualizar lluvia de fondo (serpientes y escaleras)
        self.snake_rain.update()
        self.ladder_rain.update()

        # Si hay un modal abierto, solo actualizar el modal
        if self.modal_info.is_open:
            self.modal_info.update(mouse_pos)
            return

        if self.modal_config.is_open:
            self.modal_config.update(mouse_pos)
            return

        # Actualizar botones
        self.btn_start.update(mouse_pos)
        self.btn_config.update(mouse_pos)

        # Texto dinámico del botón de silencio
        if self.audio_mgr.is_muted:
            self.btn_mute.text = "SONIDO: OFF (Mute)"
            self.btn_mute.color_bg = (110, 45, 55)
        else:
            self.btn_mute.text = "SONIDO: ON"
            self.btn_mute.color_bg = (35, 45, 68)

        self.btn_mute.update(mouse_pos)
        self.btn_info.update(mouse_pos)

    def draw(self, surface: pygame.Surface):
        # 1. Fondo base oscuro
        surface.fill(COLOR_BG)

        # 2. Lluvia animada de fondo (escaleras y serpientes)
        self.ladder_rain.draw(surface)
        self.snake_rain.draw(surface)

        # 3. Título centrado en la parte superior con fuente ampliada
        font_big = self.asset_mgr.get_font("big_title")

        # Sombra del título para dar relieve visual
        t_shadow = font_big.render("SERPIENTES Y ESCALERAS", True, (10, 14, 24))
        surface.blit(t_shadow, t_shadow.get_rect(center=(WINDOW_WIDTH // 2 + 4, 164)))

        # Texto del título con fuente de mayor tamaño
        t_surf = font_big.render("SERPIENTES Y ESCALERAS", True, COLOR_GOLD)
        surface.blit(t_surf, t_surf.get_rect(center=(WINDOW_WIDTH // 2, 160)))

        # 4. Botones centrales
        self.btn_start.draw(surface, self.asset_mgr)
        self.btn_config.draw(surface, self.asset_mgr)

        # 5. Botones de esquinas inferiores
        self.btn_mute.draw(surface, self.asset_mgr)
        self.btn_info.draw(surface, self.asset_mgr)

        # 6. Modales emergentes (si están abiertos)
        self.modal_info.draw(surface, self.asset_mgr)
        self.modal_config.draw(surface, self.asset_mgr)
