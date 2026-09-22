"""
FLIP IT - juego de memoria.

Modo unico: 6 parejas (12 cartas) en una cuadricula de 4x3 y sin limite de
tiempo. Del menu se sale directo a jugar apenas se elige la tematica.

La partida no tiene pantalla de derrota a proposito: el unico dato que se
lleva la cuenta es el numero de intentos, como referencia para mejorar, y
la unica pantalla final es la de victoria.
"""

import random

import pygame

from enfocate import GameBase, GameMetadata, COLORS

import constantes
import ui
from constantes import MODO, IMG_TEMAS
from audio import play_efecto, reproducir_musica
from menu import ejecutar_menu


# ---------------------------------------------------------------------
# Carta
# ---------------------------------------------------------------------

class Carta:
    """Una carta del tablero.

    id_par identifica la pareja: dos cartas son iguales si comparten id_par
    (antes se comparaban las superficies de pygame, que funciona pero es
    fragil si algun dia las imagenes se cargan por separado).
    """

    def __init__(self, id_par, imagen, x, y, ancho, alto, reverso):
        self.id_par = id_par
        self.imagen = imagen
        self.reverso = reverso
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.ancho_orig, self.alto_orig = ancho, alto

        self.visible = False
        self.emparejada = False
        self.animacion_volteo = None
        self.progreso_volteo = 0.0
        self.celebracion = 0.0      # rebote al formar la pareja
        self.resalte = 0.0          # brillo al pasar el mouse

    # --- estado -------------------------------------------------------

    def clic_en_carta(self, pos):
        return (
            self.rect.collidepoint(pos)
            and not self.visible
            and not self.emparejada
            and self.animacion_volteo is None
        )

    def iniciar_volteo_mostrar(self):
        self.animacion_volteo = "mostrar"
        self.progreso_volteo = 0.0

    def iniciar_volteo_ocultar(self):
        self.animacion_volteo = "ocultar"
        self.progreso_volteo = 0.0

    def marcar_emparejada(self):
        self.emparejada = True
        self.celebracion = 1.0

    def actualizar(self, dt, mouse_pos):
        if self.animacion_volteo is not None:
            self.progreso_volteo += dt / constantes.DURACION_VOLTEO
            if self.progreso_volteo >= 1.0:
                self.progreso_volteo = 0.0
                self.visible = self.animacion_volteo == "mostrar"
                self.animacion_volteo = None

        if self.celebracion > 0:
            self.celebracion = max(0.0, self.celebracion - dt * 2.2)

        activa = (not self.visible and not self.emparejada
                  and self.animacion_volteo is None
                  and self.rect.collidepoint(mouse_pos))
        objetivo = 1.0 if activa else 0.0
        self.resalte += (objetivo - self.resalte) * 0.22

    # --- dibujo -------------------------------------------------------

    def dibujar(self, superficie):
        # el volteo se dibuja aparte: la carta se "adelgaza" y cambia de cara
        if self.animacion_volteo is not None:
            p = min(1.0, max(0.0, self.progreso_volteo))
            escala = abs(1 - 2 * p)          # 1 -> 0 -> 1
            ancho = max(2, int(self.ancho_orig * escala))
            cara = self.imagen if p >= 0.5 else self.reverso
            img = pygame.transform.smoothscale(cara, (ancho, self.alto_orig))
            superficie.blit(img, img.get_rect(center=self.rect.center))
            return

        # rebote corto cuando se acaba de formar la pareja
        escala = 1.0 + 0.10 * self.celebracion * (1 - self.celebracion) * 4
        subida = int(self.resalte * 6)
        rect = self.rect.move(0, -subida)

        if self.emparejada:
            aro = rect.inflate(10, 10)
            pygame.draw.rect(superficie, (150, 206, 160), aro, width=4, border_radius=22)

        sombra = ui.sombra_redondeada(rect.size, 20,
                                      alpha=70 + int(self.resalte * 45),
                                      expansion=10 + int(self.resalte * 6))
        exp = 10 + int(self.resalte * 6)
        superficie.blit(sombra, (rect.x - exp, rect.y - exp + 7 + subida))

        cara = self.imagen if (self.visible or self.emparejada) else self.reverso
        if abs(escala - 1.0) > 0.001:
            tam = (int(self.ancho_orig * escala), int(self.alto_orig * escala))
            cara = pygame.transform.smoothscale(cara, tam)
        superficie.blit(cara, cara.get_rect(center=rect.center))

        if self.resalte > 0.01:
            velo = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(velo, (255, 255, 255, int(58 * self.resalte)),
                             velo.get_rect(), border_radius=20)
            superficie.blit(velo, rect.topleft)


