import pygame
import math
import random
import os
from settings import *


class Component:
    def actualizar(self, dt):
        pass

    def dibujar(self, renderer, superficie, t, mouse_pos):
        pass


class Decoracion(Component):
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

    def dibujar(self, renderer, superficie, t, mouse_pos=None):
        x = self.x + math.sin(t * 0.5 + self.fase) * self.amplitud_x
        y = self.y
        tam = int(self.radio * 2 + 4)
        capa = pygame.Surface((tam, tam), pygame.SRCALPHA)
        centro = (tam / 2, tam / 2)
        if self.tipo == "circulo":
            pygame.draw.circle(capa, self.color, centro, self.radio)
        else:
            renderer.dibujar_estrella(capa, centro, self.radio, self.radio * 0.45, self.color)
        superficie.blit(capa, (x - tam / 2, y - tam / 2))


class BotonBase(Component):
    def __init__(self, centro, tamano, texto, fuente):
        ancho, alto = tamano
        self.rect_base = pygame.Rect(0, 0, ancho, alto)
        self.rect_base.center = centro
        self.texto = texto
        self.fuente = fuente

    def contiene(self, pos):
        return self.rect_base.collidepoint(pos)

    def _rect_actual(self, t, hover):
        escala = 1.0 + math.sin(t * 2.1) * 0.018 + (0.035 if hover else 0.0)
        ancho = int(self.rect_base.width * escala)
        alto = int(self.rect_base.height * escala)
        rect = pygame.Rect(0, 0, ancho, alto)
        rect.center = self.rect_base.center
        return rect


class Boton(BotonBase):
    def dibujar(self, renderer, superficie, t, mouse_pos):
        hover = self.contiene(mouse_pos)
        rect = self._rect_actual(t, hover)
        color = COLOR_BOTON_HOVER if hover else COLOR_BOTON
        radio = rect.height // 2
        renderer.dibujar_rect_redondeado_sombra(superficie, rect, radio, color, COLOR_BOTON_SOMBRA, 7)
        texto_superficie = self.fuente.render(self.texto, True, COLOR_TEXTO_BOTON)
        texto_rect = texto_superficie.get_rect(center=(rect.centerx, rect.centery - 2))
        superficie.blit(texto_superficie, texto_rect)


class BotonJugar(BotonBase):
    """Botón pill integrado en la tarjeta del carrusel."""
    def __init__(self, centro, tamano, texto, fuente, color_base, disponible=True):
        super().__init__(centro, tamano, texto, fuente)
        self.color_base = color_base
        self.disponible = disponible

    def dibujar(self, renderer, superficie, t, mouse_pos):
        self.dibujar_directo(superficie, t, mouse_pos)

    def dibujar_directo(self, superficie, t, mouse_pos):
        hover = self.disponible and self.contiene(mouse_pos)
        rect = self._rect_actual(t, hover)
        radio = rect.height // 2

        if self.disponible:
            color = COLOR_JUGAR_HOVER if hover else self.color_base
            color_sombra = COLOR_JUGAR_SOMBRA
            color_texto = COLOR_TEXTO_BOTON
        else:
            color = COLOR_NO_DISPONIBLE
            color_sombra = (150, 145, 165)
            color_texto = (255, 255, 255)

        # Draw shadow
        sombra = rect.copy()
        sombra.x += 4
        sombra.y += 4
        pygame.draw.rect(superficie, color_sombra, sombra, border_radius=radio)
        pygame.draw.rect(superficie, color, rect, border_radius=radio)

        texto_sup = self.fuente.render(self.texto, True, color_texto)
        texto_rect = texto_sup.get_rect(center=(rect.centerx, rect.centery - 1))
        superficie.blit(texto_sup, texto_rect)


