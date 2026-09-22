import os
import pygame
import math
from settings import *
from components import Decoracion, Boton, TarjetaJuego, FlechaNavegacion, IndicadorPagina


class State:
    def __init__(self, manager):
        self.manager = manager
    def actualizar(self, dt):
        pass
    def dibujar(self, renderer, superficie, t, mouse_pos):
        pass
    def manejar_click(self, pos):
        pass
    def manejar_tecla(self, key):
        """Devuelve True si la tecla fue manejada."""
        return False


class MenuState(State):
    def __init__(self, manager):
        super().__init__(manager)
        self.boton_empezar = Boton((ANCHO // 2, 470), (300, 84), "¡EMPEZAR!", manager.fuente_boton)

    def manejar_click(self, pos):
        if self.boton_empezar.contiene(pos):
            self.manager.cambiar_estado("seleccion")

    def dibujar(self, renderer, superficie, t, mouse_pos):
        renderer.dibujar_palabra_animada(
            superficie, "ABRE TU", self.manager.fuente_titulo, ANCHO // 2, 160,
            PALETA_TITULO, t, amplitud=8, velocidad=2.2,
        )
        renderer.dibujar_palabra_animada(
            superficie, "MENTE", self.manager.fuente_titulo, ANCHO // 2, 240,
            PALETA_TITULO[::-1], t, amplitud=8, velocidad=2.2, sombra=True,
        )

        tagline = self.manager.fuente_tagline.render("¡vamos a jugar y a divertirnos!", True, (120, 108, 150))
        angulo = math.sin(t * 1.1) * 2.5
        tagline_rotada = pygame.transform.rotate(tagline, angulo)
        tagline_rect = tagline_rotada.get_rect(center=(ANCHO // 2, 360))
        superficie.blit(tagline_rotada, tagline_rect)
        self.boton_empezar.dibujar(renderer, superficie, t, mouse_pos)


class SeleccionState(State):
    VELOCIDAD_SLIDE = 2200  # px/s
    ANCHO_SLIDE = 500       # distancia total del slide

    def __init__(self, manager):
        super().__init__(manager)
        self.boton_volver = Boton((100, 46), (140, 48), "← Volver", manager.fuente_boton_volver)

        self.juegos = [
            TarjetaJuego(
                "¿QUIÉN ES QUIÉN?", "Memoria Familiar (Grupo 1)",
                (255, 111, 129), "cartas",
                clave_juego="quien_es_quien",
                descripcion="Conoce a la familia y responde preguntas sobre sus características y relaciones.",
                habilidad="Memoria y reconocimiento",
                controles="Ratón / Tecla ENTER",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "Grupo-1", "Juego-quien-es-quien-Grupo-1-Taller-master", "assets", "cover", "launcher_cover.png")
            ),
            TarjetaJuego(
                "ANIMAL GENIUS", "Memoria y Atención (Grupo 2)",
                (76, 175, 80), "cartas",
                clave_juego="animal_genius",
                descripcion="Juego interactivo y cognitivo para estimulación de memoria y atención con animales.",
                habilidad="Atención y memoria visual",
                controles="Ratón / Clic",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "Grupo-2", "Grupo-2-Animal-Genius-main", "assets", "cover", "launcher_cover.jpg")
            ),
            TarjetaJuego(
                "EL BAÚL DEL SABER", "Refranes y Recuerdos (Grupo 3)",
                (245, 160, 50), "laberinto",
                clave_juego="el_baul_del_saber",
                descripcion="Juego guiado de refranes populares y reflexión emocional para adultos mayores.",
                habilidad="Lenguaje y reflexión",
                controles="Ratón / Clic",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo 3", "ElBaulDelSaber-main", "assets", "cover.png")
            ),
            TarjetaJuego(
                "MENTE ACTIVA", "Memoria Sensorial (Grupo 4)",
                (255, 140, 130), "cartas",
                clave_juego="mente_activa",
                descripcion="Juego de memoria visual-auditiva con pistas sensoriales adaptativas.",
                habilidad="Memoria sensorial y enfoque",
                controles="Ratón / Clic / ESC = Menú",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo 4", "MenteActiva-Memoria_Sensorial_grupo_4-main", "assets", "cover", "launcher_cover.png")
            ),
            TarjetaJuego(
                "SUPER QUIZ 64", "Asociación Auditiva (Grupo 5)",
                (255, 120, 50), "cartas",
                clave_juego="super_quiz_64",
                descripcion="Escucha con atención y asocia el sonido con su respectiva imagen en cada ronda.",
                habilidad="Asociación auditiva y memoria",
                controles="Ratón / Clic / ESC = Salir",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo 5", "superQuiz64.py", "portada.png")
            ),
            TarjetaJuego(
                "BINGO CALMA", "Estimulación Sensorial (Grupo 6)",
                (47, 168, 155), "bingo",
                clave_juego="bingo_calma",
                descripcion="Bingo temático y sensorial para estimulación cognitiva, con 75 conceptos familiares y figuras ganadoras.",
                habilidad="Atención sostenida y memoria",
                controles="Ratón / Clic / ESC = Salir",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo 6", "Proyecto taller de abstraccion eugenio", "portada.png")
            ),
            TarjetaJuego(
                "REMEMBER ME", "Sopa de Letras (Grupo 7)",
                (158, 140, 214), "laberinto",
                clave_juego="remember_me",
                descripcion="Sopa de letras que ejercita la agilidad mental y la concentración.",
                habilidad="Agilidad mental y atención",
                controles="Ratón / Teclado",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo 7", "remember-me-main", "assets", "portada.png")
            ),
            TarjetaJuego(
                "JUEGO DE MEMORIA", "Estados de Venezuela (Grupo 8)",
                (155, 89, 182), "cartas",
                clave_juego="memory_grupo_8",
                descripcion="Encuentra las parejas de cartas iguales de los estados de Venezuela antes de que acabe el tiempo.",
                habilidad="Memoria visual y concentración",
                controles="Ratón / Clic / ESC = Salir",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo 8", "tallergrupo8-main", "portada.png")
            ),
            TarjetaJuego(
                "LETRA A LETRA", "Palabras Cruzadas (Grupo 9)",
                (86, 190, 200), "laberinto",
                clave_juego="letra_a_letra",
                descripcion="Juego de palabras adaptado para estimulación cognitiva y memoria semántica.",
                habilidad="Lenguaje y memoria",
                controles="Teclado / Ratón",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo9", "Letra a letra", "preview.png")
            ),
            TarjetaJuego(
                "ENCUENTRA AL INTRUSO", "Discriminación Visual (Grupo 10)",
                (238, 104, 34), "bingo",
                clave_juego="encuentra_al_intruso",
                descripcion="Observa la cuadrícula con atención y encuentra al objeto intruso en cada ronda.",
                habilidad="Atención y discriminación",
                controles="Ratón / Clic",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo 10", "prueba-practica-main", "portada.png")
            ),
            TarjetaJuego(
                "BALL SORT", "Clasificación y Lógica (Grupo 11)",
                (52, 152, 219), "laberinto",
                clave_juego="ball_sort",
                descripcion="Organiza las bolas para que cada tubo contenga únicamente bolas del mismo color.",
                habilidad="Planificación y razonamiento lógico",
                controles="Ratón / Clic / Teclas 1-7",
                portada_path=os.path.join(CARPETA_BASE, "juegos", "grupo 11", "BallSort", "BallSort", "portada.png")
            ),
        ]

        self.indice_actual = 0
        self.total_juegos = len(self.juegos)

        # Animación de slide
        self.animando = False
        self.offset_x = 0.0         # desplazamiento actual en px
        self.direccion_slide = 0    # -1 izquierda, +1 derecha
        self.indice_siguiente = 0

        # Centro de la tarjeta
        self.tarjeta_cx = ANCHO // 2
        self.tarjeta_cy = 340

        # Flechas de navegación
        self.flecha_izq = FlechaNavegacion((self.tarjeta_cx - 250, self.tarjeta_cy), -1, tamano=36)
        self.flecha_der = FlechaNavegacion((self.tarjeta_cx + 250, self.tarjeta_cy), +1, tamano=36)

        # Indicadores de página
        self.indicador = IndicadorPagina(580, self.total_juegos)

        # Mensaje temporal
        self.mensaje = None
        self.mensaje_t = 0.0

    def _navegar(self, direccion):
        """Inicia la animación de slide. direccion: -1 o +1."""
        if self.animando:
            return
        siguiente = (self.indice_actual + direccion) % self.total_juegos
        self.indice_siguiente = siguiente
        self.direccion_slide = direccion
        self.offset_x = 0.0
        self.animando = True

    def _navegar_a(self, destino):
        """Navega directamente a un índice específico."""
        if self.animando or destino == self.indice_actual or destino < 0 or destino >= self.total_juegos:
            return
        direccion = 1 if destino > self.indice_actual else -1
        self.indice_siguiente = destino
        self.direccion_slide = direccion
        self.offset_x = 0.0
        self.animando = True

    def manejar_click(self, pos):
        if self.animando:
            return

        if self.boton_volver.contiene(pos):
            self.manager.cambiar_estado("menu")
            return

        if self.flecha_izq.contiene(pos):
            self._navegar(-1)
            return
        if self.flecha_der.contiene(pos):
            self._navegar(1)
            return

        # Clic en indicadores de página inferiores
        idx_indicador = self.indicador.contiene_indice(pos)
        if idx_indicador is not None:
            self._navegar_a(idx_indicador)
            return

        # Verificar clic en la tarjeta actual o en su botón JUGAR
        rect_tarjeta = pygame.Rect(0, 0, TarjetaJuego.ANCHO_CARRUSEL, TarjetaJuego.ALTO_CARRUSEL)
        rect_tarjeta.center = (self.tarjeta_cx, self.tarjeta_cy)
        click_tarjeta = rect_tarjeta.collidepoint(pos)
        click_boton = hasattr(self, '_boton_jugar_rect') and self._boton_jugar_rect and self._boton_jugar_rect.collidepoint(pos)

        if click_tarjeta or click_boton:
            tarjeta = self.juegos[self.indice_actual]
            if tarjeta.disponible and tarjeta.clave_juego:
                exito, msg = self.manager.launcher.lanzar_juego(
                    tarjeta.clave_juego, tarjeta.titulo
                )
                self.mensaje = msg
            else:
                self.mensaje = "Próximamente disponible"
            self.mensaje_t = 3.0

    def manejar_tecla(self, key):
        if self.animando:
            return True
        if key == pygame.K_LEFT:
            self._navegar(-1)
            return True
        elif key == pygame.K_RIGHT:
            self._navegar(1)
            return True
        elif key == pygame.K_ESCAPE:
            self.manager.cambiar_estado("menu")
            return True
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            tarjeta = self.juegos[self.indice_actual]
            if tarjeta.disponible and tarjeta.clave_juego:
                exito, msg = self.manager.launcher.lanzar_juego(
                    tarjeta.clave_juego, tarjeta.titulo
                )
                self.mensaje = msg
                self.mensaje_t = 3.0
            return True
        return False

    def actualizar(self, dt):
        # Animación de slide
        if self.animando:
            avance = self.VELOCIDAD_SLIDE * dt
            self.offset_x += avance
            if self.offset_x >= self.ANCHO_SLIDE:
                self.offset_x = 0.0
                self.indice_actual = self.indice_siguiente
                self.animando = False

        # Mensaje temporal
        if self.mensaje_t > 0:
            self.mensaje_t -= dt
            if self.mensaje_t <= 0:
                self.mensaje = None

    def dibujar(self, renderer, superficie, t, mouse_pos):
        # Título animado
        renderer.dibujar_palabra_animada(
            superficie, "¿QUE QUIERES JUGAR?", self.manager.fuente_titulo_seleccion,
            ANCHO // 2, 80, PALETA_TITULO, t, amplitud=4, velocidad=2.0,
        )

        fuentes = {
            "titulo": self.manager.fuente_tarjeta_titulo,
            "subtitulo": self.manager.fuente_tarjeta_sub,
            "descripcion": self.manager.fuente_descripcion,
            "badge": self.manager.fuente_badge,
            "jugar": self.manager.fuente_jugar,
        }

        cx = self.tarjeta_cx
        cy = self.tarjeta_cy

        if self.animando:
            # Calcular easing (suave al inicio y final)
            progreso = self.offset_x / self.ANCHO_SLIDE
            ease = progreso * progreso * (3.0 - 2.0 * progreso)  # smoothstep
            desplaz = ease * self.ANCHO_SLIDE

            # Tarjeta actual se va
            cx_actual = cx - self.direccion_slide * desplaz
            alpha_actual = max(0, 255 - int(255 * ease))

            # Tarjeta siguiente entra
            cx_siguiente = cx + self.direccion_slide * (self.ANCHO_SLIDE - desplaz)

            # Dibujar tarjeta actual (se va)
            capa_actual = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            self.juegos[self.indice_actual].dibujar_carrusel(
                capa_actual, int(cx_actual), cy, t, (-100, -100), fuentes, self.indice_actual
            )
            capa_actual.set_alpha(alpha_actual)
            superficie.blit(capa_actual, (0, 0))

            # Dibujar tarjeta siguiente (entra)
            capa_siguiente = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            self._boton_jugar_rect = self.juegos[self.indice_siguiente].dibujar_carrusel(
                capa_siguiente, int(cx_siguiente), cy, t, (-100, -100), fuentes, self.indice_siguiente
            )
            capa_siguiente.set_alpha(min(255, int(255 * ease)))
            superficie.blit(capa_siguiente, (0, 0))
        else:
            # Dibujar tarjeta actual centrada
            self._boton_jugar_rect = self.juegos[self.indice_actual].dibujar_carrusel(
                superficie, cx, cy, t, mouse_pos, fuentes, self.indice_actual
            )

        # Flechas de navegación
        self.flecha_izq.dibujar(superficie, t, mouse_pos)
        self.flecha_der.dibujar(superficie, t, mouse_pos)

        # Indicadores de página
        indice_visual = self.indice_siguiente if self.animando else self.indice_actual
        self.indicador.dibujar(superficie, indice_visual)

        # Botón volver
        self.boton_volver.dibujar(renderer, superficie, t, mouse_pos)

        # Mensaje temporal (lanzamiento / error)
        if self.mensaje:
            alpha = min(255, int(255 * min(self.mensaje_t, 0.4) / 0.4)) if self.mensaje_t < 0.4 else 255
            globo = self.manager.fuente_tarjeta_sub.render(self.mensaje, True, (255, 255, 255))
            fondo_rect = globo.get_rect(center=(ANCHO // 2, 620)).inflate(46, 28)
            capa = pygame.Surface(fondo_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(capa, (108, 92, 160, alpha), capa.get_rect(), border_radius=20)
            superficie.blit(capa, fondo_rect.topleft)
            globo.set_alpha(alpha)
            superficie.blit(globo, globo.get_rect(center=fondo_rect.center))


class StateManager:
    def __init__(self, renderer, launcher=None, audio=None):
        self.renderer = renderer
        self.launcher = launcher
        self.audio = audio
        self.juego_corriendo = False

        # Fuentes existentes
        self.fuente_logo = cargar_fuente("Baloo2-SemiBold.ttf", 24)
        self.fuente_titulo = cargar_fuente("Fredoka-Bold.ttf", 74)
        self.fuente_subtitulo = cargar_fuente("Baloo2-SemiBold.ttf", 32)
        self.fuente_tagline = cargar_fuente("BubblegumSans-Regular.ttf", 22)
        self.fuente_boton = cargar_fuente("Baloo2-ExtraBold.ttf", 30)
        self.fuente_boton_volver = cargar_fuente("Baloo2-SemiBold.ttf", 20)
        self.fuente_titulo_seleccion = cargar_fuente("Fredoka-Bold.ttf", 38)

        # Fuentes del carrusel
        self.fuente_tarjeta_titulo = cargar_fuente("Baloo2-ExtraBold.ttf", 28)
        self.fuente_tarjeta_sub = cargar_fuente("Baloo2-SemiBold.ttf", 18)
        self.fuente_descripcion = cargar_fuente("Baloo2-SemiBold.ttf", 15)
        self.fuente_badge = cargar_fuente("Baloo2-ExtraBold.ttf", 13)
        self.fuente_jugar = cargar_fuente("Baloo2-ExtraBold.ttf", 22)

        self.decoraciones = [Decoracion(ANCHO, ALTO) for _ in range(16)]

        self.estados = {
            "menu": MenuState(self),
            "seleccion": SeleccionState(self)
        }
        self.estado_actual = self.estados["menu"]

        self.transicionando = False
        self.transicion_t = 0.0
        self.transicion_duracion = 0.55
        self.estado_destino = None

    def cambiar_estado(self, nombre_estado):
        if not self.transicionando:
            self.transicionando = True
            self.transicion_t = 0.0
            self.estado_destino = self.estados[nombre_estado]

    def manejar_click(self, pos):
        if not self.transicionando:
            self.estado_actual.manejar_click(pos)

    def manejar_tecla(self, key):
        """Delega la tecla al estado actual. Devuelve True si fue manejada."""
        if not self.transicionando:
            return self.estado_actual.manejar_tecla(key)
        return False

    def actualizar(self, dt):
        for decoracion in self.decoraciones:
            decoracion.actualizar(dt)
        self.estado_actual.actualizar(dt)
        if self.transicionando:
            self.transicion_t += dt
            if self.transicion_t >= self.transicion_duracion / 2 and self.estado_destino is not None:
                self.estado_actual = self.estado_destino
                self.estado_destino = None
            if self.transicion_t >= self.transicion_duracion:
                self.transicionando = False
                self.transicion_t = 0.0
                
        esta_corriendo = self.launcher.juego_en_ejecucion() if self.launcher else False
        if esta_corriendo and not self.juego_corriendo:
            if self.audio:
                self.audio.pausar()
            self.juego_corriendo = True
        elif not esta_corriendo and self.juego_corriendo:
            if self.audio:
                self.audio.reanudar()
            self.juego_corriendo = False

    def dibujar(self, superficie, t, mouse_pos):
        self.renderer.dibujar_fondo()
        for decoracion in self.decoraciones:
            decoracion.dibujar(self.renderer, superficie, t, mouse_pos)
        self.estado_actual.dibujar(self.renderer, superficie, t, mouse_pos)
        self._dibujar_logo(superficie)
        if self.transicionando:
            progreso = self.transicion_t / self.transicion_duracion
            alpha = int(255 * math.sin(progreso * math.pi))
            velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            velo.fill((255, 250, 240, max(alpha, 0)))
            superficie.blit(velo, (0, 0))

    def _dibujar_logo(self, superficie):
        texto = self.fuente_logo.render("Abre Tu Mente", True, COLOR_LOGO)
        x = ANCHO - texto.get_width() - 34
        y = 20
        superficie.blit(texto, (x, y))
        pygame.draw.circle(superficie, (255, 209, 102), (x - 14, y + 12), 6)
