"""Utility functions for the music player"""

import os
from config import SONGS_DIR, LYRICS_DIR


def get_available_songs():
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
    
    if not available_pairs:
        print("No se encontraron pares de canción/letra coincidentes.")
    
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