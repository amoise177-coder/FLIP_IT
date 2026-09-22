import sys
import pygame
from pathlib import Path
from niveles import GeneradorNiveles
from fondo import FondoVideoOpenCV
from puntuaciones import GestorPuntuaciones
import ui

pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Aviso: Dispositivo de audio no detectado ({e}).")

info_pantalla = pygame.display.Info()
ANCHO = info_pantalla.current_w
ALTO = info_pantalla.current_h

pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)
pygame.display.set_caption("Super Quiz 64")
reloj = pygame.time.Clock()

RUTA_BASE = Path(__file__).resolve().parent
RUTA_VIDEO = RUTA_BASE / "assets" / "imagenes" / "fondo.mp4"

RUTA_MUSICA_AMBIENTE = RUTA_BASE / "assets" / "audios" / "ambiente.mp3"

if not RUTA_MUSICA_AMBIENTE.exists():
    for ext in [".wav", ".ogg", ".mp4", ".m4a"]:
        alt = RUTA_BASE / "assets" / "audios" / f"ambiente{ext}"
        if alt.exists():
            RUTA_MUSICA_AMBIENTE = alt
            break

RUTA_CORRECTO = RUTA_BASE / "assets" / "audios" / "correcto.mp3"
RUTA_INCORRECTO = RUTA_BASE / "assets" / "audios" / "incorrecto.mp3"

SND_CORRECTO = pygame.mixer.Sound(str(RUTA_CORRECTO)) if RUTA_CORRECTO.exists() else None
SND_INCORRECTO = pygame.mixer.Sound(str(RUTA_INCORRECTO)) if RUTA_INCORRECTO.exists() else None

reproductor_fondo = FondoVideoOpenCV(RUTA_VIDEO, ANCHO, ALTO)

fuente_titulo = pygame.font.SysFont("Trebuchet MS", int(ALTO * 0.055), bold=True)
fuente_subtitulo = pygame.font.SysFont("Trebuchet MS", int(ALTO * 0.040), bold=True)
fuente_texto = pygame.font.SysFont("Trebuchet MS", int(ALTO * 0.032))

def gestionar_musica_menu(estado_juego):
    """Maneja la reproducción de la música de fondo según la pantalla actual."""
    if RUTA_MUSICA_AMBIENTE.exists():
        if estado_juego in ["MENU", "SELECCION_MODO", "RECORDS", "INSTRUCCIONES", "RESULTADOS"]:
            if not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.load(str(RUTA_MUSICA_AMBIENTE))
                    pygame.mixer.music.set_volume(0.18)  
                    pygame.mixer.music.play(-1) 
                except Exception as e:
                    print(f"No se pudo reproducir la música de ambiente: {e}")
        elif estado_juego == "JUGANDO":
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()

