"""
Prepara las cartas y los circulos de seleccion de las 4 tematicas:
spiderman, mickey, cenicienta e instrumentos.

Para spiderman/mickey/cenicienta usa las fotos que el usuario subio
(quedan en una carpeta aparte "fuentes_subidas/", fuera del proyecto,
asi que este script no se puede volver a correr tal cual en otra
maquina: es solo el registro de como se armaron las cartas).

El tema "instrumentos" ya NO se genera aqui: paso a generar_instrumentos.py,
que dibuja las 12 cartas con degradados, contorno y sombra (acabado de
juego comercial). Las funciones de abajo quedan como referencia de la
primera version, pero main() no las usa.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "Assets" / "Images"

FUENTES = Path("/root/.claude/uploads/d2e9fe40-f3fa-596b-a8f4-c9d7fb89e18a")

# clave: (archivo_fuente, numero_de_pareja)
SPIDERMAN = [
    ("15814a5b-image.png", 1),
    ("1125afcd-image.jpg", 2),
    ("debc7f27-image.jpg", 3),
    ("14562517-image.jpg", 4),
    ("50c1a3f0-image.jpg", 5),
    ("ce81c17a-image.jpg", 6),
]

MICKEY = [
    ("5187dcae-image.jpg", 1),   # Pluto
    ("b1196a10-image.jpg", 2),   # Minnie
    ("fec40b01-image.jpg", 3),   # Donald
    ("8010bd0e-image.jpg", 4),   # Donald (cabeza)
    ("113f7c6a-image.jpg", 5),   # moño de Minnie
]

CENICIENTA = [
    ("33db4ecb-image.png", 1),
    ("8e1247d1-image.jpg", 2),
    ("05d57f86-image.jpg", 3),
    ("a97ac523-image.jpg", 4),
]

TAM_CARTA = (220, 200)
FONDO_CARTA = (255, 250, 240, 255)
BORDE_CARTA = (230, 230, 230, 255)


def preparar_carta(nombre_fuente, destino):
    origen = Image.open(FUENTES / nombre_fuente).convert("RGBA")
    lienzo = Image.new("RGBA", TAM_CARTA, (0, 0, 0, 0))
    d = ImageDraw.Draw(lienzo)
    d.rounded_rectangle([3, 3, TAM_CARTA[0] - 3, TAM_CARTA[1] - 3], radius=24, fill=FONDO_CARTA, outline=BORDE_CARTA, width=3)

    copia = origen.copy()
    copia.thumbnail((TAM_CARTA[0] - 20, TAM_CARTA[1] - 20), Image.LANCZOS)
    x = (TAM_CARTA[0] - copia.width) // 2
    y = (TAM_CARTA[1] - copia.height) // 2
    lienzo.paste(copia, (x, y), copia)
    lienzo.save(destino)


def circulo_desde_foto(nombre_fuente, destino, size=240, grosor=8):
    img = Image.open(FUENTES / nombre_fuente).convert("RGBA")
    w, h = img.size
    lado = min(w, h)
    izq, arriba = (w - lado) // 2, (h - lado) // 2
    img = img.crop((izq, arriba, izq + lado, arriba + lado)).resize((size, size), Image.LANCZOS)

    mascara = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mascara).ellipse([0, 0, size, size], fill=255)

    resultado = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    resultado.paste(img, (0, 0), mascara)
    ImageDraw.Draw(resultado).ellipse(
        [grosor // 2, grosor // 2, size - grosor // 2, size - grosor // 2],
        outline=(255, 255, 255, 255), width=grosor,
    )
    resultado.save(destino)


def procesar_tema(lista, carpeta, icono_circulo_fuente):
    carpeta_destino = IMG_DIR / carpeta
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    for archivo, numero in lista:
        preparar_carta(archivo, carpeta_destino / f"{numero}.png")
    circulo_desde_foto(icono_circulo_fuente, IMG_DIR / "temas" / f"{carpeta}.png")


# ---------------------------------------------------------------------
# instrumentos: iconos propios (sin licencia de por medio)
# ---------------------------------------------------------------------

def _tarjeta_vacia():
    img = Image.new("RGBA", TAM_CARTA, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([3, 3, TAM_CARTA[0] - 3, TAM_CARTA[1] - 3], radius=24, fill=FONDO_CARTA, outline=BORDE_CARTA, width=3)
    return img, d


def instr_guitarra(img):
    d = ImageDraw.Draw(img)
    cx, cy = 110, 120
    d.ellipse([cx - 35, cy - 10, cx + 35, cy + 60], fill=(180, 120, 60, 255))
    d.ellipse([cx - 25, cy - 45, cx + 25, cy + 5], fill=(180, 120, 60, 255))
    d.ellipse([cx - 12, cy + 12, cx + 12, cy + 36], fill=(60, 40, 25, 255))
    d.rectangle([cx - 6, cy - 100, cx + 6, cy - 40], fill=(120, 80, 45, 255))
    d.rectangle([cx - 10, cy - 112, cx + 10, cy - 96], fill=(40, 30, 20, 255))
    for i in range(4):
        d.line([cx - 4 + i * 3, cy - 40, cx - 4 + i * 3, cy + 55], fill=(230, 220, 190, 255), width=1)


def instr_tambor(img):
    d = ImageDraw.Draw(img)
    cx, cy = 110, 120
    d.rounded_rectangle([cx - 55, cy - 30, cx + 55, cy + 45], radius=10, fill=(210, 60, 70, 255))
    d.ellipse([cx - 55, cy - 45, cx + 55, cy - 15], fill=(240, 225, 200, 255), outline=(150, 40, 50, 255), width=4)
    for x in (cx - 55, cx - 20, cx + 20, cx + 55 - 6):
        d.line([x, cy - 30, x, cy + 40], fill=(230, 200, 140, 255), width=3)
    d.line([cx - 40, cy - 70, cx - 5, cy - 20], fill=(90, 60, 40, 255), width=6)
    d.line([cx + 40, cy - 75, cx + 5, cy - 15], fill=(90, 60, 40, 255), width=6)


def instr_piano(img):
    d = ImageDraw.Draw(img)
    cx, cy = 110, 115
    d.rounded_rectangle([cx - 70, cy - 30, cx + 70, cy + 40], radius=8, fill=(250, 250, 250, 255), outline=(60, 60, 60, 255), width=3)
    ancho_tecla = 140 / 7
    for i in range(7):
        x0 = cx - 70 + i * ancho_tecla
        d.line([x0, cy - 30, x0, cy + 40], fill=(180, 180, 180, 255), width=2)
    for i in range(6):
        if i % 7 in (1, 2, 4, 5, 6):
            pass
    for i in [0, 1, 3, 4, 5]:
        x0 = cx - 70 + (i + 1) * ancho_tecla - ancho_tecla * 0.28
        d.rectangle([x0, cy - 30, x0 + ancho_tecla * 0.56, cy + 6], fill=(30, 30, 30, 255))


def instr_violin(img):
    d = ImageDraw.Draw(img)
    cx, cy = 110, 130
    d.ellipse([cx - 26, cy - 10, cx + 26, cy + 40], fill=(150, 90, 45, 255))
    d.ellipse([cx - 20, cy - 45, cx + 20, cy], fill=(150, 90, 45, 255))
    d.rectangle([cx - 5, cy - 100, cx + 5, cy - 40], fill=(90, 55, 30, 255))
    d.line([cx - 45, cy - 90, cx + 40, cy + 10], fill=(200, 150, 90, 255), width=4)
    for dx in (-6, 0, 6):
        d.line([cx + dx, cy - 5, cx + dx, cy + 30], fill=(60, 40, 25, 255), width=1)


def instr_trompeta(img):
    d = ImageDraw.Draw(img)
    cx, cy = 90, 120
    d.polygon([(cx, cy - 8), (cx + 90, cy - 22), (cx + 100, cy + 25), (cx, cy + 8)], fill=(230, 190, 50, 255))
    d.ellipse([cx + 78, cy - 30, cx + 130, cy + 34], fill=(230, 190, 50, 255))
    d.ellipse([cx + 92, cy - 12, cx + 116, cy + 14], fill=(180, 140, 20, 255))
    for i in range(3):
        x = cx - 5 + i * 14
        d.rounded_rectangle([x, cy - 40, x + 8, cy - 10], radius=3, fill=(210, 170, 40, 255))


def instr_flauta(img):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 105, 190, 125], radius=10, fill=(210, 210, 215, 255))
    for x in range(60, 180, 20):
        d.ellipse([x - 5, 108, x + 5, 122], fill=(60, 60, 65, 255))
    d.ellipse([180, 100, 205, 130], fill=(230, 230, 235, 255))


def instr_maracas(img):
    d = ImageDraw.Draw(img)
    for dx, color in ((-35, (220, 90, 60, 255)), (35, (230, 170, 50, 255))):
        cx = 110 + dx
        d.ellipse([cx - 24, 90, cx + 24, 150], fill=color)
        d.rectangle([cx - 5, 148, cx + 5, 185], fill=(120, 80, 45, 255))
        for i in range(5):
            ang = i * 1.3
            px = cx + math.cos(ang) * 12
            py = 118 + math.sin(ang) * 18
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255, 180))


def instr_pandereta(img):
    d = ImageDraw.Draw(img)
    cx, cy, r = 110, 115, 55
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(180, 130, 60, 255), width=10)
    d.ellipse([cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18], fill=(250, 240, 210, 200))
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        px, py = cx + math.cos(rad) * r, cy + math.sin(rad) * r
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=(220, 210, 150, 255), outline=(150, 130, 60, 255), width=2)


def instr_saxofon(img):
    d = ImageDraw.Draw(img)
    d.line([100, 60, 100, 130], fill=(220, 180, 60, 255), width=16)
    d.arc([70, 100, 160, 190], start=0, end=180, fill=(220, 180, 60, 255), width=16)
    d.ellipse([135, 150, 175, 190], fill=(220, 180, 60, 255))
    for y in range(70, 120, 14):
        d.ellipse([108, y - 5, 122, y + 5], fill=(180, 140, 30, 255))
    d.polygon([(80, 55), (110, 45), (110, 68), (85, 72)], fill=(40, 30, 20, 255))


def instr_arpa(img):
    d = ImageDraw.Draw(img)
    d.line([70, 50, 150, 175], fill=(160, 110, 60, 255), width=10)
    d.line([70, 50, 70, 175], fill=(160, 110, 60, 255), width=10)
    d.line([70, 175, 150, 175], fill=(120, 80, 45, 255), width=12)
    n = 8
    for i in range(n):
        t = i / (n - 1)
        x0 = 75 + t * 65
        y0 = 55 + t * 10
        d.line([x0, y0, 75, 172], fill=(230, 220, 190, 255), width=1)


def instr_xilofono(img):
    d = ImageDraw.Draw(img)
    colores = [(230, 70, 70, 255), (230, 150, 60, 255), (230, 210, 60, 255), (140, 200, 90, 255),
               (70, 160, 220, 255), (110, 90, 200, 255)]
    x = 40
    for i, color in enumerate(colores):
        alto = 70 - i * 6
        d.rounded_rectangle([x, 150 - alto, x + 20, 150], radius=4, fill=color)
        x += 24


def instr_acordeon(img):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([55, 55, 90, 175], radius=6, fill=(200, 50, 60, 255))
    d.rounded_rectangle([135, 55, 170, 175], radius=6, fill=(200, 50, 60, 255))
    for i in range(6):
        x = 90 + i * 7.5
        d.polygon([(x, 60), (x + 7.5, 68), (x + 7.5, 162), (x, 170)], fill=(230, 210, 170, 255) if i % 2 == 0 else (210, 190, 150, 255))
    for i in range(3):
        d.ellipse([60, 90 + i * 22, 72, 102 + i * 22], fill=(240, 240, 240, 255))


INSTRUMENTOS = [
    instr_guitarra, instr_tambor, instr_piano, instr_violin, instr_trompeta, instr_flauta,
    instr_maracas, instr_pandereta, instr_saxofon, instr_arpa, instr_xilofono, instr_acordeon,
]


def glifo_nota(draw, cx, cy, s, color=(255, 255, 255, 255)):
    draw.ellipse([cx - s * 0.14, cy + s * 0.10, cx + s * 0.14, cy + s * 0.30], fill=color)
    draw.rectangle([cx + s * 0.10, cy - s * 0.30, cx + s * 0.16, cy + s * 0.20], fill=color)
    draw.pieslice([cx + s * 0.08, cy - s * 0.34, cx + s * 0.30, cy - s * 0.10], start=270, end=90, fill=color)


def generar_icono_instrumentos():
    size = 240
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, size - 4, size - 4], fill=(190, 150, 90, 255), outline=(255, 255, 255, 255), width=8)
    glifo_nota(d, 120, 122, 220)
    img.save(IMG_DIR / "temas" / "instrumentos.png")


def main():
    procesar_tema(SPIDERMAN, "spiderman", "debc7f27-image.jpg")
    procesar_tema(MICKEY, "mickey", "b1196a10-image.jpg")
    procesar_tema(CENICIENTA, "cenicienta", "8e1247d1-image.jpg")
    print("Listo: temas spiderman / mickey / cenicienta generados.")
    print("Para el tema instrumentos usa: python generar_instrumentos.py")


if __name__ == "__main__":
    main()
