"""
Genera los assets genericos del juego (los que no dependen de la tematica):

  Assets/Images/fondo.png       fondo del tablero de juego
  Assets/Images/fondo_menu.png  fondo del menu
  Assets/Images/volteada.png    reverso de las cartas

Criterio (accesibilidad visual para ninos con TDAH):
  - paleta pastel de bajo contraste en el fondo, para que las cartas sean
    siempre el elemento con mas contraste de la pantalla
  - nada de texturas finas ni patrones repetitivos que generen ruido visual
  - formas grandes, suaves y desenfocadas: dan profundidad sin llamar la atencion

Se corre con "python generar_assets.py".
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "Assets" / "Images"

ANCHO, ALTO = 1280, 720


def degradado_vertical(size, c1, c2):
    ancho, alto = size
    barra = Image.new("RGB", (1, alto))
    px = barra.load()
    for y in range(alto):
        t = y / max(1, alto - 1)
        px[0, y] = tuple(int(c1[k] + (c2[k] - c1[k]) * t) for k in range(3))
    return barra.resize(size, Image.BILINEAR)


def manchas(img, circulos, desenfoque=90):
    """Manchas de color grandes y muy desenfocadas."""
    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for cx, cy, r, color, alpha in circulos:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    capa = capa.filter(ImageFilter.GaussianBlur(desenfoque))
    img.alpha_composite(capa)


def vineta(img, fuerza=48):
    """Oscurecimiento suave en las esquinas: centra la mirada en el tablero."""
    capa = Image.new("L", img.size, 0)
    ImageDraw.Draw(capa).ellipse(
        [-img.width * 0.22, -img.height * 0.30,
         img.width * 1.22, img.height * 1.30], fill=255
    )
    capa = capa.filter(ImageFilter.GaussianBlur(140))
    sombra = Image.new("RGBA", img.size, (110, 96, 130, fuerza))
    img.alpha_composite(Image.composite(Image.new("RGBA", img.size, (0, 0, 0, 0)),
                                        sombra, capa))


def fondo_juego():
    """Lavanda muy claro -> crema durazno. Tranquilo y con poco contraste."""
    img = degradado_vertical((ANCHO, ALTO), (238, 236, 250), (252, 240, 232)).convert("RGBA")
    manchas(img, [
        (250, 140, 300, (206, 222, 250), 120),
        (1040, 180, 280, (250, 224, 226), 110),
        (640, 640, 420, (232, 240, 226), 100),
        (120, 600, 240, (244, 232, 246), 120),
    ])
    vineta(img, 42)
    img.convert("RGB").save(IMG_DIR / "fondo.png")


def fondo_menu():
    """Un poco mas colorido que el tablero, pero igual de suave."""
    img = degradado_vertical((ANCHO, ALTO), (245, 234, 248), (226, 240, 250)).convert("RGBA")
    manchas(img, [
        (200, 120, 340, (252, 218, 228), 140),
        (1080, 120, 320, (216, 226, 252), 140),
        (980, 620, 380, (226, 246, 228), 120),
        (240, 620, 300, (254, 236, 214), 130),
    ])
    # burbujas grandes, apenas visibles: profundidad sin ruido visual
    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for cx, cy, r in [(150, 260, 70), (1140, 330, 55), (420, 90, 40),
                      (900, 90, 32), (700, 660, 48), (330, 560, 36)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 60))
    capa = capa.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(capa)
    vineta(img, 34)
    img.convert("RGB").save(IMG_DIR / "fondo_menu.png")


def carta_volteada():
    """Reverso de la carta: morado pastel, borde blanco y un destello central."""
    s = 4
    w, h = 240, 220
    lienzo = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))

    mascara = Image.new("L", lienzo.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle(
        [6 * s, 6 * s, (w - 6) * s, (h - 6) * s], radius=26 * s, fill=255
    )
    lienzo.paste(degradado_vertical(lienzo.size, (186, 168, 232), (140, 122, 198)).convert("RGBA"),
                 (0, 0), mascara)

    # aro concentrico apenas marcado
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    cx, cy = w * s / 2, h * s / 2
    for r in (86 * s, 62 * s):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 55), width=5 * s)
    d.ellipse([cx - 44 * s, cy - 44 * s, cx + 44 * s, cy + 44 * s], fill=(255, 255, 255, 42))
    lienzo.alpha_composite(Image.composite(capa, Image.new("RGBA", lienzo.size), mascara))

    # destello de cuatro puntas al centro
    d = ImageDraw.Draw(lienzo)
    b = 40 * s
    d.polygon([(cx, cy - b), (cx + b * 0.24, cy - b * 0.24), (cx + b, cy),
               (cx + b * 0.24, cy + b * 0.24), (cx, cy + b),
               (cx - b * 0.24, cy + b * 0.24), (cx - b, cy),
               (cx - b * 0.24, cy - b * 0.24)], fill=(255, 255, 255, 235))

    # brillo superior y borde blanco
    lustre = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    ImageDraw.Draw(lustre).ellipse(
        [-60 * s, -140 * s, (w + 60) * s, 66 * s], fill=(255, 255, 255, 46)
    )
    lienzo.alpha_composite(Image.composite(lustre, Image.new("RGBA", lienzo.size), mascara))
    ImageDraw.Draw(lienzo).rounded_rectangle(
        [6 * s, 6 * s, (w - 6) * s, (h - 6) * s], radius=26 * s,
        outline=(255, 255, 255, 235), width=6 * s
    )

    lienzo.resize((w, h), Image.LANCZOS).save(IMG_DIR / "volteada.png")


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    fondo_juego()
    fondo_menu()
    carta_volteada()
    print("Listo: fondo.png, fondo_menu.png y volteada.png generados en Assets/Images")


if __name__ == "__main__":
    main()
