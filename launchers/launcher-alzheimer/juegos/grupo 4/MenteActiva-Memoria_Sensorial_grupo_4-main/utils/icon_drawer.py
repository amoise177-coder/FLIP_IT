"""
MenteActiva — Dibujante de Íconos (Sprites + Vectorial)
Carga sprites PNG desde assets/sprites/ si existen.
Si no, usa el fallback vectorial con pygame.draw.
"""
import math
import os
import pygame

from config import SPRITES_DIR


# ═══════════════════════════════════════════════════════════════════════════════
#  CACHÉ DE SPRITES
# ═══════════════════════════════════════════════════════════════════════════════

_sprite_cache = {}       # {icon_name: pygame.Surface o None}
_sprite_checked = set()  # Nombres ya verificados (evita re-buscar los que no existen)


def _load_sprite(icon_name):
    """
    Intenta cargar el sprite PNG para un ícono.
    Retorna la Surface cargada o None si no existe.
    El resultado se almacena en caché.
    """
    if icon_name in _sprite_cache:
        return _sprite_cache[icon_name]

    if icon_name in _sprite_checked:
        return None

    _sprite_checked.add(icon_name)

    filepath = os.path.join(SPRITES_DIR, f"{icon_name}.png")
    if os.path.isfile(filepath):
        try:
            surface = pygame.image.load(filepath).convert_alpha()
            _sprite_cache[icon_name] = surface
            return surface
        except Exception as e:
            print(f"[icon_drawer] Error cargando sprite '{filepath}': {e}")

    return None


def clear_sprite_cache():
    """Limpia la caché de sprites (útil si se recargan assets en caliente)."""
    _sprite_cache.clear()
    _sprite_checked.clear()


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _star_points(cx, cy, outer_r, inner_r, n_points=5, rotation=-math.pi / 2):
    """Genera los vértices de una estrella de n puntas."""
    points = []
    for i in range(n_points * 2):
        r = outer_r if i % 2 == 0 else inner_r
        angle = rotation + i * math.pi / n_points
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return points


def _heart_points(cx, cy, size):
    """Genera los vértices de un corazón."""
    points = []
    for i in range(50):
        t = i / 50.0 * 2 * math.pi
        x = size * 0.4 * (16 * math.sin(t) ** 3)
        y = -size * 0.4 * (13 * math.cos(t) - 5 * math.cos(2 * t) -
                           2 * math.cos(3 * t) - math.cos(4 * t))
        points.append((cx + x / 17, cy + y / 17))
    return points


def _darker(color, factor=0.7):
    """Retorna un color más oscuro."""
    return tuple(max(0, int(c * factor)) for c in color)


def _lighter(color, factor=1.4):
    """Retorna un color más claro."""
    return tuple(min(255, int(c * factor)) for c in color)


