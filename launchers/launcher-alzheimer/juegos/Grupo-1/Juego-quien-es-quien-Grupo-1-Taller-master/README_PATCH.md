# Parche multimedia — ¿Quién es quién?

Este parche transforma el audio y el fondo principal en recursos externos editables, sin tocar la lógica de preguntas, personajes, puntuación ni navegación.

## Archivos modificados

- `main.py`
- `requirements.txt`
- `metadata.json`
- `juego/configuracion.py`
- `juego/audio.py`
- `juego/musica.py`
- `juego/juego.py`
- `pantallas/pantalla.py`
- `pantallas/menu.py`
- `pantallas/video_fondo.py` (nuevo)
- `pantallas/creditos_screen.py`

## Assets esperados

```text
recursos/
├── sonidos/
│   ├── efectos/
│   │   ├── clic.wav
│   │   ├── correcto.wav
│   │   └── incorrecto.wav
│   └── musica/
│       ├── musica_menu.ogg
│       ├── musica_partida.ogg
│       └── musica_resultado.ogg
└── videos/
    └── menu_fondo.mp4
```

Los nombres anteriores son las rutas configuradas. Sustituir un asset por otro archivo con el mismo nombre no requiere modificar Python.

## Paradigma de objetos y abstracción

- `GestorAudio` encapsula la carga y reproducción de efectos.
- `GestorMusica` encapsula el recurso musical y sus estados.
- `FondoVideo` encapsula decodificación, conversión, actualización y bucle del video.
- `Pantalla` incorpora el ciclo de vida `al_cerrar()` para liberar recursos específicos.
- `Juego` sigue actuando como coordinador, sin conocer detalles de implementación del video o del formato de audio.
- Las pantallas siguen usando la interfaz común de `Pantalla` mediante polimorfismo.

## Comportamiento de tolerancia a fallos

- Si falta un efecto, ese efecto queda deshabilitado sin cerrar el juego.
- Si falta una pista musical, se conserva la pista que estuviera activa o se continúa en silencio.
- Si falta OpenCV o el video no puede abrirse, el menú utiliza el fondo degradado existente.
- Al cerrar el juego se liberan los recursos de video y música.
