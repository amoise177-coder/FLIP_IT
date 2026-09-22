import math
import struct
import io
import wave
import pygame

class SoundManager:
    """Generates procedural sound effects so the game has rich audio with zero missing asset errors."""
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._init_sounds()
        except Exception as e:
            print(f"Warning: Audio mixer could not be initialized: {e}")
            self.enabled = False

    def _generate_wav(self, duration_s, sample_rate, sample_func):
        """Generates a WAV byte stream from a sample generator function."""
        num_samples = int(duration_s * sample_rate)
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                val = sample_func(t, duration_s)
                # Clamp between -1.0 and 1.0
                val = max(-1.0, min(1.0, val))
                sample_int = int(val * 32767)
                frames.extend(struct.pack('<h', sample_int))
            wav.writeframes(frames)
        buffer.seek(0)
        return buffer

    def _init_sounds(self):
        sr = 44100

        # 1. Pop / Lift sound (short upward chirp)
        def pop_gen(t, dur):
            progress = t / dur
            freq = 400 + progress * 600
            env = math.exp(-t * 28)
            return math.sin(2 * math.pi * freq * t) * env * 0.45
        
        # 2. Drop / Clink sound (pleasant bubble / marble thud)
        def drop_gen(t, dur):
            env = math.exp(-t * 22)
            # Two harmonic frequencies to sound like glass / marble
            s1 = math.sin(2 * math.pi * 520 * t) * 0.4
            s2 = math.sin(2 * math.pi * 840 * t) * 0.25
            return (s1 + s2) * env

        # 3. Invalid Move / Thud sound (soft low buzz)
        def invalid_gen(t, dur):
            env = math.exp(-t * 15)
            freq = 140 - t * 40
            return (math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * (freq * 0.5) * t)) * env * 0.4

        # 4. Tube Complete sound (sparkle chime arpeggio)
        def complete_gen(t, dur):
            # Arpeggio: C5 (523), E5 (659), G5 (784), C6 (1046)
            notes = [(0.0, 523.25), (0.07, 659.25), (0.14, 783.99), (0.21, 1046.50)]
            total = 0.0
            for start, f in notes:
                if t >= start:
                    dt = t - start
                    env = math.exp(-dt * 8)
                    total += math.sin(2 * math.pi * f * dt) * env * 0.25
            return total

        # 5. Victory Fanfare (joyful chords)
        def victory_gen(t, dur):
            # C maj arpeggio + fanfare
            chords = [
                (0.00, 523.25),
                (0.12, 659.25),
                (0.24, 783.99),
                (0.36, 1046.50),
                (0.50, 1318.51),
                (0.65, 1046.50),
                (0.80, 1318.51),
                (0.95, 1567.98),
            ]
            total = 0.0
            for start, f in chords:
                if t >= start:
                    dt = t - start
                    env = math.exp(-dt * 4.5)
                    total += (math.sin(2 * math.pi * f * dt) + 0.2 * math.sin(4 * math.pi * f * dt)) * env * 0.18
            return total

        # 6. Button Click
        def click_gen(t, dur):
            env = math.exp(-t * 35)
            return math.sin(2 * math.pi * 900 * t) * env * 0.35

        try:
            self.sounds['pop'] = pygame.mixer.Sound(self._generate_wav(0.12, sr, pop_gen))
            self.sounds['drop'] = pygame.mixer.Sound(self._generate_wav(0.15, sr, drop_gen))
            self.sounds['invalid'] = pygame.mixer.Sound(self._generate_wav(0.18, sr, invalid_gen))
            self.sounds['complete'] = pygame.mixer.Sound(self._generate_wav(0.55, sr, complete_gen))
            self.sounds['victory'] = pygame.mixer.Sound(self._generate_wav(1.50, sr, victory_gen))
            self.sounds['click'] = pygame.mixer.Sound(self._generate_wav(0.08, sr, click_gen))
        except Exception as e:
            print(f"Warning: Could not compile procedural sounds: {e}")

    def play(self, sound_name):
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass
