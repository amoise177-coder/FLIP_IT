import random


class ElementoTematico:
    def __init__(self, item_id, nombre, categoria):
        self.id = item_id
        self.numero = item_id
        self.nombre = nombre
        self.categoria = categoria
        self.sacada = False
        self.letra = self._columna_letra(item_id)

    @staticmethod
    def _columna_letra(item_id):
        if item_id <= 15:
            return "B"
        elif item_id <= 30:
            return "I"
        elif item_id <= 45:
            return "N"
        elif item_id <= 60:
            return "G"
        else:
            return "O"

    def marcar_sacada(self):
        self.sacada = True

    def reiniciar(self):
        self.sacada = False

    def __repr__(self):
        return f"ElementoTematico(id={self.id}, nombre='{self.nombre}', cat='{self.categoria}')"


class CatalogoRecuerdos:
    ITEMS = {
        1: {"nombre": "Perro fiel", "cat": "Animales"},
    2: {"nombre": "Gato casero", "cat": "Animales"},
    3: {"nombre": "Caballo noble", "cat": "Animales"},
    4: {"nombre": "Canario cantor", "cat": "Animales"},
    5: {"nombre": "Gallo mañanero", "cat": "Animales"},
    6: {"nombre": "Vaca lechera", "cat": "Animales"},
    7: {"nombre": "Mariposa", "cat": "Animales"},
    8: {"nombre": "Paloma blanca", "cat": "Animales"},
    9: {"nombre": "Conejo blanco", "cat": "Animales"},
    10: {"nombre": "Oveja de lana", "cat": "Animales"},
    11: {"nombre": "Pato de estanque", "cat": "Animales"},
    12: {"nombre": "Pollito amarillo", "cat": "Animales"},
    13: {"nombre": "Abeja laboriosa", "cat": "Animales"},
    14: {"nombre": "Tortuga sabia", "cat": "Animales"},
    15: {"nombre": "Golondrina", "cat": "Animales"},
    16: {"nombre": "Café de olla", "cat": "Sabores"},
    17: {"nombre": "Pan horneado", "cat": "Sabores"},
    18: {"nombre": "Manzana roja", "cat": "Sabores"},
    19: {"nombre": "Pastel casero", "cat": "Sabores"},
    20: {"nombre": "Sopa casera", "cat": "Sabores"},
    21: {"nombre": "Chocolate", "cat": "Sabores"},
    22: {"nombre": "Naranja jugosa", "cat": "Sabores"},
    23: {"nombre": "Queso tierno", "cat": "Sabores"},
    24: {"nombre": "Helado cremoso", "cat": "Sabores"},
    25: {"nombre": "Racimo de uvas", "cat": "Sabores"},
    26: {"nombre": "Tarro de miel", "cat": "Sabores"},
    27: {"nombre": "Té de hierbas", "cat": "Sabores"},
    28: {"nombre": "Fresa dulce", "cat": "Sabores"},
    29: {"nombre": "Limón fresco", "cat": "Sabores"},
    30: {"nombre": "Galletas de canela", "cat": "Sabores"},
    31: {"nombre": "Radio de bulbos", "cat": "Objetos"},
    32: {"nombre": "Tocadiscos", "cat": "Objetos"},
    33: {"nombre": "Plancha carbón", "cat": "Objetos"},
    34: {"nombre": "Máquina coser", "cat": "Objetos"},
    35: {"nombre": "Reloj péndulo", "cat": "Objetos"},
    36: {"nombre": "Teléfono disco", "cat": "Objetos"},
    37: {"nombre": "Lámpara aceite", "cat": "Objetos"},
    38: {"nombre": "Llave antigua", "cat": "Objetos"},
    39: {"nombre": "Baúl de madera", "cat": "Objetos"},
    40: {"nombre": "Espejo dorado", "cat": "Objetos"},
    41: {"nombre": "Molinillo café", "cat": "Objetos"},
    42: {"nombre": "Vela y palmatoria", "cat": "Objetos"},
    43: {"nombre": "Libro de cuero", "cat": "Objetos"},
    44: {"nombre": "Cesta mimbre", "cat": "Objetos"},
    45: {"nombre": "Tetera de peltre", "cat": "Objetos"},
    46: {"nombre": "Rosa roja", "cat": "Naturaleza"},
    47: {"nombre": "Clavel blanco", "cat": "Naturaleza"},
    48: {"nombre": "Girasol alegre", "cat": "Naturaleza"},
    49: {"nombre": "Árbol frondoso", "cat": "Naturaleza"},
    50: {"nombre": "Sol radiante", "cat": "Naturaleza"},
    51: {"nombre": "Luna llena", "cat": "Naturaleza"},
    52: {"nombre": "Río cristalino", "cat": "Naturaleza"},
    53: {"nombre": "Estrella fuga", "cat": "Naturaleza"},
    54: {"nombre": "Montaña verde", "cat": "Naturaleza"},
    55: {"nombre": "Hoja de otoño", "cat": "Naturaleza"},
    56: {"nombre": "Nube blanca", "cat": "Naturaleza"},
    57: {"nombre": "Mar azul", "cat": "Naturaleza"},
    58: {"nombre": "Pinar perfumado", "cat": "Naturaleza"},
    59: {"nombre": "Trébol de suerte", "cat": "Naturaleza"},
    60: {"nombre": "Lluvia serena", "cat": "Naturaleza"},
    61: {"nombre": "Guitarra", "cat": "Música"},
    62: {"nombre": "Acordeón", "cat": "Música"},
    63: {"nombre": "Pandereta", "cat": "Música"},
    64: {"nombre": "Trompeta alegre", "cat": "Música"},
    65: {"nombre": "Violín dulce", "cat": "Música"},
    66: {"nombre": "Sombrero típico", "cat": "Música"},
    67: {"nombre": "Abanico encaje", "cat": "Música"},
    68: {"nombre": "Pañuelo bordado", "cat": "Música"},
    69: {"nombre": "Manto abrigado", "cat": "Música"},
    70: {"nombre": "Danza tradicional", "cat": "Música"},
    71: {"nombre": "Tambor festivo", "cat": "Música"},
    72: {"nombre": "Campana pueblo", "cat": "Música"},
    73: {"nombre": "Flauta dulce", "cat": "Música"},
    74: {"nombre": "Castañuelas", "cat": "Música"},
        75: {"nombre": "Silbato tren", "cat": "Música"}
    }


