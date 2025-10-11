# Music Player with Console Lyrics and Equalizer

A console-based music player that displays real-time synchronized lyrics and a dynamic visual equalizer.

## Features

-   **Audio Playback**: Smooth playback of audio files (MP3, WAV, OGG) using `pygame.mixer`.
-   **Synchronized Lyrics**: Displays lyrics from LRC files with a "typing" effect synchronized to the music.
-   **Dynamic Visual Equalizer**: A real-time console equalizer built with `rich`, featuring:
    -   Smooth bar transitions with a decay effect.
    -   Dynamic color cycling based on HSL for a vibrant look.
-   **Rich Console UI**: An attractive and modern user interface powered by the `rich` library.
-   **Playback Controls**: Basic controls for pause/resume, stop, and exit.

## Core Libraries

This project relies on several key Python libraries:

-   **Pygame**: Handles audio playback.
-   **Rich**: Powers the entire console user interface, including the layout, colors, and equalizer animation.
-   **Pydub**: Provides compatibility for various audio formats (like MP3) by converting them to WAV format for Pygame.
-   **Numpy**: Performs the Fast Fourier Transform (FFT) on raw audio data to generate the equalizer bands.
-   **PyLRC**: Parses the `.lrc` files to synchronize lyrics with the audio playback time.

## Installation

1.  Clone this repository.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ensure your terminal supports ANSI colors and Unicode characters for the best visual experience.

## Usage

1.  Place your music files (e.g., `.mp3`) in the `songs/` directory.
2.  Place the corresponding `.lrc` lyric files in the `lyrics/` directory.
    -   **Important**: The lyric file must have the *same name* as the song file (e.g., `song.mp3` and `song.lrc`).
3.  Run the application from the project root:
    ```bash
    python main.py
    ```
4.  The program will list the available songs. Select one by entering its number and pressing Enter.

## Controls

-   `p` - Pause / Resume
-   `s` - Stop playback and return to the menu
-   `q` - Quit the application

## Technical Implementation

-   **Audio Processing**: To play formats like MP3, the player first uses `pydub` to load the audio file and convert it into a temporary WAV file. `pygame.mixer.music` then loads and plays this temporary file. The raw audio data is kept in a `numpy` array for analysis.
-   **Threading Model**: The application uses multiple threads to ensure a smooth, non-blocking experience:
    1.  **Main Thread**: Handles user input (`msvcrt`).
    2.  **Pygame Audio Thread**: `pygame.mixer.music` runs playback in its own background thread.
    3.  **Analysis Thread**: A dedicated thread reads the current song position, extracts the corresponding audio chunk from the `numpy` array, performs an FFT to calculate equalizer data, and updates the lyrics position.
    4.  **UI Animation Thread**: The `rich` library runs its own thread to render the equalizer and lyric animations smoothly.
-   **Equalizer Logic**: The analysis thread calculates the Fast Fourier Transform (FFT) on the current audio chunk to determine the energy across different frequency ranges. These values are then logarithmically scaled and normalized to create the heights of the equalizer bars.
-   **Temporary Files**: The temporary WAV file created for playback is automatically deleted when the song is stopped or the application exits.

## Project Structure

```
music_player/
├── main.py           # Main application entry point and user interaction logic.
├── player.py         # MusicPlayer class, handles audio loading, playback, and analysis.
├── lyrics_display.py # Manages the console UI, including lyrics and equalizer rendering.
├── requirements.txt  # Project dependencies.
├── README.md         # Project documentation.
├── songs/            # Directory for your music files.
└── lyrics/           # Directory for your LRC lyric files.
```