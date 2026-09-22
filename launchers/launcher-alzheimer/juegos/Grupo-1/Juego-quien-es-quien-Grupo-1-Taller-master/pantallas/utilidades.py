"""Funciones auxiliares de dibujo compartidas por varias pantallas:
texto, paneles con sombra, el fondo degradado con destellos animados y
un resplandor suave reutilizable (paneles, botones, avatares)."""

import math

import pygame

from juego.configuracion import (
    COLOR_FONDO_DEGRADADO_ABAJO,
    COLOR_FONDO_DEGRADADO_ARRIBA,
    COLOR_SOMBRA,
)


def dibujar_texto_centrado(superficie, texto, fuente, color, centro):
    """Dibuja una línea de texto centrada en el punto indicado."""
    superficie_texto = fuente.render(texto, True, color)
    rect = superficie_texto.get_rect(center=centro)
    superficie.blit(superficie_texto, rect)
    return rect


def dibujar_texto_con_sombra(superficie, texto, fuente, color, centro, color_sombra=None, desplazamiento=(2, 3)):
    """Como dibujar_texto_centrado, pero con una sombra suave detrás para
    que el texto destaque sobre el fondo degradado (look "profesional")."""
    color_sombra = color_sombra or (*COLOR_SOMBRA, 90)
    capa_sombra = fuente.render(texto, True, color_sombra[:3])
    capa_sombra.set_alpha(color_sombra[3] if len(color_sombra) > 3 else 90)
    rect_sombra = capa_sombra.get_rect(center=(centro[0] + desplazamiento[0], centro[1] + desplazamiento[1]))
    superficie.blit(capa_sombra, rect_sombra)
    return dibujar_texto_centrado(superficie, texto, fuente, color, centro)


def ajustar_texto_a_lineas(texto, fuente, ancho_maximo):
    """Divide un texto en líneas que no excedan el ancho máximo (en
    píxeles) al renderizarse con la fuente indicada."""
    palabras = texto.split(" ")
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        candidata = f"{linea_actual} {palabra}".strip()
        if fuente.size(candidata)[0] <= ancho_maximo or not linea_actual:
            linea_actual = candidata
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)
    return lineas


def dibujar_texto_multilinea_centrado(superficie, texto, fuente, color, centro_x, y_superior, ancho_maximo, interlineado=8):
    """Dibuja texto envuelto en varias líneas, centradas horizontalmente,
    comenzando en y_superior. Devuelve la coordenada Y siguiente a la
    última línea dibujada."""
    lineas = ajustar_texto_a_lineas(texto, fuente, ancho_maximo)
    y = y_superior
    for linea in lineas:
        dibujar_texto_centrado(superficie, linea, fuente, color, (centro_x, y))
        y += fuente.get_height() + interlineado
    return y


def dibujar_resplandor(superficie, centro, radio, color, alpha_max=90, anillos=14):
    """Dibuja un resplandor suave (círculos concéntricos con intensidad
    creciente hacia el centro) centrado en ``centro``, simulando un
    brillo difuso sin depender de un motor de blur real. Se usa tanto en
    el fondo animado como en el brillo de los botones al pasar el mouse.

    Importante: los modos de mezcla ADD de Pygame suman el color tal
    cual, SIN escalarlo por el canal alfa del origen (a diferencia de un
    blit normal). Por eso aquí la intensidad de cada anillo se hornea
    directamente en el color (RGB ya multiplicado por la fracción
    deseada) sobre una capa de fondo negro — sumar negro no cambia nada,
    así que el resto de la pantalla queda intacto — en vez de confiar en
    un valor de alfa que ese modo de mezcla ignoraría."""
    if radio <= 0 or alpha_max <= 0:
        return
    capa = pygame.Surface((radio * 2, radio * 2))
    capa.fill((0, 0, 0))
    for i in range(anillos, 0, -1):
        proporcion = i / anillos
        radio_anillo = int(radio * proporcion)
        intensidad = (alpha_max * (1 - proporcion) ** 1.6) / 255.0
        color_anillo = tuple(min(255, int(c * intensidad)) for c in color)
        pygame.draw.circle(capa, color_anillo, (radio, radio), radio_anillo)
    superficie.blit(capa, (centro[0] - radio, centro[1] - radio), special_flags=pygame.BLEND_RGB_ADD)


