from pathlib import Path
import pygame

class Configuracion:
    BASE_DIR = Path(__file__).resolve().parent
    ASSETS_DIR = BASE_DIR / "assets"

    ANCHO_VENTANA = 1280
    ALTO_VENTANA = 720

    ESTADO_INICIO = "INICIO"
    ESTADO_SELECCION = "SELECCION"
    ESTADO_JUEGO = "JUEGO"

    COLOR_TEXTO_NAVY = (23, 48, 63)
    COLOR_TEXTO_NAVY_DARK = (15, 40, 55)
    COLOR_TEXTO_MUTED = (77, 105, 123)
    COLOR_FONDO_BASE = (211, 229, 241)
    COLOR_TEAL_BOTON = (47, 168, 155)
    COLOR_TEAL_BORDE = (111, 211, 191)
    COLOR_MENTA_ACTIVA = (203, 238, 229)
    COLOR_LAVANDA_MARCADO = (210, 216, 243)
    COLOR_AZUL_MARCADO_ICON = (61, 80, 150)
    COLOR_BLANCO = (255, 255, 255)
    COLOR_AMBAR_PAUSA = (217, 119, 6)

    NOMBRES_COLUMNAS = ["B", "I", "N", "G", "O"]


BASE_DIR = Configuracion.BASE_DIR
ASSETS_DIR = Configuracion.ASSETS_DIR
ANCHO_VENTANA = Configuracion.ANCHO_VENTANA
ALTO_VENTANA = Configuracion.ALTO_VENTANA
ESTADO_INICIO = Configuracion.ESTADO_INICIO
ESTADO_SELECCION = Configuracion.ESTADO_SELECCION
ESTADO_JUEGO = Configuracion.ESTADO_JUEGO
COLOR_TEXTO_NAVY = Configuracion.COLOR_TEXTO_NAVY
COLOR_TEXTO_NAVY_DARK = Configuracion.COLOR_TEXTO_NAVY_DARK
COLOR_TEXTO_MUTED = Configuracion.COLOR_TEXTO_MUTED
COLOR_FONDO_BASE = Configuracion.COLOR_FONDO_BASE
COLOR_TEAL_BOTON = Configuracion.COLOR_TEAL_BOTON
COLOR_TEAL_BORDE = Configuracion.COLOR_TEAL_BORDE
COLOR_MENTA_ACTIVA = Configuracion.COLOR_MENTA_ACTIVA
COLOR_LAVANDA_MARCADO = Configuracion.COLOR_LAVANDA_MARCADO
COLOR_AZUL_MARCADO_ICON = Configuracion.COLOR_AZUL_MARCADO_ICON
COLOR_BLANCO = Configuracion.COLOR_BLANCO
COLOR_AMBAR_PAUSA = Configuracion.COLOR_AMBAR_PAUSA
NOMBRES_COLUMNAS = Configuracion.NOMBRES_COLUMNAS


class Fuentes:
    @classmethod
    def _cargar_fuente(cls, tamano, negrita=False):
        familias = ["Segoe UI", "Plus Jakarta Sans", "Arial", "Calibri"]
        for familia in familias:
            try:
                f = pygame.font.SysFont(familia, tamano, bold=negrita)
                if f:
                    return f
            except Exception:
                continue
        return pygame.font.Font(None, tamano)

    @classmethod
    def init(cls):
        cls.titulo_inicio = cls._cargar_fuente(46, negrita=True)
        cls.subtitulo_inicio = cls._cargar_fuente(22, negrita=True)
        cls.badge_inicio = cls._cargar_fuente(18, negrita=True)
        cls.footer_inicio = cls._cargar_fuente(16, negrita=False)
        cls.footer_inicio_bold = cls._cargar_fuente(16, negrita=True)
        cls.guia_titulo = cls._cargar_fuente(28, negrita=True)
        cls.guia_paso_num = cls._cargar_fuente(20, negrita=True)
        cls.guia_paso_txt = cls._cargar_fuente(16, negrita=False)

        cls.titulo = cls._cargar_fuente(20, negrita=True)
        cls.subtitulo = cls._cargar_fuente(12, negrita=True)
        cls.normal = cls._cargar_fuente(13, negrita=False)
        cls.normal_bold = cls._cargar_fuente(13, negrita=True)
        cls.columna = cls._cargar_fuente(15, negrita=True)
        cls.riel_letra = cls._cargar_fuente(11, negrita=True)
        cls.riel_nombre = cls._cargar_fuente(13, negrita=True)
        cls.celda_nombre = cls._cargar_fuente(10, negrita=True)
        cls.dialogo_tit = cls._cargar_fuente(24, negrita=True)
        cls.dialogo_txt = cls._cargar_fuente(15, negrita=False)
        cls.btn_modo = cls._cargar_fuente(18, negrita=True)


