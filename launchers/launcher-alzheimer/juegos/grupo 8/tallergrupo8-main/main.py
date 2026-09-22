import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_dir)
if _dir not in sys.path:
    sys.path.insert(0, _dir)

import pygame
import random
import time

# ==================== CONFIGURACIÓN ====================
pygame.init()

ANCHO, ALTO = 800, 700
FPS = 60
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Memory")


BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (52, 152, 219)
AZUL_HOVER = (41, 128, 185)
VERDE = (46, 204, 113)
VERDE_HOVER = (39, 174, 96)
ROJO = (231, 76, 60)
ROJO_HOVER = (192, 57, 43)
GRIS = (236, 240, 241)
GRIS_OSCURO = (149, 165, 166)
AMARILLO = (241, 196, 15)
MORADO = (155, 89, 182)
NARANJA = (230, 126, 34)
TURQUESA = (26, 188, 156)
ROSA = (231, 76, 150)

COLORES_CARTAS = [AZUL, VERDE, ROJO, AMARILLO, MORADO, NARANJA, TURQUESA, ROSA]


FUENTE_TITULO = pygame.font.SysFont("arial", 60, bold=True)
FUENTE_MEDIA = pygame.font.SysFont("arial", 32, bold=True)
FUENTE_NORMAL = pygame.font.SysFont("arial", 24)
FUENTE_PEQUEÑA = pygame.font.SysFont("arial", 18)


# ==================== CLASE BOTÓN ====================
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, color_hover, accion=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover
        self.accion = accion
        self.hover = False

    def dibujar(self, superficie):
        color = self.color_hover if self.hover else self.color
        pygame.draw.rect(superficie, color, self.rect, border_radius=12)
        pygame.draw.rect(superficie, NEGRO, self.rect, 3, border_radius=12)

        texto_render = FUENTE_MEDIA.render(self.texto, True, BLANCO)
        texto_rect = texto_render.get_rect(center=self.rect.center)
        superficie.blit(texto_render, texto_rect)

    def actualizar(self, pos_mouse):
        self.hover = self.rect.collidepoint(pos_mouse)

    def click(self, pos_mouse):
        if self.rect.collidepoint(pos_mouse) and self.accion:
            self.accion()


# ==================== CLASE CARTA ====================
class Carta:
    def __init__(self, x, y, ancho, alto, valor, imagen):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.valor = valor
        
        self.imagen = pygame.transform.scale(imagen, (ancho, alto))
        
        self.revelada = False
        self.encontrada = False

    def dibujar(self, superficie):
        if self.encontrada or self.revelada:
            # Dibujar la foto
            superficie.blit(self.imagen, self.rect)
            
            color_borde = VERDE if self.encontrada else NEGRO
            pygame.draw.rect(superficie, color_borde, self.rect, 4, border_radius=10)
            
            if self.encontrada:
                pygame.draw.lines(
                    superficie, BLANCO, False,
                    [(self.rect.x + 20, self.rect.centery),
                     (self.rect.centerx - 5, self.rect.bottom - 20),
                     (self.rect.right - 20, self.rect.y + 20)], 5
                )
        else:
            pygame.draw.rect(superficie, GRIS_OSCURO, self.rect, border_radius=10)
            pygame.draw.rect(superficie, NEGRO, self.rect, 3, border_radius=10)
            pygame.draw.circle(superficie, BLANCO, self.rect.center, 20, 3)
            pygame.draw.circle(superficie, BLANCO, self.rect.center, 8)


# ==================== ESTADOS DEL JUEGO ====================
ESTADO_MENU = "menu"
ESTADO_JUGANDO = "jugando"
ESTADO_VICTORIA = "victoria"
ESTADO_GAMEOVER = "gameover"


