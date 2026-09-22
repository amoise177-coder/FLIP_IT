from pathlib import Path
import math
import struct
import random
from typing import Any, Callable, Dict, List, Optional, Union
import pygame

# --- Rutas Dinámicas Centralizadas desde config ---
from .config import RUTA_RAIZ, RUTA_ASSETS, RUTA_SONIDOS, RUTA_MUSICA

# --- Configuración Declarativa Fuertemente Tipada de SFX ---
_TONES: Dict[str, tuple[float, List[tuple[float, float]], str]] = {
    "click": (0.04, [(900.0, 0.25)], "linear"),
    "tile_pick": (0.07, [(520.0, 0.3), (1040.0, 0.1)], "exp"),
    "tile_place": (0.09, [(380.0, 0.35), (760.0, 0.1)], "exp"),
    "hint": (0.30, [(739.99, 0.25), (1174.66, 0.15)], "exp"),
    "invalid": (0.18, [(240.0, 0.22), (320.0, 0.08)], "exp"),
}

_ARPEGGIOS: Dict[str, tuple[List[tuple[float, float]], float]] = {
    "word_success": ([(523.25, 0.12), (659.25, 0.12), (783.99, 0.22)], 0.32),
    "recall": ([(480.0, 0.07), (360.0, 0.08)], 0.25),
}

# --- Correspondencia entre el nombre lógico del efecto y los archivos reales
# presentes en assets/sounds. Se intentan en orden; el primero que exista gana.
# Sin este mapa los .mp3 del proyecto nunca se cargaban y todos los efectos
# terminaban siendo tonos sintetizados.
_ARCHIVOS_SFX: Dict[str, tuple[str, ...]] = {
    "click": ("BotonesMenu", "click"),
    "tile_pick": ("sonido_letras", "tile_pick"),
    "tile_place": ("sonidoTAP", "tile_place"),
    "word_success": ("correcto", "word_success"),
    "recall": ("correcto2", "recall"),
    "hint": ("correcto2", "hint"),
    "invalid": ("incorrecto", "invalid"),
}


