import json
import random
from pathlib import Path
from typing import List, Optional, Dict, Any, Set, Union

class Tile:
    """Abstracción de una ficha de letra."""
    def __init__(self, letter: str, tile_id: int, value: int = 1):
        self._letter = letter.upper()
        self._id = tile_id
        self._value = value
        self.grid_pos: Optional[tuple] = None

    @property
    def letter(self) -> str: return self._letter
    @property
    def id(self) -> int: return self._id
    @property
    def value(self) -> int: return self._value

    def __repr__(self) -> str:
        return f"Tile(letter='{self._letter}', id={self._id})"


class TileBag:
    """
    Bolsa de fichas con frecuencia controlada y extracción inteligente balanceada
    diseñada para evitar atriles bloqueados y facilitar la estimulación cognitiva.
    """
    VOWELS: Set[str] = set("AEIOU")

    ADAPTED_FREQUENCY: Dict[str, int] = {
        'A': 12, 'E': 12, 'O': 10, 'I': 7, 'U': 5,
        'S': 6, 'L': 5, 'R': 5, 'M': 4, 'P': 4,
        'N': 5, 'T': 4, 'D': 4, 'C': 4, 'B': 3,
        'G': 2, 'F': 2, 'J': 1, 'Z': 1, 'Ñ': 2
    }

    def __init__(self, seed: Optional[int] = None):
        self._tiles: List[str] = []
        self._next_id: int = 1
        if seed is not None:
            random.seed(seed)
        self.reset()

    def reset(self) -> None:
        """Rellena y baraja la bolsa con las frecuencias terapéuticas."""
        self._tiles.clear()
        for letter, count in self.ADAPTED_FREQUENCY.items():
            self._tiles.extend([letter] * count)
        random.shuffle(self._tiles)

    def return_tiles(self, tiles: List[Any]) -> None:
        """Devuelve fichas a la bolsa y vuelve a barajar."""
        for t in tiles:
            letter = getattr(t, 'letter', None) or (str(t) if isinstance(t, str) else "")
            if letter:
                self._tiles.append(letter.upper())
        random.shuffle(self._tiles)

    def draw_specific_letter(self, letter: str) -> Tile:
        """Extrae una letra específica de la bolsa si existe, o genera una ficha con ella."""
        letter_clean = letter.strip().upper()
        if letter_clean in self._tiles:
            self._tiles.remove(letter_clean)
        tile = Tile(letter_clean, self._next_id)
        self._next_id += 1
        return tile

    def _pop_matching_letter(self, is_vowel: bool) -> Optional[str]:
        """Extrae una letra (vocal o consonante) de la bolsa si está disponible."""
        for i in range(len(self._tiles) - 1, -1, -1):
            if (self._tiles[i] in self.VOWELS) == is_vowel:
                return self._tiles.pop(i)
        return None

    def _pop_vowel(self) -> Optional[str]:
        """Extrae una vocal aleatoria de la bolsa si está disponible."""
        return self._pop_matching_letter(is_vowel=True)

    def _pop_consonant(self) -> Optional[str]:
        """Extrae una consonante aleatoria de la bolsa si está disponible."""
        return self._pop_matching_letter(is_vowel=False)

    def draw_tiles(self, count: int) -> List[Tile]:
        """Extrae hasta `count` fichas de la bolsa como objetos Tile."""
        drawn: List[Tile] = []
        for _ in range(count):
            if not self._tiles:
                break
            letter = self._tiles.pop()
            drawn.append(Tile(letter, self._next_id))
            self._next_id += 1
        return drawn

    def draw_balanced_tiles(
        self,
        count: int,
        current_vowels: int = 0,
        current_consonants: int = 0,
        total_target: int = 7
    ) -> List[Tile]:
        """
        Extrae `count` fichas asegurando que el atril resultante mantenga
        un balance armónico de entre 2 y 3 vocales y entre 4 y 5 consonantes.
        """
        drawn: List[Tile] = []
        vowels_count = current_vowels
        consonants_count = current_consonants

        for _ in range(count):
            if not self._tiles:
                break

            letter = None
            # Regla de balance: asegurar al menos 2 o 3 vocales
            if vowels_count < 3 and (consonants_count >= 4 or vowels_count <= consonants_count):
                letter = self._pop_vowel()
            elif consonants_count < 4:
                letter = self._pop_consonant()

            # Si el tipo preferido no está disponible en la bolsa, tomar cualquiera
            if letter is None:
                letter = self._tiles.pop()

            if letter in self.VOWELS:
                vowels_count += 1
            else:
                consonants_count += 1

            drawn.append(Tile(letter, self._next_id))
            self._next_id += 1

        return drawn

    def draw_guaranteed_hand(self, target_word: str, capacity: int = 7) -> List[Tile]:
        """
        Genera una mano completa garantizando que contenga las letras de `target_word`
        y completa las casillas restantes asegurando un balance óptimo de vocales y consonantes.
        """
        drawn: List[Tile] = []
        word_clean = target_word.strip().upper()

        # 1. Extraer letras exactas de la palabra objetivo
        for ch in word_clean[:capacity]:
            drawn.append(self.draw_specific_letter(ch))

        # 2. Completar las restantes hasta 'capacity' con balance vocálico
        vowels = sum(1 for t in drawn if t.letter in self.VOWELS)
        consonants = len(drawn) - vowels
        remaining_needed = max(0, capacity - len(drawn))

        if remaining_needed > 0:
            extra_tiles = self.draw_balanced_tiles(
                count=remaining_needed,
                current_vowels=vowels,
                current_consonants=consonants,
                total_target=capacity
            )
            drawn.extend(extra_tiles)

        # 3. Barajar las fichas para que no aparezcan en orden secuencial en el atril
        random.shuffle(drawn)
        return drawn

    def remaining_count(self) -> int:
        """Cantidad de letras restantes en la bolsa."""
        return len(self._tiles)


