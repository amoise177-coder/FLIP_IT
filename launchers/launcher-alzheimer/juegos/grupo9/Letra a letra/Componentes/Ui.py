import sys
import pygame
from typing import List, Optional, Tuple

from .config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WINDOW_TITLE,
    COLOR_BG, COLOR_PANEL, COLOR_CELL_BORDER, COLOR_TEXT_DARK,
    COLOR_BTN_PRIMARY, COLOR_BTN_HINT, COLOR_BTN_CLEAR,
    COLOR_SUCCESS, COLOR_INFO, COLOR_HINT_BOX,
    BOARD_ROWS, BOARD_COLS, CELL_SIZE, BOARD_X, BOARD_Y,
    RACK_CAPACITY, RACK_X, RACK_Y, TILE_SIZE, CATEGORIAS_FILE,
    PUNTUACIONES_FILE, SOUNDS_DIR, SOUND_ENABLED, SOUND_VOLUME, RUTA_FONDO,
    CATEGORIES, COLOR_LINE, COLOR_MUTED, CATEGORY_MAP
)

from .board import Board
from .Jugador import TileBag, PlayerRack, PlayerStats, HighScoreManager
from .dictionary_checker import DictionaryChecker

from .components import (
    UIElement, UIButton, VisualTile, BoardView, RackView,
    StatCard, CategorySelectView, UISlider, MessageBanner, get_sys_font
)
from .Audio import GestorAudio
from .Efectos import VisualEffectsManager

