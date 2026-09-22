"""
Módulo del sistema de partículas visuales:
Efectos para escaleras (estrellas/destellos), serpientes (humo/estela) y victoria (confeti).
"""
import random
import math
from typing import List, Tuple
import pygame


class Particle:
    """Partícula individual con física básica, desvanecimiento y color."""
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: Tuple[int, int, int], size: float, life: int,
                 shape: str = "circle", gravity: float = 0.15):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.shape = shape
        self.gravity = gravity
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-8, 8)

    def update(self) -> bool:
        """Actualiza la física y vida de la partícula. Retorna False si murió."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.rotation += self.rot_speed
        self.life -= 1
        return self.life > 0

    def draw(self, surface: pygame.Surface):
        if self.life <= 0:
            return
        alpha_ratio = max(0.0, min(1.0, self.life / self.max_life))
        current_size = max(1.0, self.size * alpha_ratio)

        px, py = int(self.x), int(self.y)

        if self.shape == "star":
            # Destello de 4 puntas para escaleras
            s = int(current_size)
            pygame.draw.line(surface, self.color, (px - s, py), (px + s, py), 2)
            pygame.draw.line(surface, self.color, (px, py - s), (px, py + s), 2)
            pygame.draw.circle(surface, (255, 255, 255), (px, py), max(1, s // 2))

        elif self.shape == "confetti":
            # Cuadrito giratorio para victoria
            s = int(current_size)
            rect_surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
            pygame.draw.rect(rect_surf, self.color, (0, 0, s * 2, s))
            rotated = pygame.transform.rotate(rect_surf, self.rotation)
            surface.blit(rotated, rotated.get_rect(center=(px, py)))

        else:
            # Círculo estándar con brillo
            pygame.draw.circle(surface, self.color, (px, py), int(current_size))


class ParticleManager:
    """Gestiona la creación, actualización y renderizado de partículas."""
    def __init__(self):
        self.particles: List[Particle] = []

    def clear(self):
        self.particles.clear()

    def spawn_ladder_sparkles(self, x: float, y: float, count: int = 4):
        """Genera destellos mágicos dorados y verdes al subir una escalera."""
        colors = [
            (255, 220, 80),   # Dorado brillante
            (100, 240, 140),  # Verde esmeralda
            (255, 255, 255),  # Blanco puro
            (255, 180, 50)    # Ámbar
        ]
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.2, 3.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 1.5  # Tendencia hacia arriba
            color = random.choice(colors)
            size = random.uniform(4.0, 7.5)
            life = random.randint(18, 30)
            self.particles.append(Particle(x, y, vx, vy, color, size, life, shape="star", gravity=0.08))

    def spawn_snake_dust(self, x: float, y: float, count: int = 5):
        """Genera estela de humo y chispas rojas/moradas al deslizarse por una serpiente."""
        colors = [
            (255, 80, 100),   # Rojo coral
            (255, 140, 60),   # Naranja advertencia
            (200, 70, 180),   # Púrpura
            (255, 220, 220)   # Humo claro
        ]
        for _ in range(count):
            vx = random.uniform(-2.5, 2.5)
            vy = random.uniform(-2.0, 1.0)
            color = random.choice(colors)
            size = random.uniform(5.0, 9.0)
            life = random.randint(15, 26)
            self.particles.append(Particle(x, y, vx, vy, color, size, life, shape="circle", gravity=0.05))

    def spawn_confetti(self, center_x: int, top_y: int, count: int = 10):
        """Genera lluvia de confeti festivo para la victoria."""
        colors = [
            (255, 75, 100), (80, 160, 255), (255, 220, 60),
            (70, 225, 120), (220, 90, 240), (255, 150, 50)
        ]
        for _ in range(count):
            x = center_x + random.uniform(-250, 250)
            y = top_y + random.uniform(-20, 40)
            vx = random.uniform(-2.0, 2.0)
            vy = random.uniform(2.5, 6.0)
            color = random.choice(colors)
            size = random.uniform(6.0, 10.0)
            life = random.randint(60, 110)
            self.particles.append(Particle(x, y, vx, vy, color, size, life, shape="confetti", gravity=0.08))

    def update(self):
        """Actualiza todas las partículas activas y remueve las expiradas."""
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface: pygame.Surface):
        """Dibuja todas las partículas sobre la superficie dada."""
        for p in self.particles:
            p.draw(surface)
