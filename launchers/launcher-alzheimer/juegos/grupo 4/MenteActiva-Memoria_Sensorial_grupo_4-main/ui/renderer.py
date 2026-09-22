"""
MenteActiva — Utilidades de Renderizado
Funciones y clases auxiliares para dibujar elementos de la interfaz:
rectángulos redondeados con sombra, botones accesibles, texto y partículas.
"""
import math
import random
import pygame

from config import Colors, FONT_SIZES, FONT_FALLBACKS


# ═══════════════════════════════════════════════════════════════════════════════
#  CACHÉ DE FUENTES
# ═══════════════════════════════════════════════════════════════════════════════

_font_cache = {}


def get_font(size, bold=False):
    """
    Obtiene una fuente del sistema con caché.
    Prueba la lista de fuentes en FONT_FALLBACKS.
    """
    key = (size, bold)
    if key not in _font_cache:
        font = None
        for name in FONT_FALLBACKS:
            font = pygame.font.SysFont(name, size, bold=bold)
            if font:
                break
        if not font:
            font = pygame.font.Font(None, size)
        _font_cache[key] = font
    return _font_cache[key]


# ═══════════════════════════════════════════════════════════════════════════════
#  TEXTO
# ═══════════════════════════════════════════════════════════════════════════════

def draw_text(surface, text, x, y, size_key="body", color=None,
              bold=False, center=True, max_width=None):
    """
    Dibuja texto con fuente del sistema.

    Args:
        surface: Superficie de destino.
        text: Texto a dibujar.
        x, y: Posición.
        size_key: Clave en FONT_SIZES (ej: 'title', 'body').
        color: Color RGB (por defecto DARK_TEXT).
        bold: Si la fuente es negrita.
        center: Si el texto se centra en (x, y).
        max_width: Ancho máximo — trunca con '...' si excede.
    """
    if color is None:
        color = Colors.DARK_TEXT
    size = FONT_SIZES.get(size_key, 24)
    font = get_font(size, bold)

    if max_width:
        rendered = font.render(text, True, color)
        if rendered.get_width() > max_width and len(text) > 3:
            while len(text) > 3 and font.render(text + "...", True, color).get_width() > max_width:
                text = text[:-1]
            text = text + "..."

    rendered = font.render(text, True, color)
    rect = rendered.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(rendered, rect)
    return rect


def draw_text_shadow(surface, text, x, y, size_key="body", color=None,
                     shadow_color=None, bold=False, center=True):
    """Dibuja texto con sombra suave para mayor legibilidad."""
    if shadow_color is None:
        shadow_color = (0, 0, 0, 60)
    if color is None:
        color = Colors.DARK_TEXT

    # Sombra
    size = FONT_SIZES.get(size_key, 24)
    font = get_font(size, bold)
    shadow_surf = font.render(text, True, (100, 100, 110))
    shadow_rect = shadow_surf.get_rect()
    if center:
        shadow_rect.center = (x + 2, y + 2)
    else:
        shadow_rect.topleft = (x + 2, y + 2)
    surface.blit(shadow_surf, shadow_rect)

    # Texto principal
    return draw_text(surface, text, x, y, size_key, color, bold, center)


# ═══════════════════════════════════════════════════════════════════════════════
#  RECTÁNGULOS DECORADOS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_rounded_rect_shadow(surface, rect, color, radius=12, shadow_offset=4):
    """Dibuja un rectángulo redondeado con sombra."""
    # Sombra
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    shadow_color = tuple(max(0, c - 50) for c in color[:3])
    pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=radius)
    # Rectángulo principal
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_panel(surface, rect, color=None, radius=16, alpha=220):
    """Dibuja un panel semi-transparente con bordes redondeados."""
    if color is None:
        color = Colors.WHITE
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (*color[:3], alpha),
                     pygame.Rect(0, 0, rect.width, rect.height),
                     border_radius=radius)
    surface.blit(panel_surf, rect.topleft)


# ═══════════════════════════════════════════════════════════════════════════════
#  BOTÓN ACCESIBLE
# ═══════════════════════════════════════════════════════════════════════════════

