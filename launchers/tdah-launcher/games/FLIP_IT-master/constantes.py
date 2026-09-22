import pygame
from pathlib import Path

# No inicializar pygame aquí, dejar que el launcher lo haga
# pygame.init()

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "Assets"
IMG_DIR = ASSETS_DIR / "Images"
SND_DIR = ASSETS_DIR / "Sonido"
SFX_DIR = SND_DIR / "sfx"
FONT_DIR = ASSETS_DIR / "fonts"

# Temas de cartas disponibles. Cada carpeta tiene imagenes 1.png, 2.png...
# Con 6 parejas basta con que cada tema tenga 6 imagenes; si tiene menos,
# crear_cartas() reutiliza las que hay en vez de dejar huecos.
IMG_TEMAS = {
    "spiderman": IMG_DIR / "spiderman",
    "mickey": IMG_DIR / "mickey",
    "cenicienta": IMG_DIR / "cenicienta",
    "instrumentos": IMG_DIR / "instrumentos",
}

# Info para pintar la tarjeta de cada tema en el menu de seleccion.
# "color" se usa como respaldo si el icono en Assets/Images/temas no existe.
TEMAS_INFO = {
    "spiderman": {
        "nombre": "Spiderman",
        "icono": IMG_DIR / "temas" / "spiderman.png",
        "color": (236, 156, 174),
    },
    "mickey": {
        "nombre": "Mickey y Amigos",
        "icono": IMG_DIR / "temas" / "mickey.png",
        "color": (116, 172, 224),
    },
    "cenicienta": {
        "nombre": "Cenicienta",
        "icono": IMG_DIR / "temas" / "cenicienta.png",
        "color": (182, 162, 222),
    },
    "instrumentos": {
        "nombre": "Instrumentos",
        "icono": IMG_DIR / "temas" / "instrumentos.png",
        "color": (240, 174, 144),
    },
}

TEMA_CARTAS = "instrumentos"  # tema de respaldo si algo arranca el juego sin pasar por el menu

ANCHO = 1280
ALTO = 720
FPS = 60


# ---------------------------------------------------------------------
# Modo de juego unico
# ---------------------------------------------------------------------
# El juego tiene un solo modo: 6 parejas en una cuadricula de 4x3 (12
# cartas) y sin limite de tiempo. Es la configuracion recomendada para
# ninos con TDAH: la partida dura poco, entra completa en pantalla sin
# tener que buscar cartas lejanas, y sin reloj no hay presion ni pantalla
# de derrota, solo el conteo de intentos como referencia.

MODO = {
    "num_pares": 6,
    "ancho_alto": (170, 155),
    "margen": 26,
    "columnas": 4,
    "filas": 3,
    "tiempo": None,      # None = sin limite
}

# Se conserva el nombre DIFICULTAD porque otros modulos (y el launcher)
# lo importan; ahora tiene una sola entrada.
DIFICULTAD = {"normal": MODO}


# ---------------------------------------------------------------------
# Funciones para cargar assets de forma diferida
# ---------------------------------------------------------------------

def _fondo_degradado(c1=(238, 236, 250), c2=(252, 240, 232)):
    """Respaldo por si falta el PNG: degradado pastel dibujado a mano."""
    surf = pygame.Surface((ANCHO, ALTO))
    for y in range(ALTO):
        t = y / (ALTO - 1)
        color = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        pygame.draw.line(surf, color, (0, y), (ANCHO, y))
    return surf


def get_fondo():
    """Fondo del tablero de juego."""
    if not hasattr(get_fondo, '_cached'):
        try:
            get_fondo._cached = pygame.image.load(str(IMG_DIR / "fondo.png")).convert()
        except (FileNotFoundError, pygame.error):
            get_fondo._cached = _fondo_degradado()
    return get_fondo._cached


def get_fondo_menu():
    """Fondo del menu (un poco mas colorido que el del tablero)."""
    if not hasattr(get_fondo_menu, '_cached'):
        try:
            get_fondo_menu._cached = pygame.image.load(
                str(IMG_DIR / "fondo_menu.png")).convert()
        except (FileNotFoundError, pygame.error):
            get_fondo_menu._cached = _fondo_degradado((245, 234, 248), (226, 240, 250))
    return get_fondo_menu._cached


