"""
Módulo de entidades del juego: Tablero, Serpientes, Escaleras y Jugadores.
Incluye animaciones pausadas, fluidas y visualmente detalladas:
- Salto elástico paso a paso (walk).
- Escalada peldaño a peldaño en escaleras con destellos mágicos.
- Deslizamiento suave por las curvas de la serpiente con estela de partículas.
"""
import math
import random
from typing import List, Dict, Tuple, Optional
import pygame

from constants import (
    GRID_COLS, GRID_ROWS, TOTAL_TILES,
    COLOR_BOARD_BG, COLOR_PANEL_BORDER, TILE_PALETTE,
    COLOR_TILE_START, COLOR_TILE_END, COLOR_TILE_BORDER,
    COLOR_TEXT_DARK, COLOR_SNAKE, COLOR_SNAKE_HEAD,
    COLOR_SNAKE_BELLY, COLOR_LADDER, COLOR_LADDER_RAIL, COLOR_LADDER_RUNG,
    SPEED_WALK, SPEED_LADDER, SPEED_SNAKE
)
from assets import AssetManager
from particles import ParticleManager


class Snake:
    """Representa una serpiente con cuerpo ondulado y puntos de deslizamiento."""
    def __init__(self, head: int, tail: int):
        if head <= tail:
            raise ValueError("La cabeza debe ser mayor que la cola.")
        self.head = head
        self.tail = tail

    def get_curve_points(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                         segments: int = 30) -> List[Tuple[float, float]]:
        """Calcula los puntos precisos a lo largo del cuerpo ondulado de la serpiente."""
        x1, y1 = start_pos  # Cabeza
        x2, y2 = end_pos    # Cola

        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        angle = math.atan2(dy, dx)
        perp_x = -math.sin(angle)
        perp_y = math.cos(angle)

        wave_freq = 3.2
        wave_amp = min(22.0, dist * 0.14)

        points: List[Tuple[float, float]] = []
        for i in range(segments + 1):
            t = i / segments
            base_x = x1 + dx * t
            base_y = y1 + dy * t
            envelope = math.sin(t * math.pi)
            offset = math.sin(t * math.pi * wave_freq) * wave_amp * envelope
            px = base_x + perp_x * offset
            py = base_y + perp_y * offset
            points.append((px, py))
        return points

    def draw(self, surface: pygame.Surface, start_pos: Tuple[int, int], end_pos: Tuple[int, int]):
        """Renderizado colorido, con bandas y detalles expresivos."""
        points = self.get_curve_points(start_pos, end_pos)
        if len(points) < 2:
            return

        # 1. Sombra suave profunda
        shadow_points = [(p[0] + 3, p[1] + 4) for p in points]
        pygame.draw.lines(surface, (10, 15, 25, 90), False, shadow_points, 12)

        # 2. Cuerpo base colorido
        pygame.draw.lines(surface, COLOR_SNAKE, False, points, 10)

        # 3. Rayas decorativas / vientre amarillo
        belly_points = [(p[0], p[1]) for p in points]
        pygame.draw.lines(surface, COLOR_SNAKE_BELLY, False, belly_points, 4)

        # 4. Cabeza
        x1, y1 = start_pos
        angle = math.atan2(points[1][1] - y1, points[1][0] - x1)
        perp_x = -math.sin(angle)
        perp_y = math.cos(angle)

        # Lengua bífida
        tongue_len = 8
        tx = x1 - math.cos(angle) * tongue_len
        ty = y1 - math.sin(angle) * tongue_len
        pygame.draw.line(surface, (255, 50, 80), (x1, y1), (tx, ty), 2)

        # Cabeza redonda
        pygame.draw.circle(surface, COLOR_SNAKE_HEAD, (int(x1), int(y1)), 11)
        pygame.draw.circle(surface, (255, 220, 230), (int(x1), int(y1)), 5)

        # Ojos saltones
        e1 = (int(x1 + perp_x * 5), int(y1 + perp_y * 5))
        e2 = (int(x1 - perp_x * 5), int(y1 - perp_y * 5))
        pygame.draw.circle(surface, (255, 255, 255), e1, 4)
        pygame.draw.circle(surface, (255, 255, 255), e2, 4)
        pygame.draw.circle(surface, (20, 20, 30), e1, 2)
        pygame.draw.circle(surface, (20, 20, 30), e2, 2)


