import os
import math
import pygame

base_dir = r"c:\Users\DELL\Desktop\launcher taller\enfocate-interfaz\juegos\grupo 6\Proyecto taller de abstraccion eugenio"
fonts_dir = r"c:\Users\DELL\Desktop\launcher taller\enfocate-interfaz\assets\fonts"
assets_dir = os.path.join(base_dir, "assets")

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

ANCHO, ALTO = 1280, 720
surface = pygame.Surface((ANCHO, ALTO))

# 1. Background gradient (teal/mint to warm cream)
for y in range(ALTO):
    t = y / max(ALTO - 1, 1)
    r = int(220 * (1 - t) + 250 * t)
    g = int(245 * (1 - t) + 252 * t)
    b = int(240 * (1 - t) + 238 * t)
    pygame.draw.line(surface, (r, g, b), (0, y), (ANCHO, y))

# Decorative soft background circles
capa_deco = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
pygame.draw.circle(capa_deco, (47, 168, 155, 35), (220, 170), 190)
pygame.draw.circle(capa_deco, (100, 200, 180, 30), (1060, 200), 210)
pygame.draw.circle(capa_deco, (47, 168, 155, 25), (640, 560), 290)
pygame.draw.circle(capa_deco, (80, 190, 160, 30), (380, 520), 140)
pygame.draw.circle(capa_deco, (47, 168, 155, 20), (900, 500), 170)
surface.blit(capa_deco, (0, 0))

# Fonts
try:
    fuente_tit = pygame.font.Font(os.path.join(fonts_dir, "Fredoka-Bold.ttf"), 78)
    fuente_sub = pygame.font.Font(os.path.join(fonts_dir, "Baloo2-SemiBold.ttf"), 28)
    fuente_tag = pygame.font.Font(os.path.join(fonts_dir, "Baloo2-ExtraBold.ttf"), 22)
    fuente_bingo = pygame.font.Font(os.path.join(fonts_dir, "Fredoka-Bold.ttf"), 52)
except Exception:
    fuente_tit = pygame.font.SysFont("Arial", 78, bold=True)
    fuente_sub = pygame.font.SysFont("Arial", 28, bold=True)
    fuente_tag = pygame.font.SysFont("Arial", 22, bold=True)
    fuente_bingo = pygame.font.SysFont("Arial", 52, bold=True)


# Load BINGO letter images if available
bingo_dir = os.path.join(assets_dir, "BINGO")
letras_bingo = ["B", "I", "N", "G", "O"]
colores_letras = [
    (235, 87, 87),   # Rojo cálido
    (255, 180, 60),  # Amarillo dorado
    (47, 168, 155),  # Teal
    (100, 160, 230), # Azul claro
    (180, 120, 210), # Violeta suave
]


