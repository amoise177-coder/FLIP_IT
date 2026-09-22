# 📘 Manual Maestro: Pilares de la POO y Explicación Exhaustiva del Código
## Proyecto: *Bingo Calma — Estimulación Cognitiva y Sensorial*

> **Diseño de lectura:**  
> En este manual, **cada función y método se presenta directamente junto a su código específico**, seguido inmediatamente de su explicación paso a paso para facilitar la lectura y comprensión inmediata sin tener que desplazarse por el documento.

---

## 📑 Tabla de Contenidos General

1. [Glosario y Conceptos Básicos de Python para Principiantes](#1-glosario-y-conceptos-básicos-de-python-para-principiantes)
2. [Los 4 Pilares de la POO: Teoría y Fundamentos](#2-los-4-pilares-de-la-poo-teoría-y-fundamentos)
3. [Módulo 1: `logica.py` (Dominio y Reglas del Juego)](#3-módulo-1-logicapy-dominio-y-reglas-del-juego)
   - 3.1. [Clase `ElementoTematico`](#31-clase-elementotematico)
   - 3.2. [Catálogo de Recuerdos y `crear_catalogo_completo()`](#32-catálogo-de-recuerdos-y-crear_catalogo_completo)
   - 3.3. [Clase `Bolillero`](#33-clase-bolillero)
   - 3.4. [Clase `Carton`](#34-clase-carton)
   - 3.5. [Clase `SistemaRecompensas`](#35-clase-sistemarecompensas)
   - 3.6. [Clase `NivelEstimulacion`](#36-clase-nivelestimulacion)
   - 3.7. [Clase `PartidaBingoCognitivo`](#37-clase-partidabingocognitivo)
4. [Módulo 2: `recursos.py` (Multimedia, Gráficos y Audio)](#4-módulo-2-recursospy-multimedia-gráficos-y-audio)
   - 4.1. [Clase `Configuracion`](#41-clase-configuracion)
   - 4.2. [Clase `Fuentes`](#42-clase-fuentes)
   - 4.3. [Clase `GestorMusica`](#43-clase-gestormusica)
   - 4.4. [Clase `GestorAssets`](#44-clase-gestorassets)
   - 4.5. [Función `inicializar_sistema_recursos()`](#45-función-inicializar_sistema_recursos)
5. [Módulo 3: `main.py` (Interfaz Gráfica e Interacción)](#5-módulo-3-mainpy-interfaz-gráfica-e-interacción)
   - 5.1. [Clase `BotonCalma`](#51-clase-botoncalma)
   - 5.2. [Clase `TableroCartonGUI`](#52-clase-tablerocartongui)
   - 5.3. [Clase `BingoCalmaApp`](#53-clase-bingocalmaapp)
6. [Resumen Comparativo de Pilares por Clase](#6-resumen-comparativo-de-pilares-por-clase)
7. [Apéndice Técnico: ¿Cómo Quedaría el Código Sin Usar Decoradores?](#7-apéndice-técnico-cómo-quedaría-el-código-sin-usar-decoradores)

---

## 1. Glosario y Conceptos Básicos de Python para Principiantes

Si nunca has programado en Python, estos son los términos esenciales que encontrarás a lo largo de este manual:

* **¿Qué es una Clase (`class`)?**  
  Es un plano arquitectónico, plantilla o molde. Por ejemplo, la clase `Carton` define qué datos tiene un cartón (25 casillas) y qué acciones puede hacer (marcar casilla, comprobar bingo), pero aún no es un cartón en la pantalla.
* **¿Qué es un Objeto / Instancia?**  
  Es la entidad real construida a partir de la clase. Si la clase es `Carton`, el cartón 1 y el cartón 2 en tu pantalla son dos objetos distintos nacidos del mismo molde.
* **¿Qué es un Atributo (`self.variable`)?**  
  Son las características o datos que pertenecen al objeto. Ejemplo: `self.nombre = "Café de olla"`.
* **¿Qué es un Método (`def nombre_metodo(self, ...):`)?**  
  Es una función que vive dentro de una clase y representa una acción que el objeto puede realizar. Ejemplo: `def sacar_bola(self):`.
* **¿Qué significa `self`?**  
  Significa *"yo mismo"* o *"este objeto específico"*. En Python, cuando un objeto ejecuta un método, `self` le permite acceder a sus propios datos y no confundirse con los datos de otro objeto similar.
* **¿Qué es `__init__`?**  
  Es el método **Constructor**. Es la función que se ejecuta automáticamente de forma obligatoria en el instante exacto en que nace un nuevo objeto para inicializar sus variables.
* **¿Qué es una Lista (`[]`) y un Diccionario (`{}`)?**  
  - Una **Lista** es una secuencia ordenada de cosas: `[bola1, bola2, bola3]`.
  - Un **Diccionario** asocia claves con valores como una libreta telefónica: `{1: "Perro fiel", 2: "Gato casero"}`.
* **¿Qué es un Conjunto (`set()`)?**  
  Una colección que no permite elementos repetidos y permite comprobar si algo existe adentro en tiempo récord ($O(1)$).

---

## 2. Los 4 Pilares de la POO: Teoría y Fundamentos

```
                  ┌──────────────────────────────────────────────┐
                  │    LOS 4 PILARES FUNDAMENTALES DE LA POO     │
                  └───────┬──────┬──────────────┬────────┬───────┘
                          │      │              │        │
           ┌──────────────┘      │              │        └──────────────┐
           ▼                     ▼              ▼                       ▼
    1. ABSTRACCIÓN       2. ENCAPSULAMIENTO 3. HERENCIA           4. POLIMORFISMO
   (Ocultar detalles     (Proteger datos y   (Reutilizar y        (Mismo mensaje,
    y exponer interfaz   controlar acceso    extender clases      diferente respuesta
    simple)              interno)            existentes)          según el objeto)
```

1. **Abstracción:** Ocultar la complejidad interna del sistema y presentar únicamente una interfaz simple y clara hacia el exterior. Quien usa el objeto no necesita saber cómo está programado por dentro para poder utilizarlo.
2. **Encapsulamiento:** Agrupar datos y métodos dentro de una misma estructura y restringir el acceso directo a los detalles internos, obligando a interactuar mediante métodos que validan y protegen el estado del objeto.
3. **Herencia:** Capacidad de una clase de derivar de otra clase "padre", heredando todos sus atributos y métodos, para reutilizar código y especializar comportamientos sin repetir código.
4. **Polimorfismo:** Capacidad de objetos de distintas clases de responder a un método que lleva el mismo nombre, ejecutando cada uno el comportamiento adecuado a su naturaleza.

---

## 3. Módulo 1: `logica.py` (Dominio y Reglas del Juego)

Este archivo es el **núcleo matemático y lógico**. No dibuja nada en pantalla ni reproduce sonidos; funciona puramente con datos y reglas de negocio.

---

### 3.1. Clase `ElementoTematico`
Representa cada una de las 75 fichas nostálgicas que sustituyen a los números tradicionales del bingo (ej: *"Café de olla"*, *"Rosa roja"*).

#### A. Constructor `__init__`
```python
    def __init__(self, item_id, nombre, categoria):
        self.id = item_id
        self.numero = item_id
        self.nombre = nombre
        self.categoria = categoria
        self.sacada = False
        self.letra = self._columna_letra(item_id)
```
**Explicación paso a paso:**
- Recibe tres datos iniciales: el identificador numérico (`item_id` del 1 al 75), el `nombre` descriptivo y la `categoria` temática.
- Inicializa los atributos del objeto: guarda el ID, el número, el nombre y la categoría.
- Establece `self.sacada = False`, indicando que la ficha se encuentra inicialmente dentro del bolillero.
- Llama a `self._columna_letra(item_id)` para determinar automáticamente si pertenece a la columna B, I, N, G u O.

---

#### B. Método Estático `_columna_letra`
```python
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
```
**Explicación paso a paso:**
- Función utilitaria estática que no depende del estado del objeto.
- Implementa la regla tradicional del bingo americano por rangos numéricos:
  - Del 1 al 15 $\rightarrow$ Columna **B**
  - Del 16 al 30 $\rightarrow$ Columna **I**
  - Del 31 al 45 $\rightarrow$ Columna **N**
  - Del 46 al 60 $\rightarrow$ Columna **G**
  - Del 61 al 75 $\rightarrow$ Columna **O**

---

#### C. Métodos de Estado: `marcar_sacada` y `reiniciar`
```python
    def marcar_sacada(self):
        self.sacada = True

    def reiniciar(self):
        self.sacada = False
```
**Explicación paso a paso:**
- `marcar_sacada(self)`: Cambia `self.sacada` a `True` cuando la balota es extraída del bombo virtual.
- `reiniciar(self)`: Restablece `self.sacada` a `False` para dejar la balota disponible para una nueva partida.

---

#### D. Método Especial `__repr__`
```python
    def __repr__(self):
        return f"ElementoTematico(id={self.id}, nombre='{self.nombre}', cat='{self.categoria}')"
```
**Explicación paso a paso:**
- Proporciona una representación textual formateada para consola y depuración, mostrando el ID, el nombre y la categoría del elemento.

---

#### 🏛️ Pilares de la POO en `ElementoTematico` y Evidencia en el Código:
* **Encapsulamiento:**  
  *Evidencia:* La variable `self.sacada` está protegida; su mutación se realiza mediante los métodos autorizados `marcar_sacada()` y `reiniciar()`.  
  *Evidencia:* La determinación de la columna está encapsulada en `_columna_letra(item_id)` y se ejecuta automáticamente al instanciar el objeto.
* **Abstracción:**  
  *Evidencia:* Transforma un número entero en una entidad temática completa con nombre, categoría, letra y estado de extracción.
* **Polimorfismo:**  
  *Evidencia:* Implementa el método `reiniciar()`, compartiendo nombre y propósito con `Bolillero` y `PartidaBingoCognitivo`.

---

### 3.2. Catálogo de Recuerdos y `crear_catalogo_completo()`

```python
class CatalogoRecuerdos:
    ITEMS = {
        1: {"nombre": "Perro fiel", "cat": "Animales"},
        # ... del 1 al 75 ...
        75: {"nombre": "Silbato tren", "cat": "Música"}
    }

CATALOGO_75_ITEMS = CatalogoRecuerdos.ITEMS

def crear_catalogo_completo():
    return {
        item_id: ElementoTematico(item_id, datos["nombre"], datos["cat"])
        for item_id, datos in CatalogoRecuerdos.ITEMS.items()
    }
```
**Explicación paso a paso:**
- `CatalogoRecuerdos.ITEMS`: Diccionario de clase que funciona como base de datos estática centralizada con los 75 recuerdos distribuidos en 5 categorías.
- `crear_catalogo_completo()`: Función de fábrica (Factory) que genera un nuevo diccionario donde cada clave (1 a 75) apunta a una instancia independiente de `ElementoTematico`.

#### 🏛️ Pilares de la POO:
* **Abstracción:** Separa la definición estática de datos del modelo de objetos del juego.

---

### 3.3. Clase `Bolillero`
Controla el bombo virtual de extracción aleatoria sin repetición.

#### A. Constructor `__init__`
```python
    def __init__(self, max_bolas_regular=40):
        self.catalogo = crear_catalogo_completo()
        self.bolas = list(self.catalogo.values())
        self.bolas_disponibles = self.bolas.copy()
        self.historial_extraidas = []
        self.ids_extraidos = set()
        self.max_bolas_regular = max_bolas_regular
```
**Explicación paso a paso:**
- Inicializa el catálogo con las 75 balotas temáticas.
- Genera la lista `self.bolas_disponibles` como copia de trabajo.
- Crea la lista `self.historial_extraidas` para almacenar el orden cronológico de salida.
- Crea el conjunto `self.ids_extraidos` (`set()`) para consultas de pertenencia en tiempo constante $O(1)$.
- Fija el límite de la fase regular en 40 balotas.

---

#### B. Método `sacar_bola`
```python
    def sacar_bola(self):
        if not self.bolas_disponibles:
            return None
        elemento = random.choice(self.bolas_disponibles)
        self.bolas_disponibles.remove(elemento)
        elemento.marcar_sacada()
        self.historial_extraidas.append(elemento)
        self.ids_extraidos.add(elemento.id)
        return elemento
```
**Explicación paso a paso:**
- Verifica si quedan balotas disponibles; si no quedan, retorna `None`.
- Selecciona un elemento al azar mediante `random.choice`.
- Remueve el elemento de `self.bolas_disponibles` garantizando que no se repita.
- Invoca `elemento.marcar_sacada()`.
- Registra el elemento en `self.historial_extraidas` y su ID en `self.ids_extraidos`.
- Retorna el objeto extraído.

---

#### C. Propiedades Calculadas (`@property`)
```python
    @property
    def total_extraidas(self):
        return len(self.historial_extraidas)

    @property
    def quedan_bolas(self):
        return len(self.bolas_disponibles) > 0

    @property
    def fase_regular_completa(self):
        return self.total_extraidas >= self.max_bolas_regular
```
**Explicación paso a paso:**
- `total_extraidas`: Retorna la cantidad de balotas sacadas calculando la longitud del historial.
- `quedan_bolas`: Retorna `True` si aún restan balotas disponibles en el bombo.
- `fase_regular_completa`: Evalúa si se alcanzó el límite de 40 extracciones.

---

#### D. Métodos de Consulta y Reinicio: `obtener_ultima_bola` y `reiniciar`
```python
    def obtener_ultima_bola(self):
        return self.historial_extraidas[-1] if self.historial_extraidas else None

    def reiniciar(self):
        for elem in self.bolas:
            elem.reiniciar()
        self.bolas_disponibles = self.bolas.copy()
        self.historial_extraidas.clear()
        self.ids_extraidos.clear()
```
**Explicación paso a paso:**
- `obtener_ultima_bola(self)`: Retorna el último elemento extraído usando el índice `[-1]`, o `None` si la partida apenas comienza.
- `reiniciar(self)`: Itera por cada balota invocando `elem.reiniciar()`, restaura la lista de disponibles y limpia el historial y el conjunto de IDs.

---

#### 🏛️ Pilares de la POO en `Bolillero` y Evidencia en el Código:
* **Abstracción:**  
  *Evidencia:* Toda la mecánica de extracción aleatoria sin reemplazo, gestión de listas y sincronización de conjuntos queda abstraída tras la llamada `bolillero.sacar_bola()`.
* **Encapsulamiento:**  
  *Evidencia:* Las propiedades `@property total_extraidas`, `quedan_bolas` y `fase_regular_completa` exponen datos calculados en modo solo lectura, impidiendo su alteración directa desde el exterior.
* **Polimorfismo:**  
  *Evidencia:* `reiniciar()` restablece el bolillero y coordina el método polimórfico `reiniciar()` de cada `ElementoTematico`.

---

### 3.4. Clase `Carton`
Representa una tarjeta de bingo de 5x5 casillas con verificación de 14 figuras.

#### A. Constructor `__init__`
```python
    def __init__(self, posicion_id=0, catalogo_ref=None):
        self.posicion_id = posicion_id
        self.catalogo = catalogo_ref or crear_catalogo_completo()
        self.matriz_ids = self.generar_carton()
        self.matriz = self.matriz_ids
        self.marcados = [[False] * 5 for _ in range(5)]
        self.marcados[2][2] = True
        self.modalidades_verificadas = {i: False for i in range(1, 15)}
```
**Explicación paso a paso:**
- Asigna el identificador de posición del cartón (0 o 1).
- Asocia la referencia al catálogo temático.
- Invoca `self.generar_carton()` para construir la matriz numérica de 5x5.
- Crea `self.marcados`: matriz booleana de 5x5 inicializada en `False`.
- Establece `self.marcados[2][2] = True` (la casilla central libre/estrella de cortesía).
- Inicializa el diccionario `self.modalidades_verificadas` para registrar qué figuras ya fueron premiadas.

---

#### B. Método `generar_carton`
```python
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
```
**Explicación paso a paso:**
- Define los 5 rangos de las columnas B-I-N-G-O.
- Con `random.sample(r, 5)` extrae 5 valores aleatorios sin repetición por columna.
- Transpone las columnas en filas mediante `list(map(list, zip(*columnas)))`.
- Asigna `0` en la casilla central `[2][2]` como marcador de espacio libre.

---

#### C. Métodos de Consulta y Marcado: `obtener_elemento_en`, `esta_marcado` y `marcar_manualmente`
```python
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
```
**Explicación paso a paso:**
- `obtener_elemento_en`: Retorna el `ElementoTematico` ubicado en la casilla, o `None` si es el centro libre (0).
- `esta_marcado`: Consulta booleana que retorna `True` si la casilla tiene ficha colocada.
- `marcar_manualmente`: Valida la jugada del usuario:
  - Si es la casilla central `[2][2]`, reporta `"centro_libre"`.
  - Si la casilla ya estaba marcada, reporta `"ya_marcado"`.
  - Si el ID de la casilla pertenece a `ids_extraidos`, asigna `self.marcados[fila][col] = True` y reporta `"acierto"`.
  - Si la balota aún no ha sido extraída del bombo, reporta `"no_extraido"`.

---

#### D. Verificación de Formas Matemáticas (`forma_1` a `forma_13` y `carton_lleno`)
```python
    def forma_1(self):
        return all(self.marcados[i][2] for i in range(5))

    def forma_2(self):
        return all(self.marcados[4][j] for j in range(5))

    def forma_4(self):
        d1 = (self.marcados[0][0] and self.marcados[1][1] and self.marcados[3][3] and self.marcados[4][4])
        d2 = (self.marcados[0][4] and self.marcados[1][3] and self.marcados[3][1] and self.marcados[4][0])
        return d1 and d2

    def forma_11(self):
        return all(self.marcados[i][2] for i in range(5)) and all(self.marcados[2][j] for j in range(5))

    def forma_12(self):
        return (self.marcados[0][0] and self.marcados[0][4] and self.marcados[4][0] and self.marcados[4][4])

    def carton_lleno(self):
        for f in range(5):
            for c in range(5):
                if f == 2 and c == 2:
                    continue
                if not self.marcados[f][c]:
                    return False
        return True
```
**Explicación paso a paso:**
- Cada método evalúa algebraicamente un patrón en la matriz de booleanos:
  - `forma_1`: Evalúa la columna central vertical (`i=0..4, col=2`).
  - `forma_2`: Evalúa la línea inferior horizontal (`fila=4, j=0..4`).
  - `forma_4`: Evalúa la diagonal en X (`d1` y `d2`).
  - `forma_11`: Evalúa la cruz central (fila 2 y columna 2 completas).
  - `forma_12`: Evalúa las 4 esquinas exteriores.
  - `carton_lleno`: Revisa que las 24 casillas activas estén en `True`.

---

#### E. Detección y Validación de Bingo: `existe_bingo` y `validar_bingo`
```python
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
```
**Explicación paso a paso:**
- `existe_bingo`: Inspecciona si hay nuevas figuras formadas usando introspección con `getattr(self, f"forma_{i}")`. Si una forma es válida y no había sido premiada, la marca en `self.modalidades_verificadas` y la añade a la lista.
- `validar_bingo`: Filtra las figuras detectadas comprobando si pertenecen al conjunto `modalidades_permitidas` del modo de dificultad actual.

---

#### 🏛️ Pilares de la POO en `Carton` y Evidencia en el Código:
* **Abstracción:**  
  *Evidencia:* Toda la matemática matricial de 25 casillas y las 14 combinaciones geométricas quedan abstraídas. La aplicación gráfica simplemente consulta `carton.validar_bingo(modalidades)`.
* **Encapsulamiento:**  
  *Evidencia:* `marcar_manualmente()` valida que el elemento esté en `ids_extraidos` antes de modificar `self.marcados[fila][col]`.
* **Polimorfismo Reflexivo:**  
  *Evidencia:* `metodo = getattr(self, f"forma_{i}")` invoca uniformemente cualquiera de los métodos `forma_1` a `forma_13` bajo la misma firma.

---

### 3.5. Clase `SistemaRecompensas`
Gestiona la economía del juego y el refuerzo cognitivo positivo.

#### A. Constructor `__init__`
```python
    def __init__(self, estrellas_iniciales=100):
        self.estrellas_totales = estrellas_iniciales
        self.estrellas_sesion_actual = 0
        self.fichas_enfoque = 10
        self.aciertos_destreza = 0
```
**Explicación paso a paso:**
- Otorga 100 estrellas iniciales al jugador como saldo base.
- Inicia en 0 las estrellas y aciertos de la sesión actual.
- Fija el nivel base de fichas de enfoque en 10.

---

#### B. Métodos de Economía: `ajustar_enfoque`, `registrar_acierto_destreza` y `acreditar_premio_figura`
```python
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
```
**Explicación paso a paso:**
- `ajustar_enfoque`: Incrementa o disminuye las fichas de enfoque validando que el valor permanezca entre 5 y 50 (`if 5 <= nuevo <= 50`).
- `registrar_acierto_destreza`: Suma +1 a los aciertos y acredita +2 estrellas tanto al saldo total como al de la sesión.
- `acreditar_premio_figura`: Consulta la tabla de puntos base, aplica el multiplicador de enfoque, suma las estrellas y las retorna.
- `reiniciar_sesion`: Restablece los contadores de la sesión actual sin perder el acumulado histórico (`self.estrellas_totales`).

---

#### 🏛️ Pilares de la POO en `SistemaRecompensas`:
* **Encapsulamiento:**  
  *Evidencia:* La restricción `if 5 <= nuevo <= 50:` en `ajustar_enfoque()` protege el estado interno de valores ilegales.
* **Abstracción:**  
  *Evidencia:* Modela la economía del juego y el refuerzo cognitivo tras métodos simples como `registrar_acierto_destreza()`.

---

### 3.6. Clase `NivelEstimulacion`
Define los modos de juego adaptados a diferentes niveles cognitivos.

```python
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
```
**Explicación paso a paso:**
- `obtener_modalidades(cls, nivel)`: Método de clase que retorna el conjunto de modalidades válidas según el modo seleccionado (1: Tradicional, 2: Especial con 14 figuras, 3: Cartón Lleno).
- `obtener_nombre_modo(cls, nivel)`: Retorna el nombre representativo del modo para la interfaz gráfica.

#### 🏛️ Pilares de la POO:
* **Abstracción:** Centraliza la parametrización de reglas en una clase unificada.

---

### 3.7. Clase `PartidaBingoCognitivo`
Controlador maestro que orquesta la partida integrando el bolillero, los cartones y las recompensas.

#### A. Constructor `__init__`
```python
    def __init__(self, nivel_inicial=1):
        self.nivel = nivel_inicial
        self.bolillero = Bolillero(max_bolas_regular=40)
        self.cartones = []
        self.recompensas = SistemaRecompensas(estrellas_iniciales=100)
        self.estado = self.ESTADO_CONFIGURACION
        self.juego_activo = False
        self.ultimo_logro = None
```
**Explicación paso a paso:**
- Fija el nivel de juego.
- Instancia los subsistemas colaboradores: `Bolillero` y `SistemaRecompensas`.
- Inicializa la lista de cartones vacía y el estado en `"CONFIGURACION"`.

---

#### B. Gestión de Cartones y Sorteo: `agregar_carton`, `iniciar_sorteo` y `extraer_siguiente_elemento`
```python
    def agregar_carton(self):
        if len(self.cartones) < 4:
            nuevo = Carton(posicion_id=len(self.cartones), catalogo_ref=self.bolillero.catalogo)
            self.cartones.append(nuevo)
            return nuevo
        return None

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
        elemento = self.bolillero.sacar_bola()
        if not elemento or self.bolillero.fase_regular_completa:
            self.estado = self.ESTADO_FINALIZADO
            self.juego_activo = False
        return elemento
```
**Explicación paso a paso:**
- `agregar_carton`: Crea una nueva instancia de `Carton` y la añade a `self.cartones` (hasta un máximo de 4).
- `iniciar_sorteo`: Valida la existencia de cartones, activa la bandera `self.juego_activo = True` y cambia el estado a `"EXTRACCION_REGULAR"`.
- `extraer_siguiente_elemento`: Pide una nueva balota al bolillero; si se vacía o se alcanza el límite regular de 40 balotas, finaliza la partida.

---

#### C. Interacción del Usuario: `marcar_casilla_por_usuario`
```python
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
```
**Explicación paso a paso:**
- Valida el índice del cartón.
- Delega el marcado al cartón correspondiente mediante `carton.marcar_manualmente()`.
- Si se produce un acierto:
  - Otorga puntos de destreza con `self.recompensas.registrar_acierto_destreza()`.
  - Obtiene las modalidades válidas para el nivel actual.
  - Comprueba si se completó una figura con `carton.validar_bingo()`.
  - Si hay figura (o Bingo Pleno), calcula las estrellas y estructura el diccionario `info_logro` para que la interfaz gráfica despliegue el modal de felicitación.

---

#### 🏛️ Pilares de la POO en `PartidaBingoCognitivo`:
* **Abstracción (Patrón Fachada):**  
  *Evidencia:* La GUI no interactúa directamente con el bolillero ni con los cartones de forma aislada; se comunica exclusivamente con `PartidaBingoCognitivo`.
* **Composición:**  
  *Evidencia:* La clase contiene y coordina instancias de `Bolillero`, `Carton` y `SistemaRecompensas`.

---

## 4. Módulo 2: `recursos.py` (Multimedia, Gráficos y Audio)

---

### 4.1. Clase `Configuracion`
```python
class Configuracion:
    BASE_DIR = Path(__file__).resolve().parent
    ASSETS_DIR = BASE_DIR / "assets"
    ANCHO_VENTANA = 1280
    ALTO_VENTANA = 720
    ESTADO_INICIO = "INICIO"
    ESTADO_SELECCION = "SELECCION"
    ESTADO_JUEGO = "JUEGO"
    COLOR_TEXTO_NAVY = (23, 48, 63)
    COLOR_FONDO_BASE = (211, 229, 241)
    COLOR_TEAL_BOTON = (47, 168, 155)
    # ...
```
**Explicación paso a paso:**
- Centraliza constantes de resolución (1280x720), estados del juego y paletas cromáticas accesibles en tonos menta, lavanda y azul marino.

#### 🏛️ Pilares de la POO:
* **Abstracción:** Centraliza valores numéricos y colores en una sola entidad.

---

### 4.2. Clase `Fuentes`
```python
class Fuentes:
    @classmethod
    def _cargar_fuente(cls, tamano, negrita=False):
        familias = ["Segoe UI", "Plus Jakarta Sans", "Arial", "Calibri"]
        for familia in familias:
            try:
                f = pygame.font.SysFont(familia, tamano, bold=negrita)
                if f:
                    return f
            except Exception:
                continue
        return pygame.font.Font(None, tamano)

    @classmethod
    def init(cls):
        cls.titulo_inicio = cls._cargar_fuente(46, negrita=True)
        cls.subtitulo_inicio = cls._cargar_fuente(22, negrita=True)
        # ...
```
**Explicación paso a paso:**
- `_cargar_fuente`: Prueba secuencialmente tipografías de alta legibilidad instaladas en el sistema operativo (*Segoe UI*, *Arial*). Si no encuentra ninguna, recurre a la fuente interna de Pygame para evitar caídas del programa.
- `init`: Carga en memoria todos los tamaños tipográficos de la interfaz.

---

### 4.3. Clase `GestorMusica`
```python
class GestorMusica:
    PISTA_MENU = ASSETS_DIR / "musica" / "Blossom.ogg"
    PISTA_JUEGO = ASSETS_DIR / "musica" / "melancholy.ogg"
    pista_actual = None

    @classmethod
    def reproducir_menu(cls):
        if cls.pista_actual == cls.PISTA_MENU:
            return
        if cls.PISTA_MENU.exists():
            try:
                pygame.mixer.music.fadeout(350)
                pygame.mixer.music.load(str(cls.PISTA_MENU))
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
                cls.pista_actual = cls.PISTA_MENU
            except Exception:
                pass

    @classmethod
    def reproducir_juego(cls):
        if cls.pista_actual == cls.PISTA_JUEGO:
            return
        if cls.PISTA_JUEGO.exists():
            try:
                pygame.mixer.music.fadeout(350)
                pygame.mixer.music.load(str(cls.PISTA_JUEGO))
                pygame.mixer.music.set_volume(0.30)
                pygame.mixer.music.play(-1)
                cls.pista_actual = cls.PISTA_JUEGO
            except Exception:
                pass
```
**Explicación paso a paso:**
- `reproducir_menu`: Realiza una transición suave (`fadeout(350)`), carga la pista relajante `"Blossom.ogg"`, fija el volumen al 35% y la reproduce en bucle continuo.
- `reproducir_juego`: Cambia suavemente a la pista `"melancholy.ogg"` al 30% de volumen para optimizar la concentración del jugador.

#### 🏛️ Pilares de la POO:
* **Encapsulamiento:** La variable `pista_actual` impide recargar innecesariamente la canción que ya está sonando.
* **Abstracción:** Oculta la manipulación de canales de audio de Pygame tras dos llamadas simples.

---

### 4.4. Clase `GestorAssets` y `inicializar_sistema_recursos`

```python
    @staticmethod
    def limpiar_halo(surf, umbral=45):
        s = surf.copy()
        try:
            import numpy as np
            alpha = pygame.surfarray.pixels_alpha(s)
            alpha[alpha < umbral] = 0
            del alpha
        except Exception:
            w, h = s.get_size()
            for y in range(h):
                for x in range(w):
                    if s.get_at((x, y))[3] < umbral:
                        s.set_at((x, y), (0, 0, 0, 0))
        return s
```
**Explicación paso a paso:**
- `limpiar_halo`: Algoritmo de procesamiento de imágenes que elimina halos blancos o bordes imperfectos en las texturas recortadas manipulando el canal alfa con NumPy.

```python
    @classmethod
    def extraer_iconos_spritesheets(cls, carpeta_bingo=None):
        # Lee B.png, I.png, N.png, G.png, O.png (hojas 3x5)
        # Recorta las 15 figuras por hoja, elimina espacios vacíos y escala a 44x44 px.
        # Retorna el diccionario de 75 iconos indexados por ID.
```
**Explicación paso a paso:**
- Recorta las hojas maestras de 3 filas x 5 columnas, generando los 75 iconos temáticos escalados uniformemente.

---

## 5. Módulo 3: `main.py` (Interfaz Gráfica e Interacción)

---

### 5.1. Clase `BotonCalma`

#### A. Constructor `__init__`
```python
    def __init__(self, rect, pre_dibujado=False, radio=16, circular=False):
        self.rect = rect
        self.pre_dibujado = pre_dibujado
        self.radio = radio
        self.circular = circular
        self.hovered = False
```
**Explicación paso a paso:**
- Guarda el rectángulo geométrico (`pygame.Rect`).
- Registra el estilo visual (radio de esquinas redondeadas o si es circular).
- Inicializa el estado `self.hovered = False`.

---

#### B. Métodos de Actualización y Dibujo: `actualizar`, `dibujar_hover` y `es_clickeado`
```python
    def actualizar(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def dibujar_hover(self, superficie, alpha_halo=40, border_halo=160):
        if not self.hovered:
            return
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        if self.circular:
            cx = self.rect.width // 2
            cy = self.rect.height // 2
            r = self.rect.width // 2
            pygame.draw.circle(overlay, (255, 255, 255, alpha_halo), (cx, cy), r)
            pygame.draw.circle(overlay, (255, 255, 255, border_halo), (cx, cy), r, width=3)
        else:
            pygame.draw.rect(overlay, (255, 255, 255, alpha_halo), (0, 0, self.rect.width, self.rect.height), border_radius=self.radio)
            pygame.draw.rect(overlay, (255, 255, 255, border_halo), (0, 0, self.rect.width, self.rect.height), width=3, border_radius=self.radio)
        superficie.blit(overlay, self.rect.topleft)

    def es_clickeado(self, evento):
        return evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.rect.collidepoint(evento.pos)
```
**Explicación paso a paso:**
- `actualizar`: Evalúa si el cursor colisiona con el botón (`collidepoint`) y actualiza `self.hovered`.
- `dibujar_hover`: Dibuja un resplandor translúcido suave sobre el botón cuando el ratón pasa por encima.
- `es_clickeado`: Retorna `True` si se produjo un evento de clic izquierdo dentro de las coordenadas del botón.

---

### 5.2. Clase `TableroCartonGUI`

#### A. Algoritmo Tipográfico `dividir_texto_en_lineas`
```python
    @staticmethod
    def dividir_texto_en_lineas(texto, fuente, max_ancho=72):
        if fuente.size(texto)[0] <= max_ancho:
            return [texto]
        palabras = texto.split()
        if len(palabras) <= 1:
            return [texto]
        elif len(palabras) == 2:
            return palabras
        else:
            mejor_div = [palabras[0], " ".join(palabras[1:])]
            mejor_max = max(fuente.size(mejor_div[0])[0], fuente.size(mejor_div[1])[0])
            for i in range(1, len(palabras)):
                l1 = " ".join(palabras[:i])
                l2 = " ".join(palabras[i:])
                mw = max(fuente.size(l1)[0], fuente.size(l2)[0])
                if mw < mejor_max:
                    mejor_max = mw
                    mejor_div = [l1, l2]
            return mejor_div
```
**Explicación paso a paso:**
- Mide el ancho del texto con la fuente. Si excede 72 px, busca la partición en dos líneas más equilibrada para que el texto nunca desborde la casilla.

---

#### B. Métodos de Conversión y Renderizado: `obtener_celda_en_pos` y `dibujar`
```python
    def obtener_celda_en_pos(self, mouse_pos):
        mx, my = mouse_pos
        for f in range(5):
            for c in range(5):
                cx = self.x + self.INICIO_X + c * (self.ANCHO_CELDA + self.ESPACIO_X)
                cy = self.y + self.INICIO_Y + f * (self.ALTO_CELDA + self.ESPACIO_Y)
                if cx <= mx < cx + self.ANCHO_CELDA and cy <= my < cy + self.ALTO_CELDA:
                    return f, c
        return None
```
**Explicación paso a paso:**
- Traduce las coordenadas en píxeles del cursor `(mx, my)` a la coordenada matemática `(fila, columna)` de la cuadrícula de 5x5.

```python
    def dibujar(self, superficie, mouse_pos, elemento_actual_id):
        # 1. Dibuja textura del tablero de madera.
        # 2. Dibuja el badge con información de aciertos.
        # 3. Recorre las casillas dibujando iconos temáticos, nombres y fichas marcadas.
```
**Explicación paso a paso:**
- Renderiza el tablero, destaca la casilla coincidente con la balota actual y dibuja las fichas colocadas sobre las casillas acertadas.

---

### 5.3. Clase `BingoCalmaApp`

#### A. Constructor `__init__` e Inicio de Partida `_iniciar_partida`
```python
    def __init__(self):
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Bingo Calma - Estimulación Cognitiva y Sensorial")
        inicializar_sistema_recursos()
        self.reloj = pygame.time.Clock()
        self.estado = ESTADO_INICIO
        self.modo_seleccionado = 1
        # ... inicializa botones BotonCalma ...
        GestorMusica.reproducir_menu()
        self._iniciar_partida(self.modo_seleccionado)
```
**Explicación paso a paso:**
- Crea la ventana de 1280x720, inicializa el reloj a 60 FPS, configura los botones de la GUI y arranca la música de menú.

```python
    def _iniciar_partida(self, modo):
        random.seed()
        self.modo_seleccionado = modo
        self.partida = PartidaBingoCognitivo(nivel_inicial=modo)
        self.partida.agregar_carton()
        self.partida.agregar_carton()
        self.partida.iniciar_sorteo()
        self.tableros_gui = [
            TableroCartonGUI(250, 100, self.partida.cartones[0], 0),
            TableroCartonGUI(754, 100, self.partida.cartones[1], 1)
        ]
        self.elemento_actual = self.partida.extraer_siguiente_elemento()
        self.juego_pausado = False
        self.modal_logro = None
```
**Explicación paso a paso:**
- Instancia una nueva `PartidaBingoCognitivo`, crea dos cartones lógicos y sus respectivos tableros visuales `TableroCartonGUI`, y extrae la primera balota.

---

#### B. Bucle Principal del Videojuego: `ejecutar`
```python
    def ejecutar(self):
        corriendo = True
        while corriendo:
            self.reloj.tick(60)
            self.ticks_anim += 1
            mouse_pos = pygame.mouse.get_pos()
            self._actualizar_hover_botones(mouse_pos)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    if self.modal_como_jugar:
                        self.modal_como_jugar = False
                    else:
                        corriendo = False
                self._manejar_eventos(evento)

            self._dibujar(mouse_pos)
            pygame.display.flip()

        pygame.quit()
        sys.exit()
```
**Explicación paso a paso:**
- Mantiene el juego a 60 FPS fijos.
- Procesa eventos del sistema operativo (cerrar ventana o tecla ESC).
- Actualiza el estado visual de los botones.
- Dibuja la escena completa y actualiza la pantalla mediante doble búfer con `pygame.display.flip()`.

---

#### C. Conexión de Clics con la Lógica: `_procesar_clic_celdas`
```python
    def _procesar_clic_celdas(self, pos):
        for idx, tab_gui in enumerate(self.tableros_gui):
            celda = tab_gui.obtener_celda_en_pos(pos)
            if celda:
                fila, col = celda
                acierto, elem, cod, logro = self.partida.marcar_casilla_por_usuario(idx, fila, col)
                if logro:
                    self.modal_logro = logro
```
**Explicación paso a paso:**
- Identifica qué casilla tocó el jugador en la GUI.
- Envía las coordenadas `(fila, columna)` a `self.partida.marcar_casilla_por_usuario()`.
- Si se completó una figura, activa el modal de logro para desplegar la pantalla de felicitación.

---

## 6. Resumen Comparativo de Pilares por Clase

| Módulo | Clase | Pilar Principal | Evidencia Exacta en el Código |
| :--- | :--- | :--- | :--- |
| `logica.py` | `ElementoTematico` | **Encapsulamiento** | En `_columna_letra(item_id)` que calcula la letra internamente, y en `marcar_sacada()` y `reiniciar()` que controlan `self.sacada`. |
| `logica.py` | `Bolillero` | **Abstracción** | En `sacar_bola()`, que oculta la remoción aleatoria y el historial. En `@property total_extraidas` (encapsulamiento). |
| `logica.py` | `Carton` | **Abstracción y Encapsulamiento** | En `marcar_manualmente()`, que valida que la balota realmente haya salido antes de alterar `self.marcados[f][c]`. |
| `logica.py` | `SistemaRecompensas`| **Encapsulamiento** | En `ajustar_enfoque(delta)`, que restringe las fichas a `5 <= nuevo <= 50`. |
| `logica.py` | `NivelEstimulacion`  | **Abstracción** | En `obtener_modalidades(cls, nivel)`, que centraliza los conjuntos de reglas sin ensuciar la lógica con condiciones repetidas. |
| `logica.py` | `PartidaBingoCognitivo` | **Composición y Abstracción** | En `__init__`, donde compone instancias de `Bolillero`, `Carton` y `SistemaRecompensas`. Sirve de fachada unificada hacia la GUI. |
| `recursos.py`| `GestorMusica` | **Encapsulamiento y Abstracción** | En `pista_actual`, que evita recargar la música innecesariamente, y en los métodos `reproducir_menu()` y `reproducir_juego()`. |
| `recursos.py`| `GestorAssets` | **Abstracción** | En `extraer_iconos_spritesheets()`, que convierte cuadrículas de imágenes crudas en iconos limpios escalados por ID numérico. |
| `main.py` | `BotonCalma` | **Composición y Abstracción** | Utiliza `pygame.Rect` para colisiones y provee el método `es_clickeado(evento)`, abstrayendo la detección de clics del ratón. |
| `main.py` | `TableroCartonGUI` | **Separación de Responsabilidades** | Separa el modelo de datos (`Carton`) de su renderizado visual, traduciendo píxeles a casillas con `obtener_celda_en_pos()`. |
| `main.py` | `BingoCalmaApp` | **Abstracción de Alto Nivel** | En `ejecutar()`, que encapsula todo el ciclo de vida del juego a 60 FPS, coordinando eventos, actualización de estado y renderizado. |

---

## 7. Apéndice Técnico: ¿Cómo Quedaría el Código Sin Usar Decoradores?

Los decoradores en Python (como `@property`, `@classmethod` y `@staticmethod`) son atajos de sintaxis. El programa puede reescribirse sin ellos aplicando el estilo clásico de la POO:

### 7.1. Reemplazando `@property` en `Bolillero`
```python
# CON DECORADOR:
@property
def total_extraidas(self):
    return len(self.historial_extraidas)

# SIN DECORADOR (Método Getter tradicional):
def obtener_total_extraidas(self):
    return len(self.historial_extraidas)

# Invocación en el juego:
# Antes: print(bolillero.total_extraidas)
# Ahora: print(bolillero.obtener_total_extraidas())
```

### 7.2. Reemplazando `@classmethod` en `NivelEstimulacion`
```python
# CON DECORADOR:
@classmethod
def obtener_modalidades(cls, nivel):
    return cls.MODO_TRADICIONAL if nivel == 1 else cls.MODO_ESPECIAL

# SIN DECORADOR (Acceso directo por nombre de clase):
def obtener_modalidades(nivel):
    return NivelEstimulacion.MODO_TRADICIONAL if nivel == 1 else NivelEstimulacion.MODO_ESPECIAL
```

### 7.3. Reemplazando `@staticmethod` en `ElementoTematico`
```python
# CON DECORADOR:
@staticmethod
def _columna_letra(item_id):
    return "B" if item_id <= 15 else "I"

# SIN DECORADOR (Método de instancia estándar con self):
def _columna_letra(self, item_id):
    return "B" if item_id <= 15 else "I"
```

---
*Manual integral elaborado con el código fuente y especificaciones del Taller de Abstracción y Programación Orientada a Objetos.*