class Boton:
    """
    Botón interactivo con hover, clic y estilo accesible.
    Diseñado con áreas de clic amplias para adultos mayores.
    """

    def __init__(self, x, y, width, height, text, color=None,
                 text_color=None, font_key="button", on_click=None, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or Colors.LAVENDER
        self.text_color = text_color or Colors.DARK_TEXT
        self.font_key = font_key
        self.on_click = on_click
        self.icon = icon

        self._hovered = False
        self._pressed = False
        self._hover_scale = 0.0  # 0 a 1 para animación suave

    @property
    def hovered(self):
        return self._hovered

    def update(self, dt, mouse_pos):
        """Actualiza el estado de hover y animación."""
        self._hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if self._hovered else 0.0
        speed = 8.0 * dt
        if self._hover_scale < target:
            self._hover_scale = min(target, self._hover_scale + speed)
        elif self._hover_scale > target:
            self._hover_scale = max(target, self._hover_scale - speed)

    def handle_event(self, event):
        """Procesa eventos de clic. Retorna True si se activó el botón."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._pressed = True
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._pressed and self.rect.collidepoint(event.pos):
                self._pressed = False
                if self.on_click:
                    self.on_click()
                return True
            self._pressed = False
        return False

    def draw(self, surface):
        """Dibuja el botón con efectos de hover."""
        # Escala de hover
        expand = int(self._hover_scale * 4)
        draw_rect = self.rect.inflate(expand, expand)

        # Color con hover
        r, g, b = self.color
        if self._pressed:
            btn_color = (max(0, r - 30), max(0, g - 30), max(0, b - 30))
        elif self._hover_scale > 0:
            factor = 0.15 * self._hover_scale
            btn_color = (min(255, int(r + (255 - r) * factor)),
                         min(255, int(g + (255 - g) * factor)),
                         min(255, int(b + (255 - b) * factor)))
        else:
            btn_color = self.color

        # Sombra
        shadow_rect = draw_rect.move(3, 3)
        shadow_color = tuple(max(0, c - 60) for c in btn_color)
        pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=12)

        # Cuerpo del botón
        pygame.draw.rect(surface, btn_color, draw_rect, border_radius=12)

        # Borde
        border_color = tuple(max(0, c - 20) for c in btn_color)
        pygame.draw.rect(surface, border_color, draw_rect, 2, border_radius=12)

        # Texto
        draw_text(surface, self.text, draw_rect.centerx, draw_rect.centery,
                  self.font_key, self.text_color, bold=True, center=True)

        # Cursor de mano (indicador visual de hover)
        if self._hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)


# ═══════════════════════════════════════════════════════════════════════════════
#  PARTÍCULAS DE CELEBRACIÓN (optimizadas)
# ═══════════════════════════════════════════════════════════════════════════════

# Caché global de superficies base para partículas.
# Clave: (shape, size, color_rgb)  →  Valor: pygame.Surface (SRCALPHA, opaca).
_PARTICLE_SURFACE_CACHE = {}

# Número máximo de partículas simultáneas para evitar acumulación.
_MAX_PARTICLES = 200

# Colores disponibles para partículas (tupla para poder usarla como clave de caché).
_PARTICLE_COLORS = (
    Colors.CORAL, Colors.GOLD, Colors.SKY_BLUE,
    Colors.SAGE_GREEN, Colors.LAVENDER, Colors.WARM_ROSE,
)


def _get_base_surface(shape, size, color_rgb):
    """Obtiene (o crea y cachea) la superficie base opaca de una partícula."""
    key = (shape, size, color_rgb)
    surf = _PARTICLE_SURFACE_CACHE.get(key)
    if surf is not None:
        return surf

    s = size
    full_color = (*color_rgb, 255)

    if shape == 0:  # circle
        surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, full_color, (s, s), s)
    elif shape == 1:  # rect
        surf = pygame.Surface((s * 2, s), pygame.SRCALPHA)
        pygame.draw.rect(surf, full_color, (0, 0, s * 2, s), border_radius=2)
    else:  # star
        dim = s * 3
        surf = pygame.Surface((dim, dim), pygame.SRCALPHA)
        cx, cy = dim // 2, dim // 2
        for i in range(5):
            angle = i * 2 * math.pi / 5 - math.pi / 2
            px = cx + int(s * math.cos(angle))
            py = cy + int(s * math.sin(angle))
            pygame.draw.line(surf, full_color, (cx, cy), (px, py), max(1, s // 3))

    _PARTICLE_SURFACE_CACHE[key] = surf
    return surf


class Particula:
    """Partícula individual para efectos de celebración (optimizada)."""

    __slots__ = (
        'x', 'y', 'vx', 'vy', 'life', 'max_life',
        'size', 'shape', 'color_rgb', 'rotation', 'rot_speed',
    )

    def __init__(self, x, y, color=None):
        self.x = float(x)
        self.y = float(y)
        c = color or random.choice(_PARTICLE_COLORS)
        self.color_rgb = c[:3]
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-6, -1)
        self.size = random.randint(3, 8)
        self.life = random.uniform(1.5, 3.5)
        self.max_life = self.life
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)
        # 0=circle, 1=rect, 2=star  (int es más rápido que comparar strings)
        self.shape = random.randint(0, 2)

    def update(self, dt):
        dt60 = 60.0 * dt
        self.x += self.vx * dt60
        self.y += self.vy * dt60
        self.vy += 0.08 * dt60  # gravedad
        self.vx *= 0.998
        self.life -= dt
        self.rotation += self.rot_speed * dt


class SistemaParticulas:
    """Sistema de partículas para celebraciones y efectos visuales (optimizado).

    Optimizaciones principales:
    - Las superficies base se pre-renderizan una sola vez y se cachean.
    - Se usa set_alpha() en lugar de crear superficies SRCALPHA por frame.
    - Se rota solo cuando es necesario (rectángulos).
    - Se limita el número máximo de partículas activas.
    - Se usa filtrado in-place para reducir presión de GC.
    """

    def __init__(self):
        self._particulas = []

    def emitir(self, x, y, cantidad=20, color=None):
        """Emite un grupo de partículas desde una posición."""
        espacio = _MAX_PARTICLES - len(self._particulas)
        cantidad = min(cantidad, espacio)
        for _ in range(cantidad):
            self._particulas.append(Particula(x, y, color))

    def emitir_lluvia(self, width, cantidad=40):
        """Emite partículas desde la parte superior (celebración general)."""
        espacio = _MAX_PARTICLES - len(self._particulas)
        cantidad = min(cantidad, espacio)
        for _ in range(cantidad):
            x = random.randint(0, width)
            y = random.randint(-20, 30)
            self._particulas.append(Particula(x, y))

    def update(self, dt):
        """Actualiza todas las partículas y elimina las muertas (in-place)."""
        write = 0
        particulas = self._particulas
        for i in range(len(particulas)):
            p = particulas[i]
            p.update(dt)
            if p.life > 0:
                particulas[write] = p
                write += 1
        del particulas[write:]

    def draw(self, surface):
        """Dibuja todas las partículas activas de forma optimizada."""
        blit = surface.blit  # evitar lookup repetido
        for p in self._particulas:
            ratio = p.life / p.max_life
            if ratio <= 0:
                continue
            alpha = int(255.0 * ratio)
            s = max(1, int(p.size * ratio))

            # Obtener superficie base cacheada al tamaño actual
            base = _get_base_surface(p.shape, s, p.color_rgb)

            if p.shape == 1:  # rect — necesita rotación
                rotated = pygame.transform.rotate(base, p.rotation)
                rotated.set_alpha(alpha)
                blit(rotated, (int(p.x) - rotated.get_width() // 2,
                               int(p.y) - rotated.get_height() // 2))
            else:
                # circle / star — sin rotación, solo alpha
                if alpha < 255:
                    frame = base.copy()
                    frame.set_alpha(alpha)
                    blit(frame, (int(p.x) - base.get_width() // 2,
                                 int(p.y) - base.get_height() // 2))
                else:
                    blit(base, (int(p.x) - base.get_width() // 2,
                                int(p.y) - base.get_height() // 2))

    @property
    def active(self):
        return len(self._particulas) > 0

    def clear(self):
        self._particulas.clear()


# ═══════════════════════════════════════════════════════════════════════════════
#  FONDO DECORATIVO
# ═══════════════════════════════════════════════════════════════════════════════

def draw_gradient_background(surface, color_top, color_bottom):
    """Dibuja un degradado vertical suave."""
    height = surface.get_height()
    width = surface.get_width()
    for y in range(height):
        t = y / max(height - 1, 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))


_cached_bg = None
_cached_bg_size = None


def draw_background(surface):
    """Dibuja el fondo del juego con degradado (con caché)."""
    global _cached_bg, _cached_bg_size
    size = (surface.get_width(), surface.get_height())
    if _cached_bg is None or _cached_bg_size != size:
        _cached_bg = pygame.Surface(size)
        draw_gradient_background(_cached_bg, (235, 245, 251), (210, 225, 240))
        _cached_bg_size = size
    surface.blit(_cached_bg, (0, 0))


# ═══════════════════════════════════════════════════════════════════════════════
#  OVERLAY
# ═══════════════════════════════════════════════════════════════════════════════

def draw_overlay(surface, alpha=150):
    """Dibuja un overlay oscuro semi-transparente sobre toda la pantalla."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((*Colors.OVERLAY_DARK, alpha))
    surface.blit(overlay, (0, 0))


def reset_cursor():
    """Restaura el cursor por defecto."""
    try:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    except Exception:
        pass
