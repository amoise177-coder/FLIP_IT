"""
MenteActiva — Game Manager
Orquestador principal que integra Tablero, GestorSensorial y SistemaDePistas.
Controla el flujo completo del juego: previsualización, selección, evaluación y victoria.
"""
import random
from enum import Enum
import pygame

from config import (
    DifficultyLevel, DIFFICULTY_CONFIGS,
    FAIL_DISPLAY_TIME, MATCH_DISPLAY_TIME,
    POSITIVE_MESSAGES, ENCOURAGEMENT_MESSAGES,
    MESSAGE_DISPLAY_TIME,
)
from core.tablero import Tablero
from core.gestor_sensorial import GestorSensorial
from core.sistema_pistas import SistemaDePistas, NivelPista


class GameState(Enum):
    """Estados del flujo de juego."""
    PREVIEW = "preview"                 # Mostrando todas las cartas brevemente
    WAITING_FIRST = "waiting_first"     # Esperando primera selección
    WAITING_SECOND = "waiting_second"   # Esperando segunda selección
    CHECKING = "checking"              # Evaluando coincidencia
    SHOWING_MATCH = "showing_match"    # Mostrando acierto
    SHOWING_FAIL = "showing_fail"      # Mostrando fallo (1.8s)
    VICTORY = "victory"                # Todas las parejas encontradas