# ---------------------------------------------------------------------
# Armado del tablero
# ---------------------------------------------------------------------

def _directorio_tema(tema):
    """Carpeta de imagenes del tema elegido. Si el nombre no existe (por
    ejemplo si se llama al juego directo, sin pasar por el menu) usa el
    tema por defecto de constantes.py para no romper el arranque."""
    return IMG_TEMAS.get(tema) or IMG_TEMAS[constantes.TEMA_CARTAS]


def _imagenes_del_tema(img_dir):
    """Archivos de imagen de la carpeta del tema, ordenados por numero
    (1, 2, 3...) en vez de por orden alfabetico."""
    if not img_dir.exists():
        return []

    def clave_orden(ruta):
        return (0, int(ruta.stem)) if ruta.stem.isdigit() else (1, ruta.stem)

    archivos = [p for p in img_dir.iterdir()
                if p.suffix.lower() in (".png", ".jpg", ".jpeg")]
    return sorted(archivos, key=clave_orden)


def crear_cartas(tema):
    """Devuelve las 12 cartas del tablero, ya barajadas y colocadas."""
    ancho, alto = MODO["ancho_alto"]
    margen = MODO["margen"]
    columnas, filas = MODO["columnas"], MODO["filas"]
    pares = MODO["num_pares"]

    archivos = _imagenes_del_tema(_directorio_tema(tema))

    try:
        reverso = pygame.transform.smoothscale(
            constantes.get_carta_volteada(), (ancho, alto)
        )
    except (FileNotFoundError, pygame.error):
        reverso = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(reverso, constantes.MORADO_P, reverso.get_rect(), border_radius=20)

    # Cargar las imagenes base una sola vez
    imagenes_base = []
    if archivos:
        for ruta in archivos:
            try:
                original = pygame.image.load(str(ruta)).convert_alpha()
                imagenes_base.append(
                    pygame.transform.smoothscale(original, (ancho, alto))
                )
            except (FileNotFoundError, pygame.error):
                pass

    baraja = []
    for i in range(pares):
        imagen = None
        if imagenes_base:
            idx_img = i % len(imagenes_base)
            imagen = imagenes_base[idx_img]

        if imagen is None:
            idx_img = i
            imagen = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            paleta = ui.PALETA_TEMAS[i % len(ui.PALETA_TEMAS)]
            imagen.blit(ui.degradado_redondeado((ancho, alto), paleta[0], paleta[1], 20), (0, 0))

        # id_par se basa en la imagen real: si dos parejas comparten el
        # mismo dibujo (porque el tema tiene menos imagenes que parejas),
        # cualquier dos cartas con ese dibujo hacen match entre si.
        baraja.append((idx_img, imagen))
        baraja.append((idx_img, imagen))

    random.shuffle(baraja)

    ancho_total = columnas * ancho + (columnas - 1) * margen
    alto_total = filas * alto + (filas - 1) * margen
    x_inicial = (constantes.ANCHO - ancho_total) // 2
    y_inicial = (constantes.ALTO - alto_total) // 2 + 34   # deja aire para el HUD

    cartas = []
    for idx, (id_par, imagen) in enumerate(baraja):
        fila, col = divmod(idx, columnas)
        x = x_inicial + col * (ancho + margen)
        y = y_inicial + fila * (alto + margen)
        cartas.append(Carta(id_par, imagen, x, y, ancho, alto, reverso))
    return cartas


def dibujar_estrella(superficie, centro, radio, color, borde=ui.BLANCO):
    """Estrella de cinco puntas para la pantalla de victoria."""
    import math
    puntos = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        r = radio if i % 2 == 0 else radio * 0.45
        puntos.append((centro[0] + r * math.cos(ang), centro[1] + r * math.sin(ang)))
    pygame.draw.polygon(superficie, color, puntos)
    pygame.draw.polygon(superficie, borde, puntos, 3)


# ---------------------------------------------------------------------
# Juego
# ---------------------------------------------------------------------

