"""
Módulo de interfaz de usuario interactiva: Dado y Botones.
"""
import random
from typing import Dict, List, Tuple
import pygame

from constants import COLOR_ACCENT, COLOR_TEXT_MUTED
from assets import AssetManager


class Dice:
    """Dado interactivo con animación visual de tirada."""
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.value: int = 1
        self.is_rolling: bool = False
        self.roll_timer: int = 0
        self.roll_duration: int = 22

    def roll(self) -> int:
        self.is_rolling = True
        self.roll_timer = self.roll_duration
        self.value = random.randint(1, 6)
        return self.value

    def update(self):
        if self.is_rolling:
            self.roll_timer -= 1
            if self.roll_timer % 3 == 0:
                self.value = random.randint(1, 6)
            if self.roll_timer <= 0:
                self.is_rolling = False

    def draw(self, surface: pygame.Surface, is_hovered: bool = False):
        x, y, w, h = self.rect

        # Sombra
        pygame.draw.rect(surface, (12, 16, 26), (x + 4, y + 6, w, h), border_radius=16)

        # Cuerpo del dado
        bg_col = (255, 255, 255) if not is_hovered else (245, 250, 255)
        border_col = (210, 220, 240) if not is_hovered else COLOR_ACCENT
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=16)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=16)

        # Puntos del dado
        dot_color = (36, 46, 68)
        rad = 7
        cx, cy = x + w // 2, y + h // 2
        l, r = x + w // 4 + 2, x + 3 * w // 4 - 2
        t, b = y + h // 4 + 2, y + 3 * h // 4 - 2

        pip_map: Dict[int, List[Tuple[int, int]]] = {
            1: [(cx, cy)],
            2: [(l, t), (r, b)],
            3: [(l, t), (cx, cy), (r, b)],
            4: [(l, t), (r, t), (l, b), (r, b)],
            5: [(l, t), (r, t), (cx, cy), (l, b), (r, b)],
            6: [(l, t), (r, t), (l, cy), (r, cy), (l, b), (r, b)]
        }

        for px, py in pip_map.get(self.value, [(cx, cy)]):
            pygame.draw.circle(surface, dot_color, (px, py), rad)


class Button:
    """Botón amigable con bordes redondeados y respuesta a eventos."""
    def __init__(self, rect: pygame.Rect, text: str, color_bg: Tuple[int, int, int],
                 color_hover: Tuple[int, int, int], font_key: str = "bold"):
        self.rect = rect
        self.text = text
        self.color_bg = color_bg
        self.color_hover = color_hover
        self.font_key = font_key
        self.is_hovered: bool = False
        self.enabled: bool = True

    def update(self, mouse_pos: Tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager):
        color = self.color_hover if (self.is_hovered and self.enabled) else self.color_bg
        if not self.enabled:
            color = (50, 60, 80)

        pygame.draw.rect(surface, (10, 14, 24), (self.rect.x + 2, self.rect.y + 3, self.rect.w, self.rect.h), border_radius=10)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        font = asset_mgr.get_font(self.font_key)
        txt_color = (255, 255, 255) if self.enabled else COLOR_TEXT_MUTED
        text_surf = font.render(self.text, True, txt_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return bool(self.enabled and event.type == pygame.MOUSEBUTTONDOWN and
                    event.button == 1 and self.rect.collidepoint(event.pos))
