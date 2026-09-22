import os
import pygame

class GestorAudio:
    """
    Gestor de audio desacoplado para alta cohesión.
    Maneja la inicialización del mixer, carga y reproducción en bucle
    de archivos de música compatibles (.wav, .ogg, .mp3) sin saturar main.py.
    """
    def __init__(self, ruta_carpeta_audio=None, volumen=0.25):
        self.volumen = volumen
        if ruta_carpeta_audio is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.carpeta_audio = os.path.join(base_dir, "assets", "audio")
        else:
            self.carpeta_audio = ruta_carpeta_audio

        self._iniciar_mixer()

    def _iniciar_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"[Audio] Error al iniciar pygame.mixer: {e}")

    def reproducir_musica_fondo(self, nombres_candidatos=None):
        if nombres_candidatos is None:
            nombres_candidatos = [
                "frecuencia_tdah.wav",
                "frecuencia_tdah.ogg",
                "frecuencia_tdah.mp3"
            ]

        ruta_encontrada = None
        # 1. Probar nombres preferidos
        for nombre in nombres_candidatos:
            ruta = os.path.join(self.carpeta_audio, nombre)
            if os.path.exists(ruta):
                ruta_encontrada = ruta
                break

        # 2. Si no coincide con el nombre exacto, buscar cualquier .mp3, .wav u .ogg en la carpeta
        if not ruta_encontrada and os.path.exists(self.carpeta_audio):
            for archivo in os.listdir(self.carpeta_audio):
                if archivo.lower().endswith((".mp3", ".wav", ".ogg")):
                    ruta_encontrada = os.path.join(self.carpeta_audio, archivo)
                    break

        if not ruta_encontrada:
            print("[Audio] Aviso: No se encontró archivo de audio compatible en assets/audio/.")
            return False

        try:
            pygame.mixer.music.load(ruta_encontrada)
            pygame.mixer.music.set_volume(self.volumen)
            pygame.mixer.music.play(-1)
            print(f"[Audio] Reproduciendo en bucle: {os.path.basename(ruta_encontrada)}")
            return True
        except pygame.error as e:
            print(f"[Audio] Error de Pygame al cargar '{os.path.basename(ruta_encontrada)}': {e}")
            print("[Audio] Causa típica: archivo mayor a 100MB o con contenedor MP4/M4A no compatible con SDL_mixer.")
            return False

    def pausar(self):
        pygame.mixer.music.pause()

    def reanudar(self):
        pygame.mixer.music.unpause()

    def detener(self):
        pygame.mixer.music.stop()

    def ajustar_volumen(self, volumen):
        self.volumen = max(0.0, min(1.0, volumen))
        pygame.mixer.music.set_volume(self.volumen)
