# Sistema Recreativo — interfaz del launcher "enfócate"

Interfaz visual (menú principal + pantalla de selección) para el launcher
que correrá los juegos de la materia en Python. Este entregable es **solo
la interfaz**: pantallas, animaciones, colores y tipografía. No carga
juegos reales todavía — eso se conecta después sobre esta misma base.

## Cómo ejecutarla

```bash
pip install -r requirements.txt
python3 interfaz_launcher.py
```

Se abre una ventana de 1100x680. Controles:

- Clic en **¡EMPEZAR!** → pasa a la pantalla "¿Qué quieres jugar?".
- Clic en una tarjeta de juego → muestra un mensaje (aún no abre ningún
  juego real; es el lugar donde se conectará cada uno).
- Clic en **← Volver** → regresa al menú principal.
- `Esc` o cerrar la ventana → salir.

En la carpeta `capturas/` hay imágenes fijas de referencia por si quieres
ver el diseño sin correr el programa.

## Decisiones de diseño (pensado para niños con TDAH)

- **Colores vivos pero no puros**: la paleta usa tonos como coral, turquesa
  y amarillo sol suavizados, en vez de rojo/verde/azul al 100%, para que
  llamen la atención sin saturar la vista.
- **Movimiento continuo y suave**: el título "respira" con un rebote leve
  letra por letra, el botón pulsa despacio y hay burbujas/estrellas
  flotando de fondo — nunca parpadeos ni cambios bruscos.
- **Poca información por pantalla**: un título, un subtítulo y un solo
  botón de acción en el menú; en la selección, solo las tarjetas de juego.
- **Tipografía especial y redondeada**: se usan tres fuentes gratuitas de
  Google Fonts (licencia SIL Open Font License, se pueden usar y
  redistribuir libremente):
  - `Fredoka` (Bold) — título grande, bien "burbujeante".
  - `Baloo 2` (SemiBold / ExtraBold) — subtítulos, botones y tarjetas.
  - `Bubblegum Sans` — el detalle decorativo bajo el subtítulo.

## Cómo seguir conectando esto al launcher real

`interfaz_launcher.py` está organizado para que sea fácil de extender:

- `InterfazLauncher.manejar_click()` es el único lugar donde una tarjeta
  de juego "reacciona" a un clic — ahí es donde, más adelante, se puede
  llamar al código que realmente carga y corre el juego (por ejemplo,
  usando `GameBase`/`GameMetadata` del launcher "enfocate" del curso).
- La lista `self.tarjetas` en `InterfazLauncher.__init__` es la que arma
  las tarjetas de la pantalla de selección — agregar un juego nuevo es
  agregar un elemento `TarjetaJuego` más ahí.
- Los colores están centralizados arriba del archivo (`PALETA_TITULO`,
  `COLOR_BOTON`, etc.) para poder ajustarlos sin tocar la lógica.
