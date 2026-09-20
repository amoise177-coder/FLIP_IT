"""
Genera la musica de fondo y los efectos de sonido de FLIP IT.

Todo el audio es sintetizado aqui con numpy (ondas propias), asi que no
depende de ningun archivo con derechos de autor: se puede volver a correr
en cualquier maquina con "python generar_audio.py".

Criterio de diseno (ninos con TDAH):
  - tempo lento y estable, sin cambios bruscos de volumen
  - timbre tipo caja de musica / celesta, sin percusion fuerte ni golpes secos
  - loops perfectos (la cola de reverb se envuelve al inicio) para que no
    haya un "corte" audible cada vez que la pista se repite
  - el sonido de error es suave y descendente, nunca un buzz agresivo

Salida (Assets/Sonido):
  sonido_fondo.ogg          musica del menu
  sonido_juego.ogg          musica de la partida
  sonido_instrucciones.ogg  musica de la pantalla de instrucciones
  sfx/boton.ogg  sfx/carta.ogg  sfx/correcto.ogg  sfx/incorrecto.ogg
"""

import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 44100
BASE_DIR = Path(__file__).resolve().parent
SND_DIR = BASE_DIR / "Assets" / "Sonido"
SFX_DIR = SND_DIR / "sfx"


# ---------------------------------------------------------------------
# utilidades basicas
# ---------------------------------------------------------------------

def nota(nombre):
    """Convierte 'C4', 'F#3', 'Bb5' en su frecuencia en Hz."""
    escala = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    semis = escala[nombre[0].upper()]
    i = 1
    while i < len(nombre) and nombre[i] in "#b":
        semis += 1 if nombre[i] == "#" else -1
        i += 1
    octava = int(nombre[i:])
    midi = 12 * (octava + 1) + semis
    return 440.0 * 2 ** ((midi - 69) / 12)


def env_adsr(n, ataque, decaimiento, sostener, liberacion):
    """Envolvente clasica en muestras, devuelta como array de largo n."""
    a = max(1, int(ataque * SR))
    d = max(1, int(decaimiento * SR))
    r = max(1, int(liberacion * SR))
    s = max(0, n - a - d - r)
    partes = [
        np.linspace(0, 1, a, endpoint=False),
        np.linspace(1, sostener, d, endpoint=False),
        np.full(s, sostener),
        np.linspace(sostener, 0, r),
    ]
    env = np.concatenate(partes)
    return env[:n] if len(env) >= n else np.pad(env, (0, n - len(env)))


def campana(freq, dur, amp=1.0, brillo=1.0):
    """Voz tipo celesta / caja de musica: parciales inarmonicos que se
    apagan mas rapido mientras mas agudos son."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    parciales = [(1.0, 1.00), (2.0, 0.42), (3.01, 0.20), (4.17, 0.11), (5.43, 0.06)]
    onda = np.zeros(n)
    for mult, peso in parciales:
        decaimiento = np.exp(-t * (2.4 + 2.1 * mult) / max(0.35, brillo))
        onda += peso * decaimiento * np.sin(2 * np.pi * freq * mult * t)
    ataque = np.minimum(1.0, t / 0.006)          # ataque suave, sin "clic"
    return amp * onda * ataque / 1.8


def marimba(freq, dur, amp=1.0):
    """Pulso de madera, mas redondo y corto que la campana."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    onda = (np.sin(2 * np.pi * freq * t) * np.exp(-t * 7.0)
            + 0.30 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-t * 16.0)
            + 0.12 * np.sin(2 * np.pi * freq * 9.2 * t) * np.exp(-t * 26.0))
    return amp * onda * np.minimum(1.0, t / 0.004)