class Juego:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.estado = ESTADO_MENU
        self.dificultad = "facil"

        # Lógica de detección mazos
        self.mazos = self.obtener_mazos_disponibles()
        self.indice_mazo = 0
        self.tema_actual = self.mazos[self.indice_mazo]

        # Datos del juego
        self.cartas = []
        self.primera_carta = None
        self.segunda_carta = None
        self.bloquear_click = False
        self.tiempo_bloqueo = 0

        self.intentos = 0
        self.parejas_encontradas = 0
        self.total_parejas = 0
        self.tiempo_inicio = 0
        self.tiempo_limite = 0

        # Botón dinámico para cambiar el mazo
        self.boton_mazo = Boton(250, 260, 300, 50, f"MAZO: {self.tema_actual.upper()}", MORADO, AMARILLO, self.cambiar_mazo)

        # Botones del menú 
        self.botones_menu = [
            self.boton_mazo,
            Boton(300, 330, 200, 50, "FÁCIL (4x3)", VERDE, VERDE_HOVER, lambda: self.iniciar_juego("facil")),
            Boton(300, 400, 200, 50, "MEDIO (4x4)", AZUL, AZUL_HOVER, lambda: self.iniciar_juego("medio")),
            Boton(300, 470, 200, 50, "DIFÍCIL (6x4)", ROJO, ROJO_HOVER, lambda: self.iniciar_juego("dificil")),
            Boton(300, 540, 200, 50, "SALIR", GRIS_OSCURO, NEGRO, self.salir),
        ]

        # Botones de fin de partida
        self.boton_reintentar = Boton(200, 550, 180, 60, "REINTENTAR", VERDE, VERDE_HOVER, self.reiniciar)
        self.boton_menu = Boton(420, 550, 180, 60, "MENÚ", AZUL, AZUL_HOVER, self.volver_menu)

    # ---------- LÓGICA DE MAZOS ----------
    def obtener_mazos_disponibles(self):
        """Escanea la carpeta assets/cartas y devuelve una lista de las subcarpetas."""
        ruta_base = os.path.join("assets", "cartas")
        
        if not os.path.exists(ruta_base):
            os.makedirs(os.path.join(ruta_base, "estados"))
            
        carpetas = [nombre for nombre in os.listdir(ruta_base) if os.path.isdir(os.path.join(ruta_base, nombre))]
        
        if not carpetas:
            return ["estados"]
        return carpetas

    def cambiar_mazo(self):
        """Alterna entre las carpetas detectadas y actualiza el texto del botón."""
        self.indice_mazo = (self.indice_mazo + 1) % len(self.mazos)
        self.tema_actual = self.mazos[self.indice_mazo]
        self.boton_mazo.texto = f"MAZO: {self.tema_actual.upper()}"

    # ---------- LÓGICA DEL JUEGO ----------
    def iniciar_juego(self, dificultad):
        self.dificultad = dificultad
        config = {
            "facil":   {"cols": 4, "filas": 3, "tiempo": 90},
            "medio":   {"cols": 4, "filas": 4, "tiempo": 90},
            "dificil": {"cols": 6, "filas": 4, "tiempo": 120},
        }
        cfg = config[dificultad]
        cols, filas = cfg["cols"], cfg["filas"]
        self.tiempo_limite = cfg["tiempo"]

        total = cols * filas
        num_parejas = total // 2
        self.total_parejas = num_parejas

        # Crear valores de pareja
        valores = list(range(1, num_parejas + 1)) * 2
        random.shuffle(valores)

        # Dimensiones de cartas
        ancho_carta, alto_carta = 120, 120
        espacio = 15
        ancho_grid = cols * ancho_carta + (cols - 1) * espacio
        alto_grid = filas * alto_carta + (filas - 1) * espacio
        offset_x = (ANCHO - ancho_grid) // 2
        offset_y = 100
        
        # Llamar a nuestro escáner dinámico pasando el mazo seleccionado en el menú
        imagenes_cargadas = self.cargar_imagenes_dinamicas(
            tema=self.tema_actual, 
            cantidad_parejas=num_parejas, 
            ancho=ancho_carta, 
            alto=alto_carta
        )

        # Crear las cartas
        self.cartas = []
        for i in range(filas):
            for j in range(cols):
                idx = i * cols + j
                x = offset_x + j * (ancho_carta + espacio)
                y = offset_y + i * (alto_carta + espacio)
                
                imagen_asignada = imagenes_cargadas[valores[idx] - 1]
                
                carta = Carta(x, y, ancho_carta, alto_carta, valores[idx], imagen_asignada)
                self.cartas.append(carta)

        self.primera_carta = None
        self.segunda_carta = None
        self.bloquear_click = False
        self.intentos = 0
        self.parejas_encontradas = 0
        self.tiempo_inicio = time.time()
        self.estado = ESTADO_JUGANDO

    def reiniciar(self):
        self.iniciar_juego(self.dificultad)

    def volver_menu(self):
        self.mazos = self.obtener_mazos_disponibles()
        if self.tema_actual not in self.mazos:
            self.indice_mazo = 0
            self.tema_actual = self.mazos[self.indice_mazo]
            self.boton_mazo.texto = f"MAZO: {self.tema_actual.upper()}"
            
        self.estado = ESTADO_MENU

    def salir(self):
        pygame.quit()
        sys.exit()

    def manejar_click_carta(self, pos):
        if self.bloquear_click:
            return
        for carta in self.cartas:
            if carta.rect.collidepoint(pos) and not carta.revelada and not carta.encontrada:
                carta.revelada = True
                if not self.primera_carta:
                    self.primera_carta = carta
                elif not self.segunda_carta and carta != self.primera_carta:
                    self.segunda_carta = carta
                    self.intentos += 1
                    self.bloquear_click = True
                    self.tiempo_bloqueo = time.time()
                break

    def actualizar(self):
        if self.bloquear_click and self.primera_carta and self.segunda_carta:
            if time.time() - self.tiempo_bloqueo > 0.8:
                if self.primera_carta.valor == self.segunda_carta.valor:
                    self.primera_carta.encontrada = True
                    self.segunda_carta.encontrada = True
                    self.parejas_encontradas += 1
                else:
                    self.primera_carta.revelada = False
                    self.segunda_carta.revelada = False

                self.primera_carta = None
                self.segunda_carta = None
                self.bloquear_click = False

                # Verificar victoria
                if self.parejas_encontradas == self.total_parejas:
                    self.estado = ESTADO_VICTORIA

        if self.estado == ESTADO_JUGANDO:
            tiempo_restante = self.tiempo_limite - (time.time() - self.tiempo_inicio)
            if tiempo_restante <= 0:
                self.estado = ESTADO_GAMEOVER

    # ---------- DIBUJADO ----------
    def dibujar_menu(self):
        VENTANA.fill(GRIS)

        # Título con sombra
        titulo = FUENTE_TITULO.render("JUEGO DE MEMORIA", True, MORADO)
        titulo_rect = titulo.get_rect(center=(ANCHO // 2, 120))
        VENTANA.blit(titulo, titulo_rect)

        subtitulo = FUENTE_NORMAL.render("Encuentra todas las parejas antes de que acabe el tiempo",
                                         True, NEGRO)
        sub_rect = subtitulo.get_rect(center=(ANCHO // 2, 190))
        VENTANA.blit(subtitulo, sub_rect)

        pos = pygame.mouse.get_pos()
        for boton in self.botones_menu:
            boton.actualizar(pos)
            boton.dibujar(VENTANA)

        # Instrucciones
        instrucciones = [
            "Haz clic en las cartas para revelarlas",
            "Encuentra pares iguales para ganar",
            "Tienes tiempo limitado por partida",
        ]
        for i, texto in enumerate(instrucciones):
            t = FUENTE_PEQUEÑA.render(texto, True, GRIS_OSCURO)
            VENTANA.blit(t, (260, 610 + i * 22))

    def dibujar_juego(self):
        VENTANA.fill(GRIS)

        # Encabezado
        pygame.draw.rect(VENTANA, AZUL, (0, 0, ANCHO, 80))
        pygame.draw.line(VENTANA, NEGRO, (0, 80), (ANCHO, 80), 3)

        # Intentos
        texto_intentos = FUENTE_NORMAL.render(f"Intentos: {self.intentos}", True, BLANCO)
        VENTANA.blit(texto_intentos, (30, 25))

        # Parejas
        texto_parejas = FUENTE_NORMAL.render(
            f"Parejas: {self.parejas_encontradas}/{self.total_parejas}", True, BLANCO)
        VENTANA.blit(texto_parejas, (300, 25))

        # Tiempo
        tiempo_restante = max(0, int(self.tiempo_limite - (time.time() - self.tiempo_inicio)))
        color_tiempo = ROJO if tiempo_restante <= 10 else BLANCO
        texto_tiempo = FUENTE_NORMAL.render(f"{tiempo_restante}s", True, color_tiempo)
        VENTANA.blit(texto_tiempo, (ANCHO - 150, 25))

        # Cartas
        for carta in self.cartas:
            carta.dibujar(VENTANA)

    def dibujar_victoria(self):
        VENTANA.fill(VERDE)
        tiempo_usado = int(time.time() - self.tiempo_inicio)

        titulo = FUENTE_TITULO.render("¡GANASTE! ", True, BLANCO)
        titulo_rect = titulo.get_rect(center=(ANCHO // 2, 150))
        VENTANA.blit(titulo, titulo_rect)

        stats = [
            f"Intentos: {self.intentos}",
            f"Tiempo: {tiempo_usado}s",
            f"Dificultad: {self.dificultad.upper()}",
            f"Mazo: {self.tema_actual.upper()}"
        ]
        for i, texto in enumerate(stats):
            t = FUENTE_MEDIA.render(texto, True, BLANCO)
            t_rect = t.get_rect(center=(ANCHO // 2, 260 + i * 40))
            VENTANA.blit(t, t_rect)

        pos = pygame.mouse.get_pos()
        self.boton_reintentar.actualizar(pos)
        self.boton_reintentar.dibujar(VENTANA)
        self.boton_menu.actualizar(pos)
        self.boton_menu.dibujar(VENTANA)

    def dibujar_gameover(self):
        VENTANA.fill(ROJO)

        titulo = FUENTE_TITULO.render("¡TIEMPO AGOTADO!", True, BLANCO)
        titulo_rect = titulo.get_rect(center=(ANCHO // 2, 150))
        VENTANA.blit(titulo, titulo_rect)

        stats = [
            f"Parejas encontradas: {self.parejas_encontradas}/{self.total_parejas}",
            f"Intentos: {self.intentos}",
        ]
        for i, texto in enumerate(stats):
            t = FUENTE_MEDIA.render(texto, True, BLANCO)
            t_rect = t.get_rect(center=(ANCHO // 2, 280 + i * 50))
            VENTANA.blit(t, t_rect)

        pos = pygame.mouse.get_pos()
        self.boton_reintentar.actualizar(pos)
        self.boton_reintentar.dibujar(VENTANA)
        self.boton_menu.actualizar(pos)
        self.boton_menu.dibujar(VENTANA)

    def cargar_imagenes_dinamicas(self, tema, cantidad_parejas, ancho, alto):
        ruta_tema = os.path.join("assets", "cartas", tema)
        extensiones_validas = ('.png', '.jpg', '.jpeg')
        archivos_encontrados = []

        if not os.path.exists(ruta_tema):
            os.makedirs(ruta_tema)
            print(f"Se creó la carpeta '{ruta_tema}'. ¡Añade fotos ahí!")

        for archivo in os.listdir(ruta_tema):
            if archivo.lower().endswith(extensiones_validas):
                archivos_encontrados.append(os.path.join(ruta_tema, archivo))

        random.shuffle(archivos_encontrados)

        imagenes_cargadas = []
        for i in range(cantidad_parejas):
            if len(archivos_encontrados) > 0:
                ruta_img = archivos_encontrados[i % len(archivos_encontrados)]
                img = pygame.image.load(ruta_img).convert_alpha()
            else:
                img = pygame.Surface((ancho, alto))
                color_aleatorio = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                img.fill(color_aleatorio)
            
            img = pygame.transform.scale(img, (ancho, alto))
            imagenes_cargadas.append(img)

        return imagenes_cargadas

    # ---------- BUCLE PRINCIPAL ----------
    def ejecutar(self):
        while True:
            pos_mouse = pygame.mouse.get_pos()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salir()

                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.estado == ESTADO_MENU:
                        for boton in self.botones_menu:
                            boton.click(pos_mouse)
                    elif self.estado == ESTADO_JUGANDO:
                        self.manejar_click_carta(pos_mouse)
                    elif self.estado in (ESTADO_VICTORIA, ESTADO_GAMEOVER):
                        self.boton_reintentar.click(pos_mouse)
                        self.boton_menu.click(pos_mouse)

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if self.estado == ESTADO_JUGANDO:
                            self.volver_menu()
                        else:
                            self.salir()

            if self.estado == ESTADO_JUGANDO:
                self.actualizar()

            if self.estado == ESTADO_MENU:
                self.dibujar_menu()
            elif self.estado == ESTADO_JUGANDO:
                self.dibujar_juego()
            elif self.estado == ESTADO_VICTORIA:
                self.dibujar_victoria()
            elif self.estado == ESTADO_GAMEOVER:
                self.dibujar_gameover()

            pygame.display.flip()
            self.clock.tick(FPS)


# ==================== EJECUCIÓN ====================
if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()