CATALOGO_75_ITEMS = CatalogoRecuerdos.ITEMS


def crear_catalogo_completo():
    return {
        item_id: ElementoTematico(item_id, datos["nombre"], datos["cat"])
        for item_id, datos in CatalogoRecuerdos.ITEMS.items()
    }


class Bolillero:
    def __init__(self, max_bolas_regular=40):
        self.catalogo = crear_catalogo_completo()
        self.bolas = list(self.catalogo.values())
        self.bolas_disponibles = self.bolas.copy()
        self.historial_extraidas = []
        self.ids_extraidos = set()
        self.max_bolas_regular = max_bolas_regular

    def sacar_bola(self):
        if not self.bolas_disponibles:
            return None
        elemento = random.choice(self.bolas_disponibles)
        self.bolas_disponibles.remove(elemento)
        elemento.marcar_sacada()
        self.historial_extraidas.append(elemento)
        self.ids_extraidos.add(elemento.id)
        return elemento

    @property
    def total_extraidas(self):
        return len(self.historial_extraidas)

    @property
    def quedan_bolas(self):
        return len(self.bolas_disponibles) > 0

    @property
    def fase_regular_completa(self):
        return self.total_extraidas >= self.max_bolas_regular

    def obtener_ultima_bola(self):
        return self.historial_extraidas[-1] if self.historial_extraidas else None

    def reiniciar(self):
        for elem in self.bolas:
            elem.reiniciar()
        self.bolas_disponibles = self.bolas.copy()
        self.historial_extraidas.clear()
        self.ids_extraidos.clear()


