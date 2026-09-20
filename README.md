# FLIP IT

Juego de memoria en Python + pygame. Proyecto de la materia Objetos y
Abstracción de Datos — Gabriel Garantón, Isabela Paraqueimo y César Moya.

Está pensado para correr dentro del launcher **enfocate** de la materia, pero
también arranca solo con `python main.py` (el archivo `enfocate.py` de esta
carpeta es un sustituto local del launcher).

---

## Cómo se juega

Un solo modo: **6 parejas en una cuadrícula de 4x3 (12 cartas) y sin reloj.**

    MENÚ  →  ELIGE TUS CARTAS  →  a jugar

Al tocar una temática la partida arranca de una vez: no hay pantalla de
dificultad ni de tiempo. Se lleva la cuenta de parejas encontradas e
intentos, y al terminar aparece la pantalla de victoria con 1, 2 o 3
estrellas según los intentos que hicieron falta. No hay pantalla de derrota.

Teclas: `ESC` vuelve al menú.

## Por qué está diseñado así (accesibilidad para niños con TDAH)

- **Pocos pasos hasta jugar.** Cada pantalla intermedia es una oportunidad
  de perder el hilo, así que quedaron solo dos.
- **Sin reloj y sin derrota.** Nada de presión de tiempo; el número de
  intentos queda como referencia para mejorar, no como castigo.
- **Tablero corto.** 12 cartas grandes entran completas en pantalla, sin
  tener que buscar cartas lejos del foco de atención.
- **Fondo pastel de bajo contraste y elementos interactivos de alto
  contraste.** Lo que se puede tocar es siempre lo más visible.
- **Animaciones suaves e interpoladas**, sin parpadeos ni destellos.
- **Silueta clara.** Las ilustraciones llevan contorno oscuro para que se
  reconozcan de un vistazo.
- **Sonido tranquilo**, con fundidos entre pistas y un sonido de error
  suave y descendente en vez de un buzz.

---

## Compatibilidad con el launcher enfocate

El launcher no importa el juego: lo abre como **proceso independiente**
(`python main.py` dentro de la carpeta del juego). Lo que exige está cubierto:

| Requisito del launcher | Aquí |
|---|---|
| `main.py` como punto de entrada | ✅ ajusta `sys.path` solo, así que corre desde cualquier carpeta de trabajo |
| `metadata.json` con título, descripción, autores y controles | ✅ en la raíz |
| Portada en `assets/cover/launcher_cover` | ✅ `Assets/cover/launcher_cover.png` y una copia sin extensión, por si el escáner busca el nombre exacto |
| Correr de forma independiente | ✅ `run_preview()` crea su propia ventana de 1280x720 a 60 FPS y cierra pygame al salir |

Como el launcher no inyecta nada, `GameBase`, `GameMetadata` y `COLORS` salen
del `enfocate.py` de esta misma carpeta. No hay que borrarlo.

Lo único que queda por hacer del lado del launcher: agregar el enlace del
repositorio del juego en su `.gitmodules`.

## Estructura

    main.py                   punto de entrada (el launcher lo ejecuta como subproceso)
    metadata.json             ficha que lee el escáner del launcher
    enfocate.py               sustituto local del launcher (GameBase, COLORS...)
    src/juego.py              clase MiJuego: tablero, lógica y pantallas de partida
    menu.py                   menú principal y selección de temática
    instrucciones.py          pantalla "¿Cómo se juega?"
    ui.py                     kit visual compartido (paleta, botones, tarjetas, paneles)
    constantes.py             rutas, colores, configuración del modo de juego y audio
    audio.py                  música de fondo y efectos

    Assets/Images/            fondos, reverso de carta y las 4 temáticas
    Assets/Sonido/            música (.ogg) y Assets/Sonido/sfx/ los efectos

## Scripts de generación de assets

Los assets se generan con código, así que se pueden rehacer en cualquier
máquina. Necesitan `pillow` y `numpy` (`pip install pillow numpy`), y para
convertir el audio a `.ogg`, `ffmpeg` en el PATH.

    python generar_assets.py         fondo.png, fondo_menu.png y volteada.png
    python generar_instrumentos.py   las 12 cartas del tema "instrumentos" + su icono
    python generar_audio.py          la música y los efectos de sonido
    python generar_portada.py        la portada que muestra el launcher

`preparar_temas.py` es el registro de cómo se armaron las cartas de
Spiderman, Mickey y Cenicienta a partir de fotos; no se puede volver a
correr tal cual porque esas fotos están fuera del proyecto.

### Sobre la música

Toda la música y los efectos están **sintetizados con numpy** dentro de
`generar_audio.py` (ondas propias: celesta, marimba, pads y una reverb por
convolución). No se usó ningún archivo de audio con derechos de autor. Las
pistas están hechas para repetirse en bucle sin corte audible: la cola de
reverb se envuelve sobre el inicio.

    sonido_fondo.ogg          menú          ~58 s, 66 BPM
    sonido_juego.ogg          partida       ~47 s, 82 BPM
    sonido_instrucciones.ogg  instrucciones ~33 s, casi solo pads
    sfx/                      boton, carta, correcto, incorrecto

## Requisitos

    pip install pygame
    # solo si vas a regenerar assets:
    pip install pillow numpy
