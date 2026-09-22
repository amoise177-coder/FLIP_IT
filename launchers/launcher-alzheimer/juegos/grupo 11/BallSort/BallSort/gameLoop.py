import pygame
import copy
import math
import time
import random
from pathlib import Path
from solver import Node, Graph
from sound_effects import SoundManager
from pygame.locals import (
    K_ESCAPE, K_h, K_1, K_2, K_3, K_4, K_5, K_6, K_7,
    K_s, K_d, K_a, K_u, K_r, KEYDOWN, QUIT
)

# Paleta de colores moderna y vibrante
COLOR_PALETTE = {
    1: (235, 59, 90),    # Rojo carmesí
    2: (38, 222, 129),   # Verde esmeralda
    3: (75, 123, 236),   # Azul zafiro
    4: (250, 130, 49),   # Naranja cálido
    5: (253, 114, 114),  # Rosa pastel / coral
    6: (136, 84, 208),   # Púrpura real
    7: (43, 203, 186),   # Turquesa brillante
    8: (254, 211, 48),   # Amarillo dorado
}

BG_TOP = (20, 24, 33)
BG_BOTTOM = (12, 14, 20)
TEXT_WHITE = (245, 246, 250)
TEXT_MUTED = (165, 177, 194)
ACCENT_CYAN = (0, 210, 211)
ACCENT_GOLD = (255, 215, 0)


class ConfettiParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-14, -6)
        self.gravity = 0.35
        self.size = random.uniform(6, 12)
        self.color = random.choice([
            (235, 59, 90), (38, 222, 129), (75, 123, 236),
            (250, 130, 49), (254, 211, 48), (136, 84, 208), (0, 210, 211)
        ])
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-8, 8)
        self.lifetime = random.randint(70, 130)
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98
        self.rotation += self.rot_speed
        self.age += 1

    def draw(self, surface):
        if self.age >= self.lifetime:
            return
        surf = pygame.Surface((int(self.size), int(self.size * 0.6)), pygame.SRCALPHA)
        alpha = max(0, int(255 * (1.0 - (self.age / self.lifetime))))
        r, g, b = self.color
        surf.fill((r, g, b, alpha))
        rotated = pygame.transform.rotate(surf, self.rotation)
        surface.blit(rotated, (self.x - rotated.get_width() // 2, self.y - rotated.get_height() // 2))


class SparkleParticle:
    def __init__(self, x, y, color=ACCENT_GOLD):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.tau)
        speed = random.uniform(1.5, 4.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.radius = random.uniform(2, 4)
        self.lifetime = random.randint(25, 45)
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.age += 1

    def draw(self, surface):
        if self.age >= self.lifetime:
            return
        alpha = max(0, int(255 * (1.0 - (self.age / self.lifetime))))
        r, g, b = self.color
        surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (r, g, b, alpha), (int(self.radius), int(self.radius)), int(self.radius))
        surface.blit(surf, (int(self.x - self.radius), int(self.y - self.radius)))


def draw_vector_star(surface, center_x, center_y, radius, color):
    """Dibuja una estrella de 5 puntas perfecta y nítida."""
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius * 0.45
        angle = i * math.pi / 5 - math.pi / 2
        points.append((center_x + r * math.cos(angle), center_y + r * math.sin(angle)))
    pygame.draw.polygon(surface, color, points)


def draw_vector_icon(surface, icon_name, cx, cy, color=(255, 255, 255)):
    """Dibuja iconos vectoriales nítidos sin depender de fuentes de caracteres."""
    if icon_name == 'hint':
        # Bombilla / Pista
        pygame.draw.circle(surface, (255, 230, 90), (cx, cy - 2), 6)
        pygame.draw.rect(surface, (200, 180, 70), (cx - 3, cy + 4, 6, 3), border_radius=1)
        pygame.draw.line(surface, (255, 255, 255), (cx - 1, cy - 4), (cx + 1, cy - 4), 1)
    elif icon_name == 'undo':
        # Flecha de retorno / Deshacer
        pygame.draw.arc(surface, color, (cx - 7, cy - 6, 14, 14), 0.5, 3.4, 2)
        pygame.draw.polygon(surface, color, [(cx - 8, cy - 1), (cx - 3, cy - 5), (cx - 3, cy + 3)])
    elif icon_name == 'reset':
        # Flecha circular / Reiniciar
        pygame.draw.arc(surface, color, (cx - 6, cy - 6, 12, 12), 0.7, 5.8, 2)
        pygame.draw.polygon(surface, color, [(cx + 4, cy - 6), (cx + 8, cy - 2), (cx + 2, cy - 2)])
    elif icon_name == 'menu':
        # Tres barras / Menú hamburguesa
        for dy in (-4, 0, 4):
            pygame.draw.line(surface, color, (cx - 7, cy + dy), (cx + 7, cy + dy), 2)
    elif icon_name == 'next_arrow':
        # Flecha derecha estilizada
        pygame.draw.line(surface, color, (cx - 6, cy), (cx + 6, cy), 3)
        pygame.draw.polygon(surface, color, [(cx + 7, cy), (cx + 2, cy - 5), (cx + 2, cy + 5)])
    elif icon_name == 'help':
        # Signo de interrogación / Reglas
        pygame.draw.circle(surface, color, (cx, cy - 3), 4, 2)
        pygame.draw.line(surface, color, (cx + 2, cy - 1), (cx, cy + 2), 2)
        pygame.draw.circle(surface, color, (cx, cy + 5), 1)



class MovingBall:
    def __init__(self, color_idx, start_pos, end_pos, on_finish=None):
        self.color_idx = color_idx
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos
        self.cur_x = self.start_x
        self.cur_y = self.start_y
        self.on_finish = on_finish
        
        # Trayectoria: Subir, mover horizontalmente, bajar con rebote
        self.peak_y = min(self.start_y, self.end_y) - 60
        self.total_frames = 20
        self.current_frame = 0
        self.finished = False

    def update(self):
        if self.finished:
            return
        self.current_frame += 1
        t = min(1.0, self.current_frame / self.total_frames)

        # Interpolación horizontal suave (ease-in-out)
        t_x = 0.5 - 0.5 * math.cos(t * math.pi)
        self.cur_x = self.start_x + (self.end_x - self.start_x) * t_x

        # Trayectoria parabólica vertical para dar efecto de arco fluido
        if t < 0.4:
            # Fase de subida
            sub_t = t / 0.4
            self.cur_y = self.start_y + (self.peak_y - self.start_y) * math.sin(sub_t * math.pi / 2)
        elif t < 0.7:
            # Fase horizontal en el pico
            self.cur_y = self.peak_y
        else:
            # Fase de caída con rebote
            sub_t = (t - 0.7) / 0.3
            # Caída acelerada
            drop_progress = sub_t * sub_t
            self.cur_y = self.peak_y + (self.end_y - self.peak_y) * drop_progress

        if self.current_frame >= self.total_frames:
            self.cur_x = self.end_x
            self.cur_y = self.end_y
            self.finished = True
            if self.on_finish:
                self.on_finish()


class Game:
    def __init__(self, levels_data, level_index):
        self.levels_data = levels_data
        self.level_index = level_index
        self.n = levels_data[level_index][0]
        self.m = levels_data[level_index][1]
        self.ntubes = levels_data[level_index][2]
        self.initialState = copy.deepcopy(levels_data[level_index][3])
        self.arrTotal = copy.deepcopy(self.initialState)
        self.completed = [0] * self.ntubes
        self.nMoves = 0
        self.history = []
        for i in range(self.ntubes):
            self.fillCompleted(i)

    def fillCompleted(self, col):
        if self.checkCompleted(col):
            self.completed[col] = 1
        else:
            self.completed[col] = 0

    def checkCompleted(self, col):
        if len(self.arrTotal[col]) != self.m:
            return False
        return len(set(self.arrTotal[col])) == 1

    def validMove(self, fromCol, toCol):
        if fromCol == toCol:
            return False
        if fromCol < 0 or fromCol >= self.ntubes or toCol < 0 or toCol >= self.ntubes:
            return False
        if len(self.arrTotal[fromCol]) == 0:
            return False
        if len(self.arrTotal[toCol]) >= self.m:
            return False
        if self.completed[fromCol]:
            return False
        
        if len(self.arrTotal[toCol]) == 0:
            return True
        return self.arrTotal[fromCol][-1] == self.arrTotal[toCol][-1]

    def moveBall(self, fromCol, toCol):
        if self.validMove(fromCol, toCol):
            num = self.arrTotal[fromCol].pop(-1)
            self.arrTotal[toCol].append(num)
            self.fillCompleted(toCol)
            self.fillCompleted(fromCol)
            self.nMoves += 1
            self.history.append((fromCol, toCol))
            return True
        return False

    def undoMove(self):
        if len(self.history) > 0:
            fromCol, toCol = self.history.pop()
            num = self.arrTotal[toCol].pop(-1)
            self.arrTotal[fromCol].append(num)
            self.fillCompleted(fromCol)
            self.fillCompleted(toCol)
            self.nMoves = max(0, self.nMoves - 1)
            return True
        return False

    def resetLevel(self):
        self.arrTotal = copy.deepcopy(self.initialState)
        self.completed = [0] * self.ntubes
        for i in range(self.ntubes):
            self.fillCompleted(i)
        self.nMoves = 0
        self.history = []

    def gameOver(self):
        return self.completed.count(1) == self.n

    def hasValidMoves(self):
        """Comprueba si existe al menos un movimiento legal posible en el estado actual."""
        if self.gameOver():
            return True
        for i in range(self.ntubes):
            for j in range(self.ntubes):
                if i != j and self.validMove(i, j):
                    return True
        return False


class GameLoop:
    def __init__(self, screen, width=1280, height=720):
        self.screen = screen
        self.width = width
        self.height = height
        self.sound = SoundManager()

        self.levels = [
            # Nivel 1 (Tutorial básico - 2 colores)
            [2, 4, 3, [[2, 2, 2, 1], [1, 1, 1, 2], []]],
            # Nivel 2 (3 colores)
            [3, 4, 4, [[2, 1, 2, 3], [3, 1, 3, 2], [1, 3, 2, 1], []]],
            # Nivel 3
            [3, 4, 5, [[6, 5, 6], [5, 5, 6, 4], [6, 4, 5, 4], [4], []]],
            # Nivel 4
            [3, 4, 5, [[1, 2, 3, 1], [2, 2, 3, 1], [3, 1, 2, 3], [], []]],
            # Nivel 5
            [3, 4, 5, [[1, 2, 3, 3], [1, 2, 1, 2], [3, 1, 2, 3], [], []]],
            # Nivel 6 (4 colores)
            [4, 4, 5, [[3, 2, 1, 3], [2, 1, 1, 2], [1, 2, 3, 4], [4, 4], [3, 4]]],
            # Nivel 7
            [4, 4, 6, [[1, 3, 2, 4], [4, 2, 1, 3], [3, 4, 1, 2], [2, 1, 4, 3], [], []]],
            # Nivel 8
            [4, 4, 6, [[4, 1, 2, 3], [3, 2, 4, 1], [1, 4, 3, 2], [2, 3, 1, 4], [], []]],
            # Nivel 9 (Introducción a 5 colores)
            [5, 4, 6, [[3, 2, 1, 3], [2, 1, 1, 2], [1, 2, 3, 4], [4, 4], [3, 5, 5, 4], [5, 5]]],
            # Nivel 10
            [5, 4, 7, [[1, 5, 2, 3], [4, 2, 5, 1], [3, 1, 4, 5], [2, 3, 1, 4], [5, 4, 3, 2], [], []]],
            # Nivel 11
            [5, 4, 7, [[5, 1, 3, 2], [2, 4, 1, 5], [3, 2, 5, 4], [1, 3, 4, 2], [4, 5, 2, 3], [], []]],
            # Nivel 12
            [5, 4, 7, [[2, 3, 5, 1], [1, 4, 2, 5], [5, 1, 3, 4], [4, 2, 1, 3], [3, 5, 4, 2], [], []]],
            # Nivel 13 (Introducción a 6 colores)
            [6, 4, 7, [[1, 2, 3, 4], [6, 6], [2, 1, 1, 2], [4, 4, 6], [3, 2, 1, 3], [3, 5, 5], [5, 5, 4, 6]]],
            # Nivel 14
            [6, 4, 8, [[1, 2, 3, 4], [5, 6, 1, 2], [3, 4, 5, 6], [6, 5, 4, 3], [2, 1, 6, 5], [4, 3, 2, 1], [], []]],
            # Nivel 15
            [6, 4, 8, [[6, 1, 5, 2], [3, 4, 2, 6], [1, 5, 3, 4], [2, 6, 4, 1], [5, 3, 1, 5], [4, 2, 6, 3], [], []]],
            # Nivel 16
            [6, 4, 8, [[2, 4, 6, 1], [5, 3, 1, 4], [6, 2, 5, 3], [1, 6, 3, 2], [4, 5, 2, 6], [3, 1, 4, 5], [], []]],
            # Nivel 17
            [6, 4, 8, [[4, 3, 1, 6], [2, 5, 6, 3], [1, 2, 4, 5], [6, 1, 3, 2], [5, 4, 2, 1], [3, 6, 5, 4], [], []]],
            # Nivel 18
            [6, 4, 8, [[3, 6, 2, 5], [1, 4, 5, 2], [6, 3, 1, 4], [2, 5, 4, 6], [5, 1, 3, 2], [4, 2, 6, 3], [], []]],
            # Nivel 19
            [6, 4, 8, [[5, 2, 4, 1], [6, 3, 1, 5], [2, 6, 3, 4], [1, 4, 5, 2], [3, 1, 2, 6], [4, 5, 6, 3], [], []]],
            # Nivel 20 (Nivel Final Avanzado)
            [6, 4, 8, [[1, 6, 2, 5], [3, 4, 6, 1], [5, 2, 1, 4], [6, 3, 5, 2], [4, 1, 3, 6], [2, 5, 4, 3], [], []]]
        ]
        
        self.currentLevel = 0
        self.game = Game(self.levels, self.currentLevel)
        
        # Variables de selección y animación
        self.tubeSelected = False
        self.fromTube = -1
        self.toTube = -1
        self.moving_ball = None
        self.selected_ball_progress = 0.0  # Animación de elevación (0.0 a 1.0)
        
        # Pistas y AutoSolve
        self.hint = None
        self.showHint = False
        self.showAuto = False
        self.solver = 1
        self.noSols = False
        self.currAlg = ""
        
        # Interfaz
        self.clickable_buttons = {}
        self.tubes_rects = []
        self.particles = []
        self.level_won = False
        self.victory_played = False
        self.completed_tubes_celebrated = set()
        
        # Feedback de jugada inválida y sacudida de tubo
        self.shake_tube = -1
        self.shake_timer = 0
        self.invalid_msg = ""
        self.invalid_msg_timer = 0
        self.show_rules = False

        
        # Fuentes tipográficas
        self.font_title = pygame.font.SysFont("segoeui, arial", 28, bold=True)
        self.font_sub = pygame.font.SysFont("segoeui, arial", 18, bold=True)
        self.font_btn = pygame.font.SysFont("segoeui, arial", 16, bold=True)
        self.font_small = pygame.font.SysFont("segoeui, arial", 14)

        # Pre-generar fondo con gradiente elegante
        self.bg_surface = self._create_background()

        # Partículas ambientales sutiles
        self.ambient_stars = [
            [random.randint(0, self.width), random.randint(0, self.height), random.uniform(0.5, 2.0), random.uniform(0.1, 0.4)]
            for _ in range(40)
        ]

    def _create_background(self):
        surf = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            ratio = y / self.height
            r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
            g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
            b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (self.width, y))
        
        # Resplandor suave superior
        glow = pygame.Surface((self.width, 240), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (30, 45, 65, 45), (-100, -100, self.width + 200, 300))
        surf.blit(glow, (0, 0))
        return surf

    def loadNextLevel(self):
        if self.currentLevel < len(self.levels) - 1:
            self.currentLevel += 1
            self.game = Game(self.levels, self.currentLevel)
            self.resetSelection()
            self.level_won = False
            self.victory_played = False
            self.completed_tubes_celebrated.clear()
            self.particles.clear()
            self.invalid_msg_timer = 0
            self.shake_timer = 0
            self.show_rules = False

    def resetLevel(self):
        self.game.resetLevel()
        self.resetSelection()
        self.level_won = False
        self.victory_played = False
        self.completed_tubes_celebrated.clear()
        self.particles.clear()
        self.invalid_msg_timer = 0
        self.shake_timer = 0
        self.show_rules = False
        self.sound.play('click')

    def resetSelection(self):
        self.tubeSelected = False
        self.fromTube = -1
        self.toTube = -1
        self.showHint = False
        self.selected_ball_progress = 0.0

    def drawBall(self, surface, x, y, radius, color_idx):
        """Dibuja una bola esférica 3D con degradado y reflejo especular."""
        base_color = COLOR_PALETTE.get(color_idx, (180, 180, 180))
        
        # Sombra proyectada debajo
        shadow_surf = pygame.Surface((int(radius * 2.4), int(radius * 1.2)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, int(radius * 2.4), int(radius * 1.2)))
        surface.blit(shadow_surf, (x - int(radius * 1.2), y + int(radius * 0.45)))

        # Superficie de la bola con canal alfa
        ball_surf = pygame.Surface((int(radius * 2 + 4), int(radius * 2 + 4)), pygame.SRCALPHA)
        center_b = int(radius + 2)

        # Círculo base con sombreado periférico más oscuro
        r, g, b = base_color
        dark_r, dark_g, dark_b = int(r * 0.55), int(g * 0.55), int(b * 0.55)
        pygame.draw.circle(ball_surf, (dark_r, dark_g, dark_b), (center_b, center_b), int(radius))

        # Degradado esférico radial
        for step in range(int(radius), 0, -1):
            ratio = step / radius
            step_r = int(r * (1.1 - 0.55 * ratio))
            step_g = int(g * (1.1 - 0.55 * ratio))
            step_b = int(b * (1.1 - 0.55 * ratio))
            step_r = min(255, max(0, step_r))
            step_g = min(255, max(0, step_g))
            step_b = min(255, max(0, step_b))
            
            # Centro desplazado hacia arriba a la izquierda para simular luz direccional
            off_x = center_b - int((center_b - step) * 0.15)
            off_y = center_b - int((center_b - step) * 0.20)
            pygame.draw.circle(ball_surf, (step_r, step_g, step_b), (off_x, off_y), step)

        # Reflejo especular blanco brillante en la esquina superior izquierda
        spec_x = center_b - int(radius * 0.35)
        spec_y = center_b - int(radius * 0.35)
        spec_radius = max(2, int(radius * 0.32))
        spec_surf = pygame.Surface((spec_radius * 2, spec_radius * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(spec_surf, (255, 255, 255, 170), (0, 0, spec_radius * 2, int(spec_radius * 1.4)))
        ball_surf.blit(spec_surf, (spec_x - spec_radius, spec_y - spec_radius // 2))

        # Pequeño punto focal de máximo brillo
        pygame.draw.circle(ball_surf, (255, 255, 255, 220), (spec_x, spec_y), max(1, int(radius * 0.1)))

        # Borde exterior suave anti-aliased
        pygame.draw.circle(ball_surf, (dark_r, dark_g, dark_b, 120), (center_b, center_b), int(radius), 1)

        surface.blit(ball_surf, (x - center_b, y - center_b))

    def _get_tube_layout(self):
        """Calcula el ancho y la posición de cada tubo para una distribución armónica."""
        ntubes = self.game.ntubes
        tube_h = 280
        ball_radius = 27
        
        # Ajustar ancho de tubo según cantidad de tubos
        if ntubes <= 4:
            tube_w = 80
            ball_radius = 29
        elif ntubes <= 6:
            tube_w = 76
            ball_radius = 27
        else:
            tube_w = 70
            ball_radius = 25

        total_tubes_w = ntubes * tube_w
        avail_w = self.width - 120
        spacing = (avail_w - total_tubes_w) / (ntubes + 1)
        spacing = max(18, min(80, spacing))
        
        start_x = (self.width - (ntubes * tube_w + (ntubes - 1) * spacing)) / 2
        tube_y = 230

        coords = []
        for i in range(ntubes):
            x = start_x + i * (tube_w + spacing)
            coords.append((x, tube_y, tube_w, tube_h, ball_radius))
        return coords

    def drawTube(self, tube_idx, x, y, tube_w, tube_h, ball_radius):
        """Dibuja un tubo de cristal elegante con transparencias, reborde y sombras."""
        # Efecto de sacudida si el jugador intenta un movimiento inválido hacia este tubo
        if self.shake_tube == tube_idx and self.shake_timer > 0:
            shake_offset = int(math.sin(self.shake_timer * 1.6) * 6)
            x += shake_offset

        is_selected = (tube_idx == self.fromTube)
        is_completed = (self.game.completed[tube_idx] == 1)
        balls = self.game.arrTotal[tube_idx]
        
        # Sombra de contacto del tubo sobre la mesa/piso
        shadow_w = tube_w + 30
        shadow_h = 24
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 95), (0, 0, shadow_w, shadow_h))
        self.screen.blit(shadow_surf, (x - 15, y + tube_h - 10))

        # Aura luminosa cuando el tubo está seleccionado
        if is_selected:
            glow_surf = pygame.Surface((tube_w + 40, tube_h + 40), pygame.SRCALPHA)
            pulse = (math.sin(time.time() * 6) + 1) * 0.5  # 0.0 a 1.0
            alpha = int(70 + pulse * 45)
            pygame.draw.rect(
                glow_surf, (ACCENT_CYAN[0], ACCENT_CYAN[1], ACCENT_CYAN[2], alpha),
                (10, 10, tube_w + 20, tube_h + 20),
                border_radius=int(tube_w // 2 + 10)
            )
            self.screen.blit(glow_surf, (x - 20, y - 20))
        elif self.tubeSelected and self.fromTube >= 0 and self.moving_ball is None:
            # Guía visual: Resalta los tubos que SÍ pueden recibir la bola seleccionada
            if self.game.validMove(self.fromTube, tube_idx):
                pulse = (math.sin(time.time() * 7) + 1) * 0.5
                glow_dest = pygame.Surface((tube_w + 30, tube_h + 30), pygame.SRCALPHA)
                alpha_g = int(40 + pulse * 35)
                pygame.draw.rect(
                    glow_dest, (46, 204, 113, alpha_g),
                    (5, 5, tube_w + 20, tube_h + 20),
                    border_radius=int(tube_w // 2 + 5)
                )
                self.screen.blit(glow_dest, (x - 15, y - 15))

                # Flechita verde pulsante indicando que se puede depositar aquí
                arrow_y = y - 22 + int(pulse * 5)
                arrow_pts = [
                    (x + tube_w // 2, arrow_y + 10),
                    (x + tube_w // 2 - 7, arrow_y),
                    (x + tube_w // 2 + 7, arrow_y)
                ]
                pygame.draw.polygon(self.screen, (46, 204, 113), arrow_pts)


        # Superficie de cristal translúcido
        glass_surf = pygame.Surface((tube_w, tube_h), pygame.SRCALPHA)
        
        # Fondo de cristal con tinte azulado sutil
        pygame.draw.rect(
            glass_surf, (220, 240, 255, 28),
            (0, 0, tube_w, tube_h),
            border_bottom_left_radius=int(tube_w // 2),
            border_bottom_right_radius=int(tube_w // 2)
        )

        # Reflejo vertical de cristal en el borde izquierdo
        pygame.draw.line(glass_surf, (255, 255, 255, 80), (7, 10), (7, tube_h - tube_w // 2), 3)
        # Reflejo vertical más tenue en el lado derecho
        pygame.draw.line(glass_surf, (255, 255, 255, 35), (tube_w - 7, 10), (tube_w - 7, tube_h - tube_w // 2), 2)

        # Contorno de cristal pulido
        border_color = (180, 220, 255, 120) if not is_selected else (0, 210, 211, 220)
        border_thickness = 3 if is_selected else 2
        pygame.draw.rect(
            glass_surf, border_color,
            (0, 0, tube_w, tube_h),
            border_thickness,
            border_bottom_left_radius=int(tube_w // 2),
            border_bottom_right_radius=int(tube_w // 2)
        )

        # Reborde superior exterior del tubo (cuello labiado)
        rim_rect = pygame.Rect(x - 5, y - 4, tube_w + 10, 8)
        pygame.draw.rect(self.screen, (220, 240, 255, 180), rim_rect, border_radius=4)
        pygame.draw.rect(self.screen, border_color, rim_rect, 2, border_radius=4)

        # Renderizar bolas dentro del tubo
        center_x = x + tube_w // 2
        bottom_y = y + tube_h - ball_radius - 8
        ball_spacing = ball_radius * 2 + 4

        # Dibujar las bolas estáticas en el tubo
        num_balls = len(balls)
        for idx, color_num in enumerate(balls):
            # Si el tubo está seleccionado y es la bola superior, se anima elevándose
            if is_selected and idx == num_balls - 1 and self.moving_ball is None:
                # La bola flota por encima del tubo
                hover_offset = 50 + math.sin(time.time() * 7) * 4
                ball_y = y - hover_offset
                self.drawBall(self.screen, center_x, int(ball_y), ball_radius, color_num)
            else:
                ball_y = bottom_y - (idx * ball_spacing)
                self.drawBall(self.screen, center_x, int(ball_y), ball_radius, color_num)

        # Superponer la superficie de cristal translúcido para que las bolas se vean dentro del tubo
        self.screen.blit(glass_surf, (x, y))

        # Efecto especial si el tubo está completado (Tapón de corcho dorado y brillo)
        if is_completed:
            cork_w = tube_w - 6
            cork_h = 16
            cork_rect = pygame.Rect(x + 3, y - 8, cork_w, cork_h)
            pygame.draw.rect(self.screen, (243, 156, 18), cork_rect, border_radius=5)
            pygame.draw.rect(self.screen, (211, 84, 0), cork_rect, 2, border_radius=5)
            
            # Estrella vectorial dorada de completado en el centro del tubo
            draw_vector_star(self.screen, x + tube_w // 2, y + 26, 9, ACCENT_GOLD)

        # Placa / Número del tubo abajo
        badge_y = y + tube_h + 18
        badge_rect = pygame.Rect(x + tube_w // 2 - 16, badge_y, 32, 24)
        pygame.draw.rect(self.screen, (30, 39, 56), badge_rect, border_radius=6)
        pygame.draw.rect(self.screen, (60, 75, 100), badge_rect, 1, border_radius=6)
        
        num_text = self.font_btn.render(str(tube_idx + 1), True, TEXT_WHITE)
        self.screen.blit(num_text, (badge_rect.centerx - num_text.get_width() // 2, badge_rect.centery - num_text.get_height() // 2))

        # Rectángulo clickeable de todo el tubo (cubre la bola elevada y la base)
        return pygame.Rect(x - 8, y - 75, tube_w + 16, tube_h + 105)

    def drawTopBar(self):
        """Barra superior estilizada tipo tarjeta flotante (Glassmorphism)."""
        bar_w = self.width - 80
        bar_h = 70
        bar_x = 40
        bar_y = 20

        # Tarjeta de cristal oscuro
        bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        pygame.draw.rect(bar_surf, (28, 36, 52, 215), (0, 0, bar_w, bar_h), border_radius=16)
        pygame.draw.rect(bar_surf, (60, 75, 105, 160), (0, 0, bar_w, bar_h), 2, border_radius=16)
        self.screen.blit(bar_surf, (bar_x, bar_y))

        # Nivel con insignia
        lvl_title = self.font_title.render(f"NIVEL {self.currentLevel + 1}", True, TEXT_WHITE)
        self.screen.blit(lvl_title, (bar_x + 25, bar_y + 10))

        sub_lvl = self.font_small.render(f"de {len(self.levels)} niveles", True, TEXT_MUTED)
        self.screen.blit(sub_lvl, (bar_x + 27, bar_y + 42))

        # Movimientos
        moves_label = self.font_small.render("MOVIMIENTOS", True, TEXT_MUTED)
        self.screen.blit(moves_label, (bar_x + 190, bar_y + 14))
        
        moves_val = self.font_title.render(f"{self.game.nMoves}", True, ACCENT_CYAN)
        self.screen.blit(moves_val, (bar_x + 190, bar_y + 32))

        # Botones de acción estilizados a la derecha
        self.clickable_buttons = {}
        mouse_pos = pygame.mouse.get_pos()

        buttons_def = [
            ('help', "Reglas", (142, 68, 173)),
            ('hint', "Pista", (52, 152, 219)),
            ('undo', "Deshacer", (230, 126, 34)),
            ('reset', "Reiniciar", (231, 76, 60)),
            ('menu', "Menú", (52, 73, 94))
        ]

        btn_w = 112
        btn_h = 42
        btn_gap = 10
        start_btn_x = bar_x + bar_w - (len(buttons_def) * (btn_w + btn_gap)) - 10
        btn_y = bar_y + (bar_h - btn_h) // 2


        for i, (key, label, col) in enumerate(buttons_def):
            bx = start_btn_x + i * (btn_w + btn_gap)
            btn_rect = pygame.Rect(bx, btn_y, btn_w, btn_h)
            is_hover = btn_rect.collidepoint(mouse_pos)

            # Fondo del botón con estado hover
            btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            base_alpha = 235 if is_hover else 185
            bg_col = (col[0], col[1], col[2], base_alpha)
            pygame.draw.rect(btn_surf, bg_col, (0, 0, btn_w, btn_h), border_radius=10)
            if is_hover:
                pygame.draw.rect(btn_surf, (255, 255, 255, 150), (0, 0, btn_w, btn_h), 2, border_radius=10)

            self.screen.blit(btn_surf, (bx, btn_y))
            
            # Icono vectorial + texto
            draw_vector_icon(self.screen, key, bx + 22, btn_y + btn_h // 2, TEXT_WHITE)
            txt_surf = self.font_btn.render(label, True, TEXT_WHITE)
            self.screen.blit(
                txt_surf,
                (bx + 40, btn_y + (btn_h - txt_surf.get_height()) // 2)
            )
            self.clickable_buttons[key] = btn_rect

        # Pistas visuales si están activas
        if self.showHint and self.hint:
            from_t, to_t = self.hint
            hint_str = f"Sugerencia: Mueve de Tubo {from_t + 1} a Tubo {to_t + 1}"
            hint_surf = self.font_btn.render(hint_str, True, ACCENT_GOLD)
            
            pill_w = hint_surf.get_width() + 50
            pill_h = 34
            pill_x = self.width // 2 - pill_w // 2
            pill_y = bar_y + bar_h + 12
            
            p_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pygame.draw.rect(p_surf, (20, 30, 45, 225), (0, 0, pill_w, pill_h), border_radius=17)
            pygame.draw.rect(p_surf, (ACCENT_GOLD[0], ACCENT_GOLD[1], ACCENT_GOLD[2], 190), (0, 0, pill_w, pill_h), 2, border_radius=17)
            self.screen.blit(p_surf, (pill_x, pill_y))
            draw_vector_icon(self.screen, 'hint', pill_x + 22, pill_y + pill_h // 2, ACCENT_GOLD)
            self.screen.blit(hint_surf, (pill_x + 38, pill_y + 6))

        if self.showAuto:
            auto_str = f"Auto-resolución en curso ({self.currAlg})..."
            auto_surf = self.font_btn.render(auto_str, True, ACCENT_CYAN)
            self.screen.blit(auto_surf, (self.width // 2 - auto_surf.get_width() // 2, self.height - 50))

        if self.noSols:
            no_sol_surf = self.font_btn.render("No se encontró solución desde esta posición. ¡Prueba Deshacer!", True, (255, 107, 107))
            self.screen.blit(no_sol_surf, (self.width // 2 - no_sol_surf.get_width() // 2, self.height - 50))

    def drawVictoryModal(self):
        """Muestra una tarjeta modal animada cuando se gana el nivel."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 175))
        self.screen.blit(overlay, (0, 0))

        modal_w = 460
        modal_h = 320
        modal_x = (self.width - modal_w) // 2
        modal_y = (self.height - modal_h) // 2

        # Sombra del modal
        shadow_surf = pygame.Surface((modal_w + 30, modal_h + 30), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (0, 0, modal_w + 30, modal_h + 30), border_radius=25)
        self.screen.blit(shadow_surf, (modal_x - 15, modal_y - 15))

        # Tarjeta modal
        card_surf = pygame.Surface((modal_w, modal_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (25, 33, 48, 245), (0, 0, modal_w, modal_h), border_radius=20)
        pygame.draw.rect(card_surf, (ACCENT_GOLD[0], ACCENT_GOLD[1], ACCENT_GOLD[2], 200), (0, 0, modal_w, modal_h), 3, border_radius=20)
        self.screen.blit(card_surf, (modal_x, modal_y))

        is_game_finished = (self.currentLevel >= len(self.levels) - 1)

        # 3 Estrellas vectoriales doradas
        draw_vector_star(self.screen, self.width // 2 - 45, modal_y + 38, 14, ACCENT_GOLD)
        draw_vector_star(self.screen, self.width // 2, modal_y + 32, 19, ACCENT_GOLD)
        draw_vector_star(self.screen, self.width // 2 + 45, modal_y + 38, 14, ACCENT_GOLD)

        # Título
        title_str = "¡JUEGO COMPLETADO!" if is_game_finished else "¡NIVEL COMPLETADO!"
        title_surf = self.font_title.render(title_str, True, TEXT_WHITE)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, modal_y + 70))

        # Detalles
        moves_info = f"Completado en {self.game.nMoves} movimientos"
        info_surf = self.font_sub.render(moves_info, True, TEXT_MUTED)
        self.screen.blit(info_surf, (self.width // 2 - info_surf.get_width() // 2, modal_y + 120))

        # Botones del modal
        mouse_pos = pygame.mouse.get_pos()
        self.clickable_buttons['modal_next'] = None
        self.clickable_buttons['modal_replay'] = None
        self.clickable_buttons['modal_menu'] = None

        if not is_game_finished:
            # Botón Siguiente Nivel
            next_w, next_h = 240, 48
            next_rect = pygame.Rect(self.width // 2 - next_w // 2, modal_y + 170, next_w, next_h)
            is_hover_n = next_rect.collidepoint(mouse_pos)
            col_n = (46, 204, 113) if is_hover_n else (39, 174, 96)
            pygame.draw.rect(self.screen, col_n, next_rect, border_radius=12)
            pygame.draw.rect(self.screen, (255, 255, 255, 120 if is_hover_n else 60), next_rect, 2, border_radius=12)
            
            n_txt = self.font_btn.render("Siguiente Nivel", True, TEXT_WHITE)
            self.screen.blit(n_txt, (next_rect.centerx - n_txt.get_width() // 2 - 10, next_rect.centery - n_txt.get_height() // 2))
            draw_vector_icon(self.screen, 'next_arrow', next_rect.centerx + n_txt.get_width() // 2 + 8, next_rect.centery, TEXT_WHITE)
            self.clickable_buttons['modal_next'] = next_rect

            # Botón Rejugar
            rep_w, rep_h = 130, 40
            rep_rect = pygame.Rect(self.width // 2 - rep_w - 15, modal_y + 240, rep_w, rep_h)
            is_hover_r = rep_rect.collidepoint(mouse_pos)
            col_r = (52, 73, 94) if is_hover_r else (44, 62, 80)
            pygame.draw.rect(self.screen, col_r, rep_rect, border_radius=10)
            r_txt = self.font_btn.render("Reintentar", True, TEXT_WHITE)
            self.screen.blit(r_txt, (rep_rect.centerx - r_txt.get_width() // 2, rep_rect.centery - r_txt.get_height() // 2))
            self.clickable_buttons['modal_replay'] = rep_rect

            # Botón Menú
            men_w, men_h = 130, 40
            men_rect = pygame.Rect(self.width // 2 + 15, modal_y + 240, men_w, men_h)
            is_hover_m = men_rect.collidepoint(mouse_pos)
            col_m = (52, 73, 94) if is_hover_m else (44, 62, 80)
            pygame.draw.rect(self.screen, col_m, men_rect, border_radius=10)
            m_txt = self.font_btn.render("Menú", True, TEXT_WHITE)
            self.screen.blit(m_txt, (men_rect.centerx - m_txt.get_width() // 2, men_rect.centery - m_txt.get_height() // 2))
            self.clickable_buttons['modal_menu'] = men_rect
        else:
            # Juego terminado por completo
            congrats_txt = self.font_btn.render("¡Has superado todos los desafíos con éxito!", True, ACCENT_GOLD)
            self.screen.blit(congrats_txt, (self.width // 2 - congrats_txt.get_width() // 2, modal_y + 170))

            men_w, men_h = 180, 46
            men_rect = pygame.Rect(self.width // 2 - men_w // 2, modal_y + 230, men_w, men_h)
            is_hover_m = men_rect.collidepoint(mouse_pos)
            col_m = (46, 204, 113) if is_hover_m else (39, 174, 96)
            pygame.draw.rect(self.screen, col_m, men_rect, border_radius=12)
            m_txt = self.font_btn.render("Volver al Menú", True, TEXT_WHITE)
            self.screen.blit(m_txt, (men_rect.centerx - m_txt.get_width() // 2, men_rect.centery - m_txt.get_height() // 2))
            self.clickable_buttons['modal_menu'] = men_rect

    def drawRulesModal(self):
        """Muestra una tarjeta modal interactiva con las reglas fundamentales del juego."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 195))
        self.screen.blit(overlay, (0, 0))

        modal_w = 580
        modal_h = 420
        modal_x = (self.width - modal_w) // 2
        modal_y = (self.height - modal_h) // 2

        # Sombra
        shadow_surf = pygame.Surface((modal_w + 30, modal_h + 30), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 120), (0, 0, modal_w + 30, modal_h + 30), border_radius=25)
        self.screen.blit(shadow_surf, (modal_x - 15, modal_y - 15))

        # Tarjeta modal
        card_surf = pygame.Surface((modal_w, modal_h), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (24, 32, 48, 252), (0, 0, modal_w, modal_h), border_radius=20)
        pygame.draw.rect(card_surf, (142, 68, 173, 230), (0, 0, modal_w, modal_h), 2, border_radius=20)
        self.screen.blit(card_surf, (modal_x, modal_y))

        # Título
        title_surf = self.font_title.render("¿CÓMO SE JUEGA? (REGLAS)", True, TEXT_WHITE)
        self.screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, modal_y + 22))

        # Reglas explicadas con total claridad
        rules = [
            ("1. OBJETIVO", "Agrupar 4 bolas del mismo color en cada tubo para completarlo.", (241, 196, 15)),
            ("2. TUBOS VACÍOS", "Puedes mover cualquier bola a un tubo completamente vacío.", (46, 204, 113)),
            ("3. REGLA DE ORO", "Solo puedes apilar una bola sobre otra del MISMO COLOR.", (52, 152, 219)),
            ("4. NO MEZCLAR", "NO puedes colocar bolas de colores distintos en un mismo tubo.", (231, 76, 60)),
            ("5. BLOQUEO", "Si te quedas sin jugadas, usa 'Deshacer' o pide una 'Pista'.", (155, 89, 182))
        ]

        start_ry = modal_y + 76
        for idx, (head, desc, col) in enumerate(rules):
            ry = start_ry + idx * 52
            head_txt = self.font_btn.render(head + ":", True, col)
            self.screen.blit(head_txt, (modal_x + 35, ry))
            desc_txt = self.font_small.render(desc, True, TEXT_WHITE)
            self.screen.blit(desc_txt, (modal_x + 35, ry + 22))

        # Botón Entendido
        mouse_pos = pygame.mouse.get_pos()
        btn_ok_w, btn_ok_h = 170, 44
        btn_ok_rect = pygame.Rect(self.width // 2 - btn_ok_w // 2, modal_y + modal_h - 60, btn_ok_w, btn_ok_h)
        is_hover_ok = btn_ok_rect.collidepoint(mouse_pos)
        col_ok = (46, 204, 113) if is_hover_ok else (39, 174, 96)
        pygame.draw.rect(self.screen, col_ok, btn_ok_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255, 140 if is_hover_ok else 60), btn_ok_rect, 2, border_radius=12)
        ok_txt = self.font_btn.render("¡Entendido!", True, TEXT_WHITE)
        self.screen.blit(ok_txt, (btn_ok_rect.centerx - ok_txt.get_width() // 2, btn_ok_rect.centery - ok_txt.get_height() // 2))
        self.clickable_buttons['rules_ok'] = btn_ok_rect

    def drawGame(self):
        # Fondo degradado
        self.screen.blit(self.bg_surface, (0, 0))

        # Partículas ambientales
        for star in self.ambient_stars:
            star[1] -= star[3]
            if star[1] < 0:
                star[1] = self.height
                star[0] = random.randint(0, self.width)
            pygame.draw.circle(self.screen, (200, 220, 255, 80), (int(star[0]), int(star[1])), int(star[2]))

        # Barra superior
        self.drawTopBar()

        # Tubos y bolas
        tube_layout = self._get_tube_layout()
        self.tubes_rects = []
        for idx, (tx, ty, tw, th, br) in enumerate(tube_layout):
            rect = self.drawTube(idx, tx, ty, tw, th, br)
            self.tubes_rects.append(rect)

        # Animación de bola en movimiento
        if self.moving_ball:
            layout = tube_layout[0]
            ball_radius = layout[4]
            self.drawBall(
                self.screen,
                int(self.moving_ball.cur_x),
                int(self.moving_ball.cur_y),
                ball_radius,
                self.moving_ball.color_idx
            )
            self.moving_ball.update()
            if self.moving_ball.finished:
                self.moving_ball = None

        # Partículas activas (confeti / destellos)
        for p in self.particles[:]:
            p.update()
            p.draw(self.screen)
            if p.age >= p.lifetime:
                self.particles.remove(p)

        # Chequear tubos recién completados para lanzar chispas y sonido
        for i in range(self.game.ntubes):
            if self.game.completed[i] == 1 and i not in self.completed_tubes_celebrated:
                self.completed_tubes_celebrated.add(i)
                self.sound.play('complete')
                tx, ty, tw, th, br = tube_layout[i]
                for _ in range(18):
                    self.particles.append(SparkleParticle(tx + tw // 2, ty + 20, ACCENT_GOLD))

        # Banner de notificación explicativo de movimiento inválido
        if self.invalid_msg_timer > 0:
            self.invalid_msg_timer -= 1
            msg_surf = self.font_btn.render(self.invalid_msg, True, (255, 120, 120))
            pill_w = msg_surf.get_width() + 40
            pill_h = 36
            pill_x = (self.width - pill_w) // 2
            pill_y = self.height - 90
            
            p_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pygame.draw.rect(p_surf, (35, 20, 25, 235), (0, 0, pill_w, pill_h), border_radius=18)
            pygame.draw.rect(p_surf, (255, 90, 90, 210), (0, 0, pill_w, pill_h), 2, border_radius=18)
            self.screen.blit(p_surf, (pill_x, pill_y))
            self.screen.blit(msg_surf, (pill_x + 20, pill_y + 7))

        # Decrementar temporizador de sacudida de tubo
        if self.shake_timer > 0:
            self.shake_timer -= 1
            if self.shake_timer == 0:
                self.shake_tube = -1

        # Advertencia si el jugador se ha quedado sin movimientos válidos posibles (Deadlock / Sin salida)
        if not self.level_won and not self.game.hasValidMoves():
            deadlock_surf = self.font_btn.render("⚠️ ¡Sin movimientos válidos! Pulsa 'Deshacer' o 'Reiniciar'", True, (255, 190, 80))
            dw_w = deadlock_surf.get_width() + 40
            dw_h = 36
            dw_x = (self.width - dw_w) // 2
            dw_y = self.height - 85
            d_surf = pygame.Surface((dw_w, dw_h), pygame.SRCALPHA)
            pygame.draw.rect(d_surf, (40, 30, 10, 235), (0, 0, dw_w, dw_h), border_radius=18)
            pygame.draw.rect(d_surf, (255, 180, 50, 220), (0, 0, dw_w, dw_h), 2, border_radius=18)
            self.screen.blit(d_surf, (dw_x, dw_y))
            self.screen.blit(deadlock_surf, (dw_x + 20, dw_y + 7))

        # Si el nivel se completó
        if self.level_won:
            if not self.victory_played:
                self.victory_played = True
                self.sound.play('victory')
                # Explotar confeti
                for _ in range(100):
                    self.particles.append(ConfettiParticle(self.width // 2 + random.randint(-200, 200), self.height // 2 - 50))
            self.drawVictoryModal()
        elif self.show_rules:
            self.drawRulesModal()

    def handleMouseClick(self):
        pos = pygame.mouse.get_pos()

        # Si el modal de reglas está abierto
        if self.show_rules:
            if self.clickable_buttons.get('rules_ok') and self.clickable_buttons['rules_ok'].collidepoint(pos):
                self.sound.play('click')
                self.show_rules = False
            return "CONTINUE"

        # Si está activo el modal de victoria
        if self.level_won:
            if self.clickable_buttons.get('modal_next') and self.clickable_buttons['modal_next'].collidepoint(pos):
                self.sound.play('click')
                self.loadNextLevel()
                return "CONTINUE"
            elif self.clickable_buttons.get('modal_replay') and self.clickable_buttons['modal_replay'].collidepoint(pos):
                self.resetLevel()
                return "CONTINUE"
            elif self.clickable_buttons.get('modal_menu') and self.clickable_buttons['modal_menu'].collidepoint(pos):
                self.sound.play('click')
                return "GO_MENU"
            return "CONTINUE"

        # Interacción con botones de la barra superior
        if self.clickable_buttons.get('help') and self.clickable_buttons['help'].collidepoint(pos):
            self.sound.play('click')
            self.show_rules = True
            return "CONTINUE"
        elif self.clickable_buttons.get('hint') and self.clickable_buttons['hint'].collidepoint(pos):
            self.sound.play('click')
            self.updateHint()
            return "CONTINUE"
        elif self.clickable_buttons.get('undo') and self.clickable_buttons['undo'].collidepoint(pos):
            if self.game.undoMove():
                self.sound.play('drop')
            else:
                self.sound.play('invalid')
            self.resetSelection()
            return "CONTINUE"
        elif self.clickable_buttons.get('reset') and self.clickable_buttons['reset'].collidepoint(pos):
            self.resetLevel()
            return "CONTINUE"
        elif self.clickable_buttons.get('menu') and self.clickable_buttons['menu'].collidepoint(pos):
            self.sound.play('click')
            return "GO_MENU"

        # Si una bola ya está en movimiento, ignorar clics hasta que termine
        if self.moving_ball is not None:
            return "CONTINUE"

        # Interacción con los tubos
        for idx, tube_rect in enumerate(self.tubes_rects):
            if tube_rect.collidepoint(pos):
                # Caso 1: Ningún tubo seleccionado actualmente
                if not self.tubeSelected:
                    # Bug fix 1: No permitir seleccionar tubos vacíos
                    if len(self.game.arrTotal[idx]) == 0:
                        self.sound.play('invalid')
                        return "CONTINUE"
                    # Bug fix 2: No permitir mover bolas de un tubo ya completado
                    if self.game.completed[idx] == 1:
                        self.sound.play('invalid')
                        return "CONTINUE"

                    self.fromTube = idx
                    self.tubeSelected = True
                    self.sound.play('pop')
                    return "CONTINUE"

                # Caso 2: Un tubo ya estaba seleccionado
                else:
                    # Si hace clic en el mismo tubo, deseleccionar suavemente
                    if idx == self.fromTube:
                        self.resetSelection()
                        self.sound.play('drop')
                        return "CONTINUE"

                    # Intentar mover al tubo destino
                    if self.game.validMove(self.fromTube, idx):
                        # Configurar animación de movimiento suave
                        self._start_ball_transfer(self.fromTube, idx)
                        return "CONTINUE"
                    else:
                        # Movimiento inválido: diagnosticar motivo y notificar claramente
                        if len(self.game.arrTotal[idx]) >= self.game.m:
                            self.trigger_invalid("¡Ese tubo ya está lleno!", idx)
                        elif len(self.game.arrTotal[idx]) > 0 and self.game.arrTotal[self.fromTube][-1] != self.game.arrTotal[idx][-1]:
                            self.trigger_invalid("¡Colores distintos! Solo apila sobre bolas del mismo color o tubo vacío", idx)
                        else:
                            self.trigger_invalid("¡Movimiento no permitido!", idx)
                        return "CONTINUE"

        # Clic fuera de los tubos: deseleccionar
        if self.tubeSelected:
            self.resetSelection()
            self.sound.play('drop')

        return "CONTINUE"

    def trigger_invalid(self, message, tube_idx):
        """Activa retroalimentación de jugada inválida con mensaje, sacudida y sonido."""
        self.invalid_msg = message
        self.invalid_msg_timer = 90
        self.shake_tube = tube_idx
        self.shake_timer = 16
        self.sound.play('invalid')
        self.resetSelection()

    def _start_ball_transfer(self, from_tube, to_tube):
        """Inicia la animación de traslación de bola entre tubos."""
        tube_layout = self._get_tube_layout()
        from_x, from_y, from_w, from_h, ball_r = tube_layout[from_tube]
        to_x, to_y, to_w, to_h, _ = tube_layout[to_tube]

        # Posición de inicio (bola flotando en la boca del tubo origen)
        start_x = from_x + from_w // 2
        start_y = from_y - 50

        # Posición final (en el slot correspondiente del tubo destino)
        dest_balls_count = len(self.game.arrTotal[to_tube])
        dest_bottom_y = to_y + to_h - ball_r - 8
        ball_spacing = ball_r * 2 + 4
        dest_y = dest_bottom_y - (dest_balls_count * ball_spacing)
        dest_x = to_x + to_w // 2

        # Quitar la bola del tubo de origen INMEDIATAMENTE para evitar duplicados visuales en pantalla
        color_num = self.game.arrTotal[from_tube].pop(-1)
        self.game.fillCompleted(from_tube)

        def on_land():
            self.game.arrTotal[to_tube].append(color_num)
            self.game.fillCompleted(to_tube)
            self.game.nMoves += 1
            self.game.history.append((from_tube, to_tube))
            self.sound.play('drop')
            if self.game.gameOver():
                self.level_won = True

        self.moving_ball = MovingBall(color_num, (start_x, start_y), (dest_x, dest_y), on_land)
        self.resetSelection()

    def updateHint(self):
        self.showHint = True
        self.noSols = False
        root = Node(
            None,
            [list(c) for c in self.game.arrTotal],
            list(self.game.completed),
            self.game.n,
            self.game.m,
            self.game.ntubes,
            (-1, -1), 0, 0
        )
        graph1 = Graph(root)
        hint = graph1.getHint(root, self.solver)
        if hint is None or hint == -1:
            self.noSols = True
            self.hint = None
        else:
            self.hint = hint

    def autoSolve(self, solver_type):
        self.showAuto = True
        self.noSols = False
        self.resetSelection()

        root = Node(
            None,
            [list(c) for c in self.game.arrTotal],
            list(self.game.completed),
            self.game.n,
            self.game.m,
            self.game.ntubes,
            (-1, -1), 0, 0
        )
        graph1 = Graph(root)
        solution = graph1.getAutoSolve(root, solver_type)

        if not solution:
            self.noSols = True
            self.showAuto = False
            return

        # Ejecutar solución de forma fluida bombeando eventos para evitar que la ventana se congele
        clock = pygame.time.Clock()
        for from_col, to_col in solution:
            # Procesar eventos para evitar congelamiento de Windows
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.showAuto = False
                    return
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.showAuto = False
                    return

            self._start_ball_transfer(from_col, to_col)
            # Esperar a que la animación de la bola termine
            while self.moving_ball is not None:
                self.update()
                clock.tick(60)

            # Pequeña pausa entre movimientos para visualización agradable
            for _ in range(8):
                self.update()
                clock.tick(60)

        self.showAuto = False

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                res = self.handleMouseClick()
                if res == "GO_MENU":
                    return "GO_MENU"

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "GO_MENU"
                elif event.key == K_h:
                    self.updateHint()
                elif event.key == K_u:
                    if self.game.undoMove():
                        self.sound.play('drop')
                    else:
                        self.sound.play('invalid')
                    self.resetSelection()
                elif event.key == K_r:
                    self.resetLevel()
                elif event.key == K_a or event.key == K_1:
                    self.currAlg = "A*"
                    self.autoSolve(1)
                elif event.key == K_2:
                    self.currAlg = "Greedy"
                    self.autoSolve(2)
                elif event.key == K_3:
                    self.currAlg = "DFS"
                    self.autoSolve(3)
                elif event.key == K_4:
                    self.currAlg = "BFS"
                    self.autoSolve(4)
                elif event.key == K_5:
                    self.currAlg = "Uniform Cost"
                    self.autoSolve(5)
                elif event.key == K_6:
                    self.currAlg = "Iterative Deepening"
                    self.autoSolve(6)
                elif event.key == K_7:
                    self.currAlg = "Limited Depth"
                    self.autoSolve(7)
                elif event.key == K_d:
                    self.noSols = False
                    self.loadNextLevel()

            elif event.type == QUIT:
                return "EXIT_GAME"
        return "CONTINUE"

    def update(self):
        self.drawGame()
        pygame.display.flip()

        # Si el nivel se completa durante el gameplay regular
        if self.game.gameOver() and not self.level_won:
            self.level_won = True

        return "CONTINUE"
