"""Audio processing module for FFT analysis and equalizer data generation"""

import numpy as np
from pydub import AudioSegment
import tempfile
import os


class AudioProcessor:
    def __init__(self, num_eq_bands=16):
        self.num_eq_bands = num_eq_bands
        self.raw_data = None
        self.sample_rate = 0
        self.channels = 0
        self.chunk_size = 2048
        self.music_file_path = None

    def load_audio(self, song_path):
        """Load audio file and prepare for analysis"""
        audio_segment = AudioSegment.from_file(song_path)
        self.sample_rate = audio_segment.frame_rate
        self.channels = audio_segment.channels

        # Store raw data for analysis
        samples = np.array(audio_segment.get_array_of_samples())
        if self.channels == 2:
            self.raw_data = samples.reshape((-1, 2))
        else:
            self.raw_data = np.repeat(samples[:, np.newaxis], 2, axis=1)

        # Calculate duration
        self.duration = len(audio_segment) / 1000.0  # Duration in seconds
        
        # Create a temporary file for pygame.mixer.music
        if self.music_file_path and os.path.exists(self.music_file_path):
            os.remove(self.music_file_path)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            audio_segment.export(tmp_file.name, format="wav")
            self.music_file_path = tmp_file.name
        
        return self.music_file_path

    def calculate_eq_bands(self, mono_chunk):
        """Calculate equalizer bands from audio chunk"""
        # Apply FFT
        fft_result = np.fft.rfft(mono_chunk)
        fft_magnitude = np.abs(fft_result)

        # Logarithmic scale for frequencies
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

        # Enhanced normalization
        bands = np.array(bands)
        bands = np.log1p(bands * 5)  # Apply gain and logarithmic scale
        
        # Use a fixed ceiling or more stable dynamic maximum for normalization
        max_val = max(5.0, np.max(bands))  # Prevents division by zero and stabilizes
        if max_val > 0:
            bands = bands / max_val
        
        return np.clip(bands, 0, 1).tolist()

    def get_audio_chunk(self, current_playback_ms, analysis_chunk_samples):
        """Extract audio chunk for analysis based on current playback position"""
        if self.raw_data is None:
            return np.array([])
        
        total_samples = len(self.raw_data)
        current_sample_pos = int(current_playback_ms / 1000.0 * self.sample_rate)
        
        # Ensure we don't go out of bounds
        start_sample = max(0, current_sample_pos - analysis_chunk_samples // 2)  # Center chunk around current pos
        end_sample = min(total_samples, start_sample + analysis_chunk_samples)
        
        if end_sample - start_sample < analysis_chunk_samples // 2:  # Not enough samples for a full chunk at the end
            return np.array([])

        chunk_to_analyze = self.raw_data[start_sample:end_sample]
        
        if len(chunk_to_analyze) == 0:
            return np.array([])

        # Normalize chunk to [-1.0, 1.0] for FFT analysis
        mono_chunk_int = chunk_to_analyze.mean(axis=1)
        normalized_chunk = mono_chunk_int / 32768.0

        return normalized_chunk

    def get_duration(self):
        """Get the total duration of the loaded audio in seconds"""
        return getattr(self, 'duration', 0)

    def cleanup(self):
        """Clean up temporary audio file"""
        if self.music_file_path and os.path.exists(self.music_file_path):
            try:
                os.remove(self.music_file_path)
            except PermissionError:
                pass  # Gracefully ignore if file is still in use
            self.music_file_path = None