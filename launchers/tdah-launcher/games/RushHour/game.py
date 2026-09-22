import sys
import pygame
from pathlib import Path
from Botones import Boton
from Autos import Vehiculo, Pj

class RushHourGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        # Dimensiones exigidas
        self.ANCHO = 1280
        self.ALTO = 720
        self.screen = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Rush Hour")
        self.clock = pygame.time.Clock()

        # Base de directorios dinámicos usando pathlib
        self.BASE_DIR = Path(__file__).resolve().parent
        self.ASSETS_DIR = self.BASE_DIR / "assets"
        self.SONIDOS_DIR = self.BASE_DIR / "Sonido"

        # Cargar imágenes de fondo e interfaz
        self.fondo = pygame.image.load(self.ASSETS_DIR / "PortadaFinal.png").convert()
        self.gameplay = pygame.image.load(self.ASSETS_DIR / "portadaJuego.png").convert()
        self.tablero = pygame.image.load(self.ASSETS_DIR / "tablero.png").convert_alpha()
        self.tablero = pygame.transform.scale(self.tablero, (600, 600))
        self.cartel_vic = pygame.image.load(self.ASSETS_DIR / "victoria.png").convert_alpha()

        # Cargar Sonidos
        self.click_sound_path = self.SONIDOS_DIR / "Click.mp3"
        self.fanfare = pygame.mixer.Sound(self.SONIDOS_DIR / "Victoria.mp3")
        self.agarrar = pygame.mixer.Sound(self.SONIDOS_DIR / "Agarrar.mp3")

        # Límites del tablero y área de victoria
        self.muros = [
            pygame.Rect(360, 10, 700, 90),   # Superior
            pygame.Rect(360, 10, 45, 700),   # Izquierdo
            pygame.Rect(920, 10, 50, 700),   # Derecho
            pygame.Rect(360, 610, 700, 50)   # Inferior
        ]
        self.ganar = pygame.Rect(840, 280, 60, 60)

        # Control de estado de la aplicación
        self.estado = 'start'  # 'start', 'nivel1'..'nivel10', 'victoria'
        self.signiv = None
        self.running = True

        # Interacción de arrastre
        self.act_car = None
        self.moviendo = False
        self.cood = (0, 0)
        self.carros = []

        # Inicialización del menú y música
        self._cargar_botones()
        pygame.mixer.music.load(self.SONIDOS_DIR / "Sonidomenu.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    def _cargar_botones(self):
        if self.estado == 'start':
            self.btn_jugar = Boton(self.ASSETS_DIR / "BotonJugar.png", self.click_sound_path, (550, 515), 0.1)
            self.btn_salir = Boton(self.ASSETS_DIR / "BotonSalirRojo.png", self.click_sound_path, (550, 615), 0.1)
        elif self.estado == 'victoria':
            self.btn_siguiente = Boton(self.ASSETS_DIR / "Botonsiguiente.png", self.click_sound_path, (550, 545), 0.1)
        else:
            self.btn_reiniciar = Boton(self.ASSETS_DIR / "BotonReiniciar.png", self.click_sound_path, (150, 545), 0.1)
            self.btn_salirnivel = Boton(self.ASSETS_DIR / "BotonSalirRojo.png", self.click_sound_path, (150, 445), 0.1)

    def _inicializar_autos(self):
        self.camion_r = Vehiculo((0, 0), self.ASSETS_DIR / "camion2.png", (80, 250), 'v')
        self.camion_ama = Vehiculo((0, 0), self.ASSETS_DIR / "CamionAmarillo.png", (80, 250), 'v')
        self.camion_azuh = Vehiculo((0, 0), self.ASSETS_DIR / "CamionAzul3.png", (250, 80), 'h')
        self.morado = Vehiculo((0, 0), self.ASSETS_DIR / "Automorado2.png", (80, 150), 'v')
        self.morado_h = Vehiculo((0, 0), self.ASSETS_DIR / "Automorado3.png", (150, 80), 'h')
        self.rojo = Pj((0, 0), self.ASSETS_DIR / "rojo2.png", (150, 80), 'h', self.ganar)
        self.negro = Vehiculo((0, 0), self.ASSETS_DIR / "CKcar2.png", (150, 80), 'h')
        self.gris = Vehiculo((0, 0), self.ASSETS_DIR / "Autogris2.png", (150, 80), 'h')
        self.naranja = Vehiculo((0, 0), self.ASSETS_DIR / "AutoNaranja2.png", (80, 150), 'v')
        self.naranja_h = Vehiculo((0, 0), self.ASSETS_DIR / "AutoNaranja3.png", (150, 80), 'h')
        self.camion_v = Vehiculo((0, 0), self.ASSETS_DIR / "CamionVerde2.png", (80, 250), 'v')
        self.negro_v = Vehiculo((0, 0), self.ASSETS_DIR / "CKcar3.png", (80, 150), 'v')
        self.gris_v = Vehiculo((0, 0), self.ASSETS_DIR / "Autogris3.png", (80, 150), 'v')
        self.taxi_v = Vehiculo((0, 0), self.ASSETS_DIR / "Taxi3.png", (80, 150), 'v')
        self.taxi = Vehiculo((0, 0), self.ASSETS_DIR / "Taxi2.png", (150, 80), 'h')
        self.verde = Vehiculo((0, 0), self.ASSETS_DIR / "autoverde2.png", (80, 150), 'v')
        self.verde_h = Vehiculo((0, 0), self.ASSETS_DIR / "autoverde3.png", (150, 80), 'h')
        self.camion_vh = Vehiculo((0, 0), self.ASSETS_DIR / "CamionVerde3.png", (250, 80), 'h')

    def cargar_nivel(self, nivel: str):
        self._inicializar_autos()
        self.estado = nivel

        if nivel == 'nivel1':
            self.rojo.forma.center = (580, 315)
            self.morado.forma.center = (530, 520)
            self.camion_r.forma.center = (875, 480)
            self.negro.forma.center = (580, 405)
            self.gris.forma.center = (650, 570)
            self.camion_v.forma.center = (700, 405)
            self.carros = [self.rojo, self.morado, self.camion_r, self.negro, self.gris, self.camion_v]
            self.signiv = 'nivel2'

        elif nivel == 'nivel2':
            self.rojo.forma.center = (580, 315)
            self.negro.forma.center = (670, 405)
            self.morado.forma.center = (700, 270)
            self.taxi_v.forma.center = (700, 530)
            self.naranja.forma.center = (535, 180)
            self.gris.forma.center = (650, 140)
            self.gris_v.forma.center = (870, 180)
            self.negro_v.forma.center = (790, 180)
            self.verde.forma.center = (870, 350)
            self.carros = [self.rojo, self.negro, self.morado, self.taxi_v, self.naranja, self.gris, self.gris_v, self.negro_v, self.verde]
            self.signiv = 'nivel3'

        elif nivel == 'nivel3':
            self.rojo.forma.center = (580, 315)
            self.naranja.forma.center = (620, 180)
            self.camion_vh.forma.center = (625, 400)
            self.camion_r.forma.center = (445, 405)
            self.camion_v.forma.center = (870, 315)
            self.gris.forma.center = (820, 140)
            self.negro.forma.center = (820, 480)
            self.taxi.forma.center = (820, 570)
            self.morado.forma.center = (700, 530)
            self.morado_h.forma.center = (500, 225)
            self.naranja_h.forma.center = (500, 145)
            self.verde_h.forma.center = (490, 570)
            self.carros = [self.rojo, self.naranja, self.camion_vh, self.camion_r, self.camion_v, self.gris, self.negro, self.taxi, self.morado, self.morado_h, self.naranja_h, self.verde_h]
            self.signiv = 'nivel4'

        elif nivel == 'nivel4':
            self.rojo.forma.center = (760, 315)
            self.camion_v.forma.center = (870, 230)
            self.negro_v.forma.center = (790, 180)
            self.gris.forma.center = (650, 140)
            self.camion_r.forma.center = (618, 405)
            self.naranja_h.forma.center = (500, 145)
            self.verde_h.forma.center = (490, 570)
            self.gris_v.forma.center = (535, 355)
            self.morado.forma.center = (455, 261)
            self.camion_vh.forma.center = (787, 400)
            self.carros = [self.rojo, self.camion_v, self.negro_v, self.gris, self.negro, self.camion_r, self.naranja_h, self.verde_h, self.gris_v, self.morado, self.camion_vh]
            self.signiv = 'nivel5'

        elif nivel == 'nivel5':
            self.rojo.forma.center = (580, 315)
            self.camion_r.forma.center = (706, 230)
            self.gris.forma.center = (568, 140)
            self.camion_ama.forma.center = (450, 230)
            self.camion_vh.forma.center = (787, 400)
            self.camion_azuh.forma.center = (706, 562)
            self.naranja.forma.center = (620, 445)
            self.taxi_v.forma.center = (870, 525)
            self.carros = [self.rojo, self.camion_r, self.gris, self.camion_ama, self.camion_vh, self.camion_azuh, self.naranja, self.taxi_v]
            self.signiv = 'nivel6'

        elif nivel == 'nivel6':
            self.rojo.forma.center = (499, 315)
            self.camion_r.forma.center = (625, 230)
            self.naranja.forma.center = (535, 180)
            self.camion_vh.forma.center = (625, 400)
            self.morado.forma.center = (449, 439)
            self.gris_v.forma.center = (700, 530)
            self.negro.forma.center = (580, 486)
            self.taxi.forma.center = (820, 570)
            self.verde_h.forma.center = (820, 140)
            self.naranja_h.forma.center = (820, 222)
            self.camion_v.forma.center = (870, 396)
            self.carros = [self.rojo, self.camion_r, self.naranja, self.camion_vh, self.morado, self.gris_v, self.negro, self.taxi, self.verde_h, self.naranja_h, self.camion_v]
            self.signiv = 'start'

        elif nivel == 'nivel7':
            self.rojo.forma.center = (580, 315)
            self.camion_ama.forma.center = (700, 230)
            self.camion_r.forma.center = (870, 480)
            self.morado.forma.center = (535, 180)
            self.verde.forma.center = (450, 440)
            self.gris.forma.center = (650, 405)
            self.carros = [self.rojo, self.camion_ama, self.camion_r, self.morado, self.verde, self.gris]
            self.signiv = 'nivel8'

        elif nivel == 'nivel8':
            self.rojo.forma.center = (499, 315)
            self.camion_azuh.forma.center = (625, 140)
            self.camion_v.forma.center = (870, 230)
            self.taxi.forma.center = (650, 480)
            self.naranja.forma.center = (535, 440)
            self.negro_v.forma.center = (790, 350)
            self.carros = [self.rojo, self.camion_azuh, self.camion_v, self.taxi, self.naranja, self.negro_v]
            self.signiv = 'nivel9'

        elif nivel == 'nivel9':
            self.rojo.forma.center = (580, 315)
            self.camion_r.forma.center = (450, 230)
            self.camion_ama.forma.center = (870, 230)
            self.camion_vh.forma.center = (625, 400)
            self.morado.forma.center = (700, 270)
            self.gris_v.forma.center = (535, 440)
            self.verde_h.forma.center = (650, 570)
            self.carros = [self.rojo, self.camion_r, self.camion_ama, self.camion_vh, self.morado, self.gris_v, self.verde_h]
            self.signiv = 'nivel10'

        elif nivel == 'nivel10':
            self.rojo.forma.center = (499, 315)
            self.camion_v.forma.center = (870, 230)
            self.camion_r.forma.center = (700, 350)
            self.camion_ama.forma.center = (450, 230)
            self.camion_azuh.forma.center = (625, 140)
            self.naranja.forma.center = (535, 180)
            self.gris.forma.center = (650, 480)
            self.taxi.forma.center = (820, 570)
            self.morado.forma.center = (620, 445)
            self.carros = [self.rojo, self.camion_v, self.camion_r, self.camion_ama, self.camion_azuh, self.naranja, self.gris, self.taxi, self.morado]
            self.signiv = 'start'

        self._cargar_botones()

    def procesar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.estado == 'start':
                    if self.btn_jugar.es_presionado():
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(self.SONIDOS_DIR / "Sonidomenu.mp3")
                        pygame.mixer.music.set_volume(0.3)
                        pygame.mixer.music.play(-1)
                        self.cargar_nivel('nivel1')
                    elif self.btn_salir.es_presionado():
                        self.running = False

                elif self.estado == 'victoria':
                    if self.btn_siguiente.es_presionado():
                        if self.signiv == 'start':
                            self.estado = 'start'
                            self._cargar_botones()
                            pygame.mixer.music.load(self.SONIDOS_DIR / "Sonidomenu.mp3")
                            pygame.mixer.music.play(-1)
                        else:
                            self.cargar_nivel(self.signiv)

                else:
                    if self.btn_reiniciar.es_presionado():
                        self.cargar_nivel(self.estado)
                    elif self.btn_salirnivel.es_presionado():
                        self.estado = 'start'
                        self._cargar_botones()
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(self.SONIDOS_DIR / "Sonidomenu.mp3")
                        pygame.mixer.music.play(-1)

                if self.estado not in ['start', 'victoria']:
                    for idx, carro in enumerate(self.carros):
                        if carro.forma.collidepoint(event.pos):
                            self.agarrar.play()
                            self.act_car = idx
                            break

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.act_car = None

            if event.type == pygame.MOUSEMOTION and self.act_car is not None:
                self.cood = event.rel
                self.moviendo = True

    def actualizar(self):
        if self.moviendo and self.act_car is not None:
            carro_actual = self.carros[self.act_car]
            pos_anterior = carro_actual.forma.topleft

            if carro_actual.sen == 'h':
                carro_actual.forma.move_ip(self.cood[0], 0)
            elif carro_actual.sen == 'v':
                carro_actual.forma.move_ip(0, self.cood[1])

            for muro in self.muros:
                if carro_actual.forma.colliderect(muro):
                    carro_actual.forma.topleft = pos_anterior
                    break

            for otro_carro in self.carros:
                if otro_carro != carro_actual and carro_actual.forma.colliderect(otro_carro.forma):
                    carro_actual.forma.topleft = pos_anterior
                    break

            if carro_actual == self.rojo:
                if carro_actual.forma.colliderect(carro_actual.victoria):
                    self.fanfare.play()
                    self.estado = 'victoria'
                    self._cargar_botones()

            self.moviendo = False

    def dibujar(self):
        if self.estado == 'start':
            self.screen.blit(self.fondo, (0, 0))
            self.btn_jugar.draw(self.screen)
            self.btn_salir.draw(self.screen)

        elif self.estado == 'victoria':
            self.screen.blit(self.gameplay, (0, 0))
            self.screen.blit(self.cartel_vic, (250, 120))
            self.btn_siguiente.draw(self.screen)

        else:
            self.screen.blit(self.gameplay, (0, 0))
            self.screen.blit(self.tablero, (360, 50))
            
            for carro in self.carros:
                self.screen.blit(carro.image, carro.forma)

            self.btn_reiniciar.draw(self.screen)
            self.btn_salirnivel.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.procesar_eventos()
            self.actualizar()
            self.dibujar()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()