class GestorMusica:
    PISTA_MENU = ASSETS_DIR / "musica" / "Blossom.ogg"
    PISTA_JUEGO = ASSETS_DIR / "musica" / "melancholy.ogg"
    pista_actual = None

    @classmethod
    def reproducir_menu(cls):
        if cls.pista_actual == cls.PISTA_MENU:
            return
        if cls.PISTA_MENU.exists():
            try:
                pygame.mixer.music.fadeout(350)
                pygame.mixer.music.load(str(cls.PISTA_MENU))
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
                cls.pista_actual = cls.PISTA_MENU
            except Exception:
                pass

    @classmethod
    def reproducir_juego(cls):
        if cls.pista_actual == cls.PISTA_JUEGO:
            return
        if cls.PISTA_JUEGO.exists():
            try:
                pygame.mixer.music.fadeout(350)
                pygame.mixer.music.load(str(cls.PISTA_JUEGO))
                pygame.mixer.music.set_volume(0.30)
                pygame.mixer.music.play(-1)
                cls.pista_actual = cls.PISTA_JUEGO
            except Exception:
                pass


class GestorAssets:
    inicio_fondo = None
    inicio_btn_jugar = None
    inicio_btn_como_jugar = None
    inicio_btn_salir = None
    seleccion_fondo = None
    card_partida_corta = None
    card_partida_media = None
    card_partida_completa = None
    fondo_juego = None
    tablero = None
    recuadro_seleccion = None
    imagenes_formas = {}
    iconos_elementos = {}
    iconos_header = {}

    MAPA_ARCHIVOS_FORMAS = {
        1: "linea central.png",
        2: "linea inferior.png",
        3: "L invertida.png",
        4: "X diagonal.png",
        5: "cuadro interior.png",
        6: "ventana 3x3.png",
        7: "diamante.png",
        8: "Y.png",
        9: "mosaico completo.png",
        10: "marco exterior.png",
        11: "cruz central.png",
        12: "4 faros.png",
        13: "columna B.png",
        14: "carton lleno.png",
    }

    @staticmethod
    def limpiar_halo(surf, umbral=45):
        s = surf.copy()
        try:
            import numpy as np
            alpha = pygame.surfarray.pixels_alpha(s)
            alpha[alpha < umbral] = 0
            del alpha
        except Exception:
            w, h = s.get_size()
            for y in range(h):
                for x in range(w):
                    if s.get_at((x, y))[3] < umbral:
                        s.set_at((x, y), (0, 0, 0, 0))
        return s

    @classmethod
    def extraer_iconos_spritesheets(cls, carpeta_bingo=None):
        if carpeta_bingo is None:
            carpeta_bingo = ASSETS_DIR / "BINGO"

        iconos = {}
        columnas_config = [
            ("B", 1),
            ("I", 16),
            ("N", 31),
            ("G", 46),
            ("O", 61),
        ]

        for letra, id_base in columnas_config:
            ruta = carpeta_bingo / f"{letra}.png"
            if not ruta.exists():
                continue

            try:
                sheet = pygame.image.load(str(ruta)).convert_alpha()
            except Exception:
                continue

            w_sheet, h_sheet = sheet.get_size()
            cw = w_sheet / 5.0
            ch = h_sheet / 3.0

            for idx in range(15):
                item_id = id_base + idx
                fila = idx // 5
                col = idx % 5

                x1 = int(round(col * cw))
                y1 = int(round(fila * ch))
                x2 = int(round((col + 1) * cw))
                y2 = int(round((fila + 1) * ch))
                w = max(1, x2 - x1)
                h = max(1, y2 - y1)

                sub = sheet.subsurface(pygame.Rect(x1, y1, w, h)).copy()

                try:
                    import numpy as np
                    alpha = pygame.surfarray.pixels_alpha(sub)
                    alpha[alpha < 25] = 0
                    del alpha
                except Exception:
                    pass

                bbox = sub.get_bounding_rect()
                sub_crop = sub.subsurface(bbox).copy() if bbox.width > 0 and bbox.height > 0 else sub

                max_tam = 44
                bw, bh = sub_crop.get_size()
                scale = min(max_tam / bw, max_tam / bh)
                nw = max(1, int(round(bw * scale)))
                nh = max(1, int(round(bh * scale)))
                iconos[item_id] = pygame.transform.smoothscale(sub_crop, (nw, nh))

        return iconos

    @classmethod
    def cargar(cls):
        p_inicio = ASSETS_DIR / "pantalla de inicio"
        r_f_ini = p_inicio / "fondo.png"
        if r_f_ini.exists():
            cls.inicio_fondo = pygame.transform.smoothscale(pygame.image.load(str(r_f_ini)).convert(), (ANCHO_VENTANA, ALTO_VENTANA))
        else:
            cls.inicio_fondo = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            cls.inicio_fondo.fill(COLOR_FONDO_BASE)

        r_jugar = p_inicio / "Jugar.png"
        if r_jugar.exists():
            img_j = cls.limpiar_halo(pygame.image.load(str(r_jugar)).convert_alpha(), umbral=45)
            cls.inicio_btn_jugar = pygame.transform.smoothscale(img_j, (540, 440))
        else:
            cls.inicio_btn_jugar = pygame.Surface((540, 440), pygame.SRCALPHA)
            pygame.draw.rect(cls.inicio_btn_jugar, COLOR_TEAL_BOTON, (0, 0, 540, 440), border_radius=32)

        r_cj = p_inicio / "como jugar.png"
        if r_cj.exists():
            img_cj = cls.limpiar_halo(pygame.image.load(str(r_cj)).convert_alpha(), umbral=45)
            cls.inicio_btn_como_jugar = pygame.transform.smoothscale(img_cj, (580, 205))
        else:
            cls.inicio_btn_como_jugar = pygame.Surface((580, 205), pygame.SRCALPHA)
            pygame.draw.rect(cls.inicio_btn_como_jugar, (219, 234, 242), (0, 0, 580, 205), border_radius=28)

        r_salir = p_inicio / "salir.png"
        if r_salir.exists():
            img_s = cls.limpiar_halo(pygame.image.load(str(r_salir)).convert_alpha(), umbral=45)
            cls.inicio_btn_salir = pygame.transform.smoothscale(img_s, (580, 205))
        else:
            cls.inicio_btn_salir = pygame.Surface((580, 205), pygame.SRCALPHA)
            pygame.draw.rect(cls.inicio_btn_salir, (219, 234, 242), (0, 0, 580, 205), border_radius=28)

        p_sel = ASSETS_DIR / "pantalla de seleccion"
        r_f_sel = p_sel / "fondo.png"
        if r_f_sel.exists():
            cls.seleccion_fondo = pygame.transform.smoothscale(pygame.image.load(str(r_f_sel)).convert(), (ANCHO_VENTANA, ALTO_VENTANA))
        else:
            cls.seleccion_fondo = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            cls.seleccion_fondo.fill(COLOR_FONDO_BASE)

        dim_card = (340, 465)
        r_corta = p_sel / "partida corta.png"
        if r_corta.exists():
            img_corta = cls.limpiar_halo(pygame.image.load(str(r_corta)).convert_alpha(), umbral=35)
            cls.card_partida_corta = pygame.transform.smoothscale(img_corta, dim_card)
        else:
            cls.card_partida_corta = pygame.Surface(dim_card, pygame.SRCALPHA)
            pygame.draw.rect(cls.card_partida_corta, (227, 246, 241), (0, 0, 340, 465), border_radius=24)

        r_media = p_sel / "Partida media.png"
        if r_media.exists():
            img_media = cls.limpiar_halo(pygame.image.load(str(r_media)).convert_alpha(), umbral=35)
            cls.card_partida_media = pygame.transform.smoothscale(img_media, dim_card)
        else:
            cls.card_partida_media = pygame.Surface(dim_card, pygame.SRCALPHA)
            pygame.draw.rect(cls.card_partida_media, (254, 246, 233), (0, 0, 340, 465), border_radius=24)

        r_completa = p_sel / "Partida completa.png"
        if r_completa.exists():
            img_comp = cls.limpiar_halo(pygame.image.load(str(r_completa)).convert_alpha(), umbral=35)
            cls.card_partida_completa = pygame.transform.smoothscale(img_comp, dim_card)
        else:
            cls.card_partida_completa = pygame.Surface(dim_card, pygame.SRCALPHA)
            pygame.draw.rect(cls.card_partida_completa, (253, 235, 237), (0, 0, 340, 465), border_radius=24)

        ruta_fondo_juego = ASSETS_DIR / "fondo" / "zzzz.png"
        if ruta_fondo_juego.exists():
            img_f = pygame.image.load(str(ruta_fondo_juego)).convert()
            cls.fondo_juego = pygame.transform.smoothscale(img_f, (ANCHO_VENTANA, ALTO_VENTANA))
        else:
            cls.fondo_juego = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            cls.fondo_juego.fill((208, 228, 241))

        ruta_tablero = ASSETS_DIR / "carton" / "tablero de bingo.png"
        if ruta_tablero.exists():
            cls.tablero = pygame.image.load(str(ruta_tablero)).convert_alpha()
        else:
            cls.tablero = pygame.Surface((474, 558), pygame.SRCALPHA)
            pygame.draw.rect(cls.tablero, (211, 229, 238), (0, 0, 474, 558), border_radius=16)

        ruta_rs = ASSETS_DIR / "carton" / "recuadro seleccion.png"
        if ruta_rs.exists():
            img_rs = pygame.image.load(str(ruta_rs)).convert_alpha()
            cls.recuadro_seleccion = pygame.transform.smoothscale(img_rs, (80, 80))
        else:
            cls.recuadro_seleccion = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.rect(cls.recuadro_seleccion, COLOR_LAVANDA_MARCADO, (0, 0, 80, 80), border_radius=12)

        carpeta_formas = ASSETS_DIR / "rectangulos de formas"
        for forma_id, nombre_arch in cls.MAPA_ARCHIVOS_FORMAS.items():
            ruta = carpeta_formas / nombre_arch
            if ruta.exists():
                img_forma = pygame.image.load(str(ruta)).convert_alpha()
                cls.imagenes_formas[forma_id] = pygame.transform.smoothscale(img_forma, (186, 78))

        cls.iconos_elementos = cls.extraer_iconos_spritesheets(ASSETS_DIR / "BINGO")
        cls.iconos_header = {}
        for item_id, surf in cls.iconos_elementos.items():
            w, h = surf.get_size()
            esc = min(30 / w, 30 / h)
            nw = max(1, int(round(w * esc)))
            nh = max(1, int(round(h * esc)))
            cls.iconos_header[item_id] = pygame.transform.smoothscale(surf, (nw, nh))


def inicializar_sistema_recursos():
    pygame.init()
    pygame.font.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    Fuentes.init()
    GestorAssets.cargar()
