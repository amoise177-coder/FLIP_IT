import os
import sys
import subprocess

class Launcher:
    """
    Gestor de ejecución del Launcher (Alta cohesión y abstracción).
    Se encarga de escanear juegos instalados, verificar archivos ejecutables
    y lanzar subprocesos de juegos de forma segura sin congelar el launcher.
    """
    def __init__(self, carpeta_juegos=None):
        if carpeta_juegos is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.carpeta_juegos = os.path.join(base_dir, "juegos")
        else:
            self.carpeta_juegos = carpeta_juegos

        os.makedirs(self.carpeta_juegos, exist_ok=True)
        self.proceso_activo = None

        # Mapeo explícito: clave_juego → ruta relativa dentro de carpeta_juegos
        self.rutas_custom = {
            "quien_es_quien": os.path.join(
                "Grupo-1",
                "Juego-quien-es-quien-Grupo-1-Taller-master",
                "main.py"
            ),
            "animal_genius": os.path.join(
                "Grupo-2",
                "Grupo-2-Animal-Genius-main",
                "main.py"
            ),
            "el_baul_del_saber": os.path.join(
                "grupo 3",
                "ElBaulDelSaber-main",
                "main.py"
            ),
            "mente_activa": os.path.join(
                "grupo 4",
                "MenteActiva-Memoria_Sensorial_grupo_4-main",
                "main.py"
            ),
            "remember_me": os.path.join(
                "grupo 7",
                "remember-me-main",
                "main.py"
            ),
            "letra_a_letra": os.path.join(
                "grupo9",
                "Letra a letra",
                "main.py"
            ),
            "encuentra_al_intruso": os.path.join(
                "grupo 10",
                "prueba-practica-main",
                "main.py"
            ),
            "ball_sort": os.path.join(
                "grupo 11",
                "BallSort",
                "BallSort",
                "Main.py"
            ),
            "super_quiz_64": os.path.join(
                "grupo 5",
                "superQuiz64.py",
                "main.py"
            ),
            "memory_grupo_8": os.path.join(
                "grupo 8",
                "tallergrupo8-main",
                "main.py"
            ),
            "bingo_calma": os.path.join(
                "grupo 6",
                "Proyecto taller de abstraccion eugenio",
                "main.py"
            ),
        }

    def resolver_ruta_juego(self, nombre_juego):
        """
        Busca el archivo principal del juego (.py o .exe) en la carpeta de juegos
        o en subcarpetas de los grupos.
        """
        # 0. Ruta explícita registrada en rutas_custom
        if nombre_juego in self.rutas_custom:
            ruta_custom = os.path.join(self.carpeta_juegos, self.rutas_custom[nombre_juego])
            if os.path.exists(ruta_custom):
                return ruta_custom

        # 1. Búsqueda directa en 'juegos/'
        candidatos = [
            os.path.join(self.carpeta_juegos, f"{nombre_juego}.exe"),
            os.path.join(self.carpeta_juegos, f"{nombre_juego}.py"),
            os.path.join(self.carpeta_juegos, nombre_juego, f"{nombre_juego}.exe"),
            os.path.join(self.carpeta_juegos, nombre_juego, "main.exe"),
            os.path.join(self.carpeta_juegos, nombre_juego, "main.py"),
            os.path.join(self.carpeta_juegos, nombre_juego, f"{nombre_juego}.py"),
        ]

        for ruta in candidatos:
            if os.path.exists(ruta):
                return ruta

        # 2. Búsqueda profunda en subcarpetas de grupos (grupo*, Grupo*)
        for root, dirs, files in os.walk(self.carpeta_juegos):
            files_map = {f.lower(): f for f in files}
            if "main.py" in files_map:
                rel = os.path.relpath(root, self.carpeta_juegos)
                parts = [p.lower().replace("-", "").replace("_", "").replace(" ", "") for p in rel.split(os.sep)]
                clean_target = nombre_juego.lower().replace("-", "").replace("_", "").replace(" ", "")
                if any(clean_target in p or p in clean_target for p in parts):
                    return os.path.join(root, files_map["main.py"])

        # 3. En carpetas superiores si existieran
        base_superior = os.path.abspath(os.path.join(self.carpeta_juegos, "..", ".."))
        candidatos_sup = [
            os.path.join(base_superior, nombre_juego, "main.py"),
            os.path.join(base_superior, f"{nombre_juego}.exe"),
            os.path.join(base_superior, f"proyecto {nombre_juego}", "main.py"),
            os.path.join(base_superior, f"proyecto_{nombre_juego}", "main.py"),
        ]
        for ruta in candidatos_sup:
            if os.path.exists(ruta):
                return ruta

        return None

    def lanzar_juego(self, clave_juego, nombre_visible="Juego"):
        """
        Ejecuta el juego como subproceso (soporta .exe nativo de Windows o scripts .py).
        Configura PYTHONPATH y el directorio de trabajo para garantizar máxima compatibilidad.
        """
        ruta = self.resolver_ruta_juego(clave_juego)
        if not ruta:
            return False, f"'{nombre_visible}' aún no está instalado en la carpeta 'juegos/'."

        try:
            carpeta_trabajo = os.path.dirname(ruta)
            
            # Si es un .exe se ejecuta directamente en Windows
            if ruta.lower().endswith(".exe"):
                comando = [ruta]
            else:
                # Si es un script .py se ejecuta con Python
                comando = [sys.executable, ruta]

            # Inyectar el directorio del juego en PYTHONPATH para resolver dependencias locales
            env = os.environ.copy()
            env["PYTHONPATH"] = carpeta_trabajo + (os.pathsep + env["PYTHONPATH"] if "PYTHONPATH" in env else "")

            self.proceso_activo = subprocess.Popen(
                comando,
                cwd=carpeta_trabajo,
                env=env
            )
            return True, f"Iniciando {nombre_visible}..."
        except Exception as e:
            return False, f"Error al ejecutar {nombre_visible}: {e}"

    def juego_en_ejecucion(self):
        """Verifica si el subproceso del juego sigue activo."""
        if self.proceso_activo is not None:
            return self.proceso_activo.poll() is None
        return False
