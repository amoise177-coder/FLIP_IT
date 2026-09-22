import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path al ejecutar directamente este archivo
RUTA_RAIZ = Path(__file__).resolve().parent.parent
if str(RUTA_RAIZ) not in sys.path:
    sys.path.insert(0, str(RUTA_RAIZ))

import json
import pygame
import cv2
import numpy as np

from src.configuracion import (
    ANCHO_VENTANA,
    ALTO_VENTANA,
    FPS,
    COLOR_FONDO_FALLBACK,
    obtener_ruta_base,
)
from src.audio import GestorAudio
from src.recursos import GestorRecursos
from src.modelos import Categoria
from src.pantallas.base import Pantalla
from src.pantallas.inicio import PantallaInicio

class JuegoLetrea:
    """Motor central que orquesta el ciclo de vida del juego, eventos y transiciones."""
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.set_num_channels(32)

        self.ANCHO = ANCHO_VENTANA
        self.ALTO = ALTO_VENTANA
        self.FPS = FPS
        self.pantalla = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Letrea")
        self.reloj = pygame.time.Clock()

        # Resolución de rutas independiente de la ubicación de ejecución
        self.DIRECTORIO_BASE = obtener_ruta_base()
        self.DIRECTORIO_ASSETS = self.DIRECTORIO_BASE / "assets"

        # Servicios de audio y recursos gráficos
        self.audio = GestorAudio(self.DIRECTORIO_ASSETS)
        self.recursos = GestorRecursos(self.DIRECTORIO_ASSETS, self.ANCHO, self.ALTO)

        # Carga del banco de palabras
        self.base_categorias: dict[str, Categoria] = {}
        self._cargar_categorias()

        # Control de voz de bienvenida de la Maestra D (solo se muestran al entrar por primera vez)
        self.intro_categorias_mostrada = False
        self.intro_letras_mostrada = False

        # Control anti-doble clic (cooldown de 250 ms)
        self.COOLDOWN_CLIC_MS = 250
        self.ultimo_tiempo_clic = 0

        # Pantalla activa
        self.ejecutando = True
        self.pantalla_actual: Pantalla = PantallaInicio(self)

    def _cargar_categorias(self) -> None:
        """Carga el banco de palabras JSON y construye los modelos Categoria."""
        ruta_json = self.DIRECTORIO_ASSETS / "datos" / "banco_palabras.json"
        try:
            with open(ruta_json, "r", encoding="utf-8") as archivo:
                datos_json = json.load(archivo)
                for nombre_cat, info in datos_json.items():
                    self.base_categorias[nombre_cat] = Categoria(
                        nombre_cat, info["palabras"], info["excluidas"]
                    )
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error cargando banco_palabras.json: {e}")

    def cambiar_pantalla(self, nueva_pantalla: Pantalla, con_transicion: bool = True) -> None:
        """Transición suave y cambio polimórfico de pantalla."""
        if con_transicion:
            self.transicion_suave(nueva_pantalla)
        self.pantalla_actual = nueva_pantalla
        # Purga de eventos residuales para prevenir traspaso de clics accidentales
        pygame.event.clear(pygame.MOUSEBUTTONDOWN)
        pygame.event.clear(pygame.MOUSEBUTTONUP)
        self.ultimo_tiempo_clic = pygame.time.get_ticks()

    def transicion_suave(self, pantalla_destino: Pantalla) -> None:
        """Efecto visual de fundido cruzado (fade) entre pantallas."""
        superficie_fade = pygame.Surface((self.ANCHO, self.ALTO))
        superficie_fade.fill(COLOR_FONDO_FALLBACK)

        for alfa in range(0, 255, 80):
            self.pantalla.blit(self.pantalla, (0, 0))
            superficie_fade.set_alpha(alfa)
            self.pantalla.blit(superficie_fade, (0, 0))
            pygame.display.flip()
            pygame.time.delay(85)
            pygame.event.pump()

        for alfa in range(255, -1, -35):
            self.pantalla.fill(COLOR_FONDO_FALLBACK)
            pantalla_destino.dibujar(self.pantalla)
            superficie_fade.set_alpha(alfa)
            self.pantalla.blit(superficie_fade, (0, 0))
            pygame.display.flip()
            pygame.time.delay(40)
            pygame.event.pump()

    def reproducir_video_celebracion(self) -> None:
        """Reproduce el video de felicitaciones al completar correctamente una palabra."""
        capacidad_video = cv2.VideoCapture(str(self.recursos.ruta_video_celebrar))
        if capacidad_video.isOpened():
            reproduciendo = True
            while reproduciendo:
                exito, fotograma = capacidad_video.read()
                if not exito:
                    break

                fotograma = cv2.resize(fotograma, (self.ANCHO, self.ALTO))
                fotograma = cv2.cvtColor(fotograma, cv2.COLOR_BGR2RGB)
                fotograma = np.rot90(fotograma)
                sup_video = pygame.surfarray.make_surface(fotograma)

                self.pantalla.blit(sup_video, (0, 0))
                pygame.display.flip()

                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                        reproduciendo = False
                        self.ejecutando = False

                self.reloj.tick(30)
            capacidad_video.release()

    def dibujar_texto(self, texto: str, fuente: pygame.font.Font, color: tuple, superficie: pygame.Surface, x: int, y: int) -> None:
        """Utilidad de renderizado de texto centrado."""
        obj_texto = fuente.render(texto, True, color)
        rect_texto = obj_texto.get_rect(center=(x, y))
        superficie.blit(obj_texto, rect_texto)

    def ejecutar(self) -> None:
        """Bucle principal del juego a 60 FPS con control de eventos y debounce de clics."""
        self.audio.iniciar_musica_fondo()

        while self.ejecutando:
            # 1. Procesamiento de eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.ejecutando = False
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    self.ejecutando = False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    ahora = pygame.time.get_ticks()
                    if ahora - self.ultimo_tiempo_clic < self.COOLDOWN_CLIC_MS:
                        continue  # Bloquea el doble clic rápido accidental
                    self.ultimo_tiempo_clic = ahora
                    self.pantalla_actual.manejar_evento(evento)
                else:
                    self.pantalla_actual.manejar_evento(evento)

            # 2. Actualización de estado
            if self.ejecutando:
                self.pantalla_actual.actualizar()

                # 3. Dibujado polimórfico
                self.pantalla.fill(COLOR_FONDO_FALLBACK)
                self.pantalla_actual.dibujar(self.pantalla)
                pygame.display.flip()
                self.reloj.tick(self.FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    juego = JuegoLetrea()
    juego.ejecutar()
