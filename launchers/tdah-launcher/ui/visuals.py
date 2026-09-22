import math
import random

import pygame

from core.settings import Settings


COLORS = {
    "top": (255, 246, 219),
    "bottom": (196, 233, 249),
    "title": [(255, 111, 129), (255, 165, 89), (255, 209, 102),
              (120, 200, 150), (86, 190, 200), (158, 140, 214)],
    "text": (66, 60, 90),
    "muted": (94, 84, 120),
    "green": (86, 199, 165),
    "green_hover": (108, 214, 181),
    "green_shadow": (52, 148, 122),
    "logo": (108, 92, 160),
}


def get_font(size):
    try:
        return pygame.font.Font(Settings.FONT_PATH, size)
    except (FileNotFoundError, pygame.error):
        return pygame.font.Font(None, size)


def make_background():
    surface = pygame.Surface((Settings.S_WIDTH, Settings.S_HEIGHT))
    for y in range(Settings.S_HEIGHT):
        ratio = y / max(Settings.S_HEIGHT - 1, 1)
        color = tuple(int(COLORS["top"][i] + (COLORS["bottom"][i] - COLORS["top"][i]) * ratio) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (Settings.S_WIDTH, y))
    return surface


def draw_animated_text(surface, text, font, center, time, palette=None, amplitude=6):
    palette = palette or COLORS["title"]
    widths = [font.size(character)[0] for character in text]
    total_width = sum(widths) + 3 * max(0, len(text) - 1)
    x = center[0] - total_width / 2
    for index, character in enumerate(text):
        rendered = font.render(character, True, palette[index % len(palette)])
        y = center[1] - rendered.get_height() / 2 + math.sin(time * 2.2 + index * 0.5) * amplitude
        if character != " ":
            shadow = font.render(character, True, (0, 0, 0))
            shadow.set_alpha(28)
            surface.blit(shadow, (x + 3, y + 5))
        surface.blit(rendered, (x, y))
        x += widths[index] + 3


class FloatingDecoration:
    def __init__(self):
        self.reset(True)

    def reset(self, random_y=False):
        self.x = random.uniform(20, Settings.S_WIDTH - 20)
        self.y = random.uniform(0, Settings.S_HEIGHT) if random_y else Settings.S_HEIGHT + 40
        self.radius = random.uniform(9, 26)
        self.speed = random.uniform(10, 24)
        self.phase = random.uniform(0, math.tau)
        self.color = random.choice(((255, 179, 186, 150), (255, 223, 154, 150),
                                    (186, 230, 209, 150), (162, 216, 224, 150)))
        self.star = random.choice((False, False, True))

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < -40:
            self.reset()

    def draw(self, surface, time):
        x = self.x + math.sin(time * 0.5 + self.phase) * 18
        size = int(self.radius * 2 + 4)
        layer = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size / 2, size / 2)
        if self.star:
            points = []
            for index in range(10):
                angle = math.pi / 5 * index - math.pi / 2
                radius = self.radius if index % 2 == 0 else self.radius * 0.45
                points.append((center[0] + math.cos(angle) * radius, center[1] + math.sin(angle) * radius))
            pygame.draw.polygon(layer, self.color, points)
        else:
            pygame.draw.circle(layer, self.color, center, self.radius)
        surface.blit(layer, (x - size / 2, self.y - size / 2))


def draw_logo(surface):
    font = get_font(24)
    text = font.render("enfócate", True, COLORS["logo"])
    x = Settings.S_WIDTH - text.get_width() - 34
    surface.blit(text, (x, 20))
    pygame.draw.circle(surface, (255, 209, 102), (x - 14, 32), 6)