def dibujar_sombra_panel(superficie, rect, radio_borde=18, desplazamiento=(0, 8), difuminado=10, alpha=70):
    """Dibuja, detrás de un panel/botón, una sombra suave con el borde
    difuminado (varias capas translúcidas ligeramente más grandes)."""
    ancho_total = rect.width + difuminado * 2
    alto_total = rect.height + difuminado * 2
    capa = pygame.Surface((ancho_total, alto_total), pygame.SRCALPHA)
    for paso in range(difuminado, 0, -2):
        alpha_paso = max(1, int(alpha * (paso / difuminado) * 0.5))
        rect_paso = pygame.Rect(0, 0, rect.width + paso * 2, rect.height + paso * 2)
        rect_paso.center = (ancho_total // 2, alto_total // 2)
        pygame.draw.rect(
            capa, (*COLOR_SOMBRA, alpha_paso), rect_paso,
            border_radius=radio_borde + paso // 2,
        )
    destino = capa.get_rect(center=(rect.centerx + desplazamiento[0], rect.centery + desplazamiento[1]))
    superficie.blit(capa, destino)


def dibujar_panel(superficie, rect, color_fondo, color_borde, radio_borde=18, grosor_borde=2, sombra=True):
    if sombra:
        dibujar_sombra_panel(superficie, rect, radio_borde=radio_borde)
    pygame.draw.rect(superficie, color_fondo, rect, border_radius=radio_borde)
    # Brillo superior sutil (dos tonos), para que el panel no se vea plano.
    brillo = pygame.Surface((rect.width, max(1, rect.height // 2)), pygame.SRCALPHA)
    pygame.draw.rect(
        brillo, (255, 255, 255, 26), brillo.get_rect(),
        border_top_left_radius=radio_borde, border_top_right_radius=radio_borde,
    )
    superficie.blit(brillo, rect.topleft)
    if grosor_borde > 0:
        pygame.draw.rect(superficie, color_borde, rect, width=grosor_borde, border_radius=radio_borde)


# --- Fondo degradado con destellos animados -----------------------------

_FONDO_BASE_CACHE = {}

# (posición relativa x, y, radio en px, color, velocidad angular, fase)
_DESTELLOS = [
    (0.12, 0.18, 260, (255, 214, 150)),
    (0.88, 0.14, 300, (150, 200, 220)),
    (0.78, 0.86, 280, (230, 170, 170)),
    (0.15, 0.85, 230, (190, 210, 170)),
]


def _construir_fondo_base(ancho, alto):
    superficie = pygame.Surface((ancho, alto))
    color_arriba = COLOR_FONDO_DEGRADADO_ARRIBA
    color_abajo = COLOR_FONDO_DEGRADADO_ABAJO
    for y in range(alto):
        t = y / max(1, alto - 1)
        color = tuple(int(color_arriba[i] + (color_abajo[i] - color_arriba[i]) * t) for i in range(3))
        pygame.draw.line(superficie, color, (0, y), (ancho, y))
    return superficie


def dibujar_fondo(superficie):
    """Pinta el fondo degradado cálido con destellos suaves que se
    desplazan lentamente, en lugar de un color plano. El degradado base
    se calcula una sola vez (es costoso pintarlo píxel a fila) y se
    reutiliza en cada fotograma; solo los destellos se recalculan."""
    ancho, alto = superficie.get_size()
    clave = (ancho, alto)
    if clave not in _FONDO_BASE_CACHE:
        _FONDO_BASE_CACHE[clave] = _construir_fondo_base(ancho, alto)
    superficie.blit(_FONDO_BASE_CACHE[clave], (0, 0))

    tiempo = pygame.time.get_ticks() / 1000.0
    for indice, (x_rel, y_rel, radio, color) in enumerate(_DESTELLOS):
        angulo = tiempo * 0.12 + indice * 1.7
        cx = int(x_rel * ancho + math.sin(angulo) * 36)
        cy = int(y_rel * alto + math.cos(angulo * 0.8) * 26)
        dibujar_resplandor(superficie, (cx, cy), radio, color, alpha_max=22, anillos=8)


__all__ = [
    "dibujar_texto_centrado",
    "dibujar_texto_con_sombra",
    "ajustar_texto_a_lineas",
    "dibujar_texto_multilinea_centrado",
    "dibujar_resplandor",
    "dibujar_sombra_panel",
    "dibujar_panel",
    "dibujar_fondo",
]
