# Documentación completa del proyecto: ¿Quién es quién?

## 1. Descripción general

Este proyecto es un juego educativo desarrollado en Python con Pygame, pensado para personas mayores en una etapa temprana de Alzheimer o con dificultades de memoria. La idea principal es que el jugador conozca a una pequeña familia ficticia, aprenda sus nombres, relaciones y características, y luego responda preguntas sencillas con opciones claras y accesibles.

El juego está diseñado con:

- interfaz grande y legible;
- alto contraste de colores;
- texto fácil de interpretar;
- música y sonidos suaves y no agresivos;
- interacción simple con clic del ratón y teclado;
- ausencia de penalización severa por errores;
- variedad de preguntas entre partidas.

La lógica del juego está dividida en dos grandes bloques:

- `juego/`: estructura de datos, lógica del motor, generación dinámica de preguntas y control del flujo.
- `pantallas/`: todas las interfaces visuales del juego.

---

## 2. Objetivo del proyecto

El objetivo no es solo crear un juego entretenido, sino un recurso educativo de apoyo para la memoria y la orientación familiar. El juego busca:

- reforzar la memoria visual y verbal;
- enseñar relaciones familiares básicas;
- facilitar la identificación de personajes por nombre, rasgos o familia;
- ofrecer una experiencia tranquila y comprensible para usuarios mayores.

---

## 3. Tecnologías usadas

- Python 3
- Pygame
- JSON para almacenamiento de datos
- Programación orientada a objetos
- Generación procedural de audio y música para no depender de recursos externos

### Dependencias

El proyecto usa únicamente:

```bash
pygame>=2.5
```

---

## 4. Estructura del proyecto

```text
proyecto_quien_es_quien/
├── main.py
├── README.md
├── DOCUMENTACION_PROYECTO.md
├── metadata.json
├── requirements.txt
├── assets/
│   └── cover/
├── datos/
│   └── personajes.json
├── herramientas/
│   └── generar_portada.py
├── juego/
│   ├── __init__.py
│   ├── audio.py
│   ├── configuracion.py
│   ├── generador_preguntas.py
│   ├── juego.py
│   ├── jugador.py
│   ├── musica.py
│   ├── opciones.py
│   ├── personaje.py
│   ├── preguntas.py
│   └── sintetizador.py
├── pantallas/
│   ├── __init__.py
│   ├── avatar.py
│   ├── boton.py
│   ├── creditos_screen.py
│   ├── iconos.py
│   ├── menu.py
│   ├── opciones_screen.py
│   ├── pantalla.py
│   ├── personajes_screen.py
│   ├── pregunta_screen.py
│   ├── resultado_screen.py
│   └── utilidades.py
├── recursos/
│   ├── fuentes/
│   ├── imagenes/
│   └── sonidos/
└── __pycache__/
```

---

## 5. Flujo de ejecución

El punto de entrada es `main.py`.

### 5.1 `main.py`

Este archivo es muy pequeño por diseño. Su función es:

1. ajustar la ruta del proyecto para que funcione desde cualquier directorio;
2. inicializar Pygame;
3. crear la ventana principal;
4. crear la instancia del juego;
5. lanzar el ciclo principal.

Es importante destacar que se evita depender del directorio de trabajo actual del sistema, lo que hace que el juego pueda ejecutarse tanto como aplicación independiente como dentro de un launcher externo.

---

## 6. Sistema de configuración

El archivo `juego/configuracion.py` centraliza todas las constantes globales del proyecto.

Incluye:

- tamaño de la ventana;
- título de la ventana;
- FPS objetivo;
- rutas absolutas al proyecto y a recursos;
- paleta de colores;
- tamaños de texto;
- número de personajes por partida;
- total de preguntas por partida.

Esto ayuda a que el juego sea fácil de mantener y evita que los valores estén dispersos por el código.

### Valores clave

- Resolución: 1280x720
- FPS: 60
- 3 personajes por partida
- 8 preguntas por partida
- Cada respuesta correcta suma 10 puntos

---

## 7. Modelo de datos

### 7.1 `Personaje`

Archivo: `juego/personaje.py`

La clase `Personaje` encapsula la información de cada miembro de la familia ficticia:

- nombre
- rol (abuelo, padre, hijo, nieto, etc.)
- género
- característica
- color asociado
- referencia a su padre (si la tiene)

El diseño usa encapsulación: los atributos se guardan con prefijo de acceso privado y se leen mediante propiedades.

La clase también ofrece `cargar_familia()`, que transforma la lista de diccionarios del JSON en un diccionario de objetos `Personaje`.

### 7.2 `datos/personajes.json`

Aquí está la base de datos del juego. Define una familia con varios personajes, cada uno con:

- nombre
- rol
- género
- característica
- color
- relación con su padre

Esto permite modificar o ampliar la familia sin tocar la lógica del juego.

---

## 8. Generación dinámica de preguntas

Archivo: `juego/generador_preguntas.py`

