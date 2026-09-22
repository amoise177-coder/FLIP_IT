import sys
import random
import pygame
from logica import PartidaBingoCognitivo, Carton, ElementoTematico, NivelEstimulacion
from recursos import (
    BASE_DIR, ASSETS_DIR, ANCHO_VENTANA, ALTO_VENTANA,
    ESTADO_INICIO, ESTADO_SELECCION, ESTADO_JUEGO,
    COLOR_TEXTO_NAVY, COLOR_TEXTO_NAVY_DARK, COLOR_TEXTO_MUTED,
    COLOR_FONDO_BASE, COLOR_TEAL_BOTON, COLOR_TEAL_BORDE,
    COLOR_MENTA_ACTIVA, COLOR_LAVANDA_MARCADO, COLOR_AZUL_MARCADO_ICON,
    COLOR_BLANCO, COLOR_AMBAR_PAUSA, NOMBRES_COLUMNAS,
    Fuentes, GestorMusica, GestorAssets, inicializar_sistema_recursos
)


class BotonCalma:
    def __init__(self, rect, pre_dibujado=False, radio=16, circular=False):
        self.rect = rect
        self.pre_dibujado = pre_dibujado
        self.radio = radio
        self.circular = circular
        self.hovered = False

    def actualizar(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def dibujar_hover(self, superficie, alpha_halo=40, border_halo=160):
        if not self.hovered:
            return
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if self.circular:
            cx = self.rect.width // 2
            cy = self.rect.height // 2
            r = self.rect.width // 2
            pygame.draw.circle(overlay, (255, 255, 255, alpha_halo), (cx, cy), r)
            pygame.draw.circle(overlay, (255, 255, 255, border_halo), (cx, cy), r, width=3)
        else:
            pygame.draw.rect(overlay, (255, 255, 255, alpha_halo), (0, 0, self.rect.width, self.rect.height), border_radius=self.radio)
            pygame.draw.rect(overlay, (255, 255, 255, border_halo), (0, 0, self.rect.width, self.rect.height), width=3, border_radius=self.radio)
        superficie.blit(overlay, self.rect.topleft)

    def es_clickeado(self, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos)


class TableroCartonGUI:
    ANCHO = 474
    ALTO = 558
    ANCHO_CELDA = 80
    ALTO_CELDA = 80
    INICIO_X = 20
    INICIO_Y = 98
    ESPACIO_X = 10
    ESPACIO_Y = 10

    @staticmethod
    def dividir_texto_en_lineas(texto, fuente, max_ancho=72):
        if fuente.size(texto)[0] <= max_ancho:
            return [texto]

        palabras = texto.split()
        if len(palabras) <= 1:
            return [texto]
        elif len(palabras) == 2:
            return palabras
        else:
            mejor_div = [palabras[0], " ".join(palabras[1:])]
            mejor_max = max(fuente.size(mejor_div[0])[0], fuente.size(mejor_div[1])[0])

            for i in range(1, len(palabras)):
                l1 = " ".join(palabras[:i])
                l2 = " ".join(palabras[i:])
                mw = max(fuente.size(l1)[0], fuente.size(l2)[0])
                if mw < mejor_max:
                    mejor_max = mw
                    mejor_div = [l1, l2]

            return mejor_div

    def __init__(self, x, y, carton, indice):
        self.x = x
        self.y = y
        self.carton = carton
        self.indice = indice
        self.rect = pygame.Rect(x, y, self.ANCHO, self.ALTO)

    def obtener_celda_en_pos(self, mouse_pos):
        mx, my = mouse_pos
        for f in range(5):
            for c in range(5):
                cx = self.x + self.INICIO_X + c * (self.ANCHO_CELDA + self.ESPACIO_X)
                cy = self.y + self.INICIO_Y + f * (self.ALTO_CELDA + self.ESPACIO_Y)
                if cx <= mx < cx + self.ANCHO_CELDA and cy <= my < cy + self.ALTO_CELDA:
                    return f, c
        return None

    def contar_aciertos(self):
        return sum(1 for f in range(5) for c in range(5) if self.carton.esta_marcado(f, c))

    def dibujar(self, superficie, mouse_pos, elemento_actual_id):
        superficie.blit(GestorAssets.tablero, (self.x, self.y))

        aciertos = self.contar_aciertos()
        badge_w, badge_h = 136, 26
        badge_x = self.x + self.ANCHO - badge_w - 20
        badge_y = self.y + 16

        pygame.draw.rect(superficie, (255, 255, 255, 220), (badge_x, badge_y, badge_w, badge_h), border_radius=13)
        pygame.draw.rect(superficie, (111, 211, 191, 180), (badge_x, badge_y, badge_w, badge_h), width=1, border_radius=13)

        txt_carton_info = f"Cartón {self.indice + 1}  •  {aciertos} Ac."
        t_badge = Fuentes.subtitulo.render(txt_carton_info, True, COLOR_TEXTO_NAVY)
        superficie.blit(t_badge, t_badge.get_rect(center=(badge_x + badge_w // 2, badge_y + badge_h // 2)))

        celda_hover = self.obtener_celda_en_pos(mouse_pos)

        for fila in range(5):
            for col in range(5):
                cx = self.x + self.INICIO_X + col * (self.ANCHO_CELDA + self.ESPACIO_X)
                cy = self.y + self.INICIO_Y + fila * (self.ALTO_CELDA + self.ESPACIO_Y)

                if fila == 2 and col == 2:
                    continue

                esta_marcada = self.carton.esta_marcado(fila, col)
                elem = self.carton.obtener_elemento_en(fila, col)
                if not elem:
                    continue

                es_objetivo = (elemento_actual_id is not None and elem.id == elemento_actual_id and not esta_marcada)
                hover_activo = (celda_hover == (fila, col) and not esta_marcada)

                if esta_marcada:
                    superficie.blit(GestorAssets.recuadro_seleccion, (cx, cy))
                elif es_objetivo:
                    s_pulse = pygame.Surface((self.ANCHO_CELDA, self.ALTO_CELDA), pygame.SRCALPHA)
                    pygame.draw.rect(s_pulse, (47, 168, 155, 45), (0, 0, self.ANCHO_CELDA, self.ALTO_CELDA), border_radius=12)
                    pygame.draw.rect(s_pulse, COLOR_TEAL_BORDE, (0, 0, self.ANCHO_CELDA, self.ALTO_CELDA), width=2, border_radius=12)
                    superficie.blit(s_pulse, (cx, cy))
                elif hover_activo:
                    s_hover = pygame.Surface((self.ANCHO_CELDA, self.ALTO_CELDA), pygame.SRCALPHA)
                    pygame.draw.rect(s_hover, (255, 255, 255, 55), (0, 0, self.ANCHO_CELDA, self.ALTO_CELDA), border_radius=12)
                    pygame.draw.rect(s_hover, (255, 255, 255, 120), (0, 0, self.ANCHO_CELDA, self.ALTO_CELDA), width=1, border_radius=12)
                    superficie.blit(s_hover, (cx, cy))

                if elem.id in GestorAssets.iconos_elementos:
                    img_ico = GestorAssets.iconos_elementos[elem.id]
                    rect_ico = img_ico.get_rect(center=(cx + self.ANCHO_CELDA // 2, cy + 25))
                    superficie.blit(img_ico, rect_ico)

                color_nom = COLOR_AZUL_MARCADO_ICON if esta_marcada else COLOR_TEXTO_NAVY
                lineas_nom = self.dividir_texto_en_lineas(elem.nombre, Fuentes.celda_nombre, max_ancho=72)

                if len(lineas_nom) == 1:
                    t_nombre = Fuentes.celda_nombre.render(lineas_nom[0], True, color_nom)
                    rect_nom = t_nombre.get_rect(center=(cx + self.ANCHO_CELDA // 2, cy + 62))
                    superficie.blit(t_nombre, rect_nom)
                else:
                    t_l1 = Fuentes.celda_nombre.render(lineas_nom[0], True, color_nom)
                    t_l2 = Fuentes.celda_nombre.render(lineas_nom[1], True, color_nom)
                    rect_l1 = t_l1.get_rect(center=(cx + self.ANCHO_CELDA // 2, cy + 54))
                    rect_l2 = t_l2.get_rect(center=(cx + self.ANCHO_CELDA // 2, cy + 67))
                    superficie.blit(t_l1, rect_l1)
                    superficie.blit(t_l2, rect_l2)


class BingoCalmaApp:
    def __init__(self):
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Bingo Calma - Estimulación Cognitiva y Sensorial")
        inicializar_sistema_recursos()
        self.reloj = pygame.time.Clock()

        self.estado = ESTADO_INICIO
        self.modo_seleccionado = 1
        self.modal_como_jugar = False
        self.modal_logro = None
        self.modal_fin_partida = None
        self.juego_pausado = False
        self.ticks_anim = 0
        self.scroll_figuras = 0
        self.arrastrando_scroll = False
        self.scroll_mouse_y = 0

        self.btn_inicio_jugar = BotonCalma(pygame.Rect(64, 145, 540, 440), pre_dibujado=True, radio=32)
        self.btn_inicio_como_jugar = BotonCalma(pygame.Rect(636, 145, 580, 205), pre_dibujado=True, radio=28)
        self.btn_inicio_salir = BotonCalma(pygame.Rect(636, 380, 580, 205), pre_dibujado=True, radio=28)
        self.btn_modal_cerrar = BotonCalma(pygame.Rect(520, 560, 240, 52), pre_dibujado=False, radio=26)

        self.btn_seleccion_volver = BotonCalma(pygame.Rect(49, 49, 56, 56), pre_dibujado=True, circular=True)
        self.btn_card_corta = BotonCalma(pygame.Rect(98, 165, 340, 465), pre_dibujado=True, radio=26)
        self.btn_card_media = BotonCalma(pygame.Rect(470, 165, 340, 465), pre_dibujado=True, radio=26)
        self.btn_card_completa = BotonCalma(pygame.Rect(842, 165, 340, 465), pre_dibujado=True, radio=26)

        self.btn_juego_volver = BotonCalma(pygame.Rect(25, 29, 47, 47), pre_dibujado=True, circular=True)
        self.btn_sacar_balota = BotonCalma(pygame.Rect(1094, 29, 160, 47), pre_dibujado=True, radio=23)
        self.btn_pausar = BotonCalma(pygame.Rect(31, 646, 180, 39), pre_dibujado=True, radio=14)

        self.btn_fin_reiniciar = BotonCalma(pygame.Rect(415, 565, 210, 46), pre_dibujado=False, radio=23)
        self.btn_fin_menu = BotonCalma(pygame.Rect(655, 565, 210, 46), pre_dibujado=False, radio=23)

        GestorMusica.reproducir_menu()
        self._iniciar_partida(self.modo_seleccionado)

    def _iniciar_partida(self, modo):
        random.seed()
        self.modo_seleccionado = modo
        self.partida = PartidaBingoCognitivo(nivel_inicial=modo)
        self.partida.agregar_carton()
        self.partida.agregar_carton()
        self.partida.iniciar_sorteo()

        self.tableros_gui = [
            TableroCartonGUI(250, 100, self.partida.cartones[0], 0),
            TableroCartonGUI(754, 100, self.partida.cartones[1], 1)
        ]
        self.elemento_actual = self.partida.extraer_siguiente_elemento()
        self.juego_pausado = False
        self.modal_logro = None
        self.modal_fin_partida = None
        self.scroll_figuras = 0
        self.arrastrando_scroll = False

    def ejecutar(self):
        corriendo = True
        while corriendo:
            self.reloj.tick(60)
            self.ticks_anim += 1
            mouse_pos = pygame.mouse.get_pos()

            self._actualizar_hover_botones(mouse_pos)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    if self.modal_como_jugar:
                        self.modal_como_jugar = False
                    else:
                        corriendo = False
                self._manejar_eventos(evento)

            self._dibujar(mouse_pos)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _actualizar_hover_botones(self, mouse_pos):
        if self.estado == ESTADO_INICIO:
            if self.modal_como_jugar:
                self.btn_modal_cerrar.actualizar(mouse_pos)
            else:
                self.btn_inicio_jugar.actualizar(mouse_pos)
                self.btn_inicio_como_jugar.actualizar(mouse_pos)
                self.btn_inicio_salir.actualizar(mouse_pos)
        elif self.estado == ESTADO_SELECCION:
            self.btn_seleccion_volver.actualizar(mouse_pos)
            self.btn_card_corta.actualizar(mouse_pos)
            self.btn_card_media.actualizar(mouse_pos)
            self.btn_card_completa.actualizar(mouse_pos)
        elif self.estado == ESTADO_JUEGO:
            if self.modal_fin_partida:
                self.btn_fin_reiniciar.actualizar(mouse_pos)
                self.btn_fin_menu.actualizar(mouse_pos)
            else:
                self.btn_juego_volver.actualizar(mouse_pos)
                self.btn_sacar_balota.actualizar(mouse_pos)
                self.btn_pausar.actualizar(mouse_pos)

    def _manejar_eventos(self, evento):
        if self.estado == ESTADO_INICIO:
            self._manejar_eventos_inicio(evento)
        elif self.estado == ESTADO_SELECCION:
            self._manejar_eventos_seleccion(evento)
        elif self.estado == ESTADO_JUEGO:
            self._manejar_eventos_juego(evento)

    def _manejar_eventos_inicio(self, evento):
        if self.modal_como_jugar:
            if self.btn_modal_cerrar.es_clickeado(evento):
                self.modal_como_jugar = False
            elif evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self.modal_como_jugar = False
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                w_m, h_m = 880, 540
                x_m = (ANCHO_VENTANA - w_m) // 2
                y_m = (ALTO_VENTANA - h_m) // 2
                if not pygame.Rect(x_m, y_m, w_m, h_m).collidepoint(evento.pos):
                    self.modal_como_jugar = False
            return

        if self.btn_inicio_jugar.es_clickeado(evento):
            self.estado = ESTADO_SELECCION

        elif self.btn_inicio_como_jugar.es_clickeado(evento):
            self.modal_como_jugar = True

        elif self.btn_inicio_salir.es_clickeado(evento):
            pygame.quit()
            sys.exit()

    def _dibujar_pantalla_inicio(self, mouse_pos):
        self.ventana.blit(GestorAssets.inicio_fondo, (0, 0))

        s_glow = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        pygame.draw.circle(s_glow, (47, 168, 155, 14), (ANCHO_VENTANA - 60, 40), 220)
        pygame.draw.circle(s_glow, (157, 196, 218, 20), (60, ALTO_VENTANA - 40), 240)
        self.ventana.blit(s_glow, (0, 0))

        icon_box = pygame.Rect(64, 38, 76, 76)
        pygame.draw.rect(self.ventana, COLOR_TEAL_BOTON, icon_box, border_radius=24)
        pygame.draw.rect(self.ventana, (255, 255, 255, 100), icon_box, width=2, border_radius=24)

        cx, cy = icon_box.center
        pygame.draw.circle(self.ventana, COLOR_BLANCO, (cx, cy - 8), 11)
        pygame.draw.ellipse(self.ventana, COLOR_BLANCO, (cx - 20, cy - 2, 40, 18))
        pygame.draw.circle(self.ventana, COLOR_BLANCO, (cx, cy + 9), 6)

        t_tit = Fuentes.titulo_inicio.render("Bingo de Recuerdos", True, COLOR_TEXTO_NAVY)
        self.ventana.blit(t_tit, (156, 36))
        t_sub = Fuentes.subtitulo_inicio.render("Juego tranquilo y memoria", True, COLOR_TEXTO_MUTED)
        self.ventana.blit(t_sub, (158, 86))

        badge_rect = pygame.Rect(1020, 52, 196, 46)
        pygame.draw.rect(self.ventana, (255, 255, 255, 180), badge_rect, border_radius=23)
        pygame.draw.rect(self.ventana, COLOR_TEAL_BORDE, badge_rect, width=1, border_radius=23)
        pygame.draw.circle(self.ventana, (34, 197, 94), (1046, 75), 6)
        t_badge = Fuentes.badge_inicio.render("Sesión Lista", True, (21, 128, 61))
        self.ventana.blit(t_badge, (1062, 64))

        self._dibujar_btn_inicio_hover(GestorAssets.inicio_btn_jugar, self.btn_inicio_jugar, glow_val=30)
        self._dibujar_btn_inicio_hover(GestorAssets.inicio_btn_como_jugar, self.btn_inicio_como_jugar, glow_val=22)
        self._dibujar_btn_inicio_hover(GestorAssets.inicio_btn_salir, self.btn_inicio_salir, glow_val=22)

        pygame.draw.line(self.ventana, (190, 220, 232), (64, 620), (1216, 620), width=1)
        t_footer_msg = Fuentes.footer_inicio_bold.render("Juega con calma, sin límite de tiempo.", True, (59, 90, 108))
        self.ventana.blit(t_footer_msg, (64, 646))
        t_resolucion = Fuentes.footer_inicio.render("Bingo Calma • Estimulación Cognitiva", True, (90, 123, 142))
        self.ventana.blit(t_resolucion, (930, 646))

        if self.modal_como_jugar:
            self._dibujar_modal_como_jugar()

    def _dibujar_btn_inicio_hover(self, img, btn_obj, glow_val=24):
        x, y = btn_obj.rect.topleft
        if btn_obj.hovered:
            y -= 2
            bright = img.copy()
            glow = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            glow.fill((glow_val, glow_val, glow_val, 0))
            bright.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            self.ventana.blit(bright, (x, y))
        else:
            self.ventana.blit(img, (x, y))

    def _dibujar_modal_como_jugar(self):
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((23, 48, 63, 165))
        self.ventana.blit(overlay, (0, 0))

        w_m, h_m = 880, 540
        x_m = (ANCHO_VENTANA - w_m) // 2
        y_m = (ALTO_VENTANA - h_m) // 2
        m_rect = pygame.Rect(x_m, y_m, w_m, h_m)

        pygame.draw.rect(self.ventana, (244, 249, 252), m_rect, border_radius=32)
        pygame.draw.rect(self.ventana, COLOR_TEAL_BOTON, m_rect, width=3, border_radius=32)

        t_tit = Fuentes.guia_titulo.render("¿Cómo Jugar al Bingo de Recuerdos?", True, COLOR_TEXTO_NAVY)
        self.ventana.blit(t_tit, t_tit.get_rect(center=(x_m + w_m // 2, y_m + 48)))

        pasos = [
            ("1", "Escuche y observe la balota", "En cada turno aparece una balota temática familiar en el riel superior."),
            ("2", "Busque en sus cartones", "Revise tranquilamente sus dos cartones de juego para encontrar la figura."),
            ("3", "Toque para marcar", "Haga clic sobre la casilla correcta para colocar una suave ficha y ganar puntos."),
            ("4", "Complete figuras sin prisa", "Logre líneas, cruces o cartón lleno. Juegue a su propio ritmo sin límite de tiempo.")
        ]

        card_y = y_m + 105
        for num, tit_paso, desc_paso in pasos:
            chip_num = pygame.Rect(x_m + 50, card_y, 40, 40)
            pygame.draw.rect(self.ventana, COLOR_TEAL_BOTON, chip_num, border_radius=12)
            t_num = Fuentes.guia_paso_num.render(num, True, COLOR_BLANCO)
            self.ventana.blit(t_num, t_num.get_rect(center=chip_num.center))

            t_tit_p = Fuentes.normal_bold.render(tit_paso, True, COLOR_TEXTO_NAVY)
            self.ventana.blit(t_tit_p, (x_m + 104, card_y + 2))
            t_desc_p = Fuentes.guia_paso_txt.render(desc_paso, True, COLOR_TEXTO_MUTED)
            self.ventana.blit(t_desc_p, (x_m + 104, card_y + 24))

            card_y += 72

        b_r = self.btn_modal_cerrar.rect
        pygame.draw.rect(self.ventana, COLOR_TEAL_BOTON, b_r, border_radius=26)
        if self.btn_modal_cerrar.hovered:
            pygame.draw.rect(self.ventana, (255, 255, 255, 60), b_r, border_radius=26)
        pygame.draw.rect(self.ventana, COLOR_BLANCO, b_r, width=2, border_radius=26)
        t_btn = Fuentes.normal_bold.render("Entendido, gracias", True, COLOR_BLANCO)
        self.ventana.blit(t_btn, t_btn.get_rect(center=b_r.center))

    def _manejar_eventos_seleccion(self, evento):
        if self.btn_seleccion_volver.es_clickeado(evento):
            self.estado = ESTADO_INICIO
            GestorMusica.reproducir_menu()

        elif self.btn_card_corta.es_clickeado(evento):
            self._iniciar_partida(modo=1)
            self.estado = ESTADO_JUEGO
            GestorMusica.reproducir_juego()

        elif self.btn_card_media.es_clickeado(evento):
            self._iniciar_partida(modo=2)
            self.estado = ESTADO_JUEGO
            GestorMusica.reproducir_juego()

        elif self.btn_card_completa.es_clickeado(evento):
            self._iniciar_partida(modo=3)
            self.estado = ESTADO_JUEGO
            GestorMusica.reproducir_juego()

    def _dibujar_pantalla_seleccion(self, mouse_pos):
        self.ventana.blit(GestorAssets.seleccion_fondo, (0, 0))
        self.btn_seleccion_volver.dibujar_hover(self.ventana, alpha_halo=50, border_halo=180)

        cards_cfg = [
            (98, self.btn_card_corta, GestorAssets.card_partida_corta, (227, 246, 241), (178, 229, 217), (47, 168, 155), "Elegir Corta"),
            (470, self.btn_card_media, GestorAssets.card_partida_media, (254, 246, 233), (252, 211, 141), (47, 168, 155), "Comenzar Media"),
            (842, self.btn_card_completa, GestorAssets.card_partida_completa, (253, 235, 237), (248, 188, 197), (225, 29, 72), "Elegir Completa")
        ]

        y_pos = 165
        for x, btn_obj, img_asset, c_bg, c_border, c_btn, txt_btn in cards_cfg:
            card_surf = pygame.Surface((340, 465), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, c_bg, (0, 0, 340, 465), border_radius=26)

            inner_surf = pygame.Surface((340, 465), pygame.SRCALPHA)
            inner_surf.blit(img_asset, (0, 0))
            mask_surf = pygame.Surface((340, 465), pygame.SRCALPHA)
            pygame.draw.rect(mask_surf, (255, 255, 255, 255), (0, 0, 340, 465), border_radius=26)
            inner_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            card_surf.blit(inner_surf, (0, 0))

            r_btn = pygame.Rect(30, 368, 280, 58)
            pygame.draw.rect(card_surf, c_btn, r_btn, border_radius=16)

            t_btn = Fuentes.btn_modo.render(txt_btn, True, COLOR_BLANCO)
            w_total = t_btn.get_width() + 24
            start_x = r_btn.centerx - w_total // 2
            tri_pts = [
                (start_x, r_btn.centery - 8),
                (start_x, r_btn.centery + 8),
                (start_x + 13, r_btn.centery)
            ]
            pygame.draw.polygon(card_surf, COLOR_BLANCO, tri_pts)
            card_surf.blit(t_btn, (start_x + 22, r_btn.centery - t_btn.get_height() // 2))

            pygame.draw.rect(card_surf, c_border, (0, 0, 340, 465), width=2, border_radius=26)

            if btn_obj.hovered:
                draw_y = y_pos - 3
                self.ventana.blit(card_surf, (x, draw_y))
                sheen = pygame.Surface((340, 465), pygame.SRCALPHA)
                pygame.draw.rect(sheen, (255, 255, 255, 28), (0, 0, 340, 465), border_radius=26)
                pygame.draw.rect(sheen, (47, 168, 155), (0, 0, 340, 465), width=3, border_radius=26)
                self.ventana.blit(sheen, (x, draw_y))
            else:
                self.ventana.blit(card_surf, (x, y_pos))

    def _manejar_eventos_juego(self, evento):
        if self.modal_fin_partida:
            if self.btn_fin_reiniciar.es_clickeado(evento):
                self.modal_fin_partida = None
                self._iniciar_partida(self.modo_seleccionado)
            elif self.btn_fin_menu.es_clickeado(evento):
                self.modal_fin_partida = None
                self.estado = ESTADO_SELECCION
                GestorMusica.reproducir_menu()
            return

        if self.modal_logro:
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                tipo = self.modal_logro.get("tipo")
                self.modal_logro = None
                if tipo == "BINGO_PLENO":
                    self._finalizar_y_verificar_partida()
            return

        if self.btn_juego_volver.es_clickeado(evento):
            self.estado = ESTADO_SELECCION
            GestorMusica.reproducir_menu()
            return

        if self.btn_sacar_balota.es_clickeado(evento) and not self.juego_pausado:
            self._sacar_siguiente_balota()

        if self.btn_pausar.es_clickeado(evento):
            self.juego_pausado = not self.juego_pausado
            return

        rect_panel_figuras = pygame.Rect(20, 134, 205, 502)

        if evento.type == pygame.MOUSEWHEEL and not self.juego_pausado:
            mouse_pos = pygame.mouse.get_pos()
            if rect_panel_figuras.collidepoint(mouse_pos):
                num_figs = 14 if self.modo_seleccionado == 2 else (7 if self.modo_seleccionado == 1 else 1)
                alt_tot = num_figs * 88 - 10
                min_scr = min(0, 498 - alt_tot)
                self.scroll_figuras += evento.y * 36
                self.scroll_figuras = max(min_scr, min(0, self.scroll_figuras))
                return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not self.juego_pausado:
            if rect_panel_figuras.collidepoint(evento.pos):
                self.arrastrando_scroll = True
                self.scroll_mouse_y = evento.pos[1]
            else:
                self._procesar_clic_celdas(evento.pos)

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastrando_scroll = False

        elif evento.type == pygame.MOUSEMOTION and self.arrastrando_scroll and not self.juego_pausado:
            delta_y = evento.pos[1] - self.scroll_mouse_y
            self.scroll_mouse_y = evento.pos[1]
            num_figs = 14 if self.modo_seleccionado == 2 else (7 if self.modo_seleccionado == 1 else 1)
            alt_tot = num_figs * 88 - 10
            min_scr = min(0, 498 - alt_tot)
            self.scroll_figuras += delta_y
            self.scroll_figuras = max(min_scr, min(0, self.scroll_figuras))

    def _sacar_siguiente_balota(self):
        if self.partida.bolillero.fase_regular_completa:
            self._finalizar_y_verificar_partida()
            return

        elem = self.partida.extraer_siguiente_elemento()
        if elem:
            self.elemento_actual = elem

    def _finalizar_y_verificar_partida(self):
        resumen = self.partida.verificar_combinaciones_finales()
        self.modal_fin_partida = resumen

    def _procesar_clic_celdas(self, pos):
        for idx, tab_gui in enumerate(self.tableros_gui):
            celda = tab_gui.obtener_celda_en_pos(pos)
            if celda:
                fila, col = celda
                acierto, elem, cod, logro = self.partida.marcar_casilla_por_usuario(idx, fila, col)
                if logro:
                    self.modal_logro = logro

    def _dibujar(self, mouse_pos):
        if self.estado == ESTADO_INICIO:
            self._dibujar_pantalla_inicio(mouse_pos)
        elif self.estado == ESTADO_SELECCION:
            self._dibujar_pantalla_seleccion(mouse_pos)
        elif self.estado == ESTADO_JUEGO:
            self._dibujar_pantalla_juego(mouse_pos)

    def _dibujar_pantalla_juego(self, mouse_pos):
        self.ventana.blit(GestorAssets.fondo_juego, (0, 0))
        self._dibujar_header_juego()
        self._dibujar_panel_figuras_juego()

        elem_id = self.elemento_actual.id if self.elemento_actual else None
        for tab_gui in self.tableros_gui:
            tab_gui.dibujar(self.ventana, mouse_pos, elem_id)

        if self.juego_pausado:
            self._dibujar_overlay_pausa()

        if self.modal_logro:
            self._dibujar_modal_victoria()

        if self.modal_fin_partida:
            self._dibujar_modal_fin_partida()

    def _dibujar_header_juego(self):
        self.btn_juego_volver.dibujar_hover(self.ventana, alpha_halo=60, border_halo=160)

        total_balotas = self.partida.bolillero.total_extraidas
        if total_balotas > 0:
            pygame.draw.rect(self.ventana, COLOR_FONDO_BASE, (86, 57, 100, 18))
            t_sub = Fuentes.subtitulo.render(f"Balota {total_balotas} / 40", True, COLOR_TEXTO_MUTED)
            self.ventana.blit(t_sub, (86, 57))

        centros_ranuras = [
            (601, 52),
            (633, 52),
            (665, 52),
            (697, 52)
        ]

        ultimas_bolas = self.partida.bolillero.historial_extraidas[-4:]
        desplazamiento = 4 - len(ultimas_bolas)

        for i, bola in enumerate(ultimas_bolas):
            slot_idx = i + desplazamiento
            if slot_idx < 0 or slot_idx >= 4:
                continue
            cx, cy = centros_ranuras[slot_idx]
            es_actual = (slot_idx == 3)

            if es_actual:
                pygame.draw.circle(self.ventana, COLOR_MENTA_ACTIVA, (cx, cy), 14)
                pygame.draw.circle(self.ventana, COLOR_TEAL_BORDE, (cx, cy), 14, width=2)
                t_ico = Fuentes.riel_letra.render(f"{bola.letra}", True, (13, 148, 136))
                self.ventana.blit(t_ico, t_ico.get_rect(center=(cx, cy)))
            else:
                pygame.draw.circle(self.ventana, (255, 255, 255, 235), (cx, cy), 13)
                pygame.draw.circle(self.ventana, (189, 212, 226), (cx, cy), 13, width=1)
                t_letra = Fuentes.riel_letra.render(bola.letra, True, COLOR_TEXTO_NAVY)
                self.ventana.blit(t_letra, t_letra.get_rect(center=(cx, cy)))

        if self.elemento_actual:
            chip_x, chip_y = 740, 28
            chip_w, chip_h = 320, 48
            pygame.draw.rect(self.ventana, (255, 255, 255, 230), (chip_x, chip_y, chip_w, chip_h), border_radius=16)
            pygame.draw.rect(self.ventana, COLOR_TEAL_BORDE, (chip_x, chip_y, chip_w, chip_h), width=2, border_radius=16)

            letra_circulo = pygame.Rect(chip_x + 8, chip_y + 8, 32, 32)
            pygame.draw.rect(self.ventana, COLOR_MENTA_ACTIVA, letra_circulo, border_radius=16)
            pygame.draw.rect(self.ventana, COLOR_TEAL_BORDE, letra_circulo, width=1, border_radius=16)
            t_col = Fuentes.columna.render(self.elemento_actual.letra, True, COLOR_TEXTO_NAVY)
            self.ventana.blit(t_col, t_col.get_rect(center=letra_circulo.center))

            if self.elemento_actual.id in GestorAssets.iconos_header:
                img_ico = GestorAssets.iconos_header[self.elemento_actual.id]
                rect_h_ico = img_ico.get_rect(center=(chip_x + 64, chip_y + chip_h // 2))
                self.ventana.blit(img_ico, rect_h_ico)
                t_elem = Fuentes.riel_nombre.render(self.elemento_actual.nombre, True, COLOR_TEXTO_NAVY)
                self.ventana.blit(t_elem, (chip_x + 88, chip_y + 15))
            else:
                t_elem = Fuentes.riel_nombre.render(self.elemento_actual.nombre, True, COLOR_TEXTO_NAVY)
                self.ventana.blit(t_elem, (chip_x + 60, chip_y + 15))

        if self.partida.bolillero.fase_regular_completa:
            r_verif = self.btn_sacar_balota.rect
            import math
            pulso = int(math.sin(self.ticks_anim * 0.08) * 20)
            base_g = max(0, min(255, 185 + pulso))
            c_btn = (20, 205, 145) if self.btn_sacar_balota.hovered else (16, base_g, 129)
            pygame.draw.rect(self.ventana, c_btn, r_verif, border_radius=23)
            pygame.draw.rect(self.ventana, COLOR_BLANCO, r_verif, width=2, border_radius=23)
            t_v = Fuentes.normal_bold.render("Verificar", True, COLOR_BLANCO)
            self.ventana.blit(t_v, t_v.get_rect(center=r_verif.center))
        else:
            self.btn_sacar_balota.dibujar_hover(self.ventana)

    def _dibujar_panel_figuras_juego(self):
        if self.modo_seleccionado == 1:
            figuras_a_mostrar = [1, 2, 4, 11, 12, 13, 14]
        elif self.modo_seleccionado == 2:
            figuras_a_mostrar = list(range(1, 15))
        else:
            figuras_a_mostrar = [14]

        # Configuración del área recortada de scroll
        clip_rect = pygame.Rect(24, 136, 194, 500)
        altura_total = len(figuras_a_mostrar) * 88 - 10
        min_scroll = min(0, 498 - altura_total)
        self.scroll_figuras = max(min_scroll, min(0, self.scroll_figuras))

        clip_orig = self.ventana.get_clip()
        self.ventana.set_clip(clip_rect)

        card_y = 138 + int(self.scroll_figuras)
        for forma_id in figuras_a_mostrar:
            if forma_id in GestorAssets.imagenes_formas:
                img_forma = GestorAssets.imagenes_formas[forma_id]
                if card_y + 78 >= 134 and card_y <= 638:
                    self.ventana.blit(img_forma, (27, card_y))

                    completada = any(c.modalidades_verificadas.get(forma_id, False) for c in self.partida.cartones)
                    if completada:
                        pygame.draw.rect(self.ventana, COLOR_TEAL_BORDE, (27, card_y, 186, 78), width=3, border_radius=12)

            card_y += 88

        self.ventana.set_clip(clip_orig)

        # Barra de desplazamiento suave a la derecha del panel
        if altura_total > 498:
            track_rect = pygame.Rect(216, 138, 4, 498)
            pygame.draw.rect(self.ventana, (200, 220, 235, 120), track_rect, border_radius=2)

            thumb_h = max(36, int(498 * (498 / altura_total)))
            recorrido = 498 - thumb_h
            pct = -self.scroll_figuras / (altura_total - 498) if (altura_total - 498) > 0 else 0
            thumb_y = 138 + int(pct * recorrido)
            thumb_rect = pygame.Rect(215, thumb_y, 6, thumb_h)
            pygame.draw.rect(self.ventana, (47, 168, 155, 210), thumb_rect, border_radius=3)

        self.btn_pausar.dibujar_hover(self.ventana)

    def _dibujar_overlay_pausa(self):
        r = self.btn_pausar.rect
        pygame.draw.rect(self.ventana, COLOR_AMBAR_PAUSA, r, border_radius=14)
        pygame.draw.rect(self.ventana, COLOR_BLANCO, r, width=1, border_radius=14)
        t_re = Fuentes.normal_bold.render("▶  Reanudar", True, COLOR_BLANCO)
        self.ventana.blit(t_re, t_re.get_rect(center=r.center))

    def _dibujar_modal_victoria(self):
        if not self.modal_logro:
            return

        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((23, 48, 63, 160))
        self.ventana.blit(overlay, (0, 0))

        dialog_w, dialog_h = 520, 260
        dx = (ANCHO_VENTANA - dialog_w) // 2
        dy = (ALTO_VENTANA - dialog_h) // 2
        d_rect = pygame.Rect(dx, dy, dialog_w, dialog_h)

        pygame.draw.rect(self.ventana, (241, 245, 249), d_rect, border_radius=20)
        pygame.draw.rect(self.ventana, COLOR_TEAL_BOTON, d_rect, width=3, border_radius=20)

        t_win = Fuentes.dialogo_tit.render("¡FELICITACIONES!", True, COLOR_TEXTO_NAVY)
        self.ventana.blit(t_win, t_win.get_rect(center=(dx + dialog_w // 2, dy + 45)))

        nombres = ", ".join(self.modal_logro.get("nombres", ["Figura Lograda"]))
        t_fig = Fuentes.normal_bold.render(f"Has completado: {nombres}", True, (47, 168, 155))
        self.ventana.blit(t_fig, t_fig.get_rect(center=(dx + dialog_w // 2, dy + 90)))

        estrellas = self.modal_logro.get("estrellas", 30)
        t_pts = Fuentes.titulo.render(f"+{estrellas} Estrellas de Memoria", True, (217, 119, 6))
        self.ventana.blit(t_pts, t_pts.get_rect(center=(dx + dialog_w // 2, dy + 135)))

        t_info = Fuentes.dialogo_txt.render("Haz clic en cualquier parte para continuar jugando", True, COLOR_TEXTO_MUTED)
        self.ventana.blit(t_info, t_info.get_rect(center=(dx + dialog_w // 2, dy + 195)))

    def _dibujar_modal_fin_partida(self):
        if not self.modal_fin_partida:
            return

        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((15, 32, 45, 185))
        self.ventana.blit(overlay, (0, 0))

        dialog_w, dialog_h = 740, 520
        dx = (ANCHO_VENTANA - dialog_w) // 2
        dy = (ALTO_VENTANA - dialog_h) // 2
        d_rect = pygame.Rect(dx, dy, dialog_w, dialog_h)

        pygame.draw.rect(self.ventana, (248, 250, 252), d_rect, border_radius=24)
        pygame.draw.rect(self.ventana, COLOR_TEAL_BOTON, d_rect, width=3, border_radius=24)

        t_tit = Fuentes.dialogo_tit.render("¡SESIÓN DE BINGO FINALIZADA!", True, COLOR_TEXTO_NAVY)
        self.ventana.blit(t_tit, t_tit.get_rect(center=(dx + dialog_w // 2, dy + 42)))

        t_sub = Fuentes.dialogo_txt.render("40 balotas completadas • Verificación de combinaciones logradas", True, COLOR_TEXTO_MUTED)
        self.ventana.blit(t_sub, t_sub.get_rect(center=(dx + dialog_w // 2, dy + 74)))

        pygame.draw.line(self.ventana, (203, 213, 225), (dx + 35, dy + 95), (dx + dialog_w - 35, dy + 95), 1)

        # Panel izquierdo: Combinaciones por cartón
        col_izq_x = dx + 40
        t_sec1 = Fuentes.normal_bold.render("Combinaciones Formadas:", True, (47, 168, 155))
        self.ventana.blit(t_sec1, (col_izq_x, dy + 112))

        cartones_res = self.modal_fin_partida.get("cartones_resultados", [])
        cursor_y = dy + 140
        for c_data in cartones_res:
            c_idx = c_data.get("carton_indice", 1)
            figuras = c_data.get("figuras", [])

            t_c_hdr = Fuentes.normal_bold.render(f"Cartón #{c_idx}:", True, COLOR_TEXTO_NAVY)
            self.ventana.blit(t_c_hdr, (col_izq_x, cursor_y))
            cursor_y += 24

            if figuras:
                for f_info in figuras:
                    nom = f_info.get("nombre", "Figura")
                    pts = f_info.get("estrellas", 0)
                    t_f = Fuentes.normal.render(f"  • {nom} (+{pts} pts)", True, (30, 41, 59))
                    self.ventana.blit(t_f, (col_izq_x + 6, cursor_y))
                    cursor_y += 22
            else:
                t_sin = Fuentes.normal.render("  • Sin combinaciones completas", True, COLOR_TEXTO_MUTED)
                self.ventana.blit(t_sin, (col_izq_x + 6, cursor_y))
                cursor_y += 22

            cursor_y += 10

        # Panel derecho: Resumen de Puntaje
        col_der_x = dx + 390
        col_der_w = 310
        t_sec2 = Fuentes.normal_bold.render("Resumen de Puntaje:", True, (217, 119, 6))
        self.ventana.blit(t_sec2, (col_der_x, dy + 112))

        card_pts = pygame.Rect(col_der_x, dy + 140, col_der_w, 250)
        pygame.draw.rect(self.ventana, (254, 243, 199, 140), card_pts, border_radius=16)
        pygame.draw.rect(self.ventana, (245, 158, 11), card_pts, width=2, border_radius=16)

        aciertos = self.modal_fin_partida.get("aciertos_destreza", 0)
        pts_destr = self.modal_fin_partida.get("puntos_destreza", 0)
        total_figs = self.modal_fin_partida.get("total_figuras", 0)
        ganadas = self.modal_fin_partida.get("estrellas_ganadas", 0)
        totales = self.modal_fin_partida.get("estrellas_totales", 0)

        t_d1 = Fuentes.normal.render(f"Aciertos de destreza: {aciertos} casillas", True, COLOR_TEXTO_NAVY)
        self.ventana.blit(t_d1, (col_der_x + 18, dy + 160))

        t_d2 = Fuentes.normal.render(f"Puntos por destreza: +{pts_destr} pts", True, (71, 85, 105))
        self.ventana.blit(t_d2, (col_der_x + 18, dy + 184))

        t_d3 = Fuentes.normal.render(f"Figuras completadas: {total_figs}", True, COLOR_TEXTO_NAVY)
        self.ventana.blit(t_d3, (col_der_x + 18, dy + 212))

        pygame.draw.line(self.ventana, (251, 191, 36), (col_der_x + 18, dy + 242), (col_der_x + col_der_w - 18, dy + 242), 1)

        t_d4 = Fuentes.normal_bold.render("Estrellas Ganadas en Sesión:", True, (180, 83, 9))
        self.ventana.blit(t_d4, (col_der_x + 18, dy + 256))

        t_pts_big = Fuentes.dialogo_tit.render(f"+{ganadas} Estrellas", True, (217, 119, 6))
        self.ventana.blit(t_pts_big, (col_der_x + 18, dy + 282))

        t_d5 = Fuentes.normal_bold.render(f"Estrellas Totales: {totales}", True, COLOR_TEXTO_NAVY)
        self.ventana.blit(t_d5, (col_der_x + 18, dy + 338))

        # Botones inferiores
        r_re = self.btn_fin_reiniciar.rect
        color_re = (38, 148, 136) if self.btn_fin_reiniciar.hovered else COLOR_TEAL_BOTON
        pygame.draw.rect(self.ventana, color_re, r_re, border_radius=23)
        pygame.draw.rect(self.ventana, (255, 255, 255, 180), r_re, width=2, border_radius=23)
        t_b1 = Fuentes.normal_bold.render("Jugar de Nuevo", True, COLOR_BLANCO)
        self.ventana.blit(t_b1, t_b1.get_rect(center=r_re.center))

        r_me = self.btn_fin_menu.rect
        color_me = (203, 213, 225) if self.btn_fin_menu.hovered else (226, 232, 240)
        pygame.draw.rect(self.ventana, color_me, r_me, border_radius=23)
        pygame.draw.rect(self.ventana, (148, 163, 184), r_me, width=2, border_radius=23)
        t_b2 = Fuentes.normal_bold.render("Cambiar Modo", True, COLOR_TEXTO_NAVY)
        self.ventana.blit(t_b2, t_b2.get_rect(center=r_me.center))


if __name__ == "__main__":
    app = BingoCalmaApp()
    app.ejecutar()