# ═══════════════════════════════════════════════════════════════════════════════
#  NATURALEZA
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_sol(surf, cx, cy, r, color):
    """Sol: círculo central con rayos radiantes."""
    # Rayos
    ray_color = _lighter(color)
    for i in range(8):
        angle = i * math.pi / 4
        x1 = cx + int(r * 0.45 * math.cos(angle))
        y1 = cy + int(r * 0.45 * math.sin(angle))
        x2 = cx + int(r * 0.9 * math.cos(angle))
        y2 = cy + int(r * 0.9 * math.sin(angle))
        pygame.draw.line(surf, ray_color, (x1, y1), (x2, y2), max(3, r // 6))
    # Centro
    pygame.draw.circle(surf, color, (cx, cy), int(r * 0.38))
    pygame.draw.circle(surf, _lighter(color), (cx - r // 8, cy - r // 8), int(r * 0.12))


def _draw_luna(surf, cx, cy, r, color):
    """Luna creciente."""
    pygame.draw.circle(surf, color, (cx, cy), int(r * 0.55))
    bg = surf.get_at((0, 0)) if surf.get_width() > 0 else (0, 0, 0, 0)
    # Crear la superficie temporal para el recorte de luna creciente
    mask_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask_surf, color, (r, r), int(r * 0.55))
    pygame.draw.circle(mask_surf, (0, 0, 0, 0), (r + int(r * 0.3), r - int(r * 0.15)), int(r * 0.45))
    surf.blit(mask_surf, (cx - r, cy - r))


def _draw_flor(surf, cx, cy, r, color):
    """Flor: pétalos alrededor de un centro."""
    petal_r = int(r * 0.28)
    dist = int(r * 0.32)
    for i in range(5):
        angle = i * 2 * math.pi / 5 - math.pi / 2
        px = cx + int(dist * math.cos(angle))
        py = cy + int(dist * math.sin(angle))
        pygame.draw.circle(surf, color, (px, py), petal_r)
    # Centro
    pygame.draw.circle(surf, _lighter(color), (cx, cy), int(r * 0.2))


def _draw_arbol(surf, cx, cy, r, color):
    """Árbol: copa circular sobre tronco."""
    trunk_w = max(4, r // 5)
    trunk_h = int(r * 0.5)
    # Tronco
    trunk_color = _darker(color, 0.5)
    pygame.draw.rect(surf, trunk_color, (cx - trunk_w // 2, cy, trunk_w, trunk_h))
    # Copa
    pygame.draw.circle(surf, color, (cx, cy - int(r * 0.1)), int(r * 0.48))
    pygame.draw.circle(surf, _lighter(color), (cx - r // 6, cy - int(r * 0.2)), int(r * 0.15))


def _draw_nube(surf, cx, cy, r, color):
    """Nube: tres círculos superpuestos."""
    cr = int(r * 0.3)
    pygame.draw.circle(surf, color, (cx - int(r * 0.3), cy + int(r * 0.05)), cr)
    pygame.draw.circle(surf, color, (cx + int(r * 0.3), cy + int(r * 0.05)), cr)
    pygame.draw.circle(surf, color, (cx, cy - int(r * 0.15)), int(r * 0.38))
    # Brillo
    pygame.draw.circle(surf, _lighter(color), (cx - r // 8, cy - int(r * 0.25)), int(r * 0.1))


def _draw_estrella(surf, cx, cy, r, color):
    """Estrella de 5 puntas."""
    points = _star_points(cx, cy, int(r * 0.55), int(r * 0.22))
    if len(points) >= 3:
        pygame.draw.polygon(surf, color, points)
        pygame.draw.polygon(surf, _lighter(color), points, 2)


def _draw_montana(surf, cx, cy, r, color):
    """Montañas: dos triángulos con cima nevada."""
    # Montaña trasera (más pequeña)
    m2 = [
        (cx + int(r * 0.15), cy + int(r * 0.5)),
        (cx + int(r * 0.65), cy - int(r * 0.3)),
        (cx + int(r * 0.9), cy + int(r * 0.5)),
    ]
    pygame.draw.polygon(surf, _darker(color, 0.7), m2)
    # Montaña principal
    m1 = [
        (cx - int(r * 0.7), cy + int(r * 0.5)),
        (cx - int(r * 0.05), cy - int(r * 0.55)),
        (cx + int(r * 0.6), cy + int(r * 0.5)),
    ]
    pygame.draw.polygon(surf, color, m1)
    # Nieve en la cima
    snow = [
        (cx - int(r * 0.05), cy - int(r * 0.55)),
        (cx - int(r * 0.2), cy - int(r * 0.25)),
        (cx + int(r * 0.1), cy - int(r * 0.25)),
    ]
    pygame.draw.polygon(surf, (240, 240, 255), snow)


def _draw_gota(surf, cx, cy, r, color):
    """Gota de agua."""
    # Cuerpo circular inferior
    circle_cy = cy + int(r * 0.12)
    circle_r = int(r * 0.35)
    pygame.draw.circle(surf, color, (cx, circle_cy), circle_r)
    # Punta triangular superior
    tri = [
        (cx, cy - int(r * 0.55)),
        (cx - circle_r + 2, circle_cy - int(r * 0.08)),
        (cx + circle_r - 2, circle_cy - int(r * 0.08)),
    ]
    pygame.draw.polygon(surf, color, tri)
    # Reflejo
    pygame.draw.circle(surf, _lighter(color), (cx - r // 8, circle_cy - r // 8), int(r * 0.1))


# ═══════════════════════════════════════════════════════════════════════════════
#  ALIMENTOS
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_manzana(surf, cx, cy, r, color):
    """Manzana con tallo y hoja."""
    ar = int(r * 0.42)
    # Cuerpo
    pygame.draw.circle(surf, color, (cx, cy + int(r * 0.05)), ar)
    # Hendidura superior
    pygame.draw.circle(surf, _darker(color, 0.85), (cx, cy - int(r * 0.2)), int(r * 0.12))
    # Tallo
    pygame.draw.line(surf, (100, 70, 40), (cx, cy - int(r * 0.25)),
                     (cx + int(r * 0.05), cy - int(r * 0.5)), max(2, r // 10))
    # Hoja
    leaf_pts = [
        (cx + int(r * 0.05), cy - int(r * 0.45)),
        (cx + int(r * 0.3), cy - int(r * 0.5)),
        (cx + int(r * 0.15), cy - int(r * 0.35)),
    ]
    pygame.draw.polygon(surf, (100, 180, 100), leaf_pts)


def _draw_pan(surf, cx, cy, r, color):
    """Pan / hogaza ovalada."""
    w = int(r * 0.8)
    h = int(r * 0.5)
    rect = pygame.Rect(cx - w, cy - h // 2, w * 2, h)
    pygame.draw.ellipse(surf, color, rect)
    # Cortes decorativos
    for i in range(-1, 2):
        lx = cx + i * int(r * 0.25)
        pygame.draw.line(surf, _darker(color), (lx - int(r * 0.08), cy - int(r * 0.1)),
                         (lx + int(r * 0.08), cy + int(r * 0.1)), 2)
    # Brillo
    pygame.draw.ellipse(surf, _lighter(color),
                        pygame.Rect(cx - int(r * 0.3), cy - h // 2 + 2, int(r * 0.5), int(r * 0.18)))


def _draw_cafe(surf, cx, cy, r, color):
    """Taza de café con asa y vapor."""
    cup_w = int(r * 0.55)
    cup_h = int(r * 0.5)
    cup_rect = pygame.Rect(cx - cup_w // 2, cy - int(r * 0.05), cup_w, cup_h)
    pygame.draw.rect(surf, color, cup_rect, border_radius=4)
    # Asa
    pygame.draw.arc(surf, _darker(color),
                    pygame.Rect(cx + cup_w // 2 - 2, cy + int(r * 0.05),
                                int(r * 0.25), int(r * 0.3)),
                    -math.pi / 2, math.pi / 2, max(2, r // 10))
    # Vapor
    vapor_color = _lighter(color, 1.3)
    for i in range(3):
        vx = cx - int(r * 0.15) + i * int(r * 0.15)
        for j in range(3):
            vy = cy - int(r * 0.15) - j * int(r * 0.12)
            offset = int(r * 0.05 * math.sin(j * 1.5 + i))
            pygame.draw.circle(surf, vapor_color, (vx + offset, vy), max(1, r // 14))


def _draw_pastel(surf, cx, cy, r, color):
    """Pastel de cumpleaños con velas."""
    # Base del pastel
    base_w = int(r * 0.9)
    base_h = int(r * 0.45)
    base_rect = pygame.Rect(cx - base_w // 2, cy, base_w, base_h)
    pygame.draw.rect(surf, color, base_rect, border_radius=6)
    # Capa superior
    pygame.draw.rect(surf, _lighter(color),
                     pygame.Rect(cx - base_w // 2, cy, base_w, int(r * 0.12)),
                     border_radius=4)
    # Velas
    candle_color = (255, 200, 100)
    for i in range(-1, 2):
        vx = cx + i * int(r * 0.2)
        pygame.draw.rect(surf, candle_color,
                         (vx - 2, cy - int(r * 0.3), 4, int(r * 0.3)))
        # Llama
        pygame.draw.circle(surf, (255, 150, 50), (vx, cy - int(r * 0.35)), max(3, r // 8))


def _draw_uva(surf, cx, cy, r, color):
    """Racimo de uvas."""
    gr = max(3, int(r * 0.16))
    # Racimo triangular
    positions = [
        (0, -2), (-1, -1), (1, -1), (-2, 0), (0, 0), (2, 0), (-1, 1), (1, 1), (0, 2)
    ]
    for px, py in positions:
        gx = cx + int(px * gr * 0.9)
        gy = cy + int(py * gr * 0.85) + int(r * 0.05)
        pygame.draw.circle(surf, color, (gx, gy), gr)
        pygame.draw.circle(surf, _lighter(color), (gx - gr // 3, gy - gr // 3), max(1, gr // 3))
    # Tallo
    pygame.draw.line(surf, (100, 80, 40), (cx, cy - int(r * 0.35)),
                     (cx, cy - int(r * 0.55)), 2)


def _draw_naranja(surf, cx, cy, r, color):
    """Naranja con hoja."""
    orange_r = int(r * 0.42)
    pygame.draw.circle(surf, color, (cx, cy + int(r * 0.05)), orange_r)
    # Textura (puntos sutiles)
    for i in range(5):
        angle = i * 2 * math.pi / 5
        dx = int(orange_r * 0.3 * math.cos(angle))
        dy = int(orange_r * 0.3 * math.sin(angle))
        pygame.draw.circle(surf, _darker(color, 0.92), (cx + dx, cy + int(r * 0.05) + dy), 1)
    # Hoja
    leaf_pts = [
        (cx, cy - int(r * 0.35)),
        (cx + int(r * 0.25), cy - int(r * 0.55)),
        (cx + int(r * 0.1), cy - int(r * 0.35)),
    ]
    pygame.draw.polygon(surf, (100, 180, 80), leaf_pts)


def _draw_helado(surf, cx, cy, r, color):
    """Cono de helado."""
    # Cono (triángulo invertido)
    cone_color = (210, 170, 100)
    cone = [
        (cx - int(r * 0.3), cy - int(r * 0.05)),
        (cx + int(r * 0.3), cy - int(r * 0.05)),
        (cx, cy + int(r * 0.55)),
    ]
    pygame.draw.polygon(surf, cone_color, cone)
    # Líneas del cono
    pygame.draw.line(surf, _darker(cone_color), cone[2], (cx - int(r * 0.15), cy - int(r * 0.02)), 1)
    pygame.draw.line(surf, _darker(cone_color), cone[2], (cx + int(r * 0.15), cy - int(r * 0.02)), 1)
    # Bola de helado
    pygame.draw.circle(surf, color, (cx, cy - int(r * 0.18)), int(r * 0.32))
    pygame.draw.circle(surf, _lighter(color), (cx - r // 8, cy - int(r * 0.25)), int(r * 0.1))


def _draw_galleta(surf, cx, cy, r, color):
    """Galleta con chips de chocolate."""
    gr = int(r * 0.45)
    pygame.draw.circle(surf, color, (cx, cy), gr)
    # Borde crujiente
    pygame.draw.circle(surf, _darker(color, 0.9), (cx, cy), gr, 2)
    # Chips
    chip_color = (80, 50, 30)
    chip_positions = [
        (-0.15, -0.2), (0.2, -0.1), (-0.1, 0.15), (0.15, 0.2), (0, 0)
    ]
    for px, py in chip_positions:
        pygame.draw.circle(surf, chip_color, (cx + int(r * px), cy + int(r * py)), max(2, r // 10))


# ═══════════════════════════════════════════════════════════════════════════════
#  ANIMALES
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_gato(surf, cx, cy, r, color):
    """Cara de gato con orejas triangulares."""
    head_r = int(r * 0.38)
    # Cabeza
    pygame.draw.circle(surf, color, (cx, cy + int(r * 0.05)), head_r)
    # Orejas
    for dx in [-1, 1]:
        ear = [
            (cx + dx * int(r * 0.1), cy - int(r * 0.25)),
            (cx + dx * int(r * 0.38), cy - int(r * 0.55)),
            (cx + dx * int(r * 0.35), cy - int(r * 0.15)),
        ]
        pygame.draw.polygon(surf, color, ear)
        # Interior de oreja
        inner = [
            (cx + dx * int(r * 0.15), cy - int(r * 0.25)),
            (cx + dx * int(r * 0.33), cy - int(r * 0.48)),
            (cx + dx * int(r * 0.32), cy - int(r * 0.2)),
        ]
        pygame.draw.polygon(surf, _lighter(color), inner)
    # Ojos
    eye_y = cy
    for dx in [-1, 1]:
        pygame.draw.circle(surf, (50, 50, 50), (cx + dx * int(r * 0.15), eye_y), max(2, r // 8))
    # Nariz
    pygame.draw.circle(surf, _darker(color, 0.6), (cx, cy + int(r * 0.12)), max(2, r // 12))
    # Bigotes
    for dx in [-1, 1]:
        for dy in [-1, 0, 1]:
            wx1 = cx + dx * int(r * 0.1)
            wx2 = cx + dx * int(r * 0.5)
            wy = cy + int(r * 0.12) + dy * int(r * 0.06)
            pygame.draw.line(surf, _darker(color, 0.5), (wx1, wy), (wx2, wy + dy * 2), 1)


def _draw_perro(surf, cx, cy, r, color):
    """Cara de perro con orejas caídas."""
    head_r = int(r * 0.35)
    # Orejas caídas
    for dx in [-1, 1]:
        ear_rect = pygame.Rect(
            cx + dx * int(r * 0.25) - int(r * 0.12),
            cy - int(r * 0.15),
            int(r * 0.24), int(r * 0.5)
        )
        pygame.draw.ellipse(surf, _darker(color, 0.8), ear_rect)
    # Cabeza
    pygame.draw.circle(surf, color, (cx, cy), head_r)
    # Hocico
    pygame.draw.ellipse(surf, _lighter(color),
                        pygame.Rect(cx - int(r * 0.15), cy + int(r * 0.05),
                                    int(r * 0.3), int(r * 0.22)))
    # Ojos
    for dx in [-1, 1]:
        pygame.draw.circle(surf, (50, 50, 50), (cx + dx * int(r * 0.13), cy - int(r * 0.08)),
                           max(2, r // 10))
    # Nariz
    pygame.draw.circle(surf, (40, 40, 40), (cx, cy + int(r * 0.12)), max(3, r // 8))


def _draw_pajaro(surf, cx, cy, r, color):
    """Pájaro con ala y pico."""
    # Cuerpo
    body_rect = pygame.Rect(cx - int(r * 0.35), cy - int(r * 0.15), int(r * 0.55), int(r * 0.4))
    pygame.draw.ellipse(surf, color, body_rect)
    # Cabeza
    pygame.draw.circle(surf, color, (cx + int(r * 0.2), cy - int(r * 0.2)), int(r * 0.2))
    # Ala
    wing = [
        (cx - int(r * 0.1), cy - int(r * 0.05)),
        (cx - int(r * 0.5), cy - int(r * 0.3)),
        (cx - int(r * 0.15), cy + int(r * 0.15)),
    ]
    pygame.draw.polygon(surf, _darker(color), wing)
    # Pico
    beak = [
        (cx + int(r * 0.38), cy - int(r * 0.22)),
        (cx + int(r * 0.6), cy - int(r * 0.15)),
        (cx + int(r * 0.38), cy - int(r * 0.12)),
    ]
    pygame.draw.polygon(surf, (220, 160, 50), beak)
    # Ojo
    pygame.draw.circle(surf, (40, 40, 40), (cx + int(r * 0.25), cy - int(r * 0.23)), max(2, r // 12))


def _draw_mariposa(surf, cx, cy, r, color):
    """Mariposa con cuatro alas."""
    # Cuerpo
    pygame.draw.rect(surf, _darker(color, 0.5),
                     (cx - 2, cy - int(r * 0.35), 4, int(r * 0.7)), border_radius=2)
    # Alas superiores
    for dx in [-1, 1]:
        wing_rect = pygame.Rect(
            cx + (0 if dx == 1 else -int(r * 0.45)),
            cy - int(r * 0.45),
            int(r * 0.45), int(r * 0.4)
        )
        pygame.draw.ellipse(surf, color, wing_rect)
        # Detalle interior
        inner_rect = wing_rect.inflate(-int(r * 0.15), -int(r * 0.12))
        pygame.draw.ellipse(surf, _lighter(color), inner_rect)
    # Alas inferiores
    for dx in [-1, 1]:
        wing_rect = pygame.Rect(
            cx + (0 if dx == 1 else -int(r * 0.35)),
            cy,
            int(r * 0.35), int(r * 0.35)
        )
        pygame.draw.ellipse(surf, _darker(color, 0.85), wing_rect)
    # Antenas
    for dx in [-1, 1]:
        end_x = cx + dx * int(r * 0.2)
        end_y = cy - int(r * 0.55)
        pygame.draw.line(surf, _darker(color, 0.5), (cx, cy - int(r * 0.35)),
                         (end_x, end_y), 1)
        pygame.draw.circle(surf, _darker(color, 0.5), (end_x, end_y), max(1, r // 14))


def _draw_pez(surf, cx, cy, r, color):
    """Pez con cola triangular."""
    # Cuerpo ovalado
    body_rect = pygame.Rect(cx - int(r * 0.4), cy - int(r * 0.2), int(r * 0.7), int(r * 0.4))
    pygame.draw.ellipse(surf, color, body_rect)
    # Cola
    tail = [
        (cx - int(r * 0.35), cy),
        (cx - int(r * 0.65), cy - int(r * 0.25)),
        (cx - int(r * 0.65), cy + int(r * 0.25)),
    ]
    pygame.draw.polygon(surf, _darker(color, 0.85), tail)
    # Ojo
    pygame.draw.circle(surf, (255, 255, 255), (cx + int(r * 0.12), cy - int(r * 0.02)), max(3, r // 8))
    pygame.draw.circle(surf, (30, 30, 30), (cx + int(r * 0.14), cy - int(r * 0.02)), max(2, r // 12))
    # Aleta
    fin = [
        (cx - int(r * 0.05), cy - int(r * 0.18)),
        (cx + int(r * 0.05), cy - int(r * 0.4)),
        (cx + int(r * 0.15), cy - int(r * 0.15)),
    ]
    pygame.draw.polygon(surf, _darker(color, 0.9), fin)


def _draw_conejo(surf, cx, cy, r, color):
    """Conejo con orejas largas."""
    head_r = int(r * 0.32)
    # Orejas largas
    for dx in [-1, 1]:
        ear_rect = pygame.Rect(
            cx + dx * int(r * 0.1) - int(r * 0.09),
            cy - int(r * 0.75),
            int(r * 0.18), int(r * 0.55)
        )
        pygame.draw.ellipse(surf, color, ear_rect)
        # Interior rosa
        inner_ear = ear_rect.inflate(-int(r * 0.08), -int(r * 0.15))
        pygame.draw.ellipse(surf, _lighter(color), inner_ear)
    # Cabeza
    pygame.draw.circle(surf, color, (cx, cy + int(r * 0.05)), head_r)
    # Ojos
    for dx in [-1, 1]:
        pygame.draw.circle(surf, (50, 50, 50), (cx + dx * int(r * 0.12), cy), max(2, r // 10))
    # Nariz
    pygame.draw.circle(surf, _darker(color, 0.7), (cx, cy + int(r * 0.12)), max(2, r // 12))


def _draw_tortuga(surf, cx, cy, r, color):
    """Tortuga con caparazón."""
    # Caparazón
    shell_rect = pygame.Rect(cx - int(r * 0.4), cy - int(r * 0.2), int(r * 0.7), int(r * 0.55))
    pygame.draw.ellipse(surf, color, shell_rect)
    # Patrón del caparazón
    pygame.draw.ellipse(surf, _darker(color, 0.85), shell_rect, 2)
    # Hexágonos simplificados (líneas)
    mcx, mcy = shell_rect.centerx, shell_rect.centery
    for i in range(6):
        angle = i * math.pi / 3
        lx = mcx + int(r * 0.15 * math.cos(angle))
        ly = mcy + int(r * 0.1 * math.sin(angle))
        pygame.draw.line(surf, _darker(color, 0.8), (mcx, mcy), (lx, ly), 1)
    # Cabeza
    pygame.draw.circle(surf, _lighter(color, 1.1), (cx + int(r * 0.4), cy + int(r * 0.05)),
                       int(r * 0.14))
    pygame.draw.circle(surf, (40, 40, 40), (cx + int(r * 0.44), cy + int(r * 0.02)), max(1, r // 16))
    # Patas
    for dx, dy in [(-0.35, 0.2), (-0.25, 0.3), (0.2, 0.3), (0.1, 0.2)]:
        pygame.draw.circle(surf, _lighter(color, 1.1),
                           (cx + int(r * dx), cy + int(r * dy)), int(r * 0.08))


def _draw_abeja(surf, cx, cy, r, color):
    """Abeja con rayas y alas."""
    body_w = int(r * 0.55)
    body_h = int(r * 0.35)
    body_rect = pygame.Rect(cx - body_w // 2, cy - body_h // 2 + int(r * 0.05), body_w, body_h)
    # Cuerpo amarillo
    pygame.draw.ellipse(surf, color, body_rect)
    # Rayas negras
    stripe_color = (50, 50, 50)
    for i in range(3):
        sx = body_rect.left + int(body_w * (0.3 + i * 0.2))
        pygame.draw.line(surf, stripe_color, (sx, body_rect.top + 3),
                         (sx, body_rect.bottom - 3), max(2, r // 10))
    # Alas
    for dy in [-1, 1]:
        wing_rect = pygame.Rect(
            cx - int(r * 0.15), cy - int(r * 0.35) if dy == -1 else cy + int(r * 0.15),
            int(r * 0.35), int(r * 0.22)
        )
        pygame.draw.ellipse(surf, (200, 220, 255), wing_rect)
        pygame.draw.ellipse(surf, (180, 200, 240), wing_rect, 1)
    # Cabeza
    pygame.draw.circle(surf, (60, 60, 60), (cx - int(r * 0.3), cy + int(r * 0.05)), int(r * 0.12))
    # Antenas
    for dy_off in [-1, 1]:
        end = (cx - int(r * 0.45), cy - int(r * 0.15) + dy_off * int(r * 0.08))
        pygame.draw.line(surf, (60, 60, 60), (cx - int(r * 0.35), cy + int(r * 0.0)), end, 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  HOGAR
# ═══════════════════════════════════════════════════════════════════════════════

def _draw_casa(surf, cx, cy, r, color):
    """Casa con techo y puerta."""
    w = int(r * 0.7)
    h = int(r * 0.45)
    # Cuerpo
    body_rect = pygame.Rect(cx - w // 2, cy, w, h)
    pygame.draw.rect(surf, color, body_rect)
    # Techo
    roof = [
        (cx - int(r * 0.5), cy),
        (cx, cy - int(r * 0.45)),
        (cx + int(r * 0.5), cy),
    ]
    pygame.draw.polygon(surf, _darker(color), roof)
    # Puerta
    door_w = int(r * 0.18)
    door_h = int(r * 0.3)
    pygame.draw.rect(surf, _darker(color, 0.5),
                     (cx - door_w // 2, cy + h - door_h, door_w, door_h))
    # Ventanas
    for dx in [-1, 1]:
        pygame.draw.rect(surf, (200, 220, 255),
                         (cx + dx * int(r * 0.2) - int(r * 0.08), cy + int(r * 0.08),
                          int(r * 0.16), int(r * 0.14)))


def _draw_silla(surf, cx, cy, r, color):
    """Silla vista de perfil."""
    lw = max(3, r // 7)
    # Asiento
    seat_y = cy + int(r * 0.05)
    pygame.draw.rect(surf, color,
                     (cx - int(r * 0.3), seat_y, int(r * 0.6), lw), border_radius=2)
    # Respaldo
    pygame.draw.rect(surf, color,
                     (cx - int(r * 0.3), cy - int(r * 0.4), lw, int(r * 0.45)), border_radius=2)
    # Patas
    pygame.draw.rect(surf, _darker(color),
                     (cx - int(r * 0.28), seat_y + lw, lw - 1, int(r * 0.35)))
    pygame.draw.rect(surf, _darker(color),
                     (cx + int(r * 0.25), seat_y + lw, lw - 1, int(r * 0.35)))
    # Barras del respaldo
    for i in range(3):
        by = cy - int(r * 0.35) + i * int(r * 0.15)
        pygame.draw.line(surf, _darker(color, 0.85),
                         (cx - int(r * 0.28), by), (cx - int(r * 0.28) + lw + 1, by), 2)


def _draw_taza(surf, cx, cy, r, color):
    """Taza con asa."""
    cup_w = int(r * 0.5)
    cup_h = int(r * 0.45)
    cup_rect = pygame.Rect(cx - cup_w // 2 - int(r * 0.05), cy - int(r * 0.05), cup_w, cup_h)
    pygame.draw.rect(surf, color, cup_rect, border_radius=4)
    # Asa
    handle_rect = pygame.Rect(
        cup_rect.right - 2, cy + int(r * 0.02), int(r * 0.2), int(r * 0.25)
    )
    pygame.draw.ellipse(surf, color, handle_rect, max(2, r // 8))
    # Líquido
    liquid_rect = pygame.Rect(cup_rect.left + 3, cup_rect.top + 3, cup_rect.width - 6, int(r * 0.12))
    pygame.draw.rect(surf, _darker(color, 0.6), liquid_rect, border_radius=2)


def _draw_reloj(surf, cx, cy, r, color):
    """Reloj analógico."""
    clock_r = int(r * 0.42)
    # Marco
    pygame.draw.circle(surf, color, (cx, cy), clock_r)
    pygame.draw.circle(surf, _darker(color), (cx, cy), clock_r, 3)
    # Carátula interior
    pygame.draw.circle(surf, _lighter(color, 1.3), (cx, cy), clock_r - 4)
    # Marcas de horas
    for i in range(12):
        angle = i * math.pi / 6 - math.pi / 2
        inner = clock_r - 8
        outer = clock_r - 4
        x1 = cx + int(inner * math.cos(angle))
        y1 = cy + int(inner * math.sin(angle))
        x2 = cx + int(outer * math.cos(angle))
        y2 = cy + int(outer * math.sin(angle))
        pygame.draw.line(surf, _darker(color), (x1, y1), (x2, y2), 2)
    # Manecillas
    hand_color = _darker(color, 0.4)
    # Hora (apuntando a las 10)
    h_angle = 10 * math.pi / 6 - math.pi / 2
    pygame.draw.line(surf, hand_color, (cx, cy),
                     (cx + int(clock_r * 0.45 * math.cos(h_angle)),
                      cy + int(clock_r * 0.45 * math.sin(h_angle))), 3)
    # Minuto (apuntando a las 2)
    m_angle = 2 * math.pi / 6 - math.pi / 2
    pygame.draw.line(surf, hand_color, (cx, cy),
                     (cx + int(clock_r * 0.65 * math.cos(m_angle)),
                      cy + int(clock_r * 0.65 * math.sin(m_angle))), 2)
    # Centro
    pygame.draw.circle(surf, hand_color, (cx, cy), max(2, r // 12))


def _draw_libro(surf, cx, cy, r, color):
    """Libro abierto."""
    w = int(r * 0.7)
    h = int(r * 0.55)
    # Página izquierda
    pygame.draw.rect(surf, _lighter(color, 1.4),
                     (cx - w // 2, cy - h // 2, w // 2, h), border_radius=2)
    # Página derecha
    pygame.draw.rect(surf, _lighter(color, 1.3),
                     (cx, cy - h // 2, w // 2, h), border_radius=2)
    # Lomo
    pygame.draw.line(surf, _darker(color), (cx, cy - h // 2), (cx, cy + h // 2), 3)
    # Líneas de texto
    for i in range(4):
        ly = cy - h // 2 + int(r * 0.12) + i * int(r * 0.1)
        pygame.draw.line(surf, _darker(color, 0.7),
                         (cx - w // 2 + 6, ly), (cx - 5, ly), 1)
        pygame.draw.line(surf, _darker(color, 0.7),
                         (cx + 5, ly), (cx + w // 2 - 6, ly), 1)
    # Cubierta
    pygame.draw.rect(surf, color, (cx - w // 2, cy - h // 2, w, h), 3, border_radius=2)


def _draw_llave(surf, cx, cy, r, color):
    """Llave con anillo y dientes."""
    # Anillo
    ring_r = int(r * 0.2)
    ring_cx = cx - int(r * 0.15)
    ring_cy = cy - int(r * 0.1)
    pygame.draw.circle(surf, color, (ring_cx, ring_cy), ring_r)
    pygame.draw.circle(surf, _lighter(color, 1.4), (ring_cx, ring_cy), ring_r - max(3, r // 8))
    # Vástago
    shaft_y = ring_cy
    shaft_end = cx + int(r * 0.5)
    pygame.draw.line(surf, color, (ring_cx + ring_r, shaft_y), (shaft_end, shaft_y), max(3, r // 8))
    # Dientes
    for i in range(2):
        tx = shaft_end - i * int(r * 0.15)
        pygame.draw.line(surf, color, (tx, shaft_y), (tx, shaft_y + int(r * 0.18)), max(2, r // 9))


def _draw_lampara(surf, cx, cy, r, color):
    """Lámpara de mesa."""
    # Base
    base_w = int(r * 0.4)
    pygame.draw.rect(surf, _darker(color),
                     (cx - base_w // 2, cy + int(r * 0.35), base_w, int(r * 0.1)),
                     border_radius=3)
    # Poste
    pygame.draw.rect(surf, _darker(color, 0.8),
                     (cx - 2, cy - int(r * 0.05), 4, int(r * 0.4)))
    # Pantalla (trapecio)
    shade = [
        (cx - int(r * 0.15), cy - int(r * 0.05)),
        (cx - int(r * 0.35), cy - int(r * 0.45)),
        (cx + int(r * 0.35), cy - int(r * 0.45)),
        (cx + int(r * 0.15), cy - int(r * 0.05)),
    ]
    pygame.draw.polygon(surf, color, shade)
    pygame.draw.polygon(surf, _darker(color, 0.85), shade, 2)
    # Luz
    pygame.draw.circle(surf, _lighter(color, 1.5), (cx, cy - int(r * 0.25)), int(r * 0.08))


def _draw_corazon(surf, cx, cy, r, color):
    """Corazón."""
    points = _heart_points(cx, cy, r * 0.9)
    if len(points) >= 3:
        pygame.draw.polygon(surf, color, points)
        # Brillo
        pygame.draw.circle(surf, _lighter(color),
                           (cx - int(r * 0.12), cy - int(r * 0.15)), int(r * 0.08))


# ═══════════════════════════════════════════════════════════════════════════════
#  REGISTRO DE ÍCONOS
# ═══════════════════════════════════════════════════════════════════════════════

ICON_REGISTRY = {
    # Naturaleza
    "sol": _draw_sol,
    "luna": _draw_luna,
    "flor": _draw_flor,
    "arbol": _draw_arbol,
    "nube": _draw_nube,
    "estrella": _draw_estrella,
    "montana": _draw_montana,
    "gota": _draw_gota,
    # Alimentos
    "manzana": _draw_manzana,
    "pan": _draw_pan,
    "cafe": _draw_cafe,
    "pastel": _draw_pastel,
    "uva": _draw_uva,
    "naranja": _draw_naranja,
    "helado": _draw_helado,
    "galleta": _draw_galleta,
    # Animales
    "gato": _draw_gato,
    "perro": _draw_perro,
    "pajaro": _draw_pajaro,
    "mariposa": _draw_mariposa,
    "pez": _draw_pez,
    "conejo": _draw_conejo,
    "tortuga": _draw_tortuga,
    "abeja": _draw_abeja,
    # Hogar
    "casa": _draw_casa,
    "silla": _draw_silla,
    "taza": _draw_taza,
    "reloj": _draw_reloj,
    "libro": _draw_libro,
    "llave": _draw_llave,
    "lampara": _draw_lampara,
    "corazon": _draw_corazon,
}


def draw_icon(surface, icon_name, cx, cy, size, color):
    """
    Dibuja un ícono por nombre en la superficie indicada.

    Primero intenta cargar un sprite PNG desde assets/sprites/.
    Si no existe, usa el fallback vectorial.

    Args:
        surface: pygame.Surface donde dibujar.
        icon_name: Nombre del ícono (clave del registro).
        cx, cy: Centro del ícono.
        size: Radio aproximado del área de dibujo.
        color: Color principal del ícono (tupla RGB).
    """
    # Intentar usar sprite PNG
    sprite = _load_sprite(icon_name)
    if sprite is not None:
        # Escalar el sprite al tamaño de la carta
        target_size = int(size * 1.8)  # El sprite ocupa ~90% del área
        target_size = max(16, target_size)
        scaled = pygame.transform.smoothscale(sprite, (target_size, target_size))
        rect = scaled.get_rect(center=(cx, cy))
        surface.blit(scaled, rect)
        return

    # Fallback: dibujo vectorial
    func = ICON_REGISTRY.get(icon_name)
    if func:
        func(surface, cx, cy, size, color)
    else:
        # Fallback final: círculo con inicial
        pygame.draw.circle(surface, color, (cx, cy), size // 2)


def get_icon_names_for_theme(theme_key):
    """Retorna la lista de nombres de íconos para un tema dado."""
    from config import THEMES
    theme = THEMES.get(theme_key)
    if theme:
        return theme["icons"]
    return list(ICON_REGISTRY.keys())[:8]
