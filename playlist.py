"""Playlist management module"""

from utils import get_available_songs


class Playlist:
    def __init__(self):
        self.songs = get_available_songs()
        self.current_index = -1
        self.is_shuffled = False
        self.repeat_mode = "none"  # "none", "one", "all"
        self._original_order = list(self.songs)  # Keep original order for shuffle

    def add_song(self, song_path, lyrics_path):
        """Add a song to the playlist"""
        self.songs.append((song_path, lyrics_path))
        self._original_order = list(self.songs)

    def remove_song(self, index):
        """Remove a song from the playlist by index"""
        if 0 <= index < len(self.songs):
            self.songs.pop(index)
            if self.current_index >= len(self.songs):
                self.current_index = len(self.songs) - 1
            self._original_order = list(self.songs)

    def get_current_song(self):
        """Get the current song in the playlist"""
        if 0 <= self.current_index < len(self.songs):
            return self.songs[self.current_index]
        return None

    def get_next_song(self):
        """Get the next song in the playlist"""
        if not self.songs:
            return None

        if self.repeat_mode == "one":
            return self.songs[self.current_index]
        elif self.repeat_mode == "all" and self.current_index == len(self.songs) - 1:
            self.current_index = 0
            return self.songs[0]
        elif self.current_index < len(self.songs) - 1:
            self.current_index += 1
            return self.songs[self.current_index]
        else:
            return None

    def get_prev_song(self):
        """Get the previous song in the playlist"""
        if not self.songs:
            return None

        if self.current_index > 0:
            self.current_index -= 1
            return self.songs[self.current_index]
        elif self.repeat_mode == "all":
            self.current_index = len(self.songs) - 1
            return self.songs[self.current_index]
        else:
            return None

    def set_current_index(self, index):
        """Set the current song index"""
        if 0 <= index < len(self.songs):
            self.current_index = index

    def shuffle(self):
        """Shuffle the playlist"""
        import random
        self.is_shuffled = not self.is_shuffled
        if self.is_shuffled:
            # Shuffle all but maintain current song at position 0 temporarily
            temp_songs = self.songs[:]
            shuffled_songs = temp_songs[1:]  # Exclude current song
            random.shuffle(shuffled_songs)
            self.songs = [temp_songs[0]] + shuffled_songs if len(temp_songs) > 0 else shuffled_songs
        else:
            # Restore original order
            self.songs = list(self._original_order)

    def get_current_index(self):
        """Get the current song index"""
        return self.current_index

    def get_song_count(self):
        """Get the total number of songs in the playlist"""
        return len(self.songs)

    def toggle_repeat(self):
        """Toggle through repeat modes: none -> all -> one -> none"""
        if self.repeat_mode == "none":
            self.repeat_mode = "all"
        elif self.repeat_mode == "all":
            self.repeat_mode = "one"
        else:
            self.repeat_mode = "none"
        return self.repeat_mode

    def get_current_song_name(self):
        """Get the current song name without path and extension"""
        song = self.get_current_song()
        if song:
            import os
            return os.path.splitext(os.path.basename(song[0]))[0]
        return "No song"