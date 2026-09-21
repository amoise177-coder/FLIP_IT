"""
Pantalla "Cómo se juega".

Cabe entera en un solo pantallazo, sin scroll: son cuatro pasos numerados y
una nota. Un muro de texto con barra de desplazamiento (lo que habia antes)
es exactamente lo que un nino con TDAH no va a leer; cuatro frases cortas
con un numero de color al lado, si.
"""

import pygame

import constantes
import ui
from audio import play_efecto, reproducir_musica

PASOS = [
    ("Elige tus cartas", "Instrumentos, Spiderman, Mickey o Cenicienta."),
    ("Voltea una carta", "Haz clic en una carta y luego en otra para buscar su pareja."),
    ("Si son iguales, se quedan", "Si no lo son, se voltean solas y sigues intentando."),
    ("Junta las 6 parejas", "Cuando estén todas, ¡ganaste!"),
]

COLORES_PASO = [ui.LAVANDA, ui.AZUL, ui.ROSA, ui.VERDE]

def ejecutar_instrucciones(ventana, reloj):
    fondo = pygame.transform.smoothscale(
        constantes.get_fondo_menu(), (constantes.ANCHO, constantes.ALTO)
    )
    reproducir_musica(constantes.MUSICA_INSTRUCCIONES)

    f_titulo = ui.fuente(52, negrita=True)
    f_paso = ui.fuente(28, negrita=True)
    f_detalle = ui.fuente(21)
    f_numero = ui.fuente(30, negrita=True)
    f_nota = ui.fuente(20)

    panel_rect = pygame.Rect(0, 0, 900, 400)
    panel_rect.center = (constantes.ANCHO // 2, 356)

    btn_volver = ui.Boton(constantes.ANCHO // 2, 634, 260, 60, "Volver",
                          ui.NEUTRO, tam_texto=26)

    fundido = 1.0

    while True:
        dt = reloj.tick(constantes.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        presionando = pygame.mouse.get_pressed()[0]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return
            if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE,
                                                                pygame.K_RETURN):
                return
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_volver.rect.collidepoint(evento.pos):
                    play_efecto("boton")
                    return

        ventana.blit(fondo, (0, 0))
        ui.texto_centrado(ventana, "¿Cómo se juega?", f_titulo, ui.TEXTO,
                          (constantes.ANCHO // 2, 116), sombra=ui.BLANCO)

        ui.panel(ventana, panel_rect, radio=30)

        y = panel_rect.y + 58
        for i, (titulo, detalle) in enumerate(PASOS):
            paleta = COLORES_PASO[i % len(COLORES_PASO)]
            centro = (panel_rect.x + 66, y)
            pygame.draw.circle(ventana, paleta[1], centro, 27)
            pygame.draw.circle(ventana, ui.BLANCO, centro, 27, 3)
            ui.texto_centrado(ventana, str(i + 1), f_numero, ui.BLANCO, centro)

            ventana.blit(f_paso.render(titulo, True, ui.TEXTO),
                         (panel_rect.x + 110, y - 26))
            ventana.blit(f_detalle.render(detalle, True, ui.TEXTO_SUAVE),
                         (panel_rect.x + 110, y + 6))
            y += 86

        ui.texto_centrado(ventana, "No hay reloj: puedes jugar con calma.",
                          f_nota, ui.TEXTO_SUAVE,
                          (panel_rect.centerx, panel_rect.bottom - 28))
        btn_volver.actualizar(mouse_pos, presionando)
        btn_volver.dibujar(ventana)

        if fundido > 0.01:
            fundido = max(0.0, fundido - dt * 4.5)
            velo = pygame.Surface((constantes.ANCHO, constantes.ALTO), pygame.SRCALPHA)
            velo.fill((255, 255, 255, int(200 * fundido)))
            ventana.blit(velo, (0, 0))

        pygame.display.update()