class UIManager:
    """
    Gestor principal de la interfaz gráfica y del bucle de juego.
    Soporta pantalla de bienvenida/selección temática y tablero de juego.
    """
    STATE_MENU = "menu"
    STATE_CATEGORY_SELECT = "category_select"
    STATE_SCORES = "scores"
    STATE_INFO = "info"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self, screen: Optional[pygame.Surface] = None):
        # Inicialización de subsistemas de Pygame
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        # 1. Configuración de Pantalla (1280x720) y Reloj (60 FPS)
        if screen is not None:
            self._screen = screen
        else:
            self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(WINDOW_TITLE)
        self._clock = pygame.time.Clock()
        self._running = False

        # 2. Inicialización de Audio, Efectos Visuales y Fondo
        self._sound_mgr = GestorAudio(SOUNDS_DIR, enabled=SOUND_ENABLED, volume=SOUND_VOLUME)
        self._effects_mgr = VisualEffectsManager()
        self._bg_image: Optional[pygame.Surface] = None
        self._load_background()

        # Máquina de estados del juego (inicia en el Menú Principal interactivo)
        self._state: str = self.STATE_MENU
        self._high_scores = HighScoreManager(PUNTUACIONES_FILE)

        # 2. Inicialización de la Lógica de Dominio
        self._board_logic = Board(BOARD_ROWS, BOARD_COLS)
        self._bag_logic = TileBag()
        self._rack_logic = PlayerRack(RACK_CAPACITY)
        self._stats_logic = PlayerStats()
        self._dict_checker = DictionaryChecker(CATEGORIAS_FILE)

        # 3. Estado de Interacción
        self._selected_tile: Optional[VisualTile] = None
        self._dragged_tile: Optional[VisualTile] = None
        self._active_hint_text: str = ""
        self._direction: str = "horizontal"

        # Fuentes tipográficas optimizadas (utilizan el caché en memoria O(1))
        self._font_menu_title = get_sys_font(42, bold=True)
        self._font_menu_sub = get_sys_font(18, bold=False)
        self._font_scores_title = get_sys_font(36, bold=True)
        self._font_scores_sub = get_sys_font(18, bold=False)
        self._font_scores_cat = get_sys_font(19, bold=True)
        self._font_scores_pts = get_sys_font(22, bold=True)
        self._font_hint_label = get_sys_font(14, bold=True)
        self._font_hint_body = get_sys_font(14, bold=False)

        # Botón SFX en el Encabezado Superior (compartido)
        self._btn_audio = UIButton(
            1145, 16, 95, 36, "SFX", (255, 252, 240),
            text_color=(35, 95, 60), on_click=self.toggle_sfx, font_size=14,
            border_color=(120, 180, 135)
        )
        self._update_sfx_button()

        # Botones y Deslizador del Menú Principal
        self._btn_menu_play = UIButton(
            440, 190, 400, 62, "JUGAR", COLOR_BTN_PRIMARY,
            on_click=self.open_category_select, font_size=26
        )
        self._btn_menu_info = UIButton(
            440, 262, 400, 62, "INFORMACIÓN", (120, 150, 185),
            on_click=self.open_info, font_size=26
        )
        self._btn_menu_scores = UIButton(
            440, 334, 400, 62, "PUNTUACIONES", COLOR_BTN_HINT,
            on_click=self.open_scores, font_size=26
        )
        self._btn_menu_exit = UIButton(
            440, 406, 400, 62, "SALIR", COLOR_BTN_CLEAR,
            on_click=self.exit_game, font_size=26
        )
        self._slider_music_menu = UISlider(
            435, 502, 410, 52, "VOLUMEN DE MÚSICA", min_value=0.0, max_value=1.0,
            initial_value=self._sound_mgr.volumen_musica,
            on_change=self.set_music_volume, accent_color=COLOR_BTN_PRIMARY
        )

        # Botones en la Pantalla de Puntuaciones
        self._btn_scores_reset = UIButton(
            310, 605, 310, 56, "REINICIAR PUNTOS", COLOR_BTN_CLEAR,
            on_click=self.reset_scores, font_size=20
        )
        self._btn_scores_back = UIButton(
            660, 605, 310, 56, "VOLVER AL MENÚ", COLOR_INFO,
            on_click=self.open_menu, font_size=20
        )

        # Botón de regreso desde la ventana de Información
        self._btn_info_back = UIButton(
            490, 644, 300, 52, "VOLVER AL MENÚ", COLOR_INFO,
            on_click=self.open_menu, font_size=20
        )

        # Botón de regreso a Menú desde Selección de Categorías
        self._btn_cat_back = UIButton(
            45, 24, 180, 36, "VOLVER AL MENÚ", (225, 218, 205),
            text_color=COLOR_TEXT_DARK, on_click=self.open_menu, font_size=13
        )

        # Botones de la pantalla final de partida
        self._btn_end_again = UIButton(
            390, 390, 500, 58, "JUGAR DE NUEVO", COLOR_BTN_PRIMARY,
            on_click=self.restart_current_category, font_size=22
        )
        self._btn_end_menu = UIButton(
            390, 460, 500, 58, "VOLVER AL MENÚ", COLOR_BTN_HINT,
            on_click=self.open_menu, font_size=22
        )
        self._btn_end_exit = UIButton(
            390, 530, 500, 58, "SALIR", COLOR_BTN_CLEAR,
            on_click=self.exit_game, font_size=22
        )

        # Botón de Menú en el Encabezado del Tablero durante la partida
        self._btn_menu = UIButton(
            1030, 16, 100, 36, "MENÚ", (225, 218, 205),
            text_color=COLOR_TEXT_DARK, on_click=self.open_menu, font_size=13
        )

        # Selector de dirección para indicar claramente cómo se leerá la palabra.
        self._btn_horizontal = UIButton(
            515, 74, 130, 28, "HORIZONTAL", COLOR_BTN_PRIMARY,
            on_click=self.select_horizontal, font_size=12
        )
        self._btn_vertical = UIButton(
            652, 74, 115, 28, "VERTICAL", (225, 218, 205),
            text_color=COLOR_TEXT_DARK, on_click=self.select_vertical, font_size=12
        )
        self._update_direction_buttons()

        # Deslizador de volumen accesible durante la partida en el panel izquierdo (abajo)
        self._slider_music_playing = UISlider(
            45, 618, 260, 52, "VOLUMEN MÚSICA", min_value=0.0, max_value=1.0,
            initial_value=self._sound_mgr.volumen_musica,
            on_change=self.set_music_volume, accent_color=COLOR_BTN_PRIMARY
        )

        # 4. Creación de la Vista de Selección de Categoría (Diseño Con interfaz)
        self._category_view = CategorySelectView(
            on_select=self.select_category,
            on_back=self.open_menu
        )

        # 5. Creación de Componentes UI del Tablero (Herencia y Polimorfismo)
        self._board_view = BoardView(BOARD_X, BOARD_Y, BOARD_ROWS, BOARD_COLS, CELL_SIZE)
        rack_width = (BOARD_COLS * CELL_SIZE) + 24
        self._rack_view = RackView(RACK_X, RACK_Y, rack_width)

        # Botón para Cambiar Categoría durante la partida: reubicado arriba del deslizador de volumen
        self._btn_change_category = UIButton(
            45, 558, 260, 48, "CATEGORÍAS", COLOR_INFO,
            on_click=self.open_category_select, font_size=18
        )

        # Tarjetas de Estadísticas en el Panel Lateral Izquierdo
        initial_cat = self._dict_checker.active_category or "Todas"
        self._card_category = StatCard(45, 120, "CATEGORÍA ACTIVA", initial_cat, (50, 120, 170))
        self._card_score = StatCard(45, 182, "PUNTUACIÓN", "0 PTS", COLOR_BTN_PRIMARY)
        self._card_words = StatCard(45, 244, "PALABRAS LOGRADAS", "0", COLOR_BTN_HINT)

        # Botones de Acción Accesibles (alineados debajo del recuadro ¿Cómo jugar?)
        self._btn_renew = UIButton(
            880, 375, 365, 52, "RENOVAR ATRIL", (230, 222, 210),
            text_color=COLOR_TEXT_DARK, on_click=self.renew_rack_tiles, font_size=18
        )
        self._btn_validate = UIButton(
            880, 437, 365, 56, "COMPROBAR PALABRA", COLOR_BTN_PRIMARY,
            on_click=self.validate_word, font_size=19
        )
        self._btn_hint = UIButton(
            880, 503, 365, 54, "SOLICITAR PISTA", COLOR_BTN_HINT,
            on_click=self.request_hint, font_size=19
        )
        self._btn_clear = UIButton(
            880, 567, 365, 54, "RECOGER FICHAS", COLOR_BTN_CLEAR,
            on_click=self.recall_tiles, font_size=19
        )

        # Banner de retroalimentación textual en el panel izquierdo
        self._msg_banner = MessageBanner(45, 466, 260, 86, font_size=14)

        # Registro polimórfico de elementos estáticos / interactivos del tablero
        self._static_ui_elements: List[UIElement] = [
            self._msg_banner,
            self._board_view,
            self._rack_view,
            self._card_category,
            self._card_score,
            self._card_words,
            self._btn_renew,
            self._btn_validate,
            self._btn_hint,
            self._btn_clear,
            self._btn_change_category,
            self._btn_menu,
            self._btn_audio,
            self._btn_horizontal,
            self._btn_vertical,
            self._slider_music_playing
        ]

        # Colección de fichas visuales activas
        self._visual_tiles: List[VisualTile] = []
        self._replenish_rack()

        # Pre-renderizado de textos y superficies estáticas para máxima eficiencia a 60 FPS
        self._init_static_surfaces()

    def _init_static_surfaces(self) -> None:
        """Pre-renderiza superficies estáticas para eliminar asignaciones y renderizados repetitivos a 60 FPS."""
        # 1. Encabezado superior del tablero (juego en curso)
        self._surf_play_title = get_sys_font(36, bold=True).render("LETRA A LETRA", True, (37, 91, 72))
        self._rect_play_title = self._surf_play_title.get_rect(center=(SCREEN_WIDTH // 2, 24))
        self._surf_play_sub = get_sys_font(15, bold=True).render("PEQUEÑAS PALABRAS, GRANDES CONEXIONES", True, (151, 101, 78))
        self._rect_play_sub = self._surf_play_sub.get_rect(center=(SCREEN_WIDTH // 2, 52))

        # 2. Panel lateral derecho: Recuadro "¿CÓMO JUGAR?"
        panel_right_cx = 880 + 365 // 2
        self._surf_help_title = get_sys_font(21, bold=True).render("¿CÓMO JUGAR?", True, (37, 91, 72))
        self._rect_help_title = self._surf_help_title.get_rect(center=(panel_right_cx, 105 + 24))

        self._help_items_surfs: List[Tuple[pygame.Surface, Tuple[int, int], pygame.Surface, Tuple[int, int]]] = []
        help_lines = [
            "Elige horizontal o vertical.",
            "Arrastra las letras al tablero.",
            "Forma la palabra sin espacios.",
            "Comprueba cuando termines.",
        ]
        font_num = get_sys_font(15, bold=True)
        font_txt = get_sys_font(15, bold=False)
        for i, line in enumerate(help_lines):
            y = 105 + 54 + i * 36
            num_surf = font_num.render(str(i + 1), True, COLOR_TEXT_DARK)
            txt_surf = font_txt.render(line, True, COLOR_TEXT_DARK)
            self._help_items_surfs.append((num_surf, (880 + 24, y), txt_surf, (880 + 50, y)))

        self._surf_help_motiv = get_sys_font(16, bold=False).render("¡Tú puedes!", True, COLOR_MUTED)
        self._rect_help_motiv = self._surf_help_motiv.get_rect(center=(panel_right_cx, 105 + 224))

        # 3. Encabezado de la tarjeta de pista
        self._surf_hint_title = self._font_hint_label.render("AYUDA TERAPÉUTICA:", True, COLOR_TEXT_DARK)

        # 3.b Contenido pre-renderizado de la ventana de Información
        self._init_info_surfaces()

        # 4. Superficies translúcidas pre-renderizadas (evita Pygame.Surface(..., SRCALPHA) por frame)
        self._menu_card_surf = pygame.Surface((520, 560), pygame.SRCALPHA)
        pygame.draw.rect(self._menu_card_surf, (248, 245, 238, 235), self._menu_card_surf.get_rect(), border_radius=24)
        pygame.draw.rect(self._menu_card_surf, (205, 195, 180, 220), self._menu_card_surf.get_rect(), width=2, border_radius=24)

        self._scores_hdr_surf = pygame.Surface((SCREEN_WIDTH, 115), pygame.SRCALPHA)
        self._scores_hdr_surf.fill((246, 243, 236, 225))

        self._scores_all_surf = pygame.Surface((680, 72), pygame.SRCALPHA)
        pygame.draw.rect(self._scores_all_surf, (248, 245, 238, 235), self._scores_all_surf.get_rect(), border_radius=14)
        pygame.draw.rect(self._scores_all_surf, (90, 70, 150), self._scores_all_surf.get_rect(), width=2, border_radius=14)

# Ventana de Información: propósito del juego y modo de uso

    INFO_PROPOSITO: List[str] = [
        "Su finalidad es terapéutica, no competitiva:",
        "",
        "• Estimula la memoria semántica y la fluidez",
        "   verbal al recordar y formar palabras.",
        "• Fortalece la concentración, la asociación",
        "   y el razonamiento con retos sencillos.",
        "• Favorece la interacción social: se puede",
        "   jugar solo o acompañado, ayudándose.",
        "• Evita la frustración: no hay tiempo límite",
        "   ni penalizaciones. Equivocarse no resta.",
    ]

    INFO_PASOS: List[str] = [
        "Elige una categoría (Naturaleza, Animales...).",
        "Indica si la palabra irá HORIZONTAL o VERTICAL.",
        "Arrastra una letra del atril al tablero, o haz",
        "clic en la letra y luego en la casilla destino.",
        "Las letras deben quedar juntas, sin huecos.",
        "Pulsa COMPROBAR PALABRA: si es correcta, las",
        "fichas se fijan y sumas puntos (10 por letra).",
        "¿Atascado? Usa SOLICITAR PISTA, RECOGER FICHAS",
        "o RENOVAR ATRIL para recibir letras nuevas.",
        "La partida termina al formar 7 palabras.",
    ]

    def _init_info_surfaces(self) -> None:
        """Pre-renderiza los textos de la ventana de Información (eficiencia a 60 FPS)."""
        font_sec = get_sys_font(21, bold=True)
        font_txt = get_sys_font(16, bold=False)
        font_num = get_sys_font(15, bold=True)

        self._surf_info_title = get_sys_font(38, bold=True).render(
            "SOBRE EL JUEGO", True, (37, 91, 72)
        )
        self._rect_info_title = self._surf_info_title.get_rect(center=(SCREEN_WIDTH // 2, 52))
        self._surf_info_sub = get_sys_font(17, bold=False).render(
            "Pequeñas palabras, grandes conexiones", True, COLOR_INFO
        )
        self._rect_info_sub = self._surf_info_sub.get_rect(center=(SCREEN_WIDTH // 2, 88))

        # Columna izquierda: propósito
        self._surf_info_sec1 = font_sec.render("BENEFICIOS:", True, (37, 91, 72))
        self._info_left: List[Tuple[pygame.Surface, Tuple[int, int]]] = []
        for i, linea in enumerate(self.INFO_PROPOSITO):
            if not linea:
                continue
            self._info_left.append((font_txt.render(linea, True, COLOR_TEXT_DARK), (85, 190 + i * 25)))

        # Columna derecha: pasos numerados
        self._surf_info_sec2 = font_sec.render("¿CÓMO SE JUEGA?", True, (37, 91, 72))
        self._info_right: List[Tuple[Optional[pygame.Surface], pygame.Surface, int]] = []
        numero = 0
        y = 190
        pasos_con_numero = {0, 1, 2, 4, 5, 7, 9}
        for i, linea in enumerate(self.INFO_PASOS):
            num_surf = None
            if i in pasos_con_numero:
                numero += 1
                num_surf = font_num.render(f"{numero}.", True, COLOR_BTN_HINT)
            self._info_right.append((num_surf, font_txt.render(linea, True, COLOR_TEXT_DARK), y))
            y += 25

        self._surf_info_pie = get_sys_font(15, bold=True).render(
            "Consejo: juega sin prisa. Cada palabra construida ya es un logro.",
            True, COLOR_MUTED
        )
        self._rect_info_pie = self._surf_info_pie.get_rect(center=(SCREEN_WIDTH // 2, 596))

    def _render_info_screen(self) -> None:
        """Renderiza la ventana con el propósito del juego y las instrucciones."""
        # Velo claro para garantizar legibilidad sobre el fondo artístico
        panel = pygame.Rect(40, 20, SCREEN_WIDTH - 80, 600)
        pygame.draw.rect(self._screen, (250, 248, 242), panel, border_radius=22)
        pygame.draw.rect(self._screen, COLOR_LINE, panel, width=2, border_radius=22)

        self._screen.blit(self._surf_info_title, self._rect_info_title)
        self._screen.blit(self._surf_info_sub, self._rect_info_sub)
        pygame.draw.line(self._screen, COLOR_LINE, (80, 115), (SCREEN_WIDTH - 80, 115), 2)

        # Separador vertical entre las dos columnas
        pygame.draw.line(self._screen, COLOR_LINE, (SCREEN_WIDTH // 2, 145), (SCREEN_WIDTH // 2, 570), 1)

        self._screen.blit(self._surf_info_sec1, (85, 145))
        for surf, pos in self._info_left:
            self._screen.blit(surf, pos)

        self._screen.blit(self._surf_info_sec2, (SCREEN_WIDTH // 2 + 45, 145))
        for num_surf, txt_surf, y in self._info_right:
            if num_surf is not None:
                self._screen.blit(num_surf, (SCREEN_WIDTH // 2 + 45, y))
            self._screen.blit(txt_surf, (SCREEN_WIDTH // 2 + 72, y))

        self._screen.blit(self._surf_info_pie, self._rect_info_pie)

        self._btn_info_back.draw(self._screen)
        self._btn_audio.draw(self._screen)

    def _load_background(self) -> None:
        """Carga y adapta la imagen de fondo artístico a la resolución del juego (1280x720)."""
        try:
            if RUTA_FONDO.exists():
                raw_bg = pygame.image.load(str(RUTA_FONDO)).convert()
                self._bg_image = pygame.transform.smoothscale(
                    raw_bg, (SCREEN_WIDTH, SCREEN_HEIGHT)
                )
                print(f"[UI] Fondo artístico integrado correctamente desde '{RUTA_FONDO.name}'.")
            else:
                print(f"[UI] Archivo de fondo no encontrado en '{RUTA_FONDO}'. Se usará color sólido.")
        except Exception as err:
            print(f"[UI] Advertencia al cargar fondo: {err}. Se usará color sólido.")
            self._bg_image = None



    def select_category(self, category_name: Optional[str]) -> None:
        """Acción de selección: aplica el filtro semántico e inicia el tablero de juego con mano garantizada."""
        if category_name in ("todas", "Todas", "modo_completo", "Modo Completo"):
            self._dict_checker.set_active_category(None)
            display_name = "Modo Completo"
        else:
            self._dict_checker.set_active_category(category_name)
            meta = CATEGORY_MAP.get(str(category_name).lower())
            display_name = meta["title"] if meta else (category_name or "Todas")
        self._card_category.set_value(display_name[:16])

        # Reiniciar tablero y atril para empezar la nueva categoría
        self._board_logic.reset()
        self._stats_logic.reset()
        self._card_score.set_value("0 PTS")
        self._card_words.set_value("0")
        self._visual_tiles.clear()
        self._rack_logic.clear()
        self._selected_tile = None
        self._dragged_tile = None
        self._direction = "horizontal"
        self._board_logic.set_direction("horizontal")
        self._update_direction_buttons()

        # Inicializar atril inteligente con palabra garantizada de la categoría
        self._replenish_smart_rack()

        self._active_hint_text = ""
        self._msg_banner.set_message(
            f"¡Comenzamos con {display_name}! Forma 7 palabras a tu ritmo.",
            kind="exito", duration=6.0
        )

        self._sound_mgr.play_word_success()
        self._effects_mgr.emit_hint_sparkle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self._state = self.STATE_PLAYING

    def _update_direction_buttons(self) -> None:
        """Actualiza el resaltado visual de la dirección seleccionada."""
        if self._direction == "horizontal":
            self._btn_horizontal.bg_color = COLOR_BTN_PRIMARY
            self._btn_horizontal.text_color = (255, 255, 255)
            self._btn_vertical.bg_color = (225, 218, 205)
            self._btn_vertical.text_color = COLOR_TEXT_DARK
        else:
            self._btn_horizontal.bg_color = (225, 218, 205)
            self._btn_horizontal.text_color = COLOR_TEXT_DARK
            self._btn_vertical.bg_color = COLOR_BTN_PRIMARY
            self._btn_vertical.text_color = (255, 255, 255)

    def select_horizontal(self) -> None:
        """Selecciona la orientación horizontal para la palabra del turno."""
        if self._board_logic.current_placed_tiles:
            self._msg_banner.set_message(
                "Pulsa 'RECOGER FICHAS' antes de cambiar la dirección.", kind="aviso", duration=4.0
            )
            self._sound_mgr.play_click()
            return
        self._direction = "horizontal"
        self._board_logic.set_direction("horizontal")
        self._update_direction_buttons()
        self._sound_mgr.play_click()

    def select_vertical(self) -> None:
        """Selecciona la orientación vertical para la palabra del turno."""
        if self._board_logic.current_placed_tiles:
            self._msg_banner.set_message(
                "Pulsa 'RECOGER FICHAS' antes de cambiar la dirección.", kind="aviso", duration=4.0
            )
            self._sound_mgr.play_click()
            return
        self._direction = "vertical"
        self._board_logic.set_direction("vertical")
        self._update_direction_buttons()
        self._sound_mgr.play_click()

    def restart_current_category(self) -> None:
        """Reinicia la partida manteniendo la categoría seleccionada."""
        category = self._dict_checker.active_category
        self.select_category(category)

    def open_category_select(self) -> None:
        """Acción del botón: regresa a la pantalla de selección de categorías."""
        self._sound_mgr.play_click()
        self._state = self.STATE_CATEGORY_SELECT

    def open_menu(self) -> None:
        """Acción del botón: regresa a la pantalla del Menú Principal."""
        self._sound_mgr.play_click()
        self._state = self.STATE_MENU
        self._liberar_ficha_en_mano()

    def _liberar_ficha_en_mano(self) -> None:
        """
        Cancela cualquier arrastre o selección en curso y devuelve la ficha a su
        origen. Sin esto, salir con ESC en mitad de un arrastre dejaba la ficha
        'flotando' en la última posición del cursor.
        """
        if self._dragged_tile is not None:
            self._dragged_tile.stop_drag()
            if self._dragged_tile.grid_pos is None:
                self._dragged_tile.reset_to_origin()
            self._dragged_tile = None

        if self._selected_tile is not None:
            self._selected_tile.selected = False
            self._selected_tile = None

        self._rearrange_rack_positions()

    def open_info(self) -> None:
        """Acción del botón: abre la ventana de información del juego."""
        self._sound_mgr.play_click()
        self._state = self.STATE_INFO

    def open_scores(self) -> None:
        """Acción del botón: abre la pantalla de puntuaciones máximas."""
        self._sound_mgr.play_click()
        self._state = self.STATE_SCORES

    def reset_scores(self) -> None:
        """Acción del botón: reinicia a 0 todas las puntuaciones máximas con sonido de acción."""
        self._high_scores.reset_all()
        self._sound_mgr.play_recall()

    def exit_game(self) -> None:
        """Acción del botón Salir: finaliza la ejecución de forma limpia y segura."""
        self._sound_mgr.play_click()
        self._running = False
        try:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        except Exception:
            pass

    def set_music_volume(self, value: float) -> None:
        """Ajusta el volumen de la música en tiempo real y sincroniza los deslizadores."""
        self._sound_mgr.set_volumen_musica(value)
        if hasattr(self, "_slider_music_menu") and abs(self._slider_music_menu.value - value) > 0.005:
            self._slider_music_menu.value = value
        if hasattr(self, "_slider_music_playing") and abs(self._slider_music_playing.value - value) > 0.005:
            self._slider_music_playing.value = value

    def _replenish_smart_rack(self, target_word: Optional[str] = None) -> None:
        """
        Genera un atril equilibrado garantizando la formación de al menos una palabra
        de la categoría activa, conservando las palabras fijadas en el tablero.
        """
        if not target_word:
            target_word = self._dict_checker.get_random_target_word(
                excluded_words=self._board_logic.formed_words
            )

        # Devolver fichas actuales del atril a la bolsa
        rack_tiles = self._rack_logic.clear()
        self._bag_logic.return_tiles(rack_tiles)
        # Conservar en visual_tiles únicamente las fichas fijadas en el tablero
        self._visual_tiles = [vt for vt in self._visual_tiles if getattr(vt, "locked", False)]

        # Extraer mano inteligente garantizada con balance armónico
        new_tiles = self._bag_logic.draw_guaranteed_hand(target_word, capacity=RACK_CAPACITY)
        for t in new_tiles:
            self._rack_logic.add_tile(t)
            self._visual_tiles.append(VisualTile(t.letter, t.id))

        self._rearrange_rack_positions()

    def _setup_initial_smart_rack(self) -> None:
        """Alias para inicialización del atril al comenzar categoría."""
        self._replenish_smart_rack()

    def renew_rack_tiles(self) -> None:
        """Acción del botón: baraja y renueva las fichas del atril sin alterar las palabras ya formadas en el tablero."""
        # 1. Recoger cualquier ficha que estuviera en el tablero en curso sin consolidar
        self.recall_tiles()

        # 2. Rellenar con nueva mano inteligente garantizada
        self._replenish_smart_rack()

        # 3. Sonido suave, partículas y retroalimentación
        self._active_hint_text = ""
        self._msg_banner.set_message("Atril renovado con letras nuevas.", kind="info", duration=4.0)
        self._sound_mgr.play_recall()
        self._effects_mgr.emit_hint_sparkle(RACK_X + 222, RACK_Y + 36)

    def _replenish_rack(self) -> None:
        """Extrae fichas de la bolsa lógica con balance vocales/consonantes y crea sus VisualTile."""
        needed = self._rack_logic.needed_count()
        if needed > 0:
            vowels = self._rack_logic.vowel_count
            consonants = self._rack_logic.consonant_count
            new_logic_tiles = self._bag_logic.draw_balanced_tiles(
                count=needed,
                current_vowels=vowels,
                current_consonants=consonants,
                total_target=RACK_CAPACITY
            )
            for t in new_logic_tiles:
                self._rack_logic.add_tile(t)
                v_tile = VisualTile(t.letter, t.id)
                self._visual_tiles.append(v_tile)

        self._rearrange_rack_positions()

    def _rearrange_rack_positions(self) -> None:
        """Calcula las posiciones centradas en pantalla para las fichas presentes en el atril."""
        rack_tiles = [vt for vt in self._visual_tiles if vt.grid_pos is None]
        count = len(rack_tiles)
        if count == 0:
            return

        spacing = 8
        total_width = count * TILE_SIZE + (count - 1) * spacing
        start_x = self._rack_view.rect.x + (self._rack_view.rect.width - total_width) // 2
        start_y = self._rack_view.rect.y + (self._rack_view.rect.height - TILE_SIZE) // 2

        for i, vt in enumerate(rack_tiles):
            if vt != self._dragged_tile:
                pos_x = start_x + i * (TILE_SIZE + spacing)
                pos_y = start_y
                vt.set_origin(pos_x, pos_y)

    def _update_sfx_button(self) -> None:
        """Actualiza la apariencia del botón SFX según su estado: iluminado si está activo, opaco si está inactivo."""
        if self._sound_mgr.sfx_enabled:
            # Iluminado / Activo: Fondo marfil claro, texto verde bosque y borde verde suave
            self._btn_audio.bg_color = (255, 252, 240)
            self._btn_audio.text_color = (35, 95, 60)
            self._btn_audio.border_color = (120, 180, 135)
        else:
            # Opaco / Inactivo: Fondo grisáceo apagado, texto de bajo contraste y borde neutro
            self._btn_audio.bg_color = (185, 178, 168)
            self._btn_audio.text_color = (125, 118, 110)
            self._btn_audio.border_color = (165, 158, 148)

    def toggle_sfx(self) -> None:
        """Alterna exclusivamente la activación de los efectos de sonido (SFX)."""
        self._sound_mgr.toggle_sfx()
        self._update_sfx_button()
        self._sound_mgr.play_click()

    # Alias de compatibilidad
    toggle_audio = toggle_sfx

    def validate_word(self) -> None:
        """Acción del botón: Valida la palabra colocada en el tablero con sonido y efectos."""
        placed_text = self._board_logic.get_placed_word_text()
        if not placed_text:
            # Diagnóstico concreto para que el jugador sepa qué corregir
            problema = self._board_logic.get_placement_issue()
            mensajes = {
                "vacio": "Coloca algunas letras en el tablero y vuelve a intentarlo.",
                "una_letra": "Con una sola letra aún no hay palabra. Añade alguna más.",
                "hueco": "Las letras deben quedar juntas, sin casillas vacías entre ellas.",
                "alineacion": "Coloca todas las letras en la misma fila o en la misma columna.",
            }
            self._msg_banner.set_message(
                mensajes.get(problema, "Acomoda las letras en línea para formar la palabra."),
                kind="info", duration=5.0
            )
            self._sound_mgr.play_click()
            return

        placed_upper = placed_text.strip().upper()

        # Validación estricta anti-repetición en el tablero 7x7
        if self._board_logic.is_word_formed(placed_upper):
            self._msg_banner.set_message(
                f"'{placed_upper}' ya la formaste antes. ¡Busca una nueva!",
                kind="aviso", duration=5.0
            )
            self._sound_mgr.play_invalid()
            return

        if self._dict_checker.is_valid_word(placed_upper):
            # Obtener fichas del turno actual para bloquearlas y emitir partículas de celebración
            current_turn_vts = [
                vt for vt in self._visual_tiles
                if vt.grid_pos is not None and not getattr(vt, "locked", False)
            ]
            placed_centers = [
                self._board_view.get_cell_center(vt.grid_pos[0], vt.grid_pos[1])
                for vt in current_turn_vts
            ]

            # Fijar permanentemente las fichas formadas en sus casillas del tablero
            for vt in current_turn_vts:
                vt.locked = True

            points = self._stats_logic.add_word_points(placed_upper)
            self._board_logic.consolidate_current_turn(placed_upper)
            self._card_score.set_value(f"{self._stats_logic.score} PTS")
            self._card_words.set_value(str(self._stats_logic.words_formed))

            # Actualizar récord de puntuación persistente en JSON
            current_cat = self._dict_checker.active_category or "Todas"
            self._high_scores.update(current_cat, self._stats_logic.score)

            self._active_hint_text = ""
            restantes = max(0, 7 - self._stats_logic.words_formed)
            if restantes > 0:
                self._msg_banner.set_message(
                    f"¡Muy bien! Formaste '{placed_upper}' (+{points} pts). "
                    f"Te {'queda' if restantes == 1 else 'quedan'} {restantes}.",
                    kind="exito", duration=6.0
                )
            else:
                self._msg_banner.set_message(
                    f"¡Excelente! '{placed_upper}' (+{points} pts).",
                    kind="exito", duration=6.0
                )

            # Reproducir acorde mayor armónico y emitir destellos de celebración
            self._sound_mgr.play_word_success()
            if placed_centers:
                self._effects_mgr.emit_word_celebration(placed_centers)

            # Deseleccionar si había selección activa
            if self._selected_tile:
                self._selected_tile.selected = False
                self._selected_tile = None

            # Rellenar atril con nuevas letras para que el jugador siga jugando
            # La partida termina al formar 7 palabras.
            if self._stats_logic.words_formed >= 7:
                current_cat = self._dict_checker.active_category or "Todas"
                self._high_scores.update(current_cat, self._stats_logic.score)
                self._state = self.STATE_GAME_OVER
                self._sound_mgr.play_word_success()
                return

            self._replenish_rack()
        else:
            self._msg_banner.set_message(
                f"'{placed_upper}' no está en esta categoría. ¡Prueba otra combinación, no pierdes puntos!",
                kind="aviso", duration=6.0
            )
            self._sound_mgr.play_invalid()

    def request_hint(self) -> None:
        """Acción del botón: Ofrece una sugerencia cognitiva constructiva con sonido y brillo."""
        # Considerar solo letras disponibles en el atril y fichas no fijadas del turno actual
        rack_letters = [vt.letter for vt in self._visual_tiles if vt.grid_pos is None]
        unlocked_placed = [
            vt.letter for vt in self._visual_tiles
            if vt.grid_pos is not None and not getattr(vt, "locked", False)
        ]
        all_letters = rack_letters + unlocked_placed

        hint = self._dict_checker.get_therapeutic_hint(
            all_letters,
            excluded_words=self._board_logic.formed_words
        )
        self._active_hint_text = hint or "Sin palabras posibles. ¡Pulsa 'RENOVAR ATRIL' para nuevas letras!"
        self._msg_banner.set_message("Tienes una pista nueva arriba.", kind="info", duration=4.0)
        self._sound_mgr.play_hint()
        self._effects_mgr.emit_hint_sparkle(175, 400)

    def recall_tiles(self) -> None:
        """Acción del botón: Regresa las fichas del turno actual al atril (las palabras fijadas se quedan en el tablero)."""
        tiles_to_recall = [
            vt for vt in self._visual_tiles
            if vt.grid_pos is not None and not getattr(vt, "locked", False)
        ]
        if not tiles_to_recall:
            self._msg_banner.set_message(
                "No hay fichas que recoger: el tablero solo tiene palabras ya logradas.",
                kind="info", duration=4.0
            )
            self._sound_mgr.play_click()
            return

        self._msg_banner.set_message("Fichas devueltas al atril.", kind="info", duration=3.0)
        self._sound_mgr.play_recall()
        self._board_logic.clear_current_turn_tiles()
        for vt in tiles_to_recall:
            vt.grid_pos = None
            vt.reset_to_origin()
            self._rack_logic.add_tile(vt)

        if self._selected_tile and not getattr(self._selected_tile, "locked", False):
            self._selected_tile.selected = False
            self._selected_tile = None

        self._rearrange_rack_positions()

    def _handle_tile_click(self, tile: VisualTile, mouse_pos: Tuple[int, int]) -> None:
        """
        Gestiona la interacción dual:
        - Si está fijada (palabra ya formada): Permanece fija en su posición del tablero.
        - Si está en el tablero y no está fijada: Un clic la devuelve inmediatamente al atril.
        - Si está en el atril: Permite arrastrarla o dejarla seleccionada por clic.
        """
        if getattr(tile, "locked", False):
            self._sound_mgr.play_click()
            return

        if tile.grid_pos is not None:
            # Regresar ficha no fijada del tablero al atril
            r, c = tile.grid_pos
            self._board_logic.remove_tile(r, c)
            self._rack_logic.add_tile(tile)
            tile.grid_pos = None
            if self._selected_tile == tile:
                self._selected_tile.selected = False
                self._selected_tile = None
            self._rearrange_rack_positions()
            self._sound_mgr.play_tile_pick()
            return

        # Ficha en el atril: activar arrastre y selección
        if self._selected_tile and self._selected_tile != tile:
            self._selected_tile.selected = False

        self._selected_tile = tile
        tile.selected = True

        self._dragged_tile = tile
        tile.start_drag(mouse_pos)
        self._sound_mgr.play_tile_pick()

    def _place_tile_on_cell(self, tile: VisualTile, row: int, col: int) -> bool:
        """
        Coloca una ficha en la casilla indicada del tablero, sincronizando el estado lógico,
        centrándola en la vista y emitiendo sonido.
        """
        if self._board_logic.place_tile(tile, row, col):
            self._rack_logic.remove_tile(tile)
            cx, cy = self._board_view.get_cell_center(row, col)
            tile.rect.center = (cx, cy)
            if self._selected_tile == tile:
                tile.selected = False
                self._selected_tile = None
            self._rearrange_rack_positions()
            self._sound_mgr.play_tile_place()
            return True
        return False

    def _handle_board_click_for_selection(self, row: int, col: int) -> None:
        """Coloca la ficha seleccionada por clic directo en la casilla indicada."""
        if self._selected_tile:
            self._place_tile_on_cell(self._selected_tile, row, col)

    def _handle_events(self) -> bool:
        """
        Procesa la cola de eventos de Pygame.
        Captura pygame.QUIT y la tecla ESC para romper el bucle interno o regresar
        al Menú Principal de forma segura y permitir el regreso al Launcher.
        """
        for event in pygame.event.get():
            if not self._running:
                return False

            if event.type == pygame.QUIT:
                self._running = False
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self._state != self.STATE_MENU:
                    self.open_menu()
                    return True
                else:
                    self._running = False
                    return False

            # Detección de fin de pista musical para avanzar en la rotación de pistas de fondo
            if event.type == pygame.USEREVENT + 1:
                self._sound_mgr.procesar_fin_pista()
                continue

            if self._state == self.STATE_MENU:
                if self._btn_menu_exit.handle_event(event):
                    self._running = False
                    return False
                if any(e.handle_event(event) for e in (
                    self._btn_audio, self._btn_menu_play, self._btn_menu_info,
                    self._btn_menu_scores, self._slider_music_menu
                )):
                    continue

            elif self._state == self.STATE_INFO:
                if any(e.handle_event(event) for e in (
                    self._btn_audio, self._btn_info_back
                )):
                    continue

            elif self._state == self.STATE_SCORES:
                if any(e.handle_event(event) for e in (
                    self._btn_audio, self._btn_scores_reset, self._btn_scores_back
                )):
                    continue

            elif self._state == self.STATE_CATEGORY_SELECT:
                # 3. Eventos en pantalla de selección de categorías (Diseño Con interfaz)
                if self._category_view.handle_event(event):
                    continue

            elif self._state == self.STATE_GAME_OVER:
                if any(e.handle_event(event) for e in (
                    self._btn_end_again, self._btn_end_menu, self._btn_end_exit, self._btn_audio
                )):
                    continue

            elif self._state == self.STATE_PLAYING:
                # 4. Eventos en pantalla del tablero de juego
                consumed = False
                for elem in self._static_ui_elements:
                    if elem.handle_event(event):
                        consumed = True
                        break

                if consumed:
                    continue

                # Gestión de ratón para Fichas y Tablero
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos

                    # Comprobar si se hace clic en alguna ficha
                    clicked_tile = None
                    for vt in reversed(self._visual_tiles):
                        if vt.rect.collidepoint(mouse_pos):
                            clicked_tile = vt
                            break

                    if clicked_tile:
                        self._handle_tile_click(clicked_tile, mouse_pos)
                    else:
                        # Si hay una ficha seleccionada y se hace clic en una casilla vacía
                        cell = self._board_view.get_cell_from_pos(mouse_pos)
                        if cell and self._selected_tile:
                            r, c = cell
                            self._handle_board_click_for_selection(r, c)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self._dragged_tile:
                        tile = self._dragged_tile
                        tile.stop_drag()
                        self._dragged_tile = None

                        cell = self._board_view.get_cell_from_pos(event.pos)
                        if cell and self._place_tile_on_cell(tile, cell[0], cell[1]):
                            continue

                        # Si no cayó en casilla válida, regresa a su origen
                        if tile.grid_pos is None:
                            tile.reset_to_origin()
                            self._sound_mgr.play_click()

                elif event.type == pygame.MOUSEMOTION:
                    if self._dragged_tile:
                        self._dragged_tile.update_drag(event.pos)

        return self._running

    def _render(self) -> None:
        """Renderiza la escena correspondiente a 1280x720 con fondo artístico a 60 FPS."""
        if self._bg_image:
            self._screen.blit(self._bg_image, (0, 0))
        else:
            self._screen.fill(COLOR_BG)

        if self._state == self.STATE_MENU:
            self._render_menu_screen()
        elif self._state == self.STATE_INFO:
            self._render_info_screen()
        elif self._state == self.STATE_SCORES:
            self._render_scores_screen()
        elif self._state == self.STATE_CATEGORY_SELECT:
            self._render_category_screen()
        elif self._state == self.STATE_GAME_OVER:
            self._render_game_over_screen()
        else:
            self._render_playing_screen()

        # Partículas y efectos visuales sobreimpresos
        self._effects_mgr.draw(self._screen)

        pygame.display.flip()

    def _render_menu_screen(self) -> None:
        """Renderiza el Menú Principal interactivo con tarjeta translúcida y control de volumen."""
        # 1. Contenedor central (tarjeta estilo glassmorphism)
        card_w, card_h = 520, 560
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = 65
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        if self._bg_image:
            self._screen.blit(self._menu_card_surf, (card_x, card_y))
        else:
            pygame.draw.rect(self._screen, COLOR_PANEL, card_rect, border_radius=24)
            pygame.draw.rect(self._screen, COLOR_CELL_BORDER, card_rect, width=2, border_radius=24)

        # 2. Títulos y lema del juego
        title_surf = self._font_menu_title.render("LETRA A LETRA", True, (37, 91, 72))
        t_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 45))
        self._screen.blit(title_surf, t_rect)

        sub_surf = self._font_menu_sub.render("PEQUEÑAS PALABRAS, GRANDES CONEXIONES", True, COLOR_BTN_HINT)
        s_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, card_y + 85))
        self._screen.blit(sub_surf, s_rect)

        # Línea divisoria decorativa
        div_y = card_y + 115
        pygame.draw.line(self._screen, (215, 205, 190), (card_x + 40, div_y), (card_x + card_w - 40, div_y), 2)

        # 3. Botones del Menú Principal
        self._btn_menu_play.draw(self._screen)
        self._btn_menu_info.draw(self._screen)
        self._btn_menu_scores.draw(self._screen)
        self._btn_menu_exit.draw(self._screen)

        # 4. Contenedor y Deslizador de Volumen
        slider_box = pygame.Rect(card_x + 35, card_y + 420, card_w - 70, 96)
        pygame.draw.rect(self._screen, (240, 234, 224), slider_box, border_radius=14)
        pygame.draw.rect(self._screen, (210, 200, 185), slider_box, width=1, border_radius=14)

        self._slider_music_menu.draw(self._screen)

        # Botón de Sonido en el header superior
        self._btn_audio.draw(self._screen)

    def _render_scores_screen(self) -> None:
        """Renderiza la pantalla de puntuaciones máximas por categoría temática."""
        # 1. Encabezado superior translúcido
        if self._bg_image:
            self._screen.blit(self._scores_hdr_surf, (0, 0))
        else:
            pygame.draw.rect(self._screen, COLOR_PANEL, pygame.Rect(0, 0, SCREEN_WIDTH, 115))

        pygame.draw.line(self._screen, COLOR_CELL_BORDER, (0, 115), (SCREEN_WIDTH, 115), 2)

        title_surf = self._font_scores_title.render("PUNTUACIONES MÁXIMAS", True, COLOR_TEXT_DARK)
        t_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 42))
        self._screen.blit(title_surf, t_rect)

        sub_surf = self._font_scores_sub.render(
            "Récord de puntos alcanzado por categoría temática",
            True, COLOR_INFO
        )
        s_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 82))
        self._screen.blit(sub_surf, s_rect)

        # Botón de audio en la esquina superior
        self._btn_audio.draw(self._screen)

        # 2. Tarjetas de categorías con puntuaciones
        categories = self._dict_checker.categories

        card_w = 420
        card_h = 74
        col_x = [200, 660]
        row_y = [140, 230, 320]

        for idx, cat in enumerate(categories):
            col = idx % 2
            row = idx // 2
            x = col_x[col]
            y = row_y[row] if row < len(row_y) else 140 + row * 90
            box = pygame.Rect(x, y, card_w, card_h)

            meta = CATEGORY_MAP.get(cat.lower(), {"title": cat.capitalize(), "color": (70, 90, 110)})
            display_title = meta["title"]
            accent = meta["color"]

            if self._bg_image:
                card_s = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(card_s, (248, 245, 238, 230), card_s.get_rect(), border_radius=14)
                pygame.draw.rect(card_s, accent, card_s.get_rect(), width=2, border_radius=14)
                self._screen.blit(card_s, (x, y))
            else:
                pygame.draw.rect(self._screen, COLOR_PANEL, box, border_radius=14)
                pygame.draw.rect(self._screen, accent, box, width=2, border_radius=14)

            # Franja lateral de color de acento
            bar = pygame.Rect(x + 10, y + 10, 6, card_h - 20)
            pygame.draw.rect(self._screen, accent, bar, border_radius=3)

            # Nombre de categoría
            name_surf = self._font_scores_cat.render(display_title, True, COLOR_TEXT_DARK)
            self._screen.blit(name_surf, (x + 28, y + 24))

            # Puntuación máxima
            score_val = max(self._high_scores.get_score(cat), self._high_scores.get_score(display_title))
            score_surf = self._font_scores_pts.render(f"{score_val} PTS", True, accent)
            s_rect = score_surf.get_rect(right=x + card_w - 20, centery=y + card_h // 2)
            self._screen.blit(score_surf, s_rect)

        # Tarjeta para Modo Completo (Todas)
        all_w = 680
        all_h = 72
        all_x = (SCREEN_WIDTH - all_w) // 2
        all_y = 425
        all_box = pygame.Rect(all_x, all_y, all_w, all_h)
        all_accent = (90, 70, 150)

        if self._bg_image:
            self._screen.blit(self._scores_all_surf, (all_x, all_y))
        else:
            pygame.draw.rect(self._screen, COLOR_PANEL, all_box, border_radius=14)
            pygame.draw.rect(self._screen, all_accent, all_box, width=2, border_radius=14)

        bar_all = pygame.Rect(all_x + 10, all_y + 10, 6, all_h - 20)
        pygame.draw.rect(self._screen, all_accent, bar_all, border_radius=3)

        name_all = self._font_scores_cat.render("Todas las Categorías (Modo Completo)", True, COLOR_TEXT_DARK)
        self._screen.blit(name_all, (all_x + 28, all_y + 23))

        score_all_val = max(self._high_scores.get_score("Todas"), self._high_scores.get_score("todas"))
        score_all_surf = self._font_scores_pts.render(f"{score_all_val} PTS", True, all_accent)
        sa_rect = score_all_surf.get_rect(right=all_x + all_w - 20, centery=all_y + all_h // 2)
        self._screen.blit(score_all_surf, sa_rect)

        # 3. Botones inferiores de acción
        self._btn_scores_reset.draw(self._screen)
        self._btn_scores_back.draw(self._screen)

    def _render_category_screen(self) -> None:
        """Renderiza la pantalla de selección de categorías con el diseño visual de 'Con interfaz'."""
        self._category_view.draw(self._screen)

    def _render_game_over_screen(self) -> None:
        """Renderiza el resultado final después de formar 7 palabras."""
        card_w, card_h = 620, 570
        card_x = (SCREEN_WIDTH - card_w) // 2
        card_y = 70
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

        pygame.draw.rect(self._screen, (248, 245, 238), card_rect, border_radius=24)
        pygame.draw.rect(self._screen, COLOR_LINE, card_rect, width=2, border_radius=24)

        title = self._font_menu_title.render("¡PARTIDA TERMINADA!", True, (37, 91, 72))
        self._screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 130)))

        cat = self._dict_checker.active_category or "Todas"
        meta = CATEGORY_MAP.get(str(cat).lower())
        cat_title = meta["title"] if meta else cat
        sub = self._font_menu_sub.render(f"Categoría: {cat_title}", True, COLOR_TEXT_DARK)
        self._screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 175)))

        score = self._font_scores_title.render(f"{self._stats_logic.score} PTS", True, COLOR_BTN_PRIMARY)
        self._screen.blit(score, score.get_rect(center=(SCREEN_WIDTH // 2, 235)))

        words = self._font_scores_sub.render("7 palabras formadas", True, COLOR_TEXT_DARK)
        self._screen.blit(words, words.get_rect(center=(SCREEN_WIDTH // 2, 275)))

        self._btn_end_again.draw(self._screen)
        self._btn_end_menu.draw(self._screen)
        self._btn_end_exit.draw(self._screen)
        self._btn_audio.draw(self._screen)

    def _render_playing_screen(self) -> None:
        """Renderiza el tablero de juego y la interfaz activa a 1280x720."""
        # 1. Encabezado superior centrado sobre el fondo artístico tal como en 'Con interfaz' (pre-renderizado)
        self._screen.blit(self._surf_play_title, self._rect_play_title)
        self._screen.blit(self._surf_play_sub, self._rect_play_sub)

        # 2. Panel Lateral Izquierdo (Métricas, Pistas, Botón Categorías y Volumen)
        panel_left = pygame.Rect(28, 105, 294, 580)
        pygame.draw.rect(self._screen, COLOR_PANEL, panel_left, border_radius=20)
        pygame.draw.rect(self._screen, COLOR_LINE, panel_left, width=2, border_radius=20)

        # 3. Panel Lateral Derecho: Recuadro "¿CÓMO JUGAR?" (Diseño Con interfaz)
        panel_right = pygame.Rect(880, 105, 365, 255)
        pygame.draw.rect(self._screen, COLOR_PANEL, panel_right, border_radius=20)
        pygame.draw.rect(self._screen, COLOR_LINE, panel_right, width=2, border_radius=20)

        self._screen.blit(self._surf_help_title, self._rect_help_title)
        for num_surf, pos_num, txt_surf, pos_txt in self._help_items_surfs:
            self._screen.blit(num_surf, pos_num)
            self._screen.blit(txt_surf, pos_txt)

        self._screen.blit(self._surf_help_motiv, self._rect_help_motiv)

        # Indicador de orientación justo encima del tablero.
        direction_font = get_sys_font(13, bold=True)
        direction_label = direction_font.render("DIRECCIÓN:", True, COLOR_TEXT_DARK)
        self._screen.blit(direction_label, (422, 79))
        # 4. Dibujar Elementos Polimórficos Estáticos (tablero, atril, cartas, botones y slider)
        for elem in self._static_ui_elements:
            elem.draw(self._screen)

        # Tarjeta de Pista Activa en panel izquierdo (si está activa)
        if self._active_hint_text:
            hint_rect = pygame.Rect(45, 312, 260, 140)
            pygame.draw.rect(self._screen, COLOR_HINT_BOX, hint_rect, border_radius=12)
            pygame.draw.rect(self._screen, (228, 197, 115), hint_rect, width=2, border_radius=12)

            self._screen.blit(self._surf_hint_title, (55, 322))

            words = self._active_hint_text.split()
            line, lines = "", []
            for word in words:
                test = (line + " " + word).strip()
                if len(test) > 30:
                    lines.append(line)
                    line = word
                else:
                    line = test
            if line:
                lines.append(line)
            for i, text in enumerate(lines[:5]):
                surf = self._font_hint_body.render(text, True, COLOR_TEXT_DARK)
                self._screen.blit(surf, (55, 345 + i * 18))

        # 4. Dibujar Fichas: Primero las colocadas y atril, luego la arrastrada arriba
        for vt in self._visual_tiles:
            if vt != self._dragged_tile:
                vt.draw(self._screen)

        if self._dragged_tile:
            self._dragged_tile.draw(self._screen)

        # Las partículas y el volcado a pantalla (flip) los realiza _render():
        # hacerlo también aquí duplicaba el dibujado de efectos y el flip por frame.

    def run(self) -> None:
        """
        Bucle principal de juego con control estricto a 60 FPS (clock.tick(60)).
        Al interrumpirse por el evento QUIT o la tecla ESC, limpia la ventana y
        cierra de forma segura con pygame.quit() y devuelve el control al Launcher.
        """
        self._running = True
        # Iniciar reproducción de los archivos .mp3 de la carpeta music como música de fondo
        self._sound_mgr.reproducir_musica()

        try:
            while self._running:
                # Control estricto a 60 FPS requerido
                dt = self._clock.tick(60) / 1000.0

                # Despacho de eventos (captura QUIT, ESC y fin de pista USEREVENT+1)
                self._running = self._handle_events()

                # Comprobación de reproducción continua de música
                self._sound_mgr.actualizar()

                # Actualización de efectos visuales, animaciones y mensajes
                self._effects_mgr.update(dt)
                self._msg_banner.update(dt)

                # Renderizado
                self._render()
        finally:
            self._sound_mgr.detener_musica()
            pygame.quit()
            # Se retorna el control a main.py / al launcher en vez de llamar a
            # sys.exit(), que terminaría el proceso anfitrión por completo.

    def ejecutar(self) -> None:
        """Alias para el método run()."""
        self.run()

    @property
    def gestor_audio(self) -> GestorAudio:
        """Acceso al gestor de audio del juego."""
        return self._sound_mgr


# --- Alias para máxima compatibilidad ---
ManejadorJuego = UIManager

