import os
import pygame

ANCHO, ALTO = 1280, 720
FPS = 60

CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_FUENTES = os.path.join(CARPETA_BASE, "assets", "fonts")

FONDO_ARRIBA = (255, 246, 219)
FONDO_ABAJO = (196, 233, 249)

PALETA_TITULO = [
    (255, 111, 129), (255, 165, 89), (255, 209, 102),
    (120, 200, 150), (86, 190, 200), (158, 140, 214),
]

PALETA_DECORACION = [
    (255, 179, 186, 150), (255, 223, 154, 150),
    (186, 230, 209, 150), (162, 216, 224, 150),
    (196, 181, 232, 150),
]

COLOR_SUBTITULO = (94, 84, 120)
COLOR_TEXTO_OSCURO = (66, 60, 90)

COLOR_BOTON = (86, 199, 165)
COLOR_BOTON_HOVER = (108, 214, 181)
COLOR_BOTON_SOMBRA = (52, 148, 122)
COLOR_TEXTO_BOTON = (255, 255, 255)

COLOR_TARJETA = (255, 255, 255)
COLOR_TARJETA_BORDE = (230, 224, 245)
COLOR_TARJETA_SOMBRA = (210, 205, 225)

COLOR_FLECHA = (160, 150, 190)
COLOR_FLECHA_HOVER = (120, 110, 165)
COLOR_JUGAR = (86, 199, 165)
COLOR_JUGAR_HOVER = (108, 214, 181)
COLOR_JUGAR_SOMBRA = (52, 148, 122)
COLOR_NO_DISPONIBLE = (180, 175, 195)

COLOR_LOGO = (108, 92, 160)

def cargar_fuente(nombre_archivo, tamano):
    ruta = os.path.join(CARPETA_FUENTES, nombre_archivo)
    try:
        return pygame.font.Font(ruta, tamano)
    except (FileNotFoundError, OSError):
        return pygame.font.SysFont("comicsansms,arial", tamano, bold=True)
