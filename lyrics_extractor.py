"""Module for extracting lyrics from MP3 files and handling lyric synchronization"""

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT, APIC
import os
import re
from pylrc.classes import LyricLine
from pylrc.parser import parse as parse_lrc


def extract_lyrics_from_mp3(mp3_path):
    """Extract lyrics from MP3 file if embedded"""
    try:
        audio_file = ID3(mp3_path)
        # Look for unsynchronized lyrics (USLT tag)
        for tag in audio_file.getall("USLT"):
            return str(tag)
    except Exception as e:
        print(f"Error extracting lyrics from MP3: {e}")
        return None
    return None


def extract_synced_lyrics_from_mp3(mp3_path):
    """Extract synchronized lyrics from MP3 file if embedded"""
    try:
        audio_file = ID3(mp3_path)
        # Look for synchronized lyrics (SYLT tag)
        for tag in audio_file.getall("SYLT"):
            # Convert synchronized lyrics to LRC format
            return convert_synced_to_lrc(tag)
    except Exception as e:
        print(f"Error extracting synchronized lyrics from MP3: {e}")
        return None
    return None


def convert_synced_to_lrc(synced_lyrics):
    """Convert synchronized lyrics to LRC format string"""
    # This is a simplified conversion - real implementation would depend on the format
    # For now, we'll return a basic string
    if hasattr(synced_lyrics, 'text') and synced_lyrics.text:
        # Extract time stamps and text from synchronized lyrics
        # This is a simplified example - real implementation would need to parse the SYLT format properly
        return synced_lyrics.text
    return None


def create_lrc_file_from_mp3(mp3_path, output_lrc_path=None):
    """Create an LRC file from embedded lyrics in MP3"""
    if not output_lrc_path:
        output_lrc_path = mp3_path.replace('.mp3', '.lrc')
    
    # Check if lyrics are already available in the .lrc file
    if os.path.exists(output_lrc_path):
        print(f"Lyrics file already exists: {output_lrc_path}")
        return output_lrc_path
    
    # Try to extract unsynchronized lyrics
    lyrics = extract_lyrics_from_mp3(mp3_path)
    if lyrics:
        with open(output_lrc_path, 'w', encoding='utf-8') as f:
            f.write(lyrics)
        print(f"Lyrics extracted and saved to: {output_lrc_path}")
        return output_lrc_path
    
    # If no lyrics found, create an empty LRC file
    with open(output_lrc_path, 'w', encoding='utf-8') as f:
        f.write("[00:00.00]No lyrics found\n")
    
    print(f"No lyrics found in MP3. Created empty LRC file: {output_lrc_path}")
    return output_lrc_path


def extract_and_sync_lyrics(mp3_path, lrc_path):
    """Extract lyrics from MP3 and synchronize with LRC file if possible"""
    # First, try to create LRC from embedded lyrics
    created_lrc = create_lrc_file_from_mp3(mp3_path, lrc_path)
    
    # Parse the LRC file to ensure it's properly formatted
    try:
        with open(created_lrc, 'r', encoding='utf-8') as f:
            lrc_content = f.read()
        
        # Ensure the LRC file has proper format
        if not lrc_content.strip().startswith('[') and lrc_content.strip():
            # If not in LRC format, try to convert plain text to basic LRC
            formatted_lrc = format_to_basic_lrc(lrc_content)
            with open(created_lrc, 'w', encoding='utf-8') as f:
                f.write(formatted_lrc)
        
        return created_lrc
    except Exception as e:
        print(f"Error processing LRC file: {e}")
        return None


def format_to_basic_lrc(plain_text):
    """Convert plain text lyrics to basic LRC format"""
    lines = plain_text.split('\n')
    lrc_lines = []
    
    for i, line in enumerate(lines):
        if line.strip():
            # Simple timing - 5 seconds per line starting from 00:10
            time_seconds = 10 + (i * 5)
            minutes = int(time_seconds // 60)
            seconds = int(time_seconds % 60)
            lrc_line = f"[{minutes:02d}:{seconds:02d}.00]{line.strip()}\n"
            lrc_lines.append(lrc_line)
    
    return ''.join(lrc_lines)


def extract_album_art_from_mp3(mp3_path, output_path=None):
    """Extract album art from MP3 file if embedded"""
    try:
        audio_file = ID3(mp3_path)
        for tag in audio_file.getall("APIC"):
            if output_path is None:
                # Create output path based on MP3 filename
                output_path = mp3_path.replace('.mp3', '_cover.jpg')
            
            with open(output_path, 'wb') as img_file:
                img_file.write(tag.data)
            print(f"Album art extracted to: {output_path}")
            return output_path
    except Exception as e:
        print(f"Error extracting album art from MP3: {e}")
        return None
    return None


def auto_extract_lyrics_for_songs():
    """Auto-extract lyrics for all songs in the songs directory"""
    from utils import get_available_songs
    
    songs_with_lyrics = get_available_songs()
    new_lyrics_created = 0
    
    for song_path, lyrics_path in songs_with_lyrics:
        # Check if lyrics file exists, if not try to extract from MP3
        if not os.path.exists(lyrics_path):
            print(f"Attempting to extract lyrics for: {os.path.basename(song_path)}")
            try:
                create_lrc_file_from_mp3(song_path, lyrics_path)
                new_lyrics_created += 1
            except Exception as e:
                print(f"Could not extract lyrics for {song_path}: {e}")
    
    print(f"Auto extraction completed. {new_lyrics_created} new lyrics files created.")
    return new_lyrics_created