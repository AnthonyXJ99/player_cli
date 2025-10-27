import os
import sys
from player import MusicPlayer
from utils import get_available_songs

def show_menu():
    """Mostrar menú principal"""
    print("Music Player con Letras en Consola")
    print("=====================================")

def show_help():
    """Display help information with all available commands"""
    help_text = """
Controles Disponibles:
  p - Pausar / Reanudar
  s - Detener reproducción y volver al menú
  q - Salir de la aplicación
  + - Aumentar volumen
  - - Disminuir volumen
  n - Canción siguiente
  b - Canción anterior
  r - Alternar modo repetición (ninguno → todos → uno → ninguno)
  h - Alternar modo aleatorio
  ? - Mostrar esta ayuda
    """
    print(help_text)

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
        
        try:
            player.load_song(song_path, lyrics_path)
            player.play()
        except Exception as e:
            print(f"Error al cargar la canción: {e}")
            input("Presiona Enter para continuar...")
            return
        
        # Importar msvcrt para detectar entrada en Windows
        import msvcrt
        
        while player.is_playing() or not player.stopped:
            # Verificar si hay entrada del usuario
            try:
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
                    elif command == '+':
                        new_volume = player.increase_volume()
                        print(f"\nVolumen aumentado: {int(new_volume * 100)}%")
                    elif command == '-':
                        new_volume = player.decrease_volume()
                        print(f"\nVolumen disminuido: {int(new_volume * 100)}%")
                    elif command == 'n':
                        if player.next_track():
                            print(f"\nReproduciendo siguiente canción...")
                        else:
                            print(f"\nNo hay más canciones en la lista")
                    elif command == 'b':  # Back to previous track
                        if player.prev_track():
                            print(f"\nReproduciendo canción anterior...")
                        else:
                            print(f"\nNo hay canción anterior")
                    elif command == 'r':
                        repeat_mode = player.toggle_repeat()
                        repeat_str = {"none": "ninguno", "all": "todos", "one": "uno"}
                        print(f"\nModo repetición: {repeat_str[repeat_mode]}")
                    elif command == 'h':
                        player.toggle_shuffle()
                        shuffle_status = "activado" if player.playlist.is_shuffled else "desactivado"
                        print(f"\nModo aleatorio: {shuffle_status}")
                    elif command == '?':
                        show_help()
                    elif command == 'v':
                        new_mode = player.cycle_visualization_mode()
                        print(f"\nModo de visualización cambiado a: {new_mode}")
            except Exception as e:
                print(f"Error de entrada: {e}")
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