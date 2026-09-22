"""Componentes visuales reutilizables — tema moderno, cálido y animado.

ABSTRACCIÓN: Widget define el contrato común (draw / handle_event / update).
HERENCIA: Button, TextInput, Popup, Pill y ProgressBar heredan de Widget.
POLIMORFISMO: las pantallas los tratan mediante draw() y handle_event().

Incluye efectos de "juice": partículas, confeti, textos flotantes y destellos (FXLayer).
"""
from abc import ABC, abstractmethod
from typing import Callable
import math
import random
import pygame

from config import (WIDTH, HEIGHT, INK, MUTED, FAINT, PANEL, PANEL_ALT, WHITE,
                    SHADOW, PRIMARY, SECONDARY, SUCCESS, GOLD, FONT_STACK,
                    PRESS_ANIM, HOVER_ANIM, BURST_LIFE)

# ============================== utilidades ==============================

_font_cache: dict = {}
_mask_cache: dict = {}
_shadow_cache: dict = {}
_bg_cache: dict = {}
_family_choice = {"done": False, "value": None}


def _family() -> str | None:
    """Primera familia de FONT_STACK que existe en el sistema (o None)."""
    if not _family_choice["done"]:
        flat = {name.replace(" ", "").lower(): name for name in pygame.font.get_fonts()}
        for candidate in FONT_STACK:
            if candidate.replace(" ", "").lower() in flat:
                _family_choice["value"] = candidate
                break
        _family_choice["done"] = True
    return _family_choice["value"]


def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _font_cache:
        family = _family()
        path = pygame.font.match_font(family, bold=bold) if family else None
        _font_cache[key] = (pygame.font.Font(path, size) if path
                            else pygame.font.SysFont("arial", size, bold=bold))
    return _font_cache[key]


def text_size(text: str, size: int, bold: bool = False) -> tuple[int, int]:
    return get_font(size, bold).size(text)


