import os

class Settings:
    TITLE = "V-Sports Launcher"
    S_WIDTH = 1280
    S_HEIGHT = 720
    FPS = 60
    BACKGROUND_COLOR = (12, 18, 35)
    TEXT_COLOR = (240, 240, 240)
    HIGHLIGHT_COLOR = (64, 176, 255)

    ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), os.pardir))
    ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
    FONT_PATH = os.path.join(ASSETS_DIR, "font", "Font.otf")
    MENU_BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, "decoration", "fondo2.png")
    START_BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, "decoration", "fondo1.png")
    BANNER_IMAGE = os.path.join(ASSETS_DIR, "decoration", "BANNER.png")
    BACK_BUTTON_IMAGE = os.path.join(ASSETS_DIR, "decoration", "BOTON2.png")
    HELP_BUTTON_IMAGE = os.path.join(ASSETS_DIR, "decoration", "BOTON1.png")
    CAROUSEL_IMAGE = os.path.join(ASSETS_DIR, "decoration", "CARRUSEL.png")
    PREVIOUS_BUTTON_IMAGE = os.path.join(ASSETS_DIR, "decoration", "Recurso 15.png")
    NEXT_BUTTON_IMAGE = os.path.join(ASSETS_DIR, "decoration", "Recurso 14.png")
    MAIN_TITLE_IMAGE = BANNER_IMAGE
    MUSIC_FILES = [
        os.path.join(ASSETS_DIR, "music", "Changing-Seasons.mp3"),
        os.path.join(ASSETS_DIR, "music", "Everything-Everything.mp3"),
        os.path.join(ASSETS_DIR, "music", "Slingshot_1.mp3"),
        os.path.join(ASSETS_DIR, "music", "hotel kawai.mp3"),
        os.path.join(ASSETS_DIR, "music", "sunny.mp3"),
        os.path.join(ASSETS_DIR, "music", "tea time.mp3"),
    ]
    SOUND_SELECT = os.path.join(ASSETS_DIR, "sounds", "wii confirm.mp3")
    SOUND_QUIT = os.path.join(ASSETS_DIR, "sounds", "wii click.mp3")
    SOUND_START = os.path.join(ASSETS_DIR, "sounds", "wii click.mp3")
    SOUND_NAV = os.path.join(ASSETS_DIR, "sounds", "ppop.mp3")
