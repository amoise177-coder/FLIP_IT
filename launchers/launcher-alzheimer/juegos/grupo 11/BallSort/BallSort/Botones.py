import pygame
from pathlib import Path

class Boton:
    def __init__(self, image_path, sound_path=None, position=(0, 0), scale=1.0):
        image_path = Path(image_path)
        if sound_path:
            sound_path = Path(sound_path)

        self.original_image = pygame.image.load(str(image_path)).convert_alpha()
        orig_w = self.original_image.get_width()
        orig_h = self.original_image.get_height()
        
        self.normal_w = int(orig_w * scale)
        self.normal_h = int(orig_h * scale)
        self.hover_w = int(self.normal_w * 1.06)
        self.hover_h = int(self.normal_h * 1.06)

        self.image_normal = pygame.transform.smoothscale(self.original_image, (self.normal_w, self.normal_h))
        self.image_hover = pygame.transform.smoothscale(self.original_image, (self.hover_w, self.hover_h))
        
        self.sound = None
        if sound_path and sound_path.exists():
            try:
                self.sound = pygame.mixer.Sound(str(sound_path))
            except Exception:
                self.sound = None

        self.position = position
        self.rect = self.image_normal.get_rect(topleft=position)
        self.pressed = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            # Dibujar centrado con ligero escalado de hover
            hover_rect = self.image_hover.get_rect(center=self.rect.center)
            screen.blit(self.image_hover, hover_rect)
        else:
            screen.blit(self.image_normal, self.rect)

    def es_presionado(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed and not self.pressed:
                self.pressed = True
                if self.sound:
                    try:
                        self.sound.play()
                    except Exception:
                        pass
                return True
            if not mouse_pressed:
                self.pressed = False
            return False
        return False