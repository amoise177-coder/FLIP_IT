# Integración y testing del parche

## 1. Crear una rama antes de integrar

```bash
git checkout master
git pull origin master
git checkout -b feat/assets-multimedia
```

Haz el reemplazo de archivos de este parche conservando el resto del repositorio.

## 2. Instalar dependencias

Dentro del entorno virtual del proyecto:

```bash
python -m pip install -r requirements.txt
```

La única dependencia nueva es `opencv-python`, necesaria para decodificar el video de fondo. `pygame` sigue siendo la dependencia principal.

## 3. Copiar los assets

Crea exactamente estas rutas:

```text
recursos/sonidos/efectos/clic.wav
recursos/sonidos/efectos/correcto.wav
recursos/sonidos/efectos/incorrecto.wav
recursos/sonidos/musica/musica_menu.ogg
recursos/sonidos/musica/musica_partida.ogg
recursos/sonidos/musica/musica_resultado.ogg
recursos/videos/menu_fondo.mp4
```

El video debe ser visualmente apropiado para usarse como fondo y no necesita audio, porque el audio musical se controla por separado desde Pygame.

## 4. Requisitos recomendados de los assets

### Efectos de sonido

- `.wav` PCM sin compresión.
- 44.1 kHz.
- 16 bits.
- mono o estéreo.
- Duración corta, idealmente inferior a 1 segundo para clic/acierto/error.

### Música

- `.ogg` recomendado.
- 44.1 kHz.
- 16 bits.
- estéreo preferentemente.
- Sin clipping y con volumen moderado, porque el juego vuelve a aplicar el control de volumen.
- Loops musicales sin silencios largos en los extremos para que el ciclo sea limpio.

### Video

- `.mp4`.
- H.264 es el formato recomendado.
- Resolución recomendada: `1280x720`.
- 24–30 FPS.
- 10–30 segundos suele ser suficiente para un fondo de menú.
- Sin audio o con audio ignorado.
- Evita videos innecesariamente pesados para que el decode en tiempo real sea fluido.

## 5. Prueba de arranque

```bash
python main.py
```

Debe abrir el menú sin excepciones.

## 6. Prueba del video

1. Espera varios segundos en el menú.
2. Comprueba que el video avanza.
3. Espera hasta alcanzar el final y confirma que vuelve al primer fotograma.
4. Entra a JUGAR y verifica que las demás pantallas vuelven al fondo degradado normal.
5. Regresa al menú y verifica que el video vuelve a mostrarse.

## 7. Prueba de música

1. En el menú debe sonar `musica_menu.ogg`.
2. Debe repetirse cuando llegue al final.
3. En Opciones baja/sube el volumen de música y verifica que el cambio es inmediato.
4. Desactiva música y verifica silencio.
5. Activa música y verifica que vuelve.
6. Entra en una partida y comprueba que cambia a `musica_partida.ogg`.
7. Finaliza la partida y comprueba `musica_resultado.ogg`.

## 8. Prueba de efectos

Pulsa botones y responde preguntas.

- Clic -> `clic.wav`.
- Correcta -> `correcto.wav`.
- Incorrecta -> `incorrecto.wav`.

En Opciones, cambia el volumen de efectos y comprueba la diferencia.
Desactiva los efectos y confirma que no se reproducen.

## 9. Prueba de fallback

Esta prueba es importante porque verifica que una ausencia de asset no rompe el juego.

- Renombra temporalmente `clic.wav` y abre el juego: no debe crashear.
- Renombra temporalmente `musica_menu.ogg`: el juego debe seguir funcionando.
- Renombra temporalmente `menu_fondo.mp4`: el menú debe volver al fondo degradado.

Luego restaura los nombres originales.

## 10. Prueba del contenido solicitado

Abre CRÉDITOS y confirma literalmente:

- `SALVADOR CORDOVA`
- `JONATHAN GUAINA`
- `ING PLACIDO MALAVE`

En el menú confirma que el título es más grande y permanece por encima de la hilera animada de personajes.

## 11. Validación final Git

```bash
git status
git add .
git commit -m "feat: integrar assets de audio y video en el juego"
git push -u origin feat/assets-multimedia
```

Después compara la rama con `master` y abre un Pull Request.
