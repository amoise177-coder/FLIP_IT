"""
Módulo de la lógica central del juego (GameEngine):
Gestiona la máquina de estados (incluyendo la Pantalla de Inicio),
turnos, reglas, dados, animaciones pausadas y partículas.
"""
import random
from typing import List, Tuple, Optional
import pygame

from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_POS, BOARD_SIZE, TOTAL_TILES,
    COLOR_BG, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_CARD_BG, COLOR_CARD_ACTIVE, COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED, COLOR_GOLD, COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_SNAKE, COLOR_LADDER, COLOR_P1, COLOR_P2
)
from assets import AssetManager, AudioManager
from entities import Board, Player
from ui import Dice, Button
from particles import ParticleManager
from menu import StartScreen


class GameEngine:
    """
    Controlador de la partida:
    - Pantalla de inicio con lluvia de serpientes y modales de información y configuración.
    - Máquina de estados con animaciones fluidas y pausadas.
    - Sistema dinámico de partículas (estrellas, estela de humo y confeti festivo).
    - Renderizado visual del panel lateral y HUD moderno.
    """
    STATE_MENU = 0
    STATE_WAIT_ROLL = 1
    STATE_ROLLING = 2
    STATE_DICE_REVEAL = 3
    STATE_MOVING_STEP = 4
    STATE_RESOLVE_TILE = 5
    STATE_GAME_OVER = 6

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # Gestores de recursos y partículas
        self.asset_mgr = AssetManager()
        self.audio_mgr = AudioManager()
        self.particle_mgr = ParticleManager()

        # Iniciar reproducción de la música de fondo en bucle infinito
        self.audio_mgr.play_music("musica-de-fondo.mp3", loop=True, volume=0.35)

        # Pantalla de inicio
        self.start_screen = StartScreen(self.asset_mgr, self.audio_mgr)

        # Tablero centrado y Jugadores
        self.board = Board(BOARD_POS[0], BOARD_POS[1], BOARD_SIZE, self.asset_mgr)
        self.players: List[Player] = [
            Player(1, "Jugador 1", COLOR_P1, 0.0),
            Player(2, "Jugador 2", COLOR_P2, 3.14159)
        ]
        self.current_player_idx: int = 0
        for p in self.players:
            p.set_initial_pos(self.board.get_tile_center(1))

        # Dado interactivo (visible únicamente tras interactuar con el botón y antes del movimiento)
        self.dice = Dice(pygame.Rect(100, 195, 110, 110))
        self.show_dice: bool = False
        self.dice_reveal_timer: int = 0
        self.pending_path: List[int] = []

        # Botón de lanzamiento para Jugador 1 (AZUL) debajo de su estado en la esquina superior izquierda
        self.btn_roll_p1 = Button(
            pygame.Rect(25, 130, 260, 48),
            "TIRAR DADO", (35, 105, 225), (55, 130, 250), "bold"
        )

        # Botón de lanzamiento para Jugador 2 (ROJO) debajo de su estado en la esquina superior derecha
        self.btn_roll_p2 = Button(
            pygame.Rect(995, 130, 260, 48),
            "TIRAR DADO", (215, 45, 55), (240, 70, 80), "bold"
        )

        # Botones inferiores de navegación
        self.btn_menu = Button(
            pygame.Rect(25, 648, 260, 44),
            "Menu Principal", (35, 45, 68), (50, 65, 95), "body"
        )
        self.btn_restart = Button(
            pygame.Rect(995, 648, 260, 44),
            "Nueva Partida", (35, 45, 68), (50, 65, 95), "body"
        )

        # Botón para jugar de nuevo en modal de victoria
        self.btn_play_again = Button(
            pygame.Rect((WINDOW_WIDTH - 240) // 2, 400, 240, 48),
            "Jugar de nuevo", COLOR_ACCENT, COLOR_ACCENT_HOVER, "subtitle"
        )

        # Estado del juego (Inicia en la Pantalla de Inicio)
        self.state: int = self.STATE_MENU
        self.resolve_delay: int = 0
        self.status_message: str = "Turno de Jugador 1: Presiona TIRAR DADO para comenzar."
        self.status_accent: Tuple[int, int, int] = COLOR_P1
        self.winner: Optional[Player] = None

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_idx]

    def set_status(self, message: str, accent: Tuple[int, int, int] = COLOR_ACCENT):
        """Actualiza el mensaje y color de acento de la burbuja informativa."""
        self.status_message = message
        self.status_accent = accent

    def trigger_dice_roll(self):
        """Inicia el tiro de dado si el estado lo permite."""
        if self.state == self.STATE_WAIT_ROLL:
            self.state = self.STATE_ROLLING
            self.show_dice = True

            # Posicionar el dado bajo el botón del jugador al que le toca
            if self.current_player_idx == 0:
                self.dice.rect.topleft = (100, 195)
            else:
                self.dice.rect.topleft = (1070, 195)

            self.btn_roll_p1.enabled = False
            self.btn_roll_p2.enabled = False
            self.audio_mgr.play_sound("dados", volume=0.51)
            self.dice.roll()
            self.set_status(f"{self.current_player.name} esta lanzando...", COLOR_GOLD)

    def restart_game(self):
        """Reinicia el tablero, partículas y devuelve los jugadores a la casilla 1."""
        self.board.generate_random_elements()
        self.current_player_idx = 0
        self.winner = None
        self.state = self.STATE_WAIT_ROLL
        self.show_dice = False
        self.resolve_delay = 0
        self.btn_roll_p1.enabled = True
        self.btn_roll_p2.enabled = False
        self.particle_mgr.clear()
        for p in self.players:
            p.tile = 1
            p.destination_tile = 1
            p.set_initial_pos(self.board.get_tile_center(1))
        self.set_status("Nuevo tablero listo. Turno de Jugador 1.", COLOR_P1)

    def handle_event(self, event: pygame.event.Event):
        """Procesa un evento de entrada enviado desde el bucle principal."""
        # 1. Si está en la pantalla de inicio
        if self.state == self.STATE_MENU:
            action = self.start_screen.handle_event(event)
            if action == "START_GAME":
                self.restart_game()
                self.state = self.STATE_WAIT_ROLL
            return

        # 2. Si está en el juego
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == self.STATE_WAIT_ROLL:
                    self.trigger_dice_roll()
                elif self.state == self.STATE_GAME_OVER:
                    self.restart_game()
            elif event.key == pygame.K_r:
                self.restart_game()
            elif event.key == pygame.K_m:
                self.audio_mgr.toggle_mute()
            elif event.key == pygame.K_ESCAPE:
                self.state = self.STATE_MENU

        # Clics sobre los botones interactivos
        if self.state == self.STATE_WAIT_ROLL:
            if self.current_player_idx == 0 and self.btn_roll_p1.is_clicked(event):
                self.trigger_dice_roll()
            elif self.current_player_idx == 1 and self.btn_roll_p2.is_clicked(event):
                self.trigger_dice_roll()

        elif self.state == self.STATE_GAME_OVER and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_play_again.rect.collidepoint(event.pos):
                self.restart_game()

        if self.btn_restart.is_clicked(event):
            self.restart_game()

        if self.btn_menu.is_clicked(event):
            self.state = self.STATE_MENU

    def update(self):
        """Actualiza la lógica según el estado actual."""
        # Si está en el menú de inicio
        if self.state == self.STATE_MENU:
            self.start_screen.update()
            return

        # Actualización de partida en curso
        mouse_pos = pygame.mouse.get_pos()
        self.btn_menu.update(mouse_pos)
        self.btn_restart.update(mouse_pos)

        # Actualizar botones según el turno del jugador activo
        if self.state == self.STATE_WAIT_ROLL:
            self.btn_roll_p1.enabled = (self.current_player_idx == 0)
            self.btn_roll_p2.enabled = (self.current_player_idx == 1)
            if self.current_player_idx == 0:
                self.btn_roll_p1.update(mouse_pos)
            else:
                self.btn_roll_p2.update(mouse_pos)
        else:
            self.btn_roll_p1.enabled = False
            self.btn_roll_p2.enabled = False

        if self.state == self.STATE_GAME_OVER:
            self.btn_play_again.update(mouse_pos)

        self.dice.update()
        self.particle_mgr.update()

        player = self.current_player

        # 1. Animación del dado mientras gira
        if self.state == self.STATE_ROLLING:
            if not self.dice.is_rolling:
                roll = self.dice.value
                start_tile = player.tile
                dest_tile = start_tile + roll

                path: List[int] = []
                if dest_tile <= TOTAL_TILES:
                    path = list(range(start_tile + 1, dest_tile + 1))
                    self.set_status(f"¡{player.name} saco un {roll}!", player.color)
                else:
                    overshoot = dest_tile - TOTAL_TILES
                    path = list(range(start_tile + 1, TOTAL_TILES + 1))
                    path += list(range(TOTAL_TILES - 1, (TOTAL_TILES - overshoot) - 1, -1))
                    self.set_status(f"¡{player.name} saco {roll}! Rebote por {overshoot} casilla(s).", COLOR_GOLD)

                self.pending_path = path
                self.dice_reveal_timer = 40  # Mantener visible el dado antes de iniciar el movimiento
                self.state = self.STATE_DICE_REVEAL

        # 2. Revelación del resultado del dado (se muestra antes de hacer la animación de movimiento)
        elif self.state == self.STATE_DICE_REVEAL:
            self.dice_reveal_timer -= 1
            if self.dice_reveal_timer <= 0:
                # Se oculta el dado antes de que comience el movimiento
                self.show_dice = False
                player.start_walking(self.pending_path, self.board)
                self.state = self.STATE_MOVING_STEP

        # 3. Desplazamiento animado (caminata paso a paso)
        elif self.state == self.STATE_MOVING_STEP:
            step_done = player.update(self.particle_mgr)
            if step_done:
                self.audio_mgr.play_sound("step")

            # Cuando termina la caminata, pasar a resolver casilla
            if not player.is_animating():
                self.state = self.STATE_RESOLVE_TILE
                self.resolve_delay = 18

        # 4. Comprobar escalera, serpiente o victoria
        elif self.state == self.STATE_RESOLVE_TILE:
            if self.resolve_delay > 0:
                self.resolve_delay -= 1
                return

            current = player.tile

            # ¿Cayó en base de una escalera?
            if current in self.board.ladder_map:
                ladder = next(l for l in self.board.ladders if l.bottom == current)
                self.set_status(f"¡Subiendo por la escalera a la casilla {ladder.top}!", COLOR_LADDER)
                self.audio_mgr.play_sound("ladder_up")
                player.start_ladder_climb(ladder, self.board)
                self.state = self.STATE_MOVING_STEP
                return

            # ¿Cayó en cabeza de una serpiente?
            elif current in self.board.snake_map:
                snake = next(s for s in self.board.snakes if s.head == current)
                self.set_status(f"¡Deslizandote por la serpiente a la casilla {snake.tail}!", COLOR_SNAKE)
                self.audio_mgr.play_sound("snake_slide")
                player.start_snake_slide(snake, self.board)
                self.state = self.STATE_MOVING_STEP
                return

            # ¿Alcanzó la casilla 100 exacta?
            if current == TOTAL_TILES:
                self.winner = player
                self.state = self.STATE_GAME_OVER
                self.set_status(f"¡{player.name} ha ganado la partida!", COLOR_GOLD)
                self.audio_mgr.play_sound("victory")
                self.particle_mgr.spawn_confetti(WINDOW_WIDTH // 2, 60, count=45)
            else:
                # Pasar turno al siguiente jugador
                self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
                self.state = self.STATE_WAIT_ROLL
                self.show_dice = False
                self.btn_roll_p1.enabled = (self.current_player_idx == 0)
                self.btn_roll_p2.enabled = (self.current_player_idx == 1)
                self.set_status(f"Turno de {self.current_player.name}: Presiona TIRAR DADO.", self.current_player.color)

        # Si el juego ha terminado, continuar lluvia festiva de confeti
        elif self.state == self.STATE_GAME_OVER:
            if random.random() < 0.25:
                self.particle_mgr.spawn_confetti(random.randint(250, 1050), -10, count=3)

    def draw(self):
        """Renderiza la escena completa en pantalla según el estado."""
        # Si está en el menú de inicio, dibujar StartScreen
        if self.state == self.STATE_MENU:
            self.start_screen.draw(self.screen)
            pygame.display.flip()
            return

        # Renderizado de la partida
        self.screen.fill(COLOR_BG)

        # 1. Tablero centrado
        self.board.draw(self.screen)

        # 2. Partículas
        self.particle_mgr.draw(self.screen)

        # 3. Fichas de jugadores
        for player in self.players:
            player.draw(self.screen, self.asset_mgr)

        # 4. HUD integrado en la pantalla
        self._draw_hud()

        pygame.display.flip()

    def _draw_hud(self):
        """Renderizado de los elementos HUD integrados en la pantalla del juego."""
        font_bold = self.asset_mgr.get_font("bold")
        font_body = self.asset_mgr.get_font("body")
        font_small = self.asset_mgr.get_font("small")

        p1 = self.players[0]
        p2 = self.players[1]
        is_p1_turn = (self.current_player_idx == 0 and self.state != self.STATE_GAME_OVER)
        is_p2_turn = (self.current_player_idx == 1 and self.state != self.STATE_GAME_OVER)

        # -------------------------------------------------------------
        # 1. ESQUINA SUPERIOR IZQUIERDA: Estado del Jugador 1
        # -------------------------------------------------------------
        card_p1_rect = pygame.Rect(25, 25, 260, 95)
        bg_p1 = COLOR_CARD_ACTIVE if is_p1_turn else COLOR_CARD_BG
        border_p1 = p1.color if is_p1_turn else COLOR_PANEL_BORDER
        pygame.draw.rect(self.screen, bg_p1, card_p1_rect, border_radius=12)
        pygame.draw.rect(self.screen, border_p1, card_p1_rect, 2 if is_p1_turn else 1, border_radius=12)

        # Avatar de Jugador 1
        pygame.draw.circle(self.screen, p1.color, (card_p1_rect.x + 22, card_p1_rect.y + 26), 10)
        p1_name = font_bold.render(p1.name, True, COLOR_TEXT_LIGHT)
        self.screen.blit(p1_name, (card_p1_rect.x + 40, card_p1_rect.y + 17))

        # Badge de turno
        if is_p1_turn:
            badge_p1 = font_small.render("TU TURNO", True, COLOR_GOLD)
            self.screen.blit(badge_p1, (card_p1_rect.right - 78, card_p1_rect.y + 18))
        else:
            badge_p1 = font_small.render("EN ESPERA", True, COLOR_TEXT_MUTED)
            self.screen.blit(badge_p1, (card_p1_rect.right - 82, card_p1_rect.y + 18))

        # Casilla
        p1_pos = font_body.render(f"Casilla {p1.tile} / 100", True, COLOR_GOLD if is_p1_turn else COLOR_TEXT_MUTED)
        self.screen.blit(p1_pos, (card_p1_rect.x + 16, card_p1_rect.y + 46))

        # Barra de progreso P1
        bar_w = 228
        bar_h = 6
        progress_p1 = min(1.0, max(0.01, p1.tile / 100.0))
        pygame.draw.rect(self.screen, (20, 26, 40), (card_p1_rect.x + 16, card_p1_rect.y + 74, bar_w, bar_h), border_radius=3)
        pygame.draw.rect(self.screen, p1.color, (card_p1_rect.x + 16, card_p1_rect.y + 74, int(bar_w * progress_p1), bar_h), border_radius=3)

        # Botón de tiro de dado Jugador 1 (AZUL) debajo de su estado
        if is_p1_turn and self.state == self.STATE_WAIT_ROLL:
            self.btn_roll_p1.enabled = True
            self.btn_roll_p1.draw(self.screen, self.asset_mgr)
            hint_p1 = font_small.render("o pulsa [Espacio]", True, COLOR_TEXT_MUTED)
            self.screen.blit(hint_p1, hint_p1.get_rect(center=(self.btn_roll_p1.rect.centerx, self.btn_roll_p1.rect.bottom + 14)))

        # -------------------------------------------------------------
        # 2. ESQUINA SUPERIOR DERECHA: Estado del Jugador 2
        # -------------------------------------------------------------
        card_p2_rect = pygame.Rect(995, 25, 260, 95)
        bg_p2 = COLOR_CARD_ACTIVE if is_p2_turn else COLOR_CARD_BG
        border_p2 = p2.color if is_p2_turn else COLOR_PANEL_BORDER
        pygame.draw.rect(self.screen, bg_p2, card_p2_rect, border_radius=12)
        pygame.draw.rect(self.screen, border_p2, card_p2_rect, 2 if is_p2_turn else 1, border_radius=12)

        # Avatar de Jugador 2
        pygame.draw.circle(self.screen, p2.color, (card_p2_rect.x + 22, card_p2_rect.y + 26), 10)
        p2_name = font_bold.render(p2.name, True, COLOR_TEXT_LIGHT)
        self.screen.blit(p2_name, (card_p2_rect.x + 40, card_p2_rect.y + 17))

        # Badge de turno
        if is_p2_turn:
            badge_p2 = font_small.render("TU TURNO", True, COLOR_GOLD)
            self.screen.blit(badge_p2, (card_p2_rect.right - 78, card_p2_rect.y + 18))
        else:
            badge_p2 = font_small.render("EN ESPERA", True, COLOR_TEXT_MUTED)
            self.screen.blit(badge_p2, (card_p2_rect.right - 82, card_p2_rect.y + 18))

        # Casilla
        p2_pos = font_body.render(f"Casilla {p2.tile} / 100", True, COLOR_GOLD if is_p2_turn else COLOR_TEXT_MUTED)
        self.screen.blit(p2_pos, (card_p2_rect.x + 16, card_p2_rect.y + 46))

        # Barra de progreso P2
        progress_p2 = min(1.0, max(0.01, p2.tile / 100.0))
        pygame.draw.rect(self.screen, (20, 26, 40), (card_p2_rect.x + 16, card_p2_rect.y + 74, bar_w, bar_h), border_radius=3)
        pygame.draw.rect(self.screen, p2.color, (card_p2_rect.x + 16, card_p2_rect.y + 74, int(bar_w * progress_p2), bar_h), border_radius=3)

        # Botón de tiro de dado Jugador 2 (ROJO) debajo de su estado
        if is_p2_turn and self.state == self.STATE_WAIT_ROLL:
            self.btn_roll_p2.enabled = True
            self.btn_roll_p2.draw(self.screen, self.asset_mgr)
            hint_p2 = font_small.render("o pulsa [Espacio]", True, COLOR_TEXT_MUTED)
            self.screen.blit(hint_p2, hint_p2.get_rect(center=(self.btn_roll_p2.rect.centerx, self.btn_roll_p2.rect.bottom + 14)))

        # -------------------------------------------------------------
        # 3. DADO: Visible tras pulsar el botón y antes de mover la ficha
        # -------------------------------------------------------------
        if self.show_dice:
            self.dice.draw(self.screen, False)

        # -------------------------------------------------------------
        # 4. BURBUJA INFORMATIVA DE ESTADO (en el lateral activo)
        # -------------------------------------------------------------
        msg_x = 25 if self.current_player_idx == 0 else 995
        msg_rect = pygame.Rect(msg_x, 325, 260, 72)
        pygame.draw.rect(self.screen, (20, 26, 42), msg_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.status_accent, msg_rect, 1, border_radius=12)

        # Ajuste de líneas de mensaje para visualización elegante
        if len(self.status_message) > 28:
            words = self.status_message.split(" ")
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            m1 = font_small.render(line1, True, COLOR_TEXT_LIGHT)
            m2 = font_small.render(line2, True, COLOR_TEXT_LIGHT)
            self.screen.blit(m1, m1.get_rect(center=(msg_rect.centerx, msg_rect.centery - 12)))
            self.screen.blit(m2, m2.get_rect(center=(msg_rect.centerx, msg_rect.centery + 12)))
        else:
            m = font_small.render(self.status_message, True, COLOR_TEXT_LIGHT)
            self.screen.blit(m, m.get_rect(center=msg_rect.center))

        # -------------------------------------------------------------
        # 5. BOTONES INFERIORES DE ACCION
        # -------------------------------------------------------------
        self.btn_menu.draw(self.screen, self.asset_mgr)
        self.btn_restart.draw(self.screen, self.asset_mgr)

        # -------------------------------------------------------------
        # 6. MODAL DE VICTORIA
        # -------------------------------------------------------------
        if self.state == self.STATE_GAME_OVER and self.winner:
            over_w, over_h = 480, 250
            over_rect = pygame.Rect((WINDOW_WIDTH - over_w) // 2, (WINDOW_HEIGHT - over_h) // 2, over_w, over_h)
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((8, 12, 20, 160))
            self.screen.blit(overlay, (0, 0))

            pygame.draw.rect(self.screen, (18, 24, 38), over_rect, border_radius=16)
            pygame.draw.rect(self.screen, COLOR_GOLD, over_rect, 2, border_radius=16)

            font_win = self.asset_mgr.get_font("winner")
            w_surf = font_win.render(f"¡GANADOR: {self.winner.name.upper()}!", True, COLOR_GOLD)
            self.screen.blit(w_surf, w_surf.get_rect(center=(over_rect.centerx, over_rect.y + 60)))

            sub_surf = font_body.render("¡Ha llegado a la casilla 100 y conquistó el tablero!", True, COLOR_TEXT_LIGHT)
            self.screen.blit(sub_surf, sub_surf.get_rect(center=(over_rect.centerx, over_rect.y + 105)))

            self.btn_play_again.draw(self.screen, self.asset_mgr)
