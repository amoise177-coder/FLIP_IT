# Proyectos de juegos y launchers

Repositorio organizado con proyectos de juegos educativos en Python/Pygame y
dos launchers relacionados.

## Estructura

```text
games/
└── memorizalo/              # Juego de memoria FLIP IT / MEMORIZALO

launchers/
├── launcher-alzheimer/      # Interfaz y launcher experimental
└── tdah-launcher/           # Launcher modular con juegos
```

## Proyecto principal: MEMORIZALO

Juego de memoria desarrollado con Python y Pygame. Incluye seis parejas de
cartas, cuatro temáticas, música sintetizada, efectos de sonido, animaciones
suaves e interfaz pensada para reducir el ruido visual.

Consulta `games/memorizalo/README.md` para la explicación del juego y sus
requisitos.

## Launchers

Los launchers se conservan como proyectos independientes para facilitar su
estudio y evolución. Cada uno tiene su propio README y archivo de requisitos
cuando corresponde.

## Instalación general

Cada proyecto debe instalar sus dependencias desde su propia carpeta:

```powershell
pip install -r requirements.txt
```

Los archivos comprimidos, cachés, repositorios Git anidados y archivos de
video grandes se excluyen del repositorio para mantenerlo reproducible y
compatible con los límites de GitHub.
