from typing import Optional, List, Tuple, Any, Set

class Board:
    """
    Representa el tablero de juego como una matriz bidimensional.
    Encapsula el estado de las celdas y las operaciones de colocación y retiro.
    """

    def __init__(self, rows: int = 7, cols: int = 7):
        if rows <= 0 or cols <= 0:
            raise ValueError("Las dimensiones del tablero deben ser números positivos.")
        self._rows = rows
        self._cols = cols
        # Matriz interna privada: contiene objetos Tile o None
        self._grid: List[List[Optional[Any]]] = [
            [None for _ in range(cols)] for _ in range(rows)
        ]
        # Registro de fichas colocadas en la jugada en curso
        self._current_placed_tiles: List[Any] = []
        # Dirección elegida para la palabra actual: horizontal o vertical
        self._direction: str = "horizontal"
        # Registro histórico de palabras consolidadas en este tablero para evitar repeticiones
        self._formed_words: List[str] = []

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def current_placed_tiles(self) -> List[Any]:
        return list(self._current_placed_tiles)

    def is_valid_coordinate(self, row: int, col: int) -> bool:
        return 0 <= row < self._rows and 0 <= col < self._cols

    def is_cell_empty(self, row: int, col: int) -> bool:
        return self.is_valid_coordinate(row, col) and self._grid[row][col] is None

    def get_tile(self, row: int, col: int) -> Optional[Any]:
        return self._grid[row][col] if self.is_valid_coordinate(row, col) else None

    @property
    def direction(self) -> str:
        return self._direction

    def set_direction(self, direction: str) -> bool:
        """Establece la dirección de la palabra que se está formando."""
        direction = str(direction).lower().strip()
        if direction not in ("horizontal", "vertical"):
            return False
        # No cambiar la dirección a mitad de una jugada.
        if self._current_placed_tiles:
            return direction == self._direction
        self._direction = direction
        return True

    def place_tile(self, tile: Any, row: int, col: int) -> bool:
        """Coloca una ficha respetando la dirección elegida para el turno."""
        if not self.is_cell_empty(row, col):
            return False

        # La primera ficha fija el punto de inicio. Las siguientes deben quedar
        # en la misma fila (horizontal) o columna (vertical).
        if self._current_placed_tiles:
            positions = [t.grid_pos for t in self._current_placed_tiles if getattr(t, "grid_pos", None) is not None]
            if positions:
                first_row, first_col = positions[0]
                if self._direction == "horizontal" and row != first_row:
                    return False
                if self._direction == "vertical" and col != first_col:
                    return False
        self._grid[row][col] = tile
        if hasattr(tile, "grid_pos"):
            tile.grid_pos = (row, col)
        if tile not in self._current_placed_tiles:
            self._current_placed_tiles.append(tile)
        return True

    def remove_tile(self, row: int, col: int) -> Optional[Any]:
        """Retira y devuelve la ficha de la casilla indicada, salvo que esté consolidada."""
        if not self.is_valid_coordinate(row, col):
            return None
        tile = self._grid[row][col]
        if tile is not None:
            if getattr(tile, "locked", False):
                return None
            self._grid[row][col] = None
            if hasattr(tile, "grid_pos"):
                tile.grid_pos = None
            if tile in self._current_placed_tiles:
                self._current_placed_tiles.remove(tile)
        return tile

    def clear_current_turn_tiles(self) -> List[Any]:
        """Retira únicamente las fichas colocadas durante el turno en curso no consolidadas."""
        tiles_to_return = [t for t in self._current_placed_tiles if not getattr(t, "locked", False)]
        for tile in tiles_to_return:
            if hasattr(tile, "grid_pos") and tile.grid_pos is not None:
                r, c = tile.grid_pos
                self._grid[r][c] = None
                tile.grid_pos = None
        self._current_placed_tiles.clear()
        return tiles_to_return

    def consolidate_current_turn(self, word: Optional[str] = None) -> None:
        """Fija permanentemente las fichas del turno actual y registra la palabra."""
        if word:
            clean_word = word.strip().upper()
            if clean_word not in self._formed_words:
                self._formed_words.append(clean_word)
        for tile in self._current_placed_tiles:
            if hasattr(tile, "locked"):
                tile.locked = True
        self._current_placed_tiles.clear()

    @property
    def formed_words(self) -> List[str]:
        return list(self._formed_words)

    @staticmethod
    def _extract_line_words(line: List[Optional[Any]]) -> Set[str]:
        words: Set[str] = set()
        letters: List[str] = []
        for tile in line:
            if tile is not None and getattr(tile, "locked", False):
                letters.append(getattr(tile, "letter", ""))
            else:
                if len(letters) >= 2:
                    words.add("".join(letters).upper())
                letters = []
        if len(letters) >= 2:
            words.add("".join(letters).upper())
        return words

    def get_all_grid_words(self) -> Set[str]:
        """Escanea la matriz y extrae todas las palabras consolidadas (>= 2 letras)."""
        words: Set[str] = set()
        for row in self._grid:
            words.update(self._extract_line_words(row))
        for c in range(self._cols):
            words.update(self._extract_line_words([self._grid[r][c] for r in range(self._rows)]))
        return words

    def is_word_formed(self, word: str) -> bool:
        """Verifica si una palabra ya ha sido formada y consolidada en el tablero."""
        if not word:
            return False
        clean = word.strip().upper()
        return clean in self._formed_words or clean in self.get_all_grid_words()

    def _scan_span(self, fixed_coord: int, coords: Set[int], is_row: bool) -> str:
        dim = self._cols if is_row else self._rows
        start = min(coords)
        while start > 0 and (self._grid[fixed_coord][start - 1] if is_row else self._grid[start - 1][fixed_coord]) is not None:
            start -= 1
        end = max(coords)
        while end < dim - 1 and (self._grid[fixed_coord][end + 1] if is_row else self._grid[end + 1][fixed_coord]) is not None:
            end += 1
        tiles = [self._grid[fixed_coord][i] if is_row else self._grid[i][fixed_coord] for i in range(start, end + 1)]
        return "".join(getattr(t, "letter", "") for t in tiles) if all(t is not None for t in tiles) else ""

    def _current_positions(self) -> List[Tuple[int, int]]:
        """Coordenadas ocupadas por las fichas colocadas en el turno en curso."""
        return [
            t.grid_pos for t in self._current_placed_tiles
            if hasattr(t, "grid_pos") and t.grid_pos is not None
        ]

    def get_placed_word_text(self) -> str:
        """
        Extrae la palabra que se está formando en el turno actual.

        La lectura es estricta: todas las fichas del turno deben estar alineadas
        en una misma fila o columna y la secuencia no puede tener casillas vacías
        intermedias. Si la colocación no cumple estas condiciones se devuelve una
        cadena vacía, de modo que nunca se validan palabras con huecos.
        """
        positions = self._current_positions()
        if not positions:
            return ""

        rows = {r for r, _ in positions}
        cols = {c for _, c in positions}

        # Las fichas deben compartir fila o columna (nunca ambas dispersas)
        if len(rows) > 1 and len(cols) > 1:
            return ""

        # _scan_span devuelve "" si detecta una casilla vacía dentro del tramo
        h_word = self._scan_span(next(iter(rows)), cols, is_row=True) if len(rows) == 1 else ""
        v_word = self._scan_span(next(iter(cols)), rows, is_row=False) if len(cols) == 1 else ""

        # La palabra leída debe tener al menos 2 letras y contener TODAS las fichas del turno
        minimo = max(2, len(positions))
        candidatas = [w for w in (h_word, v_word) if len(w) >= minimo]
        if not candidatas:
            return ""
        return max(candidatas, key=len)

    def get_placement_issue(self) -> Optional[str]:
        """
        Diagnostica la colocación actual para poder mostrar un mensaje claro al
        jugador. Devuelve None si la jugada es legible, o un código de problema:
        'vacio', 'alineacion', 'una_letra' o 'hueco'.
        """
        positions = self._current_positions()
        if not positions:
            return "vacio"

        rows = {r for r, _ in positions}
        cols = {c for _, c in positions}
        if len(rows) > 1 and len(cols) > 1:
            return "alineacion"

        if self.get_placed_word_text():
            return None

        return "una_letra" if len(positions) == 1 else "hueco"

    def reset(self) -> None:
        """Reinicia el tablero vaciando todas las casillas y el registro de palabras."""
        self._grid = [[None for _ in range(self._cols)] for _ in range(self._rows)]
        self._current_placed_tiles.clear()
        self._formed_words.clear()
        self._direction = "horizontal"
