import pygame
from pathlib import Path
from Botones import Boton

class Menu:
    def __init__(self, screen, base_path):
        self.screen = screen
        self.base_path = base_path
        
        assets_dir = self.base_path / "assets"
        sound_dir = self.base_path / "Sonido"

        fondo_path = assets_dir / "Menu.png"
        if fondo_path.exists():
            raw_fondo = pygame.image.load(str(fondo_path)).convert()
            scr_w, scr_h = self.screen.get_size()
            if raw_fondo.get_size() != (scr_w, scr_h):
                self.fondo = pygame.transform.smoothscale(raw_fondo, (scr_w, scr_h))
            else:
                self.fondo = raw_fondo
        else:
            self.fondo = None

        btn_jugar_path = assets_dir / "BotonJugar.png"
        btn_salir_path = assets_dir / "BotonSalirRojo.png"
        snd_click_path = sound_dir / "Click.mp3"
        self.snd_bg_path = sound_dir / "Sonidomenu.mp3"

        # Centrar horizontalmente los botones (ancho escalado ~154)
        scr_w = self.screen.get_width()
        btn_x = (scr_w - 154) // 2
        self.jugar = Boton(btn_jugar_path, snd_click_path, (btn_x, 480), 0.1)
        self.salir = Boton(btn_salir_path, snd_click_path, (btn_x, 585), 0.1)

        self.ensure_music()

    def ensure_music(self):
        if self.snd_bg_path and self.snd_bg_path.exists():
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.load(str(self.snd_bg_path))
                    pygame.mixer.music.set_volume(0.4)
                    pygame.mixer.music.play(-1)
            except Exception:
                pass

    def run(self, clock):
        self.ensure_music()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"

        if self.jugar.es_presionado():
            return "PLAY"

        if self.salir.es_presionado():
            return "EXIT"

        self.screen.fill((0, 0, 0))
        if self.fondo:
            self.screen.blit(self.fondo, (0, 0))

        self.jugar.draw(self.screen)
        self.salir.draw(self.screen)

        pygame.display.flip()
        clock.tick(60)
        return "CONTINUE"
