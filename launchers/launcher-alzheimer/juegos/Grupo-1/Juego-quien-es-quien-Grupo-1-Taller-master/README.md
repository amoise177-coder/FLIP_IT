# ¿Quién es quién?

Juego educativo de memoria y reconocimiento familiar hecho en **Python +
Pygame**, para la materia *Objetos y Abstracción de Datos*. Está pensado
para adultos mayores en fase temprana de Alzheimer: interfaz simple,
texto grande y de alto contraste, sin límites de tiempo y sin penalizar
las respuestas incorrectas.

El diseño completo está en `Documento_Diseno_Quien_Es_Quien.pdf` (no
incluido en el repositorio de código); este README resume solo lo
necesario para ejecutar y mantener el proyecto.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
python main.py
```

Se abre una ventana de **1280x720** a 60 FPS.

## Compatibilidad con el launcher "enfocate"

Este juego está preparado para correr como un submódulo dentro del
launcher de la materia:

- `main.py` es el punto de entrada y se puede ejecutar de forma
  totalmente independiente (no importa nada del launcher).
- Todas las rutas de datos y recursos se calculan a partir de la
  ubicación de `main.py`, no del directorio de trabajo, para que
  funcione igual sin importar cómo lo lance el `engine.py` del launcher.
- `metadata.json` contiene el título, la descripción, los autores, el
  número de grupo y los controles, tal como pide el launcher.
- `assets/cover/launcher_cover.png` es la portada que se muestra en el
  menú del launcher (generada con `herramientas/generar_portada.py`).
- La resolución (1280x720) y el FPS objetivo (60) coinciden con la base
  del launcher.

**Antes de entregar el proyecto**, edita `metadata.json` y la sección de
créditos (`pantallas/creditos_screen.py`, constantes `INTEGRANTES`,
`DOCENTE` y `RECURSOS_EXTERNOS`) con los datos reales del equipo: se
dejaron con valores de ejemplo porque esa información no estaba
especificada.

## Estructura del proyecto

```
proyecto_quien_es_quien/
├── main.py                  # Punto de entrada (pequeño, sin lógica de juego)
├── metadata.json             # Metadatos para el launcher "enfocate"
├── requirements.txt
├── juego/                    # Lógica y datos (independiente de la interfaz)
│   ├── configuracion.py      # Resolución, colores, rutas, tamaños de texto
│   ├── juego.py               # Clase Juego: controla el estado y el bucle principal
│   ├── jugador.py             # Clase Jugador: puntuación y progreso
│   ├── personaje.py           # Clase Personaje: datos de cada integrante de la familia
│   ├── preguntas.py           # Jerarquía Pregunta (abstracta) y sus subclases
│   ├── opciones.py            # Preferencias de audio y tamaño de texto
│   ├── generador_preguntas.py # Genera el cuestionario de cada partida al azar (ver más abajo)
│   ├── sintetizador.py        # Generación de tonos/melodías compartida por audio y música
│   ├── audio.py               # Efectos de sonido (clic, acierto, error)
│   └── musica.py              # Música de fondo interactiva (cambia según la pantalla)
├── pantallas/                 # Interfaz (una clase por pantalla)
│   ├── pantalla.py            # Clase base abstracta Pantalla
│   ├── boton.py                # Botón reutilizable (sombra, brillo, ícono, resplandor)
│   ├── iconos.py                # Íconos vectoriales (jugar, opciones, créditos, salir, etc.)
│   ├── avatar.py               # Rostro detallado de cada personaje (con antialiasing)
│   ├── menu.py, personajes_screen.py, pregunta_screen.py,
│   │   resultado_screen.py, opciones_screen.py, creditos_screen.py
│   └── utilidades.py           # Helpers de dibujo (texto, paneles, fondo degradado, resplandor)
├── datos/
│   └── personajes.json         # Banco de al menos 8 personajes posibles
├── recursos/                   # imagenes/ sonidos/ fuentes/ (reservado; hoy no se usan
│                                  archivos porque los avatares y sonidos se generan en
│                                  tiempo de ejecución, ver "Recursos gráficos y sonoros")
├── assets/cover/launcher_cover.png   # Portada para el launcher
└── herramientas/generar_portada.py   # Script para regenerar esa portada
```

## Arquitectura orientada a objetos

- **Abstracción**: `Pregunta` (clase abstracta) define lo común a toda
  pregunta — enunciado, opciones, respuesta correcta y cómo comprobarla.
  `Pantalla` hace lo mismo para las pantallas.
- **Herencia**: `PreguntaIdentificacion`, `PreguntaCaracteristica`,
  `PreguntaRelacion` y `PreguntaVisual` heredan de `Pregunta`. Las seis
  pantallas heredan de `Pantalla`.
- **Encapsulamiento**: los atributos de `Jugador`, `Personaje` y
  `Opciones` son privados y solo se modifican a través de sus métodos
  (`sumar_puntos()`, `alternar_musica()`, etc.), nunca directamente.
- **Polimorfismo**: `Juego` guarda las 8 preguntas de una partida (de
  distintas subclases) en una sola lista y llama siempre a los mismos
  métodos (`comprobar_respuesta`, `usa_opciones_visuales`,
  `obtener_tipo`) sin preguntar de qué subclase se trata. Lo mismo pasa
  con las pantallas: `Juego` solo conoce la interfaz común
  (`procesar_evento`, `actualizar`, `dibujar`).

## Datos

Los personajes viven en `datos/personajes.json`, separados del código:
se puede agregar, quitar o modificar integrantes de la familia (nombre,
rol, género, característica, color y de quién es hijo/a) sin tocar la
lógica del juego. Las preguntas, en cambio, ya NO se leen de un archivo
fijo: `juego/generador_preguntas.py` las construye en el momento a
partir de los personajes sorteados para cada partida (ver "Variedad
entre partidas" abajo), pero siguen entregándose con el mismo formato de
diccionario de siempre (`tipo`/`enunciado`/`opciones`/`respuesta`) a
`crear_pregunta_desde_datos` en `juego/preguntas.py` — el generador solo
cambia de dónde salen esos diccionarios, no la fábrica ni la jerarquía
de clases `Pregunta` que los consume.

## Variedad entre partidas

Para que el juego no se sienta igual (ni con las mismas caras, ni con
las mismas preguntas) cada vez que se juega:

- `datos/personajes.json` guarda un banco de **8 integrantes** de una
  familia de tres generaciones (abuelos, hijos/tíos y nietos), cada uno
  con su propio color, peinado y característica.
- Al pulsar "Jugar" (`Juego.iniciar_partida`), se sortea al azar
  `TAMANO_FAMILIA_PARTIDA` (3, ver `juego/configuracion.py`) de esos 8
  personajes: esa es "la familia" que hay que conocer y sobre la que
  versará el cuestionario de esa partida en concreto.
- Con esos 3 personajes ya elegidos, `generador_preguntas.py` arma un
  cuestionario de 8 preguntas combinando identificación, característica,
  relación familiar (cuando la familia sorteada incluye algún par
  padre/madre-hijo/a o abuelo/a-nieto/a) y reconocimiento visual — con
  la redacción, el orden y la combinación exacta barajados, así que ni
  las preguntas ni su secuencia se repiten igual entre partidas.
- La mecánica en sí no cambia de una partida a otra: siempre hay
  exactamente 3 opciones por pregunta (los 3 integrantes sorteados) y 8
  preguntas por partida, con al menos una de reconocimiento visual.

## Recursos gráficos y sonoros

Para evitar depender de imágenes o audio externos (y de sus licencias),
todo se dibuja o se genera en tiempo de ejecución:

- **Rostros**: cada personaje tiene un rostro visible y con detalle
  (iris y brillo en los ojos, cejas, sombra de nariz, rubor en las
  mejillas, sombreado de piel y ropa) dibujado con formas geométricas de
  Pygame en `pantallas/avatar.py`, más un peinado y accesorios (pelo
  largo/corto, color de cabello, lentes con destello en el caso del
  abuelo) que lo distinguen del resto de la familia — importante para
  las preguntas de reconocimiento visual, donde solo se muestran las
  caras, sin nombres. Cada rostro se dibuja primero a 4x de resolución y
  luego se reduce con suavizado (*supersampling*), para que los bordes
  se vean nítidos y sin dentado incluso ampliados; el resultado se
  guarda en caché (`_CACHE` en `avatar.py`) para no repetir ese cálculo
  costoso en cada fotograma.
- **Animación**: cada retrato parpadea de vez en cuando y flota con un
  vaivén vertical suave (ambos con una fase propia por personaje, para
  que no todos parpadeen ni floten exactamente al mismo tiempo), y las
  opciones con imagen "crecen" un poco al pasar el mouse. Como el
  retrato en sí sigue cacheado, esto se logra dibujando encima (el
  parpadeo) o desplazando dónde se pega la imagen (el flotado), sin
  volver a generar el dibujo completo en cada fotograma — ver
  `dibujar_avatar` en `pantallas/avatar.py`.
- **Efectos de sonido** (clic, acierto, error): tonos generados
  matemáticamente en `juego/audio.py`, con un timbre simple (pitido
  limpio), pensado para una señal corta de interfaz.
- **Música de fondo interactiva**: `juego/musica.py` genera tres pistas
  en bucle y cambia automáticamente entre ellas según la sección del
  juego — una serena y hogareña para el menú/opciones/créditos, otra un
  poco más ligera y curiosa durante la partida (conocer a la familia y
  responder preguntas), y una tercera cálida y ascendente para la
  pantalla de resultado — sin cortar la música al pasar de una pantalla
  a otra dentro de la misma sección. A diferencia de los efectos, cada
  pista combina una melodía en escala pentatónica con un acompañamiento
  grave sostenido (tónica/quinta) por debajo, ambos con un timbre
  "cálido" (`sintetizador.py`: armónicos suaves más un trémolo ligero,
  en vez de un pitido puro), para que suene más a un acompañamiento
  discreto de caja de música que a una serie de bips de videojuego —
  algo más acorde con un juego pensado para adultos mayores.

Todo el audio es opcional y respeta los controles de la pantalla de
Opciones (volumen y activar/desactivar, por separado para música y
efectos): si el equipo no tiene salida de sonido disponible, el juego
sigue funcionando en silencio sin errores.

## Aspecto visual

Todas las pantallas comparten un mismo lenguaje visual "de vitrina"
(como el de un juego casual comercial), en vez de colores planos:

- **Fondo degradado animado** (`dibujar_fondo` en
  `pantallas/utilidades.py`): un degradado cálido de arriba hacia abajo,
  con destellos de color suaves que se desplazan lentamente en el
  tiempo. El degradado base se calcula una sola vez por tamaño de
  ventana y se reutiliza en caché; solo los destellos se recalculan
  cada fotograma.
- **Paneles y botones con profundidad**: `dibujar_panel` dibuja una
  sombra difuminada detrás de cada panel/tarjeta y un brillo sutil en
  la mitad superior, para simular una superficie curva tipo vidrio.
  `Boton` reutiliza ese mismo lenguaje (sombra, brillo, borde) y añade
  un pequeño "levantamiento" al pasar el mouse y un resplandor pulsante
  en el botón principal de cada pantalla (por ejemplo "Jugar" en el
  menú).
- **Íconos vectoriales** (`pantallas/iconos.py`): cada botón principal
  tiene un ícono dibujado a mano (triángulo de reproducir, engranaje,
  estrella, símbolo de apagado, flechas), en vez de solo texto.
- **Texto con sombra** (`dibujar_texto_con_sombra`) en los títulos, para
  que resalten sobre el fondo degradado.

Nota técnica para quien mantenga este código: Pygame tiene dos familias
de modos de mezcla para `Surface.blit(..., special_flags=...)` que
conviene no confundir. Los modos `BLEND_RGBA_*` (por ejemplo
`BLEND_RGBA_MULT`, `BLEND_RGBA_ADD`) operan también sobre el canal
alfa —y en el caso de `ADD`, la suma de color **no** se escala por ese
alfa, a diferencia de un `blit()` normal—, mientras que los `BLEND_RGB_*`
(sin la "A") dejan el alfa intacto y sí sirven para "iluminar" u
"oscurecer" una superficie sin agujerearla ni saturarla de golpe. Por
eso `dibujar_resplandor` y el sombreado de ropa en `avatar.py` usan
específicamente las variantes `BLEND_RGB_MULT`/`BLEND_RGB_ADD` sobre
superficies opacas (con la intensidad ya "horneada" en el color),
en vez de las variantes `RGBA_*` sobre superficies con transparencia.