class GameManager:
    """
    Orquestador principal del juego de memoria.

    Integra los tres componentes centrales (Tablero, GestorSensorial,
    SistemaDePistas) y gestiona la máquina de estados del juego.

    El sistema de pistas siempre está activo e infinito.

    Args:
        dificultad (DifficultyLevel): Nivel de dificultad seleccionado.
        tema (str): Clave del tema visual.
        gestor_sensorial (GestorSensorial): Gestor de sonidos compartido.
    """

    def __init__(self, dificultad, tema, gestor_sensorial):
        self._dificultad = dificultad
        self._tema = tema
        self._config = DIFFICULTY_CONFIGS[dificultad]

        # ── Componentes del juego ──
        self._tablero = Tablero(
            self._config.rows,
            self._config.cols,
            self._config.num_pairs,
            tema
        )
        self._gestor = gestor_sensorial
        self._sistema_pistas = SistemaDePistas()

        # ── Estado del juego ──
        self._estado = GameState.PREVIEW
        self._timer = self._config.preview_time

        # ── Estadísticas ──
        self._intentos = 0
        self._aciertos = 0
        self._fallos = 0

        # ── Mensajes de retroalimentación ──
        self._mensaje = ""
        self._mensaje_timer = 0.0
        self._mensaje_color = (120, 200, 140)

        # ── Pausa ──
        self._pausado = False

        # ── Control de pista automática ──
        self._pista_aplicada = False

        # Iniciar previsualización
        self._tablero.mostrar_todas()

    # ── Propiedades ──────────────────────────────────────────────────────

    @property
    def estado(self):
        return self._estado

    @property
    def tablero(self):
        return self._tablero

    @property
    def dificultad(self):
        return self._dificultad

    @property
    def config(self):
        return self._config

    @property
    def intentos(self):
        return self._intentos

    @property
    def aciertos(self):
        return self._aciertos

    @property
    def fallos(self):
        return self._fallos

    @property
    def mensaje(self):
        return self._mensaje

    @property
    def mensaje_timer(self):
        return self._mensaje_timer

    @property
    def mensaje_color(self):
        return self._mensaje_color

    @property
    def pausado(self):
        return self._pausado

    @property
    def parejas_encontradas(self):
        return self._tablero.obtener_parejas_encontradas()

    @property
    def total_parejas(self):
        return self._config.num_pairs

    @property
    def sistema_pistas(self):
        return self._sistema_pistas

    @property
    def es_victoria(self):
        return self._estado == GameState.VICTORY

    # ── Control de pausa ─────────────────────────────────────────────────

    def pausar(self):
        self._pausado = True

    def reanudar(self):
        self._pausado = False

    def toggle_pausa(self):
        self._pausado = not self._pausado

    # ── Manejo de eventos ────────────────────────────────────────────────

    def manejar_evento(self, event):
        """
        Procesa un evento de pygame.
        Retorna una acción si es necesario (ej: "victoria", "menu").
        """
        if self._pausado:
            return None

        if self._estado == GameState.VICTORY:
            return None

        if self._estado == GameState.PREVIEW:
            # Permitir saltar previsualización con clic o tecla
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                self._terminar_preview()
            return None

        # ── Clic del mouse ──
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._estado in (GameState.WAITING_FIRST, GameState.WAITING_SECOND):
                carta = self._tablero.obtener_carta_en(event.pos)
                if carta:
                    self._intentar_seleccion(carta)

        # ── Controles de teclado ──
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._tablero.mover_cursor(-1, 0)
                self._tablero.activar_cursor()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._tablero.mover_cursor(1, 0)
                self._tablero.activar_cursor()
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._tablero.mover_cursor(0, -1)
                self._tablero.activar_cursor()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._tablero.mover_cursor(0, 1)
                self._tablero.activar_cursor()
            elif event.key == pygame.K_SPACE:
                # Seleccionar carta bajo el cursor
                carta = self._tablero.obtener_carta_cursor()
                if carta:
                    self._intentar_seleccion(carta)

        return None

    def _intentar_seleccion(self, carta):
        """Intenta seleccionar una carta."""
        if self._estado == GameState.WAITING_FIRST:
            resultado = self._tablero.seleccionar_carta(carta)
            if resultado == "primera":
                self._gestor.reproducir_volteo()
                self._estado = GameState.WAITING_SECOND
                # Registrar que esta carta ha sido vista
                self._sistema_pistas.registrar_carta_vista(carta.pair_id)

        elif self._estado == GameState.WAITING_SECOND:
            resultado = self._tablero.seleccionar_carta(carta)
            if resultado == "segunda":
                self._gestor.reproducir_volteo()
                self._estado = GameState.CHECKING
                self._timer = 0.5  # Breve pausa para ver la segunda carta
                # Registrar vista
                self._sistema_pistas.registrar_carta_vista(carta.pair_id)
                self._intentos += 1

    def _terminar_preview(self):
        """Finaliza la previsualización y comienza el juego."""
        self._tablero.ocultar_todas()
        self._estado = GameState.WAITING_FIRST
        self._timer = 0.0

    # ── Actualización ────────────────────────────────────────────────────

    def actualizar(self, dt):
        """
        Actualiza la lógica del juego.
        Retorna "victoria" si se completó el juego, None en caso contrario.
        """
        if self._pausado:
            return None

        # Actualizar tablero (animaciones)
        self._tablero.actualizar(dt)

        # Actualizar sistema de pistas
        self._sistema_pistas.actualizar(dt)

        # Actualizar mensaje temporal
        if self._mensaje_timer > 0:
            self._mensaje_timer -= dt
            if self._mensaje_timer <= 0:
                self._mensaje = ""

        # ── Máquina de estados ──
        if self._estado == GameState.PREVIEW:
            self._timer -= dt
            if self._timer <= 0:
                self._terminar_preview()

        elif self._estado == GameState.CHECKING:
            # Esperar a que terminen las animaciones de volteo
            if not self._tablero.hay_animacion_activa():
                self._timer -= dt
                if self._timer <= 0:
                    self._evaluar_resultado()

        elif self._estado == GameState.SHOWING_MATCH:
            self._timer -= dt
            if self._timer <= 0:
                self._tablero.limpiar_seleccion()
                if self._tablero.esta_completo():
                    self._estado = GameState.VICTORY
                    self._gestor.reproducir_victoria()
                    return "victoria"
                else:
                    self._estado = GameState.WAITING_FIRST
                    # Aplicar pistas visuales si hay alguna activa
                    if self._sistema_pistas.tiene_pista_activa:
                        self._sistema_pistas.aplicar_pistas_visuales(
                            self._tablero, self._gestor
                        )

        elif self._estado == GameState.SHOWING_FAIL:
            self._timer -= dt
            if self._timer <= 0:
                # Voltear las cartas de regreso
                self._tablero.confirmar_fallo()
                self._estado = GameState.WAITING_FIRST
                self._pista_aplicada = False
                # Aplicar pistas después del fallo
                if self._sistema_pistas.tiene_pista_activa:
                    self._sistema_pistas.aplicar_pistas_visuales(
                        self._tablero, self._gestor
                    )

        return None

    def _evaluar_resultado(self):
        """Evalúa si las dos cartas seleccionadas son pareja."""
        coincide = self._tablero.evaluar_coincidencia()

        if coincide is None:
            return

        if coincide:
            # ¡Acierto!
            self._aciertos += 1
            pair_id = self._tablero.primera_seleccion.pair_id
            self._tablero.confirmar_acierto()
            self._gestor.reproducir_acierto()
            self._sistema_pistas.registrar_acierto(pair_id)
            self._mostrar_mensaje(random.choice(POSITIVE_MESSAGES), (120, 200, 140))
            self._estado = GameState.SHOWING_MATCH
            self._timer = MATCH_DISPLAY_TIME
        else:
            # Fallo
            self._fallos += 1
            pair_id_1 = self._tablero.primera_seleccion.pair_id
            pair_id_2 = self._tablero.segunda_seleccion.pair_id
            self._gestor.reproducir_fallo()
            self._sistema_pistas.registrar_fallo(pair_id_1, pair_id_2)
            self._mostrar_mensaje(random.choice(ENCOURAGEMENT_MESSAGES), (232, 144, 126))
            self._estado = GameState.SHOWING_FAIL
            self._timer = FAIL_DISPLAY_TIME

            # Aplicar pistas si se activaron
            if self._sistema_pistas.tiene_pista_activa and not self._pista_aplicada:
                self._pista_aplicada = True
                self._sistema_pistas.aplicar_pistas_visuales(
                    self._tablero, self._gestor
                )

    def _mostrar_mensaje(self, texto, color):
        """Muestra un mensaje temporal de retroalimentación."""
        self._mensaje = texto
        self._mensaje_timer = MESSAGE_DISPLAY_TIME
        self._mensaje_color = color

    # ── Reinicio ─────────────────────────────────────────────────────────

    def reiniciar(self):
        """Reinicia la partida manteniendo la configuración actual."""
        self._tablero.reiniciar()
        self._sistema_pistas.reiniciar()
        self._estado = GameState.PREVIEW
        self._timer = self._config.preview_time
        self._intentos = 0
        self._aciertos = 0
        self._fallos = 0
        self._mensaje = ""
        self._mensaje_timer = 0.0
        self._pausado = False
        self._pista_aplicada = False
        self._tablero.mostrar_todas()

    # ── Dibujar ──────────────────────────────────────────────────────────

    def dibujar(self, surface):
        """Dibuja el tablero y los efectos del juego."""
        self._tablero.dibujar(surface)
