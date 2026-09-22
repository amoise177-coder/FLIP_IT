import abc
import pygame
from typing import Optional, Tuple, Callable, Dict, List
from .config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    COLOR_PANEL, COLOR_GRID_BG, COLOR_CELL, COLOR_CELL_BORDER,
    COLOR_BTN_PRIMARY, COLOR_TEXT_DARK, COLOR_TEXT_LIGHT, COLOR_INFO,
    COLOR_LINE, COLOR_MUTED,
    CELL_SIZE, TILE_SIZE, CATEGORIES
)

# Caché en memoria de fuentes tipográficas para evitar llamadas repetitivas al subsistema del SO
_FONT_CACHE: Dict[Tuple[str, int, bool], pygame.font.Font] = {}

def _safe_font_load(font_names: str, size: int, bold: bool = False) -> pygame.font.Font:
    """Carga de forma protegida y en caché O(1) fuentes del sistema con fallback a fuente genérica."""
    key = (font_names, size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    try:
        font = pygame.font.SysFont(font_names, size, bold=bold)
    except Exception:
        font = pygame.font.Font(None, size)
    _FONT_CACHE[key] = font
    return font

def clear_font_cache() -> None:
    """Limpia el caché de fuentes en caso de reinicialización de subsistemas de Pygame."""
    _FONT_CACHE.clear()

def get_sys_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Carga fuentes sans-serif claras del sistema para máxima legibilidad."""
    return _safe_font_load("segoeui,segoeuiemoji,segoeuisymbol,arial", size, bold=bold)

def get_tile_font(size: int = 33, bold: bool = True) -> pygame.font.Font:
    """Carga fuentes armónicas con proporciones clásicas para fichas de juego noble."""
    return _safe_font_load("georgia,cambria,palatino,trebuchetms,segoeui,arial", size, bold=bold)

def get_small_badge_font(size: int = 11) -> pygame.font.Font:
    """Carga fuente pequeña para valores clásicos de puntuación en fichas."""
    return _safe_font_load("segoeui,arial", size, bold=True)

#Clase Base Abstracta para Elementos Gráficos

class UIElement(abc.ABC):
    """
    Clase base abstracta que define la interfaz común para cualquier componente de la UI.
    Permite tratar a todos los elementos polimórficamente.
    """
    def __init__(self, x: int, y: int, width: int, height: int):
        self._rect = pygame.Rect(x, y, width, height)
        self._visible: bool = True
        self._enabled: bool = True

    @property
    def rect(self) -> pygame.Rect: return self._rect
    @property
    def visible(self) -> bool: return self._visible
    @visible.setter
    def visible(self, value: bool) -> None: self._visible = value
    @property
    def enabled(self) -> bool: return self._enabled
    @enabled.setter
    def enabled(self, value: bool) -> None: self._enabled = value

    @abc.abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja el elemento en la superficie de destino."""
        pass

    @abc.abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Procesa un evento de Pygame. Retorna True si el evento fue consumido."""
        pass

    def update(self, dt: float) -> None:
        """Actualiza animaciones o estados temporales."""
        pass

#Elementos Clicables y Botón

class ClickableElement(UIElement):
    """
    Clase base intermedia para componentes interactivos con respuesta a cursor (hover)
    y ejecución de callback al presionar clic izquierdo.
    """
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        on_click: Optional[Callable[[], None]] = None
    ):
        super().__init__(x, y, width, height)
        self._on_click = on_click
        self._is_hovered: bool = False

    @property
    def is_hovered(self) -> bool:
        return self._is_hovered

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self._visible or not self._enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self._is_hovered = self._rect.collidepoint(event.pos)
            return False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect.collidepoint(event.pos):
                if self._on_click:
                    self._on_click()
                return True

        return False


class UIButton(ClickableElement):
    """
    Botón interactivo accesible con bordes suaves, sombra y respuesta a cursor (hover).
    """
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        bg_color: Tuple[int, int, int],
        text_color: Tuple[int, int, int] = COLOR_TEXT_LIGHT,
        on_click: Optional[Callable[[], None]] = None,
        font_size: int = 22,
        border_color: Optional[Tuple[int, int, int]] = None
    ):
        super().__init__(x, y, width, height, on_click=on_click)
        self._text = text
        self._bg_color = bg_color
        self._text_color = text_color
        self._border_color = border_color
        self._font = get_sys_font(font_size, bold=True)

    @property
    def text(self) -> str: return self._text
    @text.setter
    def text(self, value: str) -> None: self._text = value
    @property
    def bg_color(self) -> Tuple[int, int, int]: return self._bg_color
    @bg_color.setter
    def bg_color(self, value: Tuple[int, int, int]) -> None: self._bg_color = value
    @property
    def text_color(self) -> Tuple[int, int, int]: return self._text_color
    @text_color.setter
    def text_color(self, value: Tuple[int, int, int]) -> None: self._text_color = value
    @property
    def border_color(self) -> Optional[Tuple[int, int, int]]: return self._border_color
    @border_color.setter
    def border_color(self, value: Optional[Tuple[int, int, int]]) -> None: self._border_color = value

    def draw(self, surface: pygame.Surface) -> None:
        if not self._visible:
            return

        # Sombra suave
        shadow_rect = self._rect.move(0, 4)
        pygame.draw.rect(surface, (196, 188, 174), shadow_rect, border_radius=16)

        # Color con leve aclarado al pasar el ratón
        color = tuple(min(c + 10, 255) for c in self._bg_color) if self._is_hovered else self._bg_color
        pygame.draw.rect(surface, color, self._rect, border_radius=16)

        # Borde
        if self._border_color:
            pygame.draw.rect(surface, self._border_color, self._rect, width=2, border_radius=16)
        else:
            pygame.draw.rect(surface, tuple(max(c - 12, 0) for c in color), self._rect, width=1, border_radius=16)

        # Texto centrado
        text_surf = self._font.render(self._text, True, self._text_color)
        text_rect = text_surf.get_rect(center=self._rect.center)
        surface.blit(text_surf, text_rect)

# Ficha Visual Interactiva (Arrastre y Clic Directo)

class VisualTile(UIElement):
    """
    Representa visualmente una ficha de letra con volumen (sombra), textura y soporte dual:
    - Arrastrar y soltar (Drag & Drop).
    - Clic directo para seleccionar y luego colocar en una casilla.
    - Acabado delicado y artesanal con micro-relieve letterpress y puntaje clásico.
    """
    TILE_VALUES: Dict[str, int] = {
        'A': 1, 'E': 1, 'O': 1, 'I': 1, 'U': 1, 'S': 1, 'L': 1, 'R': 1, 'N': 1, 'T': 1,
        'D': 2, 'G': 2, 'C': 3, 'B': 3, 'M': 3, 'P': 3, 'F': 4, 'H': 4, 'V': 4,
        'J': 8, 'Z': 10, 'Ñ': 1
    }

    def __init__(self, letter: str, tile_id: int, size: int = TILE_SIZE):
        super().__init__(0, 0, size, size)
        self._letter = letter.upper()
        self._id = tile_id
        self._selected: bool = False
        self._dragging: bool = False
        self._locked: bool = False  # Indica si la ficha forma parte de una palabra ya consolidada
        self._drag_offset_x: int = 0
        self._drag_offset_y: int = 0
        self._origin_pos: Tuple[int, int] = (0, 0)
        self.grid_pos: Optional[Tuple[int, int]] = None
        self._font = get_tile_font(29, bold=True)
        self._val_font = get_small_badge_font(10)

    @property
    def letter(self) -> str: return self._letter
    @property
    def id(self) -> int: return self._id
    @property
    def dragging(self) -> bool: return self._dragging
    @property
    def locked(self) -> bool: return self._locked
    @locked.setter
    def locked(self, value: bool) -> None:
        self._locked = bool(value)
        if self._locked:
            self._selected, self._dragging = False, False
    @property
    def selected(self) -> bool: return self._selected
    @selected.setter
    def selected(self, value: bool) -> None:
        if not self._locked:
            self._selected = value

    def set_origin(self, x: int, y: int) -> None:
        self._origin_pos = (x, y)
        if not self._dragging and not self._locked:
            self._rect.x = x
            self._rect.y = y

    def reset_to_origin(self) -> None:
        if not self._locked:
            self._rect.x = self._origin_pos[0]
            self._rect.y = self._origin_pos[1]
            self._dragging = False

    def start_drag(self, mouse_pos: Tuple[int, int]) -> None:
        if self._locked:
            return
        self._dragging = True
        self._drag_offset_x = mouse_pos[0] - self._rect.x
        self._drag_offset_y = mouse_pos[1] - self._rect.y

    def update_drag(self, mouse_pos: Tuple[int, int]) -> None:
        if self._locked:
            return
        if self._dragging:
            self._rect.x = mouse_pos[0] - self._drag_offset_x
            self._rect.y = mouse_pos[1] - self._drag_offset_y

    def stop_drag(self) -> None:
        self._dragging = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self._visible:
            return

        # 1. Sombra exterior suave y orgánica
        s_offset = 2 if self._locked else (4 if not self._dragging else 8)
        shadow_rect = self._rect.move(2, s_offset)
        shadow_col = (180, 172, 158) if self._locked else ((175, 162, 142) if not self._dragging else (140, 130, 110))
        pygame.draw.rect(surface, shadow_col, shadow_rect, border_radius=11)

        # 2. Fondo de la ficha (acabado cálido satinado)
        if self._locked:
            base_bg = (250, 246, 235)   # Marfil apergaminado consolidado
            border_col = (188, 152, 75)  # Oro viejo pulido
            border_w = 2
        elif self._selected or self._dragging:
            base_bg = (255, 236, 178)   # Ámbar suave luminoso
            border_col = (235, 170, 50)
            border_w = 3
        else:
            base_bg = (248, 232, 198)   # Tono madera/marfil natural suave
            border_col = (175, 138, 90)  # Caramelo cálido
            border_w = 2

        pygame.draw.rect(surface, base_bg, self._rect, border_radius=11)

        # 3. Bisel de luz superior (brillo sutil que da volumen y delicadeza)
        hl_rect = pygame.Rect(self._rect.x + 2, self._rect.y + 2, self._rect.width - 4, self._rect.height // 2)
        hl_surf = pygame.Surface((hl_rect.width, hl_rect.height), pygame.SRCALPHA)
        hl_surf.fill((255, 255, 255, 60))
        surface.blit(hl_surf, (hl_rect.x, hl_rect.y))

        # 4. Borde pulido redondeado
        pygame.draw.rect(surface, border_col, self._rect, width=border_w, border_radius=11)

        # 5. Letra con sutil relieve (letterpress suave)
        # Micro-sombra de luz inferior (1px)
        light_col = (255, 255, 255) if not self._locked else (255, 252, 245)
        light_surf = self._font.render(self._letter, True, light_col)
        light_rect = light_surf.get_rect(center=(self._rect.centerx, self._rect.centery + 1))
        surface.blit(light_surf, light_rect)

        # Letra principal en tono caoba profundo
        txt_col = (42, 34, 26) if not self._locked else (48, 38, 28)
        text_surf = self._font.render(self._letter, True, txt_col)
        text_rect = text_surf.get_rect(center=self._rect.center)
        surface.blit(text_surf, text_rect)

        # 6. Pequeño valor clásico en subíndice discreto (estilo Scrabble artesanal)
        val = self.TILE_VALUES.get(self._letter, 1)
        val_col = (130, 110, 90) if not self._locked else (150, 130, 95)
        val_surf = self._val_font.render(str(val), True, val_col)
        val_rect = val_surf.get_rect(bottomright=(self._rect.right - 5, self._rect.bottom - 4))
        surface.blit(val_surf, val_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        # Los eventos de fichas se coordinan a través de UIManager para resolver colisiones
        return False

# Vista del Tablero de Juego (7x7)

class BoardView(UIElement):
    """
    Renderiza la cuadrícula del tablero y mapea posiciones del cursor a coordenadas de matriz.
    """
    def __init__(self, x: int, y: int, rows: int = 7, cols: int = 7, cell_size: int = CELL_SIZE):
        super().__init__(x, y, cols * cell_size, rows * cell_size)
        self._rows = rows
        self._cols = cols
        self._cell_size = cell_size

    def draw(self, surface: pygame.Surface) -> None:
        # Fondo contenedor del tablero
        outer_rect = pygame.Rect(
            self._rect.x - 12,
            self._rect.y - 12,
            self._rect.width + 24,
            self._rect.height + 24
        )
        pygame.draw.rect(surface, COLOR_GRID_BG, outer_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_CELL_BORDER, outer_rect, width=2, border_radius=16)

        # Casillas individuales
        for r in range(self._rows):
            for c in range(self._cols):
                cx = self._rect.x + c * self._cell_size
                cy = self._rect.y + r * self._cell_size
                cell_rect = pygame.Rect(cx + 2, cy + 2, self._cell_size - 4, self._cell_size - 4)

                # Casilla central marcada con suavidad
                if r == self._rows // 2 and c == self._cols // 2:
                    pygame.draw.rect(surface, (255, 243, 215), cell_rect, border_radius=8)
                    pygame.draw.rect(surface, (230, 200, 140), cell_rect, width=2, border_radius=8)
                else:
                    pygame.draw.rect(surface, COLOR_CELL, cell_rect, border_radius=8)
                    pygame.draw.rect(surface, COLOR_CELL_BORDER, cell_rect, width=1, border_radius=8)

    def get_cell_from_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Convierte una coordenada (x, y) de pantalla a (fila, columna)."""
        mx, my = pos
        if self._rect.collidepoint(mx, my):
            col = int((mx - self._rect.x) // self._cell_size)
            row = int((my - self._rect.y) // self._cell_size)
            if 0 <= row < self._rows and 0 <= col < self._cols:
                return (row, col)
        return None

    def get_cell_center(self, row: int, col: int) -> Tuple[int, int]:
        """Calcula el centro exacto en píxeles de una casilla dada."""
        cx = self._rect.x + col * self._cell_size + self._cell_size // 2
        cy = self._rect.y + row * self._cell_size + self._cell_size // 2
        return (cx, cy)

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

# Vista del Atril (RackView)

class RackView(UIElement):
    """
    Contenedor visual del atril de fichas con estilo cálido y redondeado.
    """
    def __init__(self, x: int, y: int, width: int, height: int = TILE_SIZE + 20):
        super().__init__(x, y, width, height)

    def draw(self, surface: pygame.Surface) -> None:
        if not self._visible:
            return

        # Sombra suave
        shadow = self._rect.move(0, 3)
        pygame.draw.rect(surface, (205, 198, 184), shadow, border_radius=16)
        pygame.draw.rect(surface, COLOR_PANEL, self._rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_LINE, self._rect, width=2, border_radius=16)

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

# Panel Lateral y Tarjetas de Estadísticas (StatCard)

class StatCard(UIElement):
    """
    Muestra estadísticas cognitivas de forma clara y destacada.
    """
    def __init__(self, x: int, y: int, title: str, initial_val: str, val_color: Tuple[int, int, int]):
        super().__init__(x, y, 260, 52)
        self._title = title
        self._val = initial_val
        self._val_color = val_color
        self._font_title = get_sys_font(14, bold=True)
        self._font_val = get_sys_font(22, bold=True)

    def set_value(self, val: str) -> None:
        self._val = val

    def draw(self, surface: pygame.Surface) -> None:
        if not self._visible:
            return
        t_surf = self._font_title.render(self._title, True, COLOR_TEXT_DARK)
        v_surf = self._font_val.render(self._val, True, self._val_color)
        surface.blit(t_surf, (self._rect.x, self._rect.y))
        surface.blit(v_surf, (self._rect.x, self._rect.y + 20))

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

# Retroalimentación Textual en Pantalla (MessageBanner)

class MessageBanner(UIElement):
    """
    Muestra mensajes breves y no punitivos al jugador (aciertos, avisos y
    orientaciones). Hereda de UIElement y utiliza update(dt) para desvanecer
    el mensaje automáticamente tras unos segundos.

    Tipos admitidos: 'exito', 'aviso', 'info'.
    """

    ESTILOS: Dict[str, Dict[str, Tuple[int, int, int]]] = {
        "exito": {"fondo": (228, 243, 229), "borde": (76, 140, 95), "texto": (30, 80, 45)},
        "aviso": {"fondo": (255, 244, 219), "borde": (222, 160, 60), "texto": (110, 70, 15)},
        "info":  {"fondo": (228, 238, 250), "borde": (55, 120, 185), "texto": (25, 60, 105)},
    }

    def __init__(self, x: int, y: int, width: int, height: int, font_size: int = 14):
        super().__init__(x, y, width, height)
        self._text: str = ""
        self._kind: str = "info"
        self._timer: float = 0.0
        self._duration: float = 0.0
        self._font = get_sys_font(font_size, bold=False)
        self._font_icon = get_sys_font(font_size + 3, bold=True)
        self._max_chars: int = max(12, width // 7)

    @property
    def text(self) -> str:
        return self._text

    @property
    def active(self) -> bool:
        return bool(self._text) and self._timer > 0.0

    def set_message(self, text: str, kind: str = "info", duration: float = 5.0) -> None:
        """Publica un mensaje visible durante `duration` segundos."""
        self._text = str(text or "").strip()
        self._kind = kind if kind in self.ESTILOS else "info"
        self._duration = max(0.5, float(duration))
        self._timer = self._duration

    def clear(self) -> None:
        self._text, self._timer = "", 0.0

    def update(self, dt: float) -> None:
        if self._timer > 0.0:
            self._timer = max(0.0, self._timer - dt)
            if self._timer == 0.0:
                self._text = ""

    def _wrap(self) -> List[str]:
        """Divide el mensaje en líneas que quepan en el ancho del recuadro."""
        lineas: List[str] = []
        actual = ""
        for palabra in self._text.split():
            prueba = (actual + " " + palabra).strip()
            if len(prueba) > self._max_chars and actual:
                lineas.append(actual)
                actual = palabra
            else:
                actual = prueba
        if actual:
            lineas.append(actual)
        return lineas[:4]

    def draw(self, surface: pygame.Surface) -> None:
        if not self._visible or not self.active:
            return

        estilo = self.ESTILOS[self._kind]
        pygame.draw.rect(surface, estilo["fondo"], self._rect, border_radius=12)
        pygame.draw.rect(surface, estilo["borde"], self._rect, width=2, border_radius=12)

        # Franja lateral de color para reforzar el tipo de mensaje
        franja = pygame.Rect(self._rect.x + 8, self._rect.y + 10, 5, self._rect.height - 20)
        pygame.draw.rect(surface, estilo["borde"], franja, border_radius=3)

        lineas = self._wrap()
        alto_linea = self._font.get_height() + 2
        alto_total = alto_linea * len(lineas)
        inicio_y = self._rect.y + max(8, (self._rect.height - alto_total) // 2)

        for i, linea in enumerate(lineas):
            surf = self._font.render(linea, True, estilo["texto"])
            surface.blit(surf, (self._rect.x + 22, inicio_y + i * alto_linea))

    def handle_event(self, event: pygame.event.Event) -> bool:
        return False

#Deslizador Interactivo de Volumen (UISlider)

class UISlider(UIElement):
    """
    Control deslizante interactivo y accesible para ajustar parámetros continuos
    (como el volumen de la música). Soporta clic directo, arrastre suave con el ratón,
    indicación de porcentaje y retroalimentación visual en tiempo real.
    """
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = 50,
        label: str = "VOLUMEN MÚSICA",
        min_value: float = 0.0,
        max_value: float = 1.0,
        initial_value: float = 0.7,
        on_change: Optional[Callable[[float], None]] = None,
        accent_color: Tuple[int, int, int] = COLOR_BTN_PRIMARY
    ):
        super().__init__(x, y, width, height)
        self._label = label
        self._min_value = float(min_value)
        self._max_value = float(max_value)
        self._value = max(self._min_value, min(self._max_value, float(initial_value)))
        self._on_change = on_change
        self._accent_color = accent_color
        self._is_dragging: bool = False
        self._is_hovered: bool = False

        self._font_label = get_sys_font(14, bold=True)
        self._font_val = get_sys_font(14, bold=True)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, val: float) -> None:
        self._value = max(self._min_value, min(self._max_value, float(val)))

    @property
    def track_rect(self) -> pygame.Rect:
        track_h = 8
        track_y = self._rect.y + 28
        track_x = self._rect.x + 8
        track_w = self._rect.width - 16
        return pygame.Rect(track_x, track_y, track_w, track_h)

    def _update_value_from_pos(self, mouse_x: int) -> None:
        tr = self.track_rect
        if tr.width <= 0:
            return
        ratio = (mouse_x - tr.x) / float(tr.width)
        ratio = max(0.0, min(1.0, ratio))
        new_val = self._min_value + ratio * (self._max_value - self._min_value)
        if abs(new_val - self._value) > 0.001:
            self._value = round(new_val, 2)
            if self._on_change:
                self._on_change(self._value)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self._visible or not self._enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            expanded_track = self.track_rect.inflate(16, 24)
            if self._rect.collidepoint(event.pos) or expanded_track.collidepoint(event.pos):
                self._is_dragging = True
                self._update_value_from_pos(event.pos[0])
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._is_dragging:
                self._is_dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            self._is_hovered = self._rect.collidepoint(event.pos) or self.track_rect.inflate(16, 24).collidepoint(event.pos)
            if self._is_dragging:
                self._update_value_from_pos(event.pos[0])
                return True

        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self._visible:
            return

        # 1. Etiquetas de Texto: Nombre del control y porcentaje actual
        lbl_surf = self._font_label.render(self._label, True, COLOR_TEXT_DARK)
        surface.blit(lbl_surf, (self._rect.x + 4, self._rect.y + 2))

        pct_val = int(round((self._value - self._min_value) / max(0.001, self._max_value - self._min_value) * 100))
        pct_text = f"{pct_val}%"
        val_surf = self._font_val.render(pct_text, True, self._accent_color)
        val_x = self._rect.right - val_surf.get_width() - 4
        surface.blit(val_surf, (val_x, self._rect.y + 2))

        # 2. Pista (Riel de fondo inactivo)
        tr = self.track_rect
        pygame.draw.rect(surface, (215, 208, 195), tr, border_radius=4)
        pygame.draw.rect(surface, COLOR_CELL_BORDER, tr, width=1, border_radius=4)

        # 3. Riel activo (Relleno proporcional con color de acento)
        ratio = (self._value - self._min_value) / max(0.001, self._max_value - self._min_value)
        fill_w = int(tr.width * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(tr.x, tr.y, fill_w, tr.height)
            pygame.draw.rect(surface, self._accent_color, fill_rect, border_radius=4)

        # 4. Perilla deslizante (Knob / Thumb interactivo)
        knob_x = tr.x + fill_w
        knob_y = tr.centery
        radius = 11 if (self._is_dragging or self._is_hovered) else 9

        # Sombra suave de la perilla
        shadow_circle = (knob_x + 1, knob_y + 2)
        pygame.draw.circle(surface, (160, 150, 140), shadow_circle, radius)

        # Cuerpo de la perilla
        knob_color = (255, 255, 255) if not self._is_dragging else (245, 250, 245)
        pygame.draw.circle(surface, knob_color, (knob_x, knob_y), radius)

        # Borde exterior de la perilla
        knob_border_col = self._accent_color if (self._is_hovered or self._is_dragging) else (140, 130, 120)
        pygame.draw.circle(surface, knob_border_col, (knob_x, knob_y), radius, width=2)

        # Punto focal central si está seleccionado/arrastrando
        if self._is_dragging or self._is_hovered:
            pygame.draw.circle(surface, self._accent_color, (knob_x, knob_y), 4)

# Vista de Selección de Categoría Temática (Diseño Con interfaz)

class CategorySelectView(UIElement):
    """
    Pantalla previa al tablero: el jugador elige una categoría temática.
    Presenta la estética de 'Con interfaz': fondo limpio, título centrado,
    subtítulo explicativo, 6 botones temáticos en 2 columnas y botón de regreso.
    """
    def __init__(
        self,
        on_select: Callable[[str], None],
        on_back: Optional[Callable[[], None]] = None
    ):
        super().__init__(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self._on_select = on_select
        self._on_back = on_back
        self._font_title = get_sys_font(36, bold=True)
        self._font_sub = get_sys_font(22, bold=False)
        self._buttons: List[UIButton] = []
        self._build_buttons()
        self._back_button = UIButton(
            40, 640, 220, 50, "VOLVER", COLOR_INFO,
            on_click=self._on_back, font_size=20
        )

    def _build_buttons(self) -> None:
        self._buttons.clear()
        cols = 2
        btn_w, btn_h = 420, 66
        gap_x, gap_y = 36, 18
        grid_w = cols * btn_w + gap_x
        start_x = (SCREEN_WIDTH - grid_w) // 2
        start_y = 175

        themed_categories = [c for c in CATEGORIES if c.get("id") != "todas"]
        all_categories = [c for c in CATEGORIES if c.get("id") == "todas"]

        for index, category in enumerate(themed_categories):
            row, col = divmod(index, cols)
            x = start_x + col * (btn_w + gap_x)
            y = start_y + row * (btn_h + gap_y)
            cat_id = category["id"]
            button = UIButton(
                x, y, btn_w, btn_h,
                category["title"],
                category["color"],
                on_click=lambda cid=cat_id: self._on_select(cid),
                font_size=23
            )
            self._buttons.append(button)

        # Botón especial destacado para Modo Completo
        for category in all_categories:
            y = start_y + 3 * (btn_h + gap_y)
            cat_id = category["id"]
            button = UIButton(
                start_x, y, grid_w, btn_h,
                "MODO COMPLETO (TODAS LAS CATEGORÍAS)",
                category["color"],
                on_click=lambda cid=cat_id: self._on_select(cid),
                font_size=23
            )
            self._buttons.append(button)

    def draw(self, surface: pygame.Surface) -> None:
        title = self._font_title.render("Elige una categoría", True, COLOR_TEXT_DARK)
        subtitle = self._font_sub.render(
            "Las palabras, las pistas y las letras se adaptan al tema que elijas.",
            True,
            COLOR_INFO
        )
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 58)))
        surface.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 108)))

        for button in self._buttons:
            button.draw(surface)
        self._back_button.draw(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        return any(b.handle_event(event) for b in self._buttons) or self._back_button.handle_event(event)


