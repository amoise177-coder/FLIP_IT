"""
MenteActiva — Generador de Sonidos Procedurales
Crea sonidos armónicos sin dependencias externas de archivos de audio.
Usa la biblioteca estándar de Python (math, array) + pygame.mixer.
"""
import math
import array
import pygame


# ─── Frecuencias de notas musicales (octava 4) ──────────────────────────────
NOTE_FREQUENCIES = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46,
    'G5': 783.99, 'A5': 880.00,
}

# Asignar una nota distinta a cada par de cartas (para pistas auditivas)
PAIR_NOTES = ['C4', 'E4', 'G4', 'C5', 'D4', 'F4', 'A4', 'B4']

SAMPLE_RATE = 44100


def _get_mixer_channels():
    """Obtener el número de canales del mixer inicializado."""
    try:
        init_info = pygame.mixer.get_init()
        if init_info:
            return init_info[2]  # (frequency, size, channels)
    except Exception:
        pass
    return 1


def _envelope(i, n_samples, attack_ms=10, release_ms=50):
    """Envolvente suave para evitar clics de audio."""
    attack_samples = int(SAMPLE_RATE * attack_ms / 1000)
    release_samples = int(SAMPLE_RATE * release_ms / 1000)

    if i < attack_samples:
        return i / max(attack_samples, 1)
    elif i > n_samples - release_samples:
        return (n_samples - i) / max(release_samples, 1)
    return 1.0


def generate_tone(frequency, duration=0.3, volume=0.4):
    """
    Genera un tono sinusoidal puro con envolvente suave.
    Retorna un pygame.mixer.Sound.
    """
    channels = _get_mixer_channels()
    n_samples = int(SAMPLE_RATE * duration)
    buf = array.array('h')  # signed 16-bit
    max_val = 32767

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        env = _envelope(i, n_samples)
        sample = int(max_val * volume * env * math.sin(2 * math.pi * frequency * t))
        sample = max(-32768, min(32767, sample))
        buf.append(sample)
        if channels == 2:
            buf.append(sample)  # duplicar para estéreo

    return pygame.mixer.Sound(buffer=buf)


def generate_harmonic_tone(frequency, duration=0.3, volume=0.35):
    """
    Genera un tono con armónicos suaves (más cálido que un seno puro).
    Fundamental + 2.º armónico al 40% + 3.er armónico al 15%.
    """
    channels = _get_mixer_channels()
    n_samples = int(SAMPLE_RATE * duration)
    buf = array.array('h')
    max_val = 32767

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        env = _envelope(i, n_samples, attack_ms=15, release_ms=80)
        # Mezcla de armónicos para un sonido más rico
        wave = (
            math.sin(2 * math.pi * frequency * t) * 1.0 +
            math.sin(2 * math.pi * frequency * 2 * t) * 0.4 +
            math.sin(2 * math.pi * frequency * 3 * t) * 0.15
        )
        sample = int(max_val * volume * env * wave / 1.55)  # normalizar
        sample = max(-32768, min(32767, sample))
        buf.append(sample)
        if channels == 2:
            buf.append(sample)

    return pygame.mixer.Sound(buffer=buf)


def generate_chord(frequencies, duration=0.5, volume=0.3):
    """
    Genera un acorde (múltiples frecuencias simultáneas).
    """
    channels = _get_mixer_channels()
    n_samples = int(SAMPLE_RATE * duration)
    buf = array.array('h')
    max_val = 32767
    n_freq = len(frequencies)

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        env = _envelope(i, n_samples, attack_ms=20, release_ms=120)
        wave = sum(math.sin(2 * math.pi * f * t) for f in frequencies)
        sample = int(max_val * volume * env * wave / max(n_freq, 1))
        sample = max(-32768, min(32767, sample))
        buf.append(sample)
        if channels == 2:
            buf.append(sample)

    return pygame.mixer.Sound(buffer=buf)


def generate_sweep(freq_start, freq_end, duration=0.4, volume=0.3):
    """
    Genera un barrido de frecuencia (ascendente o descendente).
    """
    channels = _get_mixer_channels()
    n_samples = int(SAMPLE_RATE * duration)
    buf = array.array('h')
    max_val = 32767

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        progress = i / max(n_samples - 1, 1)
        freq = freq_start + (freq_end - freq_start) * progress
        env = _envelope(i, n_samples, attack_ms=10, release_ms=100)
        sample = int(max_val * volume * env * math.sin(2 * math.pi * freq * t))
        sample = max(-32768, min(32767, sample))
        buf.append(sample)
        if channels == 2:
            buf.append(sample)

    return pygame.mixer.Sound(buffer=buf)


def generate_click(duration=0.05, volume=0.2):
    """Sonido de clic corto y suave."""
    return generate_tone(800, duration, volume)


# ─── Presets de sonidos del juego ────────────────────────────────────────────

def create_flip_sound():
    """Tono armónico al voltear una carta."""
    return generate_harmonic_tone(523.25, duration=0.15, volume=0.25)


def create_match_sound():
    """Acorde mayor alegre para acierto (Do-Mi-Sol)."""
    return generate_chord([261.63, 329.63, 392.00], duration=0.5, volume=0.3)


def create_fail_sound():
    """Tono descendente suave para fallo (no punitivo)."""
    return generate_sweep(350, 250, duration=0.3, volume=0.15)


def create_hint_sound(pair_id=0):
    """
    Nota musical única por par de cartas (pista auditiva nivel 2).
    Cada par tiene su propia nota para guiar por resonancia.
    """
    note_name = PAIR_NOTES[pair_id % len(PAIR_NOTES)]
    freq = NOTE_FREQUENCIES[note_name]
    return generate_harmonic_tone(freq, duration=0.6, volume=0.2)


def create_victory_sound():
    """Fanfarria de victoria: arpegio ascendente Do-Mi-Sol-Do5."""
    channels = _get_mixer_channels()
    notes = [261.63, 329.63, 392.00, 523.25]
    note_dur = 0.2
    gap = 0.05
    total_duration = len(notes) * (note_dur + gap) + 0.3  # cola extra
    n_samples = int(SAMPLE_RATE * total_duration)
    buf = array.array('h')
    max_val = 32767

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        wave = 0.0
        for idx, freq in enumerate(notes):
            start = idx * (note_dur + gap)
            end = start + note_dur + 0.3  # reverberación
            if start <= t < end:
                local_t = t - start
                local_n = int(SAMPLE_RATE * (end - start))
                local_i = int(local_t * SAMPLE_RATE)
                env = _envelope(local_i, local_n, attack_ms=10, release_ms=150)
                wave += env * math.sin(2 * math.pi * freq * local_t)

        sample = int(max_val * 0.25 * wave)
        sample = max(-32768, min(32767, sample))
        buf.append(sample)
        if channels == 2:
            buf.append(sample)

    return pygame.mixer.Sound(buffer=buf)


def create_button_click():
    """Clic de botón de interfaz."""
    return generate_click(duration=0.04, volume=0.15)