def wrap(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if font.size(trial)[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def lerp_color(a, b, t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_text(surface, text, size, color, pos, centered=False, bold=None, alpha=255):
    if not text:
        return
    font = get_font(size, bold if bold is not None else size >= 48)
    rendered = font.render(text, True, color[:3])
    if alpha < 255:
        rendered.set_alpha(alpha)
    if centered:
        # Corrección óptica: las fuentes como Segoe UI tienden a verse altas,
        # bajamos 1-2 px el centro vertical para que el ojo quede equilibrado.
        rect = rendered.get_rect(center=(pos[0], pos[1] + 2))
    else:
        rect = rendered.get_rect(topleft=pos)
    surface.blit(rendered, rect)


def draw_gradient_rect(surface, rect, top, bottom, radius=0):
    r = pygame.Rect(rect)
    w, h = r.w, r.h
    if radius > 0:
        grad = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            t = y / max(1, h - 1)
            pygame.draw.line(grad, lerp_color(top, bottom, t), (0, y), (w, y))
        key = (w, h, radius)
        mask = _mask_cache.get(key)
        if mask is None:
            mask = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
            _mask_cache[key] = mask
        grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(grad, (r.x, r.y))
    else:
        for y in range(h):
            t = y / max(1, h - 1)
            pygame.draw.line(surface, lerp_color(top, bottom, t), (r.x, r.y + y), (r.x + r.w, r.y + y))


def draw_background(surface, top, bottom):
    key = (top, bottom)
    bg = _bg_cache.get(key)
    if bg is None:
        bg = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            t = y / max(1, HEIGHT - 1)
            pygame.draw.line(bg, lerp_color(top, bottom, t), (0, y), (WIDTH, y))
        _bg_cache[key] = bg
    surface.blit(bg, (0, 0))


def draw_soft_circle(surface, x, y, radius, color, alpha):
    radius = max(2, int(radius))
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for rr in range(radius, 0, -3):
        a = int(alpha * (1 - rr / radius))
        pygame.draw.circle(s, (*color[:3], a), (radius, radius), rr)
    surface.blit(s, (int(x - radius), int(y - radius)))


def draw_star(surface, center, outer, inner, color):
    """Estrella de 5 puntas como polígono: simétrica y perfectamente centrada."""
    cx, cy = int(center[0]), int(center[1])
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = outer if i % 2 == 0 else inner
        pts.append((cx + int(rad * math.cos(ang)), cy + int(rad * math.sin(ang))))
    pygame.draw.polygon(surface, color, pts)


def _shadow_surf(w: int, h: int, radius: int, alpha: int = 56, dy: int = 6) -> pygame.Surface:
    key = (w, h, radius, alpha)
    cached = _shadow_cache.get(key)
    if cached is not None:
        return cached
    surf = pygame.Surface((w + dy * 2, h + dy * 2), pygame.SRCALPHA)
    for spread, a in ((dy, alpha), (dy + 4, alpha // 2), (dy + 8, alpha // 4)):
        rect = pygame.Rect(spread, spread, w + (dy - spread) * 2, h + (dy - spread) * 2)
        pygame.draw.rect(surf, (*SHADOW, a), rect, border_radius=max(6, radius + dy - spread))
    _shadow_cache[key] = surf
    return surf


def _glow_surf(w: int, h: int, radius: int, color, alpha: int = 70) -> pygame.Surface:
    pad = 12
    surf = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    for i in range(4, -1, -1):
        a = max(6, alpha // (i + 1))
        rect = pygame.Rect(pad - i * 3, pad - i * 3, w + i * 6, h + i * 6)
        pygame.draw.rect(surf, (*color, a), rect, border_radius=max(8, radius + i * 3))
    return surf


def draw_panel(surface, rect, radius=22, fill=PANEL, top=None, bottom=None,
               shadow=True, border=None, border_width=0, shadow_alpha=56):
    r = pygame.Rect(rect)
    if shadow:
        surface.blit(_shadow_surf(r.w, r.h, radius, shadow_alpha), (r.x - 6, r.y - 6))
    if top and bottom:
        draw_gradient_rect(surface, r, top, bottom, radius)
    else:
        pygame.draw.rect(surface, fill, r, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, r, border_width, border_radius=radius)


# ============================== widgets base ==============================

class Widget(ABC):
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    def update(self, dt: float) -> None:  # opcional: micro-animaciones
        pass


class Button(Widget):
    """Botón con degradado, sombra, brillo al pasar el ratón y hundimiento al pulsar."""

    def __init__(self, rect, text: str, color=PRIMARY, action: Callable[[], None] = None,
                 radius: int = 24, size: int = 30, text_color=WHITE, icon=None, shadow=True):
        self._rect = pygame.Rect(rect)
        self._text, self._color = text, color
        self._action, self._radius = action, radius
        self._size, self._text_color = size, text_color
        self._icon, self._shadow_flag = icon, shadow
        self._hover = 0.0
        self._press = 0.0
        self._hovered = False

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    def update(self, dt: float) -> None:
        self._hovered = self._rect.collidepoint(pygame.mouse.get_pos())
        target = 1.0 if self._hovered else 0.0
        self._hover += (target - self._hover) * min(1.0, dt / HOVER_ANIM)
        self._press = max(0.0, self._press - dt / PRESS_ANIM)

    def draw(self, surface) -> None:
        color = self._color
        if self._hover > 0.02:
            color = lerp_color(self._color, WHITE, 0.18 * self._hover)
        r = self._rect.copy()
        if self._hover > 0.02:
            grow = int(4 * self._hover)
            r.inflate_ip(grow, grow)
        r.y += int(4 * min(1.0, self._press))
        radius = self._radius

        if self._shadow_flag:
            surface.blit(_shadow_surf(r.w, r.h, radius), (r.x - 6, r.y - 6))
        if self._hovered:
            surface.blit(_glow_surf(r.w, r.h, radius, color, alpha=64), (r.x - 12, r.y - 12))

        top = lerp_color(color, WHITE, 0.22)
        bottom = lerp_color(color, tuple(max(0, c - 34) for c in color), 0.35)
        draw_gradient_rect(surface, r, top, bottom, radius)
        pygame.draw.rect(surface, lerp_color(color, WHITE, 0.5), r.inflate(-8, -8), 2,
                         border_radius=max(6, radius - 4))

        if self._icon:
            cx = r.x + 42
            cy = r.centery
            pygame.draw.circle(surface, lerp_color(color, WHITE, 0.15), (cx, cy), 18)
            draw_text(surface, self._icon, 22, WHITE, (cx, cy), True, bold=True)
            text_pos = (r.centerx + 14, r.centery)
        else:
            text_pos = r.center
        draw_text(surface, self._text, self._size, self._text_color, text_pos, True, bold=True)

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self._rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self._rect.collidepoint(event.pos):
            self._press = 1.0
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self._rect.collidepoint(event.pos):
            if self._action:
                self._action()
            self._press = 0.0


class Pill(Widget):
    """Etiqueta de cápsula (no interactiva) para HUD y badges."""

    def __init__(self, rect, text: str, fill=PANEL, color=INK, size=22, bold=False,
                 icon=None, border=None):
        self._rect = pygame.Rect(rect)
        self._text, self._fill = text, fill
        self._color, self._size, self._bold = color, size, bold
        self._icon = icon
        self._border = border or lerp_color(fill, INK, 0.22)

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    def draw(self, surface) -> None:
        pygame.draw.rect(surface, self._fill, self._rect, border_radius=self._rect.h // 2)
        pygame.draw.rect(surface, self._border, self._rect, 2, border_radius=self._rect.h // 2)
        shift = 0
        if self._icon:
            cx = self._rect.x + 26
            cy = self._rect.centery
            pygame.draw.circle(surface, self._color, (cx, cy), 11)
            pygame.draw.circle(surface, lerp_color(self._color, WHITE, 0.25), (cx, cy), 8, 1)
            draw_text(surface, self._icon, 15, WHITE, (cx, cy), True, bold=True)
            shift = 22
        draw_text(surface, self._text, self._size, self._color,
                  (self._rect.centerx + shift, self._rect.centery), True, bold=self._bold)

    def handle_event(self, event) -> None:
        pass


class TextInput(Widget):
    """Campo de texto con etiqueta, brillo al enfocar, cursor parpadeante y envío por Enter."""

    def __init__(self, rect, placeholder: str, on_submit: Callable[[str], None],
                 label: str | None = None):
        self._rect = pygame.Rect(rect)
        self._placeholder, self._on_submit = placeholder, on_submit
        self._label = label
        self._value, self._active = "", False
        self._cursor = 0.0

    @property
    def value(self) -> str:
        return self._value

    def update(self, dt: float) -> None:
        self._cursor += dt

    def draw(self, surface) -> None:
        if self._label:
            draw_text(surface, self._label, 21, MUTED, (self._rect.x + 6, self._rect.y - 32), bold=True)
        if self._active:
            surface.blit(_glow_surf(self._rect.w, self._rect.h, 18, SECONDARY, alpha=46),
                         (self._rect.x - 12, self._rect.y - 12))
        draw_panel(surface, self._rect, radius=18, fill=PANEL, shadow=False,
                   border=SECONDARY if self._active else FAINT, border_width=3)

        text = self._value or self._placeholder
        font = get_font(24)
        max_w = self._rect.w - 40
        while font.size(text)[0] > max_w and len(text) > 1:
            text = text[1:]
        color = INK if self._value else MUTED
        text_h = font.get_height()
        ty = self._rect.y + (self._rect.h - text_h) // 2 - 2
        draw_text(surface, text, 24, color, (self._rect.x + 24, ty))

        if self._active and int(self._cursor * 2) % 2 == 0:
            caret_x = self._rect.x + 24 + font.size(text)[0]
            caret_y = self._rect.y + (self._rect.h - 26) // 2
            pygame.draw.rect(surface, SECONDARY, (caret_x, caret_y, 3, 26), border_radius=2)

    def handle_event(self, event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._active = self._rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self._active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._on_submit(self._value)
                self._value = ""
            elif event.key == pygame.K_BACKSPACE:
                self._value = self._value[:-1]
            elif event.key == pygame.K_ESCAPE:
                self._active = False
            elif event.unicode.isprintable() and len(self._value) < 62:
                self._value += event.unicode


class ProgressBar(Widget):
    """Barra de progreso animada: la varilla se desliza suavemente hacia su objetivo."""

    def __init__(self, rect, percent: float = 0.0, color=GOLD, track=(231, 205, 171)):
        self._rect = pygame.Rect(rect)
        self._color = color
        self._track = track
        self._current = 0.0
        self._target = max(0.0, min(1.0, percent))

    def set(self, percent: float) -> None:
        self._target = max(0.0, min(1.0, percent))

    def update(self, dt: float) -> None:
        self._current += (self._target - self._current) * min(1.0, dt / 0.35)

    def handle_event(self, event) -> None:
        pass

    def draw(self, surface) -> None:
        r = self._rect
        pygame.draw.rect(surface, self._track, r, border_radius=r.h // 2)
        w = int(r.w * self._current)
        if w > 4:
            draw_gradient_rect(surface, (r.x, r.y, w, r.h),
                               lerp_color(self._color, WHITE, 0.35), self._color, radius=r.h // 2)
            pygame.draw.rect(surface, (255, 255, 255), (r.x, r.y + 2, w, max(2, r.h // 3)),
                             border_radius=2)
            head = r.x + w
            pygame.draw.circle(surface, WHITE, (head, r.centery), r.h // 2 + 1)
            pygame.draw.circle(surface, self._color, (head, r.centery), r.h // 2 - 2)


class Popup(Widget):
    """Ventana modal con banda de color, contenido ajustado y botón de cierre."""

    def __init__(self, title: str, content: str, on_close: Callable[[], None],
                 button_text: str = "Entendido", color=SECONDARY):
        self._title, self._content = title, content
        self._age = 0.0
        self._close = Button((516, 436, 248, 58), button_text, color, on_close, radius=22, size=24)

    def update(self, dt: float) -> None:
        self._age += dt
        self._close.update(dt)

    def draw(self, surface) -> None:
        fade = min(1.0, self._age / 0.18)
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((*SHADOW, int(150 * fade)))
        surface.blit(shade, (0, 0))

        panel = pygame.Rect(210, 170, 860, 345)
        draw_panel(surface, panel, radius=30, top=PANEL, bottom=PANEL_ALT)

        band = pygame.Rect(210, 170, 860, 96)
        draw_gradient_rect(surface, band, lerp_color(self._close._color, WHITE, 0.28),
                           self._close._color, radius=30)
        pygame.draw.rect(surface, (255, 255, 255), (214, 260, 852, 4), border_radius=2)
        draw_text(surface, self._title, 34, WHITE, (640, 206), True, bold=True)

        font = get_font(26)
        lines = wrap(self._content, font, 780)
        y = 312
        for line in lines[:4]:
            draw_text(surface, line, 26, INK, (640, y), True)
            y += 40
        self._close.draw(surface)

    def handle_event(self, event) -> None:
        self._close.handle_event(event)


# ============================== effects (juice) ==============================

class Particle:
    def __init__(self, x, y, vx, vy, size, color, life, gravity, drag=3.2):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.size, self.color = size, color
        self.total = life
        self.life = life
        self.gravity, self.drag = gravity, drag

    def update(self, dt: float) -> bool:
        self.life -= dt
        if self.life <= 0:
            return False
        self.vx *= max(0.0, 1.0 - self.drag * dt)
        self.vy *= max(0.0, 1.0 - self.drag * dt)
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        return True

    def draw(self, surface) -> None:
        t = max(0.0, self.life / self.total)
        r = max(1, int(self.size * (0.5 + 0.6 * t)))
        d = r * 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, int(255 * t)), (r, r), r)
        surface.blit(s, (int(self.x - r), int(self.y - r)))


class ConfettiPiece:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vx = random.uniform(-170, 170)
        self.vy = random.uniform(-340, -120)
        self.color = color
        self.w, self.h = 7, 4
        self.life = random.uniform(0.9, 1.5)
        self.total = self.life
        self.rot = random.uniform(0, 6.28)
        self.vrot = random.uniform(-8, 8)
        self.gravity = 420

    def update(self, dt: float) -> bool:
        self.life -= dt
        if self.life <= 0:
            return False
        self.vy += self.gravity * dt
        self.vx *= max(0.0, 1.0 - 1.4 * dt)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rot += self.vrot * dt
        return True

    def draw(self, surface) -> None:
        ca, sa = math.cos(self.rot), math.sin(self.rot)
        w2, h2 = self.w / 2, self.h / 2
        pts = [
            (self.x + ca * -w2 - sa * -h2, self.y + sa * -w2 + ca * -h2),
            (self.x + ca * w2 - sa * -h2, self.y + sa * w2 + ca * -h2),
            (self.x + ca * w2 - sa * h2, self.y + sa * w2 + ca * h2),
            (self.x + ca * -w2 - sa * h2, self.y + sa * -w2 + ca * h2),
        ]
        pygame.draw.polygon(surface, self.color, pts)


class FloatingText:
    def __init__(self, text: str, x, y, color, size=34, life=1.5, rise=46):
        self.text, self.x, self.y = text, x, y
        self.color, self.size = color, size
        self.total = life
        self.age = 0.0
        self.rise = rise

    def update(self, dt: float) -> bool:
        self.age += dt
        return self.age < self.total

    def draw(self, surface) -> None:
        t = self.age / self.total
        if t > 1:
            return
        grow = math.sin(min(1.0, t * 6) * 3.1416)
        size = int(self.size * (1 + 0.35 * grow))
        alpha = 255
        if t > 0.6:
            alpha = int(255 * (1 - (t - 0.6) / 0.4))
        draw_text(surface, self.text, size, self.color, (self.x, self.y - self.rise * t),
                  True, bold=True, alpha=alpha)


class FXLayer:
    """Capa de efectos: partículas, confeti, textos flotantes y destellos de pantalla."""

    def __init__(self):
        self._parts: list = []
        self._confetti: list = []
        self._texts: list = []
        self._flashes: list = []

    def update(self, dt: float) -> None:
        self._parts = [p for p in self._parts if p.update(dt)]
        self._confetti = [c for c in self._confetti if c.update(dt)]
        self._texts = [t for t in self._texts if t.update(dt)]
        for f in self._flashes:
            f[3] += dt
        self._flashes = [f for f in self._flashes if f[3] < f[1]]

    def burst(self, x, y, colors, n=24, speed=250, gravity=260, size=(5, 10)) -> None:
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(speed * 0.35, speed)
            vx = math.cos(ang) * sp
            vy = math.sin(ang) * sp - speed * 0.2
            self._parts.append(Particle(x, y, vx, vy, random.uniform(*size),
                                        random.choice(colors),
                                        random.uniform(BURST_LIFE * 0.55, BURST_LIFE), gravity))

    def sparkle(self, x, y, colors, n=6, speed=120) -> None:
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            sp = random.uniform(20, speed)
            vx, vy = math.cos(ang) * sp, math.sin(ang) * sp - 40
            self._parts.append(Particle(x + random.uniform(-30, 30), y + random.uniform(-20, 20),
                                        vx, vy, random.uniform(3, 6), random.choice(colors),
                                        0.8, 160, drag=2.2))

    def confetti(self, x, y, n=26) -> None:
        colors = [GOLD, WHITE, SECONDARY, SUCCESS]
        for _ in range(n):
            self._confetti.append(ConfettiPiece(x, y, random.choice(colors)))

    def float_text(self, text, x, y, color, size=34, life=1.6, rise=50) -> None:
        self._texts.append(FloatingText(text, x, y, color, size, life, rise))

    def flash(self, color, power=95, duration=0.5) -> None:
        self._flashes.append([color, duration, power, 0.0])

    def draw(self, surface) -> None:
        for p in self._parts:
            p.draw(surface)
        for c in self._confetti:
            c.draw(surface)
        for f in self._flashes:
            t = f[3] / f[1]
            a = int(f[2] * (1 - t))
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((*f[0], a))
            surface.blit(ov, (0, 0))
        for t in self._texts:
            t.draw(surface)