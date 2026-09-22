"""
Kit visual de FLIP IT: paleta pastel, tipografias, paneles, botones y
tarjetas. Lo usan menu.py, instrucciones.py y src/juego.py para que todas
las pantallas se vean como un mismo producto y no como pantallas sueltas.

Decisiones de diseno pensadas en ninos con TDAH (y que ademas son las que
usan los juegos casuales del mercado):

  - fondo pastel de bajo contraste y elementos interactivos de alto
    contraste: el ojo va directo a lo que se puede tocar
  - pocos elementos por pantalla y siempre en el mismo lugar
  - botones grandes (minimo 56 px de alto) con sombra: se ve que "se pueden
    apretar" antes de leerlos
  - animaciones suaves e interpoladas (nada de parpadeos ni destellos)
  - texto oscuro sobre pastel claro, no blanco sobre color saturado
"""

import pygame

# ---------------------------------------------------------------------
# paleta
# ---------------------------------------------------------------------

TEXTO = (72, 60, 88)
TEXTO_SUAVE = (126, 116, 142)
BLANCO = (255, 255, 255)
PANEL = (255, 255, 255, 214)
PANEL_BORDE = (255, 255, 255, 235)

# cada paleta es (color_arriba, color_abajo)
AZUL = ((176, 219, 248), (116, 172, 224))
VERDE = ((196, 232, 188), (134, 194, 136))
LAVANDA = ((224, 210, 245), (182, 162, 222))
DURAZNO = ((253, 218, 196), (240, 174, 144))
ROSA = ((252, 208, 216), (236, 156, 174))
NEUTRO = ((236, 234, 242), (198, 194, 212))
AMARILLO = ((253, 235, 186), (240, 206, 122))

PALETA_TEMAS = [LAVANDA, AZUL, ROSA, DURAZNO]


# ---------------------------------------------------------------------
# tipografia
# ---------------------------------------------------------------------

_FUENTES_PREFERIDAS = ["Segoe UI", "Trebuchet MS", "Verdana",
                       "DejaVu Sans", "Liberation Sans", "Arial"]
_cache_fuentes = {}


def fuente(tam, negrita=False):
    """Fuente del sistema, con varias alternativas por si el equipo no
    tiene la primera. Se guarda en cache porque crear una fuente en cada
    cuadro tira los FPS al piso."""
    clave = (tam, negrita)
    if clave not in _cache_fuentes:
        f = None
        for nombre in _FUENTES_PREFERIDAS:
            ruta = pygame.font.match_font(nombre, bold=negrita)
            if ruta:
                f = pygame.font.Font(ruta, tam)
                break
        if f is None:
            f = pygame.font.SysFont("arial", tam, bold=negrita)
        _cache_fuentes[clave] = f
    return _cache_fuentes[clave]


def texto_centrado(destino, cadena, f, color, centro, sombra=None):
    if sombra:
        s = f.render(cadena, True, sombra)
        destino.blit(s, s.get_rect(center=(centro[0], centro[1] + 2)))
    surf = f.render(cadena, True, color)
    rect = surf.get_rect(center=centro)
    destino.blit(surf, rect)
    return rect


# ---------------------------------------------------------------------
# superficies reutilizables (todas cacheadas)
# ---------------------------------------------------------------------

_cache_grad = {}
_cache_sombra = {}


def degradado_redondeado(tam, c1, c2, radio):
    """Rectangulo redondeado relleno con un degradado vertical."""
    clave = (tam, c1, c2, radio)
    if clave in _cache_grad:
        return _cache_grad[clave]

    ancho, alto = tam
    grad = pygame.Surface(tam).convert()
    for y in range(alto):
        t = y / max(1, alto - 1)
        color = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        pygame.draw.line(grad, color, (0, y), (ancho, y))

    mascara = pygame.Surface(tam, pygame.SRCALPHA)
    pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=radio)

    salida = pygame.Surface(tam, pygame.SRCALPHA)
    salida.blit(grad, (0, 0))
    salida.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    _cache_grad[clave] = salida
    return salida


