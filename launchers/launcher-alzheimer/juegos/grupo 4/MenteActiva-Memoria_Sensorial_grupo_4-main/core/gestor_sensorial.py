"""
MenteActiva — Gestor Sensorial
Administra todos los sonidos y la música de fondo del juego.
Encapsula la creación, almacenamiento y reproducción de estímulos auditivos.
"""
import os
import pygame
from config import MUSIC_DIR, MUSIC_VOLUME, MUSIC_FADE_MS, ASSETS_DIR
from utils.sound_generator import (
    create_flip_sound, create_match_sound, create_fail_sound,
    create_hint_sound, create_victory_sound, create_button_click,
)

# Directorio para efectos de sonido personalizados
SFX_DIR = os.path.join(ASSETS_DIR, "sfx")


class GestorSensorial:
    """
    Gestiona los eventos sonoros y la música de fondo del juego.

    Genera todos los sonidos al inicializarse (proceduralmente)
    y los almacena en caché para reproducción instantánea.
    La música de fondo se carga desde archivos en assets/music/.

    Sonidos personalizados: si existen archivos en assets/sfx/
    con los nombres 'acierto', 'fallo' o 'victoria' (extensiones
    .wav, .ogg, .mp3), se usarán en lugar de los sonidos generados.

    Atributos privados:
        _sonidos (dict): Caché de sonidos generados.
        _habilitado (bool): Control global de audio (efectos).
        _volumen (float): Volumen maestro de efectos (0.0 a 1.0).
        _musica_habilitada (bool): Control de música de fondo.
        _volumen_musica (float): Volumen de la música de fondo.
        _musica_actual (str): Clave de la música sonando ("menu", "juego", o None).
    """

    def __init__(self, habilitado=True, volumen=0.7):
        self._habilitado = habilitado
        self._volumen = volumen
        self._sonidos = {}
        self._hint_sounds = {}
        self._inicializado = False

        # ── Música de fondo ──
        self._musica_habilitada = True
        self._volumen_musica = MUSIC_VOLUME
        self._musica_actual = None
        self._rutas_musica = {}  # {"menu": path, "juego": path}

    def _cargar_sonido_externo(self, nombre):
        """
        Busca un archivo de sonido personalizado en assets/sfx/.
        Retorna pygame.mixer.Sound si lo encuentra, None si no.

        Args:
            nombre: Nombre base del archivo (sin extensión).
        """
        if not os.path.isdir(SFX_DIR):
            return None
        for ext in [".wav", ".ogg", ".mp3"]:
            filepath = os.path.join(SFX_DIR, f"{nombre}{ext}")
            if os.path.isfile(filepath):
                try:
                    sound = pygame.mixer.Sound(filepath)
                    print(f"[GestorSensorial] Sonido externo cargado: {filepath}")
                    return sound
                except Exception as e:
                    print(f"[GestorSensorial] Error al cargar {filepath}: {e}")
        return None

    def inicializar(self):
        """
        Genera todos los sonidos del juego y detecta archivos de música.
        Para 'acierto', 'fallo' y 'victoria', intenta cargar archivos
        externos desde assets/sfx/ antes de usar los sonidos generados.
        Debe llamarse después de pygame.mixer.init().
        """
        try:
            if not pygame.mixer.get_init():
                return

            # Crear directorio sfx si no existe
            os.makedirs(SFX_DIR, exist_ok=True)

            self._sonidos = {
                "volteo": create_flip_sound(),
                "acierto": self._cargar_sonido_externo("acierto") or create_match_sound(),
                "fallo": self._cargar_sonido_externo("fallo") or create_fail_sound(),
                "victoria": self._cargar_sonido_externo("victoria") or create_victory_sound(),
                "clic": create_button_click(),
            }

            # Generar sonidos de pista para cada par posible (0..7)
            for i in range(8):
                self._hint_sounds[i] = create_hint_sound(i)

            # Aplicar volumen maestro
            self._aplicar_volumen()
            self._inicializado = True

            # Detectar archivos de música
            self._detectar_musica()

        except Exception as e:
            print(f"[GestorSensorial] Error al generar sonidos: {e}")
            self._habilitado = False

    def _detectar_musica(self):
        """Busca archivos de música en assets/music/."""
        self._rutas_musica = {}
        if not os.path.isdir(MUSIC_DIR):
            return

        for nombre_clave in ["menu", "juego"]:
            for ext in [".mp3", ".ogg", ".wav"]:
                filepath = os.path.join(MUSIC_DIR, f"{nombre_clave}{ext}")
                if os.path.isfile(filepath):
                    self._rutas_musica[nombre_clave] = filepath
                    break

        if self._rutas_musica:
            print(f"[GestorSensorial] Música detectada: {list(self._rutas_musica.keys())}")

    def _aplicar_volumen(self):
        """Aplica el volumen maestro a todos los sonidos."""
        for sound in self._sonidos.values():
            sound.set_volume(self._volumen)
        for sound in self._hint_sounds.values():
            sound.set_volume(self._volumen * 0.6)  # Pistas más suaves

    # ── Propiedades ──────────────────────────────────────────────────────

    @property
    def habilitado(self):
        return self._habilitado

    @habilitado.setter
    def habilitado(self, value):
        self._habilitado = value
        if not value:
            pygame.mixer.stop()

    @property
    def volumen(self):
        return self._volumen

    @volumen.setter
    def volumen(self, value):
        self._volumen = max(0.0, min(1.0, value))
        if self._inicializado:
            self._aplicar_volumen()

    @property
    def musica_habilitada(self):
        return self._musica_habilitada

    @musica_habilitada.setter
    def musica_habilitada(self, value):
        self._musica_habilitada = value
        if not value:
            self.detener_musica()

    # ── Reproducción de sonidos ──────────────────────────────────────────

    def _reproducir(self, nombre):
        """Reproduce un sonido por nombre si el audio está habilitado."""
        if not self._habilitado or not self._inicializado:
            return
        sound = self._sonidos.get(nombre)
        if sound:
            sound.play()

    def reproducir_volteo(self):
        """Tono armónico al voltear una carta."""
        self._reproducir("volteo")

    def reproducir_acierto(self):
        """Acorde mayor alegre al encontrar una pareja."""
        self._reproducir("acierto")

    def reproducir_fallo(self):
        """Tono descendente suave al fallar (no punitivo)."""
        self._reproducir("fallo")

    def reproducir_victoria(self):
        """Fanfarria al completar todas las parejas."""
        self._reproducir("victoria")

    def reproducir_clic(self):
        """Sonido de clic de interfaz."""
        self._reproducir("clic")

    def reproducir_pista_auditiva(self, pair_id):
        """
        Reproduce la nota musical asignada a un par de cartas (Pista N2).
        Cada par tiene una nota distinta para guiar por resonancia sonora.
        """
        if not self._habilitado or not self._inicializado:
            return
        sound = self._hint_sounds.get(pair_id)
        if sound:
            sound.play()

    # ── Música de fondo ─────────────────────────────────────────────────

    def reproducir_musica_menu(self):
        """Inicia la música de fondo del menú (loop infinito)."""
        self._reproducir_musica("menu")

    def reproducir_musica_juego(self):
        """Inicia la música de fondo del juego (loop infinito)."""
        self._reproducir_musica("juego")

    def _reproducir_musica(self, clave):
        """
        Reproduce música de fondo por clave.
        Si ya está sonando la misma, no hace nada.
        Si hay otra sonando, hace fadeout antes de cambiar.
        """
        if not self._musica_habilitada or not self._inicializado:
            return

        # Si ya está sonando la misma música, no cambiar
        if self._musica_actual == clave:
            return

        filepath = self._rutas_musica.get(clave)
        if not filepath:
            # No hay archivo de música para esta clave, silenciar
            if self._musica_actual is not None:
                try:
                    pygame.mixer.music.fadeout(MUSIC_FADE_MS)
                except Exception:
                    pass
                self._musica_actual = None
            return

        try:
            # Fadeout de la música actual si hay alguna
            if self._musica_actual is not None:
                pygame.mixer.music.fadeout(MUSIC_FADE_MS // 2)

            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self._volumen_musica)
            pygame.mixer.music.play(-1, fade_ms=MUSIC_FADE_MS)  # -1 = loop infinito
            self._musica_actual = clave
        except Exception as e:
            print(f"[GestorSensorial] Error al reproducir música '{clave}': {e}")
            self._musica_actual = None

    def detener_musica(self):
        """Detiene la música de fondo con fadeout."""
        try:
            pygame.mixer.music.fadeout(MUSIC_FADE_MS)
        except Exception:
            pass
        self._musica_actual = None

    def detener_todo(self):
        """Detiene todos los sonidos y la música."""
        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except Exception:
            pass
        self._musica_actual = None
