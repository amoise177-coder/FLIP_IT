"""
MenteActiva — Clase Tablero
Encapsula la matriz bidimensional de cartas, la lógica de selección,
evaluación de parejas y el cálculo dinámico del layout.
"""
import random
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, CARD_MARGIN,
    CARD_MIN_SIZE, CARD_MAX_SIZE, THEMES,
)
from core.carta import Carta


class Tablero:
    """
    Representa el tablero de juego como una matriz bidimensional de Cartas.

    Responsabilidades:
        - Generar y barajar las parejas de cartas.
        - Calcular el tamaño y posición de cada carta dinámicamente.
        - Gestionar las selecciones (primera y segunda carta).
        - Evaluar coincidencias.
        - Consultar el estado del juego (completo o no).

    Atributos:
        filas (int): Número de filas del tablero.
        columnas (int): Número de columnas del tablero.
        cartas (list[Carta]): Lista plana de todas las cartas.
        matriz (list[list[Carta]]): Vista matricial del tablero.
    """

    def __init__(self, filas, columnas, num_parejas, tema_key="naturaleza"):
        self._filas = filas
        self._columnas = columnas
        self._num_parejas = num_parejas
        self._tema_key = tema_key

        self._cartas = []      # lista plana
        self._matriz = []      # lista de listas (filas x columnas)
        self._primera = None   # primera carta seleccionada
        self._segunda = None   # segunda carta seleccionada

        # Navegación por teclado
        self._cursor_row = 0
        self._cursor_col = 0

        # Área de renderizado
        self._offset_x = 0
        self._offset_y = 0
        self._card_size = CARD_MIN_SIZE

        self._generar_tablero()

    # ── Propiedades ──────────────────────────────────────────────────────

    @property
    def filas(self):
        return self._filas

    @property
    def columnas(self):
        return self._columnas

    @property
    def cartas(self):
        return list(self._cartas)

    @property
    def matriz(self):
        return self._matriz

    @property
    def primera_seleccion(self):
        return self._primera

    @property
    def segunda_seleccion(self):
        return self._segunda

    @property
    def cursor_pos(self):
        return (self._cursor_row, self._cursor_col)

    # ── Generación del tablero ───────────────────────────────────────────

    def _generar_tablero(self):
        """
        Genera las cartas con parejas aleatorias y las distribuye
        en la matriz bidimensional.
        """
        tema = THEMES.get(self._tema_key, THEMES["naturaleza"])
        icon_names = tema["icons"]
        theme_color = tema["color"]

        # Seleccionar los íconos necesarios (num_parejas)
        selected_icons = icon_names[:self._num_parejas]

        # Crear parejas de cartas
        card_list = []
        for pair_id, icon_name in enumerate(selected_icons):
            card_list.append(Carta(pair_id, icon_name, theme_color))
            card_list.append(Carta(pair_id, icon_name, theme_color))

        # Barajar aleatoriamente
        random.shuffle(card_list)

        # Organizar en matriz
        self._cartas = card_list
        self._matriz = []
        idx = 0
        for row in range(self._filas):
            fila = []
            for col in range(self._columnas):
                if idx < len(card_list):
                    fila.append(card_list[idx])
                    idx += 1
                else:
                    fila.append(None)
            self._matriz.append(fila)

        # Calcular layout
        self._calcular_layout()

    def _calcular_layout(self, area_top=90, area_bottom=80):
        """
        Calcula dinámicamente el tamaño y posición de cada carta
        según el tamaño del tablero y el área disponible.
        """
        area_w = WINDOW_WIDTH - CARD_MARGIN * 2
        area_h = WINDOW_HEIGHT - area_top - area_bottom

        # Calcular tamaño máximo de carta que cabe en la grilla
        max_card_w = (area_w - CARD_MARGIN * (self._columnas + 1)) // self._columnas
        max_card_h = (area_h - CARD_MARGIN * (self._filas + 1)) // self._filas
        card_size = min(max_card_w, max_card_h)
        card_size = max(CARD_MIN_SIZE, min(CARD_MAX_SIZE, card_size))
        self._card_size = card_size

        # Calcular offset para centrar el tablero
        total_w = self._columnas * card_size + (self._columnas - 1) * CARD_MARGIN
        total_h = self._filas * card_size + (self._filas - 1) * CARD_MARGIN
        self._offset_x = (WINDOW_WIDTH - total_w) // 2
        self._offset_y = area_top + (area_h - total_h) // 2

        # Asignar rect a cada carta
        for row in range(self._filas):
            for col in range(self._columnas):
                carta = self._matriz[row][col]
                if carta:
                    x = self._offset_x + col * (card_size + CARD_MARGIN)
                    y = self._offset_y + row * (card_size + CARD_MARGIN)
                    carta.rect = pygame.Rect(x, y, card_size, card_size)

    # ── Selección e interacción ──────────────────────────────────────────

    def obtener_carta_en(self, pos):
        """Retorna la carta bajo la posición del mouse, o None."""
        for carta in self._cartas:
            if carta and carta.contiene_punto(pos):
                return carta
        return None

    def seleccionar_carta(self, carta):
        """
        Intenta seleccionar una carta.
        Retorna:
            "primera" - si es la primera selección.
            "segunda" - si es la segunda selección (evaluar coincidencia).
            None - si la carta no es seleccionable.
        """
        if not carta or not carta.is_clickable:
            return None

        if self._primera is None:
            self._primera = carta
            carta.voltear()
            return "primera"

        elif self._segunda is None and carta is not self._primera:
            self._segunda = carta
            carta.voltear()
            return "segunda"

        return None

    def evaluar_coincidencia(self):
        """
        Evalúa si las dos cartas seleccionadas son pareja.
        Retorna True si coinciden, False si no.
        """
        if self._primera is None or self._segunda is None:
            return None

        return self._primera.pair_id == self._segunda.pair_id

    def confirmar_acierto(self):
        """Marca ambas cartas como emparejadas y limpia la selección."""
        if self._primera and self._segunda:
            self._primera.emparejar()
            self._segunda.emparejar()
        self._primera = None
        self._segunda = None

    def confirmar_fallo(self):
        """Oculta ambas cartas y limpia la selección."""
        if self._primera:
            self._primera.ocultar()
        if self._segunda:
            self._segunda.ocultar()
        self._primera = None
        self._segunda = None

    def limpiar_seleccion(self):
        """Limpia la selección actual sin cambiar el estado de las cartas."""
        self._primera = None
        self._segunda = None

    # ── Consultas ────────────────────────────────────────────────────────

    def esta_completo(self):
        """Verifica si todas las parejas han sido encontradas."""
        return all(
            carta.estado.value == "emparejada"
            for carta in self._cartas
            if carta is not None
        )

    def obtener_parejas_encontradas(self):
        """Retorna el número de parejas ya emparejadas."""
        emparejadas = sum(
            1 for carta in self._cartas
            if carta and carta.estado.value == "emparejada"
        )
        return emparejadas // 2

    def obtener_cartas_por_pair_id(self, pair_id):
        """Retorna las cartas con el pair_id dado."""
        return [c for c in self._cartas if c and c.pair_id == pair_id]

    def hay_animacion_activa(self):
        """Verifica si alguna carta está animándose."""
        return any(c.is_animating for c in self._cartas if c)

    # ── Previsualización ─────────────────────────────────────────────────

    def mostrar_todas(self):
        """Muestra todas las cartas (para previsualización)."""
        for carta in self._cartas:
            if carta:
                carta.forzar_visible()

    def ocultar_todas(self):
        """Oculta todas las cartas que no estén emparejadas."""
        for carta in self._cartas:
            if carta and carta.estado.value != "emparejada":
                carta.ocultar()

    # ── Navegación por teclado ───────────────────────────────────────────

    def mover_cursor(self, dr, dc):
        """Mueve el cursor del teclado por la grilla."""
        # Desmarcar anterior
        prev_carta = self._matriz[self._cursor_row][self._cursor_col]
        if prev_carta:
            prev_carta.keyboard_selected = False

        # Mover
        self._cursor_row = (self._cursor_row + dr) % self._filas
        self._cursor_col = (self._cursor_col + dc) % self._columnas

        # Marcar nuevo
        new_carta = self._matriz[self._cursor_row][self._cursor_col]
        if new_carta:
            new_carta.keyboard_selected = True

    def obtener_carta_cursor(self):
        """Retorna la carta bajo el cursor del teclado."""
        return self._matriz[self._cursor_row][self._cursor_col]

    def activar_cursor(self):
        """Activa la selección por teclado (muestra el cursor)."""
        carta = self._matriz[self._cursor_row][self._cursor_col]
        if carta:
            carta.keyboard_selected = True

    def desactivar_cursor(self):
        """Desactiva la selección por teclado."""
        for carta in self._cartas:
            if carta:
                carta.keyboard_selected = False

    # ── Actualización ────────────────────────────────────────────────────

    def actualizar(self, dt):
        """Actualiza la animación de todas las cartas."""
        for carta in self._cartas:
            if carta:
                carta.actualizar(dt)

    # ── Renderizado ──────────────────────────────────────────────────────

    def dibujar(self, surface):
        """Dibuja todas las cartas del tablero."""
        for carta in self._cartas:
            if carta:
                carta.dibujar(surface)

    # ── Reinicio ─────────────────────────────────────────────────────────

    def reiniciar(self):
        """Regenera el tablero con nuevas posiciones aleatorias."""
        for carta in self._cartas:
            if carta:
                carta.reset()
        random.shuffle(self._cartas)
        # Reorganizar matriz
        idx = 0
        for row in range(self._filas):
            for col in range(self._columnas):
                if idx < len(self._cartas):
                    self._matriz[row][col] = self._cartas[idx]
                    idx += 1
        self._primera = None
        self._segunda = None
        self._cursor_row = 0
        self._cursor_col = 0
        self._calcular_layout()
