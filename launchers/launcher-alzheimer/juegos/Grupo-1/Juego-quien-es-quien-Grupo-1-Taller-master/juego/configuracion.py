"""Constantes de configuración compartidas por todo el juego.

Centralizar aquí la resolución, colores, tamaños y rutas evita "números
mágicos" repartidos por el código y mantiene la interfaz consistente.
"""

import os

# --- Ventana -----------------------------------------------------------
ANCHO_VENTANA = 1280
ALTO_VENTANA = 720
FPS = 60
TITULO_VENTANA = "¿Quién es quién?"

# --- Rutas -------------------------------------------------------------
# Siempre relativas a la raíz del proyecto, nunca al directorio desde
# el que se ejecuta el proceso. Esto mantiene la compatibilidad con el
# launcher externo de la materia.
RUTA_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_DATOS = os.path.join(RUTA_BASE, "datos")
RUTA_RECURSOS = os.path.join(RUTA_BASE, "recursos")
RUTA_IMAGENES = os.path.join(RUTA_RECURSOS, "imagenes")
RUTA_SONIDOS = os.path.join(RUTA_RECURSOS, "sonidos")
RUTA_FUENTES = os.path.join(RUTA_RECURSOS, "fuentes")
RUTA_PERSONAJES_JSON = os.path.join(RUTA_DATOS, "personajes.json")

# Fondo estático exclusivo del menú principal.
RUTA_IMAGEN_MENU = os.path.join(RUTA_IMAGENES, "menu_fondo.png")

# Efectos de interfaz.
RUTA_EFECTO_CLIC = os.path.join(RUTA_SONIDOS, "efectos", "clic.wav")
RUTA_EFECTO_CORRECTO = os.path.join(RUTA_SONIDOS, "efectos", "correcto.wav")
RUTA_EFECTO_INCORRECTO = os.path.join(RUTA_SONIDOS, "efectos", "incorrecto.wav")

# Música de fondo por sección.
RUTA_MUSICA_MENU = os.path.join(RUTA_SONIDOS, "musica", "musica_menu")
RUTA_MUSICA_PARTIDA = os.path.join(RUTA_SONIDOS, "musica", "musica_partida")
RUTA_MUSICA_RESULTADO = os.path.join(RUTA_SONIDOS, "musica", "musica_resultado")

# --- Paleta de colores -------------------------------------------------
COLOR_FONDO = (250, 246, 237)
COLOR_FONDO_PANEL = (255, 255, 255)
COLOR_TEXTO = (43, 43, 43)
COLOR_TEXTO_SUAVE = (95, 95, 95)
COLOR_TITULO = (58, 74, 96)
COLOR_BORDE = (210, 200, 185)

COLOR_FONDO_DEGRADADO_ARRIBA = (255, 249, 240)
COLOR_FONDO_DEGRADADO_ABAJO = (234, 219, 196)

COLOR_BOTON = (58, 121, 145)
COLOR_BOTON_HOVER = (78, 148, 175)
COLOR_BOTON_TEXTO = (255, 255, 255)

COLOR_BOTON_SECUNDARIO = (225, 221, 212)
COLOR_BOTON_SECUNDARIO_HOVER = (211, 205, 192)
COLOR_BOTON_SECUNDARIO_TEXTO = (58, 58, 58)

COLOR_CORRECTO = (86, 155, 94)
COLOR_INCORRECTO = (196, 90, 78)

COLOR_SOMBRA = (40, 30, 20)

# --- Tipografía --------------------------------------------------------
NOMBRE_FUENTE = None

TAMANOS_TEXTO = {
    "normal": {
        "titulo": 54,
        "titulo_menu": 74,
        "subtitulo": 30,
        "texto": 26,
        "boton": 26,
        "pequeno": 20,
    },
    "grande": {
        "titulo": 62,
        "titulo_menu": 84,
        "subtitulo": 36,
        "texto": 32,
        "boton": 30,
        "pequeno": 24,
    },
}

PUNTOS_POR_PREGUNTA = 10

# --- Variedad entre partidas -------------------------------------------
TAMANO_FAMILIA_PARTIDA = 3
TOTAL_PREGUNTAS_PARTIDA = 8
