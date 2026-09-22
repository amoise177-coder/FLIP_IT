import sys
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

ruta = sys.argv[1]
try:
    audio = MP3(ruta)
    if audio.tags:
        audio.tags.delete()
        audio.save()
        print("Tags eliminados con éxito.")
    else:
        print("No había tags.")
except Exception as e:
    print("Error:", e)
