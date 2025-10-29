"""Utility functions for the music player"""

import os
from config import SONGS_DIR, LYRICS_DIR
from lyrics_extractor import auto_extract_lyrics_for_songs, extract_album_art_from_mp3


def get_available_songs(auto_extract=True):
    """Obtener lista de canciones disponibles"""
    if not os.path.exists(SONGS_DIR) or not os.path.exists(LYRICS_DIR):
        print(f"Error: Las carpetas '{SONGS_DIR}' o '{LYRICS_DIR}' no existen.")
        return []
    
    try:
        supported_formats = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma', '.opus', '.aiff', '.au')
        song_files = [f for f in os.listdir(SONGS_DIR) if f.lower().endswith(supported_formats)]
        lyrics_files = [f for f in os.listdir(LYRICS_DIR) if f.endswith('.lrc')]
    except PermissionError:
        print("Error: Permiso denegado para leer las carpetas de canciones o letras.")
        return []
    except Exception as e:
        print(f"Error al leer las carpetas: {e}")
        return []
    
    available_pairs = []
    for song in song_files:
        song_name = os.path.splitext(song)[0]
        matching_lyrics = [l for l in lyrics_files if os.path.splitext(l)[0] == song_name]
        if matching_lyrics:
            available_pairs.append((os.path.join(SONGS_DIR, song), os.path.join(LYRICS_DIR, matching_lyrics[0])))
        else:
            # If no matching lyrics file exists but auto_extract is enabled, check if we can extract from MP3
            if auto_extract and song.lower().endswith('.mp3'):
                from lyrics_extractor import create_lrc_file_from_mp3
                song_path = os.path.join(SONGS_DIR, song)
                lrc_path = os.path.join(LYRICS_DIR, song_name + '.lrc')
                try:
                    created_path = create_lrc_file_from_mp3(song_path, lrc_path)
                    if os.path.exists(created_path):
                        available_pairs.append((song_path, created_path))
                except Exception as e:
                    print(f"No se pudo extraer letras para {song}: {e}")
    
    if not available_pairs:
        print("No se encontraron pares de canción/letra coincidentes.")
        # Try auto-extraction if no pairs found
        if auto_extract:
            print("Intentando extraer letras de archivos MP3...")
            auto_extract_lyrics_for_songs()
            # Try again after extraction
            return get_available_songs(auto_extract=False)  # Don't try to extract again
    
    return available_pairs


def format_time(seconds):
    """Format seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"


def show_message(message, message_type="info"):
    """Display a user-friendly message with optional type indication"""
    type_prefixes = {
        "error": "[ERROR]",
        "warning": "[WARNING]",
        "info": "[INFO]",
        "success": "[SUCCESS]"
    }
    
    prefix = type_prefixes.get(message_type, "[INFO]")
    print(f"{prefix} {message}")