# Parche: fondo del menú con imagen + música MP3/OGG

Este parche mantiene el fondo del menú como **imagen estática** y añade soporte
para que las pistas de música puedan estar en **MP3 u OGG**, sin necesidad de
convertirlas.

## Fondo del menú

Coloca la imagen en:

`recursos/imagenes/menu_fondo.png`

La clase `FondoImagen` la escala de forma proporcional para cubrir 1280x720 y
recorta los excedentes desde el centro, evitando deformaciones.

## Música

Coloca las pistas en:

`recursos/sonidos/musica/`

con estos nombres base:

- `musica_menu.mp3` **o** `musica_menu.ogg`
- `musica_partida.mp3` **o** `musica_partida.ogg`
- `musica_resultado.mp3` **o** `musica_resultado.ogg`

El gestor busca **primero MP3** y, si no existe, intenta OGG. No necesitas
cambiar ningún archivo Python cuando reemplaces una pista.

La música continúa usando `pygame.mixer.music`, se reproduce en bucle y
responde en tiempo real al volumen y al interruptor de música de la pantalla
de Opciones. Pygame-CE documenta soporte para MP3 y OGG en el mixer y para
`loops=-1` en `pygame.mixer.music.play()`. 

## Efectos de sonido

Los efectos permanecen igual:

`recursos/sonidos/efectos/clic.wav`

`recursos/sonidos/efectos/correcto.wav`

`recursos/sonidos/efectos/incorrecto.wav`

## Dependencias

El proyecto queda con:

`pygame-ce>=2.5.7`

Ya no se necesita `opencv-python`, porque el fondo de video fue eliminado.

## Limpieza del parche anterior

Elimina del proyecto:

`pantallas/video_fondo.py`

`recursos/videos/menu_fondo.mp4`

También puedes borrar la carpeta `recursos/videos/` si queda vacía.

## Prueba recomendada

Prueba primero solo con MP3. Después, si quieres comprobar el fallback, deja
una pista en MP3 y otra en OGG de forma alternativa. El juego debe detectar la
que exista automáticamente.