def pad(freq, dur, amp=1.0):
    """Colchon armonico: tres osciladores desafinados con ataque lento."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    onda = np.zeros(n)
    for desafine, peso in ((0.997, 0.5), (1.0, 0.6), (1.004, 0.5)):
        f = freq * desafine
        onda += peso * (np.sin(2 * np.pi * f * t)
                        + 0.28 * np.sin(2 * np.pi * f * 2 * t)
                        + 0.10 * np.sin(2 * np.pi * f * 3 * t))
    vibrato = 1 + 0.015 * np.sin(2 * np.pi * 0.22 * t)   # respiracion muy lenta
    return amp * onda * env_adsr(n, 1.2, 0.8, 0.75, 1.4) * vibrato / 3.2


def mezclar(destino, sonido, inicio_seg):
    """Suma un sonido sobre la pista en el segundo indicado."""
    i = int(inicio_seg * SR)
    fin = min(len(destino), i + len(sonido))
    if i < len(destino):
        destino[i:fin] += sonido[:fin - i]


def reverb(senal, largo=1.5, mezcla=0.30, semilla=11):
    """Reverb por convolucion con ruido que decae (sala amplia y suave)."""
    n_ir = int(largo * SR)
    rnd = np.random.default_rng(semilla)
    ir = rnd.normal(0, 1, n_ir) * np.exp(-np.arange(n_ir) / (0.34 * SR))
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))  # sin pre-eco
    ir /= np.abs(ir).sum()
    n_total = len(senal) + n_ir
    largo_fft = 1 << int(np.ceil(np.log2(n_total)))
    humedo = np.fft.irfft(np.fft.rfft(senal, largo_fft) * np.fft.rfft(ir, largo_fft))
    seco = np.pad(senal, (0, n_total - len(senal)))
    return seco + mezcla * humedo[:n_total] * 8.0, n_ir


def cerrar_loop(senal, n_cola, n_util):
    """Envuelve la cola de reverb sobre el inicio para que el loop sea
    perfecto: al repetirse la pista no se escucha ningun corte."""
    salida = senal[:n_util].copy()
    cola = senal[n_util:n_util + n_cola]
    salida[: len(cola)] += cola
    return salida


def normalizar(x, pico=0.72):
    m = np.max(np.abs(x))
    return x * (pico / m) if m > 0 else x


def guardar(nombre, senal, carpeta=None, calidad="4"):
    """Escribe un WAV estereo y lo convierte a OGG (pygame lee ogg nativo)."""
    carpeta = carpeta or SND_DIR
    carpeta.mkdir(parents=True, exist_ok=True)
    # leve apertura estereo: el canal derecho llega unas muestras despues
    retardo = int(0.012 * SR)
    izq = senal
    der = np.concatenate([np.zeros(retardo), senal[:-retardo]]) * 0.96
    estereo = np.stack([izq, der], axis=1)
    datos = np.clip(estereo, -1, 1)
    pcm = (datos * 32767).astype("<i2")

    wav = carpeta / (nombre + ".wav")
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())

    ogg = carpeta / (nombre + ".ogg")
    if shutil.which("ffmpeg"):
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
             "-c:a", "libvorbis", "-q:a", calidad, str(ogg)],
            check=True,
        )
        wav.unlink()
        print("  ->", ogg.relative_to(BASE_DIR))
    else:
        print("  -> (sin ffmpeg, queda en wav)", wav.relative_to(BASE_DIR))


# ---------------------------------------------------------------------
# musica del menu: lenta, tipo caja de musica
# ---------------------------------------------------------------------

def musica_menu():
    bpm = 66
    negra = 60 / bpm
    compas = 4 * negra
    acordes = [
        (["C3", "G3"], ["C5", "E5", "G5", "D6"]),      # Cmaj9
        (["A2", "E3"], ["A4", "C5", "E5", "G5"]),      # Am7
        (["F2", "C3"], ["F4", "A4", "C5", "E5"]),      # Fmaj7
        (["G2", "D3"], ["G4", "B4", "D5", "E5"]),      # G6
    ]
    n_compases = 16
    dur = n_compases * compas
    pista = np.zeros(int((dur + 3) * SR))

    melodia = [0, 2, 3, 2, 4, 3, 2, 1]   # indices dentro del acorde
    for c in range(n_compases):
        t0 = c * compas
        bajo, arriba = acordes[c % len(acordes)]

        for f in bajo:
            mezclar(pista, pad(nota(f), compas + 1.2, 0.30), t0)
        for f in arriba:
            mezclar(pista, pad(nota(f), compas + 1.0, 0.10), t0)

        # arpegio de caja de musica: corcheas suaves
        for i, grado in enumerate([0, 1, 2, 3, 2, 1]):
            f = nota(arriba[grado % len(arriba)])
            amp = 0.30 if i % 3 == 0 else 0.19
            mezclar(pista, campana(f, 1.6, amp), t0 + i * negra * 0.66)

        # melodia sencilla arriba, solo en la mitad de los compases
        if c % 2 == 0:
            grado = melodia[(c // 2) % len(melodia)]
            f = nota(arriba[grado % len(arriba)]) * 2
            mezclar(pista, campana(f, 2.4, 0.26, brillo=1.3), t0 + negra)
        if c % 4 == 3:
            f = nota(arriba[-1]) * 2
            mezclar(pista, campana(f, 2.0, 0.18, brillo=1.2), t0 + 2 * negra)

    humedo, n_cola = reverb(pista, largo=1.8, mezcla=0.34)
    salida = cerrar_loop(humedo, n_cola, int(dur * SR))
    return normalizar(salida, 0.70)


# ---------------------------------------------------------------------
# musica de la partida: la misma paleta, con un poco mas de movimiento
# ---------------------------------------------------------------------

def musica_juego():
    bpm = 82
    negra = 60 / bpm
    compas = 4 * negra
    acordes = [
        (["F2", "C3"], ["F4", "A4", "C5", "E5"]),      # Fmaj7
        (["G2", "D3"], ["G4", "B4", "D5", "E5"]),      # G6
        (["E2", "B2"], ["E4", "G4", "B4", "D5"]),      # Em7
        (["A2", "E3"], ["A4", "C5", "E5", "G5"]),      # Am7
    ]
    n_compases = 16
    dur = n_compases * compas
    pista = np.zeros(int((dur + 3) * SR))

    for c in range(n_compases):
        t0 = c * compas
        bajo, arriba = acordes[c % len(acordes)]

        for f in bajo:
            mezclar(pista, pad(nota(f), compas + 1.0, 0.26), t0)
        for f in arriba[:3]:
            mezclar(pista, pad(nota(f), compas + 0.8, 0.08), t0)

        # ostinato de marimba: pulso constante que ayuda a mantener el ritmo
        patron = [0, 2, 1, 3, 2, 0, 1, 2]
        for i, grado in enumerate(patron):
            f = nota(arriba[grado % len(arriba)]) / 2
            amp = 0.26 if i % 4 == 0 else 0.15
            mezclar(pista, marimba(f, 0.9, amp), t0 + i * negra * 0.5)

        # campanitas cada dos compases, para que no sature
        if c % 2 == 1:
            for i, grado in enumerate([3, 2, 0]):
                f = nota(arriba[grado % len(arriba)]) * 2
                mezclar(pista, campana(f, 1.8, 0.20 - i * 0.04), t0 + i * negra)

    humedo, n_cola = reverb(pista, largo=1.5, mezcla=0.28)
    salida = cerrar_loop(humedo, n_cola, int(dur * SR))
    return normalizar(salida, 0.68)


# ---------------------------------------------------------------------
# musica de instrucciones: casi solo colchon, para leer sin distraerse
# ---------------------------------------------------------------------

def musica_instrucciones():
    bpm = 58
    compas = 4 * 60 / bpm
    acordes = [["C3", "G3", "E4", "B4"], ["A2", "E3", "C4", "G4"],
               ["F2", "C3", "A3", "E4"], ["G2", "D3", "B3", "F#4"]]
    n_compases = 8
    dur = n_compases * compas
    pista = np.zeros(int((dur + 3) * SR))
    for c in range(n_compases):
        t0 = c * compas
        for j, f in enumerate(acordes[c % len(acordes)]):
            mezclar(pista, pad(nota(f), compas + 1.4, 0.30 if j < 2 else 0.14), t0)
        if c % 2 == 0:
            mezclar(pista, campana(nota(acordes[c % 4][-1]) * 2, 2.6, 0.14), t0 + compas / 2)
    humedo, n_cola = reverb(pista, largo=2.0, mezcla=0.36)
    salida = cerrar_loop(humedo, n_cola, int(dur * SR))
    return normalizar(salida, 0.60)


# ---------------------------------------------------------------------
# efectos
# ---------------------------------------------------------------------

def sfx_boton():
    dur = 0.22
    t = np.arange(int(dur * SR)) / SR
    f = np.linspace(620, 880, len(t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
    s += 0.25 * np.sin(2 * np.pi * np.cumsum(f * 2) / SR) * np.exp(-t * 24)
    s *= np.minimum(1.0, t / 0.004)
    return normalizar(s, 0.55)


def sfx_carta():
    """Volteo: madera corta + un pequeño brillo ascendente."""
    s = marimba(nota("A4"), 0.30, 0.9)
    brillo = campana(nota("E6"), 0.45, 0.30, brillo=1.4)
    n = max(len(s), len(brillo))
    out = np.zeros(n)
    out[: len(s)] += s
    out[: len(brillo)] += brillo
    return normalizar(out, 0.55)


def sfx_correcto():
    """Arpegio ascendente alegre pero corto (refuerzo positivo claro)."""
    out = np.zeros(int(0.9 * SR))
    for i, nom in enumerate(["C5", "E5", "G5", "C6"]):
        mezclar(out, campana(nota(nom), 0.85, 0.55 - i * 0.05, brillo=1.2), i * 0.075)
    humedo, _ = reverb(out, largo=0.6, mezcla=0.25)
    return normalizar(humedo[: len(out)], 0.62)


def sfx_incorrecto():
    """Dos notas descendentes suaves: avisa sin regañar."""
    out = np.zeros(int(0.7 * SR))
    mezclar(out, marimba(nota("E4"), 0.5, 0.7), 0.0)
    mezclar(out, marimba(nota("C4"), 0.6, 0.6), 0.13)
    humedo, _ = reverb(out, largo=0.5, mezcla=0.20)
    return normalizar(humedo[: len(out)], 0.45)


def main():
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    print("Generando musica...")
    guardar("sonido_fondo", musica_menu())
    guardar("sonido_juego", musica_juego())
    guardar("sonido_instrucciones", musica_instrucciones())
    print("Generando efectos...")
    guardar("boton", sfx_boton(), SFX_DIR, calidad="5")
    guardar("carta", sfx_carta(), SFX_DIR, calidad="5")
    guardar("correcto", sfx_correcto(), SFX_DIR, calidad="5")
    guardar("incorrecto", sfx_incorrecto(), SFX_DIR, calidad="5")
    print("Listo.")


if __name__ == "__main__":
    main()
