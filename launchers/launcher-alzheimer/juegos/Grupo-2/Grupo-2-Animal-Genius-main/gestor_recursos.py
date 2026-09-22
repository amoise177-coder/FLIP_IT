import pygame
from pathlib import Path
from constants import const


class GestorRecursos:

    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        ruta_fuente = base_dir / "assets" / "fonts" / "Fredoka.ttf"

        try:
            self.fuente_titulo = pygame.font.Font(str(ruta_fuente), 32)
            self.fuente_texto = pygame.font.Font(str(ruta_fuente), 22)
        except (FileNotFoundError, OSError) as e:
            print(f"No se pudo cargar la fuente en '{ruta_fuente}': {e}. Usando fuente predeterminada.")
            self.fuente_titulo = pygame.font.SysFont("Comic Sans MS", 32)
            self.fuente_texto = pygame.font.SysFont("Comic Sans MS", 22)

        self.fondos = self._cargar_fondos()

        self.fondos_biomas = self._cargar_fondos_biomas()

    def _cargar_fondos(self) -> dict[str, pygame.Surface | None]:
        archivos = {
            "menu_principal": "fondo_menu_principal.jpg",
            "menu": "fondo_menu.jpg",
            "modos": "fondo_modos.jpg",
            "juego": "fondo_juego.jpg",
        }
        fondos = {}

        for clave, archivo in archivos.items():
            ruta = const.BACKGROUNDS_DIR / archivo
            try:
                img = pygame.image.load(str(ruta)).convert()
                fondos[clave] = pygame.transform.scale(
                    img, (const.ANCHO_PANTALLA, const.ALTO_PANTALLA)
                )
            except Exception as e:
                print(f"Error cargando fondo '{archivo}': {e}")
                fondos[clave] = None

        return fondos

    def _cargar_fondos_biomas(self) -> dict[str, pygame.Surface | None]:
        archivos_biomas = {
            "pradera": "pradera.jpg",
            "bosque": "bosque.jpg",
            "selva": "selva.jpg",
            "artico": "artico.jpg",
            "oceano": "oceano.jpg",
        }
        surfaces = {}

        for bioma, archivo in archivos_biomas.items():
            ruta = const.BACKGROUNDS_DIR / archivo
            try:
                img_base = pygame.image.load(str(ruta)).convert()
                surfaces[bioma] = img_base
            except Exception as e:
                print(f"Error procesando imagen de bioma '{bioma}' en {ruta}: {e}")
                surfaces[bioma] = None

        return surfaces

    def cargar_imagen_animal(
        self, nombre_archivo: str, ancho: int = 440, alto: int = 310
    ) -> pygame.Surface | None:
        ruta = const.IMAGES_DIR / nombre_archivo
        try:
            img = pygame.image.load(str(ruta)).convert()
            return pygame.transform.scale(img, (ancho, alto))
        except Exception as e:
            print(f"Error cargando imagen del animal '{nombre_archivo}': {e}")
            return None

    def cargar_logo(self, ancho: int = 400, alto: int = 200) -> pygame.Surface | None:
        ruta = const.BACKGROUNDS_DIR / "logo.png"
        try:
            img = pygame.image.load(str(ruta)).convert_alpha()
            return pygame.transform.smoothscale(img, (ancho, alto))
        except Exception as e:
            print(f"Error cargando el logo: {e}")
            return None