class MiJuego(GameBase):
    def __init__(self) -> None:
        meta = GameMetadata(
            title="MEMORÍZALO",
            description="Juego de memoria excepcional",
            authors=["Gabriel Garanton", "Isabela Paraqueimo", "Cesar Moya"],
        )
        super().__init__(meta)
        self._clock = pygame.time.Clock()
        self._fondo = None
        self._ventana = None
        self._salir = False

        # estado general: "menu" | "playing" | "victory"
        self._game_state = "menu"

        # partida en curso
        self._game_initialized = False
        self._cartas = []
        self._num_pares = MODO["num_pares"]
        self._tema_actual = None
        self._seleccionadas = []
        self._pares_encontrados = 0
        self._intentos = 0
        self._esperando_verificacion = False
        self._esperando_voltear_atras = False
        self._marca_verificacion = 0
        self._mouse = (0, 0)

        # --- sistema de pista TDAH ---
        # si el jugador falla muchas veces seguidas sin encontrar un par,
        # se muestra una ayuda suave (brillo en dos cartas que forman pareja)
        # para reducir la frustracion, que es lo que mas afecta a ninos con TDAH.
        self._fallos_seguidos = 0
        self._pista_activa = False
        self._pista_cartas = []       # las dos cartas que se resaltan
        self._pista_pulso = 0.0       # animacion del brillo
        self._FALLOS_PARA_PISTA = 4   # tras 4 fallos seguidos, mostrar pista

        # controles (se crean en on_start, cuando ya hay ventana)
        self._btn_menu = None
        self._btn_otra_vez = None
        self._btn_victoria_menu = None
        self._insignia_pares = None
        self._insignia_intentos = None
        self._brillo_victoria = 0.0

    # -----------------------------------------------------------------
    # ciclo de vida
    # -----------------------------------------------------------------

    def on_start(self) -> None:
        self._fondo = pygame.transform.smoothscale(
            constantes.get_fondo(), (constantes.ANCHO, constantes.ALTO)
        )
        self._btn_menu = ui.Boton(112, constantes.ALTO - 52, 176, 56,
                                  "Menú", ui.NEUTRO, tam_texto=24)
        self._insignia_pares = ui.Insignia(24, 20, 150, 74, "PAREJAS", ui.VERDE)
        self._insignia_intentos = ui.Insignia(constantes.ANCHO - 174, 20, 150, 74,
                                              "INTENTOS", ui.LAVANDA)
        self._btn_otra_vez = ui.Boton(constantes.ANCHO // 2 - 130, 470, 244, 66,
                                      "Jugar otra vez", ui.VERDE, tam_texto=26)
        self._btn_victoria_menu = ui.Boton(constantes.ANCHO // 2 + 130, 470, 244, 66,
                                           "Menú", ui.NEUTRO, tam_texto=26)
        self._game_state = "menu"

    def _superficie_activa(self):
        """Standalone (run_preview) dibuja sobre self._ventana; dentro del
        launcher 'enfocate' dibuja sobre self.surface."""
        return self._ventana or self.surface

    # -----------------------------------------------------------------
    # update
    # -----------------------------------------------------------------

    def update(self, dt: float) -> None:
        if self._game_state == "menu":
            self._update_menu()
        elif self._game_state == "playing":
            self._update_game(dt)
        elif self._game_state == "victory":
            self._update_victoria(dt)

    def _update_menu(self):
        """ejecutar_menu es bloqueante: corre su propio bucle hasta que el
        jugador elige tematica (y ahi arranca la partida) o decide salir."""
        tema = ejecutar_menu(self._superficie_activa(), self._clock)
        if tema:
            self._start_game(tema)
        else:
            self._salir = True
            self._stop_context()

    def _start_game(self, tema=None):
        pygame.event.clear()
        reproducir_musica(constantes.MUSICA_JUEGO)

        self._tema_actual = tema or self._tema_actual or constantes.TEMA_CARTAS
        self._cartas = crear_cartas(self._tema_actual)
        self._num_pares = MODO["num_pares"]

        self._seleccionadas = []
        self._pares_encontrados = 0
        self._intentos = 0
        self._esperando_verificacion = False
        self._esperando_voltear_atras = False
        self._marca_verificacion = 0
        self._brillo_victoria = 0.0

        self._fallos_seguidos = 0
        self._pista_activa = False
        self._pista_cartas = []
        self._pista_pulso = 0.0

        self._game_initialized = True
        self._game_state = "playing"

    def _ir_al_menu(self):
        self._game_initialized = False
        self._game_state = "menu"
        self._cartas = []
        reproducir_musica(constantes.MUSICA_MENU)

    def _update_game(self, dt):
        if not self._game_initialized:
            return

        self._mouse = pygame.mouse.get_pos()
        presionando = pygame.mouse.get_pressed()[0]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self._salir = True
                self._stop_context()
                return
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                play_efecto("boton")
                self._ir_al_menu()
                return
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self._btn_menu and self._btn_menu.rect.collidepoint(evento.pos):
                    play_efecto("boton")
                    self._ir_al_menu()
                    return
                if not self._esperando_verificacion:
                    for carta in self._cartas:
                        if carta.clic_en_carta(evento.pos) and len(self._seleccionadas) < 2:
                            play_efecto("carta")
                            carta.iniciar_volteo_mostrar()
                            self._seleccionadas.append(carta)
                            break

        if self._btn_menu:
            self._btn_menu.actualizar(self._mouse, presionando)

        self._logica_partida(dt)

    def _logica_partida(self, dt):
        # dos cartas destapadas -> se dejan a la vista un momento y se comparan
        if len(self._seleccionadas) == 2 and not self._esperando_verificacion:
            self._esperando_verificacion = True
            self._intentos += 1
            self._marca_verificacion = pygame.time.get_ticks()

        if self._esperando_verificacion and not self._esperando_voltear_atras:
            transcurrido = pygame.time.get_ticks() - self._marca_verificacion
            if transcurrido > constantes.ESPERA_VERIFICACION:
                c1, c2 = self._seleccionadas
                if c1.id_par == c2.id_par:
                    play_efecto("correcto")
                    c1.marcar_emparejada()
                    c2.marcar_emparejada()
                    self._pares_encontrados += 1
                    self._seleccionadas = []
                    self._esperando_verificacion = False
                    self._fallos_seguidos = 0
                    self._pista_activa = False
                    self._pista_cartas = []
                else:
                    play_efecto("incorrecto")
                    c1.iniciar_volteo_ocultar()
                    c2.iniciar_volteo_ocultar()
                    self._esperando_voltear_atras = True
                    self._fallos_seguidos += 1
                    if self._fallos_seguidos >= self._FALLOS_PARA_PISTA and not self._pista_activa:
                        self._activar_pista()

        if self._esperando_voltear_atras and self._seleccionadas:
            if all(c.animacion_volteo is None for c in self._seleccionadas):
                self._seleccionadas = []
                self._esperando_verificacion = False
                self._esperando_voltear_atras = False

        for carta in self._cartas:
            carta.actualizar(dt, self._mouse)

        # pulso de la pista
        if self._pista_activa:
            self._pista_pulso += dt * 3.0

        if self._pares_encontrados == self._num_pares and not self._esperando_verificacion:
            if all(c.celebracion <= 0 for c in self._cartas):
                self._game_state = "victory"
                self._brillo_victoria = 0.0

    def _activar_pista(self):
        """Elige un par no emparejado y lo marca para que brille."""
        no_emparejadas = [c for c in self._cartas if not c.emparejada]
        # agrupar por id_par
        grupos = {}
        for c in no_emparejadas:
            grupos.setdefault(c.id_par, []).append(c)
        # elegir un grupo que tenga al menos 2 cartas
        for id_par, cartas in grupos.items():
            if len(cartas) >= 2:
                self._pista_cartas = cartas[:2]
                self._pista_activa = True
                self._pista_pulso = 0.0
                return

    def _update_victoria(self, dt):
        self._mouse = pygame.mouse.get_pos()
        presionando = pygame.mouse.get_pressed()[0]
        self._brillo_victoria = min(1.0, self._brillo_victoria + dt * 2.2)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self._salir = True
                self._stop_context()
                return
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self._ir_al_menu()
                return
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self._btn_otra_vez and self._btn_otra_vez.rect.collidepoint(evento.pos):
                    play_efecto("boton")
                    self._start_game(self._tema_actual)
                    return
                if self._btn_victoria_menu and self._btn_victoria_menu.rect.collidepoint(evento.pos):
                    play_efecto("boton")
                    self._ir_al_menu()
                    return

        for b in (self._btn_otra_vez, self._btn_victoria_menu):
            if b:
                b.actualizar(self._mouse, presionando)

    # -----------------------------------------------------------------
    # draw
    # -----------------------------------------------------------------

    def draw(self) -> None:
        destino = self._superficie_activa()
        if not destino:
            return
        if self._game_state == "playing":
            self._draw_game(destino)
        elif self._game_state == "victory":
            self._draw_game(destino)
            self._draw_victoria(destino)
        else:
            destino.fill(COLORS["background"])

    def _draw_game(self, destino):
        if self._fondo:
            destino.blit(self._fondo, (0, 0))
        else:
            destino.fill((240, 238, 250))

        for carta in self._cartas:
            carta.dibujar(destino)

        # pista TDAH: brillo suave y pulsante sobre las cartas indicadas
        if self._pista_activa and self._pista_cartas:
            import math
            pulso = 0.35 + 0.25 * math.sin(self._pista_pulso)
            for carta in self._pista_cartas:
                if not carta.emparejada and not carta.visible:
                    brillo = pygame.Surface(carta.rect.size, pygame.SRCALPHA)
                    pygame.draw.rect(brillo, (250, 214, 122, int(140 * pulso)),
                                     brillo.get_rect(), border_radius=20)
                    destino.blit(brillo, carta.rect.topleft)
                    # borde dorado
                    pygame.draw.rect(destino, (240, 206, 122, int(200 * pulso)),
                                     carta.rect.inflate(4, 4), width=3, border_radius=22)

        if self._insignia_pares:
            self._insignia_pares.dibujar(
                destino, f"{self._pares_encontrados}/{self._num_pares}")
        if self._insignia_intentos:
            self._insignia_intentos.dibujar(destino, self._intentos)

        if self._tema_actual:
            nombre = constantes.TEMAS_INFO.get(self._tema_actual, {}).get(
                "nombre", self._tema_actual.capitalize())
            ui.texto_centrado(destino, nombre, ui.fuente(24, negrita=True),
                              ui.TEXTO_SUAVE, (constantes.ANCHO // 2, 46))

        if self._btn_menu:
            self._btn_menu.dibujar(destino)

    def _estrellas_ganadas(self):
        """3 estrellas si casi no fallo, 2 si fallo poco, 1 si tardo mas.
        Con 6 parejas el minimo posible de intentos es 6."""
        if self._intentos <= 8:
            return 3
        if self._intentos <= 12:
            return 2
        return 1

    def _draw_victoria(self, destino):
        p = self._brillo_victoria

        velo = pygame.Surface((constantes.ANCHO, constantes.ALTO), pygame.SRCALPHA)
        velo.fill(constantes.OVERLAY_VICTORIA + (int(190 * p),))
        destino.blit(velo, (0, 0))

        panel_rect = pygame.Rect(0, 0, 620, 400)
        panel_rect.center = (constantes.ANCHO // 2, 340)
        ui.panel(destino, panel_rect, radio=32, relleno=(255, 255, 255, 240))

        ui.texto_centrado(destino, "¡Muy bien!", ui.fuente(56, negrita=True),
                          ui.TEXTO, (panel_rect.centerx, panel_rect.y + 72),
                          sombra=ui.BLANCO)

        ganadas = self._estrellas_ganadas()
        for i in range(3):
            cx = panel_rect.centerx + (i - 1) * 92
            cy = panel_rect.y + 168
            crecer = 1.0 if i < ganadas else 0.82
            color = (250, 214, 122) if i < ganadas else (226, 224, 234)
            dibujar_estrella(destino, (cx, cy), int(40 * crecer), color)

        ui.texto_centrado(
            destino,
            f"Encontraste las {self._num_pares} parejas en {self._intentos} intentos",
            ui.fuente(23), ui.TEXTO_SUAVE, (panel_rect.centerx, panel_rect.y + 250))

        if self._btn_otra_vez:
            self._btn_otra_vez.dibujar(destino)
        if self._btn_victoria_menu:
            self._btn_victoria_menu.dibujar(destino)

    # -----------------------------------------------------------------
    # ejecucion independiente
    # -----------------------------------------------------------------

    def run_preview(self) -> None:
        """Ejecucion sin el launcher: crea la ventana y corre el bucle."""
        if not pygame.get_init():
            pygame.init()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            pass

        ventana = pygame.display.set_mode((constantes.ANCHO, constantes.ALTO))
        pygame.display.set_caption("MEMORÍZALO")
        self._ventana = ventana
        self.surface = ventana
        self.running = True

        self.on_start()

        while not self._salir:
            dt = self._clock.tick(constantes.FPS) / 1000.0
            self.update(dt)
            if self._salir:
                break
            self.draw()
            pygame.display.update()

        pygame.quit()
