import os
os.chdir(r"c:\Users\natha\Documents\Javier\tetoyecto\Game-Simon-Clasico-main\Game-Simon-Clasico-main")
import funtions
print('nivel=', repr(funtions.consultar_nivel()))
funtions.colores_secuencia.clear()
funtions.generar_colores()
print('secuencia=', funtions.colores_secuencia)
print('longitud=', len(funtions.colores_secuencia))
