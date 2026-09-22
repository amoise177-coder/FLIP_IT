"""Generador dinámico de preguntas para una partida.

En vez de leer siempre el mismo cuestionario fijo desde un archivo, cada
partida sortea al azar unos pocos integrantes del "banco" de personajes
(ver ``datos/personajes.json`` y ``Juego.iniciar_partida``) y este módulo
construye, a partir de ESOS integrantes en concreto, un cuestionario
nuevo: la redacción, el orden y la combinación de tipos de pregunta
cambian de una partida a otra, aunque la mecánica siga siendo la misma
(siempre hay una respuesta correcta entre varias opciones).

Este módulo solo produce diccionarios con el mismo formato que antes se
leía de ``datos/preguntas.json`` (las claves ``tipo``, ``enunciado``,
``opciones``, ``respuesta`` y, para las de identificación,
``personaje_imagen``). Esos diccionarios se siguen entregando a
``juego.preguntas.cargar_preguntas``/``crear_pregunta_desde_datos``, así
que la fábrica y la jerarquía de clases ``Pregunta`` no cambian en
absoluto: solo cambia de dónde salen los datos.
"""

import random

from .configuracion import TOTAL_PREGUNTAS_PARTIDA


def _opciones_barajadas(nombres):
    opciones = list(nombres)
    random.shuffle(opciones)
    return opciones


def _preguntas_identificacion(familia, nombres):
    """"¿Cómo se llama esta persona?" — una por integrante."""
    return [
        {
            "tipo": "identificacion",
            "enunciado": "¿Cómo se llama esta persona?",
            "personaje_imagen": personaje.nombre,
            "opciones": _opciones_barajadas(nombres),
            "respuesta": personaje.nombre,
        }
        for personaje in familia
    ]


def _preguntas_caracteristica(familia, nombres):
    """Asocia a cada integrante con su característica, sin depender de la
    gramática exacta de esta (funciona igual sea "Le gusta..." o "Juega
    fútbol...", a diferencia de una plantilla tipo "¿A quién le gusta...?")."""
    return [
        {
            "tipo": "caracteristica",
            "enunciado": f"¿A quién corresponde esta característica: “{personaje.caracteristica}”?",
            "opciones": _opciones_barajadas(nombres),
            "respuesta": personaje.nombre,
        }
        for personaje in familia
    ]


def _preguntas_visuales(familia, nombres):
    """Igual que las de característica, pero mostrando las imágenes como
    opciones en vez de nombres en texto (reconocimiento visual)."""
    return [
        {
            "tipo": "visual",
            "enunciado": f"Selecciona la imagen de quien tiene esta característica: “{personaje.caracteristica}”.",
            "opciones": _opciones_barajadas(nombres),
            "respuesta": personaje.nombre,
        }
        for personaje in familia
    ]


def _texto_hijo(genero):
    return "hijo" if genero == "M" else "hija"


def _texto_abuelo(genero):
    return "abuelo" if genero == "M" else "abuela"


def _texto_nieto(genero):
    return "nieto" if genero == "M" else "nieta"


def _preguntas_relacion(familia, nombres):
    """Preguntas de relación familiar (padre/madre-hijo/a y también
    abuelo/a-nieto/a), generadas SOLO entre integrantes que estén ambos
    presentes en la familia sorteada para esta partida — con un banco
    de 8 personajes no siempre hay una relación directa entre los pocos
    que le tocan a una partida, así que esta función puede devolver
    pocas o ninguna, y quien la llama debe estar preparado para eso."""
    por_nombre = {p.nombre: p for p in familia}
    preguntas = []
    for hijo in familia:
        padre = por_nombre.get(hijo.padre)
        if padre is None:
            continue
        preguntas.append({
            "tipo": "relacion",
            "enunciado": f"¿Quién es el/la {_texto_hijo(hijo.genero)} de {padre.nombre}?",
            "opciones": _opciones_barajadas(nombres),
            "respuesta": hijo.nombre,
        })
        preguntas.append({
            "tipo": "relacion",
            "enunciado": f"¿De quién es {_texto_hijo(hijo.genero)} {hijo.nombre}?",
            "opciones": _opciones_barajadas(nombres),
            "respuesta": padre.nombre,
        })

        abuelo = por_nombre.get(padre.padre)
        if abuelo is not None:
            preguntas.append({
                "tipo": "relacion",
                "enunciado": f"¿Quién es el/la {_texto_nieto(hijo.genero)} de {abuelo.nombre}?",
                "opciones": _opciones_barajadas(nombres),
                "respuesta": hijo.nombre,
            })
            preguntas.append({
                "tipo": "relacion",
                "enunciado": f"¿Quién es {'el' if abuelo.genero == 'M' else 'la'} {_texto_abuelo(abuelo.genero)} de {hijo.nombre}?",
                "opciones": _opciones_barajadas(nombres),
                "respuesta": abuelo.nombre,
            })
    return preguntas


def generar_datos_preguntas(familia, total=TOTAL_PREGUNTAS_PARTIDA):
    """Genera el cuestionario de una partida a partir de ``familia``
    (lista de ``Personaje`` sorteados para esta ronda).

    Siempre incluye una pregunta de identificación y una de
    característica por cada integrante, y al menos una de reconocimiento
    visual (es el tipo de pregunta que más importa para este juego). El
    resto se completa con preguntas de relación familiar (cuando la
    familia sorteada tiene alguna) y más reconocimiento visual, hasta
    llegar a ``total`` preguntas sin repetir el mismo enunciado exacto.
    El orden final también se baraja, para que ni la combinación de
    preguntas ni su secuencia se repitan entre partidas.
    """
    nombres = [personaje.nombre for personaje in familia]

    preguntas = _preguntas_identificacion(familia, nombres) + _preguntas_caracteristica(familia, nombres)
    vistos = {(p["tipo"], p["enunciado"]) for p in preguntas}

    visuales = _preguntas_visuales(familia, nombres)
    random.shuffle(visuales)
    relaciones = _preguntas_relacion(familia, nombres)
    random.shuffle(relaciones)

    faltan = total - len(preguntas)
    extra = []
    if faltan > 0 and visuales:
        primera_visual = visuales.pop(0)
        extra.append(primera_visual)
        vistos.add((primera_visual["tipo"], primera_visual["enunciado"]))

    resto_candidatas = relaciones + visuales
    random.shuffle(resto_candidatas)
    for candidata in resto_candidatas:
        if len(extra) >= faltan:
            break
        clave = (candidata["tipo"], candidata["enunciado"])
        if clave in vistos:
            continue
        vistos.add(clave)
        extra.append(candidata)

    preguntas += extra
    random.shuffle(preguntas)
    return preguntas[:total]


__all__ = ["generar_datos_preguntas"]
