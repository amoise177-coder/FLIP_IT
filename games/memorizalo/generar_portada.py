"""
Genera la portada que el launcher 'enfocate' muestra en su menu:

    Assets/cover/launcher_cover.png
    Assets/cover/launcher_cover      (misma imagen sin extension, por si el
                                      escaner busca el nombre exacto del README)

Se dibuja con pygame reusando ui.py y los assets del juego, asi que la
portada queda exactamente con la misma paleta y tipografia que el menu.

Se corre con "python generar_portada.py".
"""

import os
import shutil
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")   # no hace falta ventana real

import pygame

import constantes
import ui

BASE_DIR = Path(__file__).resolve().parent
COVER_DIR = BASE_DIR / "Assets" / "cover"

ANCHO, ALTO = 640, 360


def _carta(ruta, tam, angulo):
    """Carga una imagen de carta, la escala y la inclina."""
    img = pygame.image.load(str(ruta)).convert_alpha()
    img = pygame.transform.smoothscale(img, tam)
    return pygame.transform.rotozoom(img, angulo, 1.0)


def generar():
    pygame.init()
    pygame.display.set_mode((ANCHO, ALTO))
    lienzo = pygame.Surface((ANCHO, ALTO))

    fondo = pygame.transform.smoothscale(constantes.get_fondo_menu(), (ANCHO, ALTO))
    lienzo.blit(fondo, (0, 0))

    # tres cartas en abanico: dos destapadas y una boca abajo
    instr = constantes.IMG_DIR / "instrumentos"
    piezas = [
        (constantes.IMG_DIR / "volteada.png", -14, (150, 300)),
        (instr / "1.png", 4, (320, 268)),
        (instr / "11.png", 16, (492, 300)),
    ]
    for ruta, angulo, centro in piezas:
        if not ruta.exists():
            continue
        carta = _carta(ruta, (132, 120), angulo)
        rect = carta.get_rect(center=centro)
        sombra = ui.sombra_redondeada((rect.width - 16, rect.height - 16), 18,
                                      alpha=90, expansion=12)
        lienzo.blit(sombra, (rect.x - 4, rect.y + 6))
        lienzo.blit(carta, rect)

    # placa con el titulo, igual que en el menu
    f_titulo = ui.fuente(58, negrita=True)
    f_sub = ui.fuente(17, negrita=True)
    titulo = f_titulo.render("MEMORÍZALO", True, ui.TEXTO)
    placa = pygame.Rect(0, 0, titulo.get_width() + 76, titulo.get_height() + 30)
    placa.center = (ANCHO // 2, 104)

    exp = 14
    lienzo.blit(ui.sombra_redondeada(placa.size, 26, alpha=90, expansion=exp),
                (placa.x - exp, placa.y - exp + 8))
    lienzo.blit(ui.degradado_redondeado(placa.size, (255, 255, 255), (233, 226, 248), 26),
                placa.topleft)
    pygame.draw.rect(lienzo, ui.BLANCO, placa, width=3, border_radius=26)
    ui.texto_centrado(lienzo, "MEMORÍZALO", f_titulo, ui.TEXTO,
                      (placa.centerx, placa.centery - 3), sombra=ui.BLANCO)
    ui.texto_centrado(lienzo, "JUEGO DE MEMORIA", f_sub, ui.TEXTO_SUAVE,
                      (ANCHO // 2, placa.bottom + 22))

    COVER_DIR.mkdir(parents=True, exist_ok=True)
    destino = COVER_DIR / "launcher_cover.png"
    pygame.image.save(lienzo, str(destino))
    # copia sin extension: el README del launcher nombra la ruta asi
    shutil.copyfile(destino, COVER_DIR / "launcher_cover")
    pygame.quit()
    print("Listo:", destino.relative_to(BASE_DIR), "(+ copia sin extension)")


if __name__ == "__main__":
    generar()
