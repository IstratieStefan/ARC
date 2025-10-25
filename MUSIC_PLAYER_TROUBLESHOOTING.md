# Music Player Troubleshooting Guide

## Issues Fixed

### 1. Import Error (ModuleNotFoundError)
**Fixed**: Updated imports in `main.py` to use full package paths:
- Changed: `from music_player.menu import MainMenu`
- To: `from arc.apps.music_player.menu import MainMenu`

### 2. Audio Playback Not Working

#### Install Required System Libraries
On your Raspberry Pi, run:

```bash
cd /home/admin/ARC
chmod +x fix_audio.sh
./fix_audio.sh
```

Or manually install:

```bash
sudo apt-get update
sudo apt-get install -y \
    libsdl2-mixer-2.0-0 \
    libsdl2-mixer-dev \
    alsa-utils \
    pulseaudio \
    libmpg123-0 \
    libmpg123-dev \
    libvorbis0a \
    libvorbisfile3 \
    libflac8
```

#### Configure Audio Output

1. **Select audio device** (if you have HDMI and headphone jack):
   ```bash
   sudo raspi-config
   # Navigate to: System Options -> Audio -> Select your output
   ```

2. **Test audio**:
   ```bash
   speaker-test -t wav -c 2
   # Press Ctrl+C to stop
   ```

3. **Check ALSA devices**:
   ```bash
   aplay -l
   ```

4. **Set environment variable** (if needed):
   ```bash
   export SDL_AUDIODRIVER=alsa
   ```

### 3. Song Length Not Loading

**Fixed**: Added better error handling in `song_selector.py`:
- Now shows debug output when scanning music directory
- Reports errors when reading MP3 tags
- Shows track durations as they're scanned

**Verify your MP3 files**:
```bash
# Check if MP3 files have proper tags
file ~/Music/*.mp3

# View MP3 info
sudo apt-get install id3v2
id3v2 -l ~/Music/yourfile.mp3
```

### 4. Album Art Not Showing

**Fixed**: Improved album art extraction with better error messages.

**Ensure MP3s have embedded album art**:
```bash
# Check for album art
id3v2 -l ~/Music/yourfile.mp3 | grep APIC

# Add album art if missing
pip install eyeD3
eyeD3 --add-image cover.jpg:FRONT_COVER song.mp3
```

## Debug Output

The updated music player now shows detailed debug information:

```bash
/home/admin/ARC/venv/bin/python -m arc.apps.music_player.main
```

You should see:
- Audio driver being used
- Music directory scan results
- Track loading status
- Album art loading status
- Error messages with full details

## Common Issues

### "No sound" but no errors
1. Check volume:
   ```bash
   alsamixer
   # Press F6 to select sound card
   # Use arrow keys to adjust, M to unmute
   ```

2. Verify pygame mixer initialized:
   - Look for: `Pygame mixer initialized: (44100, -16, 2, 2048)`
   - This should appear when you start the player

### "Music directory does not exist"
Edit `config/arc.yaml` and set:
```yaml
music_dir: ~/Music
```

Or create and populate the directory:
```bash
mkdir -p ~/Music
# Copy MP3 files to ~/Music/
```

### MP3s don't play but show no error
Some Raspberry Pi OS versions need additional codecs:
```bash
sudo apt-get install -y ffmpeg
```

### Still having issues?

Run with full debug output:
```bash
export SDL_DEBUG=1
/home/admin/ARC/venv/bin/python -m arc.apps.music_player.main 2>&1 | tee music_debug.log
```

Then check `music_debug.log` for detailed error information.

## Quick Test

1. **Test that audio hardware works**:
   ```bash
   speaker-test -t wav -c 2
   ```

2. **Test pygame audio**:
   ```bash
   cd /home/admin/ARC
   /home/admin/ARC/venv/bin/python -c "import pygame; pygame.mixer.init(); print('Audio OK')"
   ```

3. **Test music player**:
   ```bash
   /home/admin/ARC/venv/bin/python -m arc.apps.music_player.main
   ```

## What Should Work Now

✓ Import errors fixed
✓ Better mixer initialization with Raspberry Pi-compatible settings
✓ Debug output for all operations
✓ Improved error handling
✓ Song length extraction
✓ Album art loading
✓ Proper ALSA audio driver selection on Linux


