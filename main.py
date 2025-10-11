import os
import sys
from player import MusicPlayer

def get_available_songs():
    """Obtener lista de canciones disponibles"""
    songs_dir = "songs"
    lyrics_dir = "lyrics"
    
    if not os.path.exists(songs_dir) or not os.path.exists(lyrics_dir):
        return []
    
    song_files = [f for f in os.listdir(songs_dir) if f.endswith(('.mp3', '.wav', '.ogg'))]
    lyrics_files = [f for f in os.listdir(lyrics_dir) if f.endswith('.lrc')]
    
    available_pairs = []
    for song in song_files:
        song_name = os.path.splitext(song)[0]
        matching_lyrics = [l for l in lyrics_files if os.path.splitext(l)[0] == song_name]
        if matching_lyrics:
            available_pairs.append((os.path.join(songs_dir, song), os.path.join(lyrics_dir, matching_lyrics[0])))
    
    return available_pairs

def show_menu():
    """Mostrar menú principal"""
    print("Music Player con Letras en Consola")
    print("=====================================")

def main():
    player = MusicPlayer()
    
    show_menu()
    
    # Obtener canciones disponibles
    available_songs = get_available_songs()
    
    if not available_songs:
        print("No se encontraron canciones. Asegúrate de tener archivos de música y letras en las carpetas correspondientes.")
        print("\nInstrucciones:")
        print("- Añade archivos de música (MP3, WAV, OGG) a la carpeta 'songs'")
        print("- Añade archivos de letras (LRC) con el mismo nombre que las canciones a la carpeta 'lyrics'")
        print("- Ejemplo: 'ejemplo.mp3' y 'ejemplo.lrc'")
        input("\nPresiona Enter para salir...")
        return
    
    print("\nCanciones disponibles:")
    for i, (song_path, lyrics_path) in enumerate(available_songs, 1):
        song_name = os.path.splitext(os.path.basename(song_path))[0]
        print(f"{i}. {song_name}")
    
    try:
        choice = input(f"\nSelecciona una canción (1-{len(available_songs)}): ").strip()
        choice_idx = int(choice) - 1 if choice.isdigit() else 0
        
        if 0 <= choice_idx < len(available_songs):
            song_path, lyrics_path = available_songs[choice_idx]
            # print(f"\nCargando: {os.path.splitext(os.path.basename(song_path))[0]}") # Removed debug print
        else:
            song_path, lyrics_path = available_songs[0]  # Por defecto, primera canción
            # print(f"\nOpción inválida, seleccionando: {os.path.splitext(os.path.basename(song_path))[0]}") # Removed debug print
        
        player.load_song(song_path, lyrics_path)
        player.play()
        
        # Importar msvcrt para detectar entrada en Windows
        import msvcrt
        
        while player.is_playing() or not player.stopped:
            # Verificar si hay entrada del usuario
            if msvcrt.kbhit():
                command = msvcrt.getch().decode('utf-8').lower()
                if command == 'p':
                    if player.is_paused():
                        player.unpause()
                    else:
                        player.pause()
                elif command == 's':
                    player.stop()
                elif command == 'q':
                    player.stop()
                    break
            
            # Pequeño delay para no sobrecargar el CPU
            import time
            time.sleep(0.1)
            
            # Si la música ha terminado
            if not player.is_playing() and not player.stopped:
                break
    
    except FileNotFoundError:
        print("Archivo no encontrado. Asegúrate de tener archivos de música y letras en las carpetas correspondientes.")
    except KeyboardInterrupt:
        print("\nReproducción interrumpida por el usuario.")
    except Exception as e:
        print(f"Ocurrió un error: {str(e)}")
    finally:
        if not player.stopped:
            player.stop()

if __name__ == "__main__":
    main()