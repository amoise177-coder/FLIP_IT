import os
from typing import Dict, List, Optional

import pygame

from core.settings import Settings


class AssetManager:
    """Centraliza la carga de recursos gráficos y de audio del launcher."""

    _assets: Dict[str, object] = {}
    _covers: Dict[str, pygame.Surface] = {}
    _font_path: Optional[str] = None

    @classmethod
    def load_all_assets(cls) -> None:
        """Carga la fuente principal y las imágenes de fondo usadas por las pantallas."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()

        cls._font_path = Settings.FONT_PATH if os.path.exists(Settings.FONT_PATH) else None
        if cls._font_path:
            cls._assets["font"] = pygame.font.Font(cls._font_path, 36)
        else:
            cls._assets["font"] = pygame.font.Font(None, 36)

        menu_candidates = [
            Settings.MENU_BACKGROUND_IMAGE,
            os.path.join(Settings.ASSETS_DIR, "decoration", "fondo2.png"),
            os.path.join(Settings.ASSETS_DIR, "decoration", "fondo2 (1).png"),
        ]
        for path in menu_candidates:
            if path and os.path.exists(path):
                background = pygame.image.load(path)
                try:
                    if pygame.display.get_init() and pygame.display.get_surface():
                        background = background.convert()
                except pygame.error:
                    pass
                cls._assets["menu_background"] = pygame.transform.scale(background, (Settings.S_WIDTH, Settings.S_HEIGHT))
                cls._assets["selection_background"] = pygame.transform.smoothscale(
                    background, (Settings.S_WIDTH, Settings.S_HEIGHT)
                )
                break

        start_candidates = [
            Settings.START_BACKGROUND_IMAGE,
            os.path.join(Settings.ASSETS_DIR, "decoration", "fondo1.png"),
            os.path.join(Settings.ASSETS_DIR, "decoration", "fondo2 (2).png"),
            os.path.join(Settings.ASSETS_DIR, "decoration", "fondo1.1.png"),
        ]
        for path in start_candidates:
            if path and os.path.exists(path):
                start_background = pygame.image.load(path)
                try:
                    start_background = start_background.convert()
                except pygame.error:
                    pass
                cls._assets["start_background"] = pygame.transform.smoothscale(
                    start_background, (Settings.S_WIDTH, Settings.S_HEIGHT)
                )
                break

        if os.path.exists(Settings.BANNER_IMAGE):
            title_image = pygame.image.load(Settings.BANNER_IMAGE)
            try:
                title_image = title_image.convert_alpha()
            except pygame.error:
                pass
            max_width = min(Settings.S_WIDTH - 120, title_image.get_width())
            image_height = int(title_image.get_height() * max_width / title_image.get_width())
            cls._assets["banner"] = pygame.transform.smoothscale(title_image, (max_width, image_height))

        back_candidates = [
            getattr(Settings, "BACK_BUTTON_IMAGE", None),
            os.path.join(Settings.ASSETS_DIR, "decoration", "BOTON2.png"),
        ]
        for path in back_candidates:
            if path and os.path.exists(path):
                back_image = pygame.image.load(path)
                try:
                    back_image = back_image.convert_alpha()
                except pygame.error:
                    pass
                cls._assets["back_button"] = back_image
                break


        carousel_candidates = [
            getattr(Settings, "CAROUSEL_IMAGE", None),
            os.path.join(Settings.ASSETS_DIR, "decoration", "CARRUSEL.png"),
        ]
        for path in carousel_candidates:
            if path and os.path.exists(path):
                carousel_image = pygame.image.load(path)
                try:
                    carousel_image = carousel_image.convert_alpha()
                except pygame.error:
                    pass
                cls._assets["carousel"] = carousel_image
                break

        for asset_name, asset_path in (
            ("previous_button", Settings.PREVIOUS_BUTTON_IMAGE),
            ("next_button", Settings.NEXT_BUTTON_IMAGE),
        ):
            if os.path.exists(asset_path):
                button_image = pygame.image.load(asset_path)
                try:
                    button_image = button_image.convert_alpha()
                except pygame.error:
                    pass
                cls._assets[asset_name] = button_image

    @classmethod
    def load_game_covers(cls, games: List[dict]) -> None:
        """Asocia una portada visual a cada juego detectado por el escáner."""
        for game in games:
            game_folder_path = game.get("folder_path")
            if game_folder_path and os.path.exists(game_folder_path):
                # El cover del juego debe estar en la carpeta assets/cover con el nombre launcher_cover.
                cover_path = os.path.join(game_folder_path, "assets", "cover", "launcher_cover")

                if os.path.exists(cover_path):
                    cls._covers[game["folder"]] = pygame.image.load(cover_path).convert_alpha()
                    continue

                alt_path = cls._find_cover_alternative(cover_path) if cover_path else None
                if alt_path:
                    cls._covers[game["folder"]] = pygame.image.load(alt_path).convert_alpha()
                    continue

                cls._covers[game["folder"]] = pygame.Surface((200, 120))
                cls._covers[game["folder"]].fill((32, 48, 72))

    @classmethod
    def _find_cover_alternative(cls, cover_path: Optional[str]) -> Optional[str]:
        """Busca una portada en formatos png/jpg/jpeg si no existe el archivo exacto."""
        if not cover_path:
            return None

        base, _ = os.path.splitext(cover_path)
        for ext in [".png", ".jpg", ".jpeg"]:
            alt_path = f"{base}{ext}"
            if os.path.exists(alt_path):
                return alt_path
        return None

    @classmethod
    def get_asset(cls, name: str):
        return cls._assets.get(name)

    @classmethod
    def get_font(cls, size: int) -> pygame.font.Font:
        if cls._font_path and os.path.exists(cls._font_path):
            return pygame.font.Font(cls._font_path, size)
        return pygame.font.Font(None, size)

    @classmethod
    def get_cover(cls, folder: str) -> pygame.Surface:
        return cls._covers.get(folder, pygame.Surface((200, 120)))
