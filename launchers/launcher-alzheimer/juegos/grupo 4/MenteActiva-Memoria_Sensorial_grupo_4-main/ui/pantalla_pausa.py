"""
MenteActiva — Overlay de Pausa
Dibuja un overlay oscuro con controles de pausa sobre la pantalla de juego.
"""
import pygame

from config import WINDOW_WIDTH, WINDOW_HEIGHT, Colors
from ui.renderer import draw_text, draw_overlay, draw_panel


def dibujar_pausa(surface):
    """
    Dibuja el overlay de pausa directamente sobre la superficie del juego.
    Función simple (no una clase) porque es un overlay, no una pantalla completa.
    """
    # Overlay oscuro
    draw_overlay(surface, alpha=160)

    # Panel central
    panel_w = 400
    panel_h = 220
    panel_x = (WINDOW_WIDTH - panel_w) // 2
    panel_y = (WINDOW_HEIGHT - panel_h) // 2
    draw_panel(surface, pygame.Rect(panel_x, panel_y, panel_w, panel_h),
               color=Colors.WHITE, alpha=240, radius=20)

    # Título
    draw_text(surface, "Juego en Pausa",
              WINDOW_WIDTH // 2, panel_y + 50,
              "heading", Colors.DARK_TEXT, bold=True)

    # Instrucciones
    draw_text(surface, "Presiona P para continuar",
              WINDOW_WIDTH // 2, panel_y + 110,
              "body", Colors.DARK_TEXT)

    draw_text(surface, "R = Reiniciar  ·  ESC = Menú",
              WINDOW_WIDTH // 2, panel_y + 150,
              "small", Colors.DARK_TEXT)

    # Borde decorativo
    pygame.draw.rect(surface, Colors.LAVENDER,
                     pygame.Rect(panel_x, panel_y, panel_w, panel_h),
                     3, border_radius=20)
