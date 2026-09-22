import os
import math
import pygame

base_dir = r"c:\Users\DELL\Desktop\launcher taller\enfocate-interfaz\juegos\grupo 11\BallSort\BallSort"
fonts_dir = r"c:\Users\DELL\Desktop\launcher taller\enfocate-interfaz\assets\fonts"
assets_dir = os.path.join(base_dir, "assets")

os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

ANCHO, ALTO = 1280, 720
surface = pygame.Surface((ANCHO, ALTO))

# 1. Background gradient (Soft Cyan/Sky Blue to Warm Soft White)
for y in range(ALTO):
    t = y / max(ALTO - 1, 1)
    r = int(225 * (1 - t) + 255 * t)
    g = int(240 * (1 - t) + 250 * t)
    b = int(255 * (1 - t) + 242 * t)
    pygame.draw.line(surface, (r, g, b), (0, y), (ANCHO, y))

# Decorative soft colored circles floating (representing colorful spheres)
capa_deco = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
colores_bolas = [
    (235, 59, 90),   # Rojo
    (38, 222, 129),  # Verde
    (75, 123, 236),  # Azul
    (250, 130, 49),  # Naranja
    (136, 84, 208),  # Violeta
    (254, 211, 48),  # Amarillo
    (43, 203, 186)   # Turquesa
]

puntos_deco = [
    (120, 140, 70, 0),
    (1160, 160, 80, 2),
    (180, 560, 90, 1),
    (1100, 540, 85, 4),
    (320, 280, 45, 5),
    (960, 310, 50, 3),
]
for x, y, rad, ci in puntos_deco:
    c = colores_bolas[ci % len(colores_bolas)]
    pygame.draw.circle(capa_deco, (*c, 35), (x, y), rad)
    pygame.draw.circle(capa_deco, (*c, 60), (x, y), rad, 3)

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

