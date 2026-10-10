#!/usr/bin/env python3
"""
YouTube Playlist -> MP3 + .m3u
Requires: yt-dlp  (pip install yt-dlp)
          ffmpeg  (https://ffmpeg.org/download.html)
          Node.js (https://nodejs.org)
"""

import subprocess
import sys
import json
import os
import re
import shutil

# Try to import msvcrt for instant keypress detection (Windows only)
try:
    import msvcrt
    INSTANT_KEY = True
except ImportError:
    INSTANT_KEY = False


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def read_choice(prompt):
    """Read a single character instantly (Windows) or wait for Enter (other)."""
    print(prompt, end="", flush=True)
    if INSTANT_KEY:
        ch = msvcrt.getwch()
        print(ch)
        return ch.strip()
    else:
        return input().strip()


def sanitize_filename(name):
    """Remove characters that are unsafe in filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()


def find_yt_dlp():
    """Locate the yt-dlp executable, checking common install locations."""
    exe_dir = os.path.dirname(sys.executable)
    local = os.path.join(exe_dir, "yt-dlp.exe")
    if os.path.isfile(local):
        return local

    path = shutil.which("yt-dlp") or shutil.which("yt-dlp.exe")
    if path:
        return path

    candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Scripts", "yt-dlp.exe"),
        os.path.join(os.environ.get("APPDATA", ""), "Python", "Scripts", "yt-dlp.exe"),
        r"C:\Python312\Scripts\yt-dlp.exe",
        r"C:\Python311\Scripts\yt-dlp.exe",
        r"C:\Python310\Scripts\yt-dlp.exe",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


# ─────────────────────────────────────────────
#  Menu
# ─────────────────────────────────────────────

def show_menu():
    """Display the main menu and return the user's choice."""
    print("\n" + "=" * 40)
    print("   YouTube Playlist Downloader")
    print("=" * 40)
    print("  [1]  Download a playlist")
    print("  [0]  Exit")
    print("=" * 40)
    hint = " (press 1 or 0): " if INSTANT_KEY else " (enter 1 or 0, then Enter): "
    return read_choice(hint)


# ─────────────────────────────────────────────
#  Core download logic
# ─────────────────────────────────────────────

def find_cookies(ytdlp):
    """Look for cookies.txt in the same folder as the exe/script."""
    exe_dir = os.path.dirname(sys.executable)
    cookies_path = os.path.join(exe_dir, "cookies.txt")
    if os.path.isfile(cookies_path):
        return cookies_path
    return None


def download_playlist(ytdlp):
    """Ask for URL + output folder, download playlist as MP3s, write .m3u."""

    playlist_url = input("\nPaste YouTube playlist URL: ").strip()
    if not playlist_url:
        print("❌ No URL entered.")
        return

    output_dir = input("Output folder (press Enter for current directory): ").strip()
    if not output_dir:
        output_dir = "."
    os.makedirs(output_dir, exist_ok=True)

    # ── Check for cookies.txt ────────────────────
    cookies = find_cookies(ytdlp)
    cookie_args = ["--cookies", cookies] if cookies else []
    if cookies:
        print(f"🍪 Found cookies.txt — using it for authentication")
    else:
        print("⚠️  No cookies.txt found — age-restricted videos may fail")
        print(f"   Place cookies.txt next to the .exe to enable authentication")

    # ── Fetch playlist metadata ──────────────────
    print("\n📋 Fetching playlist info...")
    result = subprocess.run(
        [
            ytdlp,
            "--flat-playlist",
            *cookie_args,
            "--extractor-args", "youtube:player_client=android,web",
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            "-J",
            playlist_url,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("❌ Error fetching playlist:")
        print(result.stderr)
        return

    data = json.loads(result.stdout)
    entries = data.get("entries", [])
    playlist_title = sanitize_filename(data.get("title", "playlist"))

    if not entries:
        print("❌ No tracks found. Make sure the playlist is public.")
        return

    print(f"✅ Found {len(entries)} tracks in \"{playlist_title}\"\n")

    # ── Download audio ───────────────────────────
    print("⬇️  Downloading audio...\n")
    output_template = os.path.join(
        output_dir, "%(playlist_index)s - %(title)s.%(ext)s"
    )

    subprocess.run([
        ytdlp,
        "-x",
        "--audio-format",       "mp3",
        "--audio-quality",      "0",
        "--embed-thumbnail",
        "--add-metadata",
        "--convert-thumbnails", "jpg",
        *cookie_args,
        "--extractor-args",     "youtube:player_client=android,web",
        "--js-runtimes",        "node",
        "--remote-components",  "ejs:github",
        "--output",             output_template,
        "--no-playlist-reverse",
        playlist_url,
    ])

    # ── Collect MP3s & write .m3u ────────────────
    mp3_files = sorted(
        f for f in os.listdir(output_dir) if f.lower().endswith(".mp3")
    )

    if not mp3_files:
        print("\n❌ No MP3 files found in the output folder.")
        print("   Make sure ffmpeg is installed and added to PATH.")
        return

    m3u_path = os.path.join(output_dir, f"{playlist_title}.m3u")
    with open(m3u_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for filename in mp3_files:
            title = os.path.splitext(filename)[0]
            f.write(f"#EXTINF:-1,{title}\n")
            f.write(f"{filename}\n")

    print(f"\n✅ Done!")
    print(f"   📁 MP3s saved to : {os.path.abspath(output_dir)}")
    print(f"   🎵 Playlist file  : {os.path.abspath(m3u_path)}")
    print(f"   🎶 Tracks         : {len(mp3_files)}")
    print("\nTransfer the entire folder (MP3s + .m3u) to your device and open the .m3u in Musicolet.")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

def main():
    ytdlp = find_yt_dlp()
    if not ytdlp:
        print("❌ yt-dlp not found.")
        print("   Install it with:  pip install yt-dlp")
        print("   Or place yt-dlp.exe in the same folder as this program.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    while True:
        choice = show_menu()

        if choice == "1":
            try:
                download_playlist(ytdlp)
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")

        elif choice == "0":
            print("\nGoodbye! 👋")
            sys.exit(0)

        else:
            print("❌ Invalid input. Press 1 or 0.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted.")
        sys.exit(0)