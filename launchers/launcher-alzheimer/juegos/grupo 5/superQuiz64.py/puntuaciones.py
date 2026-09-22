import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class GestorPuntuaciones:
    """Clase encargada de gestionar el historial de las últimas partidas en formato JSON."""

    def __init__(self, nombre_archivo="puntuaciones.json", limite_historial=10):
        self.ruta_archivo = BASE_DIR / nombre_archivo
        self.limite_historial = limite_historial
        self.historial = self.cargar_puntuaciones()

    def cargar_puntuaciones(self):
        """Carga el historial registrado desde el archivo JSON."""
        if not self.ruta_archivo.exists():
            return []

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos if isinstance(datos, list) else []
        except Exception as e:
            print(f"Error al leer las puntuaciones: {e}")
            return []

    def guardar_puntuacion(self, modo, aciertos, total):
        """Registra una nueva partida en el historial (máximo 10, eliminando la más antigua)."""
        precision = round((aciertos / total) * 100, 1) if total > 0 else 0.0

        nueva_partida = {
            "modo": modo.capitalize(),
            "aciertos": aciertos,
            "total": total,
            "precision": precision
        }

        self.historial.insert(0, nueva_partida)

        if len(self.historial) > self.limite_historial:
            self.historial = self.historial[:self.limite_historial]

        try:
            with open(self.ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(self.historial, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error al guardar la puntuación: {e}")

    def obtener_mejores(self):
        """Retorna la lista del historial de partidas (últimas 10)."""
        return self.historial