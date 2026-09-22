import pygame

class boton:
    def __init__(self, pantalla, texto, ruta_imagen="boton_base.png"):
        self.pantalla = pantalla
        self.texto = texto
        
        try:
            self.imagen_base = pygame.image.load(ruta_imagen).convert_alpha()
        except Exception:
            self.imagen_base = pygame.Surface((220, 70), pygame.SRCALPHA)
            pygame.draw.rect(self.imagen_base, (40, 70, 100), (0, 0, 220, 70), border_radius=20)

        self.ancho, self.alto = 220, 70
        self.imagen_normal = pygame.transform.smoothscale(self.imagen_base, (self.ancho, self.alto))
        self.imagen_hover = pygame.transform.smoothscale(self.imagen_base, (int(self.ancho * 1.05), int(self.alto * 1.05)))
        
        self.imagen_actual = self.imagen_normal
        self.rect = self.imagen_actual.get_rect()

        self.fuente = pygame.font.SysFont("Arial Black", 22)
        self.prepara_texto(texto)

    def prepara_texto(self, texto):
        self.texto = texto
        self.txt_surface = self.fuente.render(self.texto, True, (255, 255, 255))
        self.sombra_surface = self.fuente.render(self.texto, True, (15, 25, 40))

    def dibuja_boton(self):
        mouse_pos = pygame.mouse.get_pos()
        centro_actual = self.rect.center
        
        if self.rect.collidepoint(mouse_pos):
            self.imagen_actual = self.imagen_hover
        else:
            self.imagen_actual = self.imagen_normal

        self.rect = self.imagen_actual.get_rect(center=centro_actual)

        # 1. Dibujar la textura del botón
        self.pantalla.blit(self.imagen_actual, self.rect)

        # 2. Centrado óptico: desplazamos el centro Y unos píxeles hacia arriba (-3 o -4)
        offset_y = -5  
        centro_ajustado = (self.rect.centerx, self.rect.centery + offset_y)
        
        rect_txt = self.txt_surface.get_rect(center=centro_ajustado)

        # 3. Dibujar sombra y texto principal
        self.pantalla.blit(self.sombra_surface, (rect_txt.x + 2, rect_txt.y + 2))
        self.pantalla.blit(self.txt_surface, rect_txt)