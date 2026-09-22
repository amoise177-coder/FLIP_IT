import pygame
from pathlib import Path
from src.configuracion import TAMANO_BOTON_LETRA, ANCHO_OVER, ALTO_OVER

class GestorRecursos:
    def __init__(self, ruta_assets: Path, ancho_pantalla: int, alto_pantalla: int):
        self._ruta_assets = ruta_assets
        self._ruta_imagenes = ruta_assets / "imagenes"
        self._ancho = ancho_pantalla
        self._alto = alto_pantalla
        self._cache_pistas: dict[tuple[str, str], list[pygame.Surface]] = {}

        self._cargar_fuentes()
        self._cargar_imagenes_ui()
        self._cargar_letras()
        self._cargar_recursos_categorias()
        self.ruta_video_celebrar = self._ruta_assets / "video" / "celebrar.mp4"

    def _cargar_fuentes(self) -> None:
        ruta_fuente = self._ruta_assets / "fuentes" / "Baloo.ttf"
        try:
            self.fuente_titulo = pygame.font.Font(str(ruta_fuente), 85)
            self.fuente_grande = pygame.font.Font(str(ruta_fuente), 110)
            self.fuente_media = pygame.font.Font(str(ruta_fuente), 40)
        except (FileNotFoundError, pygame.error):
            self.fuente_titulo = pygame.font.SysFont("Arial", 85, bold=True)
            self.fuente_grande = pygame.font.SysFont("Arial", 110, bold=True)
            self.fuente_media = pygame.font.SysFont("Arial", 40, bold=True)

    def cargar_imagen(self, nombre_archivo: str, escalar_pantalla: bool = False, tamano: tuple[int, int] | None = None) -> pygame.Surface | None:
        ruta = self._ruta_imagenes / nombre_archivo
        try:
            img = pygame.image.load(str(ruta)).convert_alpha()
            if escalar_pantalla:
                return pygame.transform.scale(img, (self._ancho, self._alto))
            elif tamano:
                return pygame.transform.scale(img, tamano)
            return img
        except (FileNotFoundError, pygame.error):
            return None

    def cargar_maestra_d(self, nombre_archivo: str, alto_deseado: int = 330) -> pygame.Surface | None:
        """Carga una pose de la Maestra D escalándola suavemente sin deformarla."""
        ruta = self._ruta_imagenes / nombre_archivo
        try:
            img = pygame.image.load(str(ruta)).convert_alpha()
            ancho_orig, alto_orig = img.get_size()
            ancho_deseado = int(ancho_orig * (alto_deseado / alto_orig))
            return pygame.transform.smoothscale(img, (ancho_deseado, alto_deseado))
        except (FileNotFoundError, pygame.error):
            return None

    def obtener_maestra_d(self, pose: str = "MD1") -> pygame.Surface | None:
        """Retorna la superficie precalculada de la pose de la Maestra D solicitada."""
        return self.poses_maestra_d.get(pose)

    def _cargar_imagenes_ui(self) -> None:
        self.img_fondo1 = self.cargar_imagen("fondo1.png", escalar_pantalla=True)
        self.img_fondo2 = self.cargar_imagen("fondo2.png", escalar_pantalla=True)
        self.img_fondo4 = self.cargar_imagen("fondo4.png", escalar_pantalla=True)

        self.img_btn_jugar = self.cargar_imagen("boton1.png")
        self.img_atras = self.cargar_imagen("atras.png")
        self.img_atras_azul = self.cargar_imagen("atrasazul.png")

        # Botón de ayuda: extraer del lienzo 1280x720 y estandarizar a 80x80
        img_ayuda_raw = self.cargar_imagen("ayuda.png")
        if img_ayuda_raw:
            bbox = img_ayuda_raw.get_bounding_rect()
            if bbox.width > 0 and bbox.height > 0:
                self.img_ayuda = pygame.transform.smoothscale(img_ayuda_raw.subsurface(bbox), (80, 80))
            else:
                self.img_ayuda = self.cargar_imagen("ayudaazul.png", tamano=(80, 80))
        else:
            self.img_ayuda = self.cargar_imagen("ayudaazul.png", tamano=(80, 80))

        self.img_ayuda_azul = self.cargar_imagen("ayudaazul.png", tamano=(80, 80))
        self.img_ayuda_inicio = self.cargar_imagen("ayudainicio.png", escalar_pantalla=True)
        self.img_ayuda_inicio2 = self.cargar_imagen("ayudainicio2.png", escalar_pantalla=True)

        self.img_btn_izq = self.cargar_imagen("deslizarizq.png")
        self.img_btn_der = self.cargar_imagen("deslizardere.png")
        self.img_marco_pista = self.cargar_imagen("marco.png", tamano=(250, 250))

        # Poses de la Maestra D (altura 330px para visualización destacada)
        self.poses_maestra_d = {
            "MD1": self.cargar_maestra_d("MD1.png", alto_deseado=330),
            "MD2": self.cargar_maestra_d("MD2.png", alto_deseado=330),
            "MD3": self.cargar_maestra_d("MD3.png", alto_deseado=330),
            "MD4": self.cargar_maestra_d("MD4.png", alto_deseado=330),
        }

    def _cargar_letras(self) -> None:
        """Carga y precalcula texturas de letras activas e inactivas."""
        self.imagenes_letras = {}
        self.imagenes_letras_desactivadas = {}
        tamano_letra = (TAMANO_BOTON_LETRA, TAMANO_BOTON_LETRA)

        for indice, letra in enumerate([chr(i) for i in range(65, 91)], start=1):
            img = self.cargar_imagen(f"{indice}.png", tamano=tamano_letra)
            self.imagenes_letras[letra] = img
            if img:
                img_desc = img.copy()
                img_desc.set_alpha(110)
                self.imagenes_letras_desactivadas[letra] = img_desc

        img_enie = self.cargar_imagen("ñ.png", tamano=tamano_letra) or self.cargar_imagen("enie.png", tamano=tamano_letra)
        if img_enie:
            self.imagenes_letras["Ñ"] = img_enie
            img_desc_enie = img_enie.copy()
            img_desc_enie.set_alpha(110)
            self.imagenes_letras_desactivadas["Ñ"] = img_desc_enie

    def _cargar_recursos_categorias(self) -> None:
        self.fondos_categorias = {
            "Animales": self.cargar_imagen("fondo3animales.png", escalar_pantalla=True),
            "Frutas y Comida": self.cargar_imagen("fondo3frutas.png", escalar_pantalla=True),
            "Colores": self.cargar_imagen("fondo3colores.png", escalar_pantalla=True),
            "Objetos de la Casa": self.cargar_imagen("fondo3.png", escalar_pantalla=True),
            "Partes del Cuerpo": self.cargar_imagen("fondo3ryp.png", escalar_pantalla=True),
        }

        self.portadas_carrusel = {
            "Animales": self.cargar_imagen("animales.png", tamano=(250, 250)),
            "Frutas y Comida": self.cargar_imagen("frutas.png", tamano=(250, 250)),
            "Colores": self.cargar_imagen("colores.png", tamano=(250, 250)),
            "Objetos de la Casa": self.cargar_imagen("odlc.png", tamano=(250, 250)),
            "Partes del Cuerpo": self.cargar_imagen("ryp.png", tamano=(250, 250)),
        }

        self.portadas_over = {
            "Animales": self.cargar_imagen("animalesover.png", tamano=(ANCHO_OVER, ALTO_OVER)),
            "Frutas y Comida": self.cargar_imagen("frutasover.png", tamano=(ANCHO_OVER, ALTO_OVER)),
            "Colores": self.cargar_imagen("coloresover.png", tamano=(ANCHO_OVER, ALTO_OVER)),
            "Objetos de la Casa": self.cargar_imagen("odhover.png", tamano=(ANCHO_OVER, ALTO_OVER)),
            "Partes del Cuerpo": self.cargar_imagen("pyrover.png", tamano=(ANCHO_OVER, ALTO_OVER)),
        }

    def cargar_pistas_por_letra(self, nombre_categoria: str, letra: str) -> list[pygame.Surface]:
        """Carga y cachea las pistas gráficas asociadas a una categoría y letra."""
        clave = (nombre_categoria, letra)
        if clave in self._cache_pistas:
            return self._cache_pistas[clave]

        imagenes = []
        ruta_carpeta = self._ruta_imagenes / nombre_categoria / letra
        if ruta_carpeta.exists():
            for archivo in sorted(ruta_carpeta.iterdir()):
                if archivo.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    try:
                        img = pygame.image.load(str(archivo)).convert_alpha()
                        img = pygame.transform.scale(img, (150, 150))
                        imagenes.append(img)
                    except pygame.error:
                        pass

        if not imagenes:
            img_respaldo = self.portadas_carrusel.get(nombre_categoria)
            if img_respaldo:
                imagenes.append(img_respaldo)

        self._cache_pistas[clave] = imagenes
        return imagenes

    def liberar_pistas(self, nombre_categoria: str, letra: str) -> None:
        """Libera de la memoria RAM las pistas de una letra una vez completada."""
        self._cache_pistas.pop((nombre_categoria, letra), None)
