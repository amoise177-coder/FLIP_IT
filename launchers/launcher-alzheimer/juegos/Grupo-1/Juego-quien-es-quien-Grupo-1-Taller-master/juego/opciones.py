"""Preferencias configurables por el jugador (audio y tamaño de texto)."""


def _limitar(valor, minimo=0.0, maximo=1.0):
    return max(minimo, min(maximo, valor))


class Opciones:
    """Encapsula las preferencias de audio y accesibilidad.

    Los valores solo se modifican a través de sus métodos, que validan
    los rangos permitidos, en lugar de dejar que cualquier parte del
    juego los sobrescriba libremente.
    """

    PASO_VOLUMEN = 0.1

    def __init__(self):
        self._volumen_musica = 0.6
        self._volumen_efectos = 0.8
        self._musica_activa = True
        self._efectos_activos = True
        self._tamano_texto = "normal"  # "normal" o "grande"

    @property
    def volumen_musica(self):
        return self._volumen_musica

    @property
    def volumen_efectos(self):
        return self._volumen_efectos

    @property
    def musica_activa(self):
        return self._musica_activa

    @property
    def efectos_activos(self):
        return self._efectos_activos

    @property
    def tamano_texto(self):
        return self._tamano_texto

    def subir_volumen_musica(self):
        self._volumen_musica = _limitar(self._volumen_musica + self.PASO_VOLUMEN)

    def bajar_volumen_musica(self):
        self._volumen_musica = _limitar(self._volumen_musica - self.PASO_VOLUMEN)

    def subir_volumen_efectos(self):
        self._volumen_efectos = _limitar(self._volumen_efectos + self.PASO_VOLUMEN)

    def bajar_volumen_efectos(self):
        self._volumen_efectos = _limitar(self._volumen_efectos - self.PASO_VOLUMEN)

    def alternar_musica(self):
        self._musica_activa = not self._musica_activa

    def alternar_efectos(self):
        self._efectos_activos = not self._efectos_activos

    def alternar_tamano_texto(self):
        self._tamano_texto = "grande" if self._tamano_texto == "normal" else "normal"
