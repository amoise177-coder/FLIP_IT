"""
MenteActiva — Pantalla de Menú Principal
Interfaz accesible con pantalla de inicio, selección de dificultad y tema.
Diseñada con botones grandes, alto contraste, fondo decorativo y navegación clara.
"""
import math
import random
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, Colors,
    DifficultyLevel, DIFFICULTY_CONFIGS, THEMES, ScreenName,
)
from ui.renderer import (
    draw_text, draw_text_shadow, draw_background,
    draw_panel, Boton, reset_cursor, get_font,
)
from utils.icon_drawer import draw_icon


# ═══════════════════════════════════════════════════════════════════════════════
#  ELEMENTOS DECORATIVOS DE FONDO
# ═══════════════════════════════════════════════════════════════════════════════

class _FloatingIcon:
    """Ícono decorativo flotante para el fondo del menú."""

    def __init__(self):
        self.icon = random.choice([
            "sol", "luna", "flor", "arbol", "nube", "estrella", "gota",
            "manzana", "cafe", "uva", "helado", "galleta",
            "gato", "mariposa", "pez", "conejo", "abeja",
            "casa", "libro", "corazon", "reloj", "lampara",
        ])
        self.x = random.randint(30, WINDOW_WIDTH - 30)
        self.y = random.randint(30, WINDOW_HEIGHT - 30)
        self.size = random.randint(14, 28)
        self.speed_x = random.uniform(-0.15, 0.15)
        self.speed_y = random.uniform(-0.1, 0.1)
        self.bob_speed = random.uniform(0.4, 1.2)
        self.bob_amp = random.uniform(4, 12)
        self.phase = random.uniform(0, math.pi * 2)
        self.alpha = random.randint(40, 100)
        self.color = random.choice([
            Colors.LAVENDER, Colors.CORAL, Colors.SAGE_GREEN,
            Colors.GOLD, Colors.SKY_BLUE, Colors.WARM_ROSE,
            Colors.TEAL,
        ])

    def update(self, dt):
        self.x += self.speed_x * 60 * dt
        self.y += self.speed_y * 60 * dt
        # Wrap around
        if self.x < -40:
            self.x = WINDOW_WIDTH + 40
        elif self.x > WINDOW_WIDTH + 40:
            self.x = -40
        if self.y < -40:
            self.y = WINDOW_HEIGHT + 40
        elif self.y > WINDOW_HEIGHT + 40:
            self.y = -40

    def draw(self, surface, t):
        offset_y = math.sin(t * self.bob_speed + self.phase) * self.bob_amp
        # Dibujar en superficie con alpha para dar sensación suave
        icon_surf = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        cx = self.size * 3 // 2
        cy = self.size * 3 // 2
        # Aplicar alpha al color
        faded_color = (*self.color[:3],)
        draw_icon(icon_surf, self.icon, cx, cy, self.size, faded_color)
        # Aplicar transparencia general
        icon_surf.set_alpha(self.alpha)
        surface.blit(icon_surf, (int(self.x - cx), int(self.y + offset_y - cy)))


class _BubbleDecor:
    """Burbuja/círculo decorativo suave para el fondo."""

    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT)
        self.radius = random.randint(30, 120)
        self.color = random.choice([
            (184, 169, 201), (232, 144, 126), (168, 213, 186),
            (242, 201, 76), (135, 206, 235), (212, 160, 160),
        ])
        self.alpha = random.randint(15, 35)
        self.bob_speed = random.uniform(0.3, 0.8)
        self.phase = random.uniform(0, math.pi * 2)

    def draw(self, surface, t):
        offset_y = math.sin(t * self.bob_speed + self.phase) * 6
        surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, self.alpha),
                           (self.radius, self.radius), self.radius)
        surface.blit(surf, (self.x - self.radius, int(self.y + offset_y) - self.radius))


# ═══════════════════════════════════════════════════════════════════════════════
#  PANTALLA DE MENÚ
# ═══════════════════════════════════════════════════════════════════════════════

