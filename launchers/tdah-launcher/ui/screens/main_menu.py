import math
from typing import List, Optional

import pygame

from core.managers.asset_manager import AssetManager
from core.managers.sound_player import SoundPlayer
from core.settings import Settings
from ui.visuals import COLORS, get_font, make_background


class MainMenu:
    def __init__(self, games_list: List[dict]) -> None:
        self.background = make_background()
        self.games_list = list(games_list)
        self.title_font = get_font(24)
        self.bubble_title_font = get_font(24)
        self.desc_font = get_font(18)
        self.bar_font = get_font(18)
        self.selected_index = 0
        self.page_start = 0
        self.message = None
        self.message_time = 0.0
        self.nav_sound = self._load_sound("SOUND_NAV", "assets/sounds/nav_move.wav")
        self.select_sound = self._load_sound("SOUND_SELECT", "assets/sounds/select.wav")
        self.quit_sound = self._load_sound("SOUND_QUIT", "assets/sounds/quit.wav")

        # Configuración del Carrusel
        self.carousel_image = AssetManager.get_asset("carousel")
        cw, ch = self.carousel_image.get_size() if self.carousel_image else (1152, 265)
        self.carrusel_x = (Settings.S_WIDTH - cw) // 2
        self.carrusel_y = 315

        # Centros locales de los 4 marcos en CARRUSEL.png
        self.frame_centers = [(145, 132), (433, 132), (720, 132), (1007, 132)]
        self.card_rects = [
            pygame.Rect(self.carrusel_x + cx - 110, self.carrusel_y + cy - 95, 220, 190)
            for cx, cy in self.frame_centers
        ]

        # Botón volver (BOTON2) y ayuda (BOTON1)
        self.back_button_image = AssetManager.get_asset("back_button")
        if self.back_button_image:
            self.back_rect = self.back_button_image.get_rect(topleft=(40, 24))
        else:
            self.back_rect = pygame.Rect(35, 24, 74, 62)

        self.help_button_image = AssetManager.get_asset("help_button")
        if self.help_button_image:
            self.help_rect = self.help_button_image.get_rect(
                topleft=(Settings.S_WIDTH - 40 - self.help_button_image.get_width(), 24)
            )
        else:
            self.help_rect = pygame.Rect(Settings.S_WIDTH - 114, 24, 74, 62)

        # Botones de navegación (flechas)
        arrow_y = self.carrusel_y + 132
        self.previous_button = self._prepare_navigation_button("previous_button", (55, arrow_y))
        self.next_button = self._prepare_navigation_button("next_button", (Settings.S_WIDTH - 55, arrow_y))

    def _prepare_navigation_button(self, asset_name, center):
        image = AssetManager.get_asset(asset_name)
        if image is None:
            return pygame.Rect(center[0] - 32, center[1] - 32, 64, 64)
        size = min(76, max(48, min(image.get_size())))
        scaled = pygame.transform.smoothscale(image, (size, size))
        return {"image": scaled, "rect": scaled.get_rect(center=center)}

    def _button_rect(self, button):
        return button["rect"] if isinstance(button, dict) else button

    def _change_page(self, direction):
        page_size = len(self.card_rects)
        page_start = max(0, self.page_start + direction * page_size)
        last_page_start = max(0, ((len(self.games_list) - 1) // page_size) * page_size) if self.games_list else 0
        self.page_start = min(page_start, last_page_start)
        self.selected_index = self.page_start

    def _load_sound(self, settings_key, default_path):
        path = getattr(Settings, settings_key, default_path)
        try:
            return pygame.mixer.Sound(path) if path else None
        except (pygame.error, FileNotFoundError):
            return None

    def _play_sound(self, sound):
        if sound:
            SoundPlayer.play_sound(sound)

    def _launch_selected(self):
        if not self.games_list:
            return None
        if self.games_list[self.selected_index].get("is_ghost"):
            self._play_sound(self.select_sound)
            return "TEST_GAME"
        self._play_sound(self.select_sound)
        return {"action": "LAUNCH", "game_data": self.games_list[self.selected_index]}

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_UP):
                    previous_index = self.selected_index
                    self.selected_index = max(0, self.selected_index - 1)
                    if self.selected_index != previous_index:
                        self._play_sound(self.nav_sound)
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    previous_index = self.selected_index
                    self.selected_index = min(max(0, len(self.games_list) - 1), self.selected_index + 1)
                    if self.selected_index != previous_index:
                        self._play_sound(self.nav_sound)
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    self.page_start = (self.selected_index // 4) * 4
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return self._launch_selected()
                elif event.key == pygame.K_ESCAPE:
                    self._play_sound(self.quit_sound)
                    return "START"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_rect.collidepoint(event.pos):
                    self._play_sound(self.quit_sound)
                    return "START"
                if self.help_rect.collidepoint(event.pos):
                    self._play_sound(self.nav_sound)
                    self.message = "Usa las flechas o ratón para elegir un juego y pulsa ENTER para jugar."
                    self.message_time = 3.5
                    return None
                if self._button_rect(self.previous_button).collidepoint(event.pos):
                    self._play_sound(self.nav_sound)
                    self._change_page(-1)
                    return None
                if self._button_rect(self.next_button).collidepoint(event.pos):
                    self._play_sound(self.nav_sound)
                    self._change_page(1)
                    return None
                for index, rect in enumerate(self.card_rects):
                    game_index = self.page_start + index
                    if rect.collidepoint(event.pos) and game_index < len(self.games_list):
                        self.selected_index = game_index
                        return self._launch_selected()
        return None

    def update(self, dt):
        if self.message_time > 0:
            self.message_time -= dt
            if self.message_time <= 0:
                self.message = None
        return None

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int, max_lines: int = 3) -> List[str]:
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                    if len(lines) >= max_lines:
                        break
                current = word
        if current and len(lines) < max_lines:
            lines.append(current)
        elif len(lines) >= max_lines and current:
            if not lines[-1].endswith("..."):
                lines[-1] = lines[-1][: max(0, len(lines[-1]) - 3)] + "..."
        return lines

    def _draw_tooltip_bubble(self, screen: pygame.Surface, game: dict, target_center_x: int, target_top_y: int):
        title = str(game.get("title", "Juego sin nombre"))
        description = str(game.get("description", ""))

        desc_lines = self._wrap_text(description, self.desc_font, 310, max_lines=3)
        line_h = self.desc_font.get_linesize()
        bubble_w = 340
        bubble_h = 44 + len(desc_lines) * line_h + 16

        # Clamping horizontal
        bx = max(20, min(Settings.S_WIDTH - bubble_w - 20, target_center_x - bubble_w // 2))
        by = max(80, target_top_y - bubble_h - 12)

        bubble = pygame.Surface((bubble_w, bubble_h + 14), pygame.SRCALPHA)
        # Sombra
        pygame.draw.rect(bubble, (0, 0, 0, 30), (4, 4, bubble_w - 8, bubble_h), border_radius=20)
        # Fondo
        pygame.draw.rect(bubble, (255, 255, 255, 245), (0, 0, bubble_w - 8, bubble_h), border_radius=20)
        # Borde morado
        pygame.draw.rect(bubble, (140, 115, 185), (0, 0, bubble_w - 8, bubble_h), width=3, border_radius=20)

        # Flecha indicadora apuntando a la portada
        local_target_x = max(24, min(bubble_w - 32, target_center_x - bx))
        pts = [
            (local_target_x - 12, bubble_h - 1),
            (local_target_x + 12, bubble_h - 1),
            (local_target_x, bubble_h + 11),
        ]
        pygame.draw.polygon(bubble, (255, 255, 255, 245), pts)
        pygame.draw.polygon(bubble, (140, 115, 185), pts, width=3)

        # Título
        t_surf = self.bubble_title_font.render(title, True, (108, 92, 160))
        bubble.blit(t_surf, t_surf.get_rect(center=((bubble_w - 8) // 2, 24)))

        # Descripción
        for idx, line in enumerate(desc_lines):
            l_surf = self.desc_font.render(line, True, (75, 65, 95))
            bubble.blit(l_surf, l_surf.get_rect(center=((bubble_w - 8) // 2, 48 + idx * line_h + 8)))

        screen.blit(bubble, (bx, by))

    def draw(self, screen: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()

        # 1. Fondo de selección
        selection_background = AssetManager.get_asset("selection_background")
        if selection_background:
            screen.blit(selection_background, (0, 0))
        else:
            screen.blit(self.background, (0, 0))

        # 2. Determinar qué juego está bajo el cursor o seleccionado
        hovered_slot: Optional[int] = None
        for index, rect in enumerate(self.card_rects):
            if rect.collidepoint(mouse_pos) and (self.page_start + index < len(self.games_list)):
                hovered_slot = index
                break

        # Si el ratón no está sobre ninguno, usar la selección activa por teclado
        active_slot = hovered_slot
        if active_slot is None and self.games_list:
            current_page_idx = self.selected_index - self.page_start
            if 0 <= current_page_idx < len(self.card_rects):
                active_slot = current_page_idx

        # 3. Dibujar las portadas adaptadas dentro de los marcos
        target_cover_size = (220, 190)
        mask = pygame.Surface(target_cover_size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, target_cover_size[0], target_cover_size[1]), border_radius=42)

        for index, (cx, cy) in enumerate(self.frame_centers):
            game_index = self.page_start + index
            if game_index < len(self.games_list):
                game = self.games_list[game_index]
                raw_cover = AssetManager.get_cover(game.get("folder", ""))
                scaled_cover = pygame.transform.smoothscale(raw_cover, target_cover_size)
                masked_cover = mask.copy()
                masked_cover.blit(scaled_cover, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

                center_pos = (self.carrusel_x + cx, self.carrusel_y + cy)

                # Efecto sutil de resaltado si está seleccionado/hover
                if index == active_slot:
                    glow = pygame.Surface((target_cover_size[0] + 16, target_cover_size[1] + 16), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (255, 220, 100, 120), glow.get_rect(), border_radius=48)
                    screen.blit(glow, glow.get_rect(center=center_pos))

                screen.blit(masked_cover, masked_cover.get_rect(center=center_pos))

        # 4. Dibujar el marco frontal CARRUSEL
        if self.carousel_image:
            screen.blit(self.carousel_image, (self.carrusel_x, self.carrusel_y))

        # 5. Botones de navegación anterior / siguiente
        self._draw_navigation_button(screen, self.previous_button, self.page_start > 0)
        self._draw_navigation_button(
            screen,
            self.next_button,
            self.page_start + len(self.card_rects) < len(self.games_list),
        )

        # 6. Botón Volver (BOTON2)
        if self.back_button_image:
            hover = self.back_rect.collidepoint(mouse_pos)
            if hover:
                scaled = pygame.transform.smoothscale(
                    self.back_button_image,
                    (int(self.back_rect.width * 1.08), int(self.back_rect.height * 1.08)),
                )
                screen.blit(scaled, scaled.get_rect(center=self.back_rect.center))
            else:
                screen.blit(self.back_button_image, self.back_rect)
        else:
            pygame.draw.rect(screen, COLORS["green"], self.back_rect, border_radius=16)


        # 8. Tooltip flotante con información (Nombre y Descripción)
        if active_slot is not None and (self.page_start + active_slot < len(self.games_list)):
            active_game = self.games_list[self.page_start + active_slot]
            cx, _ = self.frame_centers[active_slot]
            self._draw_tooltip_bubble(
                screen,
                active_game,
                target_center_x=self.carrusel_x + cx,
                target_top_y=self.carrusel_y + 10,
            )

            # Información en la franja inferior morada (Integrantes)
            authors = active_game.get("authors", ["Desconocido"])
            authors_str = "Integrantes: " + " - ".join(authors if isinstance(authors, list) else [str(authors)])
            a_surf = self.bar_font.render(authors_str[:85], True, (240, 230, 255))
            screen.blit(a_surf, (50, 665))

        if not self.games_list:
            empty = get_font(26).render("Todavía no hay juegos disponibles", True, COLORS["muted"])
            screen.blit(empty, empty.get_rect(center=(Settings.S_WIDTH // 2, 447)))

        # Mensaje temporal si se presiona el botón de ayuda
        if self.message:
            msg_surf = self.desc_font.render(self.message, True, (255, 255, 255))
            msg_rect = msg_surf.get_rect(center=(Settings.S_WIDTH // 2, 220)).inflate(40, 24)
            pygame.draw.rect(screen, (108, 92, 160), msg_rect, border_radius=16)
            screen.blit(msg_surf, msg_surf.get_rect(center=msg_rect.center))

    def _draw_navigation_button(self, screen, button, enabled):
        rect = self._button_rect(button)
        if isinstance(button, dict):
            image = button["image"].copy()
            image.set_alpha(255 if enabled else 80)
            screen.blit(image, rect)
        else:
            pygame.draw.circle(screen, (210, 205, 225), rect.center, rect.width // 2)