La clave del proyecto es que no hay un banco fijo de preguntas guardado en un archivo. En cambio, cada partida:

1. selecciona aleatoriamente 3 personajes del banco total;
2. genera un conjunto de preguntas relacionadas con esos personajes;
3. mezcla el orden de la lista para que no siempre sea igual.

### Tipos de pregunta generados

- identificación por nombre
- identificación por característica
- preguntas de relación familiar
- reconocimiento visual

### Lógica principal

- `_preguntas_identificacion()`: pregunta por nombre.
- `_preguntas_caracteristica()`: pregunta por virtud o característica.
- `_preguntas_visuales()`: reconoce la cara del personaje por imagen.
- `_preguntas_relacion()`: utiliza relaciones entre padres e hijos y abuelos y nietos.
- `generar_datos_preguntas()`: crea la lista completa de preguntas para la partida.

Esto hace que cada partida tenga un patrón distinto aunque la mecánica no cambie.

---

## 9. Jerarquía de preguntas

Archivo: `juego/preguntas.py`

La lógica de preguntas se estructura con abstracción, herencia y polimorfismo.

### Clase base

`Pregunta` define la interfaz común:

- enunciado
- opciones
- respuesta correcta
- validación de respuesta
- comprobación de si se usan imágenes o texto

### Subclases

- `PreguntaIdentificacion`
- `PreguntaCaracteristica`
- `PreguntaRelacion`
- `PreguntaVisual`

Cada una implementa el comportamiento específico sin romper la interfaz común del juego.

Esto permite que `Juego` maneje preguntas de cualquier tipo con la misma API.

---

## 10. Motor del juego

Archivo: `juego/juego.py`

La clase `Juego` es el centro del sistema. Controla:

- la ventana y el reloj;
- el estado activo de la pantalla;
- la familia de la partida;
- la lista de preguntas actuales;
- el jugador;
- las opciones y audio;
- navegación entre pantallas;
- flujo principal del juego.

### Estados principales

- `MENU`
- `PERSONAJES`
- `PREGUNTA`
- `RESULTADO`
- `OPCIONES_PANTALLA`
- `CREDITOS`

### Ciclo principal

El juego usa un bucle while ejecutado por `ejecutar()`:

1. procesa eventos;
2. actualiza la pantalla actual;
3. dibuja el contenido;
4. ajusta el FPS.

---

## 11. Jugador y puntuación

Archivo: `juego/jugador.py`

La clase `Jugador` guarda:

- puntuación total;
- número de respuestas correctas;
- número de respuestas totales.

Se usa encapsulación para que la puntuación solo se actualice por métodos definidos:

- `sumar_puntos()`
- `registrar_fallo()`
- `reiniciar()`

La lógica de puntuación es simple: las respuestas correctas suman 10 puntos y las incorrectas no restan puntos. Esta decisión busca mantener una experiencia más amable para usuarios mayores.

---

## 12. Opciones y accesibilidad

Archivo: `juego/opciones.py`

Aquí se gestionan:

- volumen de música;
- volumen de efectos;
- activación o desactivación de música;
- activación o desactivación de efectos;
- tamaño de texto.

Esto permite adaptar la experiencia según las necesidades del usuario. El tamaño de texto puede cambiar entre modo normal y grande.

---

## 13. Sistema de audio

### 13.1 `juego/sintetizador.py`

Este módulo genera tonos y melodías desde código, en vez de depender de archivos de sonido externos.

Se usa para crear:

- pitidos de clic;
- alarma de acierto;
- sonido de error;
- melodías de fondo.

### 13.2 `juego/audio.py`

La clase `GestorAudio` crea y reproduce sonidos cortos de eventos del juego:

- clic;
- respuesta correcta;
- respuesta incorrecta.

Si no hay salida de audio disponible, el juego sigue funcionando en silencio.

### 13.3 `juego/musica.py`

`GestorMusica` crea melodías suaves adaptadas a cada pantalla:

- menú y créditos: ambiente tranquilo;
- partida: música ligera y acompañante;
- resultado: tono más cálido y motivador.

La música se reproduce en bucle y cambia según el estado actual del juego.

---

## 14. Arquitectura de pantallas

Carpeta: `pantallas/`

Cada pantalla cumple un contrato común definido por `pantallas/pantalla.py`:

- `procesar_evento()`
- `actualizar()`
- `dibujar()`
- `al_entrar()`

### Pantallas principales

#### `menu.py`

Pantalla principal con los botones:

- JUGAR
- OPCIONES
- CRÉDITOS
- SALIR

Muestra un resumen visual de la familia para que el usuario vea la temática del juego antes de jugar.

#### `personajes_screen.py`

Pantalla intermedia para presentar los personajes seleccionados de la familia de la partida.

#### `pregunta_screen.py`

Pantalla central del juego. Aquí se muestra:

- el número de pregunta;
- la puntuación actual;
- el enunciado;
- la imagen del personaje si aplica;
- las opciones de respuesta;
- feedback tras responder.

