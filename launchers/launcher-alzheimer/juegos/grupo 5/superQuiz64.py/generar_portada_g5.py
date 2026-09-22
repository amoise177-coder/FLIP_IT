import os
import math
import pygame

base_dir = r"c:\Users\DELL\Desktop\launcher taller\enfocate-interfaz\juegos\grupo 5\superQuiz64.py"
fonts_dir = r"c:\Users\DELL\Desktop\launcher taller\enfocate-interfaz\assets\fonts"
imagenes_dir = os.path.join(base_dir, "assets", "imagenes")

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

ANCHO, ALTO = 1280, 720
surface = pygame.Surface((ANCHO, ALTO))

# 1. Background gradient (warm orange/peach to cream)
for y in range(ALTO):
    t = y / max(ALTO - 1, 1)
    r = int(255 * (1 - t) + 255 * t)
    g = int(235 * (1 - t) + 248 * t)
    b = int(220 * (1 - t) + 240 * t)
    pygame.draw.line(surface, (r, g, b), (0, y), (ANCHO, y))

# Decorative soft background circles
capa_deco = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
pygame.draw.circle(capa_deco, (255, 160, 80, 40), (200, 150), 180)
pygame.draw.circle(capa_deco, (255, 200, 100, 35), (1080, 180), 200)
pygame.draw.circle(capa_deco, (255, 120, 50, 30), (640, 550), 280)
pygame.draw.circle(capa_deco, (255, 180, 60, 25), (350, 500), 150)
pygame.draw.circle(capa_deco, (255, 140, 90, 30), (950, 480), 160)
surface.blit(capa_deco, (0, 0))

# Fonts
try:
    fuente_tit = pygame.font.Font(os.path.join(fonts_dir, "Fredoka-Bold.ttf"), 78)
    fuente_sub = pygame.font.Font(os.path.join(fonts_dir, "Baloo2-SemiBold.ttf"), 28)
    fuente_tag = pygame.font.Font(os.path.join(fonts_dir, "Baloo2-ExtraBold.ttf"), 22)
except Exception:
    fuente_tit = pygame.font.SysFont("Arial", 78, bold=True)
    fuente_sub = pygame.font.SysFont("Arial", 28, bold=True)
    fuente_tag = pygame.font.SysFont("Arial", 22, bold=True)


