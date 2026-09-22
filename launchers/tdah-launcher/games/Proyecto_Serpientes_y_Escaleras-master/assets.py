"""
Módulo de gestión de recursos (imágenes, fuentes y audio).
Garantiza fallback automático y el uso de fuentes internas seguras.
"""
import os
from typing import Dict, Tuple, Optional, List
import pygame


class AssetManager:
    """
    Gestiona la carga de imágenes y fuentes del juego.
    Utiliza fuentes internas de Pygame (pygame.font.Font(None, ...)) para evitar
    dependencias de fuentes del sistema o glifos faltantes.
    """
    def __init__(self, base_path: str = "assets"):
        self.base_path = base_path
        self.images_path = os.path.join(base_path, "images")
        self.fonts_path = os.path.join(base_path, "fonts")
        self.images: Dict[str, pygame.Surface] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        self._init_fonts()

    def _init_fonts(self):
        """Inicializa tipografías usando exclusivamente la fuente interna de Pygame."""
        pygame.font.init()
        self.fonts["big_title"] = pygame.font.Font(None, 84)
        self.fonts["title"] = pygame.font.Font(None, 34)
        self.fonts["subtitle"] = pygame.font.Font(None, 24)
        self.fonts["body"] = pygame.font.Font(None, 20)
        self.fonts["bold"] = pygame.font.Font(None, 20)
        self.fonts["small"] = pygame.font.Font(None, 16)
        self.fonts["tile"] = pygame.font.Font(None, 17)
        self.fonts["message"] = pygame.font.Font(None, 22)
        self.fonts["winner"] = pygame.font.Font(None, 36)

    def get_font(self, name: str) -> pygame.font.Font:
        return self.fonts.get(name, self.fonts["body"])

    def load_image(self, name: str, size: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        """Carga una imagen opcional desde assets/images/; retorna None si no existe."""
        if name in self.images:
            return self.images[name]

        file_path = os.path.join(self.images_path, name)
        if os.path.exists(file_path):
            try:
                img = pygame.image.load(file_path).convert_alpha()
                if size:
                    img = pygame.transform.smoothscale(img, size)
                self.images[name] = img
                return img
            except Exception as e:
                print(f"[AssetManager] Error al cargar la imagen {name}: {e}")
        return None


class AudioManager:
    """
    Gestiona la reproducción de música y efectos sonoros con soporte para silenciado global (Mute).
    """
    def __init__(self, base_path: Optional[str] = None):
        # Rutas de búsqueda prioritarias (assets/sounds, assets/audio, assets)
        self.base_paths: List[str] = []
        if base_path:
            self.base_paths.append(base_path)
        self.base_paths.extend([
            os.path.join("assets", "sounds"),
            os.path.join("assets", "audio"),
            "assets"
        ])

        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.is_initialized = False
        self.is_muted = False
        self.music_volume = 0.35
        self.current_music: Optional[str] = None

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.is_initialized = True
        except Exception as e:
            print(f"[AudioManager] No se pudo inicializar pygame.mixer: {e}")

    def _resolve_path(self, name: str) -> Optional[str]:
        if os.path.isfile(name):
            return name

        # Mapeo de alias comunes para efectos sonoros
        aliases = {
            "dice_roll": "dados",
            "dice": "dados",
            "dado": "dados",
            "roll": "dados",
            "lanzamiento": "dados"
        }
        alias_name = aliases.get(name.lower(), None)

        variations = [
            name,
            name.replace(" ", "-"),
            name.replace(" ", "_"),
            name.replace("-", " "),
            name.replace("_", " "),
            name.lower()
        ]
        if alias_name:
            variations.extend([alias_name, f"{alias_name}s", alias_name.replace(" ", "-")])

        seen = set()
        clean_variations = [v for v in variations if not (v in seen or seen.add(v))]
        extensions = ["", ".mp3", ".wav", ".ogg"]

        for bp in self.base_paths:
            if not os.path.exists(bp):
                continue

            for var in clean_variations:
                for ext in extensions:
                    candidate = var if (ext != "" and var.endswith(ext)) else f"{var}{ext}"
                    path = os.path.join(bp, candidate)
                    if os.path.isfile(path):
                        return path

            # Búsqueda difusa por nombre normalizado
            try:
                norm_query = name.lower().replace(" ", "").replace("-", "").replace("_", "")
                for fname in os.listdir(bp):
                    base, _ = os.path.splitext(fname)
                    norm_base = base.lower().replace(" ", "").replace("-", "").replace("_", "")
                    if norm_query in norm_base or norm_base in norm_query:
                        candidate_path = os.path.join(bp, fname)
                        if os.path.isfile(candidate_path):
                            return candidate_path
            except Exception:
                pass

        return None

    def set_music_volume(self, volume: float, auto_unmute: bool = True):
        """Ajusta el volumen de la música (entre 0.0 y 1.0) y actualiza el mezclador."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.is_muted and auto_unmute and self.music_volume > 0:
            self.is_muted = False
        if self.is_initialized:
            try:
                pygame.mixer.music.set_volume(0.0 if self.is_muted else self.music_volume)
                if not self.is_muted:
                    pygame.mixer.music.unpause()
                    if not pygame.mixer.music.get_busy() and self.current_music:
                        pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"[AudioManager] Error al ajustar volumen de música: {e}")

    def get_music_volume(self) -> float:
        """Retorna el volumen actual configurado para la música."""
        return self.music_volume

    def change_music_volume(self, delta: float):
        """Incrementa o decrementa el volumen de la música por un delta."""
        new_vol = round(self.music_volume + delta, 2)
        self.set_music_volume(new_vol, auto_unmute=(delta > 0))

    def toggle_mute(self) -> bool:
        """Alterna el estado de silenciado y detiene o reanuda la música de fondo."""
        self.is_muted = not self.is_muted
        if self.is_initialized:
            try:
                if self.is_muted:
                    pygame.mixer.music.set_volume(0.0)
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.unpause()
                    if not pygame.mixer.music.get_busy() and self.current_music:
                        pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"[AudioManager] Error al alternar silencio: {e}")
        return self.is_muted

    def play_sound(self, sound_name: str, volume: float = 0.7):
        """Reproduce un efecto de sonido si el archivo existe y el juego no está silenciado."""
        if not self.is_initialized or self.is_muted:
            return

        if sound_name not in self.sounds:
            path = self._resolve_path(sound_name)
            if path:
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(volume)
                    self.sounds[sound_name] = snd
                except Exception as e:
                    print(f"[AudioManager] Error cargando sonido {path}: {e}")

        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()

    def play_music(self, music_file: str = "musica-de-fondo.mp3", loop: bool = True, volume: float = 0.35):
        """Reproduce música ambiental en bucle continuo durante la ejecución del juego."""
        if not self.is_initialized:
            return

        self.music_volume = volume
        path = self._resolve_path(music_file)
        if path and os.path.isfile(path):
            try:
                self.current_music = path
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0.0 if self.is_muted else self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                if self.is_muted:
                    pygame.mixer.music.pause()
            except Exception as e:
                print(f"[AudioManager] Error cargando música {path}: {e}")
        else:
            print(f"[AudioManager] No se encontró el archivo de música: {music_file}")