class PlayerRack:
    """Encapsula el atril de fichas del jugador y balance vocálico."""
    def __init__(self, capacity: int = 7):
        self._capacity = capacity
        self._tiles: List[Any] = []

    @property
    def capacity(self) -> int: return self._capacity
    @property
    def tiles(self) -> List[Any]: return list(self._tiles)
    @property
    def vowel_count(self) -> int:
        return sum(1 for t in self._tiles if getattr(t, 'letter', '') in TileBag.VOWELS)
    @property
    def consonant_count(self) -> int:
        return len(self._tiles) - self.vowel_count

    def count(self) -> int: return len(self._tiles)
    def needed_count(self) -> int: return max(0, self._capacity - len(self._tiles))

    def add_tile(self, tile: Any) -> bool:
        """Añade una ficha al atril si hay espacio disponible."""
        if len(self._tiles) >= self._capacity:
            return False
        self._tiles.append(tile)
        return True

    def add_tiles(self, tiles: List[Any]) -> int:
        """Añade una lista de fichas hasta agotar capacidad."""
        added = 0
        for tile in tiles:
            if not self.add_tile(tile):
                break
            added += 1
        return added

    def remove_tile(self, tile: Any) -> bool:
        """Retira una ficha específica del atril por identidad, id o letra."""
        if tile in self._tiles:
            self._tiles.remove(tile)
            return True
        t_id = getattr(tile, 'id', None)
        t_let = getattr(tile, 'letter', None)
        for t in self._tiles:
            if (t_id is not None and getattr(t, 'id', None) == t_id) or (t_let and getattr(t, 'letter', '') == t_let):
                self._tiles.remove(t)
                return True
        return False

    def clear(self) -> List[Any]:
        """Limpia el atril devolviendo todas sus fichas."""
        cleared = list(self._tiles)
        self._tiles.clear()
        return cleared


class PlayerStats:
    """Gestiona la puntuación y el progreso de la sesión sin penalizaciones."""
    def __init__(self):
        self._score: int = 0
        self._words_formed: int = 0
        self._formed_words: List[str] = []

    @property
    def score(self) -> int: return self._score
    @property
    def words_formed(self) -> int: return self._words_formed
    @property
    def formed_words(self) -> List[str]: return list(self._formed_words)

    def is_word_formed(self, word: str) -> bool:
        return bool(word and word.strip().upper() in self._formed_words)

    def add_word_points(self, word: str) -> int:
        clean = word.strip().upper()
        if clean not in self._formed_words:
            self._formed_words.append(clean)
        pts = len(clean) * 10
        self._score += pts
        self._words_formed += 1
        return pts

    def reset(self) -> None:
        self._score, self._words_formed = 0, 0
        self._formed_words.clear()


class HighScoreManager:
    """Guarda y consulta la puntuación más alta por categoría con JSON persistente."""
    def __init__(self, filepath: Union[str, Path]):
        self._filepath: Path = Path(filepath)
        self._scores: Dict[str, int] = {}
        self._load()

    def _load(self) -> None:
        try:
            if self._filepath.exists():
                with open(self._filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self._scores = {str(k).lower(): int(v) for k, v in data.items() if isinstance(v, (int, float))}
        except Exception as err:
            print(f"[SCORES] Advertencia al leer {self._filepath}: {err}")
            self._scores = {}

    def get_score(self, category_key: str) -> int:
        return self._scores.get(str(category_key).strip().lower(), 0)

    def update(self, category_key: str, score: int) -> bool:
        key = str(category_key).strip().lower()
        if score <= self.get_score(key):
            return False
        self._scores[key] = score
        self._save()
        return True

    def reset_all(self) -> None:
        """Reinicia a 0 todas las puntuaciones máximas registradas."""
        self._scores = {k: 0 for k in self._scores}
        self._save()

    def _save(self) -> None:
        try:
            self._filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(self._scores, f, indent=4, ensure_ascii=False)
        except Exception as err:
            print(f"[SCORES] Error al guardar {self._filepath}: {err}")
