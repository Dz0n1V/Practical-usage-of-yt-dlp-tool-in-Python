# yt-dlp-playlist-downloader

A Python CLI tool that downloads YouTube playlists as MP3 files and automatically generates an `.m3u` playlist file — ready to use in local music players like Musicolet.

## Features

- Downloads an entire YouTube playlist as MP3 audio files
- Embeds thumbnails and metadata into each MP3
- Generates an `.m3u` playlist file pointing to the downloaded tracks
- Interactive menu with instant keypress support (Windows)
- Automatically locates `yt-dlp` across common install paths
- Optional `cookies.txt` support for age-restricted content

## Requirements

- [Python 3.10+](https://www.python.org/downloads/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — `pip install yt-dlp`
- [ffmpeg](https://ffmpeg.org/download.html) — must be added to system PATH
- [Node.js](https://nodejs.org) — for YouTube JS challenge solving

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Dz0n1V/Practical-usage-of-yt-dlp-tool-in-Python.git
   cd Practical-usage-of-yt-dlp-tool-in-Python
   ```

2. Install yt-dlp:
   ```bash
   pip install yt-dlp
   ```

3. Install ffmpeg and add it to PATH:
   - Download from https://ffmpeg.org/download.html
   - Extract and add the `bin/` folder to your system PATH

4. Install Node.js from https://nodejs.org (LTS version)

## Usage

```bash
python yt_playlist_to_mp3.py
```

On launch, a menu appears:

```
========================================
   YouTube Playlist Downloader
========================================
  [1]  Download a playlist
  [0]  Exit
========================================
```

Press `1`, paste a YouTube playlist URL, and choose an output folder. The script will download all tracks as MP3s and generate a `PlaylistName.m3u` file in the same folder.

## Age-restricted content

For playlists containing age-restricted videos, place a `cookies.txt` file in the same folder as the script or `.exe`. The program will detect it automatically.

To export cookies from your browser, use the [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) extension.

> ⚠️ Never commit `cookies.txt` to version control.

## Output structure

```
📁 output_folder/
   01 - Song Title.mp3
   02 - Song Title.mp3
   ...
   PlaylistName.m3u
```

Transfer the entire folder to your device and open the `.m3u` in Musicolet or any local music player that supports playlists.

## Building a standalone .exe (Windows)

```bash
pip install auto-py-to-exe
auto-py-to-exe
```

Select `yt_playlist_to_mp3.py`, choose **One File** and **Console Based**, then click Convert. Place `yt-dlp.exe` and `cookies.txt` (optional) in the same folder as the generated `.exe`.

## License

MIT