def get_carta_volteada():
    if not hasattr(get_carta_volteada, '_cached'):
        try:
            get_carta_volteada._cached = pygame.image.load(
                str(IMG_DIR / "volteada.png")).convert_alpha()
        except (FileNotFoundError, pygame.error):
            surf = pygame.Surface((240, 220), pygame.SRCALPHA)
            pygame.draw.rect(surf, MORADO_P, surf.get_rect(), border_radius=26)
            pygame.draw.rect(surf, BLANCO, surf.get_rect(), width=6, border_radius=26)
            get_carta_volteada._cached = surf
    return get_carta_volteada._cached


def get_icono_tema(tema):
    """Icono redondo para la tarjeta de seleccion de tema. Si no existe el
    PNG en Assets/Images/temas, dibuja un circulo de color como respaldo
    para que el menu nunca se rompa por falta de un archivo."""
    if not hasattr(get_icono_tema, '_cache'):
        get_icono_tema._cache = {}
    if tema not in get_icono_tema._cache:
        info = TEMAS_INFO[tema]
        try:
            get_icono_tema._cache[tema] = pygame.image.load(
                str(info["icono"])).convert_alpha()
        except (FileNotFoundError, pygame.error):
            surf = pygame.Surface((240, 240), pygame.SRCALPHA)
            pygame.draw.circle(surf, info["color"], (120, 120), 118)
            pygame.draw.circle(surf, BLANCO, (120, 120), 118, 6)
            get_icono_tema._cache[tema] = surf
    return get_icono_tema._cache[tema]


# ---------------------------------------------------------------------
# Colores (paleta pastel unica para todo el juego)
# ---------------------------------------------------------------------

BLANCO = (255, 255, 255)
TEXTO_OSCURO = (72, 60, 88)
TEXTO_SUAVE = (126, 116, 142)

MORADO_P = (182, 162, 222)
AZUL_P = (116, 172, 224)
AZUL_OSCURO = (129, 127, 137)
VERDE_PASTEL = (134, 194, 136)
ROJO_PASTEL = (236, 156, 174)
DURAZNO_PASTEL = (240, 174, 144)

OVERLAY_VICTORIA = (206, 232, 246)   # velo azul claro de la pantalla final

DURACION_VOLTEO = 0.20
ESPERA_VERIFICACION = 800   # ms que las dos cartas quedan a la vista


# ---------------------------------------------------------------------
# Fuentes (se mantienen por compatibilidad; ui.py es el que se usa ahora)
# ---------------------------------------------------------------------

def get_fuente_titulo():
    if not hasattr(get_fuente_titulo, '_cached'):
        try:
            get_fuente_titulo._cached = pygame.font.Font(str(FONT_DIR / "titulo.ttf"), 60)
        except (FileNotFoundError, pygame.error):
            get_fuente_titulo._cached = pygame.font.SysFont("arial", 60, bold=True)
    return get_fuente_titulo._cached


def get_fuente_menu():
    if not hasattr(get_fuente_menu, '_cached'):
        try:
            get_fuente_menu._cached = pygame.font.Font(str(FONT_DIR / "subtitulo.ttf"), 36)
        except (FileNotFoundError, pygame.error):
            get_fuente_menu._cached = pygame.font.SysFont("arial", 36)
    return get_fuente_menu._cached


# ---------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------
# Las pistas se generan con generar_audio.py (son sintetizadas, no llevan
# licencia de nadie). Se busca .ogg primero y .wav como respaldo.

MUSICA_MENU = SND_DIR / "sonido_fondo.ogg"
MUSICA_JUEGO = SND_DIR / "sonido_juego.ogg"
MUSICA_INSTRUCCIONES = SND_DIR / "sonido_instrucciones.ogg"

# nombres antiguos, por si algun modulo del launcher los sigue pidiendo
MUSICA_FONDO = MUSICA_MENU
SONIDO_JUEGO = MUSICA_JUEGO
SONIDO_INSTRUCCIONES = MUSICA_INSTRUCCIONES

SONIDO_ACTIVADO = True

VOLUMEN_GENERAL = 1.0
VOLUMEN_MUSICA = 0.30   # la musica queda bastante por debajo de los efectos
VOLUMEN_EFECTOS = 0.85


def volumen_musica_final():
    return max(0, min(1.0, VOLUMEN_GENERAL * VOLUMEN_MUSICA))


def volumen_efectos_final():
    return max(0, min(1.0, VOLUMEN_GENERAL * VOLUMEN_EFECTOS))
