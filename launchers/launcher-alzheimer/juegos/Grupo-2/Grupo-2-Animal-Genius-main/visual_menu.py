import math
import pygame
from constants import const
from ui_components import aplicar_marco_capsula, crear_etiqueta_glossy


def dibujar_slider(pantalla, fuente_texto, etiqueta: str, rect: pygame.Rect, valor: float, pos_mouse: tuple[int, int]) -> None:
    txt = fuente_texto.render(f"{etiqueta}: {int(valor * 100)}%", True, (40, 40, 40))
    pantalla.blit(txt, (rect.x, rect.y - 24))
    pygame.draw.rect(pantalla, (200, 200, 200), rect, border_radius=10)
    ancho_relleno = int(rect.width * valor)
    rect_relleno = pygame.Rect(rect.x, rect.y, ancho_relleno, rect.height)
    pygame.draw.rect(pantalla, (85, 165, 255), rect_relleno, border_radius=10)
    pygame.draw.rect(pantalla, (180, 180, 180), rect, width=2, border_radius=10)

    orbe_x = rect.x + ancho_relleno
    orbe_y = rect.centery
    is_hover = rect.collidepoint(pos_mouse) or (pygame.mouse.get_pressed()[0] and rect.collidepoint(pos_mouse))
    radio_orbe = 12 if is_hover else 9
    pygame.draw.circle(pantalla, (255, 255, 255), (orbe_x, orbe_y), radio_orbe)
    pygame.draw.circle(pantalla, (30, 90, 180), (orbe_x, orbe_y), radio_orbe, width=3)


