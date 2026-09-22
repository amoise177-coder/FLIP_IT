from playsound import playsound
import threading
import os

ruta = os.path.abspath("assets/audio/frecuencia_tdah.mp3")
print("Ruta:", ruta)
def reproducir():
    playsound(ruta)

t = threading.Thread(target=reproducir)
t.start()
import time
time.sleep(3)
print("Sigue vivo")