class PantallaMenu:
    """
    Menú principal con flujo de selección paso a paso:
        0. Pantalla de inicio (Jugar / Salir)
        1. Selección de Dificultad (Fácil / Medio / Desafiante)
        2. Selección de Tema (Naturaleza / Alimentos / Animales / Hogar)
    """

    def __init__(self):
        self._paso = 0  # 0=inicio, 1=dificultad, 2=tema
        self._dificultad_seleccionada = None
        self._tema_seleccionado = None
        self._quiere_salir = False

        self._botones = []
        self._boton_volver = None
        self._animacion_timer = 0.0

        # ── Decoraciones de fondo ──
        self._floating_icons = [_FloatingIcon() for _ in range(18)]
        self._bubbles = [_BubbleDecor() for _ in range(8)]

        # ── Caché del fondo decorativo ──
        self._bg_cached = None
        self._bg_size = None

        self._construir_paso_inicio()

    # ── Construcción de botones por paso ─────────────────────────────────

    def _construir_paso_inicio(self):
        """Construye la pantalla de inicio con Jugar y Salir."""
        self._paso = 0
        self._botones = []

        center_x = WINDOW_WIDTH // 2

        # Botón Jugar — grande y llamativo con color vivo
        btn_w = 320
        btn_h = 80
        self._botones.append(Boton(
            center_x - btn_w // 2, 400,
            btn_w, btn_h,
            "Jugar",
            color=(80, 210, 120),
            text_color=Colors.SOFT_BLACK,
            font_key="heading",
            on_click=lambda: self._ir_a_dificultad(),
        ))

        # Botón Salir — color vivo pero distinguible
        btn_w_exit = 200
        btn_h_exit = 55
        self._botones.append(Boton(
            center_x - btn_w_exit // 2, 510,
            btn_w_exit, btn_h_exit,
            "Salir",
            color=(240, 120, 120),
            text_color=Colors.SOFT_BLACK,
            font_key="button",
            on_click=lambda: self._solicitar_salir(),
        ))

        self._boton_volver = None

    def _construir_paso_dificultad(self):
        """Construye los botones del paso de selección de dificultad."""
        self._paso = 1
        self._botones = []

        btn_w = 420
        btn_h = 85
        center_x = WINDOW_WIDTH // 2
        start_y = 290

        configs = [
            (DifficultyLevel.EASY, "Facil  -  Tablero 2x3"),
            (DifficultyLevel.MEDIUM, "Intermedio  -  Tablero 3x4"),
            (DifficultyLevel.HARD, "Avanzado  -  Tablero 4x4"),
        ]

        for i, (level, label) in enumerate(configs):
            cfg = DIFFICULTY_CONFIGS[level]
            self._botones.append(Boton(
                center_x - btn_w // 2, start_y + i * (btn_h + 20),
                btn_w, btn_h,
                label,
                color=cfg.color,
                text_color=Colors.SOFT_BLACK,
                on_click=lambda lv=level: self._seleccionar_dificultad(lv),
            ))

        # Botón volver
        self._boton_volver = Boton(
            30, WINDOW_HEIGHT - 70, 140, 45, "Volver",
            color=(200, 195, 210),
            text_color=Colors.DARK_TEXT,
            font_key="small",
            on_click=self._volver,
        )

    def _construir_paso_tema(self):
        """Construye los botones del paso de selección de tema."""
        self._paso = 2
        self._botones = []

        btn_w = 260
        btn_h = 75
        total_w = btn_w * 2 + 30
        start_x = (WINDOW_WIDTH - total_w) // 2
        start_y = 300

        temas = [
            ("naturaleza", "Naturaleza"),
            ("alimentos", "Alimentos"),
            ("animales", "Animales"),
            ("hogar", "Hogar"),
        ]

        for i, (key, label) in enumerate(temas):
            col = i % 2
            row = i // 2
            x = start_x + col * (btn_w + 30)
            y = start_y + row * (btn_h + 20)
            tema_data = THEMES[key]

            self._botones.append(Boton(
                x, y, btn_w, btn_h,
                label,
                color=tema_data["color"],
                text_color=Colors.SOFT_BLACK,
                on_click=lambda k=key: self._seleccionar_tema(k),
            ))

        # Botón volver
        self._boton_volver = Boton(
            30, WINDOW_HEIGHT - 70, 140, 45, "Volver",
            color=(200, 195, 210),
            text_color=Colors.DARK_TEXT,
            font_key="small",
            on_click=self._volver,
        )

    # ── Acciones de selección ────────────────────────────────────────────

    def _ir_a_dificultad(self):
        self._construir_paso_dificultad()

    def _solicitar_salir(self):
        self._quiere_salir = True

    def _seleccionar_dificultad(self, dificultad):
        self._dificultad_seleccionada = dificultad
        self._construir_paso_tema()

    def _seleccionar_tema(self, tema):
        self._tema_seleccionado = tema

    def _volver(self):
        if self._paso == 2:
            self._construir_paso_dificultad()
        elif self._paso == 1:
            self._construir_paso_inicio()

    # ── Interfaz de pantalla ─────────────────────────────────────────────

    def handle_event(self, event):
        """
        Procesa eventos. Retorna (ScreenName.GAME, data) cuando
        se completa la selección, o None.
        """
        # Salir del juego
        if self._quiere_salir:
            self._quiere_salir = False
            return (ScreenName.QUIT, None)

        # Verificar si se completó la selección de tema
        if self._tema_seleccionado:
            data = {
                "dificultad": self._dificultad_seleccionada,
                "tema": self._tema_seleccionado,
            }
            self._tema_seleccionado = None
            return (ScreenName.GAME, data)

        # Tecla Escape para volver
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self._paso > 0:
                self._volver()
                return None

        # Botones
        for btn in self._botones:
            btn.handle_event(event)

        if self._boton_volver:
            self._boton_volver.handle_event(event)

        return None

    def update(self, dt):
        """Actualiza animaciones y estados de hover."""
        self._animacion_timer += dt
        mouse_pos = pygame.mouse.get_pos()

        reset_cursor()

        for btn in self._botones:
            btn.update(dt, mouse_pos)

        if self._boton_volver:
            self._boton_volver.update(dt, mouse_pos)

        # Actualizar íconos flotantes
        for icon in self._floating_icons:
            icon.update(dt)

        return None

    def draw(self, surface):
        """Dibuja la pantalla de menú."""
        draw_background(surface)

        # ── Burbujas decorativas ──
        t = self._animacion_timer
        for bubble in self._bubbles:
            bubble.draw(surface, t)

        # ── Íconos flotantes de fondo ──
        for icon in self._floating_icons:
            icon.draw(surface, t)

        # ── Título decorativo ──
        self._draw_title(surface, t)

        # ── Contenido según paso ──
        if self._paso == 0:
            self._draw_home_content(surface)
        elif self._paso == 1:
            self._draw_difficulty_content(surface)
        elif self._paso == 2:
            self._draw_theme_content(surface)

        # ── Botones ──
        for btn in self._botones:
            btn.draw(surface)

        if self._boton_volver:
            self._boton_volver.draw(surface)

    def _draw_title(self, surface, t):
        """Dibuja el título principal con estilo decorativo y colorido."""
        title_y = 90 if self._paso == 0 else 70

        # ── Título principal: "MenteActiva" con colores por letra ──
        title_text = "MenteActiva"
        # Colores más vivos y saturados para el título
        title_colors = [
            (255, 90, 70), (255, 90, 70), (255, 90, 70), (255, 90, 70), (255, 90, 70),
            (0, 190, 190), (0, 190, 190), (0, 190, 190), (0, 190, 190), (0, 190, 190), (0, 190, 190),
        ]

        # Renderizar letra por letra con colores diferentes
        font_size = 72 if self._paso == 0 else 60
        font = get_font(font_size, bold=True)
        total_width = font.size(title_text)[0]
        start_x = WINDOW_WIDTH // 2 - total_width // 2

        # Sombra del título
        shadow_font = get_font(font_size, bold=True)
        shadow_surf = shadow_font.render(title_text, True, (60, 60, 70))
        shadow_rect = shadow_surf.get_rect()
        shadow_rect.midleft = (start_x + 3, title_y + 3)
        surface.blit(shadow_surf, shadow_rect)

        # Renderizar cada carácter con su color
        cursor_x = start_x
        for i, char in enumerate(title_text):
            color = title_colors[i % len(title_colors)]
            # Ligero rebote individual
            bounce = math.sin(t * 2.5 + i * 0.4) * 2
            char_surf = font.render(char, True, color)
            surface.blit(char_surf, (cursor_x, title_y - font_size // 2 + int(bounce)))
            cursor_x += char_surf.get_width()

        # ── Subtítulo ──
        sub_y = title_y + (font_size // 2) + 15
        # Línea decorativa antes del subtítulo
        line_w = 180
        line_y = sub_y - 8
        pygame.draw.line(surface, (*Colors.LAVENDER, ),
                         (WINDOW_WIDTH // 2 - line_w, line_y),
                         (WINDOW_WIDTH // 2 + line_w, line_y), 1)

        sub_font = get_font(22, bold=True)
        sub_text = "Memoria Sensorial  -  Estimulacion Cognitiva"
        sub_surf = sub_font.render(sub_text, True, Colors.DARK_TEXT)
        sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, sub_y + 5))
        surface.blit(sub_surf, sub_rect)

        # Línea decorativa después
        line_y2 = sub_y + 20
        pygame.draw.line(surface, (*Colors.LAVENDER, ),
                         (WINDOW_WIDTH // 2 - line_w, line_y2),
                         (WINDOW_WIDTH // 2 + line_w, line_y2), 1)

    def _draw_home_content(self, surface):
        """Dibuja el contenido de la pantalla de inicio."""
        # Descripción motivacional centrada
        desc_y = 340
        draw_text(surface, "Ejercita tu memoria de forma divertida",
                  WINDOW_WIDTH // 2, desc_y, "body", Colors.DARK_TEXT)

        # Texto informativo debajo de los botones
        info_y = 600
        draw_text(surface, "Pistas automaticas - Sin presion - A tu ritmo",
                  WINDOW_WIDTH // 2, info_y, "small", Colors.DARK_TEXT)
        draw_text(surface, "Disenado para estimulacion cognitiva",
                  WINDOW_WIDTH // 2, info_y + 25, "tiny", Colors.DARK_TEXT)

    def _draw_difficulty_content(self, surface):
        """Dibuja encabezado y contexto del paso de dificultad."""
        draw_text(surface, "Selecciona la dificultad",
                  WINDOW_WIDTH // 2, 210, "heading", Colors.DARK_TEXT, bold=True)

        # Indicador de paso
        self._draw_step_indicator(surface, 0)

        # Descripción inferior
        desc_y = 610
        draw_text(surface, "Las pistas se activan automaticamente cuando las necesites",
                  WINDOW_WIDTH // 2, desc_y, "small", Colors.DARK_TEXT)
        draw_text(surface, "La dificultad solo cambia el tamanio del tablero",
                  WINDOW_WIDTH // 2, desc_y + 28, "small", Colors.DARK_TEXT)

    def _draw_theme_content(self, surface):
        """Dibuja encabezado y contexto del paso de tema."""
        draw_text(surface, "Selecciona el tema",
                  WINDOW_WIDTH // 2, 210, "heading", Colors.DARK_TEXT, bold=True)

        # Indicador de paso
        self._draw_step_indicator(surface, 1)

    def _draw_step_indicator(self, surface, active_step):
        """Dibuja el indicador de progreso (2 puntos) para dificultad/tema."""
        y = 245
        dot_spacing = 30
        start_x = WINDOW_WIDTH // 2 - dot_spacing // 2

        for i in range(2):
            x = start_x + i * dot_spacing
            if i == active_step:
                pygame.draw.circle(surface, Colors.CORAL, (x, y), 6)
            elif i < active_step:
                pygame.draw.circle(surface, Colors.SAGE_GREEN, (x, y), 5)
            else:
                pygame.draw.circle(surface, Colors.LIGHT_TEXT, (x, y), 4)

    def reset(self):
        """Reinicia el menú al paso inicial."""
        self._paso = 0
        self._dificultad_seleccionada = None
        self._tema_seleccionado = None
        self._quiere_salir = False
        self._construir_paso_inicio()