def dibujar_menu_principal(v, pantalla) -> None:
    pos_mouse = pygame.mouse.get_pos()
    fondo = v.recursos.fondos.get("menu_principal")
    pantalla.blit(fondo, (0, 0)) if fondo else pantalla.fill((230, 240, 250))

    ancho_p, alto_p = 320, 320
    x_p = (const.ANCHO_PANTALLA // 2) - (ancho_p // 2)
    y_p = 290

    surf_panel = pygame.Surface((ancho_p, alto_p), pygame.SRCALPHA)
    pygame.draw.rect(surf_panel, (0, 0, 0, 40), (0, 8, ancho_p, alto_p), border_radius=35)
    pygame.draw.rect(surf_panel, (255, 255, 255, 220), (0, 0, ancho_p, alto_p), border_radius=35)
    pygame.draw.rect(surf_panel, (255, 215, 0), (0, 0, ancho_p, alto_p), width=5, border_radius=35)
    pantalla.blit(surf_panel, (x_p, y_p))

    tiempo_ticks = pygame.time.get_ticks()
    offset_y = int(math.sin(tiempo_ticks * 0.003) * 4) 
    y_centro_logo = 140 + offset_y 

    if v.surf_logo:
        logo_peq = pygame.transform.smoothscale(v.surf_logo, (460, 200))
        rect_logo = logo_peq.get_rect(center=(const.ANCHO_PANTALLA // 2, y_centro_logo))
        pantalla.blit(logo_peq, rect_logo)
    else:
        titulo = v.fuente_titulo.render("Juego Educativo", True, const.COLOR_TEXTO_DARK)
        pantalla.blit(titulo, titulo.get_rect(center=(const.ANCHO_PANTALLA // 2, y_centro_logo)))

    v.dibujar_boton_con_hover(pantalla, v.surf_btn_jugar, v.rect_btn_jugar, pos_mouse)
    dibujar_slider(pantalla, v.fuente_texto, "Música", v.rect_slider_musica, v.volumen_musica, pos_mouse)
    dibujar_slider(pantalla, v.fuente_texto, "Efectos", v.rect_slider_efectos, v.volumen_efectos, pos_mouse)
    v.dibujar_boton_con_hover(pantalla, v.surf_btn_salir, v.rect_btn_salir, pos_mouse)


def dibujar_menu_zonas(v, pantalla) -> None:
    pos_mouse = pygame.mouse.get_pos()
    fondo = v.recursos.fondos.get("menu") or v.recursos.fondos.get("menu_principal")
    pantalla.blit(fondo, (0, 0)) if fondo else pantalla.fill((230, 240, 250))

    v._dibujar_letrero_titulo(pantalla, "¡Elige un lugar para explorar!", y_centro=50, ancho=460)
    tiempo_ticks = pygame.time.get_ticks()

    for idx, (bioma, rect_base) in enumerate(v.rects_zonas_tarjetas.items()):
        offset_y = int(math.sin((tiempo_ticks * 0.003) + idx) * 4)
        rect = rect_base.move(0, offset_y)
        es_hover = rect.collidepoint(pos_mouse)
        rect_dibujo = rect.copy()

        if es_hover:
            rect_dibujo.inflate_ip(8, 8)
            rect_dibujo.y -= 3

        sombra = pygame.Surface((rect_dibujo.width, rect_dibujo.height), pygame.SRCALPHA)
        pygame.draw.rect(sombra, (0, 0, 0, 45), (0, 0, rect_dibujo.width, rect_dibujo.height), border_radius=22)
        pantalla.blit(sombra, (rect_dibujo.x, rect_dibujo.y + 5))

        surf_bioma = getattr(v.recursos, "fondos_biomas", {}).get(bioma) or v.recursos.fondos.get(bioma)

        if surf_bioma:
            img_escalada = pygame.transform.smoothscale(surf_bioma, (rect_dibujo.width, rect_dibujo.height))
            tarjeta = aplicar_marco_capsula(img_escalada, radio_borde=22, grosor_borde=5)
            pantalla.blit(tarjeta, rect_dibujo.topleft)
            
            if es_hover:
                brillo_overlay = pygame.Surface(tarjeta.get_size(), pygame.SRCALPHA)
                pygame.draw.rect(brillo_overlay, (255, 255, 255, 45), brillo_overlay.get_rect(), border_radius=22)
                pantalla.blit(brillo_overlay, rect_dibujo.topleft)
        else:
            color_bg = const.COLORES_BIOMAS.get(bioma, {}).get("arriba", (200, 200, 200))
            pygame.draw.rect(pantalla, color_bg, rect_dibujo, border_radius=22)
            pygame.draw.rect(pantalla, (255, 255, 255), rect_dibujo, width=4, border_radius=22)

        badge = v.badges_zonas[bioma]
        rect_badge = badge.get_rect(center=(rect_dibujo.centerx, rect_dibujo.bottom - 10))
        
        if es_hover:
            w_b, h_b = int(badge.get_width() * 1.05), int(badge.get_height() * 1.05)
            badge_esc = pygame.transform.smoothscale(badge, (w_b, h_b))
            pantalla.blit(badge_esc, badge_esc.get_rect(center=(rect_dibujo.centerx, rect_dibujo.bottom - 10)))
        else:
            pantalla.blit(badge, rect_badge)

    v.dibujar_boton_con_hover(pantalla, v.surf_btn_volver, v.rect_btn_volver, pos_mouse)


def dibujar_pantalla_resultados(v, pantalla, puntuacion_final: int, total_posible: int, aciertos: int, fallos: int) -> None:
    pos_mouse = pygame.mouse.get_pos()
    fondo = v.recursos.fondos.get("modos")
    pantalla.blit(fondo, (0, 0)) if fondo else pantalla.fill((230, 240, 250))

    ancho_p, alto_p = 560, 480
    x_p, y_p = (const.ANCHO_PANTALLA // 2) - (ancho_p // 2), 80
    
    surf_panel = pygame.Surface((ancho_p, alto_p), pygame.SRCALPHA)
    pygame.draw.rect(surf_panel, (0, 0, 0, 45), (0, 8, ancho_p, alto_p), border_radius=35)
    pygame.draw.rect(surf_panel, (255, 255, 255, 230), (0, 0, ancho_p, alto_p), border_radius=35)
    pygame.draw.rect(surf_panel, (255, 215, 0), (0, 0, ancho_p, alto_p), width=5, border_radius=35)
    pantalla.blit(surf_panel, (x_p, y_p))

    titulo = v.fuente_titulo.render("¡Juego terminado!", True, const.COLOR_TEXTO_DARK)
    pantalla.blit(titulo, titulo.get_rect(center=(const.ANCHO_PANTALLA // 2, 140)))

    txt_score = v.fuente_titulo.render(f"Puntuación: {puntuacion_final} / {total_posible}", True, (30, 60, 140))
    pantalla.blit(txt_score, txt_score.get_rect(center=(const.ANCHO_PANTALLA // 2, 205)))

    surf_aciertos = crear_etiqueta_glossy(f" Aciertos: {aciertos} ", v.fuente_texto, (110, 220, 90), (35, 130, 45))
    surf_fallos = crear_etiqueta_glossy(f" Fallos: {fallos} ", v.fuente_texto, (240, 65, 65), (150, 20, 20))
    pantalla.blit(surf_aciertos, surf_aciertos.get_rect(center=(const.ANCHO_PANTALLA // 2 - 110, 275)))
    pantalla.blit(surf_fallos, surf_fallos.get_rect(center=(const.ANCHO_PANTALLA // 2 + 110, 275)))

    if aciertos >= fallos:
        linea1, linea2, color_msg = "¡Excelente trabajo!", "Demostraste un gran conocimiento", (46, 125, 50)
    else:
        linea1, linea2, color_msg = "¡No te desanimes!", "Sigue practicando para mejorar.", (211, 47, 47)

    txt1 = v.fuente_texto.render(linea1, True, color_msg)
    pantalla.blit(txt1, txt1.get_rect(center=(const.ANCHO_PANTALLA // 2, 350)))
    txt2 = v.fuente_texto.render(linea2, True, color_msg)
    pantalla.blit(txt2, txt2.get_rect(center=(const.ANCHO_PANTALLA // 2, 385)))

    v.dibujar_boton_con_hover(pantalla, v.surf_btn_reiniciar, v.rect_btn_reiniciar, pos_mouse)
