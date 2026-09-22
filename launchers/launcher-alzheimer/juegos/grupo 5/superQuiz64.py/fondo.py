import cv2
import pygame
from pathlib import Path

class FondoVideoOpenCV:
    def __init__(self, ruta_video, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.cap = None
        self.video_cargado = False

        if Path(ruta_video).exists():
            self.cap = cv2.VideoCapture(str(ruta_video))
            if self.cap.isOpened():
                self.video_cargado = True
            else:
                print(f"Error: No se pudo abrir el video en {ruta_video}")
        else:
            print(f"Error: No se encontró el video en: {ruta_video}")

    def obtener_frame_surface(self):
        if not self.video_cargado:
            return None

        ret, frame = self.cap.read()

        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                return None

        frame = cv2.resize(frame, (self.ancho, self.alto), interpolation=cv2.INTER_CUBIC)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = frame_rgb.swapaxes(0, 1)

        return pygame.surfarray.make_surface(frame_rgb)

    def liberar(self):
        if self.cap:
            self.cap.release()