def sombra_redondeada(tam, radio, alpha=60, expansion=10, color=(120, 104, 140)):
    """Sombra suave: varios rectangulos redondeados concentricos con poca
    opacidad. pygame no trae desenfoque, y este truco se ve igual de bien
    sin costar rendimiento porque queda en cache."""
    clave = (tam, radio, alpha, expansion, color)
    if clave in _cache_sombra:
        return _cache_sombra[clave]

    ancho, alto = tam
    sup = pygame.Surface((ancho + expansion * 2, alto + expansion * 2), pygame.SRCALPHA)
    capas = max(3, expansion)
    for i in range(capas, 0, -1):
        crecer = int(expansion * i / capas)
        a = int(alpha * (1 - (i - 1) / capas) / capas * 2.2)
        rect = pygame.Rect(expansion - crecer, expansion - crecer,
                           ancho + crecer * 2, alto + crecer * 2)
        pygame.draw.rect(sup, color + (max(1, a),), rect, border_radius=radio + crecer)
    _cache_sombra[clave] = sup
    return sup


def panel(destino, rect, radio=28, relleno=PANEL, con_sombra=True):
    """Tarjeta blanca translucida: el contenedor base de todas las pantallas."""
    if con_sombra:
        s = sombra_redondeada((rect.width, rect.height), radio, alpha=70, expansion=16)
        destino.blit(s, (rect.x - 16, rect.y - 12))
    capa = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(capa, relleno, capa.get_rect(), border_radius=radio)
    pygame.draw.rect(capa, PANEL_BORDE, capa.get_rect(), width=2, border_radius=radio)
    destino.blit(capa, rect.topleft)


