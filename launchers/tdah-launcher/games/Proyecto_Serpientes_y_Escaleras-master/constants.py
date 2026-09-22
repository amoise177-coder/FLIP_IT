"""
Módulo de configuración global, dimensiones y paleta de colores alegre y moderna.
"""
from typing import Tuple, List

# ==============================================================================
# RESOLUCIÓN Y RENDIMIENTO
# ==============================================================================
WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
FPS: int = 60

# ==============================================================================
# VELOCIDADES DE ANIMACIÓN (Progreso por frame a 60 FPS)
# ==============================================================================
# Valores ajustados para que el movimiento sea pausado, claro y disfrutable
SPEED_WALK: float = 0.050      # ~20 frames (~0.33s) por cada casilla al caminar
SPEED_LADDER: float = 0.090    # Exactamente 2 veces más rápido (antes 0.045)
SPEED_SNAKE: float = 0.076     # Exactamente 2 veces más rápido (antes 0.038)

# ==============================================================================
# TABLERO DE JUEGO (10x10)
# ==============================================================================
BOARD_SIZE: int = 660
BOARD_POS: Tuple[int, int] = ((WINDOW_WIDTH - BOARD_SIZE) // 2, (WINDOW_HEIGHT - BOARD_SIZE) // 2)
GRID_COLS: int = 10
GRID_ROWS: int = 10
TOTAL_TILES: int = GRID_COLS * GRID_ROWS
CELL_SIZE: int = BOARD_SIZE // GRID_COLS

# ==============================================================================
# PALETA DE COLORES VIBRANTE Y ENTRETENIDA
# ==============================================================================
COLOR_BG: Tuple[int, int, int] = (15, 18, 30)
COLOR_PANEL_BG: Tuple[int, int, int] = (24, 30, 48)
COLOR_PANEL_BORDER: Tuple[int, int, int] = (45, 56, 84)
COLOR_CARD_BG: Tuple[int, int, int] = (32, 40, 64)
COLOR_CARD_ACTIVE: Tuple[int, int, int] = (44, 58, 96)

COLOR_BOARD_BG: Tuple[int, int, int] = (20, 24, 38)
COLOR_TILE_BORDER: Tuple[int, int, int] = (195, 205, 225)
COLOR_TEXT_DARK: Tuple[int, int, int] = (35, 45, 65)
COLOR_TEXT_LIGHT: Tuple[int, int, int] = (245, 250, 255)
COLOR_TEXT_MUTED: Tuple[int, int, int] = (150, 165, 190)

# Paleta multicolor pastel para casillas del tablero
TILE_PALETTE: List[Tuple[int, int, int]] = [
    (218, 240, 255),  # Azul cielo suave
    (218, 250, 230),  # Menta refrescante
    (255, 235, 220),  # Melocotón cálido
    (242, 230, 255),  # Lavanda suave
    (255, 250, 215)   # Vainilla alegre
]

# Casillas especiales
COLOR_TILE_START: Tuple[int, int, int] = (195, 245, 215)
COLOR_TILE_END: Tuple[int, int, int] = (255, 230, 150)

# Elementos del juego y estados
COLOR_ACCENT: Tuple[int, int, int] = (79, 110, 247)
COLOR_ACCENT_HOVER: Tuple[int, int, int] = (105, 132, 255)
COLOR_GOLD: Tuple[int, int, int] = (255, 195, 50)
COLOR_SNAKE: Tuple[int, int, int] = (240, 65, 90)
COLOR_SNAKE_BELLY: Tuple[int, int, int] = (255, 215, 90)
COLOR_SNAKE_HEAD: Tuple[int, int, int] = (210, 40, 65)
COLOR_LADDER: Tuple[int, int, int] = (46, 190, 105)
COLOR_LADDER_RAIL: Tuple[int, int, int] = (215, 150, 40)
COLOR_LADDER_RUNG: Tuple[int, int, int] = (255, 210, 80)

# Jugadores
COLOR_P1: Tuple[int, int, int] = (45, 160, 255)     # Cyan / Azul eléctrico
COLOR_P2: Tuple[int, int, int] = (255, 75, 120)     # Fucsia / Coral vibrante