class Carton:
    NOMBRES_MODALIDADES = {
        1: "Columna Central (Camino de Recuerdos)",
        2: "Base Firme (Línea Inferior)",
        3: "Escuadra de Orientación (L Invertida)",
        4: "Cruce de Caminos (Diagonal en X)",
        5: "Pequeño Refugio (Cuadro Interior 4 Esquinas)",
        6: "Ventana al Pasado (Marco Concéntrico 3x3)",
        7: "Rombo de Luces (Diamante Radiante)",
        8: "Árbol Genealógico (Figura Y)",
        9: "Mosaico Completo (Esquinas + Cuadro Central)",
        10: "Marco de la Memoria (Borde Exterior)",
        11: "Cruz de la Amistad (Cruz Central)",
        12: "Cuatro Faros (Esquinas Exteriores)",
        13: "Sendero Inicial (Animales / Columna B)",
        14: "¡Bingo Pleno! (Cartón Lleno de Recuerdos)"
    }

    def __init__(self, posicion_id=0, catalogo_ref=None):
        self.posicion_id = posicion_id
        self.catalogo = catalogo_ref or crear_catalogo_completo()
        self.matriz_ids = self.generar_carton()
        self.matriz = self.matriz_ids
        self.marcados = [[False] * 5 for _ in range(5)]
        self.marcados[2][2] = True
        self.modalidades_verificadas = {i: False for i in range(1, 15)}

    def generar_carton(self):
        rangos = [
            range(1, 16),
            range(16, 31),
            range(31, 46),
            range(46, 61),
            range(61, 76)
        ]
        columnas = [random.sample(r, 5) for r in rangos]
        matriz = list(map(list, zip(*columnas)))
        matriz[2][2] = 0
        return matriz

    def obtener_elemento_en(self, fila, col):
        item_id = self.matriz_ids[fila][col]
        return self.catalogo.get(item_id) if item_id != 0 else None

    def esta_marcado(self, fila, col):
        return self.marcados[fila][col]

    def marcar_manualmente(self, fila, col, ids_extraidos):
        if fila == 2 and col == 2:
            return False, None, "centro_libre"
        if self.marcados[fila][col]:
            return False, self.obtener_elemento_en(fila, col), "ya_marcado"

        item_id = self.matriz_ids[fila][col]
        elemento = self.catalogo.get(item_id)
        if item_id in ids_extraidos:
            self.marcados[fila][col] = True
            return True, elemento, "acierto"
        return False, elemento, "no_extraido"

    def marcar_automatico(self, item_id):
        for f in range(5):
            for c in range(5):
                if self.matriz_ids[f][c] == item_id:
                    self.marcados[f][c] = True
                    return True
        return False

    def forma_1(self):
        return all(self.marcados[i][2] for i in range(5))

    def forma_2(self):
        return all(self.marcados[4][j] for j in range(5))

    def forma_3(self):
        return all(self.marcados[i][4] for i in range(5)) and self.marcados[4][2] and self.marcados[4][3]

    def forma_4(self):
        d1 = (self.marcados[0][0] and self.marcados[1][1] and self.marcados[3][3] and self.marcados[4][4])
        d2 = (self.marcados[0][4] and self.marcados[1][3] and self.marcados[3][1] and self.marcados[4][0])
        return d1 and d2

    def forma_5(self):
        return (self.marcados[1][1] and self.marcados[3][1] and
                self.marcados[1][3] and self.marcados[3][3])

    def forma_6(self):
        return (self.marcados[1][1] and self.marcados[1][2] and self.marcados[1][3] and
                self.marcados[2][1] and self.marcados[2][3] and
                self.marcados[3][1] and self.marcados[3][2] and self.marcados[3][3])

    def forma_7(self):
        p = (self.marcados[0][2] and self.marcados[2][0] and self.marcados[2][4] and self.marcados[4][2])
        c = (self.marcados[1][1] and self.marcados[1][3] and self.marcados[3][1] and self.marcados[3][3])
        return p and c

    def forma_8(self):
        l = all(self.marcados[4][j] for j in range(5))
        y = (self.marcados[0][0] and self.marcados[1][1] and self.marcados[3][2] and
             self.marcados[1][3] and self.marcados[0][4])
        return l and y

    def forma_9(self):
        esq = (self.marcados[0][0] and self.marcados[0][4] and self.marcados[4][0] and self.marcados[4][4])
        return self.forma_6() and esq

    def forma_10(self):
        fb = all(self.marcados[0][i] for i in range(5)) and all(self.marcados[4][i] for i in range(5))
        lat = (self.marcados[1][0] and self.marcados[2][0] and self.marcados[3][0] and
               self.marcados[1][4] and self.marcados[2][4] and self.marcados[3][4])
        return fb and lat

    def forma_11(self):
        return all(self.marcados[i][2] for i in range(5)) and all(self.marcados[2][j] for j in range(5))

    def forma_12(self):
        return (self.marcados[0][0] and self.marcados[0][4] and self.marcados[4][0] and self.marcados[4][4])

    def forma_13(self):
        return all(self.marcados[i][0] for i in range(5))

    def carton_lleno(self):
        for f in range(5):
            for c in range(5):
                if f == 2 and c == 2:
                    continue
                if not self.marcados[f][c]:
                    return False
        return True

    def existe_bingo(self):
        modalidades_detectadas = []
        if self.carton_lleno() and not self.modalidades_verificadas[14]:
            self.modalidades_verificadas[14] = True
            modalidades_detectadas.append(14)

        for i in range(1, 14):
            metodo = getattr(self, f"forma_{i}")
            if metodo() and not self.modalidades_verificadas[i]:
                self.modalidades_verificadas[i] = True
                modalidades_detectadas.append(i)

        if modalidades_detectadas:
            modalidades_detectadas.sort(reverse=True)
            if modalidades_detectadas[0] == 14:
                return True, 14
            return True, modalidades_detectadas
        return False, None

    def validar_bingo(self, modalidades_permitidas):
        resultado, modalidades = self.existe_bingo()
        if not resultado:
            return False, None
        if isinstance(modalidades, list):
            validas = [m for m in modalidades if m in modalidades_permitidas]
        else:
            validas = [modalidades] if modalidades in modalidades_permitidas else []

        if validas:
            return True, validas[0] if len(validas) == 1 else validas
        return False, None


