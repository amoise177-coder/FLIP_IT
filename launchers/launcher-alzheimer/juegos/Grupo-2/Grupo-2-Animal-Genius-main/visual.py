import pygame
from constants import const
from gestor_recursos import GestorRecursos
from ui_components import (
    crear_etiqueta_glossy,
    crear_boton_glossy,
    dibujar_indicadores_progreso, 
    crear_boton_capsula_volver,
)
import visual_menu
import visual_partida


class RenderizadorJuego:

    def __init__(self):
        self.recursos = GestorRecursos()
        self.fuente_texto = self.recursos.fuente_texto
        self.fuente_titulo = self.recursos.fuente_titulo

        self.volumen_musica = 0.5
        self.volumen_efectos = 0.5

        self._indice_seleccion_usuario = None
        self._es_respuesta_correcta = None

        self._inicializar_rectangulos()
        self._inicializar_botones_estaticos()
        self._inicializar_badges_biomas()

        self._opciones_actuales = ["", "", "", ""]
        self._surfaces_opciones_actuales = []
        self._ultima_carta_procesada = None
        self._imagen_actual_escalada = None
        self._bloques_rasca = []
        self._total_bloques_inicial = 0
        
        self.surf_logo = self.recursos.cargar_logo(ancho=450, alto=220)

    def reiniciar_estado_seleccion(self) -> None:
        self._indice_seleccion_usuario = None
        self._es_respuesta_correcta = None

    def marcar_seleccion_usuario(self, indice: int, es_correcto: bool) -> None:
        self._indice_seleccion_usuario = indice
        self._es_respuesta_correcta = es_correcto

    def _inicializar_rectangulos(self) -> None:
        self.rect_btn_jugar = pygame.Rect(const.ANCHO_PANTALLA // 2 - 150, 315, 300, 55)
        self.rect_slider_musica = pygame.Rect(const.ANCHO_PANTALLA // 2 - 140, 405, 280, 22)
        self.rect_slider_efectos = pygame.Rect(const.ANCHO_PANTALLA // 2 - 140, 485, 280, 22)
        self.rect_btn_salir = pygame.Rect(const.ANCHO_PANTALLA // 2 - 150, 535, 300, 50)

        w_card, h_card = 190, 180
        espacio_x, espacio_y = 30, 20
        ancho_fila1 = (3 * w_card) + (2 * espacio_x)
        inicio_x_fila1 = (const.ANCHO_PANTALLA - ancho_fila1) // 2
        ancho_fila2 = (2 * w_card) + (1 * espacio_x)
        inicio_x_fila2 = (const.ANCHO_PANTALLA - ancho_fila2) // 2
        y_fila1 = 130
        y_fila2 = y_fila1 + h_card + espacio_y

        self.rects_zonas_tarjetas = {
            "pradera": pygame.Rect(inicio_x_fila1, y_fila1, w_card, h_card),
            "bosque":  pygame.Rect(inicio_x_fila1 + w_card + espacio_x, y_fila1, w_card, h_card),
            "selva":   pygame.Rect(inicio_x_fila1 + (w_card + espacio_x) * 2, y_fila1, w_card, h_card),
            "artico":  pygame.Rect(inicio_x_fila2, y_fila2, w_card, h_card),
            "oceano":  pygame.Rect(inicio_x_fila2 + w_card + espacio_x, y_fila2, w_card, h_card),
        }

        self.rects_modos = {
            "normal": pygame.Rect(const.ANCHO_PANTALLA // 2 - 175, 220, 350, 55),
            "preguntas": pygame.Rect(const.ANCHO_PANTALLA // 2 - 175, 295, 350, 55),
            "rasca": pygame.Rect(const.ANCHO_PANTALLA // 2 - 175, 370, 350, 55),
        }

        ancho_b, alto_b, espacio_x_op = 340, 52, 24
        inicio_x_op = (const.ANCHO_PANTALLA - ((ancho_b * 2) + espacio_x_op)) // 2
        y_arriba, y_abajo = 495, 558

        self.rects_opciones = [
            pygame.Rect(inicio_x_op, y_arriba, ancho_b, alto_b),
            pygame.Rect(inicio_x_op + ancho_b + espacio_x_op, y_arriba, ancho_b, alto_b),
            pygame.Rect(inicio_x_op, y_abajo, ancho_b, alto_b),
            pygame.Rect(inicio_x_op + ancho_b + espacio_x_op, y_abajo, ancho_b, alto_b),
        ]

        self.rect_btn_si = pygame.Rect(const.ANCHO_PANTALLA // 2 - 200, 490, 180, 65)
        self.rect_btn_no = pygame.Rect(const.ANCHO_PANTALLA // 2 + 20, 490, 180, 65)
        self.rect_btn_reiniciar = pygame.Rect(const.ANCHO_PANTALLA // 2 - 150, 465, 300, 60)

        ancho_v, alto_v = 180, 48
        self.rect_btn_volver = pygame.Rect((const.ANCHO_PANTALLA - ancho_v) // 2, 535, ancho_v, alto_v)

    def _inicializar_botones_estaticos(self) -> None:
        self.surf_btn_jugar = crear_boton_glossy("Jugar", self.fuente_titulo, 300, 55, (110, 220, 90), (35, 130, 45))
        self.surf_btn_salir = crear_boton_glossy("Salir", self.fuente_titulo, 300, 50, (240, 65, 65), (150, 20, 20))
        self.surfs_btn_modos = {
            "normal": crear_boton_glossy("Clásico", self.fuente_texto, 350, 55, (85, 165, 255), (20, 65, 175)),
            "preguntas": crear_boton_glossy("¿Sí o No?", self.fuente_texto, 350, 55, (85, 165, 255), (20, 65, 175)),
            "rasca": crear_boton_glossy("Rasca y mira", self.fuente_texto, 350, 55, (85, 165, 255), (20, 65, 175)),
        }
        self.surf_btn_si = crear_boton_glossy("Sí", self.fuente_titulo, 180, 65, (110, 220, 90), (35, 130, 45))
        self.surf_btn_no = crear_boton_glossy("No", self.fuente_titulo, 180, 65, (240, 65, 65), (150, 20, 20))
        self.surf_btn_reiniciar = crear_boton_glossy("Volver al menú", self.fuente_texto, 300, 60, (85, 165, 255), (20, 65, 175))
        self.surf_btn_volver = crear_boton_capsula_volver("< Volver", self.fuente_texto, ancho=180, alto=48)

    def _inicializar_badges_biomas(self) -> None:
        nombres_amigables = {"artico": "Ártico", "oceano": "Océano", "pradera": "Pradera", "selva": "Selva", "bosque": "Bosque"}
        self.badges_zonas = {}
        for zona, nombre in nombres_amigables.items():
            colores = const.COLORES_BIOMAS.get(zona, {"arriba": (180, 180, 180), "abajo": (80, 80, 80)})
            self.badges_zonas[zona] = crear_etiqueta_glossy(nombre, self.fuente_texto, colores["arriba"], colores["abajo"])

    def dibujar_boton_con_hover(self, pantalla: pygame.Surface, superficie_btn: pygame.Surface, rect_btn: pygame.Rect, pos_mouse: tuple[int, int]) -> None:
        sombra_base = pygame.Surface(rect_btn.size, pygame.SRCALPHA)
        pygame.draw.rect(sombra_base, (0, 0, 0, 50), (0, 0, rect_btn.width, rect_btn.height), border_radius=rect_btn.height // 2)
        pantalla.blit(sombra_base, (rect_btn.x, rect_btn.y + 4))

        if rect_btn.collidepoint(pos_mouse):
            ancho_hover, alto_hover = int(rect_btn.width * 1.06), int(rect_btn.height * 1.06)
            btn_escalado = pygame.transform.smoothscale(superficie_btn, (ancho_hover, alto_hover)).copy()
            sombra = pygame.Surface(btn_escalado.get_size(), flags=pygame.SRCALPHA)
            sombra.fill((235, 235, 235, 255))
            btn_escalado.blit(sombra, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            rect_hover = btn_escalado.get_rect(center=rect_btn.center)
            rect_hover.y -= 2
            pantalla.blit(btn_escalado, rect_hover)
        else:
            pantalla.blit(superficie_btn, rect_btn)

    def _dibujar_letrero_titulo(self, pantalla: pygame.Surface, texto: str, y_centro: int = 55, ancho: int = 460) -> None:
        surf_cartel = pygame.Surface((ancho, 56), pygame.SRCALPHA)
        pygame.draw.rect(surf_cartel, (0, 0, 0, 40), (0, 5, ancho, 56), border_radius=28)
        pygame.draw.rect(surf_cartel, (255, 255, 255, 240), (0, 0, ancho, 56), border_radius=28)
        pygame.draw.rect(surf_cartel, (255, 195, 45), (0, 0, ancho, 56), width=4, border_radius=28)
        titulo = self.fuente_titulo.render(texto, True, const.COLOR_TEXTO_DARK)
        surf_cartel.blit(titulo, titulo.get_rect(center=(ancho // 2, 28)))
        pantalla.blit(surf_cartel, surf_cartel.get_rect(center=(const.ANCHO_PANTALLA // 2, y_centro)))

    # --- MENÚ PRINCIPAL ---
    def dibujar_menu_principal(self, pantalla) -> None:
        visual_menu.dibujar_menu_principal(self, pantalla)

    def manejar_eventos_menu_principal(self, evento) -> str | None:
        pos = pygame.mouse.get_pos()
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect_btn_jugar.collidepoint(pos): return "jugar"
            elif self.rect_btn_salir.collidepoint(pos): return "salir"
                
        if pygame.mouse.get_pressed()[0]:
            if self.rect_slider_musica.collidepoint(pos):
                rel_x = max(0, min(pos[0] - self.rect_slider_musica.x, self.rect_slider_musica.width))
                self.volumen_musica = rel_x / self.rect_slider_musica.width
            elif self.rect_slider_efectos.collidepoint(pos):
                rel_x = max(0, min(pos[0] - self.rect_slider_efectos.x, self.rect_slider_efectos.width))
                self.volumen_efectos = rel_x / self.rect_slider_efectos.width
        return None

    def obtener_clic_menu_principal(self, pos_mouse: tuple[int, int]) -> bool:
        return self.rect_btn_jugar.collidepoint(pos_mouse)

    def obtener_clic_boton_salir(self, pos_mouse: tuple[int, int]) -> bool:
        return self.rect_btn_salir.collidepoint(pos_mouse)

    # --- ZONAS Y MODOS ---
    def dibujar_menu_zonas(self, pantalla) -> None:
        visual_menu.dibujar_menu_zonas(self, pantalla)

    def obtener_clic_zona(self, pos_mouse: tuple[int, int]) -> str | None:
        for bioma, rect in self.rects_zonas_tarjetas.items():
            if rect.collidepoint(pos_mouse): return bioma
        return None

    def dibujar_menu_modos(self, pantalla) -> None:
        pos_mouse = pygame.mouse.get_pos()
        fondo = self.recursos.fondos.get("modos")
        pantalla.blit(fondo, (0, 0)) if fondo else pantalla.fill((230, 240, 250))
        self._dibujar_letrero_titulo(pantalla, "¡Selecciona un modo de juego!", y_centro=80, ancho=480)

        ancho_p, alto_p = 440, 280
        x_p, y_p = (const.ANCHO_PANTALLA // 2) - (ancho_p // 2), 170
        surf_panel = pygame.Surface((ancho_p, alto_p), pygame.SRCALPHA)
        pygame.draw.rect(surf_panel, (0, 0, 0, 35), (0, 6, ancho_p, alto_p), border_radius=25)
        pygame.draw.rect(surf_panel, (255, 255, 255, 215), (0, 0, ancho_p, alto_p), border_radius=25)
        pantalla.blit(surf_panel, (x_p, y_p))

        for idx, (modo, rect) in enumerate(self.rects_modos.items(), start=1):
            self.dibujar_boton_con_hover(pantalla, self.surfs_btn_modos[modo], rect, pos_mouse)
            cx_badge, cy_badge = rect.left - 15, rect.centery
            pygame.draw.circle(pantalla, (255, 200, 50), (cx_badge, cy_badge), 20)
            pygame.draw.circle(pantalla, (255, 255, 255), (cx_badge, cy_badge), 20, width=3)
            txt_num = self.fuente_titulo.render(str(idx), True, const.COLOR_TEXTO_DARK)
            pantalla.blit(txt_num, txt_num.get_rect(center=(cx_badge, cy_badge)))

        self.dibujar_boton_con_hover(pantalla, self.surf_btn_volver, self.rect_btn_volver, pos_mouse)

    def obtener_clic_menu_modos(self, pos_mouse: tuple[int, int]) -> str | None:
        for modo, rect in self.rects_modos.items():
            if rect.collidepoint(pos_mouse): return modo
        return None

    def obtener_clic_boton_volver(self, pos_mouse: tuple[int, int]) -> bool:
        return self.rect_btn_volver.collidepoint(pos_mouse)

    # --- RASCA Y GANA ---
    def _inicializar_grilla_rasca(self) -> None:
        self._bloques_rasca = []
        ancho_img, alto_img = 420, 290
        x_inicio, y_inicio, tamanio = (const.ANCHO_PANTALLA // 2) - (ancho_img // 2), 135, 6
        for x in range(x_inicio, x_inicio + ancho_img, tamanio):
            for y in range(y_inicio, y_inicio + alto_img, tamanio):
                self._bloques_rasca.append(pygame.Rect(x, y, tamanio, tamanio))
        self._total_bloques_inicial = len(self._bloques_rasca)

    def procesar_rasca_mouse(self, pos_mouse: tuple[int, int], max_bloques_revelar: int) -> bool:
        if (self._total_bloques_inicial - len(self._bloques_rasca)) >= int(self._total_bloques_inicial * 0.12):
            return False
        radio_rascado = 10
        self._bloques_rasca = [
            b for b in self._bloques_rasca if not (
                b.collidepoint(pos_mouse) or 
                (abs(b.centerx - pos_mouse[0]) < radio_rascado and abs(b.centery - pos_mouse[1]) < radio_rascado)
            )
        ]
        return True

    def revelar_imagen_completa(self) -> None:
        """Vacía completamente los bloques de la capa de rasca para mostrar la imagen completa."""
        if hasattr(self, "_bloques_rasca") and isinstance(self._bloques_rasca, list):
            self._bloques_rasca.clear()

    # --- INTERFAZ DE PARTIDA Y RESULTADOS ---
    def dibujar_interfaz(self, pantalla, carta_actual, puntuacion: int, mensaje: str, revelada: bool = False, modo: str = "normal", tiempo_restante: float = 0.0, tiempo_agotado: bool = False) -> None:
        visual_partida.dibujar_interfaz(self, pantalla, carta_actual, puntuacion, mensaje, revelada, modo, tiempo_restante, tiempo_agotado)

    def obtener_indice_y_opcion_clic(self, pos_mouse: tuple[int, int]) -> tuple[int | None, str | None]:
        for i, rect in enumerate(self.rects_opciones):
            if rect.collidepoint(pos_mouse): return i, self._opciones_actuales[i]
        return None, None

    def obtener_opcion_clic(self, pos_mouse: tuple[int, int]) -> str | None:
        _, opcion = self.obtener_indice_y_opcion_clic(pos_mouse)
        return opcion

    def dibujar_ronda_sino(self, pantalla, pregunta_actual, puntuacion: int, mensaje: str) -> None:
        visual_partida.dibujar_ronda_sino(self, pantalla, pregunta_actual, puntuacion, mensaje)

    def obtener_clic_sino(self, pos_mouse: tuple[int, int]) -> bool | None:
        if self.rect_btn_si.collidepoint(pos_mouse): return True
        if self.rect_btn_no.collidepoint(pos_mouse): return False
        return None

    def dibujar_pantalla_resultados(self, pantalla, puntuacion_final: int, total_posible: int, aciertos: int, fallos: int) -> None:
        visual_menu.dibujar_pantalla_resultados(self, pantalla, puntuacion_final, total_posible, aciertos, fallos)

    def obtener_clic_resultados(self, pos_mouse: tuple[int, int]) -> bool:
        return self.rect_btn_reiniciar.collidepoint(pos_mouse)

    def dibujar_indicadores_progreso(self, pantalla, total_preguntas: int, resultados: list[str]) -> None:
        dibujar_indicadores_progreso(pantalla, const.ANCHO_PANTALLA // 2, 440, total_preguntas, resultados)
        
