import wave
import math
import struct
import os

sample_rate = 44100
duration = 4.0 # 4 seconds loop
frequency = 432.0 # 432Hz healing tone

filepath = os.path.join(os.path.dirname(__file__), 'assets', 'audio', 'frecuencia_tdah.wav')

with wave.open(filepath, 'w') as wav_file:
    wav_file.setnchannels(1) # mono
    wav_file.setsampwidth(2) # 16-bit
    wav_file.setframerate(sample_rate)
    
    for i in range(int(sample_rate * duration)):
        # Generate sine wave
        value = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        # Add a slow pulsation (binaural beat effect / amplitude modulation)
        envelope = 0.5 + 0.5 * math.sin(2.0 * math.pi * 4.0 * i / sample_rate) # 4Hz pulse (Theta wave)
        value = int(value * envelope)
        
        data = struct.pack('<h', value)
        wav_file.writeframesraw(data)

print(f"Archivo generado en: {filepath}")
