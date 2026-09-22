import math
import random
from typing import List, Tuple
import pygame


class Particle:
    """
    Representa una partícula individual de celebración visual con física suave,
    desvanecimiento gradual por canal alfa y encogimiento.
    """

    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        vx: float,
        vy: float,
        radius: float = 6.0,
        lifetime: float = 1.0
    ) -> None:
        self.x: float = x
        self.y: float = y
        self.color: Tuple[int, int, int] = color
        self.vx: float = vx
        self.vy: float = vy
        self.radius: float = radius
        self.lifetime: float = lifetime
        self.max_lifetime: float = lifetime
        self.alive: bool = True

    def update(self, dt: float) -> bool:
        """Actualiza la posición y decaimiento. Retorna False cuando la partícula expira."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return False

        # Movimiento con ligera resistencia del aire y flotación ascendente
        self.x += self.vx * dt * 60.0
        self.y += self.vy * dt * 60.0
        self.vy -= 0.05 * dt * 60.0  # Ligera flotación hacia arriba
        self.vx *= (0.96 ** (dt * 60.0))

        return True

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja la partícula con desvanecimiento alfa sobre la superficie."""
        if not self.alive:
            return

        progress = max(0.0, self.lifetime / self.max_lifetime)
        current_radius = max(1.5, self.radius * progress)
        alpha = int(255 * progress)

        diameter = int(current_radius * 2) + 4
        particle_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)

        pygame.draw.circle(
            particle_surf,
            color_with_alpha,
            (diameter // 2, diameter // 2),
            int(current_radius)
        )

        surface.blit(
            particle_surf,
            (int(self.x - diameter // 2), int(self.y - diameter // 2))
        )


class VisualEffectsManager:
    """
    Administrador central de efectos visuales y sistemas de partículas.
    Permite generar estímulos positivos gratificantes al formar palabras o recibir pistas.
    """

    # Paleta de celebración accesible: dorados suaves, ámbar, esmeralda y crema
    CELEBRATION_COLORS: List[Tuple[int, int, int]] = [
        (255, 200, 60),   # Dorado cálido
        (255, 170, 50),   # Ámbar suave
        (76, 175, 80),    # Verde esmeralda reconfortante
        (100, 180, 240),  # Azul cielo suave
        (255, 235, 150)   # Brillo crema
    ]

    def __init__(self) -> None:
        self._particles: List[Particle] = []

    @property
    def active_particle_count(self) -> int:
        """Cantidad de partículas activas en pantalla."""
        return len(self._particles)

    def emit_word_celebration(self, cell_centers: List[Tuple[int, int]]) -> None:
        """
        Emite una cascada de destellos suaves sobre las casillas de la palabra validada.
        """
        for cx, cy in cell_centers:
            for _ in range(14):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1.2, 3.8)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed - 1.5  # Sesgo hacia arriba
                color = random.choice(self.CELEBRATION_COLORS)
                radius = random.uniform(4.0, 7.5)
                lifetime = random.uniform(0.7, 1.2)

                self._particles.append(
                    Particle(
                        x=cx + random.uniform(-10, 10),
                        y=cy + random.uniform(-10, 10),
                        color=color,
                        vx=vx,
                        vy=vy,
                        radius=radius,
                        lifetime=lifetime
                    )
                )

    def emit_hint_sparkle(self, x: int, y: int) -> None:
        """Emite un brillo suave alrededor de la zona de sugerencias."""
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.8, 2.2)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 0.8
            color = (100, 180, 255)
            self._particles.append(
                Particle(
                    x=x + random.uniform(-15, 15),
                    y=y + random.uniform(-15, 15),
                    color=color,
                    vx=vx,
                    vy=vy,
                    radius=4.5,
                    lifetime=0.8
                )
            )

    def update(self, dt: float) -> None:
        """Actualiza todas las partículas activas descartando las expiradas."""
        alive_particles: List[Particle] = []
        for p in self._particles:
            if p.update(dt):
                alive_particles.append(p)
        self._particles = alive_particles

    def draw(self, surface: pygame.Surface) -> None:
        """Dibuja todas las partículas sobre la escena."""
        for p in self._particles:
            p.draw(surface)

    def clear(self) -> None:
        """Elimina todas las partículas activas."""
        self._particles.clear()


# Alias para máxima flexibilidad
EfectosManager = VisualEffectsManager
EffectsManager = VisualEffectsManager
