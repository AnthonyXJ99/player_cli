import pygame
import pylrc
import time
import threading
from audio_processor import AudioProcessor
from lyrics_display import LyricsDisplay
from playlist import Playlist
import os
from config import DEFAULT_EQ_BANDS

class MusicPlayer:
    def __init__(self, num_eq_bands=DEFAULT_EQ_BANDS):
        self.num_eq_bands = num_eq_bands
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.lyrics_display = LyricsDisplay(num_eq_bands=self.num_eq_bands)
        self.song_loaded = False
        self.paused = False
        self.stopped = True
        
        # Audio processor instance
        self.audio_processor = AudioProcessor(num_eq_bands=self.num_eq_bands)
        
        # Playlist instance
        self.playlist = Playlist()
        
        self.lyrics = None
        self.analysis_thread = None
        self.volume = 1.0

    def load_song(self, song_path, lyrics_path):
        try:
            # Load audio using audio processor
            music_file_path = self.audio_processor.load_audio(song_path)
            pygame.mixer.music.load(music_file_path)

            self.song_loaded = True

            try:
                with open(lyrics_path, 'r', encoding='utf-8') as f:
                    self.lyrics = pylrc.parse(f.read())
            except Exception as e:
                print(f"Warning: Could not load lyrics file: {e}")
                self.lyrics = None
            
            # Get and display song information
            song_info = self.get_song_info(song_path)
            if hasattr(self.lyrics_display, 'update_song_info'):
                self.lyrics_display.update_song_info(song_info)
                
        except Exception as e:
            print(f"Error loading song: {e}")
            self.song_loaded = False
            self.lyrics = None

    def play(self):
        if not self.song_loaded:
            return
        self.stopped = False
        self.paused = False
        self.lyrics_display.start()
        pygame.mixer.music.play() # Start music playback
        self.analysis_thread = threading.Thread(target=self._analyze_audio_and_update_display)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()

    # Removed the private _calculate_eq_bands method as it's now in the AudioProcessor class

    def _analyze_audio_and_update_display(self):
        # This thread will now only analyze audio and update display, not play audio
        analysis_chunk_samples = int(self.audio_processor.sample_rate * 0.1)  # 100ms chunks

        while not self.stopped:
            if self.paused:
                time.sleep(0.1)
                continue

            current_playback_ms = pygame.mixer.music.get_pos()
            if current_playback_ms == -1:  # Music has stopped or not playing
                break

            # Get audio chunk for analysis
            normalized_chunk = self.audio_processor.get_audio_chunk(current_playback_ms, analysis_chunk_samples)
            
            if len(normalized_chunk) == 0:
                break

            eq_bands = self.audio_processor.calculate_eq_bands(normalized_chunk)
            self.lyrics_display.update_eq(eq_bands)

            current_time_sec = current_playback_ms / 1000.0
            total_time = self.audio_processor.get_duration()
            self.lyrics_display.update_progress(current_time_sec, total_time)
            if self.lyrics:
                self.lyrics_display.update_current_line(self.lyrics, current_time_sec, self)

            time.sleep(0.1)  # Sleep to control analysis frequency
        
        self.stop()

    def pause(self):
        self.paused = True
        pygame.mixer.music.pause()
        
    def unpause(self):
        self.paused = False
        pygame.mixer.music.unpause()
        
    def stop(self):
        if self.stopped:
            return
        self.stopped = True
        self.lyrics_display.stop()
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()  # Explicitly unload the music
        
        # Only join the analysis thread if it's not the current thread
        if self.analysis_thread and self.analysis_thread != threading.current_thread():
            self.analysis_thread.join()
        elif self.analysis_thread:
            # If it's the same thread, just reset the reference
            self.analysis_thread = None
        
        # Clean up audio processor resources
        self.audio_processor.cleanup()

    def is_playing(self):
        return self.song_loaded and not self.stopped and not self.paused and pygame.mixer.music.get_busy()

    def is_paused(self):
        return self.paused and not self.stopped
        
    def set_volume(self, volume):
        """Set volume level (0.0 to 1.0)"""
        if 0.0 <= volume <= 1.0:
            self.volume = volume
            pygame.mixer.music.set_volume(volume)
            # Update visual volume indicator
            if hasattr(self.lyrics_display, 'update_volume_display'):
                self.lyrics_display.update_volume_display(volume)
    
    def get_volume(self):
        """Get current volume level"""
        return self.volume
    
    def increase_volume(self):
        """Increase volume by 0.1"""
        new_volume = min(1.0, self.volume + 0.1)
        self.set_volume(new_volume)
        return new_volume
    
    def decrease_volume(self):
        """Decrease volume by 0.1"""
        new_volume = max(0.0, self.volume - 0.1)
        self.set_volume(new_volume)
        return new_volume
    
    def next_track(self):
        """Play the next track in the playlist"""
        next_song = self.playlist.get_next_song()
        if next_song:
            song_path, lyrics_path = next_song
            self.stop()  # Stop current playback
            self.load_song(song_path, lyrics_path)
            self.play()
            return True
        return False
    
    def prev_track(self):
        """Play the previous track in the playlist"""
        prev_song = self.playlist.get_prev_song()
        if prev_song:
            song_path, lyrics_path = prev_song
            self.stop()  # Stop current playback
            self.load_song(song_path, lyrics_path)
            self.play()
            return True
        return False
    
    def load_playlist(self):
        """Load the playlist from available songs"""
        self.playlist = Playlist()
    
    def get_current_track_info(self):
        """Get information about the current track"""
        return {
            'track_number': self.playlist.get_current_index() + 1,
            'total_tracks': self.playlist.get_song_count(),
            'track_name': self.playlist.get_current_song_name()
        }
    
    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.playlist.shuffle()
    
    def toggle_repeat(self):
        """Toggle repeat mode"""
        return self.playlist.toggle_repeat()
    
    def set_visualization_mode(self, mode):
        """Set the visualization mode: 'bars', 'waveform', 'spectrum'"""
        return self.lyrics_display.set_visualization_mode(mode)
    
    def cycle_visualization_mode(self):
        """Cycle through visualization modes"""
        current_mode = self.lyrics_display.get_visualization_mode()
        if current_mode == "bars":
            new_mode = "waveform"
        elif current_mode == "waveform":
            new_mode = "spectrum"
        else:
            new_mode = "bars"
        self.lyrics_display.set_visualization_mode(new_mode)
        return new_mode
    
    def get_song_info(self, song_path):
        """Get song information like duration, artist, title from file"""
        try:
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3NoHeaderError
            audio = MP3(song_path)
            
            info = {
                'duration': audio.info.length if audio else 0,
                'bitrate': audio.info.bitrate if audio else 0,
                'sample_rate': audio.info.sample_rate if audio else 0
            }
            
            # Try to get ID3 tags
            try:
                tags = ID3(song_path)
                info['title'] = str(tags.get("TIT2", "")) or os.path.splitext(os.path.basename(song_path))[0]
                info['artist'] = str(tags.get("TPE1", "")) or "Unknown Artist"
                info['album'] = str(tags.get("TALB", "")) or "Unknown Album"
            except ID3NoHeaderError:
                # No ID3 tags, use filename
                info['title'] = os.path.splitext(os.path.basename(song_path))[0]
                info['artist'] = "Unknown Artist"
                info['album'] = "Unknown Album"
                
            return info
        except:
            # Fallback if mutagen fails
            return {
                'title': os.path.splitext(os.path.basename(song_path))[0],
                'artist': "Unknown Artist",
                'album': "Unknown Album",
                'duration': 0,
                'bitrate': 0,
                'sample_rate': 0
            }