# 🖥️ Manual Maestro de `main.py`: Arquitectura GUI, Pilares de la POO y Explicación Exhaustiva Método por Método
## Proyecto: *Bingo Calma — Estimulación Cognitiva y Sensorial*

> **Objetivo de este documento:**  
> Analizar en profundidad y de forma 100% didáctica el archivo [`main.py`](file:///d:/documentos/Proyecto%20taller%20de%20abstraccion%20eugenio/main.py), el cual constituye la **Capa de Presentación e Interacción Gráfica** del sistema. Se incluye el código fuente íntegro de cada método, su explicación paso a paso para personas sin conocimientos de programación, la demostración empírica de qué **pilar de la POO** se evidencia en cada clase y sección, y el análisis técnico de cómo quedaría el código sin usar decoradores.

---

## 📑 Tabla de Contenidos

1. [El Rol de `main.py` en la Arquitectura en 3 Capas](#1-el-rol-de-mainpy-en-la-arquitectura-en-3-capas)
2. [Los 4 Pilares de la POO Aplicados a la Interfaz Gráfica](#2-los-4-pilares-de-la-poo-aplicados-a-la-interfaz-gráfica)
3. [Patrones de Diseño Implementados en `main.py`](#3-patrones-de-diseño-implementados-en-mainpy)
4. [Análisis Exhaustivo del Código: Método por Método](#4-análisis-exhaustivo-del-código-método-por-método)
   - 4.1. [Importaciones e Inicialización](#41-importaciones-e-inicialización)
   - 4.2. [Clase `BotonCalma` (Componente de Interacción)](#42-clase-botoncalma)
   - 4.3. [Clase `TableroCartonGUI` (Representación Visual del Cartón)](#43-clase-tablerocartongui)
   - 4.4. [Clase `BingoCalmaApp` (Orquestador y Bucle del Juego)](#44-clase-bingocalmaapp)
   - 4.5. [Bloque de Entrada Principal `if __name__ == '__main__':`](#45-bloque-de-entrada-principal)
5. [Apéndice: ¿Cómo Quedaría `main.py` Sin Decoradores?](#5-apéndice-cómo-quedaría-mainpy-sin-decoradores)
6. [Tabla Síntesis de Pilares y Evidencias en `main.py`](#6-tabla-síntesis-de-pilares-y-evidencias-en-mainpy)

---

## 1. El Rol de `main.py` en la Arquitectura en 3 Capas

En el desarrollo de software profesional moderno, se utiliza la separación de responsabilidades en capas:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. CAPA DE PRESENTACIÓN (main.py)                           │
│    - Dibuja en pantalla (Pygame: 1280x720 a 60 FPS)         │
│    - Captura el ratón y teclado                             │
│    - Traduce clics a órdenes lógicas                        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Habla con
                               ▼
┌──────────────────────────────┴──────────────────────────────┐
│ 2. CAPA DE RECURSOS (recursos.py)                           │
│    - Fuentes legibles, música ambiental relajante           │
│    - Recorte de spritesheets de 75 recuerdos temáticos      │
└──────────────────────────────┬──────────────────────────────┘
                               │ Alimenta a
                               ▼
┌──────────────────────────────┴──────────────────────────────┐
│ 3. CAPA DE LÓGICA Y DOMINIO (logica.py)                     │
│    - Bolillero, Cartones de 5x5, 14 Figuras y Estrellas     │
│    - No sabe qué es un píxel; calcula reglas puras          │
└─────────────────────────────────────────────────────────────┘
```

[`main.py`](file:///d:/documentos/Proyecto%20taller%20de%20abstraccion%20eugenio/main.py) tiene una única misión: **ser los ojos, oídos y manos del jugador**, mostrando la información de forma hermosa y no estresante, y enviando las acciones del usuario a la capa de lógica.

---

## 2. Los 4 Pilares de la POO Aplicados a la Interfaz Gráfica

### A. Abstracción
* **Concepto:** No abrumar al programador ni al usuario con detalles de hardware, frecuencias de refresco o matemáticas de píxeles.
* **En `main.py`:** Cuando el usuario hace clic en el cartón, no calculamos manualmente fórmulas de trigonometría ni vectores; invocamos `tablero_gui.obtener_celda_en_pos(pos)` y este nos abstrae el cálculo devolviendo limpiamente `(fila, columna)`. Cuando queremos saber si se pulsó un botón, llamamos a `boton.es_clickeado(evento)`.

### B. Encapsulamiento
* **Concepto:** Proteger las variables visuales y de estado para que no puedan ser alteradas de forma arbitraria o inconsistente.
* **En `main.py`:** Variables como `self.hovered` en `BotonCalma` solo cambian a través del método `actualizar(mouse_pos)`. En `BingoCalmaApp`, los estados del juego (`INICIO`, `SELECCION`, `JUEGO`) y las banderas de modales (`modal_como_jugar`, `modal_logro`) están encapsulados dentro de la clase principal, garantizando que nunca se dibuje una pantalla incorrecta.

### C. Herencia y Composición
* **Concepto:** En lugar de reescribir código para rectángulos y áreas de pantalla, se componen estructuras geométricas probadas de Pygame (`pygame.Rect`).
* **En `main.py`:**
  - `BotonCalma` compone un objeto `self.rect = rect`, heredando todas las funciones matemáticas de colisión de Pygame (`collidepoint`).
  - `TableroCartonGUI` utiliza composición al recibir y almacenar un objeto lógico `self.carton = carton`.

### D. Polimorfismo
* **Concepto:** Múltiples objetos responden a la misma orden con su propio comportamiento especializado.
* **En `main.py`:**
  - Todos los botones interactivos (rectangulares, circulares, con imagen pre-dibujada o sin ella) implementan la misma firma: `actualizar(mouse_pos)` y `dibujar_hover()`.
  - El sistema de dibujo invoca polimórficamente `_dibujar(mouse_pos)` y este delega en la función correspondiente según el estado actual de la máquina de estados.

---

## 3. Patrones de Diseño Implementados en `main.py`

1. **Bucle de Juego (*Game Loop Pattern*):**  
   Implementado en `BingoCalmaApp.ejecutar()`. Ejecuta a 60 ciclos por segundo las fases de:
   `Entrada de Eventos` $\rightarrow$ `Actualización de Estado` $\rightarrow$ `Dibujo en Pantalla (Render)` $\rightarrow$ `Refresco (Display Flip)`.
2. **Máquina de Estados Finita (*State Machine Pattern*):**  
   Controla el flujo de pantallas mediante `self.estado` con tres estados formales:
   - `ESTADO_INICIO`: Portada de bienvenida y guía "¿Cómo Jugar?".
   - `ESTADO_SELECCION`: Tarjetas de elección de partida (Corta, Media, Completa).
   - `ESTADO_JUEGO`: Tablero activo con balotas y cartones.
3. **Componente Visual / Widget Pattern:**  
   `BotonCalma` y `TableroCartonGUI` actúan como componentes visuales autónomos y reutilizables.

---

## 4. Análisis Exhaustivo del Código: Método por Método

---

### 4.1. Importaciones e Inicialización

```python
import sys
import random
import pygame
from logica import PartidaBingoCognitivo, Carton, ElementoTematico, NivelEstimulacion
from recursos import (
    BASE_DIR, ASSETS_DIR, ANCHO_VENTANA, ALTO_VENTANA,
    ESTADO_INICIO, ESTADO_SELECCION, ESTADO_JUEGO,
    COLOR_TEXTO_NAVY, COLOR_TEXTO_NAVY_DARK, COLOR_TEXTO_MUTED,
    COLOR_FONDO_BASE, COLOR_TEAL_BOTON, COLOR_TEAL_BORDE,
    COLOR_MENTA_ACTIVA, COLOR_LAVANDA_MARCADO, COLOR_AZUL_MARCADO_ICON,
    COLOR_BLANCO, COLOR_AMBAR_PAUSA, NOMBRES_COLUMNAS,
    Fuentes, GestorMusica, GestorAssets, inicializar_sistema_recursos
)
```

#### Explicación para Principiantes:
- `import sys`: Permite cerrar el programa de forma limpia y segura (`sys.exit()`).
- `import random`: Para generar semillas aleatorias en cada nueva partida.
- `import pygame`: La biblioteca multimedia para crear ventanas, leer ratón y dibujar gráficos.
- `from logica import ...`: Trae las reglas de negocio del bingo (bolillero, cartón, figuras).
- `from recursos import ...`: Trae las dimensiones (1280x720), los colores relajantes, las fuentes y los gestores de assets y música.

---

### 4.2. Clase `BotonCalma`

Es el componente que convierte cualquier rectángulo de la pantalla en un botón interactivo suave con respuesta al pasar el ratón (*hover*).

```python
class BotonCalma:
    def __init__(self, rect, pre_dibujado=False, radio=16, circular=False):
        self.rect = rect
        self.pre_dibujado = pre_dibujado
        self.radio = radio
        self.circular = circular
        self.hovered = False

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

#### Explicación de Métodos Paso a Paso:

1. **`__init__(self, rect, pre_dibujado=False, radio=16, circular=False)`**:
   - **Propósito:** Constructor de la clase.
   - **Qué hace:** Recibe un rectángulo geométrico (`pygame.Rect`), guarda si el botón ya tiene una imagen dibujada debajo (`pre_dibujado`), qué curvatura tienen sus esquinas (`radio`) y si es un botón redondo (`circular`). Establece `self.hovered = False` porque al crearse el cursor aún no está sobre él.
2. **`actualizar(self, mouse_pos)`**:
   - **Propósito:** Comprobar la presencia del cursor.
   - **Qué hace:** Utiliza el método geométrico `self.rect.collidepoint(mouse_pos)` de Pygame. Si las coordenadas del ratón `(x, y)` caen dentro del botón, pone `self.hovered = True`; si no, `False`.
3. **`dibujar_hover(self, superficie, alpha_halo=40, border_halo=160)`**:
   - **Propósito:** Brindar retroalimentación sensorial suave (esencial en estimulación cognitiva).
   - **Qué hace:** Si `self.hovered` es `False`, no hace nada y termina de inmediato (`return`). Si es `True`, crea una superficie semitransparente (`SRCALPHA`), dibuja un resplandor blanco muy suave (opacidad 40) y un borde blanco definido (opacidad 160) adaptándose a su forma (círculo o rectángulo redondeado), y lo estampa en pantalla con `blit()`.
4. **`es_clickeado(self, evento)`**:
   - **Propósito:** Detectar una pulsación válida.
   - **Qué hace:** Evalúa 3 condiciones simultáneas:
     1. `evento.type == pygame.MOUSEBUTTONDOWN`: El usuario presionó el ratón.
     2. `evento.button == 1`: Fue el botón izquierdo del ratón (no el derecho ni la rueda).
     3. `self.rect.collidepoint(evento.pos)`: La flecha del ratón estaba dentro del botón al hacer clic.
     - Devuelve `True` si se cumplen las 3; de lo contrario, devuelve `False`.

#### 🏛️ Pilares de la POO en `BotonCalma` y Evidencia en el Código:
* **Abstracción:**
  - *Evidencia:* Toda la detección matemática de contacto y eventos de ratón queda oculta tras `boton.es_clickeado(evento)`. Quien programa la interfaz no necesita recordar códigos numéricos de botones de hardware.
* **Encapsulamiento:**
  - *Evidencia:* El estado visual `self.hovered` reside dentro del botón y solo se modifica mediante la llamada oficial `actualizar(mouse_pos)`.
* **Composición:**
  - *Evidencia:* En la línea `self.rect = rect`: compone un objeto `pygame.Rect` dentro de sí para reutilizar sus capacidades de colisión.

---

### 4.3. Clase `TableroCartonGUI`

Dibuja un cartón de bingo en pantalla y traduce los píxeles del ratón a coordenadas matemáticas de cuadrícula `(fila, columna)`.

```python
class TableroCartonGUI:
    ANCHO = 474
    ALTO = 558
    ANCHO_CELDA = 80
    ALTO_CELDA = 80
    INICIO_X = 20
    INICIO_Y = 98
    ESPACIO_X = 10
    ESPACIO_Y = 10

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

    def __init__(self, x, y, carton, indice):
        self.x = x
        self.y = y
        self.carton = carton
        self.indice = indice
        self.rect = pygame.Rect(x, y, self.ANCHO, self.ALTO)

    def obtener_celda_en_pos(self, mouse_pos):
        mx, my = mouse_pos
        for f in range(5):
            for c in range(5):
                cx = self.x + self.INICIO_X + c * (self.ANCHO_CELDA + self.ESPACIO_X)
                cy = self.y + self.INICIO_Y + f * (self.ALTO_CELDA + self.ESPACIO_Y)
                if cx <= mx < cx + self.ANCHO_CELDA and cy <= my < cy + self.ALTO_CELDA:
                    return f, c
        return None

    def contar_aciertos(self):
        return sum(1 for f in range(5) for c in range(5) if self.carton.esta_marcado(f, c))

    def dibujar(self, superficie, mouse_pos, elemento_actual_id):
        superficie.blit(GestorAssets.tablero, (self.x, self.y))

        aciertos = self.contar_aciertos()
        badge_w, badge_h = 136, 26
        badge_x = self.x + self.ANCHO - badge_w - 20
        badge_y = self.y + 16

        pygame.draw.rect(superficie, (255, 255, 255, 220), (badge_x, badge_y, badge_w, badge_h), border_radius=13)
        pygame.draw.rect(superficie, (111, 211, 191, 180), (badge_x, badge_y, badge_w, badge_h), width=1, border_radius=13)

        txt_carton_info = f"Cartón {self.indice + 1}  •  {aciertos} Ac."
        t_badge = Fuentes.subtitulo.render(txt_carton_info, True, COLOR_TEXTO_NAVY)
        superficie.blit(t_badge, t_badge.get_rect(center=(badge_x + badge_w // 2, badge_y + badge_h // 2)))

        celda_hover = self.obtener_celda_en_pos(mouse_pos)

        for fila in range(5):
            for col in range(5):
                cx = self.x + self.INICIO_X + col * (self.ANCHO_CELDA + self.ESPACIO_X)
                cy = self.y + self.INICIO_Y + fila * (self.ALTO_CELDA + self.ESPACIO_Y)

                if fila == 2 and col == 2:
                    continue

                esta_marcada = self.carton.esta_marcado(fila, col)
                elem = self.carton.obtener_elemento_en(fila, col)
                if not elem:
                    continue

                es_objetivo = (elemento_actual_id is not None and elem.id == elemento_actual_id and not esta_marcada)
                hover_activo = (celda_hover == (fila, col) and not esta_marcada)

                if esta_marcada:
                    superficie.blit(GestorAssets.recuadro_seleccion, (cx, cy))
                elif es_objetivo:
                    s_pulse = pygame.Surface((self.ANCHO_CELDA, self.ALTO_CELDA), pygame.SRCALPHA)
                    pygame.draw.rect(s_pulse, (47, 168, 155, 45), (0, 0, self.ANCHO_CELDA, self.ALTO_CELDA), border_radius=12)
                    pygame.draw.rect(s_pulse, COLOR_TEAL_BORDE, (0, 0, self.ANCHO_CELDA, self.ALTO_CELDA), width=2, border_radius=12)
                    superficie.blit(s_pulse, (cx, cy))
                elif hover_activo:
                    s_hover = pygame.Surface((self.ANCHO_CELDA, self.ALTO_CELDA), pygame.SRCALPHA)
                    pygame.draw.rect(s_hover, (255, 255, 255, 55), (0, 0, self.ANCHO_CELDA, self.ALTO_CELDA), border_radius=12)
                    pygame.draw.rect(s_hover, (255, 255, 255, 120), (0, 0, self.ANCHO_CELDA, self.ALTO_CELDA), width=1, border_radius=12)
                    superficie.blit(s_hover, (cx, cy))

                if elem.id in GestorAssets.iconos_elementos:
                    img_ico = GestorAssets.iconos_elementos[elem.id]
                    rect_ico = img_ico.get_rect(center=(cx + self.ANCHO_CELDA // 2, cy + 25))
                    superficie.blit(img_ico, rect_ico)

                color_nom = COLOR_AZUL_MARCADO_ICON if esta_marcada else COLOR_TEXTO_NAVY
                lineas_nom = self.dividir_texto_en_lineas(elem.nombre, Fuentes.celda_nombre, max_ancho=72)

                if len(lineas_nom) == 1:
                    t_nombre = Fuentes.celda_nombre.render(lineas_nom[0], True, color_nom)
                    rect_nom = t_nombre.get_rect(center=(cx + self.ANCHO_CELDA // 2, cy + 62))
                    superficie.blit(t_nombre, rect_nom)
                else:
                    t_l1 = Fuentes.celda_nombre.render(lineas_nom[0], True, color_nom)
                    t_l2 = Fuentes.celda_nombre.render(lineas_nom[1], True, color_nom)
                    rect_l1 = t_l1.get_rect(center=(cx + self.ANCHO_CELDA // 2, cy + 54))
                    rect_l2 = t_l2.get_rect(center=(cx + self.ANCHO_CELDA // 2, cy + 67))
                    superficie.blit(t_l1, rect_l1)
                    superficie.blit(t_l2, rect_l2)
```

#### Explicación de Métodos Paso a Paso:

1. **`dividir_texto_en_lineas(texto, fuente, max_ancho=72)`**:
   - **Propósito:** Algoritmo tipográfico para que los nombres de los recuerdos nunca se salgan de las casillas de 80x80 píxeles.
   - **Qué hace:** Mide el texto con `fuente.size(texto)[0]`. Si cabe en una sola línea, devuelve `[texto]`. Si no cabe, prueba partir las palabras en dos renglones y busca la combinación más equilibrada visualmente para que ambos renglones se vean armónicos.
2. **`__init__(self, x, y, carton, indice)`**:
   - **Propósito:** Crear la vista visual del cartón.
   - **Qué hace:** Guarda la posición en la ventana `(x, y)`, el número de cartón (`indice`), y guarda la referencia al objeto lógico `Carton` (`self.carton = carton`).
3. **`obtener_celda_en_pos(self, mouse_pos)`**:
   - **Propósito:** Conversión matemática de píxeles a filas y columnas.
   - **Qué hace:** Hace un doble bucle de 5 filas por 5 columnas. Calcula el rectángulo de cada casilla sumando el ancho de celda (80 px) y el espacio de separación (10 px). Si el ratón está adentro, devuelve `(fila, columna)`. Si el clic cayó fuera del cartón, devuelve `None`.
4. **`contar_aciertos(self)`**:
   - **Propósito:** Informar el progreso al jugador.
   - **Qué hace:** Pregunta a su objeto `self.carton` cuántas de sus 25 casillas están en `True`.
5. **`dibujar(self, superficie, mouse_pos, elemento_actual_id)`**:
   - **Propósito:** Pintar el cartón en pantalla.
   - **Qué hace:**
     - Dibuja la base de madera del tablero con `superficie.blit()`.
     - Dibuja la placa superior que dice *"Cartón 1 • X Ac."*.
     - Recorre las casillas saltándose el centro `[2][2]`.
     - Si la casilla está marcada: dibuja la ficha lavanda suave (`recuadro_seleccion`).
     - Si la casilla coincide con la balota que acaba de salir: dibuja un resplandor color verde menta para ayudar visualmente al jugador.
     - Si el jugador pasa el cursor por encima: dibuja un resplandor blanco suave.
     - Dibuja la ilustración temática centrada a 44x44 px y el nombre dividido en dos líneas.

#### 🏛️ Pilares de la POO en `TableroCartonGUI` y Evidencia en el Código:
* **Separación de Responsabilidades y Abstracción:**
  - *Evidencia:* `TableroCartonGUI` no calcula números aleatorios ni evalúa figuras ganadoras; de eso se encarga la clase `Carton`. La clase GUI abstrae toda la renderización de píxeles, fuentes y texturas.
* **Composición:**
  - *Evidencia:* En la línea `self.carton = carton`. El tablero visual está compuesto por una instancia de la clase de dominio `Carton`, consultando sus métodos `self.carton.esta_marcado(f, c)` y `self.carton.obtener_elemento_en(f, c)`.

---

### 4.4. Clase `BingoCalmaApp`

Es el **Director de Orquesta de toda la aplicación**. Coordina las pantallas, procesa los eventos y mantiene el ciclo de vida del juego a 60 cuadros por segundo.

```python
class BingoCalmaApp:
    def __init__(self):
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Bingo Calma - Estimulación Cognitiva y Sensorial")
        inicializar_sistema_recursos()
        self.reloj = pygame.time.Clock()

        self.estado = ESTADO_INICIO
        self.modo_seleccionado = 1
        self.modal_como_jugar = False
        self.modal_logro = None
        self.juego_pausado = False
        self.ticks_anim = 0

        self.btn_inicio_jugar = BotonCalma(pygame.Rect(64, 145, 540, 440), pre_dibujado=True, radio=32)
        self.btn_inicio_como_jugar = BotonCalma(pygame.Rect(636, 145, 580, 205), pre_dibujado=True, radio=28)
        self.btn_inicio_salir = BotonCalma(pygame.Rect(636, 380, 580, 205), pre_dibujado=True, radio=28)
        self.btn_modal_cerrar = BotonCalma(pygame.Rect(520, 560, 240, 52), pre_dibujado=False, radio=26)

        self.btn_seleccion_volver = BotonCalma(pygame.Rect(49, 49, 56, 56), pre_dibujado=True, circular=True)
        self.btn_card_corta = BotonCalma(pygame.Rect(98, 165, 340, 465), pre_dibujado=True, radio=26)
        self.btn_card_media = BotonCalma(pygame.Rect(470, 165, 340, 465), pre_dibujado=True, radio=26)
        self.btn_card_completa = BotonCalma(pygame.Rect(842, 165, 340, 465), pre_dibujado=True, radio=26)

        self.btn_juego_volver = BotonCalma(pygame.Rect(25, 29, 47, 47), pre_dibujado=True, circular=True)
        self.btn_sacar_balota = BotonCalma(pygame.Rect(1094, 29, 160, 47), pre_dibujado=True, radio=23)
        self.btn_pausar = BotonCalma(pygame.Rect(31, 646, 180, 39), pre_dibujado=True, radio=14)

        GestorMusica.reproducir_menu()
        self._iniciar_partida(self.modo_seleccionado)
```

#### Explicación de Métodos Paso a Paso:

#### 1. `__init__(self)`
- Crea la ventana de 1280x720 píxeles, fija el título institucional y llama a `inicializar_sistema_recursos()` para cargar fuentes, música e imágenes.
- Inicia el reloj a 60 cuadros por segundo (`self.reloj = pygame.time.Clock()`).
- Define el estado inicial en `"INICIO"`.
- Instancia todos los botones interactivos del juego usando `BotonCalma`.
- Inicia la música suave de menú y prepara la partida.

---

#### 2. `_iniciar_partida(self, modo)`
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
- **Qué hace:** Crea un nuevo objeto lógico `PartidaBingoCognitivo`. Le agrega dos cartones y da inicio al sorteo. A continuación, crea dos objetos gráficos `TableroCartonGUI` ubicados en las coordenadas X=250 y X=754. Extrae la primera balota del bolillero y reinicia las banderas de pausa y victoria.

---

#### 3. `ejecutar(self)` (El Bucle Principal del Videojuego)
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
- **Qué hace:** Mantiene vivo el programa mediante un bucle `while corriendo:`:
  1. `self.reloj.tick(60)`: Asegura que el juego no se acelere y corra exactamente a 60 FPS.
  2. Lee la posición del ratón y avisa a los botones para activar el resplandor de *hover*.
  3. Procesa los eventos del sistema: si se pulsa la cruz roja de la ventana (`QUIT`) o la tecla `Escape`, finaliza limpiamente.
  4. Redibuja todo con `self._dibujar(mouse_pos)`.
  5. `pygame.display.flip()`: Muestra el cuadro terminado en la pantalla del monitor (doble búfer).

---

#### 4. `_actualizar_hover_botones(self, mouse_pos)`
```python
    def _actualizar_hover_botones(self, mouse_pos):
        if self.estado == ESTADO_INICIO:
            if self.modal_como_jugar:
                self.btn_modal_cerrar.actualizar(mouse_pos)
            else:
                self.btn_inicio_jugar.actualizar(mouse_pos)
                self.btn_inicio_como_jugar.actualizar(mouse_pos)
                self.btn_inicio_salir.actualizar(mouse_pos)
        elif self.estado == ESTADO_SELECCION:
            self.btn_seleccion_volver.actualizar(mouse_pos)
            self.btn_card_corta.actualizar(mouse_pos)
            self.btn_card_media.actualizar(mouse_pos)
            self.btn_card_completa.actualizar(mouse_pos)
        elif self.estado == ESTADO_JUEGO:
            self.btn_juego_volver.actualizar(mouse_pos)
            self.btn_sacar_balota.actualizar(mouse_pos)
            self.btn_pausar.actualizar(mouse_pos)
```
- **Qué hace:** Pregunta en qué pantalla estamos y envía la posición actual del cursor únicamente a los botones visibles en ese momento, optimizando el rendimiento.

---

#### 5. `_manejar_eventos(self, evento)` y sus submétodos
```python
    def _manejar_eventos(self, evento):
        if self.estado == ESTADO_INICIO:
            self._manejar_eventos_inicio(evento)
        elif self.estado == ESTADO_SELECCION:
            self._manejar_eventos_seleccion(evento)
        elif self.estado == ESTADO_JUEGO:
            self._manejar_eventos_juego(evento)
```
- **`_manejar_eventos_inicio(self, evento)`**: Si se hace clic en "Jugar", cambia al estado `SELECCION`. Si pulsa "¿Cómo Jugar?", abre el modal explicativo. Si pulsa "Salir", cierra el juego.
- **`_manejar_eventos_seleccion(self, evento)`**: Si pulsa "Volver", regresa al inicio. Si elige una de las tres tarjetas (Corta, Media o Completa), inicia la partida con esa dificultad, cambia el estado a `JUEGO` y activa la música de concentración con `GestorMusica.reproducir_juego()`.
- **`_manejar_eventos_juego(self, evento)`**:
  - Si hay un modal de victoria y se hace clic: reinicia una nueva partida tranquila.
  - Si pulsa "Volver": regresa a selección de modo y pone la música de menú.
  - Si pulsa "Sacar Balota" y no está en pausa: llama a `self._sacar_siguiente_balota()`.
  - Si pulsa "Pausa": invierte el estado de pausa (`self.juego_pausado = not self.juego_pausado`).
  - Si hace clic en la pantalla: llama a `self._procesar_clic_celdas(evento.pos)` para verificar si tocó una casilla.

---

#### 6. `_sacar_siguiente_balota(self)`
```python
    def _sacar_siguiente_balota(self):
        elem = self.partida.extraer_siguiente_elemento()
        if elem:
            self.elemento_actual = elem
```
- **Qué hace:** Le pide a la capa de lógica extraer una nueva balota y actualiza la referencia de la balota activa para que el encabezado y los cartones la destaquen en pantalla.

---

#### 7. `_procesar_clic_celdas(self, pos)`
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
- **Qué hace:** Conecta la interfaz gráfica con las reglas matemáticas:
  1. Consulta a los tableros GUI si el clic tocó alguna casilla.
  2. Si hubo toque, envía la fila y columna al método `marcar_casilla_por_usuario` de la partida.
  3. Si la partida responde que esa jugada completó una figura o bingo (`logro`), activa `self.modal_logro` para que en el siguiente cuadro se dibuje la pantalla festiva de felicitaciones.

---

#### 8. Métodos de Renderizado y Dibujo:
- **`_dibujar(self, mouse_pos)`**: Actúa como conmutador; según `self.estado`, delega el renderizado en `_dibujar_pantalla_inicio`, `_dibujar_pantalla_seleccion` o `_dibujar_pantalla_juego`.
- **`_dibujar_pantalla_inicio(self, mouse_pos)`**: Dibuja el fondo, el logo de Bingo de Recuerdos, los resplandores suaves, los 3 botones principales y, si está activo, el modal de guía.
- **`_dibujar_modal_como_jugar(self)`**: Dibuja un fondo oscurecido translúcido (*overlay*) y una tarjeta central con 4 pasos claros, iconos numéricos y el botón "Entendido, gracias".
- **`_dibujar_pantalla_seleccion(self, mouse_pos)`**: Muestra las 3 tarjetas de modo de juego (Corta, Media, Completa), aplicando una suave micro-animación de elevación (sube 3 píxeles) y resplandor al pasar el cursor por encima.
- **`_dibujar_pantalla_juego(self, mouse_pos)`**: Dibuja el fondo del tablero, la cabecera con el riel de balotas, las figuras deseadas en la columna lateral izquierda y los dos cartones de juego.
- **`_dibujar_header_juego(self)`**: Muestra en el margen superior el contador de balotas (`Balota X / 40`), las últimas 4 balotas que salieron ordenadas cronológicamente, y resalta a la derecha la balota actual con su ilustración a todo color y su nombre temático.
- **`_dibujar_panel_figuras_juego(self)`**: Muestra en la columna izquierda miniaturas de las figuras de bingo a formar (Cruz, Diamante, Cartón Lleno, etc.) y les dibuja un contorno verde menta cuando ya han sido completadas con éxito.
- **`_dibujar_overlay_pausa(self)`**: Muestra un botón ámbar suave para reanudar cuando el usuario hace una pausa en la partida.
- **`_dibujar_modal_victoria(self)`**: Muestra un cuadro de diálogo festivo pero relajante con el mensaje *"¡FELICITACIONES!"*, el nombre de la figura conseguida y las estrellas ganadas, invitando a seguir jugando sin presiones.

---

### 4.5. Bloque de Entrada Principal

```python
if __name__ == "__main__":
    app = BingoCalmaApp()
    app.ejecutar()
```

#### Explicación para Principiantes:
`if __name__ == "__main__":` es la convención estándar de Python para indicar: *"Si este archivo se ejecutó directamente (haciendo doble clic o ejecutando `python main.py`), arranca el juego"*.
Crea el objeto `app` e inicia el bucle `ejecutar()`.

---

## 5. Apéndice: ¿Cómo Quedaría `main.py` Sin Decoradores?

En [`main.py`](file:///d:/documentos/Proyecto%20taller%20de%20abstraccion%20eugenio/main.py), el único decorador presente es `@staticmethod` en el método `dividir_texto_en_lineas` de la clase `TableroCartonGUI`.

### A. Con decorador (Código actual en línea 56):
```python
class TableroCartonGUI:
    # ...
    @staticmethod
    def dividir_texto_en_lineas(texto, fuente, max_ancho=72):
        if fuente.size(texto)[0] <= max_ancho:
            return [texto]
        palabras = texto.split()
        # ... cálculo de división ...
        return mejor_div
```

### B. Sin decorador (Opción 1: Método estándar con `self`):
Se le agrega el parámetro `self`. Ahora es un método común de la instancia:
```python
class TableroCartonGUI:
    # ...
    def dividir_texto_en_lineas(self, texto, fuente, max_ancho=72):
        if fuente.size(texto)[0] <= max_ancho:
            return [texto]
        palabras = texto.split()
        # ...
        return mejor_div

    def dibujar(self, superficie, mouse_pos, elemento_actual_id):
        # Se invoca a través de self:
        lineas_nom = self.dividir_texto_en_lineas(elem.nombre, Fuentes.celda_nombre, max_ancho=72)
```

### C. Sin decorador (Opción 2: Función libre utilitaria):
Al ser un algoritmo tipográfico que solo procesa cadenas de texto y fuentes, se puede colocar fuera de la clase:
```python
# Función libre en main.py:
def dividir_texto_en_dos_lineas(texto, fuente, max_ancho=72):
    if fuente.size(texto)[0] <= max_ancho:
        return [texto]
    palabras = texto.split()
    # ...
    return mejor_div

class TableroCartonGUI:
    def dibujar(self, superficie, mouse_pos, elemento_actual_id):
        # Llamada directa a la función libre:
        lineas_nom = dividir_texto_en_dos_lineas(elem.nombre, Fuentes.celda_nombre, max_ancho=72)
```

---

## 6. Tabla Síntesis de Pilares y Evidencias en `main.py`

| Clase en `main.py` | Pilar de la POO | Evidencia Exacta en el Código |
| :--- | :--- | :--- |
| **`BotonCalma`** | **Abstracción y Composición** | - Compone `pygame.Rect` en `self.rect = rect`.<br>- Abstrae la detección de eventos de hardware en `es_clickeado(evento)`.<br>- Encapsula el estado de brillo en `self.hovered`. |
| **`TableroCartonGUI`** | **Separación de Responsabilidades y Composición** | - Separa la vista gráfica del modelo matemático (`Carton`).<br>- Compone un cartón en `self.carton = carton`.<br>- Abstrae la conversión de coordenadas con `obtener_celda_en_pos()`. |
| **`BingoCalmaApp`** | **Abstracción de Alto Nivel y Encapsulamiento** | - Encapsula el Bucle Principal del Juego a 60 FPS dentro de `ejecutar()`.<br>- Encapsula la Máquina de Estados (`self.estado = ESTADO_INICIO`).<br>- Trata polimórficamente los botones al actualizar y renderizar en `_actualizar_hover_botones()`. |

---
*Manual técnico y didáctico elaborado para el estudio exhaustivo de la capa de presentación de Bingo Calma.*
