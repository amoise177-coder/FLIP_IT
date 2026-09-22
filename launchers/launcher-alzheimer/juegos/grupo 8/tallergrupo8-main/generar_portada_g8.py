import os
import math
import pygame

base_dir = r"c:\Users\DELL\Desktop\launcher taller\enfocate-interfaz\juegos\grupo 8\tallergrupo8-main"
fonts_dir = r"c:\Users\DELL\Desktop\launcher taller\enfocate-interfaz\assets\fonts"
estados_dir = os.path.join(base_dir, "assets", "cartas", "estados")

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

ANCHO, ALTO = 1280, 720
surface = pygame.Surface((ANCHO, ALTO))

# 1. Warm purple/blue to cream gradient
for y in range(ALTO):
    t = y / max(ALTO - 1, 1)
    r = int(240 * (1 - t) + 255 * t)
    g = int(244 * (1 - t) + 248 * t)
    b = int(255 * (1 - t) + 235 * t)
    pygame.draw.line(surface, (r, g, b), (0, y), (ANCHO, y))

# Decorative soft background shapes
capa_deco = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
pygame.draw.circle(capa_deco, (155, 89, 182, 35), (250, 160), 200)
pygame.draw.circle(capa_deco, (52, 152, 219, 35), (1050, 200), 220)
pygame.draw.circle(capa_deco, (46, 204, 113, 30), (640, 520), 300)
surface.blit(capa_deco, (0, 0))

# Fonts
try:
    fuente_tit = pygame.font.Font(os.path.join(fonts_dir, "Fredoka-Bold.ttf"), 74)
    fuente_sub = pygame.font.Font(os.path.join(fonts_dir, "Baloo2-SemiBold.ttf"), 30)
    fuente_tag = pygame.font.Font(os.path.join(fonts_dir, "Baloo2-ExtraBold.ttf"), 22)
except Exception:
    fuente_tit = pygame.font.SysFont("Arial", 74, bold=True)
    fuente_sub = pygame.font.SysFont("Arial", 30, bold=True)
    fuente_tag = pygame.font.SysFont("Arial", 22, bold=True)

# Helper function to create a memory card
def crear_carta_preview(ruta_img, nombre_estado, color_borde=(52, 152, 219), w=230, h=290):
    card = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(card, (255, 255, 255), (0, 0, w, h), border_radius=22)
    pygame.draw.rect(card, color_borde, (0, 0, w, h), width=4, border_radius=22)

    if os.path.exists(ruta_img):
        try:
            im = pygame.image.load(ruta_img).convert_alpha()
            iw = w - 24
            ih = h - 72
            im_sc = pygame.transform.smoothscale(im, (iw, ih))
            mask = pygame.Surface((iw, ih), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), (0, 0, iw, ih), border_radius=16)
            im_sc.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            card.blit(im_sc, (12, 14))
        except Exception as e:
            print("Error cargando carta:", e)

    # Name at bottom
    txt = fuente_tag.render(nombre_estado.upper(), True, (60, 64, 75))
    card.blit(txt, txt.get_rect(center=(w // 2, h - 30)))
    return card

# Back of card (mystery card)
def crear_dorso_carta(w=230, h=290):
    card = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(card, (149, 165, 166), (0, 0, w, h), border_radius=22)
    pygame.draw.rect(card, (45, 55, 72), (0, 0, w, h), width=4, border_radius=22)
    pygame.draw.circle(card, (255, 255, 255), (w // 2, h // 2), 36, 4)
    pygame.draw.circle(card, (255, 255, 255), (w // 2, h // 2), 14)
    return card

img_merida = os.path.join(estados_dir, "merida.jpeg")
img_zulia = os.path.join(estados_dir, "zulia.jpeg")
img_caracas = os.path.join(estados_dir, "caracas.jpeg")

carta1 = crear_carta_preview(img_merida, "Mérida", (46, 204, 113))
carta2 = crear_carta_preview(img_zulia, "Zulia", (52, 152, 219))
carta3 = crear_carta_preview(img_caracas, "Caracas", (230, 126, 34))
carta_dorso = crear_dorso_carta()

# Shadows
def blit_sombra(dest, surf, cx, cy, ang=0):
    surf_rot = pygame.transform.rotate(surf, ang) if ang != 0 else surf
    sombra = pygame.Surface(surf_rot.get_size(), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 40))
    sombra.blit(surf_rot, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    rect = surf_rot.get_rect(center=(cx, cy))
    dest.blit(sombra, (rect.left + 5, rect.top + 8))
    dest.blit(surf_rot, rect)

# Blit 4 cards fan layout
blit_sombra(surface, carta_dorso, 280, 480, ang=12)
blit_sombra(surface, carta1, 520, 465, ang=-5)
blit_sombra(surface, carta2, 760, 465, ang=4)
blit_sombra(surface, carta3, 1000, 480, ang=-10)

# Title
tit_texto = "JUEGO DE MEMORIA"
# 3D shadow
for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 5), (0, 7)]:
    color_s = (100, 50, 130) if oy > 2 else (255, 255, 255)
    s_tit = fuente_tit.render(tit_texto, True, color_s)
    surface.blit(s_tit, s_tit.get_rect(center=(ANCHO // 2 + ox, 115 + oy)))

tit_sup = fuente_tit.render(tit_texto, True, (155, 89, 182))
surface.blit(tit_sup, tit_sup.get_rect(center=(ANCHO // 2, 115)))

# Subtitle pill
sub_text = "Encuentra las parejas de cartas iguales • Estados de Venezuela"
sub_sup = fuente_sub.render(sub_text, True, (70, 80, 100))
sub_rect = sub_sup.get_rect(center=(ANCHO // 2, 185))
pill_sub = pygame.Surface((sub_rect.width + 44, sub_rect.height + 16), pygame.SRCALPHA)
pygame.draw.rect(pill_sub, (255, 255, 255, 210), pill_sub.get_rect(), border_radius=20)
surface.blit(pill_sub, pill_sub.get_rect(center=sub_rect.center))
surface.blit(sub_sup, sub_rect)

out_path = os.path.join(base_dir, "portada.png")
pygame.image.save(surface, out_path)
print("Portada Grupo 8 guardada exitosamente en:", out_path)
