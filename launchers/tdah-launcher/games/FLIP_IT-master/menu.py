"""
Menu de FLIP IT.

Flujo (a proposito lo mas corto posible):

    MENU  ->  ELIGE TU TEMATICA  ->  a jugar

Antes habia dos pantallas mas (dificultad y tiempo). Se quitaron: el juego
tiene un solo modo, de 6 parejas y sin reloj, asi que apenas el nino elige
la tematica la partida arranca. Menos pasos entre "quiero jugar" y "estoy
jugando" es una de las recomendaciones basicas de diseno para ninos con
TDAH, y ademas es como funcionan los juegos casuales del mercado.

ejecutar_menu() devuelve la clave del tema elegido ("instrumentos",
"spiderman"...) o None si el jugador decide salir.
"""

import pygame

import constantes
import ui
from audio import play_efecto, reproducir_musica, toggle_sonido
from constantes import TEMAS_INFO
from instrucciones import ejecutar_instrucciones
from opciones import ejecutar_opciones

ESTADO_MENU = "menu"
ESTADO_TEMA = "tema"


def _fondo_escalado():
    return pygame.transform.smoothscale(
        constantes.get_fondo_menu(), (constantes.ANCHO, constantes.ALTO)
    )


def _dibujar_logo(ventana, centro_y):
    """Titulo del juego dentro de una placa redondeada, como el logo de un
    juego comercial: una sola pieza, siempre en el mismo sitio."""
    f_titulo = ui.fuente(84, negrita=True)
    f_sub = ui.fuente(24, negrita=True)

    titulo = f_titulo.render("MEMORÍZALO", True, ui.TEXTO)
    ancho_placa = titulo.get_width() + 120
    alto_placa = titulo.get_height() + 46
    placa = pygame.Rect(0, 0, ancho_placa, alto_placa)
    placa.center = (constantes.ANCHO // 2, centro_y)

    exp = 18
    ventana.blit(ui.sombra_redondeada(placa.size, 34, alpha=85, expansion=exp),
                 (placa.x - exp, placa.y - exp + 10))
    ventana.blit(ui.degradado_redondeado(placa.size, (255, 255, 255), (233, 226, 248), 34),
                 placa.topleft)
    pygame.draw.rect(ventana, ui.BLANCO, placa, width=4, border_radius=34)

    ui.texto_centrado(ventana, "MEMORÍZALO", f_titulo, ui.TEXTO,
                      (placa.centerx, placa.centery - 4), sombra=ui.BLANCO)
    ui.texto_centrado(ventana, "Encuentra las parejas", f_sub, ui.TEXTO_SUAVE,
                      (placa.centerx, placa.bottom + 30))


def _construir_tarjetas():
    claves = list(TEMAS_INFO.keys())
    ancho, alto = 236, 268
    hueco = 28
    total = len(claves) * ancho + (len(claves) - 1) * hueco
    x0 = (constantes.ANCHO - total) // 2 + ancho // 2

    tarjetas = []
    for i, clave in enumerate(claves):
        info = TEMAS_INFO[clave]
        tarjeta = ui.TarjetaTema(
            x0 + i * (ancho + hueco), 372, ancho, alto,
            constantes.get_icono_tema(clave), info["nombre"],
            ui.PALETA_TEMAS[i % len(ui.PALETA_TEMAS)],
        )
        tarjetas.append((clave, tarjeta))
    return tarjetas


def ejecutar_menu(ventana, reloj):
    pygame.display.set_caption("MEMORÍZALO")
    reproducir_musica(constantes.MUSICA_MENU)

    fondo = _fondo_escalado()

    # --- pantalla 1: menu principal (solo tres opciones) ---
    cx = constantes.ANCHO // 2
    btn_jugar = ui.Boton(cx, 380, 380, 88, "JUGAR", ui.VERDE, tam_texto=40)
    btn_como = ui.Boton(cx, 482, 380, 62, "Cómo se juega", ui.AZUL, tam_texto=26)
    btn_opciones = ui.Boton(cx, 558, 380, 62, "Opciones", ui.LAVANDA, tam_texto=26)
    btn_salir = ui.Boton(cx, 634, 380, 62, "Salir", ui.NEUTRO, tam_texto=26)
    btn_sonido = ui.Boton(constantes.ANCHO - 80, 52, 120, 50,
                          "🔊 ON" if constantes.SONIDO_ACTIVADO else "🔇 OFF",
                          ui.AMARILLO if constantes.SONIDO_ACTIVADO else ui.NEUTRO,
                          tam_texto=20)
    botones_menu = [btn_jugar, btn_como, btn_opciones, btn_salir, btn_sonido]

    # --- pantalla 2: eleccion de tematica ---
    tarjetas = _construir_tarjetas()
    btn_volver = ui.Boton(cx, 610, 240, 60, "Volver", ui.NEUTRO, tam_texto=26)

    f_titulo_pantalla = ui.fuente(52, negrita=True)
    f_pista = ui.fuente(22, negrita=False)

    estado = ESTADO_MENU
    fundido = 0.0        # velo blanco que suaviza el cambio de pantalla

    def cambiar(nuevo):
        nonlocal estado, fundido
        estado = nuevo
        fundido = 1.0

    while True:
        dt = reloj.tick(constantes.FPS) / 1000.0
        mouse_pos = pygame.mouse.get_pos()
        presionando = pygame.mouse.get_pressed()[0]

        # ------------------------------------------------ eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return None

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                if estado == ESTADO_TEMA:
                    play_efecto("boton")
                    cambiar(ESTADO_MENU)
                else:
                    return None

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos = evento.pos
                if estado == ESTADO_MENU:
                    if btn_jugar.rect.collidepoint(pos):
                        play_efecto("boton")
                        cambiar(ESTADO_TEMA)
                    elif btn_como.rect.collidepoint(pos):
                        play_efecto("boton")
                        ejecutar_instrucciones(ventana, reloj)
                        reproducir_musica(constantes.MUSICA_MENU)
                        fundido = 1.0
                    elif btn_opciones.rect.collidepoint(pos):
                        play_efecto("boton")
                        ejecutar_opciones(ventana, reloj)
                        reproducir_musica(constantes.MUSICA_MENU)
                        fundido = 1.0
                    elif btn_salir.rect.collidepoint(pos):
                        play_efecto("boton")
                        return None
                    elif btn_sonido.rect.collidepoint(pos):
                        play_efecto("boton")
                        activado = toggle_sonido()
                        btn_sonido.texto = "🔊 ON" if activado else "🔇 OFF"
                        btn_sonido.paleta = ui.AMARILLO if activado else ui.NEUTRO
                        if activado:
                            reproducir_musica(constantes.MUSICA_MENU)

                elif estado == ESTADO_TEMA:
                    if btn_volver.rect.collidepoint(pos):
                        play_efecto("boton")
                        cambiar(ESTADO_MENU)
                    else:
                        if btn_sonido.rect.collidepoint(pos):
                            play_efecto("boton")
                            activado = toggle_sonido()
                            btn_sonido.texto = "🔊 ON" if activado else "🔇 OFF"
                            btn_sonido.paleta = ui.AMARILLO if activado else ui.NEUTRO
                            if activado:
                                reproducir_musica(constantes.MUSICA_MENU)
                        for clave, tarjeta in tarjetas:
                            if tarjeta.rect.collidepoint(pos):
                                play_efecto("boton")
                                return clave      # -> derecho a jugar

        # ------------------------------------------------ dibujo
        ventana.blit(fondo, (0, 0))

        if estado == ESTADO_MENU:
            _dibujar_logo(ventana, 210)
            for b in botones_menu:
                b.actualizar(mouse_pos, presionando)
                b.dibujar(ventana)

        else:
            ui.texto_centrado(ventana, "ELIGE TUS CARTAS", f_titulo_pantalla,
                              ui.TEXTO, (cx, 132), sombra=ui.BLANCO)
            ui.texto_centrado(ventana, "Toca un dibujo y empiezas a jugar",
                              f_pista, ui.TEXTO_SUAVE, (cx, 184))
            for _, tarjeta in tarjetas:
                tarjeta.actualizar(mouse_pos)
                tarjeta.dibujar(ventana)
            btn_volver.actualizar(mouse_pos, presionando)
            btn_volver.dibujar(ventana)
            btn_sonido.actualizar(mouse_pos, presionando)
            btn_sonido.dibujar(ventana)

        # velo de transicion: media que el cambio de pantalla no sea un salto
        if fundido > 0.01:
            fundido = max(0.0, fundido - dt * 4.5)
            velo = pygame.Surface((constantes.ANCHO, constantes.ALTO), pygame.SRCALPHA)
            velo.fill((255, 255, 255, int(200 * fundido)))
            ventana.blit(velo, (0, 0))

        pygame.display.update()
