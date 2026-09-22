"""Dibuja un "retrato" de un personaje: rostro con ojos, cejas, nariz y
boca visibles, con sombreado suave, mejillas sonrosadas y un brillo en
la mirada, más un peinado, ropa con sombreado en dos tonos y una sombra
propia en el suelo — todo con formas geométricas de Pygame (sin
depender de archivos de imagen externos), dibujado a mayor resolución y
reducido después (supersampling) para que los bordes se vean suaves en
lugar de dentados.

El resultado de cada combinación (personaje, tamaño, resaltado) se
calcula una sola vez y se reutiliza desde una caché: dibujar un rostro
con todo este detalle en cada fotograma sería innecesariamente costoso,
y como los datos de los personajes no cambian en tiempo de ejecución,
cachear es seguro.
"""

import math

import pygame

COLOR_PIEL = (255, 219, 172)
COLOR_PIEL_SOMBRA = (222, 186, 142)
COLOR_OJO_IRIS = (75, 55, 45)
COLOR_CEJA = (95, 70, 55)
COLOR_BOCA = (165, 70, 65)
COLOR_RUBOR = (235, 130, 120)
COLOR_SOMBRA_SUELO = (35, 25, 20)

_FACTOR_SUPERMUESTREO = 4
_CACHE = {}


def _oscurecer(color, factor=0.75):
    return tuple(max(0, int(c * factor)) for c in color)


def _aclarar(color, factor=0.3):
    return tuple(min(255, int(c + (255 - c) * factor)) for c in color)


def _valor_hash(nombre, modulo):
    """Número pseudoaleatorio pero estable para un nombre dado (mismo
    personaje -> siempre el mismo valor), usado para variar en pequeños
    detalles (grosor de pelo, fase de animación) sin necesitar guardar
    nada en los datos del personaje."""
    return sum((indice + 1) * ord(caracter) for indice, caracter in enumerate(nombre)) % modulo


def _estilo_para(personaje):
    """Devuelve el peinado/accesorios que distinguen a cada personaje.

    Se basa en el rol (para detectar a los abuelos, que llevan canas y
    lentes) y en el género (pelo largo o corto) en vez de enumerar cada
    rol posible uno por uno, para que el banco de personajes pueda tener
    más de los 4 roles originales (tíos, nietos, etc.) sin tener que
    tocar este archivo cada vez. Además, cada personaje recibe una
    pequeña variación propia (más o menos cabello, un flequillo un poco
    distinto) para que dos personajes con el mismo corte no se vean
    idénticos salvo por el color."""
    rol = personaje.rol.lower()
    es_mayor = "abuelo" in rol or "abuela" in rol
    variacion = _valor_hash(personaje.nombre, 100) / 100.0  # 0.0 a 0.99, estable por nombre

    if es_mayor:
        return {
            "color_cabello": (222, 222, 222),
            "pelo_largo": False,
            "flequillo": 0.0,
            "lentes": True,
            "grosor_pelo": 0.85 + variacion * 0.3,
        }

    pelo_largo = personaje.genero == "F"
    return {
        "color_cabello": _oscurecer(personaje.color, 0.55),
        "pelo_largo": pelo_largo,
        "flequillo": (0.30 + variacion * 0.10) if pelo_largo else (0.24 + variacion * 0.12),
        "lentes": False,
        "grosor_pelo": 0.8 + variacion * 0.4,
    }


def _superficie_ovalo(tamano, color):
    superficie = pygame.Surface(tamano, pygame.SRCALPHA)
    pygame.draw.ellipse(superficie, color, superficie.get_rect())
    return superficie