class SistemaRecompensas:
    ESTRELLAS_POR_MODALIDAD = {
        1: 15, 2: 20, 3: 35, 4: 60, 5: 25, 6: 45, 7: 80,
        8: 120, 9: 200, 10: 350, 11: 30, 12: 25, 13: 15, 14: 1000
    }

    def __init__(self, estrellas_iniciales=100):
        self.estrellas_totales = estrellas_iniciales
        self.estrellas_sesion_actual = 0
        self.fichas_enfoque = 10
        self.aciertos_destreza = 0

    def ajustar_enfoque(self, delta):
        nuevo = self.fichas_enfoque + delta
        if 5 <= nuevo <= 50:
            self.fichas_enfoque = nuevo
        return self.fichas_enfoque

    def registrar_acierto_destreza(self):
        self.aciertos_destreza += 1
        puntos_acierto = 2
        self.estrellas_totales += puntos_acierto
        self.estrellas_sesion_actual += puntos_acierto
        return puntos_acierto

    def acreditar_premio_figura(self, modalidad):
        base = self.ESTRELLAS_POR_MODALIDAD.get(modalidad, 20)
        multiplicador = max(1, self.fichas_enfoque // 10)
        estrellas = base * multiplicador
        self.estrellas_totales += estrellas
        self.estrellas_sesion_actual += estrellas
        return estrellas

    def reiniciar_sesion(self):
        self.estrellas_sesion_actual = 0
        self.aciertos_destreza = 0


class NivelEstimulacion:
    MODO_TRADICIONAL = {1, 2, 4, 11, 12, 13, 14}
    MODO_ESPECIAL = set(range(1, 15))
    MODO_COMPLETO = {14}

    NOMBRES_MODOS = {
        1: "Tradicional",
        2: "Especial (14 figuras)",
        3: "Completo (Cartón Lleno)"
    }

    @classmethod
    def obtener_modalidades(cls, nivel):
        if nivel == 1:
            return cls.MODO_TRADICIONAL
        elif nivel == 2:
            return cls.MODO_ESPECIAL
        elif nivel == 3:
            return cls.MODO_COMPLETO
        return cls.MODO_TRADICIONAL

    @classmethod
    def obtener_nombre_modo(cls, nivel):
        return cls.NOMBRES_MODOS.get(nivel, f"Modo {nivel}")


class PartidaBingoCognitivo:
    ESTADO_CONFIGURACION = "CONFIGURACION"
    ESTADO_EXTRACCION_REGULAR = "EXTRACCION_REGULAR"
    ESTADO_FINALIZADO = "FINALIZADO"

    def __init__(self, nivel_inicial=1):
        self.nivel = nivel_inicial
        self.bolillero = Bolillero(max_bolas_regular=40)
        self.cartones = []
        self.recompensas = SistemaRecompensas(estrellas_iniciales=100)
        self.estado = self.ESTADO_CONFIGURACION
        self.juego_activo = False
        self.ultimo_logro = None

    def fijar_nivel(self, nivel):
        if nivel in (1, 2, 3):
            self.nivel = nivel

    def agregar_carton(self):
        if len(self.cartones) < 4:
            nuevo = Carton(posicion_id=len(self.cartones), catalogo_ref=self.bolillero.catalogo)
            self.cartones.append(nuevo)
            return nuevo
        return None

    def eliminar_carton(self, indice):
        if 0 <= indice < len(self.cartones) and not self.juego_activo:
            self.cartones.pop(indice)
            for i, c in enumerate(self.cartones):
                c.posicion_id = i
            return True
        return False

    def iniciar_sorteo(self):
        if not self.cartones:
            return False
        self.juego_activo = True
        self.estado = self.ESTADO_EXTRACCION_REGULAR
        self.recompensas.reiniciar_sesion()
        return True

    def extraer_siguiente_elemento(self):
        if not self.juego_activo:
            return None
        if self.bolillero.fase_regular_completa:
            return None
        elemento = self.bolillero.sacar_bola()
        if not elemento:
            self.estado = self.ESTADO_FINALIZADO
            self.juego_activo = False
            return None
        if self.bolillero.fase_regular_completa:
            self.estado = self.ESTADO_FINALIZADO
        return elemento

    def marcar_casilla_por_usuario(self, carton_idx, fila, col):
        if not (0 <= carton_idx < len(self.cartones)):
            return False, None, "carton_invalido", None

        carton = self.cartones[carton_idx]
        acierto, elemento, codigo = carton.marcar_manualmente(fila, col, self.bolillero.ids_extraidos)

        info_logro = None
        if acierto:
            self.recompensas.registrar_acierto_destreza()
            modalidades_validas = NivelEstimulacion.obtener_modalidades(self.nivel)
            hubo_bingo, modalidad = carton.validar_bingo(modalidades_validas)

            if hubo_bingo:
                if modalidad == 14:
                    estrellas = self.recompensas.acreditar_premio_figura(14)
                    info_logro = {
                        "tipo": "BINGO_PLENO",
                        "carton_indice": carton_idx + 1,
                        "modalidad": 14,
                        "nombres": [Carton.NOMBRES_MODALIDADES[14]],
                        "estrellas": estrellas
                    }
                    self.ultimo_logro = info_logro
                    self.estado = self.ESTADO_FINALIZADO
                    self.juego_activo = False
                else:
                    mods = modalidad if isinstance(modalidad, list) else [modalidad]
                    nombres = [Carton.NOMBRES_MODALIDADES.get(m, f"Figura {m}") for m in mods]
                    estrellas = sum(self.recompensas.acreditar_premio_figura(m) for m in mods)
                    info_logro = {
                        "tipo": "FIGURA_COMPLETADA",
                        "carton_indice": carton_idx + 1,
                        "modalidades": mods,
                        "nombres": nombres,
                        "estrellas": estrellas
                    }
                    self.ultimo_logro = info_logro

        return acierto, elemento, codigo, info_logro

    def verificar_combinaciones_finales(self):
        self.juego_activo = False
        self.estado = self.ESTADO_FINALIZADO
        modalidades_validas = NivelEstimulacion.obtener_modalidades(self.nivel)

        cartones_resumen = []
        todas_figuras_detectadas = []
        hay_bingo_pleno = False

        for idx, carton in enumerate(self.cartones):
            figuras_este_carton = []

            if 14 in modalidades_validas and carton.carton_lleno():
                hay_bingo_pleno = True
                if not carton.modalidades_verificadas.get(14, False):
                    carton.modalidades_verificadas[14] = True
                    self.recompensas.acreditar_premio_figura(14)
                figuras_este_carton.append({
                    "modalidad": 14,
                    "nombre": Carton.NOMBRES_MODALIDADES[14],
                    "estrellas": self.recompensas.ESTRELLAS_POR_MODALIDAD[14] * max(1, self.recompensas.fichas_enfoque // 10)
                })

            for m in range(1, 14):
                if m in modalidades_validas:
                    metodo = getattr(carton, f"forma_{m}", None)
                    if metodo and metodo():
                        if not carton.modalidades_verificadas.get(m, False):
                            carton.modalidades_verificadas[m] = True
                            self.recompensas.acreditar_premio_figura(m)
                        figuras_este_carton.append({
                            "modalidad": m,
                            "nombre": Carton.NOMBRES_MODALIDADES.get(m, f"Figura {m}"),
                            "estrellas": self.recompensas.ESTRELLAS_POR_MODALIDAD.get(m, 20) * max(1, self.recompensas.fichas_enfoque // 10)
                        })

            cartones_resumen.append({
                "carton_indice": idx + 1,
                "figuras": figuras_este_carton
            })
            todas_figuras_detectadas.extend(figuras_este_carton)

        resumen = {
            "tipo": "FIN_PARTIDA",
            "total_balotas": self.bolillero.total_extraidas,
            "aciertos_destreza": self.recompensas.aciertos_destreza,
            "puntos_destreza": self.recompensas.aciertos_destreza * 2,
            "cartones_resultados": cartones_resumen,
            "total_figuras": len(todas_figuras_detectadas),
            "estrellas_ganadas": self.recompensas.estrellas_sesion_actual,
            "estrellas_totales": self.recompensas.estrellas_totales,
            "bingo_pleno": hay_bingo_pleno
        }
        self.ultimo_logro = resumen
        return resumen

    def finalizar_sesion(self):
        self.juego_activo = False
        self.estado = self.ESTADO_FINALIZADO

    def reiniciar_partida(self):
        self.bolillero.reiniciar()
        self.cartones.clear()
        self.juego_activo = False
        self.estado = self.ESTADO_CONFIGURACION
        self.ultimo_logro = None