# Helper: draw a speaker icon with sound waves
def dibujar_altavoz(superficie, cx, cy, tamano=60, color=(255, 120, 50)):
    """Draws a stylized speaker icon with emanating sound waves."""
    s = tamano
    # Speaker body
    body_w = int(s * 0.35)
    body_h = int(s * 0.45)
    body_rect = pygame.Rect(cx - s // 2, cy - body_h // 2, body_w, body_h)
    pygame.draw.rect(superficie, color, body_rect, border_radius=4)

    # Speaker cone (triangle)
    cone_pts = [
        (body_rect.right, body_rect.top),
        (body_rect.right + int(s * 0.3), cy - int(s * 0.4)),
        (body_rect.right + int(s * 0.3), cy + int(s * 0.4)),
        (body_rect.right, body_rect.bottom),
    ]
    pygame.draw.polygon(superficie, color, cone_pts)

    # Sound waves (arcs)
    wave_x = body_rect.right + int(s * 0.35)
    for i, alpha in enumerate([200, 150, 100]):
        radio = int(s * 0.25) + i * int(s * 0.18)
        wave_surf = pygame.Surface((radio * 2 + 4, radio * 2 + 4), pygame.SRCALPHA)
        pygame.draw.arc(wave_surf, (*color, alpha),
                        (2, 2, radio * 2, radio * 2),
                        -math.pi / 3, math.pi / 3, max(3, int(s * 0.06)))
        superficie.blit(wave_surf, (wave_x - 2, cy - radio - 2))


# Helper: create a rounded image card
def crear_carta_imagen(ruta_img, nombre, color_borde=(255, 140, 80), w=200, h=200):
    card = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(card, (255, 255, 255, 240), (0, 0, w, h), border_radius=20)
    pygame.draw.rect(card, color_borde, (0, 0, w, h), width=4, border_radius=20)

    if os.path.exists(ruta_img):
        try:
            im = pygame.image.load(ruta_img).convert_alpha()
            iw = w - 20
            ih = h - 56
            im_sc = pygame.transform.smoothscale(im, (iw, ih))
            mask = pygame.Surface((iw, ih), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, iw, ih), border_radius=14)
            im_sc.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            card.blit(im_sc, (10, 10))
        except Exception as e:
            print("Error cargando imagen:", e)

    # Name at bottom
    txt = fuente_tag.render(nombre.upper(), True, (60, 64, 75))
    card.blit(txt, txt.get_rect(center=(w // 2, h - 24)))
    return card


def blit_sombra(dest, surf, cx, cy, ang=0):
    surf_rot = pygame.transform.rotate(surf, ang) if ang != 0 else surf
    sombra = pygame.Surface(surf_rot.get_size(), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 40))
    sombra.blit(surf_rot, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    rect = surf_rot.get_rect(center=(cx, cy))
    dest.blit(sombra, (rect.left + 5, rect.top + 8))
    dest.blit(surf_rot, rect)


# Central container card
card_w, card_h = 800, 350
card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
pygame.draw.rect(card, (255, 255, 255, 235), (0, 0, card_w, card_h), border_radius=32)
pygame.draw.rect(card, (255, 140, 70, 160), (0, 0, card_w, card_h), width=4, border_radius=32)

# Load animal images from the game's assets to showcase
animales = ["gato", "perro", "leon", "guitarra"]
colores_bordes = [(255, 120, 50), (255, 165, 89), (255, 100, 70), (255, 180, 100)]
cartas = []
for nombre, col_b in zip(animales, colores_bordes):
    ruta = os.path.join(imagenes_dir, f"{nombre}.jpg")
    carta = crear_carta_imagen(ruta, nombre, col_b, w=160, h=170)
    cartas.append(carta)

# Place cards inside the container
espacio = card_w // (len(cartas) + 1)
for i, c in enumerate(cartas):
    x = espacio * (i + 1) - c.get_width() // 2
    y = (card_h - c.get_height()) // 2
    card.blit(c, (x, y))

# Shadow and container placement
sombra_card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
pygame.draw.rect(sombra_card, (0, 0, 0, 45), (0, 0, card_w, card_h), border_radius=32)
card_x = (ANCHO - card_w) // 2
card_y = 280
surface.blit(sombra_card, (card_x + 6, card_y + 10))
surface.blit(card, (card_x, card_y))

# Draw speaker icons on sides
dibujar_altavoz(surface, 130, 420, tamano=80, color=(255, 140, 70))
dibujar_altavoz(surface, ANCHO - 130, 420, tamano=80, color=(255, 160, 90))

# Musical note decorations
notas = [(180, 300, 30), (1100, 330, 35), (300, 600, 25), (980, 590, 28)]
for nx, ny, ns in notas:
    nota_capa = pygame.Surface((ns * 3, ns * 4), pygame.SRCALPHA)
    pygame.draw.circle(nota_capa, (255, 140, 70, 120), (ns, ns * 3), ns)
    pygame.draw.line(nota_capa, (255, 140, 70, 120), (ns + ns - 2, ns * 3), (ns + ns - 2, ns // 2), max(3, ns // 5))
    surface.blit(nota_capa, (nx - ns, ny - ns * 2))

# Title with 3D shadow effect
tit_texto = "SUPER QUIZ 64"
for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 5), (0, 7)]:
    color_s = (180, 70, 10) if oy > 2 else (255, 255, 255)
    s_tit = fuente_tit.render(tit_texto, True, color_s)
    surface.blit(s_tit, s_tit.get_rect(center=(ANCHO // 2 + ox, 105 + oy)))

tit_sup = fuente_tit.render(tit_texto, True, (255, 120, 50))
surface.blit(tit_sup, tit_sup.get_rect(center=(ANCHO // 2, 105)))

# Subtitle pill
sub_text = "Escucha el sonido y asocia con la imagen correcta • Asociación Auditiva"
sub_sup = fuente_sub.render(sub_text, True, (85, 65, 50))
sub_rect = sub_sup.get_rect(center=(ANCHO // 2, 185))
pill_sub = pygame.Surface((sub_rect.width + 44, sub_rect.height + 16), pygame.SRCALPHA)
pygame.draw.rect(pill_sub, (255, 255, 255, 215), pill_sub.get_rect(), border_radius=20)
surface.blit(pill_sub, pill_sub.get_rect(center=sub_rect.center))
surface.blit(sub_sup, sub_rect)

# Badge "Grupo 5"
badge_text = "GRUPO 5"
badge_sup = fuente_tag.render(badge_text, True, (255, 255, 255))
badge_rect = badge_sup.get_rect(center=(ANCHO // 2, 230))
badge_bg = pygame.Surface((badge_rect.width + 30, badge_rect.height + 10), pygame.SRCALPHA)
pygame.draw.rect(badge_bg, (255, 120, 50, 200), badge_bg.get_rect(), border_radius=14)
surface.blit(badge_bg, badge_bg.get_rect(center=badge_rect.center))
surface.blit(badge_sup, badge_rect)

out_path = os.path.join(base_dir, "portada.png")
pygame.image.save(surface, out_path)
print("Portada SUPER QUIZ 64 guardada exitosamente en:", out_path)
