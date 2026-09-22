import pygame

COLOR_FONDO_FALLBACK = (225, 238, 245)
COLOR_TEXTO_TITULO = (60, 64, 70)
COLOR_TEXTO_SUBTITULO = (110, 115, 125)
COLOR_TEXTO_BOTON_BLANCO = (255, 255, 255)
COLOR_TEXTO_BOTON_OSCURO = (60, 64, 70)

COLOR_TARJETA = (245, 247, 250)
COLOR_BORDE_TARJETA = (210, 215, 225)

COLOR_JUGAR_TOP = (140, 195, 75)
COLOR_JUGAR_BOTTOM = (100, 160, 45)

COLOR_COMO_JUGAR_TOP = (75, 150, 220)
COLOR_COMO_JUGAR_BOTTOM = (45, 110, 180)

COLOR_SALIR_TOP = (240, 243, 248)
COLOR_SALIR_BOTTOM = (215, 220, 230)
COLOR_BORDE_SALIR = (180, 185, 195)

COLOR_ROJO_TOP = (235, 75, 75)
COLOR_ROJO_BOTTOM = (190, 40, 40)

class BotonEstiloFlipIt:
    def __init__(self, x, y, ancho, alto, texto, color_top, color_bottom, color_texto=COLOR_TEXTO_BOTON_BLANCO, color_borde=None, tamano_fuente=30, con_icono_play=False):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color_top = color_top
        self.color_bottom = color_bottom
        self.color_texto = color_texto
        self.color_borde = color_borde
        self.con_icono_play = con_icono_play
        self.fuente = pygame.font.SysFont("Trebuchet MS", tamano_fuente, bold=True)

    def dibujar(self, superficie):
        pos_mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(pos_mouse)

        superficie_boton = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        c_top = [min(255, c + 20) for c in self.color_top] if hover else self.color_top
        c_bottom = [min(255, c + 20) for c in self.color_bottom] if hover else self.color_bottom

        for y in range(self.rect.height):
            factor = y / self.rect.height
            r = int(c_top[0] + factor * (c_bottom[0] - c_top[0]))
            g = int(c_top[1] + factor * (c_bottom[1] - c_top[1]))
            b = int(c_top[2] + factor * (c_bottom[2] - c_top[2]))
            pygame.draw.line(superficie_boton, (r, g, b), (0, y), (self.rect.width, y))

        mascara = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mascara, (255, 255, 255, 255), mascara.get_rect(), border_radius=18)
        superficie_boton.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        superficie.blit(superficie_boton, self.rect.topleft)

        if self.color_borde:
            pygame.draw.rect(superficie, self.color_borde, self.rect, width=2, border_radius=18)

        txt_surface = self.fuente.render(self.texto, True, self.color_texto)
        txt_rect = txt_surface.get_rect()

        if self.con_icono_play:
            tam_icono = int(self.rect.height * 0.35)
            espacio_total = tam_icono + 12 + txt_rect.width
            inicio_x = self.rect.centerx - (espacio_total // 2)

            pt1 = (inicio_x, self.rect.centery - tam_icono // 2)
            pt2 = (inicio_x, self.rect.centery + tam_icono // 2)
            pt3 = (inicio_x + tam_icono, self.rect.centery)
            pygame.draw.polygon(superficie, self.color_texto, [pt1, pt2, pt3])

            txt_rect.midleft = (inicio_x + tam_icono + 12, self.rect.centery)
            superficie.blit(txt_surface, txt_rect)
        else:
            txt_rect.center = self.rect.center
            superficie.blit(txt_surface, txt_rect)

    def fue_cliqueado(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                return True
        return False