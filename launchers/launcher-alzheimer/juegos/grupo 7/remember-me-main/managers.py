import pygame
from pathlib import Path

class AssetManager:
    BASE_DIR = Path(__file__).resolve().parent
    ASSETS_DIR = BASE_DIR / "assets"

    EASY_DATA = [
        {"image": ASSETS_DIR / "easy" / "img1.png", "words": ["JULIA", "CECILIA", "SOFIA","LUCIA"]},
        {"image": ASSETS_DIR / "easy" / "img2.png", "words": ["UVAS", "PERA", "PIÑA","FRESA"]},
        {"image": ASSETS_DIR / "easy" / "img3.png", "words": ["ACEITE", "TORTILLA", "TOMATE","PAELLA"]}
    ]
    HARD_DATA = [
        {"image": ASSETS_DIR / "hard" / "img1.png", "words": ["ABEJA", "ANILLO", "ARCOIRIS","ABANICO","ARAÑA","ANCLA"]},
        {"image": ASSETS_DIR / "hard" / "img2.png", "words": ["IGLESIA", "IMPRESORA", "IGUANA","INCENDIO","IGLÚ","INDIO"]},
        {"image": ASSETS_DIR / "hard" / "img3.png", "words": ["ENFERMERA", "ERIZO", "ESCOBA","ELEFANTE","ESPEJO","ESPADA"]}
    ]

    @classmethod
    def load_background(cls, filename, width, height):
        path = cls.ASSETS_DIR / filename
        if path.exists():
            surf = pygame.image.load(str(path))
            return pygame.transform.scale(surf, (width, height))
        fallback = pygame.Surface((width, height))
        fallback.fill((45, 52, 54))
        return fallback

    @staticmethod
    def get_rounded_image(image, border_radius=15):
        rect = image.get_rect()
        rounded_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        mask_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), rect, border_radius=border_radius)
        rounded_surf.blit(image, (0, 0))
        rounded_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        return rounded_surf

    @classmethod
    def load_puzzle_image(cls, path):
        max_size = 500
        container = pygame.Surface((max_size, max_size))
        container.fill((45, 52, 54))
        if path.exists():
            surf = pygame.image.load(str(path))
            orig_w, orig_h = surf.get_size()
            ratio = min(max_size / orig_w, max_size / orig_h)
            new_w = int(orig_w * ratio)
            new_h = int(orig_h * ratio)  
            scaled_surf = pygame.transform.scale(surf, (new_w, new_h))
            x_offset = (max_size - new_w) // 2
            y_offset = (max_size - new_h) // 2
            container.blit(scaled_surf, (x_offset, y_offset))

            return cls.get_rounded_image(container, border_radius=15)

        container.fill((200, 200, 200))
        return cls.get_rounded_image(container, border_radius=15)

    @classmethod
    def load_sound(cls, filename, volume=0.5):
        path = cls.ASSETS_DIR / filename
        if path.exists():
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(volume)
            return sound
        return None

    @classmethod
    def play_music(cls, filename, volume=0.5):
        music_path = cls.ASSETS_DIR / filename
        if music_path.exists():
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)