"""Gestor del subsistema de audio y efectos de sonido de Letrea."""

import pygame
from pathlib import Path

class GestorAudio:
    """Gestiona la carga con caché, reproducción y volúmenes de efectos y música de fondo."""
    def __init__(self, ruta_assets: Path):
        self._ruta_audio = ruta_assets / "audio"
        self._volumen_efectos = 0.4
        self._sonidos_cacheados: dict[str, pygame.mixer.Sound] = {}
        self._nombres_archivos = {
            "atras": "atras.MP3",
            "musica": "musicafondo.MP3",
            "categoria": "categoria.MP3",
            "deslizar": "deslizar.MP3",
            "jugar": "jugar.MP3",
            "letra": "letra.MP3",
            "letra2": "letra2.MP3",
            "correcto": "letracompletado.MP3",
            "borrar": "palabraborrar.MP3",
            "error_leve": "palabraerror.MP3",
            "botonayuda": "botonayuda.MP3",
            "nivelcompletado": "nivelcompletado.MP3",
            "categoriaselec": "categoriaselec.MP3",
            "letraselec": "letraselec.MP3",
            "intentalodenuevo": "intentalodenuevo.MP3",
            "amarillo1": "amarillo1.MP3",
            "amarillo2": "amarillo2.MP3",
            "aparecemaestrad": "aparecemaestrad.MP3",
            "animaleshover": "animaleshover.MP3",
            "coloreshover": "coloreshover.MP3",
            "frutasycomidahover": "frutasycomidahover.MP3",
            "hogarhover": "hogarhover.MP3",
            "ropaypdchover": "ropaypdchover.MP3",
        }

    def _buscar_archivo(self, archivo: str) -> Path | None:
        """Busca el archivo de audio tolerando mayúsculas y minúsculas."""
        for intento in [
            self._ruta_audio / archivo,
            self._ruta_audio / archivo.lower(),
            self._ruta_audio / archivo.upper(),
            self._ruta_audio / archivo.replace(".mp3", ".MP3"),
            self._ruta_audio / archivo.replace(".MP3", ".mp3"),
        ]:
            if intento.exists():
                return intento
        return None

    def reproducir(self, nombre_audio: str) -> pygame.mixer.Channel | None:
        """Reproduce el efecto de sonido desde el caché y retorna el canal."""
        if nombre_audio not in self._sonidos_cacheados:
            archivo = self._nombres_archivos.get(nombre_audio)
            if not archivo:
                return None
            ruta_completa = self._buscar_archivo(archivo)
            if not ruta_completa:
                return None
            try:
                sonido = pygame.mixer.Sound(str(ruta_completa))
                self._sonidos_cacheados[nombre_audio] = sonido
            except (pygame.error, FileNotFoundError) as e:
                print(f"No se pudo cargar audio {archivo}: {e}")
                return None
        try:
            # Los efectos hover deben sonar sutiles (volumen 0.08)
            vol = 0.08 if "hover" in nombre_audio else self._volumen_efectos
            self._sonidos_cacheados[nombre_audio].set_volume(vol)
            return self._sonidos_cacheados[nombre_audio].play()
        except pygame.error:
            return None

    def iniciar_musica_fondo(self) -> None:
        """Pone la música de fondo en bucle continuo."""
        archivo_musica = self._nombres_archivos.get("musica")
        if not archivo_musica:
            return
        ruta_completa = self._buscar_archivo(archivo_musica)
        if not ruta_completa:
            return
        try:
            pygame.mixer.music.load(str(ruta_completa))
            pygame.mixer.music.set_volume(self._volumen_efectos)
            pygame.mixer.music.play(-1)
        except (pygame.error, FileNotFoundError):
            pass
