from pathlib import Path
import json
import random
import unicodedata
from collections import Counter
from typing import Set, List, Dict, Optional, Union


def _normalizar_palabra(texto: str) -> str:
    """Quita tildes de las vocales, pero conserva la Ñ como letra propia."""
    texto = texto.strip().upper()
    texto = texto.replace("Ñ", "@@N_ENIE@@")
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
    return texto.replace("@@N_ENIE@@", "Ñ")


class DictionaryChecker:
    """
    Gestiona el diccionario curado de palabras cotidianas en español
    organizadas por categorías semánticas y ofrece algoritmos de asistencia cognitiva.
    """

    # Categorías terapéuticas por defecto en memoria (respaldo absoluto autónomo)
    FALLBACK_CATEGORIES: Dict[str, List[str]] = {
        "naturaleza": [
            "ARBOL", "FLOR", "MAR", "LUNA", "SOL", "RIO", "NUBE", "CIELO", "LAGO", "CAMPO", "JARDIN", "ROSA"
        ],
        "objetos": [
            "MESA", "SILLA", "LIBRO", "PLATO", "VASO", "RELOJ", "PUERTA", "VENTANA", "CARTA", "SOPA",
            "AUTO", "TREN", "ROPA", "ZAPATO", "CAMISA", "PELOTA"
        ],
        "frutas_alimentos": [
            "PAN", "AGUA", "CAFE", "LECHE", "FRUTA", "TARTA", "MANZANA", "PERA", "PLATANO", "FRESA",
            "LIMON", "NARANJA", "UVA"
        ],
        "familia_hogar": [
            "AMOR", "CASA", "VIDA", "PAPA", "MAMA", "HIJO", "HIJA", "NINO", "ABUELO", "ABUELA",
            "TIO", "TIA", "HERMANO", "AMIGO", "PAZ", "SALUD", "SONRISA"
        ],
        "animales": [
            "GATO", "PERRO", "RANA", "PATO", "LOBO", "OSO", "LEON", "PEZ", "AVE"
        ],
        "cuerpo_humano": [
            "OJO", "MANO", "PIE", "BOCA", "NARIZ", "BRAZO", "CARA", "PELO"
        ]
    }

    # Conjunto aplanado de todas las palabras fallback para compatibilidad retroactiva
    FALLBACK_WORDS: Set[str] = {
        word for words in FALLBACK_CATEGORIES.values() for word in words
    }

    def __init__(self, filepath: Optional[Union[str, Path]] = None):
        self._filepath: Optional[Path] = Path(filepath) if filepath else None
        self._categories: Dict[str, List[str]] = {}
        self._category_sets: Dict[str, Set[str]] = {}
        self._words: Set[str] = set()
        self._active_category: Optional[str] = None
        self._load_dictionary()

    @classmethod
    def ensure_dictionary_file(cls, filepath: Path) -> None:
        """
        Verifica y genera el archivo JSON de categorías curadas en disco si no existe,
        creando las carpetas intermedias necesarias con pathlib.
        """
        if not filepath.exists():
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(cls.FALLBACK_CATEGORIES, f, indent=4, ensure_ascii=False)
                print(f"[ENTORNO] Archivo de categorías '{filepath.name}' generado en {filepath.parent.name}.")
            except Exception as err:
                print(f"[ERROR] No se pudo crear {filepath}: {err}")

    def _load_dictionary(self) -> None:
        """
        Carga el vocabulario desde un archivo JSON estructurado (por categorías o lista plana).
        Si el archivo no existe o ocurre un error, utiliza el respaldo en memoria.
        """
        if self._filepath and self._filepath.exists():
            try:
                with open(self._filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, dict):
                    # Formato por categorías: {"Naturaleza": [...], "Objetos": [...]}
                    self._categories = {
                        cat: [_normalizar_palabra(w) for w in words if isinstance(w, str)]
                        for cat, words in data.items()
                        if isinstance(words, list)
                    }
                    self._category_sets = {cat: set(words) for cat, words in self._categories.items()}
                    self._words = {w for words in self._categories.values() for w in words}
                    return
                elif isinstance(data, list):
                    # Compatibilidad con formato de lista plana
                    words_clean = [_normalizar_palabra(w) for w in data if isinstance(w, str)]
                    self._words = set(words_clean)
                    self._categories = {"General": words_clean}
                    self._category_sets = {"General": set(words_clean)}
                    return
            except Exception as e:
                print(f"[WARN] Error al cargar {self._filepath}: {e}. Usando categorías por defecto.")

        # Respaldo en memoria por defecto
        self._categories = {cat: list(words) for cat, words in self.FALLBACK_CATEGORIES.items()}
        self._category_sets = {cat: set(words) for cat, words in self._categories.items()}
        self._words = set(self.FALLBACK_WORDS)

    @property
    def total_words(self) -> int:
        """Cantidad total de palabras disponibles en todas las categorías."""
        return len(self._words)

    @property
    def categories(self) -> List[str]:
        """Lista de nombres de categorías disponibles."""
        return list(self._categories.keys())

    @property
    def active_category(self) -> Optional[str]:
        """Categoría actualmente activa para asistencia de pistas."""
        return self._active_category

    def set_active_category(self, category: Optional[str]) -> bool:
        """
        Define la categoría activa. Si es None, busca en todas las categorías.
        Retorna True si la categoría es válida o None.
        """
        if category is None:
            self._active_category = None
            return True

        if category in self._categories:
            self._active_category = category
            return True

        # Búsqueda tolerante (mayúsculas/minúsculas y espacios) para que la
        # selección siga funcionando aunque las claves del JSON difieran.
        clave = str(category).strip().lower()
        for nombre in self._categories:
            if nombre.strip().lower() == clave:
                self._active_category = nombre
                return True

        print(f"[DICCIONARIO] Categoría '{category}' no encontrada. Se usará el vocabulario completo.")
        self._active_category = None
        return False

    def get_words_for_category(self, category: Optional[str]) -> List[str]:
        """Retorna las palabras asociadas a una categoría específica con búsqueda tolerante."""
        if not category:
            return []
        if category in self._categories:
            return list(self._categories[category])
        clave = str(category).strip().lower()
        for nombre, words in self._categories.items():
            if nombre.strip().lower() == clave:
                return list(words)
        return []

    def get_random_target_word(
        self,
        category: Optional[str] = None,
        min_len: int = 3,
        max_len: int = 5,
        excluded_words: Optional[Union[Set[str], List[str]]] = None
    ) -> str:
        """
        Selecciona una palabra cotidiana adecuada de la categoría indicada (o activa)
        con una longitud acotada para estimulación cognitiva óptima,
        evitando repetir palabras que ya fueron formadas en el tablero.
        """
        cat = category or self._active_category
        words = self.get_words_for_category(cat) if cat else list(self._words)

        excluded_set = {_normalizar_palabra(w) for w in excluded_words} if excluded_words else set()
        available_words = [w for w in words if _normalizar_palabra(w) not in excluded_set]
        # Si ya se formaron todas las palabras de la categoría, permitir las restantes
        if not available_words:
            available_words = words

        suitable = [w for w in available_words if min_len <= len(w) <= max_len]
        if not suitable:
            suitable = available_words if available_words else ["SOL", "LUNA", "PAN", "MESA", "CASA"]
        return random.choice(suitable)

    def is_valid_word(self, word: str, category: Optional[str] = None) -> bool:
        """Verifica si la palabra existe en la categoría activa (o en todo el diccionario si es Modo Completo)."""
        if not word:
            return False
        norm = _normalizar_palabra(word)
        cat = category if category is not None else self._active_category
        if cat:
            cat_set = self._category_sets.get(cat)
            if cat_set is None:
                clave = str(cat).strip().lower()
                for nombre, words_set in self._category_sets.items():
                    if nombre.strip().lower() == clave:
                        cat_set = words_set
                        break
            return norm in cat_set if cat_set else False
        return norm in self._words

    def find_possible_words(
        self,
        letters: List[str],
        category: Optional[str] = None,
        excluded_words: Optional[Union[Set[str], List[str]]] = None
    ) -> List[str]:
        """
        Encuentra todas las palabras que se pueden formar con las letras provistas,
        excluyendo palabras que ya fueron consolidadas en el tablero.
        Permite filtrar por categoría activa o buscar en el vocabulario general.
        Ordenadas de mayor a menor longitud para ofrecer mejores estímulos cognitivos.
        """
        clean_letters = [_normalizar_palabra(char) for char in letters if isinstance(char, str)]
        available_counts = Counter(clean_letters)
        possible = []

        cat = category or self._active_category
        target_words = self._categories.get(cat, self._words) if cat else self._words
        excluded_set = {_normalizar_palabra(w) for w in excluded_words} if excluded_words else set()

        for word in target_words:
            if _normalizar_palabra(word) in excluded_set:
                continue
            word_counts = Counter(word)
            if all(word_counts[char] <= available_counts[char] for char in word):
                possible.append(word)

        # Ordenar por longitud descendente y luego alfabéticamente
        possible.sort(key=lambda w: (-len(w), w))
        return possible

    def get_therapeutic_hint(
        self,
        current_letters: List[str],
        category: Optional[str] = None,
        excluded_words: Optional[Union[Set[str], List[str]]] = None
    ) -> str:
        """
        Genera una sugerencia amigable contextualizada con la categoría activa
        sin dar la respuesta completa de inmediato y evitando sugerir palabras ya formadas.
        Si no hay palabras directas con las letras actuales, analiza la palabra más cercana
        del tema y orienta constructivamente al usuario a pulsar 'RENOVAR ATRIL'.
        """
        target_cat = category or self._active_category
        candidates = self.find_possible_words(current_letters, category=target_cat, excluded_words=excluded_words)

        # 2. Si hay palabras que se pueden formar
        if candidates:
            target = candidates[0]
            return f"Puedes formar '{target[0]}...' ({len(target)} letras)"

        # 3. No hay palabras posibles con las letras actuales: encontrar la palabra más cercana
        cat_words = self.get_words_for_category(target_cat) if target_cat else list(self._words)
        excluded_set = {_normalizar_palabra(w) for w in excluded_words} if excluded_words else set()
        available_targets = [w for w in cat_words if w.upper() not in excluded_set]

        if not available_targets:
            return "¡Tema completado! Elige una nueva categoría."

        clean_letters = [ch.upper() for ch in current_letters if isinstance(ch, str)]
        available_counts = Counter(clean_letters)

        best_word = None
        min_missing = 999
        missing_letters = []

        for word in available_targets:
            word_upper = word.upper()
            word_counts = Counter(word_upper)
            diff_letters = []
            for ch, count in word_counts.items():
                needed = count - available_counts.get(ch, 0)
                if needed > 0:
                    diff_letters.extend([ch] * needed)
            if len(diff_letters) < min_missing:
                min_missing = len(diff_letters)
                best_word = word_upper
                missing_letters = diff_letters

        if best_word and min_missing == 1:
            miss_char = missing_letters[0]
            return f"Falta letra '{miss_char}' para '{best_word}'. ¡Pulsa 'RENOVAR ATRIL'!"

        elif best_word and min_missing == 2:
            return f"Busca '{best_word}'. ¡Pulsa 'RENOVAR ATRIL' para nuevas letras!"

        else:
            return "Sin palabras con estas fichas. ¡Pulsa 'RENOVAR ATRIL' para nuevas letras!"
