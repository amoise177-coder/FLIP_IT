"""
MenteActiva — Sistema de Pistas Adaptativo
Máquina de estados que monitorea los fallos consecutivos del jugador
y activa pistas sensoriales escalonadas de forma automática.

Ciclo de pistas por par:
    2 fallos → Borde dorado pulsante
    3 fallos → Pista auditiva (nota musical)
    4 fallos → Revelación temporal de ambas cartas con borde dorado

Al encontrar una pareja (acierto), TODOS los contadores de fallos
se reinician a 0, forzando el ciclo a comenzar desde cero.
"""
from enum import Enum

from config import HINT_THRESHOLD, HINT_REVEAL_TIME


class NivelPista(Enum):
    """Niveles de pista escalonados."""
    INACTIVO = 0        # Sin pista activa
    RESALTADO = 1       # Pista N1: borde dorado pulsante
    AUDITIVA = 2        # Pista N2: nota musical del par
    REVELACION = 3      # Pista N3: revelación temporal de 0.8s


class SistemaDePistas:
    """
    Sistema adaptativo de pistas anti-frustración.

    Monitorea los fallos del usuario sobre cartas que ya fueron
    descubiertas previamente. Escala las pistas progresivamente:

        Fallos = 2 → Pista N1 (borde dorado pulsante)
        Fallos = 3 → Pista N2 (pista auditiva)
        Fallos = 4 → Pista N3 (revelación temporal)

    Al acertar una pareja, TODOS los contadores de fallos se
    reinician a 0, reiniciando el ciclo completo de pistas.

    Atributos:
        _umbral (int): Fallos necesarios para activar la primera pista.
        _conteo_fallos (dict): Fallos acumulados por pair_id.
        _nivel_pista (dict): Nivel de pista activo por pair_id.
    """

    def __init__(self, umbral=None):
        self._umbral = umbral if umbral is not None else HINT_THRESHOLD

        # Estado por cada par de cartas
        self._conteo_fallos = {}     # {pair_id: int}
        self._nivel_pista = {}       # {pair_id: NivelPista}
        self._cartas_vistas = set()  # pair_ids de cartas vistas al menos una vez

        # Pista activa actual (la de mayor prioridad)
        self._pair_id_activo = None
        self._nivel_activo = NivelPista.INACTIVO

        # Temporizador para revelación (Pista N3)
        self._reveal_timer = 0.0
        self._reveal_active = False

    # ── Propiedades ──────────────────────────────────────────────────────

    @property
    def nivel_activo(self):
        return self._nivel_activo

    @property
    def pair_id_activo(self):
        return self._pair_id_activo

    @property
    def tiene_pista_activa(self):
        return self._nivel_activo != NivelPista.INACTIVO and self._pair_id_activo is not None

    # ── Registro de eventos ──────────────────────────────────────────────

    def registrar_carta_vista(self, pair_id):
        """
        Registra que al menos una carta de un par ha sido vista.
        Esto permite al sistema detectar fallos en pares ya conocidos.
        """
        self._cartas_vistas.add(pair_id)

    def registrar_fallo(self, pair_id_1, pair_id_2):
        """
        Registra un fallo (las dos cartas no coinciden).
        Si alguna de las cartas pertenece a un par previamente visto,
        incrementa el contador de fallos para ese par.

        Args:
            pair_id_1: pair_id de la primera carta seleccionada.
            pair_id_2: pair_id de la segunda carta seleccionada.
        """
        # Incrementar fallos para pares que ya han sido vistos
        for pid in [pair_id_1, pair_id_2]:
            if pid in self._cartas_vistas:
                self._conteo_fallos[pid] = self._conteo_fallos.get(pid, 0) + 1
                self._evaluar_pista(pid)

    def registrar_acierto(self, pair_id):
        """
        Registra un acierto (pareja encontrada).
        Reinicia TODOS los contadores de fallos y pistas de TODOS los pares,
        de modo que el ciclo de pistas comienza desde cero.
        """
        # Reiniciar TODOS los contadores y pistas — no solo el par encontrado
        self._conteo_fallos.clear()
        self._nivel_pista.clear()
        self._desactivar_pista()
        # Nota: NO limpiamos _cartas_vistas, porque las cartas siguen
        # habiendo sido vistas — solo reiniciamos los fallos.

    # ── Evaluación de pistas ─────────────────────────────────────────────

    def _evaluar_pista(self, pair_id):
        """
        Evalúa si un par debe recibir pista y de qué nivel.
        Escala progresivamente: 2 fallos → N1, 3 → N2, 4 → N3.
        """
        fallos = self._conteo_fallos.get(pair_id, 0)

        if fallos >= self._umbral + 2:
            nuevo_nivel = NivelPista.REVELACION
        elif fallos >= self._umbral + 1:
            nuevo_nivel = NivelPista.AUDITIVA
        elif fallos >= self._umbral:
            nuevo_nivel = NivelPista.RESALTADO
        else:
            return  # Aún no alcanza el umbral

        self._nivel_pista[pair_id] = nuevo_nivel

        # Activar la pista del par con mayor prioridad
        self._actualizar_pista_activa()

    def _actualizar_pista_activa(self):
        """Determina cuál es la pista de mayor nivel activa."""
        max_nivel = NivelPista.INACTIVO
        max_pair = None

        for pid, nivel in self._nivel_pista.items():
            if nivel.value > max_nivel.value:
                max_nivel = nivel
                max_pair = pid

        self._nivel_activo = max_nivel
        self._pair_id_activo = max_pair

    def _desactivar_pista(self):
        """Desactiva la pista actual."""
        self._nivel_activo = NivelPista.INACTIVO
        self._pair_id_activo = None
        self._reveal_active = False

    # ── Aplicar pistas a las cartas ──────────────────────────────────────

    def aplicar_pistas_visuales(self, tablero, gestor_sensorial=None):
        """
        Aplica los efectos visuales y auditivos de la pista activa
        a las cartas correspondientes del tablero.

        Args:
            tablero: Instancia de Tablero.
            gestor_sensorial: Instancia de GestorSensorial (para pistas auditivas).
        """
        # Primero, desactivar glow de todas las cartas
        for carta in tablero.cartas:
            if carta:
                carta.desactivar_glow()

        if not self.tiene_pista_activa:
            return

        # Obtener las cartas del par con pista
        cartas_pista = tablero.obtener_cartas_por_pair_id(self._pair_id_activo)
        cartas_ocultas = [c for c in cartas_pista if c.estado.value == "oculta"]

        if not cartas_ocultas:
            self._desactivar_pista()
            self._actualizar_pista_activa()
            return

        # Aplicar según nivel
        if self._nivel_activo.value >= NivelPista.RESALTADO.value:
            # Pista N1: borde dorado pulsante
            for carta in cartas_ocultas:
                carta.activar_glow()

        if self._nivel_activo.value >= NivelPista.AUDITIVA.value:
            # Pista N2: nota musical (se reproduce una vez al activarse)
            if gestor_sensorial and not self._reveal_active:
                gestor_sensorial.reproducir_pista_auditiva(self._pair_id_activo)

        if self._nivel_activo.value >= NivelPista.REVELACION.value:
            # Pista N3: revelación temporal
            if not self._reveal_active:
                self._reveal_active = True
                self._reveal_timer = HINT_REVEAL_TIME
                for carta in cartas_ocultas:
                    carta.activar_hint_reveal(HINT_REVEAL_TIME)

    # ── Actualización ────────────────────────────────────────────────────

    def actualizar(self, dt):
        """Actualiza temporizadores internos."""
        if self._reveal_active:
            self._reveal_timer -= dt
            if self._reveal_timer <= 0:
                self._reveal_active = False

    # ── Reinicio ─────────────────────────────────────────────────────────

    def reiniciar(self):
        """Reinicia completamente el sistema de pistas."""
        self._conteo_fallos.clear()
        self._nivel_pista.clear()
        self._cartas_vistas.clear()
        self._pair_id_activo = None
        self._nivel_activo = NivelPista.INACTIVO
        self._reveal_active = False
        self._reveal_timer = 0.0