class TarjetaOpcion:
    def __init__(self, x, y, ancho, alto, elemento, identificador):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.elemento = elemento
        self.identificador = identificador
        self.radio_borde = 28
        self.estado_feedback = None 
        
        tam_etiqueta = int(alto * 0.16)
        self.btn_letra = ui.BotonEstiloFlipIt(
            x + (ancho // 2) - (tam_etiqueta // 2),
            y - int(tam_etiqueta * 0.55),
            tam_etiqueta,
            tam_etiqueta,
            self.identificador,
            ui.COLOR_ROJO_TOP,
            ui.COLOR_ROJO_BOTTOM,
            tamano_fuente=int(tam_etiqueta * 0.6)
        )

        if self.elemento:
            self.elemento.cargar_recursos(tamano=(ancho - 30, alto - int(tam_etiqueta) - 40))

    def dibujar(self, superficie):
        pos_mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(pos_mouse)

        color_fondo = (255, 255, 255) if not hover else (240, 245, 255)
        color_borde = ui.COLOR_BORDE_TARJETA if not hover else (75, 150, 220)

        if self.estado_feedback == 'CORRECTO':
            color_fondo = (220, 248, 220)
            color_borde = (45, 180, 45)
        elif self.estado_feedback == 'INCORRECTO':
            color_fondo = (255, 225, 225)
            color_borde = (220, 50, 50)

        surf_tarjeta = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf_tarjeta, color_fondo, surf_tarjeta.get_rect(), border_radius=self.radio_borde)

        if self.elemento and self.elemento.imagen:
            rect_img = self.elemento.imagen.get_rect(center=(self.rect.width // 2, (self.rect.height // 2) - int(ALTO * 0.015)))
            surf_tarjeta.blit(self.elemento.imagen, rect_img)

        if self.elemento and hasattr(self.elemento, 'nombre'):
            fuente_nombre = pygame.font.SysFont("Trebuchet MS", int(ALTO * 0.028), bold=True)
            txt_nombre = fuente_nombre.render(str(self.elemento.nombre).capitalize(), True, ui.COLOR_TEXTO_TITULO)
            rect_txt = txt_nombre.get_rect(center=(self.rect.width // 2, self.rect.height - int(ALTO * 0.04)))
            surf_tarjeta.blit(txt_nombre, rect_txt)

        pygame.draw.rect(surf_tarjeta, color_borde, surf_tarjeta.get_rect(), width=6 if self.estado_feedback else 4, border_radius=self.radio_borde)

        superficie.blit(surf_tarjeta, self.rect.topleft)
        self.btn_letra.dibujar(superficie)

    def fue_cliqueada(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False

class JuegoMemoria:
    def __init__(self):
        self.generador = GeneradorNiveles()
        self.gestor_records = GestorPuntuaciones()
        self.estado = "MENU"
        self.modo_actual = "amistosa"
        self.partida = []
        self.indice_nivel = 0
        self.aciertos = 0
        self.desaciertos = 0
        self.tarjetas_opciones = []
        
        self.esperando_feedback = False
        self.tiempo_inicio_feedback = 0

        cx = ANCHO // 2
        cy = ALTO // 2
        w_btn = int(ANCHO * 0.32)
        h_btn = int(ALTO * 0.075)

        self.btn_jugar = ui.BotonEstiloFlipIt(cx - w_btn // 2, cy - int(ALTO * 0.06), w_btn, h_btn, "JUGAR", ui.COLOR_JUGAR_TOP, ui.COLOR_JUGAR_BOTTOM, tamano_fuente=int(ALTO * 0.035))
        self.btn_records = ui.BotonEstiloFlipIt(cx - w_btn // 2, cy + int(ALTO * 0.03), w_btn, h_btn, "Récords", ui.COLOR_COMO_JUGAR_TOP, ui.COLOR_COMO_JUGAR_BOTTOM, tamano_fuente=int(ALTO * 0.035))
        self.btn_como_juega = ui.BotonEstiloFlipIt(cx - w_btn // 2, cy + int(ALTO * 0.12), w_btn, h_btn, "Cómo se juega", ui.COLOR_COMO_JUGAR_TOP, ui.COLOR_COMO_JUGAR_BOTTOM, tamano_fuente=int(ALTO * 0.035))
        self.btn_salir = ui.BotonEstiloFlipIt(cx - w_btn // 2, cy + int(ALTO * 0.21), w_btn, h_btn, "Salir", ui.COLOR_SALIR_TOP, ui.COLOR_SALIR_BOTTOM, ui.COLOR_TEXTO_BOTON_OSCURO, ui.COLOR_BORDE_SALIR, tamano_fuente=int(ALTO * 0.035))

        self.btn_amistoso = ui.BotonEstiloFlipIt(cx - w_btn // 2, cy - int(ALTO * 0.04), w_btn, h_btn, "Amistoso (10 Niveles)", ui.COLOR_JUGAR_TOP, ui.COLOR_JUGAR_BOTTOM, tamano_fuente=int(ALTO * 0.032))
        self.btn_test = ui.BotonEstiloFlipIt(cx - w_btn // 2, cy + int(ALTO * 0.06), w_btn, h_btn, "Test (20 Niveles)", ui.COLOR_COMO_JUGAR_TOP, ui.COLOR_COMO_JUGAR_BOTTOM, tamano_fuente=int(ALTO * 0.032))

        self.btn_reproducir_audio = ui.BotonEstiloFlipIt(cx - int(ANCHO * 0.15), cy + int(ALTO * 0.24), int(ANCHO * 0.30), int(ALTO * 0.075), "Reproducir Sonido", ui.COLOR_COMO_JUGAR_TOP, ui.COLOR_COMO_JUGAR_BOTTOM, tamano_fuente=int(ALTO * 0.032), con_icono_play=True)

        self.btn_volver = ui.BotonEstiloFlipIt(cx - w_btn // 2, cy + int(ALTO * 0.38), w_btn, h_btn, "Volver al Menú", ui.COLOR_SALIR_TOP, ui.COLOR_SALIR_BOTTOM, ui.COLOR_TEXTO_BOTON_OSCURO, ui.COLOR_BORDE_SALIR, tamano_fuente=int(ALTO * 0.032))
        self.btn_regresar_resultados = ui.BotonEstiloFlipIt(cx - w_btn // 2, cy + int(ALTO * 0.22), w_btn, h_btn, "Regresar", ui.COLOR_JUGAR_TOP, ui.COLOR_JUGAR_BOTTOM, tamano_fuente=int(ALTO * 0.035))

        gestionar_musica_menu(self.estado)

    def iniciar_partida(self, modo):
        self.modo_actual = modo
        self.partida = self.generador.generar_partida(modo)
        self.indice_nivel = 0
        self.aciertos = 0
        self.desaciertos = 0
        self.esperando_feedback = False
        self.estado = "JUGANDO"
        gestionar_musica_menu(self.estado)
        self.cargar_nivel_actual()

    def cargar_nivel_actual(self):
        self.tarjetas_opciones.clear()
        if self.indice_nivel < len(self.partida):
            nivel = self.partida[self.indice_nivel]
            
            nivel.elemento_correcto.cargar_recursos()
            nivel.elemento_correcto.reproducir_sonido()

            opciones = [
                (nivel.opcion_a, 'A'),
                (nivel.opcion_b, 'B')
            ]

            w_card = int(ANCHO * 0.28)
            h_card = int(ALTO * 0.42)
            espaciado = int(ANCHO * 0.08)

            ancho_total = (2 * w_card) + espaciado
            start_x = (ANCHO - ancho_total) // 2
            pos_y = (ALTO // 2) - (h_card // 2) - int(ALTO * 0.02)

            for i, (elem, identificador) in enumerate(opciones):
                pos_x = start_x + i * (w_card + espaciado)
                tarjeta = TarjetaOpcion(pos_x, pos_y, w_card, h_card, elem, identificador)
                self.tarjetas_opciones.append(tarjeta)

    def registrar_respuesta(self, identificador):
        if self.esperando_feedback:
            return

        pygame.mixer.stop()
        nivel = self.partida[self.indice_nivel]
        es_correcta = nivel.es_correcta(identificador)

        for tarjeta in self.tarjetas_opciones:
            if tarjeta.identificador == identificador:
                tarjeta.estado_feedback = 'CORRECTO' if es_correcta else 'INCORRECTO'

        if es_correcta:
            self.aciertos += 1
            if SND_CORRECTO: SND_CORRECTO.play()
        else:
            self.desaciertos += 1
            if SND_INCORRECTO: SND_INCORRECTO.play()

        self.esperando_feedback = True
        self.tiempo_inicio_feedback = pygame.time.get_ticks()

    def actualizar_logica(self):
        gestionar_musica_menu(self.estado)

        if self.esperando_feedback:
            ahora = pygame.time.get_ticks()
            if ahora - self.tiempo_inicio_feedback >= 700:
                self.esperando_feedback = False
                self.indice_nivel += 1
                if self.indice_nivel < len(self.partida):
                    self.cargar_nivel_actual()
                else:
                    self.gestor_records.guardar_puntuacion(self.modo_actual, self.aciertos, len(self.partida))
                    self.estado = "RESULTADOS"
                    gestionar_musica_menu(self.estado)

    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                return False

            if self.estado == "MENU":
                if self.btn_jugar.fue_cliqueado(evento):
                    self.estado = "SELECCION_MODO"
                elif self.btn_records.fue_cliqueado(evento):
                    self.estado = "RECORDS"
                elif self.btn_como_juega.fue_cliqueado(evento):
                    self.estado = "INSTRUCCIONES"
                elif self.btn_salir.fue_cliqueado(evento):
                    return False

            elif self.estado == "SELECCION_MODO":
                if self.btn_amistoso.fue_cliqueado(evento):
                    self.iniciar_partida("amistosa")
                elif self.btn_test.fue_cliqueado(evento):
                    self.iniciar_partida("test")
                elif self.btn_volver.fue_cliqueado(evento):
                    self.estado = "MENU"

            elif self.estado in ["INSTRUCCIONES", "RECORDS"]:
                if self.btn_volver.fue_cliqueado(evento):
                    self.estado = "MENU"

            elif self.estado == "JUGANDO":
                if self.btn_volver.fue_cliqueado(evento):
                    pygame.mixer.stop()
                    self.estado = "MENU"
                    gestionar_musica_menu(self.estado)

                if not self.esperando_feedback:
                    if self.btn_reproducir_audio.fue_cliqueado(evento):
                        if self.indice_nivel < len(self.partida):
                            self.partida[self.indice_nivel].elemento_correcto.reproducir_sonido()

                    for tarjeta in self.tarjetas_opciones:
                        if tarjeta.fue_cliqueada(evento):
                            self.registrar_respuesta(tarjeta.identificador)

            elif self.estado == "RESULTADOS":
                if self.btn_regresar_resultados.fue_cliqueado(evento):
                    self.estado = "MENU"
                    gestionar_musica_menu(self.estado)

        return True

    def renderizar(self):
        frame_surface = reproductor_fondo.obtener_frame_surface()
        if frame_surface:
            pantalla.blit(frame_surface, (0, 0))
        else:
            pantalla.fill(ui.COLOR_FONDO_FALLBACK)

        cx = ANCHO // 2
        cy = ALTO // 2

        if self.estado in ["MENU", "SELECCION_MODO"]:
            w_card, h_card = int(ANCHO * 0.35), int(ALTO * 0.12)
            rect_card = pygame.Rect(cx - w_card // 2, cy - int(ALTO * 0.25), w_card, h_card)
            
            pygame.draw.rect(pantalla, ui.COLOR_TARJETA, rect_card, border_radius=20)
            pygame.draw.rect(pantalla, ui.COLOR_BORDE_TARJETA, rect_card, width=2, border_radius=20)

            txt_titulo = fuente_titulo.render("SUPER QUIZ 64", True, ui.COLOR_TEXTO_TITULO)
            pantalla.blit(txt_titulo, txt_titulo.get_rect(center=rect_card.center))

            if self.estado == "MENU":
                self.btn_jugar.dibujar(pantalla)
                self.btn_records.dibujar(pantalla)
                self.btn_como_juega.dibujar(pantalla)
                self.btn_salir.dibujar(pantalla)

            elif self.estado == "SELECCION_MODO":
                self.btn_amistoso.dibujar(pantalla)
                self.btn_test.dibujar(pantalla)
                self.btn_volver.dibujar(pantalla)

        elif self.estado == "RECORDS":
            rect_cuadro = pygame.Rect(cx - int(ANCHO * 0.32), cy - int(ALTO * 0.28), int(ANCHO * 0.64), int(ALTO * 0.52))
            pygame.draw.rect(pantalla, ui.COLOR_TARJETA, rect_cuadro, border_radius=20)
            pygame.draw.rect(pantalla, ui.COLOR_BORDE_TARJETA, rect_cuadro, width=2, border_radius=20)

            txt_rec = fuente_titulo.render("Mejores Puntuaciones", True, ui.COLOR_TEXTO_TITULO)
            pantalla.blit(txt_rec, txt_rec.get_rect(center=(cx, cy - int(ALTO * 0.20))))

            mejores = self.gestor_records.obtener_mejores()
            if not mejores:
                txt_vacio = fuente_texto.render("Aún no hay récords registrados.", True, ui.COLOR_TEXTO_SUBTITULO)
                pantalla.blit(txt_vacio, txt_vacio.get_rect(center=(cx, cy)))
            else:
                for i, r in enumerate(mejores):
                    linea = f"{i+1}. Modo: {r['modo']} - {r['aciertos']}/{r['total']} aciertos ({r['precision']}%)"
                    txt_linea = fuente_texto.render(linea, True, ui.COLOR_TEXTO_TITULO)
                    pantalla.blit(txt_linea, (cx - int(ANCHO * 0.25), cy - int(ALTO * 0.10) + (i * 35)))

            self.btn_volver.dibujar(pantalla)

        elif self.estado == "INSTRUCCIONES":
            rect_cuadro = pygame.Rect(cx - int(ANCHO * 0.32), cy - int(ALTO * 0.25), int(ANCHO * 0.64), int(ALTO * 0.38))
            pygame.draw.rect(pantalla, ui.COLOR_TARJETA, rect_cuadro, border_radius=20)
            pygame.draw.rect(pantalla, ui.COLOR_BORDE_TARJETA, rect_cuadro, width=2, border_radius=20)

            txt_inst = fuente_titulo.render("¿Cómo se juega?", True, ui.COLOR_TEXTO_TITULO)
            pantalla.blit(txt_inst, txt_inst.get_rect(center=(cx, cy - int(ALTO * 0.17))))

            linea1 = fuente_texto.render("1. Escucha atentamente el sonido reproducido.", True, ui.COLOR_TEXTO_TITULO)
            linea2 = fuente_texto.render("2. Elija la opción que le corresponda al audio.", True, ui.COLOR_TEXTO_TITULO)

            pantalla.blit(linea1, (cx - int(ANCHO * 0.27), cy - int(ALTO * 0.06)))
            pantalla.blit(linea2, (cx - int(ANCHO * 0.27), cy + int(ALTO * 0.01)))

            self.btn_volver.dibujar(pantalla)

        elif self.estado == "JUGANDO":
            txt_nivel = fuente_titulo.render(f"Nivel {self.indice_nivel + 1} de {len(self.partida)}", True, ui.COLOR_TEXTO_TITULO)
            pantalla.blit(txt_nivel, txt_nivel.get_rect(center=(cx, int(ALTO * 0.08))))

            for tarjeta in self.tarjetas_opciones:
                tarjeta.dibujar(pantalla)

            self.btn_reproducir_audio.dibujar(pantalla)
            self.btn_volver.dibujar(pantalla)

        elif self.estado == "RESULTADOS":
            rect_res = pygame.Rect(cx - int(ANCHO * 0.28), cy - int(ALTO * 0.28), int(ANCHO * 0.56), int(ALTO * 0.56))
            pygame.draw.rect(pantalla, ui.COLOR_TARJETA, rect_res, border_radius=25)
            pygame.draw.rect(pantalla, ui.COLOR_BORDE_TARJETA, rect_res, width=3, border_radius=25)

            txt_res_tit = fuente_titulo.render("Resultados de la Partida", True, ui.COLOR_TEXTO_TITULO)
            pantalla.blit(txt_res_tit, txt_res_tit.get_rect(center=(cx, cy - int(ALTO * 0.18))))

            total = len(self.partida)
            porcentaje = (self.aciertos / total) * 100 if total > 0 else 0

            txt_aciertos = fuente_subtitulo.render(f"Aciertos: {self.aciertos}", True, (45, 160, 45))
            txt_errores = fuente_subtitulo.render(f"Desaciertos: {self.desaciertos}", True, (210, 50, 50))
            txt_porcentaje = fuente_texto.render(f"Precisión: {porcentaje:.1f}%", True, ui.COLOR_TEXTO_SUBTITULO)

            pantalla.blit(txt_aciertos, txt_aciertos.get_rect(center=(cx, cy - int(ALTO * 0.07))))
            pantalla.blit(txt_errores, txt_errores.get_rect(center=(cx, cy + int(ALTO * 0.01))))
            pantalla.blit(txt_porcentaje, txt_porcentaje.get_rect(center=(cx, cy + int(ALTO * 0.08))))

            self.btn_regresar_resultados.dibujar(pantalla)

        pygame.display.flip()

    def ejecutar(self):
        """Método público para iniciar el juego."""
        ejecutando = True
        while ejecutando:
            ejecutando = self.procesar_eventos()
            self.actualizar_logica()
            self.renderizar()
            reloj.tick(60)

        reproductor_fondo.liberar()
        pygame.quit()
        sys.exit()