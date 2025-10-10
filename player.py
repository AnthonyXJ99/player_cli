import pygame
import pylrc
import time
import threading
import numpy as np
from pydub import AudioSegment
from lyrics_display import LyricsDisplay
import tempfile
import os

class MusicPlayer:
    def __init__(self, num_eq_bands=16):
        self.num_eq_bands = num_eq_bands
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.lyrics_display = LyricsDisplay(num_eq_bands=self.num_eq_bands)
        self.song_loaded = False
        self.paused = False
        self.stopped = True

        self.raw_data = None
        self.sample_rate = 0
        self.channels = 0
        self.chunk_size = 2048 # This will now be the analysis chunk size
        self.music_file_path = None # To store path to temporary audio file
        self.analysis_thread = None # Renamed from stream_thread

    def load_song(self, song_path, lyrics_path):
        audio_segment = AudioSegment.from_file(song_path)
        self.sample_rate = audio_segment.frame_rate
        self.channels = audio_segment.channels
        
        # Ensure mixer is initialized with correct frequency/channels for analysis
        pygame.mixer.quit()
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=self.channels, buffer=self.chunk_size)

        # Store raw data for analysis
        samples = np.array(audio_segment.get_array_of_samples())
        if self.channels == 2:
            self.raw_data = samples.reshape((-1, 2))
        else:
            self.raw_data = np.repeat(samples[:, np.newaxis], 2, axis=1)

        # Create a temporary file for pygame.mixer.music
        if self.music_file_path and os.path.exists(self.music_file_path):
            os.remove(self.music_file_path)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            audio_segment.export(tmp_file.name, format="wav")
            self.music_file_path = tmp_file.name
        
        pygame.mixer.music.load(self.music_file_path)

        self.song_loaded = True
        print(f"Canción cargada: {song_path} ({self.sample_rate} Hz, {self.channels} canales)")

        try:
            with open(lyrics_path, 'r', encoding='utf-8') as f:
                self.lyrics = pylrc.parse(f.read())
            print(f"Letras cargadas: {lyrics_path}")
        except Exception as e:
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

    def _calculate_eq_bands(self, mono_chunk):
        # Aplicar FFT
        fft_result = np.fft.rfft(mono_chunk)
        fft_magnitude = np.abs(fft_result)

        # Escala logarítmica para las frecuencias
        min_freq = 20
        max_freq = self.sample_rate / 2
        log_freq_space = np.logspace(np.log10(min_freq), np.log10(max_freq), self.num_eq_bands + 1)
        
        bands = []
        fft_freqs = np.fft.rfftfreq(len(mono_chunk), 1.0 / self.sample_rate)

        for i in range(self.num_eq_bands):
            start_idx = np.searchsorted(fft_freqs, log_freq_space[i])
            end_idx = np.searchsorted(fft_freqs, log_freq_space[i+1])
            if start_idx == end_idx:
                bands.append(0)
                continue
            avg_magnitude = np.mean(fft_magnitude[start_idx:end_idx])
            bands.append(avg_magnitude)

        if not bands:
            return [0.0] * self.num_eq_bands

        # Normalización mejorada
        bands = np.array(bands)
        bands = np.log1p(bands * 5) # Aplicar ganancia y escala logarítmica
        
        # Usar un techo fijo o un máximo dinámico más estable para normalizar
        # Esto evita que el ecualizador "salte" mucho con los cambios de volumen
        max_val = max(5.0, np.max(bands)) # Evita la división por cero y estabiliza
        if max_val > 0:
            bands = bands / max_val
        
        return np.clip(bands, 0, 1).tolist()

    def _analyze_audio_and_update_display(self):
        # This thread will now only analyze audio and update display, not play audio
        total_samples = len(self.raw_data)
        analysis_interval_ms = 100 # Analyze every 100 ms
        analysis_chunk_samples = int(self.sample_rate * (analysis_interval_ms / 1000.0))

        while not self.stopped:
            if self.paused:
                time.sleep(0.1)
                continue

            current_playback_ms = pygame.mixer.music.get_pos()
            if current_playback_ms == -1: # Music has stopped or not playing
                break

            current_sample_pos = int(current_playback_ms / 1000.0 * self.sample_rate)
            
            # Ensure we don't go out of bounds
            start_sample = max(0, current_sample_pos - analysis_chunk_samples // 2) # Center chunk around current pos
            end_sample = min(total_samples, start_sample + analysis_chunk_samples)
            
            if end_sample - start_sample < analysis_chunk_samples // 2: # Not enough samples for a full chunk at the end
                break

            chunk_to_analyze = self.raw_data[start_sample:end_sample]
            
            if len(chunk_to_analyze) == 0:
                break

            # Normalizar el chunk a [-1.0, 1.0] para el análisis FFT
            mono_chunk_int = chunk_to_analyze.mean(axis=1)
            normalized_chunk = mono_chunk_int / 32768.0

            eq_bands = self._calculate_eq_bands(normalized_chunk)
            self.lyrics_display.update_eq(eq_bands)

            current_time_sec = current_playback_ms / 1000.0
            if self.lyrics:
                self.lyrics_display.update_current_line(self.lyrics, current_time_sec, self)

            time.sleep(analysis_interval_ms / 1000.0) # Sleep to control analysis frequency
        
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
        pygame.mixer.music.unload() # Explicitly unload the music
        if self.analysis_thread:
            self.analysis_thread.join()
        
        # Clean up temporary music file
        if self.music_file_path and os.path.exists(self.music_file_path):
            try:
                os.remove(self.music_file_path)
            except PermissionError:
                print(f"[WARNING] Could not remove temporary file: {self.music_file_path}. It might still be in use.")
            self.music_file_path = None

    def is_playing(self):
        return self.song_loaded and not self.stopped and not self.paused and pygame.mixer.music.get_busy()

    def is_paused(self):
        return self.paused and not self.stopped