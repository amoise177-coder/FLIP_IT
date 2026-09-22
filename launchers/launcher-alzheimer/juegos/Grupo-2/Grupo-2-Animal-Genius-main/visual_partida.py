import pygame
from constants import const
from ui_components import crear_etiqueta_glossy, aplicar_marco_capsula, crear_boton_glossy

def dibujar_interfaz(v, pantalla, carta_actual, puntuacion: int, mensaje: str, revelada: bool = False, modo: str = "normal", tiempo_restante: float = 0.0, tiempo_agotado: bool = False) -> None:
    pos_mouse = pygame.mouse.get_pos()
    fondo = v.recursos.fondos.get("juego")
    pantalla.blit(fondo, (0, 0)) if fondo else pantalla.fill((240, 240, 240))

    titulo_pregunta = "¿Cuál animal es?" if modo != "rasca" else "Rasca y descubre el animal"
    v._dibujar_letrero_titulo(pantalla, titulo_pregunta, y_centro=55, ancho=420)

    badge_puntos = crear_etiqueta_glossy(f"Puntos: {puntuacion}", v.fuente_texto, (85, 165, 255), (20, 65, 175))
    pantalla.blit(badge_puntos, (30, 30))

    if carta_actual:
        if v._ultima_carta_procesada != carta_actual.nombre_imagen:
            v._opciones_actuales = carta_actual.obtener_opciones_mezcladas()
            v._ultima_carta_procesada = carta_actual.nombre_imagen
            v._surfaces_opciones_actuales = [
                crear_boton_glossy(op, v.fuente_texto, rect.width, rect.height, color_arriba=(255, 160, 40), color_abajo=(210, 85, 10))
                for op, rect in zip(v._opciones_actuales, v.rects_opciones)
            ]
            if modo == "rasca":
                v._inicializar_grilla_rasca()
            v._imagen_actual_escalada = v.recursos.cargar_imagen_animal(carta_actual.nombre_imagen, ancho=420, alto=290)

    if modo == "rasca":
        limite_revelar = int(v._total_bloques_inicial * 0.12)
        bloques_revelados = v._total_bloques_inicial - len(v._bloques_rasca)
        porcentaje = max(0.0, 1.0 - (bloques_revelados / limite_revelar)) if limite_revelar > 0 else 0.0

        ancho_b, alto_b = 320, 16
        x_b, y_b = (const.ANCHO_PANTALLA // 2) - (ancho_b // 2), 95
        pygame.draw.rect(pantalla, (200, 200, 200), (x_b, y_b, ancho_b, alto_b), border_radius=8)
        color_barra = (76, 175, 80) if porcentaje > 0.25 else (244, 67, 54)
        if porcentaje > 0:
            pygame.draw.rect(pantalla, color_barra, (x_b, y_b, int(ancho_b * porcentaje), alto_b), border_radius=8)
        pygame.draw.rect(pantalla, (255, 255, 255), (x_b, y_b, ancho_b, alto_b), width=2, border_radius=8)

    pos_x, pos_y = (pantalla.get_width() // 2) - 210, 135

    # Dibujar la imagen base del animal con su marco
    if v._imagen_actual_escalada:
        img_con_marco = aplicar_marco_capsula(v._imagen_actual_escalada, radio_borde=30, grosor_borde=6)
        pantalla.blit(img_con_marco, (pos_x, pos_y))
    else:
        pygame.draw.rect(pantalla, (220, 220, 220), (pos_x, pos_y, 420, 290), border_radius=30)

    # Dibujar la capa de rascado SOLO si aún existen bloques ocultos
    if modo == "rasca" and v._bloques_rasca:
        surf_rasca = pygame.Surface((420, 290), pygame.SRCALPHA)
        for bloque in v._bloques_rasca:
            rect_local = bloque.move(-pos_x, -pos_y)
            pygame.draw.rect(surf_rasca, (150, 150, 150), rect_local)
            pygame.draw.rect(surf_rasca, (100, 100, 100), rect_local, width=1)
        
        mascara = pygame.Surface((420, 290), pygame.SRCALPHA)
        pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, 420, 290), border_radius=30)
        surf_rasca.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pantalla.blit(surf_rasca, (pos_x, pos_y))
        pygame.draw.rect(pantalla, (255, 255, 255), (pos_x, pos_y, 420, 290), width=6, border_radius=30)

    if mensaje:
        ancho_t, alto_t = 420, 48
        x_t, y_t = (const.ANCHO_PANTALLA // 2) - (ancho_t // 2), 438
        es_acierto = "Correcto" in mensaje or "bien" in mensaje.lower()
        color_borde = (46, 125, 50) if es_acierto else (211, 47, 47)

        surf_toast = pygame.Surface((ancho_t, alto_t), pygame.SRCALPHA)
        pygame.draw.rect(surf_toast, (0, 0, 0, 35), (0, 4, ancho_t, alto_t), border_radius=24)
        pygame.draw.rect(surf_toast, (255, 255, 255, 245), (0, 0, ancho_t, alto_t), border_radius=24)
        pygame.draw.rect(surf_toast, color_borde, (0, 0, ancho_t, alto_t), width=3, border_radius=24)

        txt_msg = v.fuente_titulo.render(mensaje, True, color_borde)
        surf_toast.blit(txt_msg, txt_msg.get_rect(center=(ancho_t // 2, alto_t // 2)))
        pantalla.blit(surf_toast, (x_t, y_t))

    for i, rect in enumerate(v.rects_opciones):
        if i < len(v._surfaces_opciones_actuales):
            superficie_a_dibujar = v._surfaces_opciones_actuales[i]
            if v._indice_seleccion_usuario == i:
                color_arriba_din = (110, 220, 90) if v._es_respuesta_correcta else (240, 65, 65)
                color_abajo_din = (35, 130, 45) if v._es_respuesta_correcta else (150, 20, 20)
                superficie_a_dibujar = crear_boton_glossy(
                    v._opciones_actuales[i], v.fuente_texto, rect.width, rect.height,
                    color_arriba=color_arriba_din, color_abajo=color_abajo_din
                )
            v.dibujar_boton_con_hover(pantalla, superficie_a_dibujar, rect, pos_mouse)


def dibujar_ronda_sino(v, pantalla, pregunta_actual, puntuacion: int, mensaje: str) -> None:
    pos_mouse = pygame.mouse.get_pos()
    fondo = v.recursos.fondos.get("juego")
    pantalla.blit(fondo, (0, 0)) if fondo else pantalla.fill((240, 240, 240))

    v._dibujar_letrero_titulo(pantalla, "Ronda Rápida: ¿Sí o No?", y_centro=60, ancho=440)

    badge_puntos = crear_etiqueta_glossy(f"Puntos: {puntuacion}", v.fuente_texto, (85, 165, 255), (20, 65, 175))
    pantalla.blit(badge_puntos, (30, 30))

    if pregunta_actual:
        txt_preg = v.fuente_titulo.render(pregunta_actual.enunciado, True, (255, 255, 255))
        pantalla.blit(txt_preg, txt_preg.get_rect(center=(const.ANCHO_PANTALLA // 2, 260)))

    if mensaje:
        ancho_t, alto_t = 420, 48
        x_t, y_t = (const.ANCHO_PANTALLA // 2) - (ancho_t // 2), 390
        es_acierto = "Correcto" in mensaje or "bien" in mensaje.lower()
        color_borde = (46, 125, 50) if es_acierto else (211, 47, 47)

        surf_toast = pygame.Surface((ancho_t, alto_t), pygame.SRCALPHA)
        pygame.draw.rect(surf_toast, (0, 0, 0, 35), (0, 4, ancho_t, alto_t), border_radius=24)
        pygame.draw.rect(surf_toast, (255, 255, 255, 245), (0, 0, ancho_t, alto_t), border_radius=24)
        pygame.draw.rect(surf_toast, color_borde, (0, 0, ancho_t, alto_t), width=3, border_radius=24)

        txt_msg = v.fuente_titulo.render(mensaje, True, color_borde)
        surf_toast.blit(txt_msg, txt_msg.get_rect(center=(ancho_t // 2, alto_t // 2)))
        pantalla.blit(surf_toast, (x_t, y_t))

    v.dibujar_boton_con_hover(pantalla, v.surf_btn_si, v.rect_btn_si, pos_mouse)
    v.dibujar_boton_con_hover(pantalla, v.surf_btn_no, v.rect_btn_no, pos_mouse)
