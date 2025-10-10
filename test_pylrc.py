import pylrc

# Test de la funcionalidad de pylrc
lrc_content = """[00:05.00]Esta es una línea de ejemplo
[00:07.50]Y aquí va otra línea
[00:10.00]Para mostrar cómo funciona"""

print("Parseando LRC...")
lyrics = pylrc.parse(lrc_content)

print('Tipo de objeto:', type(lyrics))
print('Longitud:', len(lyrics))

if lyrics:
    first_line = lyrics[0]
    print('Primer objeto:', first_line)
    print('Tipo de primer objeto:', type(first_line))
    print('Atributos del primer objeto:', dir(first_line))
    
    # Intentar acceder a los atributos específicos
    print('Texto:', getattr(first_line, 'text', 'No encontrado'))
    print('Tiempo:', getattr(first_line, 'time', 'No encontrado'))
else:
    print("No se encontraron letras parseadas")