import ctypes
import time
import os

ruta = os.path.abspath("assets/audio/frecuencia_tdah.mp3")
print(ruta)
res1 = ctypes.windll.winmm.mciSendStringW(f'open "{ruta}" type mpegvideo alias bgmusic', None, 0, None)
res2 = ctypes.windll.winmm.mciSendStringW('play bgmusic', None, 0, None)
print(res1, res2)
time.sleep(3)
