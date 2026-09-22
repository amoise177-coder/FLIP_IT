"""
Manejo del sonido: musica de fondo y efectos.

La musica del menu y la de la partida son pistas distintas, y el cambio
entre ellas se hace con fundido para que no haya un corte seco (un corte
brusco de audio es justo el tipo de estimulo que rompe la concentracion).
Si un archivo no existe, todo sigue funcionando en silencio.
"""

import pygame

import constantes

_efectos_cache = {}
_pista_actual = None

EFECTOS = ("boton", "carta", "correcto", "incorrecto")


def _ruta_existente(ruta_base):
    """Acepta .ogg o .wav: devuelve la primera que exista."""
    ruta_base = constantes.Path(ruta_base)
    if ruta_base.exists():
        return ruta_base
    for suf in (".ogg", ".wav", ".mp3"):
        alterna = ruta_base.with_suffix(suf)
        if alterna.exists():
            return alterna
    return None


def aplicar_volumen_musica():
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(constantes.volumen_musica_final())


def reproducir_musica(ruta_path, en_bucle=True, fundido=600):
    """Arranca una pista. Si ya esta sonando esa misma, no hace nada (asi
    la musica no se reinicia cada vez que se vuelve a entrar al menu)."""
    global _pista_actual

    if not constantes.SONIDO_ACTIVADO or not pygame.mixer.get_init():
        return
    ruta = _ruta_existente(ruta_path)
    if ruta is None:
        return
    if _pista_actual == str(ruta) and pygame.mixer.music.get_busy():
        return

    try:
        pygame.mixer.music.load(str(ruta))
        pygame.mixer.music.play(-1 if en_bucle else 0, fade_ms=fundido)
        aplicar_volumen_musica()
        _pista_actual = str(ruta)
    except (pygame.error, FileNotFoundError, OSError):
        _pista_actual = None


def detener_musica(fundido=500):
    global _pista_actual
    if pygame.mixer.get_init():
        pygame.mixer.music.fadeout(fundido)
    _pista_actual = None


def volumen_efectos():
    return constantes.volumen_efectos_final()


def play_efecto(nombre):
    if not constantes.SONIDO_ACTIVADO or not pygame.mixer.get_init():
        return
    if nombre not in EFECTOS:
        return
    try:
        if nombre not in _efectos_cache:
            ruta = _ruta_existente(constantes.SFX_DIR / f"{nombre}.ogg")
            if ruta is None:
                _efectos_cache[nombre] = None
            else:
                _efectos_cache[nombre] = pygame.mixer.Sound(str(ruta))
        snd = _efectos_cache[nombre]
        if snd is None:
            return
        snd.set_volume(volumen_efectos())
        snd.play()
    except (pygame.error, FileNotFoundError, OSError):
        _efectos_cache[nombre] = None

def toggle_sonido():
    """Activa/desactiva todo el audio del juego."""
    constantes.SONIDO_ACTIVADO = not constantes.SONIDO_ACTIVADO
    if constantes.SONIDO_ACTIVADO:
        aplicar_volumen_musica()
    else:
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(0)
    return constantes.SONIDO_ACTIVADO