def _renderizar_avatar(personaje, radio, resaltado):
    factor = _FACTOR_SUPERMUESTREO
    radio_lienzo = int(radio * 1.75) + 14
    tam_final = radio_lienzo * 2
    tam_grande = tam_final * factor

    grande = pygame.Surface((tam_grande, tam_grande), pygame.SRCALPHA)
    ccx = ccy = tam_grande // 2
    R = radio * factor

    estilo = _estilo_para(personaje)
    color_cabello = estilo["color_cabello"]
    color_ropa = personaje.color

    if resaltado:
        pygame.draw.circle(grande, (255, 214, 92), (ccx, ccy), R + 8 * factor)

    # --- Sombra propia en el "suelo" ------------------------------------
    sombra_rect = pygame.Rect(0, 0, int(R * 1.7), int(R * 0.45))
    sombra_rect.center = (ccx, ccy + int(R * 1.55))
    sombra_superficie = pygame.Surface(sombra_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(sombra_superficie, (*COLOR_SOMBRA_SUELO, 60), sombra_superficie.get_rect())
    grande.blit(sombra_superficie, sombra_rect.topleft)

    # --- Cuerpo / hombros (ropa con sombreado en dos tonos) --------------
    ancho_hombros = int(R * 1.7)
    alto_hombros = int(R * 1.0)
    rect_hombros = pygame.Rect(0, 0, ancho_hombros, alto_hombros)
    rect_hombros.centerx = ccx
    rect_hombros.top = ccy + int(R * 0.55)
    cuerpo = pygame.Surface((ancho_hombros, alto_hombros), pygame.SRCALPHA)
    pygame.draw.ellipse(cuerpo, color_ropa, cuerpo.get_rect())
    # Sombreado inferior: un overlay blanco (=sin cambios) con una banda
    # gris en la base, multiplicado solo sobre el color (no toca el
    # canal alfa), para oscurecer la parte de abajo sin "borrar" el
    # resto de la prenda ni dejar esquinas negras fuera de la silueta.
    overlay_sombra = pygame.Surface((ancho_hombros, alto_hombros))
    overlay_sombra.fill((255, 255, 255))
    pygame.draw.ellipse(overlay_sombra, (145, 145, 145), (0, alto_hombros * 0.38, ancho_hombros, alto_hombros * 0.7))
    cuerpo.blit(overlay_sombra, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    brillo_cuerpo = pygame.Surface((ancho_hombros, alto_hombros), pygame.SRCALPHA)
    pygame.draw.ellipse(brillo_cuerpo, (255, 255, 255, 45), (ancho_hombros * 0.12, 0, ancho_hombros * 0.5, alto_hombros * 0.4))
    cuerpo.blit(brillo_cuerpo, (0, 0))
    pygame.draw.ellipse(cuerpo, _oscurecer(color_ropa, 0.65), cuerpo.get_rect(), width=max(2, factor))
    grande.blit(cuerpo, rect_hombros.topleft)

    # --- Cabello largo a los lados (si aplica), detrás de la cabeza -----
    grosor_pelo = estilo.get("grosor_pelo", 1.0)
    if estilo["pelo_largo"]:
        for signo in (-1, 1):
            ancho_mechon = int(R * 0.6 * grosor_pelo)
            alto_mechon = int(R * 1.55)
            mechon = _superficie_ovalo((ancho_mechon, alto_mechon), color_cabello)
            brillo = pygame.Surface((ancho_mechon, alto_mechon), pygame.SRCALPHA)
            pygame.draw.ellipse(
                brillo, (255, 255, 255, 35),
                (ancho_mechon * (0.55 if signo > 0 else 0.05), alto_mechon * 0.08, ancho_mechon * 0.4, alto_mechon * 0.7),
            )
            mechon.blit(brillo, (0, 0))
            rect_mechon = mechon.get_rect(center=(ccx + signo * int(R * 0.70), ccy + int(R * 0.35)))
            grande.blit(mechon, rect_mechon.topleft)

    # --- Cabeza (tono de piel neutro) ------------------------------------
    radio_cabeza = int(R * 0.82)
    pygame.draw.circle(grande, COLOR_PIEL, (ccx, ccy), radio_cabeza)

    # --- Cabello superior, recortado sobre la cabeza --------------------
    if estilo["flequillo"] > 0:
        radio_cabello = int(radio_cabeza * 1.05)
        cy_cabello = ccy - int(radio_cabeza * (0.55 + estilo["flequillo"]))
        pygame.draw.circle(grande, color_cabello, (ccx, cy_cabello), radio_cabello)
        pygame.draw.circle(grande, _aclarar(color_cabello, 0.22), (ccx, cy_cabello), int(radio_cabello * 0.5), width=max(2, int(radio_cabello * 0.14)))
    else:
        rect_lados = pygame.Rect(0, 0, int(radio_cabeza * 2.06), int(radio_cabeza * 1.3))
        rect_lados.center = (ccx, ccy - int(radio_cabeza * 0.05))
        pygame.draw.arc(
            grande, color_cabello, rect_lados, math.radians(15), math.radians(165),
            max(3, int(radio_cabeza * 0.22 * grosor_pelo)),
        )
    # Volver a dibujar la cabeza encima para dejar solo un flequillo/borde visible.
    pygame.draw.circle(grande, COLOR_PIEL, (ccx, ccy), radio_cabeza)

    # --- Sombreado suave del rostro (volumen) ---------------------------
    sombra_menton = pygame.Surface((radio_cabeza * 2, radio_cabeza * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(
        sombra_menton, (*COLOR_PIEL_SOMBRA, 90),
        (radio_cabeza * 0.15, radio_cabeza * 1.15, radio_cabeza * 1.7, radio_cabeza * 0.9),
    )
    grande.blit(sombra_menton, (ccx - radio_cabeza, ccy - radio_cabeza))
    brillo_frente = pygame.Surface((radio_cabeza * 2, radio_cabeza * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(
        brillo_frente, (255, 255, 255, 55),
        (radio_cabeza * 0.35, radio_cabeza * 0.15, radio_cabeza * 1.0, radio_cabeza * 0.6),
    )
    grande.blit(brillo_frente, (ccx - radio_cabeza, ccy - radio_cabeza))
    pygame.draw.circle(grande, _oscurecer(COLOR_PIEL, 0.85), (ccx, ccy), radio_cabeza, width=max(2, factor // 2))

    # --- Mejillas sonrosadas ---------------------------------------------
    for signo in (-1, 1):
        rubor = pygame.Surface((int(radio_cabeza * 0.5), int(radio_cabeza * 0.32)), pygame.SRCALPHA)
        pygame.draw.ellipse(rubor, (*COLOR_RUBOR, 70), rubor.get_rect())
        rect_rubor = rubor.get_rect(center=(ccx + signo * int(radio_cabeza * 0.52), ccy + int(radio_cabeza * 0.28)))
        grande.blit(rubor, rect_rubor.topleft)

    # --- Ojos + cejas ------------------------------------------------------
    dx_ojo = int(radio_cabeza * 0.40)
    dy_ojo = -int(radio_cabeza * 0.03)
    radio_ojo = max(4, int(radio_cabeza * 0.19))
    radio_pupila = max(2, int(radio_cabeza * 0.09))
    centros_ojos = []
    for signo in (-1, 1):
        centro_ojo = (ccx + signo * dx_ojo, ccy + dy_ojo)
        centros_ojos.append(centro_ojo)
        pygame.draw.circle(grande, (255, 255, 255), centro_ojo, radio_ojo)
        pygame.draw.circle(grande, COLOR_OJO_IRIS, centro_ojo, radio_pupila)
        pygame.draw.circle(
            grande, (255, 255, 255),
            (centro_ojo[0] - int(radio_pupila * 0.4), centro_ojo[1] - int(radio_pupila * 0.4)),
            max(1, int(radio_pupila * 0.35)),
        )
        pygame.draw.circle(grande, _oscurecer(COLOR_PIEL, 0.9), centro_ojo, radio_ojo, width=max(1, factor // 3))

        rect_ceja = pygame.Rect(0, 0, int(radio_ojo * 2.4), int(radio_ojo * 1.6))
        rect_ceja.center = (centro_ojo[0], centro_ojo[1] - int(radio_ojo * 1.7))
        pygame.draw.arc(
            grande, COLOR_CEJA, rect_ceja, math.radians(20), math.radians(160),
            max(2, radio_ojo // 3),
        )

    # --- Nariz ---------------------------------------------------------------
    pygame.draw.circle(
        grande, COLOR_PIEL_SOMBRA, (ccx, ccy + int(radio_cabeza * 0.22)), max(2, int(radio_cabeza * 0.07))
    )

    # --- Boca (sonrisa) --------------------------------------------------------
    ancho_boca = int(radio_cabeza * 0.78)
    alto_boca = int(radio_cabeza * 0.55)
    rect_boca = pygame.Rect(0, 0, ancho_boca, alto_boca)
    rect_boca.center = (ccx, ccy + int(radio_cabeza * 0.32))
    pygame.draw.arc(
        grande, COLOR_BOCA, rect_boca, math.radians(200), math.radians(340),
        max(2, int(radio_cabeza * 0.08)),
    )

    # --- Lentes (distintivo del abuelo) -----------------------------------
    if estilo["lentes"]:
        color_montura = (80, 80, 80)
        for indice, centro_ojo in enumerate(centros_ojos):
            pygame.draw.circle(grande, color_montura, centro_ojo, radio_ojo + 5, width=max(2, int(radio_ojo * 0.22)))
            if indice == 1:
                pygame.draw.line(
                    grande, (255, 255, 255),
                    (centro_ojo[0] - radio_ojo * 0.2, centro_ojo[1] - radio_ojo * 0.7),
                    (centro_ojo[0] + radio_ojo * 0.3, centro_ojo[1] - radio_ojo * 0.3),
                    max(1, factor // 2),
                )
        pygame.draw.line(
            grande, color_montura,
            (centros_ojos[0][0] + radio_ojo, centros_ojos[0][1]),
            (centros_ojos[1][0] - radio_ojo, centros_ojos[1][1]),
            max(2, int(radio_ojo * 0.22)),
        )

    return pygame.transform.smoothscale(grande, (tam_final, tam_final))


# --- Animación: parpadeo y flotación suave -------------------------------
#
# El retrato en sí se cachea (es costoso de dibujar y no cambia), pero un
# personaje totalmente inmóvil se ve más como una estampa que como un
# personaje "vivo". En vez de volver a generar el dibujo completo cada
# fotograma, se anima con dos toques ligeros y baratos de calcular:
# - un parpadeo breve y periódico (un óvalo del tono de piel sobre cada
#   ojo, dibujado directamente encima del retrato ya cacheado);
# - un vaivén vertical suave (solo se desplaza dónde se pega la imagen).
# La fase de cada animación depende del nombre del personaje para que no
# todos parpadeen ni floten exactamente al mismo tiempo.

def _fase_animacion(nombre):
    return (_valor_hash(nombre, 997) / 997.0) * 12.0


def _esta_parpadeando(nombre, tiempo):
    periodo = 3.2 + _valor_hash(nombre, 5) * 0.5  # entre 3.2 y 5.2 s, propio de cada quien
    t = (tiempo + _fase_animacion(nombre)) % periodo
    return t < 0.13


def _desplazamiento_flotante(nombre, tiempo, amplitud=4.0, periodo=2.6):
    fase = _fase_animacion(nombre)
    return math.sin(((tiempo + fase) / periodo) * 2 * math.pi) * amplitud


def _dibujar_parpadeo(superficie, centro, radio):
    """Dibuja, directamente sobre ``superficie`` (sin caché: es un
    instante momentáneo), un párpado sobre cada ojo del retrato ya
    dibujado en ``centro``, simulando un parpadeo breve."""
    radio_cabeza = radio * 0.82
    dx_ojo = radio_cabeza * 0.40
    dy_ojo = -radio_cabeza * 0.03
    radio_ojo = max(2.0, radio_cabeza * 0.19)
    rect_parpado = pygame.Rect(0, 0, radio_ojo * 2.15, max(2, radio_ojo * 0.85))
    for signo in (-1, 1):
        centro_ojo = (centro[0] + signo * dx_ojo, centro[1] + dy_ojo)
        rect_parpado.center = centro_ojo
        pygame.draw.ellipse(superficie, COLOR_PIEL, rect_parpado)
        pygame.draw.line(
            superficie, _oscurecer(COLOR_PIEL, 0.85),
            (rect_parpado.left, centro_ojo[1]), (rect_parpado.right, centro_ojo[1]),
            max(1, int(radio_ojo * 0.12)),
        )


def dibujar_avatar(superficie, personaje, centro, radio, resaltado=False, flotante=False):
    """Dibuja (usando una caché interna) el retrato de ``personaje``
    centrado en ``centro`` con el tamaño ``radio``. ``resaltado`` añade
    un anillo dorado alrededor (usado para la opción seleccionada).
    ``flotante=True`` agrega un vaivén vertical suave, pensado para los
    retratos de presentación (menú, "conoce a la familia") y no para los
    botones de respuesta, donde conviene que la posición se mantenga
    quieta mientras el jugador decide. El parpadeo, en cambio, se aplica
    siempre: es sutil y no estorba la interacción."""
    clave = (personaje.nombre, radio, resaltado)
    imagen = _CACHE.get(clave)
    if imagen is None:
        imagen = _renderizar_avatar(personaje, radio, resaltado)
        _CACHE[clave] = imagen

    tiempo = pygame.time.get_ticks() / 1000.0
    centro_dibujo = centro
    if flotante:
        centro_dibujo = (centro[0], centro[1] + _desplazamiento_flotante(personaje.nombre, tiempo))

    rect = imagen.get_rect(center=centro_dibujo)
    superficie.blit(imagen, rect.topleft)

    if _esta_parpadeando(personaje.nombre, tiempo):
        _dibujar_parpadeo(superficie, centro_dibujo, radio)
