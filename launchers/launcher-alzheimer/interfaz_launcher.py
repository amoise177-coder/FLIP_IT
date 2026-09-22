#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Recreativo — interfaz del launcher (Enfócate)
======================================================

Interfaz visual (menú + pantalla de selección) para el launcher que
correrá los juegos en Python de la materia. Este archivo SOLO dibuja
y anima la interfaz: no carga ni ejecuta juegos reales todavía. Está
pensado para que luego se conecte con el launcher "enfocate"
(GameBase / GameMetadata / COLORS) sin tener que rehacer el diseño.

Pensado para niños con TDAH:
  - Colores vivos pero NO puros/saturados al 100% (menos carga visual).
  - Movimiento continuo y suave (nada de parpadeos ni flashes bruscos).
  - Pocos elementos por pantalla, bien grandes y con mucho espacio.
  - Un único botón de acción claro en cada pantalla.
  - Tipografías redondeadas y amigables (Fredoka / Baloo 2 / Bubblegum
    Sans, todas de Google Fonts, licencia SIL Open Font License).

Cómo ejecutarlo:
    pip install pygame
    python3 interfaz_launcher.py

Controles:
    - Clic en "¡EMPEZAR!" -> pantalla de selección de juegos.
    - Clic en "Volver"    -> regresa al menú principal.
    - ESC o cerrar la ventana -> salir.
