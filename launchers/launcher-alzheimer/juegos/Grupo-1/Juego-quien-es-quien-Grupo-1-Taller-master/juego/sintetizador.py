"""Generación de sonido en tiempo de ejecución (síntesis simple de
tonos), compartida por los efectos (``audio.py``) y la música
(``musica.py``). Evita depender de archivos de audio externos y de
revisar sus licencias: todo el sonido del juego se calcula
matemáticamente.
"""

import array
import math

FRECUENCIA_MUESTREO = 44100

# Notas de una escala pentatónica mayor (en semitonos respecto a la
# nota base), la escala más sencilla de combinar sin que "suene mal":
# cualquier combinación de estos grados encaja de forma agradable.
ESCALA_PENTATONICA = [0, 2, 4, 7, 9, 12, 14, 16, 19]
NOTA_BASE_HZ = 261.63  # Do central (C4)


def semitono_a_frecuencia(semitonos, base_hz=NOTA_BASE_HZ):
    return base_hz * (2 ** (semitonos / 12))


_CACHE_TABLAS_CALIDAS = {}


def _tabla_onda_calida(frecuencia_hz):
    """Una tabla de onda (un solo período) con el timbre "cálido"
    (fundamental + dos armónicos suaves) para ``frecuencia_hz``, cacheada
    por frecuencia. Generar el período una sola vez y repetirlo (en vez
    de calcular los tres senos muestra por muestra durante toda la nota)
    es varias veces más rápido, algo que importa porque la música de
    fondo genera bastantes segundos de audio con este timbre al iniciar
    el juego. El período se redondea al entero de muestras más cercano,
    lo que desafina la nota en menos de un puñado de centésimas de
    semitono — inaudible para un acompañamiento de fondo."""
    tabla = _CACHE_TABLAS_CALIDAS.get(frecuencia_hz)
    if tabla is not None:
        return tabla
    periodo_muestras = max(2, round(FRECUENCIA_MUESTREO / frecuencia_hz))
    tabla = []
    for i in range(periodo_muestras):
        t = i / FRECUENCIA_MUESTREO
        onda = math.sin(2 * math.pi * frecuencia_hz * t)
        onda += 0.28 * math.sin(2 * math.pi * frecuencia_hz * 2 * t)
        onda += 0.10 * math.sin(2 * math.pi * frecuencia_hz * 3 * t)
        onda /= 1.38  # renormaliza para que el pico siga en torno a 1.0
        tabla.append(onda)
    _CACHE_TABLAS_CALIDAS[frecuencia_hz] = tabla
    return tabla


def generar_tono(frecuencia_hz, duracion_ms, volumen=0.5, timbre="simple"):
    """Genera un tono como bytes PCM de 16 bits mono, con una pequeña
    envolvente de entrada/salida para evitar "clics".

    ``timbre="simple"`` (el de siempre) es una onda senoidal pura, usada
    para los efectos de interfaz (clic, acierto, error), donde interesa
    un pitido corto y nítido. ``timbre="calido"`` añade un segundo y un
    tercer armónico más suaves (una octava y una octava-y-quinta por
    encima, mediante una tabla de onda precalculada) y un trémolo muy
    ligero, para un sonido más redondo y menos "de pitido electrónico"
    — es el que usa la música de fondo.
    """
    n_muestras = int(FRECUENCIA_MUESTREO * duracion_ms / 1000)
    amplitud = int(32767 * max(0.0, min(1.0, volumen)))
    subida_bajada = max(1, int(FRECUENCIA_MUESTREO * 0.012))
    buffer = array.array("h")
    if timbre == "calido":
        tabla = _tabla_onda_calida(frecuencia_hz)
        periodo = len(tabla)
        for i in range(n_muestras):
            envolvente = min(1.0, i / subida_bajada, (n_muestras - i) / subida_bajada)
            tremolo = 1.0 + 0.04 * math.sin(2 * math.pi * 5.5 * i / FRECUENCIA_MUESTREO)
            valor = amplitud * envolvente * tabla[i % periodo] * tremolo
            buffer.append(int(max(-32767, min(32767, valor))))
    else:
        for i in range(n_muestras):
            t = i / FRECUENCIA_MUESTREO
            envolvente = min(1.0, i / subida_bajada, (n_muestras - i) / subida_bajada)
            valor = amplitud * envolvente * math.sin(2 * math.pi * frecuencia_hz * t)
            buffer.append(int(valor))
    return buffer.tobytes()


def _grado_a_frecuencia(grado, base_hz):
    octava, indice = divmod(grado, len(ESCALA_PENTATONICA))
    semitonos = ESCALA_PENTATONICA[indice] + octava * 12
    return semitono_a_frecuencia(semitonos, base_hz)


def generar_melodia(notas, duracion_nota_ms, volumen=0.2, base_hz=NOTA_BASE_HZ, timbre="simple"):
    """Concatena una secuencia de notas en un único buffer PCM, listo
    para envolver en un ``pygame.mixer.Sound`` y reproducirse (una vez o
    en bucle).

    Cada nota es un grado de la escala pentatónica (puede ser negativo o
    mayor a la longitud de la escala para bajar o subir de octava), o
    una tupla ``(grado, factor_duracion)`` para darle a esa nota en
    particular una duración distinta (``factor_duracion`` multiplica a
    ``duracion_nota_ms``) — así una melodía no sabe siempre igual de
    "metrónomo", con alguna nota más larga o más corta.
    """
    buffer = b""
    for nota in notas:
        grado, factor_duracion = nota if isinstance(nota, tuple) else (nota, 1.0)
        frecuencia = _grado_a_frecuencia(grado, base_hz)
        buffer += generar_tono(frecuencia, duracion_nota_ms * factor_duracion, volumen, timbre=timbre)
    return buffer


def generar_secuencia(notas, duracion_base_ms, volumen=0.2, base_hz=NOTA_BASE_HZ, timbre="simple"):
    """Como ``generar_melodia``, pero las notas se dan directamente en
    semitonos respecto a ``base_hz`` en vez de grados de la escala
    pentatónica — útil para un acompañamiento de bajo, donde interesan
    intervalos exactos (tónica, quinta, octava) y no grados de escala.
    Cada nota es ``(semitonos, factor_duracion)``."""
    buffer = b""
    for semitonos, factor_duracion in notas:
        frecuencia = semitono_a_frecuencia(semitonos, base_hz)
        buffer += generar_tono(frecuencia, duracion_base_ms * factor_duracion, volumen, timbre=timbre)
    return buffer


def mezclar_buffers(buffers):
    """Suma varios buffers PCM de 16 bits mono (por ejemplo, una melodía
    y un acompañamiento de bajo) en un único buffer, recortando el
    resultado para no saturar. Si un buffer es más corto que el más
    largo, se repite en bucle hasta cubrirlo (así un patrón de bajo
    corto y repetitivo puede acompañar una melodía más larga)."""
    arreglos = [array.array("h", datos) for datos in buffers if datos]
    if not arreglos:
        return b""
    largo_max = max(len(arreglo) for arreglo in arreglos)
    resultado = array.array("h", [0]) * largo_max
    for arreglo in arreglos:
        n = len(arreglo)
        if n == 0:
            continue
        veces = -(-largo_max // n)  # división hacia arriba
        extendido = (arreglo * veces)[:largo_max] if veces > 1 else arreglo
        for i in range(largo_max):
            suma = resultado[i] + extendido[i]
            resultado[i] = 32767 if suma > 32767 else (-32768 if suma < -32768 else suma)
    return resultado.tobytes()