def dibujar_bola_bingo(superficie, cx, cy, radio, numero, color, color_borde):
    """Draws a stylized bingo ball with number."""
    # Shadow
    pygame.draw.circle(superficie, (0, 0, 0, 40), (cx + 3, cy + 4), radio)
    # Main ball
    pygame.draw.circle(superficie, color, (cx, cy), radio)
    # White stripe across
    stripe_h = int(radio * 0.55)
    stripe_rect = pygame.Rect(cx - radio + 6, cy - stripe_h // 2, (radio - 6) * 2, stripe_h)
    stripe_surf = pygame.Surface((stripe_rect.width, stripe_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(stripe_surf, (255, 255, 255, 220), stripe_surf.get_rect(), border_radius=stripe_h // 2)
    superficie.blit(stripe_surf, stripe_rect.topleft)
    # Number text
    num_txt = fuente_tag.render(str(numero), True, (60, 60, 75))
    superficie.blit(num_txt, num_txt.get_rect(center=(cx, cy)))
    # Shine highlight
    brillo_rad = radio // 4
    pygame.draw.circle(superficie, (255, 255, 255, 140), (cx - radio // 3, cy - radio // 3), brillo_rad)
    # Border
    pygame.draw.circle(superficie, color_borde, (cx, cy), radio, 3)


def dibujar_carton_bingo(superficie, cx, cy, tamano=300):
    """Draws a stylized bingo card."""
    w, h = tamano, int(tamano * 1.1)
    card = pygame.Surface((w, h), pygame.SRCALPHA)

    # Card background
    pygame.draw.rect(card, (255, 255, 255, 245), (0, 0, w, h), border_radius=16)

    # Header with "BINGO" letters
    header_h = int(h * 0.18)
    header_rect = pygame.Rect(0, 0, w, header_h)
    pygame.draw.rect(card, (47, 168, 155), header_rect,
                     border_top_left_radius=16, border_top_right_radius=16)

    celda_w = w // 5
    for i, (letra, color) in enumerate(zip(letras_bingo, colores_letras)):
        txt = fuente_tag.render(letra, True, (255, 255, 255))
        card.blit(txt, txt.get_rect(center=(celda_w * i + celda_w // 2, header_h // 2)))

    # Grid
    filas, cols = 5, 5
    celda_h = (h - header_h - 8) // filas
    celda_w_grid = (w - 8) // cols

    import random
    random.seed(42)
    for fila in range(filas):
        for col in range(cols):
            gx = 4 + col * celda_w_grid
            gy = header_h + 4 + fila * celda_h
            cell_rect = pygame.Rect(gx, gy, celda_w_grid - 2, celda_h - 2)

            # Alternate cell colors slightly
            if (fila + col) % 2 == 0:
                cell_color = (245, 250, 248)
            else:
                cell_color = (235, 245, 242)

            pygame.draw.rect(card, cell_color, cell_rect, border_radius=6)
            pygame.draw.rect(card, (200, 215, 210), cell_rect, width=1, border_radius=6)

            # Center cell = free/star
            if fila == 2 and col == 2:
                star_txt = fuente_tag.render("★", True, (255, 200, 60))
                card.blit(star_txt, star_txt.get_rect(center=cell_rect.center))
            else:
                num = random.randint(1 + col * 15, 15 + col * 15)
                num_txt = pygame.font.SysFont("Arial", 16, bold=True).render(str(num), True, (80, 90, 100))
                card.blit(num_txt, num_txt.get_rect(center=cell_rect.center))

    # Card border
    pygame.draw.rect(card, (47, 168, 155, 180), (0, 0, w, h), width=3, border_radius=16)

    # Place card on surface with shadow
    sombra = pygame.Surface((w, h), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 35))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, w, h), border_radius=16)
    sombra.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    rect = card.get_rect(center=(cx, cy))
    superficie.blit(sombra, (rect.left + 5, rect.top + 8))
    superficie.blit(card, rect)


# Central container
card_w, card_h = 780, 360
card_bg = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
pygame.draw.rect(card_bg, (255, 255, 255, 230), (0, 0, card_w, card_h), border_radius=32)
pygame.draw.rect(card_bg, (47, 168, 155, 150), (0, 0, card_w, card_h), width=4, border_radius=32)

card_x = (ANCHO - card_w) // 2
card_y = 280

# Shadow
sombra_card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
pygame.draw.rect(sombra_card, (0, 0, 0, 45), (0, 0, card_w, card_h), border_radius=32)
surface.blit(sombra_card, (card_x + 6, card_y + 10))
surface.blit(card_bg, (card_x, card_y))

# Draw bingo card in center
dibujar_carton_bingo(surface, ANCHO // 2, card_y + card_h // 2, tamano=260)

# Draw bingo balls on the sides
bolas_info = [
    (card_x + 60, card_y + 80, 38, 7, colores_letras[0], (200, 60, 60)),
    (card_x + 40, card_y + 200, 32, 23, colores_letras[1], (200, 140, 40)),
    (card_x + 80, card_y + 290, 35, 45, colores_letras[2], (35, 130, 120)),
    (card_x + card_w - 60, card_y + 80, 36, 12, colores_letras[3], (70, 130, 200)),
    (card_x + card_w - 40, card_y + 200, 34, 58, colores_letras[4], (150, 90, 180)),
    (card_x + card_w - 80, card_y + 290, 38, 33, colores_letras[0], (200, 60, 60)),
]
for bx, by, br, bn, bc, bb in bolas_info:
    dibujar_bola_bingo(surface, bx, by, br, bn, bc, bb)

# Title with 3D shadow effect
tit_texto = "BINGO CALMA"
for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 5), (0, 7)]:
    color_s = (20, 100, 90) if oy > 2 else (255, 255, 255)
    s_tit = fuente_tit.render(tit_texto, True, color_s)
    surface.blit(s_tit, s_tit.get_rect(center=(ANCHO // 2 + ox, 105 + oy)))

tit_sup = fuente_tit.render(tit_texto, True, (47, 168, 155))
surface.blit(tit_sup, tit_sup.get_rect(center=(ANCHO // 2, 105)))

# Subtitle pill
sub_text = "Bingo temático y sensorial • Estimulación Cognitiva con 75 conceptos"
sub_sup = fuente_sub.render(sub_text, True, (55, 75, 70))
sub_rect = sub_sup.get_rect(center=(ANCHO // 2, 185))
pill_sub = pygame.Surface((sub_rect.width + 44, sub_rect.height + 16), pygame.SRCALPHA)
pygame.draw.rect(pill_sub, (255, 255, 255, 215), pill_sub.get_rect(), border_radius=20)
surface.blit(pill_sub, pill_sub.get_rect(center=sub_rect.center))
surface.blit(sub_sup, sub_rect)

# Badge "Grupo 6"
badge_text = "GRUPO 6"
badge_sup = fuente_tag.render(badge_text, True, (255, 255, 255))
badge_rect = badge_sup.get_rect(center=(ANCHO // 2, 230))
badge_bg = pygame.Surface((badge_rect.width + 30, badge_rect.height + 10), pygame.SRCALPHA)
pygame.draw.rect(badge_bg, (47, 168, 155, 200), badge_bg.get_rect(), border_radius=14)
surface.blit(badge_bg, badge_bg.get_rect(center=badge_rect.center))
surface.blit(badge_sup, badge_rect)

out_path = os.path.join(base_dir, "portada.png")
pygame.image.save(surface, out_path)
print("Portada BINGO CALMA guardada exitosamente en:", out_path)
