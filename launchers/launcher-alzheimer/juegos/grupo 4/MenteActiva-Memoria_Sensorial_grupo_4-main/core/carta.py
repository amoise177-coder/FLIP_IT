"""
MenteActiva — Clase Carta
Encapsula el estado, la animación de volteo y el renderizado de cada ficha del tablero.
"""
import math
from enum import Enum
import pygame

from config import (
    Colors, CARD_BORDER_RADIUS, CARD_FLIP_FRAMES,
    HINT_GLOW_SPEED,
)
from utils.icon_drawer import draw_icon


class EstadoCarta(Enum):
    """Estados posibles de una carta."""
    OCULTA = "oculta"             # Boca abajo
    VOLTEANDO_IDA = "volteando_ida"   # Animándose hacia cara visible
    VOLTEANDO_VUELTA = "volteando_vuelta"  # Animándose hacia oculta
    VISIBLE = "visible"           # Boca arriba (temporalmente)
    EMPAREJADA = "emparejada"     # Ya encontró su par (permanece visible)


class Carta:
    """
    Representa una ficha del juego de memoria.

    Atributos:
        pair_id (int):        Identificador de pareja (0..n_pairs-1).
        icon_name (str):      Nombre del ícono a dibujar.
        theme_color (tuple):  Color del tema para el ícono.
        estado (EstadoCarta): Estado actual de la carta.
        rect (pygame.Rect):   Área ocupada en pantalla.
    """

    def __init__(self, pair_id, icon_name, theme_color, rect=None):
        self._pair_id = pair_id
        self._icon_name = icon_name
        self._theme_color = theme_color
        self._estado = EstadoCarta.OCULTA
        self._rect = rect or pygame.Rect(0, 0, 100, 100)

        # ── Animación de volteo ──
        self._flip_progress = 0.0   # 0 = oculta, 1 = visible
        self._flip_speed = 1.0 / max(CARD_FLIP_FRAMES, 1)

        # ── Efectos de pista ──
        self._glow_active = False
        self._glow_timer = 0.0
        self._hint_reveal = False
        self._hint_reveal_timer = 0.0

        # ── Selección por teclado ──
        self._keyboard_selected = False

        # ── Animación de éxito ──
        self._success_scale = 0.0
        self._seen = False  # ¿Ha sido vista alguna vez?

    # ── Propiedades (encapsulamiento) ──────────────────────────────────────

    @property
    def pair_id(self):
        return self._pair_id

    @property
    def icon_name(self):
        return self._icon_name

    @property
    def estado(self):
        return self._estado

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value

    @property
    def seen(self):
        return self._seen

    @property
    def is_face_up(self):
        """¿La carta muestra su cara (visible o emparejada)?"""
        return self._estado in (EstadoCarta.VISIBLE, EstadoCarta.EMPAREJADA)

    @property
    def is_clickable(self):
        """¿Se puede hacer clic sobre esta carta?"""
        return self._estado == EstadoCarta.OCULTA

    @property
    def is_animating(self):
        """¿Está en medio de una animación de volteo?"""
        return self._estado in (EstadoCarta.VOLTEANDO_IDA, EstadoCarta.VOLTEANDO_VUELTA)

    @property
    def keyboard_selected(self):
        return self._keyboard_selected

    @keyboard_selected.setter
    def keyboard_selected(self, value):
        self._keyboard_selected = value

    # ── Acciones ──────────────────────────────────────────────────────────

    def voltear(self):
        """Inicia la animación de volteo (oculta → visible)."""
        if self._estado == EstadoCarta.OCULTA:
            self._estado = EstadoCarta.VOLTEANDO_IDA
            self._seen = True

    def ocultar(self):
        """Inicia la animación de regreso (visible → oculta)."""
        if self._estado == EstadoCarta.VISIBLE:
            self._estado = EstadoCarta.VOLTEANDO_VUELTA

    def emparejar(self):
        """Marca la carta como emparejada (permanece visible)."""
        self._estado = EstadoCarta.EMPAREJADA
        self._success_scale = 1.0
        self._glow_active = False

    def forzar_visible(self):
        """Muestra la carta inmediatamente (para previsualización)."""
        self._estado = EstadoCarta.VISIBLE
        self._flip_progress = 1.0
        self._seen = True

    def forzar_oculta(self):
        """Oculta la carta inmediatamente."""
        self._estado = EstadoCarta.OCULTA
        self._flip_progress = 0.0

    def reset(self):
        """Reinicia la carta a su estado inicial."""
        self._estado = EstadoCarta.OCULTA
        self._flip_progress = 0.0
        self._glow_active = False
        self._glow_timer = 0.0
        self._hint_reveal = False
        self._hint_reveal_timer = 0.0
        self._success_scale = 0.0
        self._seen = False

    # ── Pistas ────────────────────────────────────────────────────────────

    def activar_glow(self):
        """Activa el efecto de brillo dorado pulsante (Pista N1)."""
        self._glow_active = True

    def desactivar_glow(self):
        """Desactiva el efecto de brillo."""
        self._glow_active = False
        self._glow_timer = 0.0

    def activar_hint_reveal(self, duration):
        """Activa la revelación temporal (Pista N3)."""
        self._hint_reveal = True
        self._hint_reveal_timer = duration
        if self._estado == EstadoCarta.OCULTA:
            self._estado = EstadoCarta.VOLTEANDO_IDA

    # ── Interacción ───────────────────────────────────────────────────────

    def contiene_punto(self, pos):
        """Verifica si un punto (x, y) está dentro del área de la carta."""
        return self._rect.collidepoint(pos)

    # ── Actualización ─────────────────────────────────────────────────────

    def actualizar(self, dt):
        """
        Actualiza las animaciones de la carta.
        dt: tiempo transcurrido en segundos desde el último frame.
        """
        # Animación de volteo
        if self._estado == EstadoCarta.VOLTEANDO_IDA:
            self._flip_progress += self._flip_speed
            if self._flip_progress >= 1.0:
                self._flip_progress = 1.0
                self._estado = EstadoCarta.VISIBLE

        elif self._estado == EstadoCarta.VOLTEANDO_VUELTA:
            self._flip_progress -= self._flip_speed
            if self._flip_progress <= 0.0:
                self._flip_progress = 0.0
                self._estado = EstadoCarta.OCULTA

        # Glow pulsante
        if self._glow_active:
            self._glow_timer += dt * HINT_GLOW_SPEED

        # Animación de éxito
        if self._success_scale > 0:
            self._success_scale = max(0, self._success_scale - dt * 2.0)

        # Revelación temporal por pista
        if self._hint_reveal:
            self._hint_reveal_timer -= dt
            if self._hint_reveal_timer <= 0:
                self._hint_reveal = False
                self._hint_reveal_timer = 0.0
                if self._estado == EstadoCarta.VISIBLE:
                    self.ocultar()

    # ── Renderizado ───────────────────────────────────────────────────────

    def dibujar(self, surface):
        """Dibuja la carta en la superficie proporcionada."""
        rect = self._rect

        # ── Escala horizontal para simular volteo 3D ──
        if self._estado in (EstadoCarta.VOLTEANDO_IDA, EstadoCarta.VOLTEANDO_VUELTA):
            if self._flip_progress < 0.5:
                # Mostrando dorso, encogiéndose
                width_scale = 1.0 - self._flip_progress * 2
                self._draw_back(surface, rect, width_scale)
            else:
                # Mostrando frente, expandiéndose
                width_scale = (self._flip_progress - 0.5) * 2
                self._draw_front(surface, rect, width_scale)
        elif self._estado == EstadoCarta.OCULTA:
            self._draw_back(surface, rect, 1.0)
        elif self._estado in (EstadoCarta.VISIBLE, EstadoCarta.EMPAREJADA):
            self._draw_front(surface, rect, 1.0)

        # ── Efecto de éxito ──
        if self._success_scale > 0 and self._estado == EstadoCarta.EMPAREJADA:
            self._draw_success_ring(surface, rect)

        # ── Borde de emparejamiento ──
        if self._estado == EstadoCarta.EMPAREJADA:
            pygame.draw.rect(surface, Colors.SUCCESS, rect, 3, CARD_BORDER_RADIUS)

        # ── Glow de pista (Pista N1) ──
        if self._glow_active and self._estado == EstadoCarta.OCULTA:
            self._draw_glow(surface, rect)

        # ── Selección por teclado ──
        if self._keyboard_selected:
            pygame.draw.rect(surface, Colors.SKY_BLUE, rect.inflate(6, 6), 3, CARD_BORDER_RADIUS)

    def _draw_back(self, surface, rect, width_scale):
        """Dibuja el dorso de la carta (escala horizontal para volteo)."""
        if width_scale <= 0.02:
            return

        w = int(rect.width * width_scale)
        x = rect.centerx - w // 2
        scaled_rect = pygame.Rect(x, rect.y, w, rect.height)

        # Sombra
        shadow_rect = scaled_rect.move(3, 3)
        pygame.draw.rect(surface, Colors.CARD_SHADOW, shadow_rect, border_radius=CARD_BORDER_RADIUS)

        # Dorso
        pygame.draw.rect(surface, Colors.CARD_BACK, scaled_rect, border_radius=CARD_BORDER_RADIUS)

        # Patrón decorativo (rombo central)
        if w > 30:
            cx, cy = scaled_rect.center
            d = min(w, rect.height) // 4
            diamond = [(cx, cy - d), (cx + d, cy), (cx, cy + d), (cx - d, cy)]
            pygame.draw.polygon(surface, Colors.LAVENDER, diamond)
            pygame.draw.polygon(surface, Colors.CARD_SHADOW, diamond, 2)

    def _draw_front(self, surface, rect, width_scale):
        """Dibuja la cara frontal de la carta con su ícono."""
        if width_scale <= 0.02:
            return

        w = int(rect.width * width_scale)
        x = rect.centerx - w // 2
        scaled_rect = pygame.Rect(x, rect.y, w, rect.height)

        # Sombra
        shadow_rect = scaled_rect.move(3, 3)
        pygame.draw.rect(surface, Colors.CARD_SHADOW, shadow_rect, border_radius=CARD_BORDER_RADIUS)

        # Fondo blanco
        pygame.draw.rect(surface, Colors.WHITE, scaled_rect, border_radius=CARD_BORDER_RADIUS)

        # Borde sutil
        pygame.draw.rect(surface, (220, 215, 230), scaled_rect, 2, CARD_BORDER_RADIUS)

        # Ícono (solo si hay suficiente ancho)
        if w > rect.width * 0.5:
            icon_size = min(w, rect.height) // 3
            draw_icon(surface, self._icon_name,
                      scaled_rect.centerx, scaled_rect.centery,
                      icon_size, self._theme_color)

    def _draw_glow(self, surface, rect):
        """Dibuja el efecto de brillo dorado pulsante (Pista N1)."""
        # Intensidad pulsante (0 a 1)
        intensity = (math.sin(self._glow_timer * math.pi) + 1) / 2
        border_width = int(4 + intensity * 6)
        alpha = int(180 + intensity * 75)

        # Crear superficie con alpha para el resplandor — más grande y brillante
        glow_surf = pygame.Surface((rect.width + 24, rect.height + 24), pygame.SRCALPHA)
        glow_rect = pygame.Rect(4, 4, rect.width + 16, rect.height + 16)
        glow_color = (255, 220, 0, alpha)  # Amarillo brillante con alpha alto
        pygame.draw.rect(glow_surf, glow_color, glow_rect, border_width, CARD_BORDER_RADIUS + 4)

        surface.blit(glow_surf, (rect.x - 12, rect.y - 12))

    def _draw_success_ring(self, surface, rect):
        """Dibuja un anillo de éxito expandiéndose."""
        scale = self._success_scale
        expand = int(scale * 20)
        alpha = int(scale * 200)
        ring_surf = pygame.Surface((rect.width + expand * 2 + 4, rect.height + expand * 2 + 4),
                                   pygame.SRCALPHA)
        ring_rect = pygame.Rect(2, 2, rect.width + expand * 2, rect.height + expand * 2)
        pygame.draw.rect(ring_surf, (*Colors.SUCCESS, alpha), ring_rect, 3, CARD_BORDER_RADIUS + 4)
        surface.blit(ring_surf, (rect.x - expand - 2, rect.y - expand - 2))

    def __repr__(self):
        return f"Carta(pair={self._pair_id}, icon={self._icon_name}, estado={self._estado.value})"