"""

import os
import sys

# --- Modo "capturas": renderiza fotogramas fijos sin abrir una ventana
# real (se usa solo para verificar visualmente el diseño). No afecta el
# uso normal del programa.
MODO_CAPTURAS = "--capturas" in sys.argv
if MODO_CAPTURAS:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import random

import pygame

# ---------------------------------------------------------------------------
# Configuración general
# ---------------------------------------------------------------------------

ANCHO, ALTO = 1280, 720
FPS = 60

CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_FUENTES = os.path.join(CARPETA_BASE, "assets", "fonts")

# --- Paleta de colores: vivos pero suavizados (nada de RGB puro) ----------

FONDO_ARRIBA = (255, 246, 219)      # crema cálido
FONDO_ABAJO = (196, 233, 249)       # celeste suave

PALETA_TITULO = [
    (255, 111, 129),   # coral
    (255, 165, 89),    # naranja durazno
    (255, 209, 102),   # amarillo sol
    (120, 200, 150),   # verde menta
    (86, 190, 200),    # turquesa
    (158, 140, 214),   # violeta suave
]

PALETA_DECORACION = [
    (255, 179, 186, 150),
    (255, 223, 154, 150),
    (186, 230, 209, 150),
    (162, 216, 224, 150),
    (196, 181, 232, 150),
]

COLOR_SUBTITULO = (94, 84, 120)          # violeta oscuro suave (buen contraste)
COLOR_TEXTO_OSCURO = (66, 60, 90)

COLOR_BOTON = (86, 199, 165)
COLOR_BOTON_HOVER = (108, 214, 181)
COLOR_BOTON_SOMBRA = (52, 148, 122)
COLOR_TEXTO_BOTON = (255, 255, 255)

COLOR_TARJETA = (255, 255, 255)
COLOR_TARJETA_BORDE = (230, 224, 245)
COLOR_TARJETA_SOMBRA = (210, 205, 225)

COLOR_LOGO = (108, 92, 160)

# ---------------------------------------------------------------------------
# Utilidades de dibujo
# ---------------------------------------------------------------------------


def cargar_fuente(nombre_archivo, tamano):
    """Carga una fuente del proyecto; si falla, usa una del sistema."""
    ruta = os.path.join(CARPETA_FUENTES, nombre_archivo)
    try:
        return pygame.font.Font(ruta, tamano)
    except (FileNotFoundError, OSError):
        return pygame.font.SysFont("comicsansms,arial", tamano, bold=True)


def crear_fondo_degradado(ancho, alto, color_arriba, color_abajo):
    """Genera una sola vez la superficie con el degradado de fondo."""
    superficie = pygame.Surface((ancho, alto))
    for y in range(alto):
        t = y / max(alto - 1, 1)
        color = tuple(
            int(color_arriba[i] + (color_abajo[i] - color_arriba[i]) * t)
            for i in range(3)
        )
        pygame.draw.line(superficie, color, (0, y), (ancho, y))
    return superficie


def dibujar_estrella(superficie, centro, radio_externo, radio_interno, color):
    puntos = []
    for i in range(10):
        angulo = math.pi / 5 * i - math.pi / 2
        radio = radio_externo if i % 2 == 0 else radio_interno
        puntos.append(
            (centro[0] + math.cos(angulo) * radio, centro[1] + math.sin(angulo) * radio)
        )
    pygame.draw.polygon(superficie, color, puntos)


def dibujar_rect_redondeado_sombra(superficie, rect, radio, color, color_sombra, desplazamiento=6):
    sombra = rect.copy()
    sombra.x += desplazamiento
    sombra.y += desplazamiento
    pygame.draw.rect(superficie, color_sombra, sombra, border_radius=radio)
    pygame.draw.rect(superficie, color, rect, border_radius=radio)


def dibujar_palabra_animada(superficie, texto, fuente, x_centro, y_centro, paleta, t,
                              amplitud=7, velocidad=2.4, espacio_extra=3, sombra=True):
    """Dibuja una palabra letra por letra, cada una con su color y un
    suave rebote vertical (sin parpadeos, movimiento continuo)."""
    anchos = [fuente.size(ch)[0] for ch in texto]
    ancho_total = sum(anchos) + espacio_extra * (len(texto) - 1)
    x = x_centro - ancho_total / 2

    for i, ch in enumerate(texto):
        color = paleta[i % len(paleta)]
        offset_y = math.sin(t * velocidad + i * 0.5) * amplitud
        superficie_letra = fuente.render(ch, True, color)
        pos_y = y_centro - superficie_letra.get_height() / 2 + offset_y

        if sombra and ch != " ":
            sombra_letra = fuente.render(ch, True, (0, 0, 0))
            sombra_letra.set_alpha(35)
            superficie.blit(sombra_letra, (x + 3, pos_y + 5))

        superficie.blit(superficie_letra, (x, pos_y))
        x += anchos[i] + espacio_extra


# ---------------------------------------------------------------------------
# Elementos decorativos flotantes (burbujas / estrellas de fondo)
# ---------------------------------------------------------------------------


class Decoracion:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self._reiniciar(y_aleatoria=True)

    def _reiniciar(self, y_aleatoria=False):
        self.x = random.uniform(20, self.ancho - 20)
        self.y = random.uniform(0, self.alto) if y_aleatoria else self.alto + 40
        self.radio = random.uniform(9, 26)
        self.velocidad = random.uniform(10, 24)
        self.fase = random.uniform(0, math.tau)
        self.amplitud_x = random.uniform(8, 24)
        self.color = random.choice(PALETA_DECORACION)
        self.tipo = random.choice(("circulo", "circulo", "estrella"))

    def actualizar(self, dt):
        self.y -= self.velocidad * dt
        if self.y < -40:
            self._reiniciar()

    def dibujar(self, superficie, t):
        x = self.x + math.sin(t * 0.5 + self.fase) * self.amplitud_x
        y = self.y
        tam = int(self.radio * 2 + 4)
        capa = pygame.Surface((tam, tam), pygame.SRCALPHA)
        centro = (tam / 2, tam / 2)
        if self.tipo == "circulo":
            pygame.draw.circle(capa, self.color, centro, self.radio)
        else:
            dibujar_estrella(capa, centro, self.radio, self.radio * 0.45, self.color)
        superficie.blit(capa, (x - tam / 2, y - tam / 2))


# ---------------------------------------------------------------------------
# Botón redondeado con animación de "respiración" y hover
# ---------------------------------------------------------------------------


class Boton:
    def __init__(self, centro, tamano, texto, fuente):
        ancho, alto = tamano
        self.rect_base = pygame.Rect(0, 0, ancho, alto)
        self.rect_base.center = centro
        self.texto = texto
        self.fuente = fuente

    def _rect_actual(self, t, hover):
        escala = 1.0 + math.sin(t * 2.1) * 0.018 + (0.035 if hover else 0.0)
        ancho = int(self.rect_base.width * escala)
        alto = int(self.rect_base.height * escala)
        rect = pygame.Rect(0, 0, ancho, alto)
        rect.center = self.rect_base.center
        return rect

    def contiene(self, pos):
        return self.rect_base.collidepoint(pos)

    def dibujar(self, superficie, t, mouse_pos):
        hover = self.contiene(mouse_pos)
        rect = self._rect_actual(t, hover)
        color = COLOR_BOTON_HOVER if hover else COLOR_BOTON
        radio = rect.height // 2
        dibujar_rect_redondeado_sombra(superficie, rect, radio, color, COLOR_BOTON_SOMBRA, 7)

        texto_superficie = self.fuente.render(self.texto, True, COLOR_TEXTO_BOTON)
        texto_rect = texto_superficie.get_rect(center=(rect.centerx, rect.centery - 2))
        superficie.blit(texto_superficie, texto_rect)


# ---------------------------------------------------------------------------
# Tarjeta de juego (pantalla de selección) — solo visual, no ejecuta nada
# ---------------------------------------------------------------------------


class TarjetaJuego:
    def __init__(self, rect, titulo, subtitulo, color_icono, tipo_icono, disponible=True):
        self.rect = rect
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.color_icono = color_icono
        self.tipo_icono = tipo_icono
        self.disponible = disponible

    def contiene(self, pos):
        return self.rect.collidepoint(pos)

    def dibujar(self, superficie, t, mouse_pos, fuente_titulo, fuente_sub, indice=0):
        hover = self.disponible and self.contiene(mouse_pos)
        levante = -6 if hover else 0
        bamboleo = math.sin(t * 1.6 + indice * 1.3) * 2  # movimiento suave, siempre presente

        rect = self.rect.move(0, levante + bamboleo)
        alpha_tarjeta = 255 if self.disponible else 235

        capa = pygame.Surface(rect.size, pygame.SRCALPHA)
        rect_local = pygame.Rect(0, 0, rect.width, rect.height)
        sombra_local = rect_local.move(0, 8)
        pygame.draw.rect(capa, (*COLOR_TARJETA_SOMBRA, 120), sombra_local, border_radius=26)
        color_relleno = (*COLOR_TARJETA, alpha_tarjeta) if self.disponible else (245, 243, 250, 235)
        pygame.draw.rect(capa, color_relleno, rect_local, border_radius=26)
        borde_color = COLOR_TARJETA_BORDE if not hover else self.color_icono
        pygame.draw.rect(capa, borde_color, rect_local, width=4, border_radius=26)
        superficie.blit(capa, rect.topleft)

        centro_icono = (rect.centerx, rect.top + 62)
        self._dibujar_icono(superficie, centro_icono, t, indice)

        color_texto = COLOR_TEXTO_OSCURO if self.disponible else (150, 145, 165)
        titulo_superficie = fuente_titulo.render(self.titulo, True, color_texto)
        titulo_rect = titulo_superficie.get_rect(center=(rect.centerx, rect.top + 122))
        superficie.blit(titulo_superficie, titulo_rect)

        sub_superficie = fuente_sub.render(self.subtitulo, True, (150, 145, 165))
        sub_rect = sub_superficie.get_rect(center=(rect.centerx, rect.top + 154))
        superficie.blit(sub_superficie, sub_rect)

    def _dibujar_icono(self, superficie, centro, t, indice):
        cx, cy = centro
        color = self.color_icono

        if self.tipo_icono == "cartas":
            giro = math.sin(t * 1.3 + indice) * 6
            for dx, ang, alpha in ((-10, giro, 255), (10, -giro, 200)):
                capa = pygame.Surface((46, 60), pygame.SRCALPHA)
                pygame.draw.rect(capa, (*color, alpha), (0, 0, 46, 60), border_radius=10)
                pygame.draw.rect(capa, (255, 255, 255, alpha), (8, 10, 30, 40), border_radius=6)
                capa = pygame.transform.rotate(capa, ang)
                rect_capa = capa.get_rect(center=(cx + dx, cy))
                superficie.blit(capa, rect_capa)

        elif self.tipo_icono == "laberinto":
            tam = 56
            rect_fondo = pygame.Rect(0, 0, tam, tam)
            rect_fondo.center = (cx, cy)
            pygame.draw.rect(superficie, color, rect_fondo, border_radius=12)
            paso = tam // 4
            for i in range(1, 4):
                if i % 2 == 1:
                    pygame.draw.line(
                        superficie, (255, 255, 255),
                        (rect_fondo.left + paso * i, rect_fondo.top + 6),
                        (rect_fondo.left + paso * i, rect_fondo.top + paso * 3), 5,
                    )
                else:
                    pygame.draw.line(
                        superficie, (255, 255, 255),
                        (rect_fondo.left + 6, rect_fondo.top + paso * i),
                        (rect_fondo.left + paso * 3, rect_fondo.top + paso * i), 5,
                    )

        else:  # "proximamente"
            pulso = 1.0 + math.sin(t * 2.4) * 0.08
            radio = int(26 * pulso)
            pygame.draw.circle(superficie, color, (cx, cy), radio, width=4)
            pygame.draw.line(superficie, color, (cx - 12, cy), (cx + 12, cy), 5)
            pygame.draw.line(superficie, color, (cx, cy - 12), (cx, cy + 12), 5)


# ---------------------------------------------------------------------------
# Aplicación principal
# ---------------------------------------------------------------------------


class InterfazLauncher:
    ESTADO_MENU = "menu"
    ESTADO_SELECCION = "seleccion"

    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.fondo = crear_fondo_degradado(ANCHO, ALTO, FONDO_ARRIBA, FONDO_ABAJO)

        self.fuente_logo = cargar_fuente("Baloo2-SemiBold.ttf", 24)
        self.fuente_titulo = cargar_fuente("Fredoka-Bold.ttf", 74)
        self.fuente_subtitulo = cargar_fuente("Baloo2-SemiBold.ttf", 32)
        self.fuente_tagline = cargar_fuente("BubblegumSans-Regular.ttf", 22)
        self.fuente_boton = cargar_fuente("Baloo2-ExtraBold.ttf", 30)
        self.fuente_boton_volver = cargar_fuente("Baloo2-SemiBold.ttf", 22)
        self.fuente_titulo_seleccion = cargar_fuente("Fredoka-Bold.ttf", 42)
        self.fuente_tarjeta_titulo = cargar_fuente("Baloo2-ExtraBold.ttf", 24)
        self.fuente_tarjeta_sub = cargar_fuente("Baloo2-SemiBold.ttf", 16)

        self.decoraciones = [Decoracion(ANCHO, ALTO) for _ in range(16)]

        self.boton_empezar = Boton((ANCHO // 2, 470), (300, 84), "¡EMPEZAR!", self.fuente_boton)
        self.boton_volver = Boton((110, 50), (150, 54), "← Volver", self.fuente_boton_volver)

        ancho_tarjeta, alto_tarjeta = 230, 210
        espacio = 40
        total = ancho_tarjeta * 3 + espacio * 2
        x0 = (ANCHO - total) // 2
        y0 = 250
        self.tarjetas = [
            TarjetaJuego(
                pygame.Rect(x0, y0, ancho_tarjeta, alto_tarjeta),
                "MENTE ACTIVA", "Memoria Sensorial",
                (255, 140, 130), "cartas",
            ),
            TarjetaJuego(
                pygame.Rect(x0 + (ancho_tarjeta + espacio), y0, ancho_tarjeta, alto_tarjeta),
                "LETRA A LETRA", "Palabras Cruzadas",
                (98, 190, 200), "laberinto",
            ),
            TarjetaJuego(
                pygame.Rect(x0 + 2 * (ancho_tarjeta + espacio), y0, ancho_tarjeta, alto_tarjeta),
                "Próximamente", "Nuevo juego",
                (176, 165, 210), "proximamente", disponible=False,
            ),
        ]

        self.estado = self.ESTADO_MENU
        self.estado_destino = None
        self.transicionando = False
        self.transicion_t = 0.0
        self.transicion_duracion = 0.55
        self.mensaje_click = None
        self.mensaje_click_t = 0.0

    # -- lógica -------------------------------------------------------

    def iniciar_transicion(self, destino):
        if not self.transicionando:
            self.transicionando = True
            self.transicion_t = 0.0
            self.estado_destino = destino

    def manejar_click(self, pos):
        if self.transicionando:
            return
        if self.estado == self.ESTADO_MENU:
            if self.boton_empezar.contiene(pos):
                self.iniciar_transicion(self.ESTADO_SELECCION)
        else:
            if self.boton_volver.contiene(pos):
                self.iniciar_transicion(self.ESTADO_MENU)
                return
            for tarjeta in self.tarjetas:
                if tarjeta.contiene(pos):
                    if tarjeta.disponible:
                        self.mensaje_click = f"'{tarjeta.titulo}' se abrirá aquí cuando se conecte el juego"
                    else:
                        self.mensaje_click = "Muy pronto habrá más juegos aquí"
                    self.mensaje_click_t = 2.6

    def actualizar(self, dt):
        for decoracion in self.decoraciones:
            decoracion.actualizar(dt)

        if self.transicionando:
            self.transicion_t += dt
            if self.transicion_t >= self.transicion_duracion / 2 and self.estado_destino is not None:
                self.estado = self.estado_destino
                self.estado_destino = None
            if self.transicion_t >= self.transicion_duracion:
                self.transicionando = False
                self.transicion_t = 0.0

        if self.mensaje_click_t > 0:
            self.mensaje_click_t -= dt
            if self.mensaje_click_t <= 0:
                self.mensaje_click = None

    # -- dibujo ---------------------------------------------------------

    def dibujar(self, t, mouse_pos):
        self.pantalla.blit(self.fondo, (0, 0))

        for decoracion in self.decoraciones:
            decoracion.dibujar(self.pantalla, t)

        if self.estado == self.ESTADO_MENU:
            self._dibujar_menu(t, mouse_pos)
        else:
            self._dibujar_seleccion(t, mouse_pos)

        self._dibujar_logo()

        if self.transicionando:
            progreso = self.transicion_t / self.transicion_duracion
            alpha = int(255 * math.sin(progreso * math.pi))
            velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            velo.fill((255, 250, 240, max(alpha, 0)))
            self.pantalla.blit(velo, (0, 0))

    def _dibujar_logo(self):
        # Esquina superior derecha para no chocar nunca con el botón
        # "Volver" de la pantalla de selección (que vive arriba a la izquierda).
        texto = self.fuente_logo.render("enfócate", True, COLOR_LOGO)
        x = ANCHO - texto.get_width() - 34
        y = 20
        self.pantalla.blit(texto, (x, y))
        pygame.draw.circle(self.pantalla, (255, 209, 102), (x - 14, y + 12), 6)

    def _dibujar_menu(self, t, mouse_pos):
        dibujar_palabra_animada(
            self.pantalla, "SISTEMA", self.fuente_titulo, ANCHO // 2, 160,
            PALETA_TITULO, t, amplitud=8, velocidad=2.2,
        )
        dibujar_palabra_animada(
            self.pantalla, "RECREATIVO", self.fuente_titulo, ANCHO // 2, 240,
            PALETA_TITULO[::-1], t, amplitud=8, velocidad=2.2, sombra=True,
        )

        alpha_sub = 200 + int(math.sin(t * 1.4) * 40)
        sub_superficie = self.fuente_subtitulo.render("para niños con TDAH", True, COLOR_SUBTITULO)
        sub_superficie.set_alpha(alpha_sub)
        sub_rect = sub_superficie.get_rect(center=(ANCHO // 2, 310))
        self.pantalla.blit(sub_superficie, sub_rect)

        tagline = self.fuente_tagline.render("¡vamos a jugar y a divertirnos!", True, (120, 108, 150))
        angulo = math.sin(t * 1.1) * 2.5
        tagline_rotada = pygame.transform.rotate(tagline, angulo)
        tagline_rect = tagline_rotada.get_rect(center=(ANCHO // 2, 360))
        self.pantalla.blit(tagline_rotada, tagline_rect)

        self.boton_empezar.dibujar(self.pantalla, t, mouse_pos)

    def _dibujar_seleccion(self, t, mouse_pos):
        dibujar_palabra_animada(
            self.pantalla, "¿QUÉ QUIERES JUGAR?", self.fuente_titulo_seleccion,
            ANCHO // 2, 120, PALETA_TITULO, t, amplitud=5, velocidad=2.0,
        )

        for i, tarjeta in enumerate(self.tarjetas):
            tarjeta.dibujar(
                self.pantalla, t, mouse_pos,
                self.fuente_tarjeta_titulo, self.fuente_tarjeta_sub, indice=i,
            )

        self.boton_volver.dibujar(self.pantalla, t, mouse_pos)

        if self.mensaje_click:
            alpha = min(255, int(255 * min(self.mensaje_click_t, 0.4) / 0.4)) if self.mensaje_click_t < 0.4 else 255
            globo = self.fuente_tarjeta_sub.render(self.mensaje_click, True, (255, 255, 255))
            fondo_rect = globo.get_rect(center=(ANCHO // 2, 520)).inflate(40, 26)
            capa = pygame.Surface(fondo_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(capa, (108, 92, 160, alpha), capa.get_rect(), border_radius=18)
            self.pantalla.blit(capa, fondo_rect.topleft)
            globo.set_alpha(alpha)
            self.pantalla.blit(globo, globo.get_rect(center=fondo_rect.center))


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------


def ejecutar():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
    pygame.display.set_caption("Sistema Recreativo — Enfócate")
    reloj = pygame.time.Clock()

    app = InterfazLauncher(pantalla)
    tiempo = 0.0
    ejecutando = True

    while ejecutando:
        dt = reloj.tick(FPS) / 1000.0
        tiempo += dt

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                ejecutando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                app.manejar_click(evento.pos)

        app.actualizar(dt)
        app.dibujar(tiempo, pygame.mouse.get_pos())
        pygame.display.flip()

    pygame.quit()


def generar_capturas():
    """Renderiza fotogramas fijos a disco para verificar el diseño sin
    necesidad de una pantalla real (uso interno de desarrollo)."""
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    app = InterfazLauncher(pantalla)

    carpeta_salida = os.path.join(CARPETA_BASE, "capturas")
    os.makedirs(carpeta_salida, exist_ok=True)

    # Foto 1: menú, estado inicial
    for _ in range(10):
        app.actualizar(1 / 60)
    app.dibujar(0.4, (-10, -10))
    pygame.image.save(pantalla, os.path.join(carpeta_salida, "01_menu.png"))

    # Foto 2: menú con el mouse sobre el botón (hover)
    app.dibujar(1.2, (ANCHO // 2, 470))
    pygame.image.save(pantalla, os.path.join(carpeta_salida, "02_menu_hover.png"))

    # Foto 3: transición en curso
    app.manejar_click((ANCHO // 2, 470))
    for _ in range(9):
        app.actualizar(1 / 60)
    app.dibujar(1.35, (ANCHO // 2, 470))
    pygame.image.save(pantalla, os.path.join(carpeta_salida, "03_transicion.png"))

    # Completar transición -> pantalla de selección
    for _ in range(30):
        app.actualizar(1 / 60)
    app.dibujar(2.5, (-10, -10))
    pygame.image.save(pantalla, os.path.join(carpeta_salida, "04_seleccion.png"))

    # Foto 5: selección con hover sobre una tarjeta + mensaje de click
    app.manejar_click(app.tarjetas[0].rect.center)
    app.dibujar(2.8, app.tarjetas[0].rect.center)
    pygame.image.save(pantalla, os.path.join(carpeta_salida, "05_seleccion_click.png"))

    pygame.quit()
    print("Capturas guardadas en:", carpeta_salida)


if __name__ == "__main__":
    if MODO_CAPTURAS:
        generar_capturas()
    else:
        ejecutar()
