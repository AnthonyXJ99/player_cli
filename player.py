import pygame
import pylrc
import time
import threading
import numpy as np
from pydub import AudioSegment
from lyrics_display import LyricsDisplay



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
        self.chunk_size = 2048
        self.current_pos = 0
        self.stream_thread = None

    def load_song(self, song_path, lyrics_path):
        audio_segment = AudioSegment.from_file(song_path)
        self.sample_rate = audio_segment.frame_rate
        self.channels = audio_segment.channels
        
        pygame.mixer.quit()
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=self.channels, buffer=self.chunk_size)

        samples = np.array(audio_segment.get_array_of_samples())
        if self.channels == 2:
            self.raw_data = samples.reshape((-1, 2))
        else:
            self.raw_data = np.repeat(samples[:, np.newaxis], 2, axis=1)

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
        self.stream_thread = threading.Thread(target=self._stream_and_analyze)
        self.stream_thread.daemon = True
        self.stream_thread.start()

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

    def _stream_and_analyze(self):
        num_samples = len(self.raw_data)
        while self.current_pos < num_samples and not self.stopped:
            if self.paused:
                time.sleep(0.1)
                continue

            end_pos = self.current_pos + self.chunk_size
            chunk = self.raw_data[self.current_pos:end_pos]
            
            if len(chunk) == 0:
                break

            # Timing for sound creation and playback
            start_sound_time = time.perf_counter()
            sound = pygame.sndarray.make_sound(chunk)
            sound.play()
            end_sound_time = time.perf_counter()
            # print(f"[DEBUG Player] Sound creation and play took: {(end_sound_time - start_sound_time)*1000:.2f} ms")

            # Normalizar el chunk a [-1.0, 1.0] para el análisis FFT
            mono_chunk_int = chunk.mean(axis=1)
            normalized_chunk = mono_chunk_int / 32768.0

            # Timing for EQ calculation
            start_eq_calc_time = time.perf_counter()
            eq_bands = self._calculate_eq_bands(normalized_chunk)
            end_eq_calc_time = time.perf_counter()
            # print(f"[DEBUG Player] EQ calculation took: {(end_eq_calc_time - start_eq_calc_time)*1000:.2f} ms")

            # Timing for lyrics_display.update_eq
            start_update_eq_time = time.perf_counter()
            self.lyrics_display.update_eq(eq_bands)
            end_update_eq_time = time.perf_counter()
            # print(f"[DEBUG Player] lyrics_display.update_eq took: {(end_update_eq_time - start_update_eq_time)*1000:.2f} ms")

            current_time_sec = self.current_pos / self.sample_rate
            if self.lyrics:
                # Timing for lyrics_display.update_current_line
                start_update_lyrics_time = time.perf_counter()
                self.lyrics_display.update_current_line(self.lyrics, current_time_sec, self)
                end_update_lyrics_time = time.perf_counter()
                # print(f"[DEBUG Player] lyrics_display.update_current_line took: {(end_update_lyrics_time - start_update_lyrics_time)*1000:.2f} ms")

            chunk_duration = len(chunk) / self.sample_rate
            sleep_duration = chunk_duration * 0.95
            # print(f"[DEBUG Player] Chunk duration: {chunk_duration*1000:.2f} ms, Sleeping for: {sleep_duration*1000:.2f} ms")
            time.sleep(sleep_duration)
            
            self.current_pos += len(chunk)
        
        self.stop()

    def pause(self):
        self.paused = True
        pygame.mixer.pause()
        
    def unpause(self):
        self.paused = False
        pygame.mixer.unpause()
        
    def stop(self):
        if self.stopped:
            return
        self.stopped = True
        self.lyrics_display.stop()
        pygame.mixer.stop()
        if self.stream_thread:
            self.stream_thread.join()

    def is_playing(self):
        return self.song_loaded and not self.stopped and not self.paused

    def is_paused(self):
        return self.paused