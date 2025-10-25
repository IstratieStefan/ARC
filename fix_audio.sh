#!/bin/bash
# Audio Fix Script for Raspberry Pi
# Run this to install required audio libraries for the music player

echo "=== ARC Music Player - Audio Dependencies Installer ==="
echo ""

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install SDL2 mixer library (required for pygame audio)
echo ""
echo "Installing SDL2 audio libraries..."
sudo apt-get install -y libsdl2-mixer-2.0-0 libsdl2-mixer-dev

# Install ALSA and PulseAudio
echo ""
echo "Installing ALSA and audio backends..."
sudo apt-get install -y alsa-utils pulseaudio

# Install MP3 codec support
echo ""
echo "Installing MP3 codec support..."
sudo apt-get install -y libmpg123-0 libmpg123-dev

# Install additional audio codecs
sudo apt-get install -y libvorbis0a libvorbisfile3 libflac8

echo ""
echo "=== Testing audio setup ==="
echo "Checking ALSA devices..."
aplay -l

echo ""
echo "Checking default audio device..."
amixer

echo ""
echo "=== Audio setup complete! ==="
echo ""
echo "If you see audio device errors above, you may need to:"
echo "1. Configure default audio device: sudo raspi-config"
echo "   -> System Options -> Audio -> Select your audio output"
echo ""
echo "2. Set the default audio device with:"
echo "   export SDL_AUDIODRIVER=alsa"
echo "   export AUDIODEV=hw:0,0"
echo ""
echo "3. Test audio with:"
echo "   speaker-test -t wav -c 2"
echo ""
echo "Now try running the music player again!"

