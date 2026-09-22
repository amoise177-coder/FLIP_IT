import random
from dataclasses import dataclass
from elemento import Elemento  


@dataclass
class Carta(Elemento):

    nombre_imagen: str
    respuesta_correcta: str
    opciones_falsas: list[str]  
    zona: str  

    def cargar_recursos(self) -> None:
        pass

    def renderizar(self) -> None:  
        pass

    def obtener_opciones_mezcladas(self) -> list[str]:
        todas = self.opciones_falsas + [self.respuesta_correcta]
        random.shuffle(todas)
        return todas

@dataclass
class PreguntaSiNo:
    enunciado: str
    es_verdadero: bool  
    zona: str  



