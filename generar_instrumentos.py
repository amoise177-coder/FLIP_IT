"""
Genera las 12 cartas del tema "instrumentos" y su icono de seleccion.

Reemplaza los dibujos de linea que tenia preparar_temas.py por ilustraciones
con acabado de juego comercial:

  - todo se dibuja a 4x y se reduce con LANCZOS  -> bordes limpios, sin dientes
  - cada pieza lleva degradado vertical (luz arriba, sombra abajo)
  - contorno oscuro constante  -> silueta legible de un vistazo, que es lo que
    pide la guia de accesibilidad visual para ninos con TDAH
  - sombra suave bajo el instrumento y brillo especular arriba
  - paleta pastel unica para las 12 cartas, sin colores estridentes

Se corre con "python generar_instrumentos.py".
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "Assets" / "Images"
DEST = IMG_DIR / "instrumentos"

S = 4                       # factor de supermuestreo
TAM = (220, 200)            # tamaño final de la carta
LIENZO = (TAM[0] * S, TAM[1] * S)

CONTORNO = (62, 48, 42, 255)
GROSOR = 3                  # grosor del contorno en unidades finales

# paleta pastel compartida por todos los instrumentos
MADERA = ((214, 156, 96), (150, 97, 48))
MADERA_OSC = ((150, 105, 68), (96, 64, 40))
ROJO = ((246, 150, 146), (203, 92, 88))
CORAL = ((247, 175, 138), (214, 122, 84))
DORADO = ((250, 214, 132), (206, 154, 52))
DORADO_OSC = ((214, 172, 84), (156, 112, 34))
AZUL = ((160, 205, 240), (86, 143, 197))
VERDE = ((176, 219, 160), (108, 168, 96))
MORADO = ((196, 174, 231), (139, 110, 187))
CREMA = ((255, 250, 240), (232, 219, 197))
PLATA = ((236, 240, 245), (170, 180, 194))
GRAFITO = ((86, 86, 100), (44, 44, 56))
CUERDA = ((248, 242, 226), (206, 194, 170))

FONDO_CARTA = ((255, 253, 247), (243, 234, 219))
BORDE_CARTA = (228, 216, 194, 255)


# ---------------------------------------------------------------------
# utilidades de dibujo
# ---------------------------------------------------------------------

def esc(v):
    """Pasa una coordenada (o una lista de ellas) a la escala de trabajo."""
    if isinstance(v, (list, tuple)):
        return [esc(x) for x in v]
    return v * S


def degradado(size, c1, c2, horizontal=False):
    """Imagen con un degradado lineal de c1 a c2."""
    ancho, alto = size
    n = ancho if horizontal else alto
    barra = Image.new("RGB", (1, n) if not horizontal else (n, 1))
    px = barra.load()
    for i in range(n):
        t = i / max(1, n - 1)
        color = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
        if horizontal:
            px[i, 0] = color
        else:
            px[0, i] = color
    return barra.resize(size, Image.BILINEAR).convert("RGBA")


def figura(lienzo, tipo, coords, colores, radio=0, contorno=CONTORNO,
           grosor=GROSOR, extra=None):
    """Pinta una forma con degradado y contorno oscuro.

    tipo: 'elipse' | 'rect' | 'rrect' | 'poly' | 'pieslice' | 'linea'
    """
    coords_e = esc(coords)
    radio_e = esc(radio)
    grosor_e = max(1, esc(grosor))

    mascara = Image.new("L", lienzo.size, 0)
    dm = ImageDraw.Draw(mascara)
    if tipo == "elipse":
        dm.ellipse(coords_e, fill=255)
    elif tipo == "rect":
        dm.rectangle(coords_e, fill=255)
    elif tipo == "rrect":
        dm.rounded_rectangle(coords_e, radius=radio_e, fill=255)
    elif tipo == "poly":
        dm.polygon([tuple(p) for p in coords_e], fill=255)
    elif tipo == "pieslice":
        dm.pieslice(coords_e, start=extra[0], end=extra[1], fill=255)
    elif tipo == "linea":
        dm.line([tuple(p) for p in coords_e], fill=255, width=esc(extra), joint="curve")
        for p in coords_e:      # puntas redondeadas
            r = esc(extra) / 2
            dm.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=255)

    grad = degradado(lienzo.size, colores[0], colores[1])
    lienzo.paste(grad, (0, 0), mascara)

    if contorno and grosor:
        # el contorno se obtiene del propio borde de la mascara: sale parejo
        # en cualquier forma, incluidas las lineas gruesas
        borde = mascara.filter(ImageFilter.MaxFilter(3))
        for _ in range(max(1, grosor_e // 2)):
            borde = borde.filter(ImageFilter.MaxFilter(3))
        anillo = Image.new("L", lienzo.size, 0)
        anillo.paste(borde)
        anillo = Image.composite(Image.new("L", lienzo.size, 0), anillo, mascara)
        capa = Image.new("RGBA", lienzo.size, contorno)
        lienzo.paste(capa, (0, 0), anillo)


def detalle(lienzo, tipo, coords, color, ancho=1, extra=None):
    """Trazos finos sin contorno (cuerdas, ranuras, brillos)."""
    d = ImageDraw.Draw(lienzo)
    coords_e = esc(coords)
    if tipo == "linea":
        d.line([tuple(p) for p in coords_e], fill=color, width=max(1, esc(ancho)))
    elif tipo == "elipse":
        d.ellipse(coords_e, fill=color)
    elif tipo == "rect":
        d.rectangle(coords_e, fill=color)
    elif tipo == "rrect":
        d.rounded_rectangle(coords_e, radius=esc(extra or 2), fill=color)
    elif tipo == "arco":
        d.arc(coords_e, start=extra[0], end=extra[1], fill=color, width=max(1, esc(ancho)))


def brillo(lienzo, coords, alpha=90):
    """Reflejo blanco suave encima de una pieza."""
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    ImageDraw.Draw(capa).ellipse(esc(coords), fill=(255, 255, 255, alpha))
    capa = capa.filter(ImageFilter.GaussianBlur(esc(1.5)))
    lienzo.alpha_composite(capa)


# ---------------------------------------------------------------------
# los 12 instrumentos  (coordenadas en unidades finales: 220 x 200)
# ---------------------------------------------------------------------


def guitarra(c):
    figura(c, "rrect", [104, 26, 116, 106], MADERA_OSC, radio=5)          # mastil
    figura(c, "rrect", [98, 18, 122, 40], GRAFITO, radio=5)               # clavijero
    figura(c, "elipse", [76, 88, 144, 146], MADERA)                       # caja alta
    figura(c, "elipse", [68, 118, 152, 184], MADERA)                      # caja baja
    figura(c, "elipse", [98, 128, 126, 156], MADERA_OSC)                  # boca
    figura(c, "rrect", [98, 162, 122, 172], MADERA_OSC, radio=3)          # puente
    for i in range(4):
        x = 104 + i * 3.5
        detalle(c, "linea", [(x, 40), (x, 166)], (250, 245, 228, 220), 1)
    for i in range(3):
        detalle(c, "elipse", [95, 22 + i * 5, 101, 27 + i * 5], (236, 238, 242, 255))
        detalle(c, "elipse", [119, 22 + i * 5, 125, 27 + i * 5], (236, 238, 242, 255))
    brillo(c, [80, 96, 104, 128], 70)



def tambor(c):
    figura(c, "linea", [(48, 44), (92, 82)], MADERA, extra=6)             # baquetas
    figura(c, "linea", [(172, 40), (128, 80)], MADERA, extra=6)
    figura(c, "elipse", [40, 34, 58, 52], CREMA)
    figura(c, "elipse", [164, 30, 182, 48], CREMA)
    figura(c, "rrect", [56, 84, 164, 156], ROJO, radio=8)                 # cuerpo
    figura(c, "elipse", [56, 62, 164, 106], CREMA)                        # parche
    figura(c, "rrect", [54, 146, 166, 162], DORADO_OSC, radio=6)          # aro bajo
    for i in range(5):
        x = 60 + i * 24
        detalle(c, "linea", [(x, 100), (x + 12, 146)], (250, 224, 168, 235), 3)
        detalle(c, "linea", [(x + 12, 100), (x, 146)], (250, 224, 168, 180), 2)
    brillo(c, [72, 68, 116, 88], 80)


def piano(c):
    figura(c, "rrect", [38, 62, 182, 88], GRAFITO, radio=6)               # tapa
    figura(c, "rrect", [38, 82, 182, 146], CREMA, radio=6)                # teclas
    ancho = 144 / 8
    for i in range(1, 8):
        x = 38 + i * ancho
        detalle(c, "linea", [(x, 88), (x, 144)], (196, 188, 172, 255), 1)
    for i in (0, 1, 3, 4, 5):
        x = 38 + (i + 1) * ancho - ancho * 0.30
        figura(c, "rrect", [x, 86, x + ancho * 0.60, 122], GRAFITO, radio=2, grosor=2)
    figura(c, "rrect", [34, 142, 186, 156], MADERA_OSC, radio=5)          # base
    figura(c, "rrect", [50, 154, 62, 172], GRAFITO, radio=3)              # patas
    figura(c, "rrect", [158, 154, 170, 172], GRAFITO, radio=3)
    brillo(c, [48, 66, 130, 80], 70)



def violin(c):
    figura(c, "linea", [(44, 66), (172, 150)], CUERDA, extra=5)           # arco (detras)
    figura(c, "rrect", [38, 58, 54, 74], MADERA_OSC, radio=4, grosor=2)
    figura(c, "rrect", [104, 26, 116, 94], MADERA_OSC, radio=5)           # mastil
    figura(c, "poly", [(98, 18), (122, 18), (127, 36), (93, 36)], MADERA_OSC)
    figura(c, "elipse", [80, 80, 140, 128], MADERA)                       # cuerpo alto
    figura(c, "elipse", [74, 110, 146, 174], MADERA)                      # cuerpo bajo
    figura(c, "rrect", [101, 90, 119, 150], MADERA_OSC, radio=6, grosor=2)
    for lado in (-1, 1):
        cx = 110 + lado * 27
        detalle(c, "arco", [cx - 7, 118, cx + 7, 148], (72, 48, 32, 235), 2, (0, 360))
    for i in range(4):
        x = 104 + i * 3.4
        detalle(c, "linea", [(x, 36), (x, 154)], (250, 245, 228, 225), 1)
    brillo(c, [84, 88, 108, 120], 70)


def trompeta(c):
    figura(c, "poly", [(44, 96), (140, 84), (152, 128), (44, 116)], DORADO)   # tubo
    figura(c, "elipse", [126, 62, 190, 150], DORADO)                          # campana
    figura(c, "elipse", [142, 84, 176, 128], DORADO_OSC)
    figura(c, "rrect", [30, 96, 50, 116], DORADO_OSC, radio=6)                # boquilla
    for i in range(3):
        x = 66 + i * 20
        figura(c, "rrect", [x, 62, x + 13, 100], DORADO_OSC, radio=4, grosor=2)
        detalle(c, "rrect", [x + 2, 60, x + 11, 66], (255, 245, 210, 255), extra=2)
    detalle(c, "linea", [(52, 102), (136, 92)], (255, 246, 214, 190), 3)
    brillo(c, [138, 74, 176, 96], 95)


def flauta(c):
    figura(c, "rrect", [30, 92, 176, 114], PLATA, radio=11)
    figura(c, "elipse", [166, 86, 196, 120], PLATA)
    figura(c, "rrect", [36, 90, 52, 116], ((250, 252, 255), (214, 222, 232)),
           radio=6, grosor=2)
    for i in range(6):
        x = 62 + i * 18
        figura(c, "elipse", [x, 94, x + 12, 112], GRAFITO, grosor=2)
    detalle(c, "linea", [(38, 97), (170, 97)], (255, 255, 255, 190), 3)
    brillo(c, [60, 88, 140, 100], 70)



def maracas(c):
    for dx, color in ((-34, CORAL), (34, DORADO)):
        cx = 110 + dx
        figura(c, "rrect", [cx - 7, 108, cx + 7, 180], MADERA_OSC, radio=6)
        figura(c, "elipse", [cx - 29, 48, cx + 29, 120], color)
        for i in range(6):
            ang = i * 1.05 + (0.4 if dx > 0 else 0)
            px = cx + math.cos(ang) * 13
            py = 84 + math.sin(ang) * 20
            detalle(c, "elipse", [px - 3, py - 3, px + 3, py + 3], (255, 255, 255, 175))
        brillo(c, [cx - 20, 58, cx - 2, 78], 90)


def pandereta(c):
    figura(c, "elipse", [46, 46, 174, 158], MADERA)
    figura(c, "elipse", [62, 62, 158, 142], CREMA, grosor=2)
    cx, cy, r = 110, 102, 62
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        px, py = cx + math.cos(rad) * r * 1.05, cy + math.sin(rad) * (r * 0.86) * 1.05
        figura(c, "elipse", [px - 9, py - 9, px + 9, py + 9], DORADO, grosor=2)
        detalle(c, "elipse", [px - 3, py - 3, px + 3, py + 3], (150, 108, 34, 220))
    brillo(c, [70, 60, 116, 86], 85)



def saxofon(c):
    figura(c, "poly", [(66, 34), (98, 24), (103, 44), (71, 54)], GRAFITO)   # boquilla
    figura(c, "linea", [(98, 42), (92, 74), (98, 138)], DORADO, extra=17)   # cuerpo
    figura(c, "linea", [(98, 138), (116, 158), (140, 150)], DORADO, extra=17)  # codo
    figura(c, "poly", [(132, 162), (146, 168), (186, 112), (162, 96)], DORADO)
    figura(c, "elipse", [146, 72, 198, 126], DORADO)                        # campana
    figura(c, "elipse", [158, 86, 186, 114], DORADO_OSC, grosor=2)
    for i in range(4):
        y = 66 + i * 16
        figura(c, "elipse", [88, y, 100, y + 11], DORADO_OSC, grosor=2)
    brillo(c, [86, 52, 100, 92], 80)



def arpa(c):
    figura(c, "rrect", [50, 34, 74, 182], MADERA_OSC, radio=10)            # columna
    figura(c, "linea", [(62, 42), (172, 108)], MADERA, extra=15)           # cuello
    figura(c, "linea", [(62, 174), (172, 118)], MADERA, extra=18)          # caja
    for i in range(9):
        t = i / 8
        x = 72 + t * 92
        detalle(c, "linea", [(x, 48 + t * 60), (x, 170 - t * 52)],
                (250, 244, 226, 230), 1)
    detalle(c, "linea", [(56, 42), (56, 176)], (255, 240, 210, 130), 2)
    brillo(c, [52, 40, 70, 82], 70)


def xilofono(c):
    figura(c, "poly", [(30, 148), (190, 128), (190, 176), (30, 176)], MADERA_OSC)
    colores = [ROJO, CORAL, DORADO, VERDE, AZUL, MORADO]
    x = 38
    for i, color in enumerate(colores):
        alto = 84 - i * 8
        figura(c, "rrect", [x, 150 - alto, x + 22, 154], color, radio=5)
        detalle(c, "elipse", [x + 8, 152 - alto + 8, x + 14, 152 - alto + 14],
                (70, 54, 44, 190))
        x += 25
    figura(c, "linea", [(150, 44), (184, 92)], MADERA, extra=5)               # baqueta
    figura(c, "elipse", [142, 34, 160, 52], CREMA)
    brillo(c, [42, 74, 66, 100], 70)


def acordeon(c):
    figura(c, "rrect", [40, 46, 84, 168], ROJO, radio=8)
    figura(c, "rrect", [136, 46, 180, 168], ROJO, radio=8)
    for i in range(7):
        x = 84 + i * 7.5
        figura(c, "poly", [(x, 52), (x + 7.5, 62), (x + 7.5, 154), (x, 164)],
               CREMA if i % 2 == 0 else ((236, 222, 196), (198, 182, 156)), grosor=2)
    for i in range(3):
        figura(c, "elipse", [50, 72 + i * 26, 66, 88 + i * 26], CREMA, grosor=2)
    for i in range(4):
        figura(c, "rrect", [146, 64 + i * 24, 172, 80 + i * 24], CREMA, radio=3, grosor=2)
    brillo(c, [46, 54, 78, 86], 85)


INSTRUMENTOS = [
    ("guitarra", guitarra), ("tambor", tambor), ("piano", piano),
    ("violin", violin), ("trompeta", trompeta), ("flauta", flauta),
    ("maracas", maracas), ("pandereta", pandereta), ("saxofon", saxofon),
    ("arpa", arpa), ("xilofono", xilofono), ("acordeon", acordeon),
]

# color de la luz de fondo de cada carta, para que las 12 no se vean iguales
HALOS = {
    "guitarra": (255, 226, 190), "tambor": (255, 214, 210), "piano": (222, 228, 240),
    "violin": (252, 228, 196), "trompeta": (255, 238, 196), "flauta": (224, 236, 246),
    "maracas": (255, 226, 200), "pandereta": (250, 232, 200), "saxofon": (255, 236, 194),
    "arpa": (246, 228, 202), "xilofono": (226, 240, 224), "acordeon": (255, 218, 214),
}


# ---------------------------------------------------------------------
# armado de la carta
# ---------------------------------------------------------------------

def carta(nombre, pintar):
    fondo = Image.new("RGBA", LIENZO, (0, 0, 0, 0))
    mascara = Image.new("L", LIENZO, 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [esc(3), esc(3), LIENZO[0] - esc(3), LIENZO[1] - esc(3)], radius=esc(22), fill=255
    )
    fondo.paste(degradado(LIENZO, *FONDO_CARTA), (0, 0), mascara)

    # halo suave detras del instrumento (da profundidad sin ensuciar)
    halo = Image.new("RGBA", LIENZO, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse(
        [esc(46), esc(40), esc(174), esc(164)], fill=HALOS[nombre] + (95,)
    )
    halo = halo.filter(ImageFilter.GaussianBlur(esc(11)))
    fondo.alpha_composite(Image.composite(halo, Image.new("RGBA", LIENZO), mascara))

    # el instrumento se dibuja aparte para poder proyectarle sombra
    pieza = Image.new("RGBA", LIENZO, (0, 0, 0, 0))
    pintar(pieza)

    sombra = Image.new("RGBA", LIENZO, (0, 0, 0, 0))
    sombra.paste((70, 56, 48, 90), (0, 0), pieza.split()[3])
    sombra = sombra.filter(ImageFilter.GaussianBlur(esc(4)))
    fondo.alpha_composite(sombra, (esc(2), esc(5)))
    fondo.alpha_composite(pieza)

    # borde de la carta y brillo superior
    d = ImageDraw.Draw(fondo)
    d.rounded_rectangle(
        [esc(3), esc(3), LIENZO[0] - esc(3), LIENZO[1] - esc(3)],
        radius=esc(22), outline=BORDE_CARTA, width=esc(3),
    )
    lustre = Image.new("RGBA", LIENZO, (0, 0, 0, 0))
    ImageDraw.Draw(lustre).ellipse(
        [esc(-40), esc(-120), esc(260), esc(60)], fill=(255, 255, 255, 34)
    )
    fondo.alpha_composite(Image.composite(lustre, Image.new("RGBA", LIENZO), mascara))

    return fondo.resize(TAM, Image.LANCZOS)


def icono_tema():
    """Circulo del menu: nota musical sobre fondo pastel."""
    size = 240 * 2
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mascara = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mascara).ellipse([0, 0, size, size], fill=255)
    img.paste(degradado((size, size), (255, 226, 178), (232, 168, 120)), (0, 0), mascara)

    d = ImageDraw.Draw(img)
    r = size * 0.30
    cx = cy = size / 2
    # doble corchea
    for dx in (-r * 0.55, r * 0.35):
        d.ellipse([cx + dx - r * 0.30, cy + r * 0.30, cx + dx + r * 0.22, cy + r * 0.78],
                  fill=(72, 54, 46, 255))
        d.rectangle([cx + dx + r * 0.10, cy - r * 0.72, cx + dx + r * 0.22, cy + r * 0.56],
                    fill=(72, 54, 46, 255))
    d.polygon([(cx - r * 0.45, cy - r * 0.72), (cx + r * 0.57, cy - r * 0.90),
               (cx + r * 0.57, cy - r * 0.50), (cx - r * 0.45, cy - r * 0.32)],
              fill=(72, 54, 46, 255))

    lustre = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(lustre).ellipse([-size * 0.2, -size * 0.55, size * 1.1, size * 0.32],
                                   fill=(255, 255, 255, 70))
    img.alpha_composite(Image.composite(lustre, Image.new("RGBA", (size, size)), mascara))
    d.ellipse([5, 5, size - 5, size - 5], outline=(255, 255, 255, 255), width=14)
    return img.resize((240, 240), Image.LANCZOS)


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    (IMG_DIR / "temas").mkdir(parents=True, exist_ok=True)
    for n, (nombre, fn) in enumerate(INSTRUMENTOS, start=1):
        carta(nombre, fn).save(DEST / f"{n}.png")
        print(f"  {n:2}. {nombre}")
    icono_tema().save(IMG_DIR / "temas" / "instrumentos.png")
    print("Listo: 12 cartas de instrumentos + icono del tema.")


if __name__ == "__main__":
    main()
