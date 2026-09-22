import os
import json


class GameScanner:
    """Explora la carpeta de juegos y construye un catálogo con sus metadatos."""

    @staticmethod
    def scan_and_load_metadata(base_path: str):
        """
        Escanea el directorio de juegos, detecta proyectos que contienen un main.py
        y convierte su metadata.json en un diccionario listo para mostrar en el menú.
        """
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        catalog = []

        for folder in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder)

            # Un juego se considera válido si existe como carpeta y contiene un archivo main.py.
            if os.path.isdir(folder_path) and "main.py" in os.listdir(folder_path):
                json_path = os.path.join(folder_path, "metadata.json")

                metadata = {
                    "folder": folder,
                    "folder_path": folder_path,
                    "title": folder.replace("_", " "),
                    "description": "No se encontró descripción en metadata.json",
                    "authors": ["Desconocido"],
                    "group_number": "Desconocido",
                    "controls": "No fueron especificados los controles en metadata.json",
                }

                if os.path.exists(json_path):
                    try:
                        with open(json_path, "r", encoding="utf-8") as f:
                            group_data = json.load(f)
                            metadata.update(group_data)
                    except Exception as e:
                        print(f"Error al leer el archivo metadata.json en la carpeta '{folder}': {e}")

                folder_parts = folder.split('_')
                if len(folder_parts) >= 2 and folder_parts[0].capitalize() in ["Lunes", "Jueves"]:
                    metadata["group_number"] = f"{folder_parts[0].capitalize()} {folder_parts[1]}"

                catalog.append(metadata)

        def sort_key(game_meta):
            val = game_meta.get("group_number")
            # 1. Si es entero en metadata.json
            if isinstance(val, int):
                return (val, game_meta.get("title", ""))
            
            # 2. Si es texto (ej: "1" o "Grupo 1"), extraer los dígitos
            if isinstance(val, str):
                import re
                match = re.search(r'\d+', val)
                if match:
                    return (int(match.group()), game_meta.get("title", ""))
            
            # 3. Fallback: buscar número en el nombre de la carpeta (ej: "grupo1", "GRUPO-5")
            import re
            folder_name = game_meta.get("folder", "")
            match = re.search(r'(?:grupo|group)?[-_]?(\d+)', folder_name, re.IGNORECASE)
            if match:
                return (int(match.group(1)), game_meta.get("title", ""))

            return (999, game_meta.get("title", ""))

        catalog.sort(key=sort_key)

        return catalog