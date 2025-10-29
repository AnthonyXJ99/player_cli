import os
import sys
from player import MusicPlayer
from utils import get_available_songs
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import print
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align


console = Console()

def show_menu():
    """Mostrar menú principal"""
    console.clear()  # Clear the console for a clean look
    title = Text("Music Player", style="bold blue underline")
    subtitle = Text("con Letras en Consola", style="bold cyan")
    
    # Create a rich text object to combine title and subtitle
    welcome_text = Text()
    welcome_text.append(title)
    welcome_text.append("\n")
    welcome_text.append(subtitle)
    
    # Create a panel with the title
    welcome_panel = Panel(
        Align.center(welcome_text),
        title="[magenta]Bienvenido[/magenta]",
        border_style="bright_yellow",
        expand=False
    )
    
    console.print("\n")
    console.print(Align.center(welcome_panel))
    console.print("\n")

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
  v - Alternar modo de visualización
  ? - Mostrar esta ayuda
    """
    print(help_text)

def display_songs_paginated(songs_list, page_size=10):
    """Display songs in a paginated format"""
    total_songs = len(songs_list)
    total_pages = (total_songs + page_size - 1) // page_size  # Ceiling division
    current_page = 0
    
    while True:
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, total_songs)
        page_songs = songs_list[start_idx:end_idx]
        
        # Create a colorful table for songs
        table = Table(title=f"[bold green]Canciones disponibles (Página {current_page + 1} de {total_pages})[/bold green]", 
                     title_style="bold magenta",
                     border_style="cyan",
                     header_style="bold blue")
        
        table.add_column("#", style="dim", width=4)
        table.add_column("Canción", style="cyan", min_width=40)
        
        for i, (song_path, lyrics_path) in enumerate(page_songs, start=start_idx):
            song_name = os.path.splitext(os.path.basename(song_path))[0]
            # Truncate long names to fit the display
            display_name = song_name[:46] + "..." if len(song_name) > 46 else song_name
            table.add_row(str(i + 1), f"[bold yellow]{display_name}[/bold yellow]")
        
        console.clear()
        console.print("\n")
        console.print(Align.center(table))
        
        if total_pages > 1:
            print(f"\n[yellow]Navegación:[/yellow] [Pág. Ant] o [A] - [Pág. Sig] o [S] - [Ir a] o [G] - [Salir] o [Q]")
            choice = input("Seleccione canción, página (A/S/G) o salir (Q): ").strip().lower()
            
            if choice == 'q':
                return None
            elif choice == 'a' and current_page > 0:
                current_page -= 1
                continue
            elif choice == 's' and current_page < total_pages - 1:
                current_page += 1
                continue
            elif choice == 'g':
                try:
                    page_num = int(input(f"Ingrese número de página (1-{total_pages}): "))
                    if 1 <= page_num <= total_pages:
                        current_page = page_num - 1
                        continue
                    else:
                        print("Número de página inválido.")
                except ValueError:
                    print("Entrada inválida.")
                continue
            else:
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < total_songs:
                        return choice_idx
                    else:
                        print(f"Opción inválida. Por favor, seleccione entre 1 y {total_songs}")
                except ValueError:
                    print("Entrada inválida. Por favor ingrese un número.")
        else:
            # If only one page, just get the selection
            try:
                choice = input(f"\nSelecciona una canción (1-{total_songs}) o '?' para ayuda: ").strip()
                if choice == '?':
                    show_help()
                    continue
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < total_songs:
                    console.clear()  # Clear console before starting playback
                    return choice_idx
                else:
                    print(f"Opción inválida. Por favor, seleccione entre 1 y {total_songs}")
            except ValueError:
                print("Entrada inválida. Por favor ingrese un número.")


def main():
    player = MusicPlayer()
    
    show_menu()
    
    # Auto-extract lyrics from MP3 files if possible
    print("Buscando y extrayendo letras embebidas en archivos MP3...")
    
    # Obtener canciones disponibles (con auto-extracción)
    available_songs = get_available_songs()
    
    if not available_songs:
        print("No se encontraron canciones. Asegúrate de tener archivos de música y letras en las carpetas correspondientes.")
        print("\nInstrucciones:")
        print("- Añade archivos de música (MP3, WAV, OGG) a la carpeta 'songs'")
        print("- Añade archivos de letras (LRC) con el mismo nombre que las canciones a la carpeta 'lyrics'")
        print("- Ejemplo: 'ejemplo.mp3' y 'ejemplo.lrc'")
        print("- O las letras se pueden extraer automáticamente de archivos MP3 con información embebida")
        input("\nPresiona Enter para salir...")
        return
    
    # Use the new paginated song selection
    selected_idx = display_songs_paginated(available_songs)
    
    if selected_idx is None:  # User chose to quit
        return
    
    song_path, lyrics_path = available_songs[selected_idx]
    console.print(f"\n[green]Seleccionando:[/green] [bold]{os.path.splitext(os.path.basename(song_path))[0]}[/bold]")
    
    try:
        player.load_song(song_path, lyrics_path)
        player.play()
        
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