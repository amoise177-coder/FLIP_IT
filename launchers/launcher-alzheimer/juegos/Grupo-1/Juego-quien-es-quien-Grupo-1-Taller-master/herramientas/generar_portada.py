"""Script de una sola vez para generar la portada estática que el
launcher "enfocate" carga desde assets/cover/launcher_cover.png.

No es necesario ejecutarlo para jugar: la imagen resultante ya queda
guardada en el repositorio. Se deja aquí por si el equipo necesita
regenerarla (por ejemplo, tras cambiar los colores de los personajes).
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

RUTA_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RUTA_PROYECTO)

import pygame  # noqa: E402

from juego.configuracion import RUTA_PERSONAJES_JSON, RUTA_BASE, COLOR_TITULO, COLOR_TEXTO_SUAVE  # noqa: E402
from juego.personaje import Personaje  # noqa: E402
from pantallas.avatar import dibujar_avatar  # noqa: E402
from pantallas.utilidades import dibujar_fondo, dibujar_texto_con_sombra  # noqa: E402
import json  # noqa: E402


def generar():
    pygame.init()
    ancho, alto = 640, 360
    superficie = pygame.display.set_mode((ancho, alto))

    # Mismo fondo degradado con destellos que usa el juego, para que la
    # portada del launcher coincida con el aspecto "profesional" del resto
    # de las pantallas en vez de un simple color plano.
    dibujar_fondo(superficie)

    with open(RUTA_PERSONAJES_JSON, "r", encoding="utf-8") as archivo:
        banco = Personaje.cargar_familia(json.load(archivo))

    # El banco de personajes tiene varios integrantes (cada partida sortea
    # solo algunos, ver Juego.iniciar_partida); para la portada se muestra
    # una muestra fija de 4, con variedad de generación y género.
    nombres_portada = ["Pedro", "Ana", "Carlos", "Sofía"]
    familia = {nombre: banco[nombre] for nombre in nombres_portada if nombre in banco}

    fuente_titulo = pygame.font.Font(None, 58)
    dibujar_texto_con_sombra(superficie, "¿Quién es quién?", fuente_titulo, COLOR_TITULO, (ancho // 2, 70))

    fuente_subtitulo = pygame.font.Font(None, 26)
    subtitulo = fuente_subtitulo.render("Juego de memoria familiar", True, COLOR_TEXTO_SUAVE)
    rect_subtitulo = subtitulo.get_rect(center=(ancho // 2, 112))
    superficie.blit(subtitulo, rect_subtitulo)

    personajes = list(familia.values())
    cantidad = len(personajes)
    separacion = ancho // (cantidad + 1)
    for indice, personaje in enumerate(personajes, start=1):
        centro = (separacion * indice, 230)
        dibujar_avatar(superficie, personaje, centro, 66)

    ruta_salida = os.path.join(RUTA_BASE, "assets", "cover", "launcher_cover.png")
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    pygame.image.save(superficie, ruta_salida)
    print(f"Portada generada en: {ruta_salida}")


if __name__ == "__main__":
    generar()
