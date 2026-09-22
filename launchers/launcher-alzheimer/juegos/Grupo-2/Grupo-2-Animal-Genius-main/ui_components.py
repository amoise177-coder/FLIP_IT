import pygame

def crear_etiqueta_glossy(texto: str, fuente: pygame.font.Font, color_arriba: tuple, color_abajo: tuple) -> pygame.Surface:
    render_texto = fuente.render(texto, True, (255, 255, 255))
    w_text, h_text = render_texto.get_size()

    pad_x, pad_y = 20, 8
    ancho = w_text + (pad_x * 2)
    alto = h_text + (pad_y * 2)

    surf = pygame.Surface((ancho, alto + 4), pygame.SRCALPHA)

    pygame.draw.rect(surf, color_abajo, (0, 4, ancho, alto), border_radius=alto // 2)

    pygame.draw.rect(surf, color_arriba, (0, 0, ancho, alto), border_radius=alto // 2)

    pygame.draw.rect(surf, (255, 255, 255), (0, 0, ancho, alto), width=3, border_radius=alto // 2)

    sombra_texto = fuente.render(texto, True, (0, 0, 0, 110))
    surf.blit(sombra_texto, (pad_x + 1, pad_y + 2))
    surf.blit(render_texto, (pad_x, pad_y))

    return surf


def crear_boton_glossy(
    texto: str, 
    fuente: pygame.font.Font, 
    ancho: int, 
    alto: int, 
    color_arriba: tuple = (100, 200, 255), 
    color_abajo: tuple = (30, 100, 200)
) -> pygame.Surface:
    btn = pygame.Surface((ancho, alto), pygame.SRCALPHA)

    grad_1x2 = pygame.Surface((1, 2), pygame.SRCALPHA)
    grad_1x2.set_at((0, 0), (*color_arriba, 255))
    grad_1x2.set_at((0, 1), (*color_abajo, 255))
    grad_surf = pygame.transform.smoothscale(grad_1x2, (ancho, alto))

    mask = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, ancho, alto), border_radius=alto // 2)

    grad_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    btn.blit(grad_surf, (0, 0))

    brillo = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.ellipse(brillo, (255, 255, 255, 100), (6, 2, ancho - 12, alto // 2))
    brillo.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    btn.blit(brillo, (0, 0))

    pygame.draw.rect(btn, (255, 255, 255), (0, 0, ancho, alto), width=5, border_radius=alto // 2)

    txt_surf = fuente.render(texto, True, (255, 255, 255))
    sombra = fuente.render(texto, True, (0, 0, 0))
    sombra.set_alpha(120)
    t_rect = txt_surf.get_rect(center=(ancho // 2, alto // 2))

    btn.blit(sombra, (t_rect.x + 1, t_rect.y + 2))
    btn.blit(txt_surf, t_rect)

    return btn


def dibujar_indicadores_progreso(
    pantalla: pygame.Surface, 
    x_centro: int, 
    y: int, 
    total_preguntas: int, 
    resultados: list[str],
    radio: int = 10,
    espacio: int = 30
) -> None:
    ancho_total = (total_preguntas * espacio) - (espacio - (radio * 2))
    inicio_x = x_centro - (ancho_total // 2)

    for i in range(total_preguntas):
        x = inicio_x + (i * espacio)
        estado = resultados[i] if i < len(resultados) else "pendiente"

        if estado == "acierto":
            color_relleno = (76, 175, 80)
            color_borde = (56, 142, 60)
        elif estado == "fallo":
            color_relleno = (244, 67, 54)
            color_borde = (198, 40, 40)
        else: # pendiente
            color_relleno = (255, 255, 255)
            color_borde = (76, 175, 80)

        pygame.draw.circle(pantalla, color_relleno, (x, y), radio)
        pygame.draw.circle(pantalla, color_borde, (x, y), radio, width=2)


def aplicar_marco_capsula(
    imagen: pygame.Surface, 
    radio_borde: int = 25, 
    grosor_borde: int = 6, 
    color_borde: tuple = (255, 255, 255)
) -> pygame.Surface:
    ancho, alto = imagen.get_size()
    superficie_final = pygame.Surface((ancho, alto), pygame.SRCALPHA)

    mascara = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, ancho, alto), border_radius=radio_borde)

    superficie_final.blit(imagen, (0, 0))
    superficie_final.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    pygame.draw.rect(superficie_final, color_borde, (0, 0, ancho, alto), width=grosor_borde, border_radius=radio_borde)

    return superficie_final


def crear_boton_capsula_volver(
    texto: str, 
    fuente: pygame.font.Font, 
    ancho: int = 180, 
    alto: int = 48,
    color_arriba: tuple = (235, 75, 75), 
    color_abajo: tuple = (180, 40, 40)
) -> pygame.Surface:
    surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)

    pygame.draw.rect(surf, color_abajo, (0, 4, ancho, alto - 4), border_radius=alto // 2)

    pygame.draw.rect(surf, color_arriba, (0, 0, ancho, alto - 4), border_radius=alto // 2)

    brillo = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.ellipse(brillo, (255, 255, 255, 90), (6, 2, ancho - 12, (alto - 4) // 2))
    
    mascara = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.rect(mascara, (255, 255, 255, 255), (0, 0, ancho, alto - 4), border_radius=alto // 2)
    brillo.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(brillo, (0, 0))

    pygame.draw.rect(surf, (255, 255, 255), (0, 0, ancho, alto - 4), width=3, border_radius=alto // 2)

    txt_surf = fuente.render(texto, True, (255, 255, 255))
    sombra = fuente.render(texto, True, (0, 0, 0, 110))
    t_rect = txt_surf.get_rect(center=(ancho // 2, (alto - 4) // 2))

    surf.blit(sombra, (t_rect.x + 1, t_rect.y + 2))
    surf.blit(txt_surf, t_rect)

    return surf