La lógica funciona con preguntas de cualquier tipo sin importar la clase concreta.

#### `resultado_screen.py`

Muestra la puntuación final con mensajes motivadores, por ejemplo:

- excelente memoria;
- muy bien hecho;
- buen intento.

#### `opciones_screen.py`

Permite cambiar:

- volumen de música;
- volumen de efectos;
- activar/desactivar música;
- activar/desactivar efectos;
- tamaño de texto.

#### `creditos_screen.py`

Muestra información del proyecto, autores y recursos utilizados.

---

## 15. Componentes visuales reutilizables

### 15.1 `boton.py`

Define un botón reutilizable con:

- texto o icono;
- estado hover;
- coloreado diferencial;
- brillo y sombra;
- posibilidad de enfatizar un botón principal.

### 15.2 `avatar.py`

Genera los personajes visualmente a partir de formas geométricas en Pygame. Incluye:

- cara;
- ojos;
- cabello;
- ropa;
- expresión;
- detalles para distinguir a cada personaje.

También incluye animaciones simples como:

- parpadeo;
- flotación;
- cambios leves de escala.

### 15.3 `utilidades.py`

Contiene helpers para:

- fondo degradado;
- paneles con sombras;
- texto con sombras;
- centrado de elementos;
- texto multilínea.

---

## 16. Patrones de diseño presentes

El proyecto usa varios conceptos importantes de programación orientada a objetos:

### Abstracción

`Pregunta` y `Pantalla` definen contratos comunes para todos los tipos derivados.

### Herencia

Las clases de preguntas y pantallas comparten comportamientos base y especializan solo lo necesario.

### Encapsulamiento

Los atributos internos de `Personaje`, `Jugador` y `Opciones` no se modifican directamente desde fuera.

### Polimorfismo

El juego manipula varias preguntas y varias pantallas a través de interfaces comunes, sin saber exactamente qué subclase concreta está usando.

---

## 17. Jugabilidad y flujo de partida

Una partida sigue este flujo:

1. El jugador entra al menú.
2. Pulsa JUGAR.
3. El juego baraja personajes y crea una familia temporal para esa partida.
4. Se genera la lista de preguntas usando esos personajes.
5. Se presenta la pantalla de personajes.
6. Comienza la serie de preguntas.
7. El jugador responde una por una.
8. Se muestra retroalimentación si la respuesta es correcta o no.
9. Cuando termina la lista, aparece la pantalla final con puntuación.
10. El usuario puede repetir la partida o volver al menú.

---

## 18. Regla de variedad entre partidas

Para evitar que el juego se repita demasiado, cada partida:

- selecciona personajes al azar;
- crea preguntas distintas;
- mezcla el orden de las preguntas;
- mezcla las opciones dentro de cada pregunta.

Esto hace que la experiencia no sea exactamente igual en cada partida, incluso si la mecánica sigue siendo la misma.

---

## 19. Compatibilidad con launcher externo

El proyecto incluye:

- `metadata.json` para el launcher;
- `main.py` como punto de entrada independiente;
- rutas relativas al proyecto para no depender del directorio actual;
- portada en `assets/cover/`.

Esto facilita su integración con un launcher o sistema de entrega externo.

---

## 20. Propósito de la carpeta `herramientas/`

El archivo `herramientas/generar_portada.py` genera una portada visual para el proyecto o para el launcher.

La idea es que la imagen pueda regenerarse fácilmente si se cambia la identidad visual del juego.

---

## 21. Mantenimiento y ampliación

Para ampliar el juego o modificarlo, se recomienda seguir esta lógica:

### Añadir personajes

- editar `datos/personajes.json`;
- mantener las claves necesarias: `nombre`, `rol`, `genero`, `caracteristica`, `color`, `padre`;
- asegurarse de que cada personaje tenga una identidad clara dentro de la familia.

### Añadir nuevas preguntas

- reutilizar o ampliar la lógica de `generador_preguntas.py`;
- mantener la estructura de diccionarios esperada por `preguntas.py`;
- añadir el nuevo tipo si hace falta y registrarlo en la fábrica.

### Cambiar colores o estilo visual

- ajustar `juego/configuracion.py`;
- modificar `pantallas/utilidades.py` y `avatar.py` si es necesario.

---

## 22. Buenas prácticas del proyecto

- Centralización de configuración
- Separación entre lógica y pantalla
- Uso de archivos JSON para datos del dominio
- Generación dinámica de contenido
- Audio generado en código para evitar depender de librerías externas
- Accesibilidad visual como prioridad

---

## 23. Conclusión

Este proyecto combina varios conceptos importantes de desarrollo software: diseño orientado a objetos, generación dinámica de contenido, separación de responsabilidades, acceso a datos externos, manejo de estados visuales y audio procedimental. Todo ello se aplica en un juego pensado para un público mayor con una experiencia cálida, clara y fácil de comprender.

Su valor no está solo en la mecánica del juego, sino también en la forma en que se organiza el código para que sea legible, mantenible y extensible.
