import pygame
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Elemento:
    _CACHE_IMAGENES = {}
    _CACHE_SONIDOS = {}

    def __init__(self, id_elemento, nombre, ruta_imagen=None, ruta_audio=None):
        self.id = id_elemento
        self.nombre = nombre
        self._ruta_imagen = Path(ruta_imagen) if ruta_imagen else None
        self._ruta_audio = Path(ruta_audio) if ruta_audio else None
        self.imagen = None
        self.sonido = None

    def obtener_ruta_imagen(self):
        return self._ruta_imagen

    def obtener_ruta_audio(self):
        return self._ruta_audio

    def cargar_recursos(self, tamano=(350, 280)):
        clave_img = (str(self._ruta_imagen), tamano)
        if self._ruta_imagen and self._ruta_imagen.exists():
            if clave_img in Elemento._CACHE_IMAGENES:
                self.imagen = Elemento._CACHE_IMAGENES[clave_img]
            else:
                try:
                    imagen_original = pygame.image.load(str(self._ruta_imagen))
                    self.imagen = pygame.transform.scale(imagen_original, tamano)
                    Elemento._CACHE_IMAGENES[clave_img] = self.imagen
                except Exception as e:
                    print(f"Error al cargar la imagen '{self._ruta_imagen}': {e}")
                
        if self._ruta_audio and self._ruta_audio.exists():
            clave_audio = str(self._ruta_audio)
            if clave_audio in Elemento._CACHE_SONIDOS:
                self.sonido = Elemento._CACHE_SONIDOS[clave_audio]
            else:
                try:
                    if not pygame.mixer.get_init():
                        pygame.mixer.init()
                    self.sonido = pygame.mixer.Sound(str(self._ruta_audio))
                    Elemento._CACHE_SONIDOS[clave_audio] = self.sonido
                except Exception as e:
                    print(f"Error al cargar el audio '{self._ruta_audio}': {e}")

    def reproducir_sonido(self, limite_ms=4000):
        if self.sonido:
            pygame.mixer.stop()
            self.sonido.play(maxtime=limite_ms)


class CatalogoElementos:
    def __init__(self):
        img_dir = BASE_DIR / "assets" / "imagenes"
        audio_dir = BASE_DIR / "assets" / "audios"

        self.elementos = [

            Elemento(1, "Acordeón", img_dir / "acordeon.jpg", audio_dir / "acordeon.mp3"),
            Elemento(2, "Batería", img_dir / "bateria.jpg", audio_dir / "bateria.mp3"),
            Elemento(3, "Campana", img_dir / "campana.jpg", audio_dir / "campana.mp3"),
            Elemento(4, "Guitarra", img_dir / "guitarra.jpg", audio_dir / "guitarra.mp3"),
            Elemento(5, "Piano", img_dir / "piano.jpg", audio_dir / "piano.mp3"),
            Elemento(6, "Saxofón", img_dir / "saxofon.jpg", audio_dir / "saxofon.mp3"),
            Elemento(7, "Teclado", img_dir / "teclado.jpg", audio_dir / "teclado.mp3"),
            Elemento(8, "Trompeta", img_dir / "trompeta.jpg", audio_dir / "trompeta.mp3"),
            Elemento(9, "Violín", img_dir / "violin.jpg", audio_dir / "violin.mp3"),
            Elemento(10, "Xilófono", img_dir / "xilofono.jpg", audio_dir / "xilofono.mp3"),

            Elemento(11, "Ardilla", img_dir / "ardilla.jpg", audio_dir / "ardilla.mp3"),
            Elemento(12, "Aves", img_dir / "aves.jpg", audio_dir / "aves.mp3"),
            Elemento(13, "Búho", img_dir / "buho.jpg", audio_dir / "buho.mp3"),
            Elemento(14, "Caballo", img_dir / "caballo.jpg", audio_dir / "caballo.mp3"),
            Elemento(15, "Cabra", img_dir / "cabra.jpg", audio_dir / "cabra.mp3"),
            Elemento(16, "Cerdo", img_dir / "cerdo.jpg", audio_dir / "cerdo.mp3"),
            Elemento(17, "Elefante", img_dir / "elefante.jpg", audio_dir / "elefante.mp3"),
            Elemento(18, "Gallo", img_dir / "gallo.jpg", audio_dir / "gallo.mp3"),
            Elemento(19, "Gato", img_dir / "gato.jpg", audio_dir / "gato.mp3"),
            Elemento(20, "Grillo", img_dir / "grillo.jpg", audio_dir / "grillo.mp3"),
            Elemento(21, "León", img_dir / "leon.jpg", audio_dir / "leon.mp3"),
            Elemento(22, "Lobo", img_dir / "lobo.jpg", audio_dir / "lobo.mp3"),
            Elemento(23, "Mono", img_dir / "mono.jpg", audio_dir / "mono.mp3"),
            Elemento(24, "Oveja", img_dir / "oveja.jpg", audio_dir / "oveja.mp3"),
            Elemento(25, "Pato", img_dir / "pato.jpg", audio_dir / "pato.mp3"),
            Elemento(26, "Perro", img_dir / "perro.jpg", audio_dir / "perro.mp3"),
            Elemento(27, "Tigre", img_dir / "tigre.jpg", audio_dir / "tigre.mp3"),
            Elemento(28, "Vaca", img_dir / "vaca.jpg", audio_dir / "vaca.mp3"),

            Elemento(29, "Avión", img_dir / "avion.jpg", audio_dir / "avion.mp3"),
            Elemento(30, "Camión", img_dir / "camion.jpg", audio_dir / "camion.mp3"),
            Elemento(31, "Carro", img_dir / "carro.jpg", audio_dir / "carro.mp3"),
            Elemento(32, "Elevador", img_dir / "elevador.jpg", audio_dir / "elevador.mp3"),
            Elemento(33, "Helicóptero", img_dir / "helicoptero.jpg", audio_dir / "helicoptero.mp3"),
            Elemento(34, "Moto", img_dir / "moto.jpg", audio_dir / "moto.mp3"),
            Elemento(35, "Tren", img_dir / "tren.jpg", audio_dir / "tren.mp3"),
            Elemento(36, "Yate", img_dir / "yate.jpg", audio_dir / "yate.mp3"),

            Elemento(37, "Cascada", img_dir / "cascada.jpg", audio_dir / "cascada.mp3"),
            Elemento(38, "Despertador", img_dir / "despertador.jpg", audio_dir / "despertador.mp3"),
            Elemento(39, "Fuego", img_dir / "fuego.jpg", audio_dir / "fuego.mp3"),
            Elemento(40, "Lluvia", img_dir / "lluvia.jpg", audio_dir / "lluvia.mp3"),
            Elemento(41, "Olas", img_dir / "olas.jpg", audio_dir / "olas.mp3"),
            Elemento(42, "Río", img_dir / "rio.jpg", audio_dir / "rio.mp3")
        ]

    def obtener_todos(self):
        return self.elementos