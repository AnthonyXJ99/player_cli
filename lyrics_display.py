import random
import time
import threading
import math
import colorsys # Import colorsys
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.color import Color
from rich.progress import Progress, BarColumn, TextColumn
from config import DEFAULT_EQ_BANDS, CONSOLE_REFRESH_RATE
from visualizer import VisualizationModes

class LyricsDisplay:
    def __init__(self, num_eq_bands=DEFAULT_EQ_BANDS):
        self.console = Console(force_terminal=True)
        self.active = False
        self.live = None
        self.animation_thread = None
        self.layout = self._create_layout()

        # Estado del ecualizador (controlado externamente)
        self.num_eq_bands = num_eq_bands
        self.eq_bands = [0.0] * self.num_eq_bands
        self.decayed_eq_bands = [0.0] * self.num_eq_bands # For smoother decay
        self.smoothed_eq_bands = [0.0] * self.num_eq_bands  # For additional smoothing
        self.decay_rate = 0.2 # How fast bars fall, tune this value
        self.smoothing_factor = 0.3  # Smoothing factor for moving average
        self.hue_offset = 0.0 # For dynamic color cycling
        self.eq_lock = threading.Lock()
        
        # Visualization modes
        self.visualizer = VisualizationModes(num_bands=self.num_eq_bands)

        # Estado de las letras
        self.current_line_idx = -1
        self.completed_lyrics = []
        self.typing_line = None
        self.typing_progress = 0
        self.last_char_time = 0
        self.lyric_colors = ["bright_cyan", "bright_magenta", "bright_yellow", "bright_green", "bright_blue", "bright_red"]
        
        # Estado de la barra de progreso
        self.current_time = 0
        self.total_time = 0
        self.progress_text = Text("00:00 / 00:00", justify="center")

    def _create_layout(self):
        layout = Layout()
        layout.split(Layout(name="header", size=3), Layout(name="middle", ratio=1), Layout(name="progress", size=3))
        layout["header"].split_row(Layout(name="eq"))
        layout["middle"].split_column(Layout(name="lyrics"))
        layout["progress"].split_row(Layout(name="progress_bar"))
        return layout

    def update_eq(self, bands):
        """Método seguro para hilos para actualizar las bandas del ecualizador desde el player."""
        with self.eq_lock:
            for i in range(self.num_eq_bands):
                # Apply decay
                self.decayed_eq_bands[i] = max(self.decayed_eq_bands[i] - self.decay_rate, 0.0)
                # Update with new value (only if new value is higher)
                self.decayed_eq_bands[i] = max(self.decayed_eq_bands[i], bands[i])
                
                # Apply additional smoothing using moving average
                self.smoothed_eq_bands[i] = (
                    self.smoothing_factor * self.decayed_eq_bands[i] + 
                    (1 - self.smoothing_factor) * self.smoothed_eq_bands[i]
                )
    
    def update_progress(self, current_time, total_time):
        """Actualizar información de progreso de la reproducción"""
        self.current_time = current_time
        self.total_time = total_time
        self.progress_text = Text(f"{self._format_time(current_time)} / {self._format_time(total_time)}", justify="center")
    
    def _format_time(self, seconds):
        """Format seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def set_smoothing_factor(self, factor):
        """Adjust the smoothing factor (0.0 to 1.0)"""
        if 0.0 <= factor <= 1.0:
            self.smoothing_factor = factor
    
    def set_visualization_mode(self, mode):
        """Set the visualization mode: 'bars', 'waveform', 'spectrum'"""
        return self.visualizer.set_mode(mode)
    
    def get_visualization_mode(self):
        """Get the current visualization mode"""
        return self.visualizer.get_mode()

    def _generate_eq_text(self):
        """Genera un objeto Text de Rich a partir de los datos de las bandas del ecualizador."""
        # Use the visualization modes
        width = self.console.width or 80
        with self.eq_lock:
            # Use the smoothed bands for visualization
            bands_to_use = list(self.smoothed_eq_bands)
        return self.visualizer.generate_visualization(bands_to_use, width)

    def _animate(self):
        while self.active:
            # Increment hue_offset for color cycling
            self.hue_offset = (self.hue_offset + 0.01) % 1.0 # Tune this speed

            start_eq_gen_time = time.perf_counter()
            eq_text = self._generate_eq_text()
            end_eq_gen_time = time.perf_counter()
            # print(f"[DEBUG Lyrics] _generate_eq_text took: {(end_eq_gen_time - start_eq_gen_time)*1000:.2f} ms")

            start_eq_update_time = time.perf_counter()
            self.layout["eq"].update(Align.center(eq_text, vertical="middle"))
            end_eq_update_time = time.perf_counter()
            # print(f"[DEBUG Lyrics] layout[\"eq\"] update took: {(end_eq_update_time - start_eq_update_time)*1000:.2f} ms")

            start_typing_logic_time = time.perf_counter()
            if self.typing_line:
                text, color = self.typing_line
                if self.typing_progress < len(text) and (time.time() - self.last_char_time) > 0.05:
                    self.typing_progress += 1
                    self.last_char_time = time.time()
            end_typing_logic_time = time.perf_counter()
            # print(f"[DEBUG Lyrics] Typing logic took: {(end_typing_logic_time - start_typing_logic_time)*1000:.2f} ms")
            
            start_lyrics_render_time = time.perf_counter()
            lyric_renderable = Text(justify="center")
            for line, color in self.completed_lyrics:
                lyric_renderable.append(f"{line}\n", style=color)
            if self.typing_line:
                text, color = self.typing_line
                lyric_renderable.append(text[:self.typing_progress], style=color)
            end_lyrics_render_time = time.perf_counter()
            # print(f"[DEBUG Lyrics] Lyrics rendering took: {(end_lyrics_render_time - start_lyrics_render_time)*1000:.2f} ms")

            start_lyrics_update_time = time.perf_counter()
            self.layout["lyrics"].update(Align.center(lyric_renderable, vertical="top"))
            end_lyrics_update_time = time.perf_counter()
            # print(f"[DEBUG Lyrics] layout[\"lyrics\"] update took: {(end_lyrics_update_time - start_lyrics_update_time)*1000:.2f} ms")

            # Update progress bar
            progress_percentage = (self.current_time / self.total_time) * 100 if self.total_time > 0 else 0
            progress_description = f"{self._format_time(self.current_time)} / {self._format_time(self.total_time)}"
            
            # Create a simple progress representation without Rich's Progress
            bar_length = 50  # Length of the progress bar in characters
            filled_length = int(bar_length * progress_percentage / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            progress_text = f"[{bar}] {progress_percentage:.1f}% {progress_description}"
            
            from rich.panel import Panel
            progress_panel = Panel(progress_text, title="Progress", border_style="blue")
            self.layout["progress_bar"].update(Align.center(progress_panel, vertical="middle"))

            time.sleep(0.05)

    def update_current_line(self, lyrics, current_time, player):
        current_line_idx = -1
        for i, lyric in enumerate(lyrics):
            lyric_seconds = lyric.minutes * 60 + lyric.seconds + lyric.milliseconds / 1000.0
            if current_time >= lyric_seconds:
                current_line_idx = i
            else:
                break
        
        if current_line_idx != self.current_line_idx:
            if self.typing_line:
                full_text, color = self.typing_line
                self.completed_lyrics.append((full_text, color))
                if len(self.completed_lyrics) > 10:
                    self.completed_lyrics.pop(0)

            self.current_line_idx = current_line_idx
            if 0 <= current_line_idx < len(lyrics):
                self.typing_line = (lyrics[current_line_idx].text, random.choice(self.lyric_colors))
                self.typing_progress = 0
                self.last_char_time = time.time()

    def start(self):
        self.active = True
        self.live = Live(self.layout, console=self.console, refresh_per_second=10)
        self.live.start(refresh=True)
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def stop(self):
        self.active = False
        if self.animation_thread:
            self.animation_thread.join()
        if self.live:
            self.live.stop()
        self.console.clear()
