"""Configuración visual y técnica centralizada — tema moderno, cálido y accesible.
Cambia aquí la paleta, la tipografía o el ritmo de las animaciones sin tocar las pantallas."""

WIDTH, HEIGHT, FPS = 1280, 720, 60

# ---------------------------------------------------------------------------
# Paleta de alto contraste pensada para lectura fácil
# ---------------------------------------------------------------------------
BG_TOP = (255, 246, 230)        # crema cálido (fondo superior)
BG_BOTTOM = (255, 222, 176)     # albaricoque (fondo inferior)
BG_IDLE = BG_TOP                # relleno de seguridad durante micro-vibraciones
INK = (56, 44, 37)              # tinta cálida (texto principal)
MUTED = (122, 104, 92)          # texto secundario
FAINT = (214, 192, 166)         # bordes suaves / decoración
PANEL = (255, 252, 247)         # cuerpo de tarjetas
PANEL_ALT = (251, 236, 213)     # tarjeta cálida alternativa
WHITE = (255, 255, 255)

PRIMARY = (238, 104, 34)        # naranja vivaz (acción principal)
PRIMARY_DARK = (198, 78, 18)
SECONDARY = (16, 148, 182)      # azul petróleo (pistas / secundario)
SECONDARY_DARK = (8, 114, 142)
SUCCESS = (42, 156, 106)        # verde (comprobar / aciertos)
SUCCESS_DARK = (24, 120, 80)
GOLD = (233, 168, 22)           # dorado (progreso / estrellas)
ACCENT = (128, 94, 208)         # púrpura suave (sorpresas)
ROSE = (226, 96, 130)           # rosa cálida (aviso suave)

SHADOW = (64, 44, 24)           # color base de sombras
OVERLAY = (46, 34, 26)          # color de transición de entrada

# ---------------------------------------------------------------------------
# Tipografía: se elige automáticamente la primera familia moderna disponible
# ---------------------------------------------------------------------------
FONT_STACK = ["Segoe UI", "Segoe UI Semibold", "Calibri", "Verdana", "DejaVu Sans", "Arial"]
TITLE_SIZE = 52
SUBTITLE_SIZE = 27
BODY_SIZE = 30
HUD_SIZE = 24

# ---------------------------------------------------------------------------
# Ritmo de las animaciones (segundos)
# ---------------------------------------------------------------------------
FADE_ENTER = 0.45    # fundido de entrada de pantalla
PRESS_ANIM = 0.12    # hundimiento al pulsar
HOVER_ANIM = 0.14    # iluminación al pasar el ratón
BURST_LIFE = 0.95    # vida de las partículas de celebración