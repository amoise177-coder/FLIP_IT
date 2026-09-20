"""
Sustituto local del launcher 'enfocate' (version 2).

Colocar en la MISMA carpeta que main.py. Ajustado a la API real que usa
src/juego.py: GameBase(metadata), start(), on_start(), surface,
_stop_context() y COLORS por clave.
"""

import pygame


class _Colores(dict):
    """Colores del launcher. Si falta una clave devuelve un color neutro
    en lugar de reventar con KeyError."""

    def __missing__(self, clave):
        return (24, 26, 38)

    def __getattr__(self, nombre):
        return self[nombre.lower()]


COLORS = _Colores({
    "carbon_oscuro": (24, 26, 38),
    "carbon": (40, 43, 58),
    "blanco": (255, 255, 255),
    "negro": (0, 0, 0),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "background": (24, 26, 38),
    "surface": (40, 43, 58),
    "primary": (175, 126, 173),
    "secondary": (132, 182, 244),
    "accent": (140, 200, 160),
    "success": (140, 200, 160),
    "warning": (255, 245, 180),
    "danger": (200, 140, 140),
    "error": (200, 140, 140),
    "text": (255, 255, 255),
    "text_muted": (180, 180, 190),
    "gray": (129, 127, 137),
})


class GameMetadata:
    """Ficha del juego. Acepta campos extra sin romperse."""

    def __init__(self, title="Juego", description="", authors=None,
                 group_number=None, **extra):
        self.title = title
        self.name = title
        self.description = description
        self.authors = authors or []
        self.group_number = group_number
        for clave, valor in extra.items():
            setattr(self, clave, valor)

    def __repr__(self):
        return f"<GameMetadata {self.title!r} grupo {self.group_number}>"


class GameBase:
    """Base minima compatible con MiJuego."""

    WIDTH = 1280
    HEIGHT = 720
    FPS = 60

    def __init__(self, metadata=None, **kwargs):
        if not pygame.get_init():
            pygame.init()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            pass

        self.metadata = metadata if metadata is not None else GameMetadata()
        self.surface = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.running = False

        for clave, valor in kwargs.items():
            setattr(self, clave, valor)

    # --- ciclo de vida que juego.py invoca ---

    def start(self):
        """Crea la ventana si aun no existe y deja lista self.surface."""
        if not pygame.get_init():
            pygame.init()
        if self.surface is None:
            self.surface = pygame.display.get_surface()
        if self.surface is None:
            self.surface = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption(getattr(self.metadata, "title", "Juego"))
        self.running = True
        return self.surface

    def on_start(self):
        pass

    def _stop_context(self):
        """El launcher usa esto para cerrar el juego actual."""
        self.running = False

    stop = _stop_context
    quit = _stop_context

    # --- hooks por defecto ---

    def update(self, dt=0.0):
        pass

    def draw(self):
        if self.surface:
            self.surface.fill(COLORS["carbon_oscuro"])

    def run(self):
        surface = self.start()
        self.on_start()
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.running = False
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    def run_preview(self):
        return self.run()