class GestorAudio:
    """Gestor centralizado de audio, efectos sonoros (SFX) y música de fondo (BGM)."""

    def __init__(
        self,
        sounds_dir: Optional[Union[str, Path]] = None,
        enabled: bool = True,
        volume: float = 0.7
    ) -> None:
        self._sounds_dir: Path = Path(sounds_dir) if sounds_dir else RUTA_SONIDOS
        self._enabled: bool = enabled
        self._muted: bool = False
        self._volume: float = max(0.0, min(1.0, volume))
        self._volumen_musica: float = 0.5
        self._musica_activa: bool = True
        self._musica_pausada: bool = False
        self._musica_cargada: Optional[str] = None
        self._pista_actual: Optional[str] = None
        self._available: bool = False
        self._sounds: Dict[str, pygame.mixer.Sound] = {}
        self._playlist_musica: List[Path] = []
        self._indice_cancion_actual: int = 0
        self._reproduccion_aleatoria: bool = True

        self._init_mixer()
        if self._available:
            self._load_or_generate_sounds()
            self._cargar_playlist_musica()

    def _init_mixer(self) -> None:
        """Inicializa de forma segura el subsistema de audio de Pygame."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._available = True
        except Exception as err:
            print(f"[SOUND] Mixer no disponible ({err}). El juego continuará en modo silencioso.")
            self._available = False

    def _mixer_call(self, func: Callable[..., Any], *args: Any) -> None:
        """Invoca funciones del mixer de forma segura protegiendo contra excepciones."""
        if self._available:
            try: func(*args)
            except Exception: pass

    # --- Propiedades de Estado ---
    @property
    def is_available(self) -> bool: return self._available
    @property
    def is_muted(self) -> bool: return self._muted
    @property
    def sfx_enabled(self) -> bool: return self._enabled
    @property
    def volume(self) -> float: return self._volume
    @property
    def volumen_musica(self) -> float: return self._volumen_musica
    @property
    def pista_actual(self) -> Optional[str]: return self._pista_actual
    @property
    def reproduccion_aleatoria(self) -> bool: return self._reproduccion_aleatoria
    @reproduccion_aleatoria.setter
    def reproduccion_aleatoria(self, valor: bool) -> None: self._reproduccion_aleatoria = bool(valor)

    def toggle_aleatorio(self) -> bool:
        """Alterna entre reproducción aleatoria y secuencial de música."""
        self._reproduccion_aleatoria = not self._reproduccion_aleatoria
        return self._reproduccion_aleatoria

    # --- Controles de Volumen y Silencio ---
    def _sync_music_volume(self) -> None:
        self._mixer_call(pygame.mixer.music.set_volume, 0.0 if self._muted else self._volumen_musica)

    def toggle_sfx(self) -> bool:
        """Alterna exclusivamente la activación de los efectos de sonido (SFX)."""
        self._enabled = not self._enabled
        return self._enabled

    def toggle_mute(self) -> bool:
        """Alterna el estado de silencio tanto para efectos como música."""
        self._muted = not self._muted
        if self._muted:
            self._mixer_call(pygame.mixer.music.pause)
        elif not self._musica_pausada and self._musica_activa:
            self._mixer_call(pygame.mixer.music.unpause)
        self._sync_music_volume()
        return self._muted

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            sound.set_volume(self._volume)

    def set_volumen_musica(self, volumen: float) -> None:
        self._volumen_musica = max(0.0, min(1.0, volumen))
        self._sync_music_volume()

# GESTIÓN DE MÚSICA DE FONDO (BGM)


    def _cargar_playlist_musica(self) -> List[Path]:
        """Escanea assets/music en busca de pistas de audio para rotación BGM."""
        exts = (".mp3", ".ogg", ".wav")
        self._playlist_musica = [f for f in sorted(RUTA_MUSICA.iterdir()) if f.suffix.lower() in exts] if RUTA_MUSICA.is_dir() else []
        if not self._playlist_musica and RUTA_SONIDOS.is_dir():
            self._playlist_musica = [f for f in sorted(RUTA_SONIDOS.iterdir()) if f.suffix.lower() in exts and ("fondo" in f.name.lower() or "piano" in f.name.lower())]
        return self._playlist_musica

    def obtener_playlist_musica(self) -> List[str]:
        return [p.name for p in self._playlist_musica]

    def cargar_musica(self, ruta_o_nombre: Optional[Union[str, Path]] = None) -> bool:
        """Carga una pista de música por ruta o nombre, o la actual de la playlist."""
        if not self._available:
            return False
        if not self._playlist_musica:
            self._cargar_playlist_musica()
        if not self._playlist_musica and not ruta_o_nombre:
            return False

        if ruta_o_nombre is None:
            ruta_encontrada = self._playlist_musica[self._indice_cancion_actual % len(self._playlist_musica)]
        else:
            ruta = Path(ruta_o_nombre)
            candidatos = (base / ruta_o_nombre for base in (RUTA_MUSICA, RUTA_SONIDOS, RUTA_ASSETS, RUTA_RAIZ))
            ruta_encontrada = ruta if ruta.is_file() else next((c for c in candidatos if c.is_file()), None)

        if ruta_encontrada and ruta_encontrada.is_file():
            try:
                pygame.mixer.music.load(str(ruta_encontrada))
                self._musica_cargada, self._pista_actual = str(ruta_encontrada), ruta_encontrada.name
                if ruta_encontrada in self._playlist_musica:
                    self._indice_cancion_actual = self._playlist_musica.index(ruta_encontrada)
                self._sync_music_volume()
                return True
            except Exception as err:
                print(f"[AUDIO] No se pudo cargar música '{ruta_encontrada}': {err}")
        return False

    def _obtener_siguiente_indice(self) -> int:
        """Determina el siguiente índice de la lista (aleatorio sin repetir inmediatamente o secuencial)."""
        total = len(self._playlist_musica)
        if total <= 1:
            return 0
        if self._reproduccion_aleatoria:
            opciones = [i for i in range(total) if i != self._indice_cancion_actual]
            return random.choice(opciones)
        return (self._indice_cancion_actual + 1) % total

    def reproducir_musica(
        self,
        pista_o_ruta: Optional[Union[str, Path]] = None,
        loops: int = 0,
        volumen: Optional[float] = None
    ) -> bool:
        """Reproduce la pista actual o la indicada, configurando transición continua o aleatoria."""
        if not self._available:
            return False
        self._musica_activa, self._musica_pausada = True, False
        if volumen is not None:
            self.set_volumen_musica(volumen)

        # Si se arranca desde cero y está en modo aleatorio, seleccionar una pista de inicio al azar
        if pista_o_ruta is None and not self._musica_cargada and self._reproduccion_aleatoria and len(self._playlist_musica) > 1:
            self._indice_cancion_actual = random.randrange(len(self._playlist_musica))

        if (pista_o_ruta or not self._musica_cargada) and not self.cargar_musica(pista_o_ruta):
            return False
        if self._musica_cargada and not self._muted:
            try:
                self._mixer_call(pygame.mixer.music.set_endevent, pygame.USEREVENT + 1)
                self._sync_music_volume()
                pygame.mixer.music.play(loops=-1 if len(self._playlist_musica) <= 1 else loops)
                if len(self._playlist_musica) > 1:
                    next_idx = self._obtener_siguiente_indice()
                    self._mixer_call(pygame.mixer.music.queue, str(self._playlist_musica[next_idx]))
                return True
            except Exception as err:
                print(f"[AUDIO] Error al reproducir música: {err}")
        return False

    def procesar_fin_pista(self) -> bool:
        """Avanza a la siguiente pista de la lista de reproducción continua (aleatoria o secuencial)."""
        if not self._available or not self._musica_activa or not self._playlist_musica:
            return False
        if len(self._playlist_musica) > 1:
            self._indice_cancion_actual = self._obtener_siguiente_indice()
            return self.reproducir_musica(self._playlist_musica[self._indice_cancion_actual])
        return self.reproducir_musica(loops=-1) if len(self._playlist_musica) == 1 else False

    def actualizar(self) -> None:
        """Garantiza la continuidad de la música si la pista terminó."""
        if self._available and self._musica_activa and not self._musica_pausada and not self._muted and self._playlist_musica:
            try:
                if not pygame.mixer.music.get_busy():
                    self.procesar_fin_pista()
            except Exception:
                pass

    def detener_musica(self) -> None:
        """Detiene completamente la reproducción de música."""
        self._mixer_call(pygame.mixer.music.set_endevent)
        self._mixer_call(pygame.mixer.music.stop)
        self._musica_activa = self._musica_pausada = False
        self._musica_cargada = self._pista_actual = None

    def pausar_musica(self) -> None:
        """Pausa la música de fondo."""
        if self._available:
            self._musica_pausada = True
            self._mixer_call(pygame.mixer.music.pause)

    def reanudar_musica(self) -> None:
        """Reanuda la música de fondo."""
        if self._available and not self._muted and self._musica_activa:
            self._musica_pausada = False
            self._mixer_call(pygame.mixer.music.unpause)

# GESTIÓN DE EFECTOS SONOROS (SFX)

    def _load_or_generate_sounds(self) -> None:
        """Carga archivos de audio desde disco o sintetiza proceduralmente."""
        for nombre in (*_TONES, *_ARPEGGIOS):
            sound = self._try_load_from_disk(nombre) or self._synthesize_sound(nombre)
            if sound:
                sound.set_volume(self._volume)
                self._sounds[nombre] = sound

    def _try_load_from_disk(self, effect_name: str) -> Optional[pygame.mixer.Sound]:
        """Intenta cargar un archivo .wav, .ogg o .mp3 desde el directorio dinámico."""
        if not (self._sounds_dir and self._sounds_dir.is_dir()):
            return None

        # Se prueban primero los nombres de archivo reales del proyecto y,
        # como respaldo, el propio nombre lógico del efecto.
        nombres = _ARCHIVOS_SFX.get(effect_name, ()) + (effect_name,)
        for base in nombres:
            for ext in (".wav", ".ogg", ".mp3"):
                cand = self._sounds_dir / f"{base}{ext}"
                if cand.is_file():
                    try:
                        sonido = pygame.mixer.Sound(str(cand))
                        print(f"[SOUND] Efecto '{effect_name}' cargado desde '{cand.name}'.")
                        return sonido
                    except Exception as err:
                        print(f"[SOUND] No se pudo leer '{cand.name}' ({err}). Se sintetizará el tono.")
        return None

    @staticmethod
    def _crear_pcm_buffer(
        sample_rate: int,
        duration: float,
        frequencies: List[tuple[float, float]],
        decay_rate: float = 4.5,
        is_linear: bool = False
    ) -> bytearray:
        """Generador optimizado de búfer PCM de 16 bits estéreo con envolvente."""
        total_samples = max(1, int(sample_rate * duration))
        buf = bytearray()
        for i in range(total_samples):
            t = i / sample_rate
            prog = i / total_samples
            env = max(0.0, 1.0 - prog) if is_linear else math.exp(-decay_rate * prog)
            sample = max(-1.0, min(1.0, sum(a * math.sin(2.0 * math.pi * f * t) for f, a in frequencies) * env))
            pcm = int(sample * 29490)  # 32767 * 0.9
            buf += struct.pack("<hh", pcm, pcm)
        return buf

    def _synthesize_sound(self, effect_name: str) -> Optional[pygame.mixer.Sound]:
        """Sintetiza formas de onda armónicas en memoria usando la configuración declarativa."""
        sample_rate = 44100
        try:
            if effect_name in _TONES:
                dur, freqs, decay = _TONES[effect_name]
                buf = self._crear_pcm_buffer(sample_rate, dur, freqs, decay_rate=4.5, is_linear=(decay == "linear"))
            elif effect_name in _ARPEGGIOS:
                notes, amp = _ARPEGGIOS[effect_name]
                buf = b"".join(self._crear_pcm_buffer(sample_rate, d, [(f, amp)], decay_rate=3.0) for f, d in notes)
            else:
                return None
            return pygame.mixer.Sound(buffer=bytes(buf))
        except Exception as err:
            print(f"[SOUND] Error al sintetizar '{effect_name}': {err}")
            return None

    def reproducir_sonido(self, nombre_sonido: str) -> None:
        """Reproduce un efecto de sonido registrado."""
        if self._available and self._enabled and not self._muted:
            sound = self._sounds.get(nombre_sonido)
            if sound:
                try: sound.play()
                except Exception: pass

    # Alias para compatibilidad interna
    _play = reproducir_sonido

    # Métodos semánticos de reproducción rápida
    def play_click(self) -> None: self.reproducir_sonido("click")
    def play_tile_pick(self) -> None: self.reproducir_sonido("tile_pick")
    def play_tile_place(self) -> None: self.reproducir_sonido("tile_place")
    def play_word_success(self) -> None: self.reproducir_sonido("word_success")
    def play_hint(self) -> None: self.reproducir_sonido("hint")
    def play_recall(self) -> None: self.reproducir_sonido("recall")
    def play_invalid(self) -> None: self.reproducir_sonido("invalid")


__all__ = ["GestorAudio"]

