import difflib

class Categoria:
    """Gestiona una categoría de palabras, sus letras habilitadas y la lógica de validación."""
    def __init__(self, nombre: str, palabras_validas: list[str], letras_excluidas: list[str]):
        self._nombre = nombre
        self._palabras_validas = palabras_validas
        self._letras_excluidas = set(letras_excluidas)
        self._alfabeto = [chr(i) for i in range(65, 91)]
        self._alfabeto.insert(14, "Ñ")
        # True = letra activa/pendiente, False = letra completada
        self._estado_letras = {letra: True for letra in self._alfabeto}

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def palabras_validas(self) -> list[str]:
        return self._palabras_validas

    @property
    def letras_excluidas(self) -> set[str]:
        return self._letras_excluidas

    def esta_activa(self, letra: str) -> bool:
        """Retorna True si la letra aún no ha sido completada."""
        return self._estado_letras.get(letra.upper(), True)

    def marcar_completada(self, letra: str) -> None:
        """Marca una letra como completada."""
        self._estado_letras[letra.upper()] = False

    def obtener_letras_disponibles(self) -> list[str]:
        """Retorna las letras del abecedario permitidas en esta categoría."""
        return [letra for letra in self._alfabeto if letra not in self._letras_excluidas]

    def validar_palabra(self, palabra_ingresada: str, letra_inicial: str) -> tuple[bool, str]:
        """Valida ortográficamente la palabra escrita contra el banco de palabras."""
        if not palabra_ingresada or palabra_ingresada[0].upper() != letra_inicial.upper():
            return False, "intentalo_de_nuevo"

        palabra_upper = palabra_ingresada.upper().strip()
        palabras_con_letra = [p.upper() for p in self._palabras_validas if p.upper().startswith(letra_inicial.upper())]
        if palabra_upper in palabras_con_letra:
            return True, "correcto"
        return False, "intentalo_de_nuevo"

    def es_palabra_cercana(self, palabra_ingresada: str, letra_inicial: str) -> bool:
        """Verifica si la palabra escrita está verdaderamente cerca de una palabra válida con esa letra inicial."""
        if not palabra_ingresada or palabra_ingresada[0].upper() != letra_inicial.upper():
            return False

        palabra_upper = palabra_ingresada.upper().strip()
        palabras_con_letra = [p.upper() for p in self._palabras_validas if p.upper().startswith(letra_inicial.upper())]
        if not palabras_con_letra:
            return False

        # cutoff de 0.75 y diferencia de longitud máxima de 2 caracteres
        coincidencias = difflib.get_close_matches(palabra_upper, palabras_con_letra, n=1, cutoff=0.75)
        if not coincidencias:
            return False

        mejor_match = coincidencias[0]
        if abs(len(palabra_upper) - len(mejor_match)) > 2:
            return False

        return True
