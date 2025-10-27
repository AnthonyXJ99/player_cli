"""Different audio visualization modes for the music player"""

import numpy as np
import colorsys
from rich.text import Text
from rich.align import Align
from config import DEFAULT_EQ_BANDS


class VisualizationModes:
    def __init__(self, num_bands=DEFAULT_EQ_BANDS):
        self.num_bands = num_bands
        self.current_mode = "bars"  # Default visualization mode
        self.bar_chars = " ▁▂▃▄▅▆▇█"
        self.wave_chars = "       .-~=+*#%@"
        
    def set_mode(self, mode):
        """Set the visualization mode: 'bars', 'waveform', 'spectrum'"""
        valid_modes = ["bars", "waveform", "spectrum"]
        if mode in valid_modes:
            self.current_mode = mode
            return True
        return False
    
    def get_mode(self):
        """Get the current visualization mode"""
        return self.current_mode
    
    def generate_visualization(self, bands, console_width):
        """Generate visualization based on current mode"""
        if self.current_mode == "bars":
            return self._generate_bars_visualization(bands, console_width)
        elif self.current_mode == "waveform":
            return self._generate_waveform_visualization(bands, console_width)
        elif self.current_mode == "spectrum":
            return self._generate_spectrum_visualization(bands, console_width)
        else:
            # Fallback to bars
            return self._generate_bars_visualization(bands, console_width)
    
    def _generate_bars_visualization(self, bands, console_width):
        """Generate the original bar visualization"""
        text = Text()
        num_chars = len(self.bar_chars)
        
        for i in range(console_width):
            band_index = min(int(i * self.num_bands / console_width), self.num_bands - 1)
            band_height = bands[band_index] if band_index < len(bands) else 0

            # Map height (0.0-1.0) to a bar character
            char_index = min(int(band_height * (num_chars - 1)), num_chars - 1)
            char = self.bar_chars[char_index]
            
            # Dynamic color based on position and height
            hue = (i / console_width) % 1.0
            sat = 0.8
            light = 0.5 + band_height * 0.4
            
            r, g, b = colorsys.hls_to_rgb(hue, light, sat)
            color_hex = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            text.append(char, style=color_hex)
        
        return text
    
    def _generate_waveform_visualization(self, bands, console_width):
        """Generate a waveform like visualization"""
        text = Text()
        # Normalize and center the waveform
        for i in range(console_width):
            band_index = min(int(i * self.num_bands / console_width), self.num_bands - 1)
            amplitude = bands[band_index] if band_index < len(bands) else 0
            
            # Waveform character based on amplitude
            char_index = min(int(amplitude * (len(self.wave_chars) - 1)), len(self.wave_chars) - 1)
            char = self.wave_chars[char_index]
            
            # Color based on amplitude
            hue = 0.3  # Green-blue hue for waveform
            sat = 0.7
            light = 0.3 + amplitude * 0.6
            
            r, g, b = colorsys.hls_to_rgb(hue, light, sat)
            color_hex = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            text.append(char, style=color_hex)
        
        return text
    
    def _generate_spectrum_visualization(self, bands, console_width):
        """Generate a spectrum analyzer like visualization"""
        text = Text()
        
        # Create a spectrum effect by interpolating bands to fill console width
        for i in range(console_width):
            # Map console position to band index
            band_pos = (i / console_width) * (self.num_bands - 1)
            low_band = int(band_pos)
            high_band = min(low_band + 1, self.num_bands - 1)
            ratio = band_pos - low_band
            
            # Interpolate between adjacent bands
            if low_band < len(bands) and high_band < len(bands):
                amplitude = bands[low_band] * (1 - ratio) + bands[high_band] * ratio
            elif low_band < len(bands):
                amplitude = bands[low_band]
            else:
                amplitude = 0
            
            # Spectrum character (use different characters for different frequencies)
            if amplitude < 0.2:
                char = " "
            elif amplitude < 0.4:
                char = "."
            elif amplitude < 0.6:
                char = "o"
            elif amplitude < 0.8:
                char = "O"
            else:
                char = "@"
            
            # Color based on position (low to high frequencies)
            hue = (i / console_width) * 0.33  # Red to green range
            sat = 0.9
            light = 0.4 + amplitude * 0.5
            
            r, g, b = colorsys.hls_to_rgb(hue, light, sat)
            color_hex = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
            text.append(char, style=color_hex)
        
        return text