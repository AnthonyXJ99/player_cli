# Music Player con Letras en Consola

Un reproductor de música en consola que muestra las letras de las canciones con sincronización en tiempo real.

## Funcionalidades

- Reproducción de archivos de audio (MP3, WAV, OGG)
- Visualización de letras sincronizadas (formato LRC)
- Interfaz en consola con formato Rich
- Controles básicos de reproducción

## Instalación

1. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

2. Añade tus archivos de música a la carpeta `songs/` y los archivos de letra LRC a la carpeta `lyrics/`.
3. Asegúrate de que cada archivo de música tenga su correspondiente archivo de letra con el mismo nombre (por ejemplo: `cancion.mp3` y `cancion.lrc`).

## Uso

Ejecuta el programa con:
```
python main.py
```

## Controles

- `p` - Pausar/Reanudar reproducción
- `s` - Detener reproducción
- `q` - Salir del programa

## Formato LRC

El archivo LRC debe contener marcas de tiempo para cada línea de la letra. Ejemplo:
```
[00:10.00]Primera línea de la canción
[00:12.50]Segunda línea de la canción
```

## Estructura del Proyecto

```
music_player/
├── main.py          # Archivo principal del programa
├── player.py        # Clase principal del reproductor
├── lyrics_display.py # Manejo de visualización de letras
├── requirements.txt # Dependencias del proyecto
├── README.md       # Documentación
├── songs/          # Carpeta para archivos de música
└── lyrics/         # Carpeta para archivos de letras LRC
```

## Cómo usar con archivos reales

Para usar el reproductor con archivos reales:

1. Coloca tu archivo de música (por ejemplo `música.mp3`) en la carpeta `songs/`
2. Coloca el archivo de letras con el mismo nombre (por ejemplo `música.lrc`) en la carpeta `lyrics/`
3. Asegúrate que los tiempos en el archivo LRC coincidan con los de la canción
4. Ejecuta el programa y selecciona la canción

## Notas

- El reproductor funciona mejor con archivos de música en formato WAV o OGG en algunos sistemas
- Asegúrate de que tus archivos LRC estén codificados en UTF-8 para evitar problemas con caracteres especiales