import pygame
from pathlib import Path

class Boton:
    def __init__(self, image_path: Path, sound_path: Path, position: tuple, scale: float = 1.0):
        self.image = pygame.image.load(image_path).convert_alpha()
        original_width = self.image.get_width()
        original_height = self.image.get_height()
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        self.image = pygame.transform.smoothscale(self.image, (new_width, new_height))
        self.sound = pygame.mixer.Sound(sound_path)
        
        self.rect = self.image.get_rect(topleft=position)
        self.pressed = False

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def es_presionado(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            if mouse_pressed and not self.pressed:
                self.pressed = True
                self.sound.play()
                return True
            if not mouse_pressed:
                self.pressed = False
            return False
        return False
