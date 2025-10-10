# Importar todos los módulos para verificar que no haya errores
from player import MusicPlayer
from lyrics_display import LyricsDisplay
import pylrc

# Probar la funcionalidad de parseo con la corrección
lrc_content = '[00:05.00]Esta es una línea de ejemplo'
lyrics = pylrc.parse(lrc_content)
first_line = lyrics[0]
print(f'Parseo correcto: {first_line.text} en {first_line.minutes}:{first_line.seconds:02}.{first_line.milliseconds:03}s')

# Probar creación de objetos
player = MusicPlayer()
display = LyricsDisplay()
print('Objetos creados correctamente')

print('Todas las pruebas pasaron correctamente')