"""Pequeños íconos vectoriales (triángulo de "jugar", engranaje, estrella,
símbolo de apagado, flechas) dibujados con formas geométricas simples,
para que los botones no dependan de ningún archivo de imagen."""

import math

import pygame


def jugar(superficie, centro, tamano, color):
    """Triángulo de "reproducir"."""
    r = tamano / 2
    puntos = [
        (centro[0] - r * 0.55, centro[1] - r),
        (centro[0] - r * 0.55, centro[1] + r),
        (centro[0] + r, centro[1]),
    ]
    pygame.draw.polygon(superficie, color, puntos)


def opciones(superficie, centro, tamano, color):
    """Engranaje simple: un círculo con dientes rectangulares alrededor y
    un agujero central realmente transparente (se dibuja en una capa
    aparte y se recorta con alpha, en vez de pintarlo del color de fondo
    del botón, que cambia según el estado)."""
    r_exterior = tamano / 2
    r_interior = r_exterior * 0.55
    n_dientes = 8
    ancho_diente = r_exterior * 0.34
    margen = int(ancho_diente)
    lado = int(tamano + margen * 2)
    capa = pygame.Surface((lado, lado), pygame.SRCALPHA)
    centro_local = (lado / 2, lado / 2)
    for i in range(n_dientes):
        angulo = (2 * math.pi / n_dientes) * i
        cx = centro_local[0] + math.cos(angulo) * r_exterior * 0.82
        cy = centro_local[1] + math.sin(angulo) * r_exterior * 0.82
        diente = pygame.Surface((ancho_diente, ancho_diente), pygame.SRCALPHA)
        pygame.draw.rect(diente, color, diente.get_rect(), border_radius=2)
        rotado = pygame.transform.rotate(diente, -math.degrees(angulo))
        rect = rotado.get_rect(center=(cx, cy))
        capa.blit(rotado, rect)
    pygame.draw.circle(capa, color, centro_local, int(r_exterior * 0.68))
    pygame.draw.circle(capa, (0, 0, 0, 0), centro_local, int(r_interior))
    superficie.blit(capa, capa.get_rect(center=centro))


def creditos(superficie, centro, tamano, color):
    """Estrella de 5 puntas."""
    r_exterior = tamano / 2
    r_interior = r_exterior * 0.42
    puntos = []
    for i in range(10):
        angulo = math.pi / 2 + i * math.pi / 5
        radio = r_exterior if i % 2 == 0 else r_interior
        puntos.append((centro[0] + math.cos(angulo) * radio, centro[1] - math.sin(angulo) * radio))
    pygame.draw.polygon(superficie, color, puntos)


def salir(superficie, centro, tamano, color):
    """Símbolo de apagado: un arco abierto arriba + una línea vertical."""
    r = tamano / 2
    grosor = max(2, int(tamano * 0.14))
    rect = pygame.Rect(0, 0, tamano, tamano)
    rect.center = centro
    pygame.draw.arc(superficie, color, rect, math.radians(-245), math.radians(65), grosor)
    pygame.draw.line(superficie, color, (centro[0], centro[1] - r), (centro[0], centro[1] - r * 0.15), grosor)


def volver(superficie, centro, tamano, color):
    """Flecha apuntando a la izquierda."""
    r = tamano / 2
    puntos = [
        (centro[0] + r, centro[1] - r),
        (centro[0] + r, centro[1] + r),
        (centro[0] - r, centro[1]),
    ]
    pygame.draw.polygon(superficie, color, puntos)


def continuar(superficie, centro, tamano, color):
    """Flecha apuntando a la derecha."""
    r = tamano / 2
    puntos = [
        (centro[0] - r, centro[1] - r),
        (centro[0] - r, centro[1] + r),
        (centro[0] + r, centro[1]),
    ]
    pygame.draw.polygon(superficie, color, puntos)


def reiniciar(superficie, centro, tamano, color):
    """Flecha circular de "reiniciar partida"."""
    r = tamano / 2
    grosor = max(2, int(tamano * 0.16))
    rect = pygame.Rect(0, 0, tamano, tamano)
    rect.center = centro
    pygame.draw.arc(superficie, color, rect, math.radians(20), math.radians(300), grosor)
    punta_angulo = math.radians(20)
    punta = (centro[0] + math.cos(punta_angulo) * r, centro[1] - math.sin(punta_angulo) * r)
    ala1 = (punta[0] - grosor * 1.6, punta[1] - grosor * 0.2)
    ala2 = (punta[0] - grosor * 0.2, punta[1] + grosor * 1.6)
    pygame.draw.polygon(superficie, color, [punta, ala1, ala2])
