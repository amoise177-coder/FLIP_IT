"""
================================================================================
JUEGO DE SERPIENTES Y ESCALERAS (SNAKES & LADDERS)
================================================================================
Punto de entrada principal.
Contiene exclusivamente la inicialización y el bucle principal (Main Loop)
a 60 FPS delegando la lógica a los módulos correspondientes.
================================================================================
"""
import sys
import pygame

from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from game import GameEngine


def main():
    """Función principal y bucle de juego."""
    pygame.init()
    pygame.display.set_caption("Serpientes y Escaleras")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Inicializar el motor del juego
    game = GameEngine(screen)

    running = True
    while running:
        # 1. Procesamiento de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        # 2. Actualización de la lógica
        game.update()

        # 3. Renderizado
        game.draw()

        # 4. Limitación a 60 FPS
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