# Central Illustration: 3 stylized test tubes with spheres
def dibujar_tubo_con_bolas(cx, cy, ancho_tubo=90, alto_tubo=260, bolas=None):
    tubo_surf = pygame.Surface((ancho_tubo + 20, alto_tubo + 30), pygame.SRCALPHA)
    rect_tubo = pygame.Rect(10, 10, ancho_tubo, alto_tubo)
    radio_base = ancho_tubo // 2

    # Tubo de ensayo fondo transparente suave
    pygame.draw.rect(tubo_surf, (255, 255, 255, 140), rect_tubo,
                     border_bottom_left_radius=radio_base, border_bottom_right_radius=radio_base)

    # Dibujar bolas apiladas (de abajo hacia arriba)
    if bolas:
        diametro = ancho_tubo - 14
        radio_bola = diametro // 2
        for idx, col in enumerate(bolas):
            by = rect_tubo.bottom - radio_base - (idx * (diametro + 4))
            bx = rect_tubo.centerx
            
            # Sombra suave de la bola
            pygame.draw.circle(tubo_surf, (0, 0, 0, 30), (bx, by + 3), radio_bola)
            # Bola principal
            pygame.draw.circle(tubo_surf, col, (bx, by), radio_bola)
            # Brillo 3D en la bola
            brillo_rad = radio_bola // 3
            pygame.draw.circle(tubo_surf, (255, 255, 255, 160), (bx - radio_bola // 3, by - radio_bola // 3), brillo_rad)

    # Borde de cristal del tubo
    pygame.draw.rect(tubo_surf, (100, 140, 180, 200), rect_tubo, width=4,
                     border_bottom_left_radius=radio_base, border_bottom_right_radius=radio_base)
    # Borde superior del tubo (labio)
    pygame.draw.rect(tubo_surf, (80, 120, 160, 220), (rect_tubo.left - 4, rect_tubo.top - 2, ancho_tubo + 8, 8), border_radius=4)
    # Reflejo vertical de cristal
    pygame.draw.line(tubo_surf, (255, 255, 255, 180), (rect_tubo.left + 8, rect_tubo.top + 12), (rect_tubo.left + 8, rect_tubo.bottom - radio_base), 3)

    return tubo_surf

# Load icon launcher if present
ico_path = os.path.join(assets_dir, "iconolauncher.png")
ico_img = None
if os.path.exists(ico_path):
    try:
        ico_img = pygame.image.load(ico_path).convert_alpha()
    except Exception as e:
        print("Error al cargar iconolauncher:", e)

# Contenedor central elegante
card_w, card_h = 720, 360
card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
pygame.draw.rect(card, (255, 255, 255, 240), (0, 0, card_w, card_h), border_radius=32)
pygame.draw.rect(card, (75, 123, 236, 160), (0, 0, card_w, card_h), width=4, border_radius=32)

# Si iconolauncher está disponible, colocarlo centrado o integrado
if ico_img:
    # Escalar iconolauncher si es necesario
    iw, ih = ico_img.get_size()
    escala = min(280 / iw, 280 / ih)
    nw, nh = int(iw * escala), int(ih * escala)
    ico_scaled = pygame.transform.smoothscale(ico_img, (nw, nh))
    
    # Dibujar tubo izquierdo y derecho flanqueando al ícono
    t1 = dibujar_tubo_con_bolas(card_w // 2, card_h // 2, 80, 240, [
        (235, 59, 90), (235, 59, 90), (235, 59, 90), (235, 59, 90)
    ])
    t2 = dibujar_tubo_con_bolas(card_w // 2, card_h // 2, 80, 240, [
        (38, 222, 129), (38, 222, 129), (38, 222, 129), (38, 222, 129)
    ])
    
    # Colocar t1 a la izquierda, ícono en el centro, t2 a la derecha
    card.blit(t1, (60, (card_h - t1.get_height()) // 2))
    card.blit(ico_scaled, ((card_w - nw) // 2, (card_h - nh) // 2))
    card.blit(t2, (card_w - 60 - t2.get_width(), (card_h - t2.get_height()) // 2))
else:
    # Dibujar 4 tubos temáticos
    t1 = dibujar_tubo_con_bolas(0, 0, 84, 250, [(235, 59, 90), (235, 59, 90), (235, 59, 90), (235, 59, 90)])
    t2 = dibujar_tubo_con_bolas(0, 0, 84, 250, [(75, 123, 236), (75, 123, 236), (75, 123, 236), (75, 123, 236)])
    t3 = dibujar_tubo_con_bolas(0, 0, 84, 250, [(254, 211, 48), (254, 211, 48), (254, 211, 48), (254, 211, 48)])
    t4 = dibujar_tubo_con_bolas(0, 0, 84, 250, []) # tubo vacío
    tubos = [t1, t2, t3, t4]
    espacio = card_w // (len(tubos) + 1)
    for i, t in enumerate(tubos):
        card.blit(t, (espacio * (i + 1) - t.get_width() // 2, (card_h - t.get_height()) // 2))

# Sombra suave del contenedor central
sombra_card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
pygame.draw.rect(sombra_card, (0, 0, 0, 45), (0, 0, card_w, card_h), border_radius=32)
card_x = (ANCHO - card_w) // 2
card_y = 280
surface.blit(sombra_card, (card_x + 6, card_y + 10))
surface.blit(card, (card_x, card_y))

# Título 3D con estilo idéntico a las demás portadas
tit_texto = "BALL SORT"
for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 5), (0, 7)]:
    color_s = (35, 80, 150) if oy > 2 else (255, 255, 255)
    s_tit = fuente_tit.render(tit_texto, True, color_s)
    surface.blit(s_tit, s_tit.get_rect(center=(ANCHO // 2 + ox, 105 + oy)))

tit_sup = fuente_tit.render(tit_texto, True, (41, 128, 185))
surface.blit(tit_sup, tit_sup.get_rect(center=(ANCHO // 2, 105)))

# Subtitle pill
sub_text = "Organiza las bolitas por color en cada tubo • Rompecabezas de Lógica"
sub_sup = fuente_sub.render(sub_text, True, (65, 75, 95))
sub_rect = sub_sup.get_rect(center=(ANCHO // 2, 180))
pill_sub = pygame.Surface((sub_rect.width + 44, sub_rect.height + 16), pygame.SRCALPHA)
pygame.draw.rect(pill_sub, (255, 255, 255, 215), pill_sub.get_rect(), border_radius=20)
surface.blit(pill_sub, pill_sub.get_rect(center=sub_rect.center))
surface.blit(sub_sup, sub_rect)

# Guardar portada
out_path = os.path.join(base_dir, "portada.png")
pygame.image.save(surface, out_path)
print("Portada BALL SORT guardada exitosamente en:", out_path)