class FlechaNavegacion:
    """Flecha de navegación del carrusel (◀ o ▶)."""
    def __init__(self, centro, direccion, tamano=40):
        self.centro = centro
        self.direccion = direccion  # -1 = izquierda, +1 = derecha
        self.tamano = tamano
        self.rect = pygame.Rect(0, 0, tamano + 20, tamano + 30)
        self.rect.center = centro

    def contiene(self, pos):
        return self.rect.collidepoint(pos)

    def dibujar(self, superficie, t, mouse_pos):
        hover = self.contiene(mouse_pos)
        color = COLOR_FLECHA_HOVER if hover else COLOR_FLECHA
        cx, cy = self.centro
        s = self.tamano // 2
        # Pulso sutil al hacer hover
        desplaz = 3 if hover else 0
        dx = -desplaz if self.direccion == -1 else desplaz

        if self.direccion == -1:
            puntos = [(cx - s + dx, cy), (cx + s // 2 + dx, cy - s), (cx + s // 2 + dx, cy + s)]
        else:
            puntos = [(cx + s + dx, cy), (cx - s // 2 + dx, cy - s), (cx - s // 2 + dx, cy + s)]

        # Sombra
        sombra_puntos = [(x + 2, y + 3) for x, y in puntos]
        pygame.draw.polygon(superficie, (*COLOR_TARJETA_SOMBRA, 80), sombra_puntos)
        pygame.draw.polygon(superficie, color, puntos)

        # Borde blanco sutil
        if hover:
            pygame.draw.polygon(superficie, (255, 255, 255, 100), puntos, width=2)


class IndicadorPagina:
    """Indicadores de posición (puntos) debajo del carrusel."""
    def __init__(self, centro_y, total, radio=6, espacio=22):
        self.centro_y = centro_y
        self.total = total
        self.radio = radio
        self.espacio = espacio

    def dibujar(self, superficie, indice_actual):
        ancho_total = self.total * (self.radio * 2 + self.espacio) - self.espacio
        x_inicio = (ANCHO - ancho_total) // 2 + self.radio

        for i in range(self.total):
            cx = x_inicio + i * (self.radio * 2 + self.espacio)
            if i == indice_actual:
                pygame.draw.circle(superficie, COLOR_LOGO, (cx, self.centro_y), self.radio)
            else:
                pygame.draw.circle(superficie, (*COLOR_TARJETA_SOMBRA, 180), (cx, self.centro_y), self.radio - 1)
                pygame.draw.circle(superficie, COLOR_TARJETA_BORDE, (cx, self.centro_y), self.radio - 1, width=2)

    def contiene_indice(self, pos):
        """Devuelve el índice del punto pulsado, o None."""
        ancho_total = self.total * (self.radio * 2 + self.espacio) - self.espacio
        x_inicio = (ANCHO - ancho_total) // 2 + self.radio
        for i in range(self.total):
            cx = x_inicio + i * (self.radio * 2 + self.espacio)
            if math.hypot(pos[0] - cx, pos[1] - self.centro_y) <= self.radio + 8:
                return i
        return None


def aplicar_esquinas_redondeadas(superficie, radio=18):
    """Aplica máscara alfa para redondear esquinas de una superficie Pygame."""
    mascara = pygame.Surface(superficie.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=radio)
    resultado = superficie.copy()
    resultado.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return resultado


class TarjetaJuego(Component):
    ANCHO_CARRUSEL = 380
    ALTO_CARRUSEL = 400
    ZONA_PORTADA = 150

    def __init__(self, titulo, subtitulo, color_icono, tipo_icono,
                 clave_juego=None, disponible=True,
                 descripcion="", habilidad="", controles="",
                 portada_path=None):
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.color_icono = color_icono
        self.tipo_icono = tipo_icono
        self.clave_juego = clave_juego
        self.disponible = disponible
        self.descripcion = descripcion
        self.habilidad = habilidad
        self.controles = controles
        self.portada_path = portada_path
        self._portada_pequena = None
        self._portada_grande = None
        self._portada_cargada = False

    def _cargar_portada(self):
        """Carga la imagen de portada si existe (lazy load) y aplica esquinas redondeadas."""
        if self._portada_cargada:
            return
        self._portada_cargada = True
        if self.portada_path and os.path.exists(self.portada_path):
            try:
                img = pygame.image.load(self.portada_path).convert_alpha()

                # Escalar para caber en la zona de portada (hover)
                ancho_max = self.ANCHO_CARRUSEL - 36
                alto_max = self.ZONA_PORTADA - 16
                escala = min(ancho_max / img.get_width(), alto_max / img.get_height())
                nuevo_ancho = max(1, int(img.get_width() * escala))
                nuevo_alto = max(1, int(img.get_height() * escala))
                img_peq = pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))
                self._portada_pequena = aplicar_esquinas_redondeadas(img_peq, radio=14)

                # Escalar para caber en la tarjeta completa (sin hover)
                ancho_max_gr = self.ANCHO_CARRUSEL - 20
                alto_max_gr = self.ALTO_CARRUSEL - 24
                escala_gr = min(ancho_max_gr / img.get_width(), alto_max_gr / img.get_height())
                nuevo_ancho_gr = max(1, int(img.get_width() * escala_gr))
                nuevo_alto_gr = max(1, int(img.get_height() * escala_gr))
                img_gr = pygame.transform.smoothscale(img, (nuevo_ancho_gr, nuevo_alto_gr))
                self._portada_grande = aplicar_esquinas_redondeadas(img_gr, radio=22)
            except Exception:
                self._portada_pequena = None
                self._portada_grande = None

    def dibujar_carrusel(self, superficie, cx, cy, t, mouse_pos, fuentes, indice=0):
        """Dibuja la tarjeta en formato grande para el carrusel.
        cx, cy = centro donde dibujar la tarjeta.
        fuentes = dict con claves: titulo, subtitulo, descripcion, badge, jugar
        """
        ancho = self.ANCHO_CARRUSEL
        alto = self.ALTO_CARRUSEL
        rect = pygame.Rect(0, 0, ancho, alto)
        rect.center = (cx, cy)

        is_hovering = rect.collidepoint(mouse_pos)

        # --- Sombra profesional suave ---
        sombra_rect = rect.move(0, 8)
        sombra_capa = pygame.Surface((ancho + 16, alto + 16), pygame.SRCALPHA)
        pygame.draw.rect(sombra_capa, (*COLOR_TARJETA_SOMBRA, 100),
                         sombra_capa.get_rect(), border_radius=28)
        superficie.blit(sombra_capa, (sombra_rect.left - 8, sombra_rect.top - 4))

        # --- Tarjeta principal ---
        tarjeta = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        tarjeta_rect = tarjeta.get_rect()

        # Fondo blanco
        alpha_fondo = 252 if self.disponible else 235
        pygame.draw.rect(tarjeta, (255, 255, 255, alpha_fondo), tarjeta_rect, border_radius=28)

        # Barra de color superior (acento del juego)
        barra = pygame.Rect(0, 0, ancho, 6)
        pygame.draw.rect(tarjeta, self.color_icono, barra,
                         border_top_left_radius=28, border_top_right_radius=28)

        # Borde exterior
        color_borde = self.color_icono if is_hovering else COLOR_TARJETA_BORDE
        grosor_borde = 3 if is_hovering else 2
        pygame.draw.rect(tarjeta, color_borde, tarjeta_rect, width=grosor_borde, border_radius=28)

        superficie.blit(tarjeta, rect.topleft)

        self._cargar_portada()

        if is_hovering:
            # --- ZONA DE HOVER: Mostrar info detallada ---
            centro_portada = (rect.centerx, rect.top + 16 + self.ZONA_PORTADA // 2)
            if self._portada_pequena:
                pr = self._portada_pequena.get_rect(center=centro_portada)
                superficie.blit(self._portada_pequena, pr)
            else:
                self._dibujar_icono_grande(superficie, centro_portada, t, indice)

            # --- Separador sutil ---
            sep_y = rect.top + self.ZONA_PORTADA + 12
            pygame.draw.line(superficie, (*COLOR_TARJETA_BORDE, 180),
                             (rect.left + 28, sep_y), (rect.right - 28, sep_y), 2)

            # --- Título ---
            color_txt = COLOR_TEXTO_OSCURO if self.disponible else (150, 145, 165)
            titulo_sup = fuentes["titulo"].render(self.titulo, True, color_txt)
            if titulo_sup.get_width() > ancho - 36:
                factor = (ancho - 36) / titulo_sup.get_width()
                nw = int(titulo_sup.get_width() * factor)
                nh = int(titulo_sup.get_height() * factor)
                titulo_sup = pygame.transform.smoothscale(titulo_sup, (nw, nh))
            titulo_rect = titulo_sup.get_rect(center=(rect.centerx, sep_y + 20))
            superficie.blit(titulo_sup, titulo_rect)

            # --- Subtítulo ---
            sub_sup = fuentes["subtitulo"].render(self.subtitulo, True, (140, 135, 160))
            sub_rect = sub_sup.get_rect(center=(rect.centerx, sep_y + 44))
            superficie.blit(sub_sup, sub_rect)

            # --- Descripción con ajuste de líneas ---
            if self.descripcion:
                palabras = self.descripcion.split()
                lineas = []
                linea_act = []
                for p in palabras:
                    prueba = " ".join(linea_act + [p])
                    if fuentes["descripcion"].size(prueba)[0] <= ancho - 44:
                        linea_act.append(p)
                    else:
                        if linea_act:
                            lineas.append(" ".join(linea_act))
                        linea_act = [p]
                        if len(lineas) == 2:
                            break
                if linea_act and len(lineas) < 2:
                    lineas.append(" ".join(linea_act))
                
                y_linea = sep_y + 68
                for idx_l, linea in enumerate(lineas[:2]):
                    # Si era la segunda línea y quedan más palabras, añadir elipsis
                    if idx_l == 1 and len(lineas) == 2 and linea != " ".join(linea_act):
                        linea = linea[:45] + "..."
                    d_sup = fuentes["descripcion"].render(linea, True, (110, 105, 130))
                    d_rect = d_sup.get_rect(center=(rect.centerx, y_linea + idx_l * 20))
                    superficie.blit(d_sup, d_rect)

            # --- Badges: habilidad y controles ---
            y_badge = sep_y + 114
            if self.habilidad:
                hab_sup = fuentes["badge"].render(f"Habilidad: {self.habilidad}", True, (85, 75, 120))
                hab_rect = hab_sup.get_rect(center=(rect.centerx, y_badge))
                superficie.blit(hab_sup, hab_rect)
            if self.controles:
                ctrl_sup = fuentes["badge"].render(f"Controles: {self.controles}", True, (125, 115, 150))
                ctrl_rect = ctrl_sup.get_rect(center=(rect.centerx, y_badge + 20))
                superficie.blit(ctrl_sup, ctrl_rect)

            # --- Botón JUGAR ---
            boton_y = rect.bottom - 36
            texto_boton = "¡JUGAR AHORA!" if self.disponible else "Próximamente"
            boton = BotonJugar(
                (rect.centerx, boton_y), (200, 42), texto_boton,
                fuentes["jugar"], self.color_icono, self.disponible
            )
            boton.dibujar_directo(superficie, t, mouse_pos)
            return boton.rect_base.copy()
        else:
            # --- ZONA NO-HOVER: Mostrar solo la portada grande con diseño de tarjeta ---
            if self._portada_grande:
                pr = self._portada_grande.get_rect(center=(rect.centerx, rect.centery - 12))
                superficie.blit(self._portada_grande, pr)
            else:
                self._dibujar_icono_grande(superficie, (rect.centerx, rect.centery - 12), t, indice)

            # Pill inferior sutil indicando interactividad
            pulso = math.sin(t * 2.5) * 0.05
            pill_w = int(220 * (1.0 + pulso))
            pill_h = 28
            pill_rect = pygame.Rect(0, 0, pill_w, pill_h)
            pill_rect.center = (rect.centerx, rect.bottom - 24)
            pill_capa = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pygame.draw.rect(pill_capa, (*self.color_icono, 180), pill_capa.get_rect(), border_radius=14)
            superficie.blit(pill_capa, pill_rect.topleft)

            texto_pill = fuentes["badge"].render("Pasa el cursor para ver info", True, (255, 255, 255))
            superficie.blit(texto_pill, texto_pill.get_rect(center=pill_rect.center))
            
            # Devolver rect del botón inferior
            boton_y = rect.bottom - 36
            boton = BotonJugar(
                (rect.centerx, boton_y), (180, 44), "JUGAR",
                fuentes["jugar"], self.color_icono, self.disponible
            )
            return boton.rect_base.copy()

    def _dibujar_icono_grande(self, superficie, centro, t, indice):
        """Dibuja el icono del juego a escala grande para la zona de portada."""
        cx, cy = centro
        color = self.color_icono
        escala = 1.6  # más grande que en las tarjetas pequeñas

        if self.tipo_icono == "cartas":
            giro = math.sin(t * 1.3 + indice) * 6
            for dx, ang, alpha in ((-16, giro, 255), (16, -giro, 200)):
                w, h = int(46 * escala), int(60 * escala)
                capa = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.rect(capa, (*color, alpha), (0, 0, w, h), border_radius=14)
                pygame.draw.rect(capa, (255, 255, 255, alpha),
                                 (int(8*escala), int(10*escala), int(30*escala), int(40*escala)),
                                 border_radius=8)
                capa = pygame.transform.rotate(capa, ang)
                rect_capa = capa.get_rect(center=(cx + int(dx * escala), cy))
                superficie.blit(capa, rect_capa)

        elif self.tipo_icono == "laberinto":
            tam = int(56 * escala)
            rect_fondo = pygame.Rect(0, 0, tam, tam)
            rect_fondo.center = (cx, cy)
            pygame.draw.rect(superficie, color, rect_fondo, border_radius=16)
            paso = tam // 4
            lw = int(5 * escala)
            for i in range(1, 4):
                if i % 2 == 1:
                    pygame.draw.line(superficie, (255, 255, 255),
                                     (rect_fondo.left + paso * i, rect_fondo.top + 8),
                                     (rect_fondo.left + paso * i, rect_fondo.top + paso * 3), lw)
                else:
                    pygame.draw.line(superficie, (255, 255, 255),
                                     (rect_fondo.left + 8, rect_fondo.top + paso * i),
                                     (rect_fondo.left + paso * 3, rect_fondo.top + paso * i), lw)

        elif self.tipo_icono == "bingo":
            tam = int(54 * escala)
            rect_fondo = pygame.Rect(0, 0, tam, tam)
            rect_fondo.center = (cx, cy)
            pygame.draw.rect(superficie, color, rect_fondo, border_radius=14)
            celda = tam // 3
            for fila in range(3):
                for col in range(3):
                    bx = rect_fondo.left + col * celda + celda // 2
                    by = rect_fondo.top + fila * celda + celda // 2
                    r = int(6 * escala)
                    if fila == 1 and col == 1:
                        r = int(r + math.sin(t * 2.5) * 3)
                        pygame.draw.circle(superficie, (255, 255, 255), (bx, by), r)
                    else:
                        pygame.draw.circle(superficie, (255, 255, 255, 200), (bx, by), r, width=3)

        elif self.tipo_icono == "pelea":
            desplaz = math.sin(t * 3.0 + indice) * int(4 * escala)
            w, h = int(30 * escala), int(30 * escala)
            capa_i = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(capa_i, color, (0, int(4*escala), int(24*escala), int(22*escala)), border_radius=12)
            pygame.draw.rect(capa_i, (255, 255, 255, 180),
                             (int(4*escala), int(8*escala), int(16*escala), int(14*escala)), border_radius=8)
            superficie.blit(capa_i, (cx - int(32*escala) - desplaz, cy - h//2))
            capa_d = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(capa_d, color, (int(6*escala), int(4*escala), int(24*escala), int(22*escala)), border_radius=12)
            pygame.draw.rect(capa_d, (255, 255, 255, 180),
                             (int(10*escala), int(8*escala), int(16*escala), int(14*escala)), border_radius=8)
            superficie.blit(capa_d, (cx + int(2*escala) + desplaz, cy - h//2))
            chispa = max(0, math.sin(t * 4.5)) * int(6 * escala)
            if chispa > 3:
                pygame.draw.circle(superficie, (255, 230, 100), (cx, cy), int(chispa))

        elif self.tipo_icono == "dado":
            tam = int(52 * escala)
            angulo = math.sin(t * 1.5 + indice) * 5
            capa = pygame.Surface((tam, tam), pygame.SRCALPHA)
            pygame.draw.rect(capa, color, (0, 0, tam, tam), border_radius=16)
            blanco = (255, 255, 255)
            r = int(5 * escala)
            # Cara de 5 escalada
            m = tam * 0.27
            c = tam * 0.5
            posiciones = [(m, m), (tam - m, m), (c, c), (m, tam - m), (tam - m, tam - m)]
            for px, py in posiciones:
                pygame.draw.circle(capa, blanco, (int(px), int(py)), r)
            capa = pygame.transform.rotate(capa, angulo)
            rect_capa = capa.get_rect(center=(cx, cy))
            superficie.blit(capa, rect_capa)

        else:
            pulso = 1.0 + math.sin(t * 2.4) * 0.08
            radio = int(26 * escala * pulso)
            pygame.draw.circle(superficie, color, (cx, cy), radio, width=5)
            lw = int(12 * escala)
            pygame.draw.line(superficie, color, (cx - lw, cy), (cx + lw, cy), 6)
            pygame.draw.line(superficie, color, (cx, cy - lw), (cx, cy + lw), 6)