class Ladder:
    """Representa una escalera dorada con peldaños regulares para escalada."""
    def __init__(self, bottom: int, top: int):
        if bottom >= top:
            raise ValueError("La base debe ser menor que la cima.")
        self.bottom = bottom
        self.top = top

    def get_ladder_points(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                          num_steps: int = 14) -> List[Tuple[float, float]]:
        """Calcula las posiciones intermedias a lo largo de los peldaños."""
        x1, y1 = start_pos
        x2, y2 = end_pos
        points = []
        for i in range(num_steps + 1):
            t = i / num_steps
            points.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
        return points

    def draw(self, surface: pygame.Surface, start_pos: Tuple[int, int], end_pos: Tuple[int, int]):
        """Renderizado brillante de madera pulida y oro metálico."""
        x1, y1 = start_pos  # Base
        x2, y2 = end_pos    # Cima

        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        if length == 0:
            return

        angle = math.atan2(dy, dx)
        rail_width = 12.0
        perp_x = -math.sin(angle) * rail_width
        perp_y = math.cos(angle) * rail_width

        r1_start = (x1 + perp_x, y1 + perp_y)
        r1_end = (x2 + perp_x, y2 + perp_y)
        r2_start = (x1 - perp_x, y1 - perp_y)
        r2_end = (x2 - perp_x, y2 - perp_y)

        # Sombra proyectada
        pygame.draw.line(surface, (10, 15, 25, 90), (r1_start[0] + 3, r1_start[1] + 3),
                         (r1_end[0] + 3, r1_end[1] + 3), 6)
        pygame.draw.line(surface, (10, 15, 25, 90), (r2_start[0] + 3, r2_start[1] + 3),
                         (r2_end[0] + 3, r2_end[1] + 3), 6)

        # Rieles dorados metálicos
        pygame.draw.line(surface, COLOR_LADDER_RAIL, r1_start, r1_end, 5)
        pygame.draw.line(surface, COLOR_LADDER_RAIL, r2_start, r2_end, 5)
        pygame.draw.line(surface, (255, 240, 160), r1_start, r1_end, 1)
        pygame.draw.line(surface, (255, 240, 160), r2_start, r2_end, 1)

        # Peldaños dorados
        num_rungs = max(3, int(length // 24))
        for i in range(1, num_rungs):
            t = i / num_rungs
            rx = x1 + dx * t
            ry = y1 + dy * t
            p1 = (rx + perp_x, ry + perp_y)
            p2 = (rx - perp_x, ry - perp_y)
            pygame.draw.line(surface, (15, 15, 20), (p1[0] + 1, p1[1] + 2), (p2[0] + 1, p2[1] + 2), 4)
            pygame.draw.line(surface, COLOR_LADDER_RUNG, p1, p2, 4)
            pygame.draw.line(surface, (255, 255, 220), (p1[0], p1[1] - 1), (p2[0], p2[1] - 1), 1)


class Board:
    """Tablero de 10x10 con casillas coloridas en zigzag y elementos aleatorios."""
    def __init__(self, x: int, y: int, size: int, asset_mgr: AssetManager):
        self.x = x
        self.y = y
        self.size = size
        self.asset_mgr = asset_mgr
        self.cell_size = size // GRID_COLS

        self.snakes: List[Snake] = []
        self.ladders: List[Ladder] = []
        self.snake_map: Dict[int, int] = {}
        self.ladder_map: Dict[int, int] = {}

        self.tile_coords: Dict[int, Tuple[int, int]] = {}
        self._calculate_tile_coordinates()
        self.generate_random_elements()

    def _calculate_tile_coordinates(self):
        """Calcula coordenadas en zigzag (1 a 100)."""
        for tile in range(1, TOTAL_TILES + 1):
            zero_idx = tile - 1
            row = zero_idx // GRID_COLS
            col_in_row = zero_idx % GRID_COLS

            col = col_in_row if row % 2 == 0 else (GRID_COLS - 1) - col_in_row
            screen_x = self.x + col * self.cell_size + self.cell_size // 2
            screen_y = self.y + (GRID_ROWS - 1 - row) * self.cell_size + self.cell_size // 2
            self.tile_coords[tile] = (screen_x, screen_y)

    def get_tile_center(self, tile: int) -> Tuple[int, int]:
        clamped = max(1, min(TOTAL_TILES, tile))
        return self.tile_coords[clamped]

    def get_tile_rect(self, tile: int) -> pygame.Rect:
        cx, cy = self.get_tile_center(tile)
        return pygame.Rect(cx - self.cell_size // 2, cy - self.cell_size // 2, self.cell_size, self.cell_size)

    def generate_random_elements(self, num_snakes: int = 7, num_ladders: int = 7):
        """
        Genera aleatoriamente las posiciones de serpientes y escaleras cumpliendo:
        1. Dispersión: Máximo 3 serpientes y máximo 3 escaleras por fila/línea.
        2. Sin encadenamientos: El final de cualquier serpiente o escalera NO puede
           coincidir con el inicio ni con el fin de ninguna otra serpiente o escalera
           (evita serpiente->escalera, escalera->serpiente, serpiente->serpiente y escalera->escalera).
        3. Casillas 1 y 100 libres de inicios y finales.
        """
        for _ in range(100):
            self.snakes.clear()
            self.ladders.clear()
            self.snake_map.clear()
            self.ladder_map.clear()

            # Conjuntos disjuntos: ningún inicio puede ser un fin, ni viceversa
            all_starts = set([1, TOTAL_TILES])
            all_ends = set([1, TOTAL_TILES])

            # Contadores por fila (0 a 9) para asegurar máximo 3 por línea
            snakes_per_row = [0] * GRID_ROWS
            ladders_per_row = [0] * GRID_ROWS

            # 1. Generar Escaleras (bottom < top)
            ladder_attempts = 0
            while len(self.ladders) < num_ladders and ladder_attempts < 1000:
                ladder_attempts += 1
                bottom = random.randint(2, 80)
                bottom_row = (bottom - 1) // GRID_COLS
                if ladders_per_row[bottom_row] >= 3:
                    continue

                min_top = (bottom_row + 1) * GRID_COLS + 1
                max_top = min(TOTAL_TILES - 1, (bottom_row + 4) * GRID_COLS)
                if min_top >= max_top:
                    continue

                top = random.randint(min_top, max_top)
                top_row = (top - 1) // GRID_COLS
                if ladders_per_row[top_row] >= 3:
                    continue

                # Validar que no colisione con ningún inicio ni fin existente
                if (bottom not in all_starts and bottom not in all_ends and
                    top not in all_starts and top not in all_ends and
                    bottom != top):
                    self.ladders.append(Ladder(bottom, top))
                    self.ladder_map[bottom] = top
                    all_starts.add(bottom)
                    all_ends.add(top)
                    ladders_per_row[bottom_row] += 1
                    ladders_per_row[top_row] += 1

            if len(self.ladders) < num_ladders:
                continue  # Reintentar generación completa si no cupieron

            # 2. Generar Serpientes (head > tail)
            snake_attempts = 0
            while len(self.snakes) < num_snakes and snake_attempts < 1000:
                snake_attempts += 1
                head = random.randint(20, 99)
                head_row = (head - 1) // GRID_COLS
                if snakes_per_row[head_row] >= 3:
                    continue

                max_tail = head_row * GRID_COLS
                min_tail = max(2, (head_row - 4) * GRID_COLS + 1)
                if min_tail >= max_tail:
                    continue

                tail = random.randint(min_tail, max_tail)
                tail_row = (tail - 1) // GRID_COLS
                if snakes_per_row[tail_row] >= 3:
                    continue

                # Validar que ni head ni tail colisionen con ningún inicio ni fin de nada
                if (head not in all_starts and head not in all_ends and
                    tail not in all_starts and tail not in all_ends and
                    head != tail):
                    self.snakes.append(Snake(head, tail))
                    self.snake_map[head] = tail
                    all_starts.add(head)
                    all_ends.add(tail)
                    snakes_per_row[head_row] += 1
                    snakes_per_row[tail_row] += 1

            if len(self.snakes) == num_snakes:
                break  # Éxito: tablero generado cumpliendo estrictamente todas las restricciones

    def draw(self, surface: pygame.Surface):
        """Dibuja el tablero con un diseño alegre, multicolor y estilizado."""
        board_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(surface, COLOR_BOARD_BG, board_rect, border_radius=14)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, board_rect, 3, border_radius=14)

        font_tile = self.asset_mgr.get_font("tile")
        font_small = self.asset_mgr.get_font("small")

        for tile in range(1, TOTAL_TILES + 1):
            rect = self.get_tile_rect(tile)
            zero_idx = tile - 1
            row = zero_idx // GRID_COLS
            col_in_row = zero_idx % GRID_COLS

            palette_idx = (row * 3 + col_in_row) % len(TILE_PALETTE)
            cell_color = TILE_PALETTE[palette_idx]

            if tile == TOTAL_TILES:
                cell_color = COLOR_TILE_END
            elif tile == 1:
                cell_color = COLOR_TILE_START

            pygame.draw.rect(surface, cell_color, rect)
            pygame.draw.rect(surface, COLOR_TILE_BORDER, rect, 1)

            num_surf = font_tile.render(str(tile), True, COLOR_TEXT_DARK)
            surface.blit(num_surf, (rect.x + 5, rect.y + 4))

            if tile == 1:
                lbl = font_small.render("INICIO", True, (20, 110, 50))
                surface.blit(lbl, (rect.x + 4, rect.bottom - 16))
            elif tile == TOTAL_TILES:
                lbl = font_small.render("META 100", True, (160, 100, 10))
                surface.blit(lbl, (rect.x + 5, rect.bottom - 16))

            if tile in self.ladder_map:
                top_p = (rect.right - 8, rect.y + 5)
                l_p = (rect.right - 14, rect.y + 13)
                r_p = (rect.right - 2, rect.y + 13)
                pygame.draw.polygon(surface, (30, 160, 70), [top_p, l_p, r_p])
            elif tile in self.snake_map:
                bot_p = (rect.right - 8, rect.y + 13)
                l_p = (rect.right - 14, rect.y + 5)
                r_p = (rect.right - 2, rect.y + 5)
                pygame.draw.polygon(surface, (220, 50, 70), [bot_p, l_p, r_p])

        # Dibujar escaleras (debajo)
        for ladder in self.ladders:
            ladder.draw(surface, self.get_tile_center(ladder.bottom), self.get_tile_center(ladder.top))

        # Dibujar serpientes (encima)
        for snake in self.snakes:
            snake.draw(surface, self.get_tile_center(snake.head), self.get_tile_center(snake.tail))


class Player:
    """
    Ficha de jugador con animaciones deliberadas, pausadas y detalladas.
    """
    MODE_IDLE = 0
    MODE_WALK = 1
    MODE_LADDER = 2
    MODE_SNAKE = 3

    def __init__(self, player_id: int, name: str, color: Tuple[int, int, int], offset_angle: float):
        self.player_id = player_id
        self.name = name
        self.color = color
        self.tile: int = 1
        self.offset_angle = offset_angle

        # Coordenadas actuales y elevación del salto
        self.current_x: float = 0.0
        self.current_y: float = 0.0
        self.hop_offset_y: float = 0.0

        # Segmento actual de animación
        self.anim_mode: int = self.MODE_IDLE
        self.waypoints: List[Tuple[float, float]] = []
        self.waypoint_idx: int = 0

        # Coordenadas de inicio y fin del segmento actual
        self.start_seg_x: float = 0.0
        self.start_seg_y: float = 0.0
        self.target_seg_x: float = 0.0
        self.target_seg_y: float = 0.0

        self.progress: float = 0.0
        self.move_speed: float = SPEED_WALK
        self.destination_tile: int = 1

    def set_initial_pos(self, center: Tuple[int, int]):
        cx, cy = self._apply_offset(center)
        self.current_x = cx
        self.current_y = cy
        self.hop_offset_y = 0.0
        self.anim_mode = self.MODE_IDLE
        self.waypoints.clear()

    def _apply_offset(self, center: Tuple[int, int]) -> Tuple[float, float]:
        radius = 12.0
        return (center[0] + math.cos(self.offset_angle) * radius,
                center[1] + math.sin(self.offset_angle) * radius)

    def start_walking(self, path: List[int], board: Board):
        """Inicia el movimiento paso a paso entre casillas con salto pausado."""
        if not path:
            return
        self.anim_mode = self.MODE_WALK
        self.destination_tile = path[-1]
        self.waypoints = [self._apply_offset(board.get_tile_center(t)) for t in path]
        self.waypoint_idx = 0
        self.start_seg_x = self.current_x
        self.start_seg_y = self.current_y
        self.target_seg_x, self.target_seg_y = self.waypoints[0]
        self.progress = 0.0
        self.move_speed = SPEED_WALK

    def start_ladder_climb(self, ladder: Ladder, board: Board):
        """Inicia la escalada pausada peldaño por peldaño con destellos."""
        self.anim_mode = self.MODE_LADDER
        self.destination_tile = ladder.top
        p_start = self._apply_offset(board.get_tile_center(ladder.bottom))
        p_end = self._apply_offset(board.get_tile_center(ladder.top))
        self.waypoints = ladder.get_ladder_points(p_start, p_end, num_steps=14)
        self.waypoint_idx = 0
        self.start_seg_x = self.current_x
        self.start_seg_y = self.current_y
        self.target_seg_x, self.target_seg_y = self.waypoints[0]
        self.progress = 0.0
        self.move_speed = SPEED_LADDER

    def start_snake_slide(self, snake: Snake, board: Board):
        """Inicia el deslizamiento detallado por el cuerpo ondulado de la serpiente."""
        self.anim_mode = self.MODE_SNAKE
        self.destination_tile = snake.tail
        p_start = self._apply_offset(board.get_tile_center(snake.head))
        p_end = self._apply_offset(board.get_tile_center(snake.tail))
        self.waypoints = snake.get_curve_points(p_start, p_end, segments=30)
        self.waypoint_idx = 0
        self.start_seg_x = self.current_x
        self.start_seg_y = self.current_y
        self.target_seg_x, self.target_seg_y = self.waypoints[0]
        self.progress = 0.0
        self.move_speed = SPEED_SNAKE

    def is_animating(self) -> bool:
        return self.anim_mode != self.MODE_IDLE

    def update(self, particle_mgr: ParticleManager) -> bool:
        """
        Actualiza el movimiento y animación del jugador.
        Retorna True si un paso de casilla normal acaba de completarse.
        """
        step_finished = False
        if self.anim_mode == self.MODE_IDLE or not self.waypoints:
            self.hop_offset_y = 0.0
            return False

        # Incrementar progreso con la velocidad pausada
        self.progress = min(1.0, self.progress + self.move_speed)
        t = self.progress

        # Interpolación exacta entre el inicio y el objetivo del segmento
        self.current_x = self.start_seg_x + (self.target_seg_x - self.start_seg_x) * t
        self.current_y = self.start_seg_y + (self.target_seg_y - self.start_seg_y) * t

        # Efecto vertical y partículas según el tipo de animación
        if self.anim_mode == self.MODE_WALK:
            # Salto elástico bien definido
            self.hop_offset_y = -abs(math.sin(t * math.pi)) * 16.0

        elif self.anim_mode == self.MODE_LADDER:
            # Saltito suave por cada peldaño + destellos mágicos
            self.hop_offset_y = -abs(math.sin(t * math.pi)) * 6.0
            if random.random() < 0.75:
                particle_mgr.spawn_ladder_sparkles(self.current_x, self.current_y, count=2)

        elif self.anim_mode == self.MODE_SNAKE:
            # A ras del cuerpo de la serpiente con estela continua
            self.hop_offset_y = 0.0
            if random.random() < 0.85:
                particle_mgr.spawn_snake_dust(self.current_x, self.current_y, count=2)

        # Cuando se completa el segmento actual
        if self.progress >= 1.0:
            self.current_x = self.target_seg_x
            self.current_y = self.target_seg_y
            self.progress = 0.0
            self.waypoint_idx += 1

            if self.anim_mode == self.MODE_WALK:
                step_finished = True

            # ¿Terminó la ruta completa de waypoints?
            if self.waypoint_idx >= len(self.waypoints):
                self.tile = self.destination_tile
                self.anim_mode = self.MODE_IDLE
                self.waypoints.clear()
                self.hop_offset_y = 0.0
            else:
                # Pasar al siguiente segmento
                self.start_seg_x = self.current_x
                self.start_seg_y = self.current_y
                self.target_seg_x, self.target_seg_y = self.waypoints[self.waypoint_idx]

        return step_finished

    def draw(self, surface: pygame.Surface, asset_mgr: AssetManager):
        """Dibuja la ficha del jugador con efecto de elevación 3D y brillo."""
        radius = 15
        px = int(self.current_x)
        py = int(self.current_y + self.hop_offset_y)

        # Sombra en el suelo
        shadow_scale = max(0.6, 1.0 + self.hop_offset_y * 0.02)
        shadow_rad = int(radius * shadow_scale)
        pygame.draw.circle(surface, (10, 15, 25, 90), (int(self.current_x + 2), int(self.current_y + 4)), shadow_rad)

        # Borde exterior blanco brillante
        pygame.draw.circle(surface, (255, 255, 255), (px, py), radius)
        # Color principal del jugador
        pygame.draw.circle(surface, self.color, (px, py), radius - 2)
        # Brillo superior
        pygame.draw.circle(surface, (255, 255, 255), (px - 4, py - 4), 4)

        # Número de ficha
        font = asset_mgr.get_font("small")
        txt = font.render(str(self.player_id), True, (255, 255, 255))
        surface.blit(txt, txt.get_rect(center=(px, py)))
