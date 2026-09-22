import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_dir)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

import pygame
import random
import math
from managers import AssetManager

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.scale = 1.0
        self.target_scale = 1.0
        self.click_offset = 0

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        is_pressed = is_hovered and pygame.mouse.get_pressed()[0]

        if is_pressed:
            self.target_scale = 0.95 
            self.click_offset = 3  
        elif is_hovered:
            self.target_scale = 1.08 
            self.click_offset = 0
        else:
            self.target_scale = 1.0 
            self.click_offset = 0

        self.scale += (self.target_scale - self.scale) * 0.25

        new_w = int(self.base_rect.width * self.scale)
        new_h = int(self.base_rect.height * self.scale)
        
        self.rect = pygame.Rect(0, 0, new_w, new_h)
        self.rect.center = (self.base_rect.centerx, self.base_rect.centery + self.click_offset)

        current_color = self.hover_color if is_hovered else self.color

        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        shadow_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 70), shadow_surface.get_rect(), border_radius=16)
        surface.blit(shadow_surface, shadow_rect.topleft)

        pygame.draw.rect(surface, current_color, self.rect, border_radius=16)

        border_color = (255, 255, 255) if is_hovered else (255, 255, 255, 120)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=16)

        txt_surf = self.font.render(self.text, True, (255, 255, 255))
        if self.scale != 1.0:
            txt_w = max(1, int(txt_surf.get_width() * self.scale))
            txt_h = max(1, int(txt_surf.get_height() * self.scale))
            txt_surf = pygame.transform.smoothscale(txt_surf, (txt_w, txt_h))

        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class SopaDeLetrasGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.FPS = 60
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Remember me")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("Georgia", 58, bold=True, italic=True)
        self.font_medium = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 22)
        self.music_vol = 0.5
        self.click_vol = 0.8  
        self.effect_vol = 0.5 
        self.current_state = "splash"
        self.splash_bg = AssetManager.load_background("portada.png", self.WIDTH, self.HEIGHT)
        self.menu_bg = AssetManager.load_background("menu.png", self.WIDTH, self.HEIGHT)
        self.game_bg = AssetManager.load_background("juego.png", self.WIDTH, self.HEIGHT)   
        self.click_sound = AssetManager.load_sound("boton.mp3", self.click_vol)
        self.win_sound = AssetManager.load_sound("ganaste.mp3", self.effect_vol)
        self.lose_sound = AssetManager.load_sound("perdiste.mp3", self.effect_vol)

    def play_click(self):
        if self.click_sound:
            self.click_sound.play()

    def handle_common_events(self, event):
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

    def draw_text_with_outline(self, text, font, text_color, outline_color, center_pos, outline_width=3):
        outline_surf = font.render(text, True, outline_color)
        cx, cy = center_pos
        
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    rect = outline_surf.get_rect(center=(cx + dx, cy + dy))
                    self.screen.blit(outline_surf, rect)
                    
        main_surf = font.render(text, True, text_color)
        main_rect = main_surf.get_rect(center=center_pos)
        self.screen.blit(main_surf, main_rect)

    def run(self):
        while True:
            if self.current_state == "splash":
                self.run_splash()
            elif self.current_state == "menu":
                self.run_menu()
            elif self.current_state == "difficulty":
                self.run_difficulty()
            elif self.current_state == "options":
                self.run_options()
            elif self.current_state == "easy":
                self.run_game_loop("easy")
            elif self.current_state == "hard":
                self.run_game_loop("hard")

    def run_splash(self):
        start_time = pygame.time.get_ticks()
        duration = 3500 

        while self.current_state == "splash":
            self.screen.blit(self.splash_bg, (0, 0))
            
            current_time = pygame.time.get_ticks()
            if current_time - start_time > duration:
                self.current_state = "menu"
                AssetManager.play_music("menuMSC.mp3", self.music_vol)
                break
            for event in pygame.event.get():
                self.handle_common_events(event)
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.current_state = "menu"
                    AssetManager.play_music("menuMSC.mp3", self.music_vol)
                    break    
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def run_menu(self):
        play_btn = Button(self.WIDTH//2 - 160, 260, 320, 60, "Jugar", (41, 128, 185), (52, 152, 219), self.font_medium)
        options_btn = Button(self.WIDTH//2 - 160, 340, 320, 60, "Opciones", (127, 140, 141), (149, 165, 166), self.font_medium)
        exit_btn = Button(self.WIDTH//2 - 160, 420, 320, 60, "Salir", (192, 57, 43), (231, 76, 60), self.font_medium)
        while self.current_state == "menu":
            self.screen.blit(self.menu_bg, (0, 0))
            title_shadow = self.font_title.render("Remember Me", True, (20, 20, 20))
            title_surf = self.font_title.render("Remember Me", True, (230, 245, 255))
            self.screen.blit(title_shadow, title_shadow.get_rect(center=(self.WIDTH//2 + 3, 153)))
            self.screen.blit(title_surf, title_surf.get_rect(center=(self.WIDTH//2, 150)))
            for event in pygame.event.get():
                self.handle_common_events(event)
                if play_btn.is_clicked(event):
                    self.play_click()
                    self.current_state = "difficulty"
                if options_btn.is_clicked(event):
                    self.play_click()
                    self.current_state = "options"
                if exit_btn.is_clicked(event):
                    self.play_click()
                    pygame.quit()
                    sys.exit()   
            play_btn.draw(self.screen)
            options_btn.draw(self.screen)
            exit_btn.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def run_difficulty(self):
        easy_btn = Button(self.WIDTH//2 - 160, 280, 320, 60, "Fácil", (39, 174, 96), (46, 204, 113), self.font_medium)
        hard_btn = Button(self.WIDTH//2 - 160, 360, 320, 60, "Difícil", (192, 57, 43), (231, 76, 60), self.font_medium)
        back_btn = Button(self.WIDTH//2 - 160, 440, 320, 60, "Volver", (127, 140, 141), (149, 165, 166), self.font_medium)
        while self.current_state == "difficulty":
            self.screen.blit(self.menu_bg, (0, 0))
            title_surf = self.font_title.render("Seleccione la dificultad", True, (255, 255, 255))
            self.screen.blit(title_surf, title_surf.get_rect(center=(self.WIDTH//2, 160)))
            for event in pygame.event.get():
                self.handle_common_events(event)
                if easy_btn.is_clicked(event):
                    self.play_click()
                    self.current_state = "easy"
                if hard_btn.is_clicked(event):
                    self.play_click()
                    self.current_state = "hard"
                if back_btn.is_clicked(event):
                    self.play_click()
                    self.current_state = "menu"        
            easy_btn.draw(self.screen)
            hard_btn.draw(self.screen)
            back_btn.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def run_options(self):
        center_x = self.WIDTH // 2
        m_down = Button(center_x + 50,  240, 45, 40, "-", (127, 140, 141), (149, 165, 166), self.font_medium)
        m_up   = Button(center_x + 110, 240, 45, 40, "+", (127, 140, 141), (149, 165, 166), self.font_medium)
        c_down = Button(center_x + 50,  320, 45, 40, "-", (127, 140, 141), (149, 165, 166), self.font_medium)
        c_up   = Button(center_x + 110, 320, 45, 40, "+", (127, 140, 141), (149, 165, 166), self.font_medium)
        e_down = Button(center_x + 50,  400, 45, 40, "-", (127, 140, 141), (149, 165, 166), self.font_medium)
        e_up   = Button(center_x + 110, 400, 45, 40, "+", (127, 140, 141), (149, 165, 166), self.font_medium)
        back_btn = Button(center_x - 160, 500, 320, 60, "Volver", (192, 57, 43), (231, 76, 60), self.font_medium)

        while self.current_state == "options":
            self.screen.blit(self.menu_bg, (0, 0))
            title_surf = self.font_title.render("OPCIONES", True, (255, 255, 255))
            self.screen.blit(title_surf, title_surf.get_rect(center=(center_x, 130)))
            m_text = self.font_medium.render(f"Música del menú: {int(self.music_vol * 100)}%", True, (255, 255, 255))
            c_text = self.font_medium.render(f"Sonido de botones: {int(self.click_vol * 100)}%", True, (255, 255, 255))
            e_text = self.font_medium.render(f"Música de partida: {int(self.effect_vol * 100)}%", True, (255, 255, 255))
            self.screen.blit(m_text, m_text.get_rect(midright=(center_x + 20, 260)))
            self.screen.blit(c_text, c_text.get_rect(midright=(center_x + 20, 340)))
            self.screen.blit(e_text, e_text.get_rect(midright=(center_x + 20, 420)))
            
            for event in pygame.event.get():
                self.handle_common_events(event)
                if m_up.is_clicked(event):
                    self.music_vol = min(1.0, self.music_vol + 0.1)
                    pygame.mixer.music.set_volume(self.music_vol)
                    self.play_click()
                if m_down.is_clicked(event):
                    self.music_vol = max(0.0, self.music_vol - 0.1)
                    pygame.mixer.music.set_volume(self.music_vol)
                    self.play_click()
                if c_up.is_clicked(event):
                    self.click_vol = min(1.0, self.click_vol + 0.1)
                    if self.click_sound: self.click_sound.set_volume(self.click_vol)
                    self.play_click()
                if c_down.is_clicked(event):
                    self.click_vol = max(0.0, self.click_vol - 0.1)
                    if self.click_sound: self.click_sound.set_volume(self.click_vol)
                    self.play_click()
                if e_up.is_clicked(event):
                    self.effect_vol = min(1.0, self.effect_vol + 0.1)
                    if self.win_sound: self.win_sound.set_volume(self.effect_vol)
                    if self.lose_sound: self.lose_sound.set_volume(self.effect_vol)
                    self.play_click()
                if e_down.is_clicked(event):
                    self.effect_vol = max(0.0, self.effect_vol - 0.1)
                    if self.win_sound: self.win_sound.set_volume(self.effect_vol)
                    if self.lose_sound: self.lose_sound.set_volume(self.effect_vol)
                    self.play_click()
                if back_btn.is_clicked(event):
                    self.play_click()
                    self.current_state = "menu"   
            
            m_down.draw(self.screen)
            m_up.draw(self.screen)
            c_down.draw(self.screen)
            c_up.draw(self.screen)
            e_down.draw(self.screen)
            e_up.draw(self.screen)
            back_btn.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.FPS)

    def run_game_loop(self, difficulty):
        AssetManager.play_music("juegoIN.mp3", self.music_vol)  
        level_data = random.choice(AssetManager.EASY_DATA if difficulty == "easy" else AssetManager.HARD_DATA)
        puzzle_img = AssetManager.load_puzzle_image(level_data["image"])
        initial_time = 60 if difficulty == "easy" else 45
        time_bonus = 20 if difficulty == "easy" else 15
        target_words = [w.upper() for w in level_data["words"]]
        found_words = []
        user_input = ""
        start_ticks = pygame.time.get_ticks()
        extra_time_ms = 0
        playing = True
        won = False
        reveal_time_threshold = 20 if difficulty == "easy" else 15
        letters_to_reveal_count = 3 if difficulty == "easy" else 2
        letters_revealed = False
        back_btn = Button(20, 20, 140, 45, "Volver", (192, 57, 43), (231, 76, 60), self.font_small)

        while playing:
            current_ticks = pygame.time.get_ticks()
            seconds_passed = (current_ticks - start_ticks) / 1000
            time_left = max(0, int(initial_time + (extra_time_ms / 1000) - seconds_passed))
            if not letters_revealed and seconds_passed >= reveal_time_threshold:
                letters_revealed = True
            if time_left == 0 or len(found_words) == len(target_words):
                won = (len(found_words) == len(target_words))
                pygame.mixer.music.stop()
                if won and self.win_sound:
                    self.win_sound.play()
                elif not won and self.lose_sound:
                    self.lose_sound.play()
                playing = False
                break
            self.screen.blit(self.game_bg, (0, 0))
            self.screen.blit(puzzle_img, (100, 110))
            puzzle_rect = pygame.Rect(100, 110, puzzle_img.get_width(), puzzle_img.get_height())
            pygame.draw.rect(self.screen, (255, 255, 255), puzzle_rect, 2, border_radius=15)
            back_btn.draw(self.screen)
            panel_rect = pygame.Rect(650, 110, 530, 500)
            pygame.draw.rect(self.screen, (0, 0, 0, 160), panel_rect, border_radius=15)
            pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 2, border_radius=15)
            timer_surf = self.font_medium.render(f"Tiempo: {time_left}s", True, (241, 196, 15) if time_left > 10 else (231, 76, 60))
            self.screen.blit(timer_surf, (680, 140))
            words_title = self.font_small.render("Palabras a encontrar:", True, (255, 255, 255))
            self.screen.blit(words_title, (680, 200))

            for i, word in enumerate(target_words):
                if word in found_words:
                    display_text = f"- {word}"
                    color = (46, 204, 113)
                else:
                    if seconds_passed >= reveal_time_threshold:
                        random.seed(hash(word))
                        indices = random.sample(range(len(word)), min(letters_to_reveal_count, len(word)))
                        display_chars = [word[j] if j in indices else "?" for j in range(len(word))]
                        display_text = "- " + " ".join(display_chars)
                    else:
                        display_text = "- " + " ".join(["?" for _ in word])
                    color = (255, 255, 255)
                w_surf = self.font_small.render(display_text, True, color)
                self.screen.blit(w_surf, (700, 240 + (i * 35)))
            input_box_rect = pygame.Rect(680, 500, 470, 50)
            pygame.draw.rect(self.screen, (255, 255, 255), input_box_rect, border_radius=8)
            self.screen.blit(self.font_medium.render(user_input, True, (30, 30, 30)), (input_box_rect.x + 10, input_box_rect.y + 10))
            self.screen.blit(self.font_small.render("Escribe la palabra y presiona Enter:", True, (255, 255, 255)), (680, 465))

            for event in pygame.event.get():
                self.handle_common_events(event)
                if back_btn.is_clicked(event):
                    self.play_click()
                    pygame.mixer.music.stop()
                    AssetManager.play_music("menuMSC.mp3", self.music_vol)
                    self.current_state = "menu"
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        cleaned_input = user_input.strip().upper()
                        if cleaned_input in target_words and cleaned_input not in found_words:
                            found_words.append(cleaned_input)
                            extra_time_ms += (time_bonus * 1000) 
                        user_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    else:
                        if len(user_input) < 15 and event.unicode.isprintable():
                            user_input += event.unicode   
            pygame.display.flip()
            self.clock.tick(self.FPS)

        self.run_game_over(won)
    def run_game_over(self, won):
        back_btn = Button(self.WIDTH//2 - 160, 450, 320, 60, "Menú Principal", (41, 128, 185), (52, 152, 219), self.font_medium)
        while self.current_state in ["easy", "hard"]:
            self.screen.blit(self.menu_bg, (0, 0))
            msg = "¡GANASTE!" if won else "Perdiste..."
            text_color = (46, 204, 113) if won else (231, 76, 60)
            self.draw_text_with_outline(
                text=msg, 
                font=self.font_title, 
                text_color=text_color, 
                outline_color=(255, 255, 255), 
                center_pos=(self.WIDTH // 2, 250),
                outline_width=3
            )
            for event in pygame.event.get():
                self.handle_common_events(event)
                if back_btn.is_clicked(event):
                    self.play_click()
                    AssetManager.play_music("menuMSC.mp3", self.music_vol)
                    self.current_state = "menu"
                    return  
            back_btn.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(self.FPS)

if __name__ == "__main__":
    game = SopaDeLetrasGame()
    game.run()