def circulo_recortado(imagen, diametro):
    """Devuelve la imagen recortada en circulo, con borde blanco."""
    img = pygame.transform.smoothscale(imagen, (diametro, diametro))
    mascara = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
    pygame.draw.circle(mascara, (255, 255, 255, 255),
                       (diametro // 2, diametro // 2), diametro // 2)
    salida = pygame.Surface((diametro, diametro), pygame.SRCALPHA)
    salida.blit(img, (0, 0))
    salida.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return salida


# ---------------------------------------------------------------------
# controles
# ---------------------------------------------------------------------

class Boton:
    """Boton pastel con relieve: sube un poco y se aclara al pasar el mouse,
    y se hunde al hacer clic. El movimiento es interpolado, nunca brusco."""

    ALTO_MINIMO = 56

    def __init__(self, x, y, ancho, alto, texto, paleta=AZUL, tam_texto=32,
                 radio=None, icono=None):
        alto = max(alto, self.ALTO_MINIMO)
        self.rect = pygame.Rect(0, 0, ancho, alto)
        self.rect.center = (x, y)
        self.texto = texto
        self.paleta = paleta
        self.radio = radio if radio is not None else min(24, alto // 2)
        self.fuente = fuente(tam_texto, negrita=True)
        self.icono = icono
        self.hover = False
        self.presionado = False
        self._elev = 0.0        # 0 = en reposo, 1 = resaltado

    def actualizar(self, mouse_pos, presionando=False):
        self.hover = self.rect.collidepoint(mouse_pos)
        self.presionado = self.hover and presionando
        objetivo = 1.0 if self.hover else 0.0
        self._elev += (objetivo - self._elev) * 0.20
        return self.hover

    def dibujar(self, destino):
        subida = int(self._elev * 4) - (3 if self.presionado else 0)
        rect = self.rect.move(0, -subida)

        sombra = sombra_redondeada((rect.width, rect.height), self.radio,
                                   alpha=70 + int(self._elev * 40),
                                   expansion=10 + int(self._elev * 6))
        exp = 10 + int(self._elev * 6)
        destino.blit(sombra, (rect.x - exp, rect.y - exp + 6 + subida))

        cuerpo = degradado_redondeado((rect.width, rect.height),
                                      self.paleta[0], self.paleta[1], self.radio)
        destino.blit(cuerpo, rect.topleft)

        if self._elev > 0.01:                      # velo claro al pasar el mouse
            velo = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(velo, (255, 255, 255, int(52 * self._elev)),
                             velo.get_rect(), border_radius=self.radio)
            destino.blit(velo, rect.topleft)

        pygame.draw.rect(destino, BLANCO, rect, width=3, border_radius=self.radio)

        cx, cy = rect.center
        if self.icono:
            ico = pygame.transform.smoothscale(self.icono, (rect.height - 22, rect.height - 22))
            destino.blit(ico, ico.get_rect(midleft=(rect.x + 16, cy)))
            cx += (rect.height - 22) // 2
        # el "relieve" blanco debajo del texto lo separa del degradado
        texto_centrado(destino, self.texto, self.fuente, TEXTO, (cx, cy),
                       sombra=BLANCO)


class TarjetaTema:
    """Tarjeta grande para elegir tematica: icono redondo + nombre.
    Es el mismo patron que usan las pantallas de seleccion de personaje de
    los juegos comerciales, y funciona bien porque el nino elige por dibujo,
    no por texto."""

    def __init__(self, x, y, ancho, alto, icono, nombre, paleta=LAVANDA):
        self.rect = pygame.Rect(0, 0, ancho, alto)
        self.rect.center = (x, y)
        self.nombre = nombre
        self.paleta = paleta
        self.diametro = min(ancho - 34, alto - 78)
        self.icono = circulo_recortado(icono, self.diametro)
        self.fuente = fuente(24, negrita=True)
        self.hover = False
        self._elev = 0.0

    def actualizar(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        objetivo = 1.0 if self.hover else 0.0
        self._elev += (objetivo - self._elev) * 0.20
        return self.hover

    def dibujar(self, destino):
        subida = int(self._elev * 8)
        rect = self.rect.move(0, -subida)
        radio = 26

        exp = 14 + int(self._elev * 8)
        destino.blit(sombra_redondeada((rect.width, rect.height), radio,
                                       alpha=80 + int(self._elev * 45), expansion=exp),
                     (rect.x - exp, rect.y - exp + 8 + subida))

        base = degradado_redondeado((rect.width, rect.height),
                                    (255, 255, 255), self.paleta[0], radio)
        destino.blit(base, rect.topleft)
        pygame.draw.rect(destino, BLANCO, rect, width=3, border_radius=radio)

        centro_icono = (rect.centerx, rect.y + 24 + self.diametro // 2)
        aro = self.diametro // 2 + 6 + int(self._elev * 4)
        pygame.draw.circle(destino, self.paleta[1], centro_icono, aro)
        pygame.draw.circle(destino, BLANCO, centro_icono, aro, 4)
        destino.blit(self.icono, self.icono.get_rect(center=centro_icono))

        texto_centrado(destino, self.nombre, self.fuente, TEXTO,
                       (rect.centerx, rect.bottom - 30))


class Insignia:
    """Cajita de datos del HUD (pares encontrados, intentos...)."""

    def __init__(self, x, y, ancho, alto, etiqueta, paleta=NEUTRO):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.etiqueta = etiqueta
        self.paleta = paleta
        self.f_etq = fuente(15, negrita=True)
        self.f_val = fuente(26, negrita=True)

    def dibujar(self, destino, valor):
        destino.blit(sombra_redondeada(self.rect.size, 18, alpha=55, expansion=8),
                     (self.rect.x - 8, self.rect.y - 4))
        destino.blit(degradado_redondeado(self.rect.size, self.paleta[0], self.paleta[1], 18),
                     self.rect.topleft)
        pygame.draw.rect(destino, BLANCO, self.rect, width=2, border_radius=18)
        texto_centrado(destino, self.etiqueta, self.f_etq, TEXTO_SUAVE,
                       (self.rect.centerx, self.rect.y + 17))
        texto_centrado(destino, str(valor), self.f_val, TEXTO,
                       (self.rect.centerx, self.rect.bottom - 22))
