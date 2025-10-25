# App Launching Configuration

This document explains how apps are launched in the ARC system and how to ensure they work from anywhere.

## How It Works

When you click an app icon in the launcher, the system:

1. **Reads the config** (`config/arc.yaml`) to get the app's `exec` command
2. **Executes the command** which typically calls `run_app.sh`
3. **`run_app.sh` does the following:**
   - Determines the ARC project root (where it's located)
   - Activates the Python virtual environment (`venv`)
   - Sets `PYTHONPATH` to include the project root
   - Changes to the app's directory
   - Runs the app's Python script

## Using Absolute Paths

For apps to work from anywhere (regardless of your current directory), all paths must be absolute.

### Current Configuration

Your config now uses absolute paths like:

```yaml
builtin_apps:
  - name: Music
    icon: /home/admin/Icons/music.png
    exec: "/home/admin/Github/ARC/run_app.sh music_player main.py"
```

This means:
- ✅ Works when launched from any directory
- ✅ Uses the virtual environment automatically
- ✅ Sets the correct working directory for the app

## Updating Paths for Your System

If your ARC project is **not** at `/home/admin/Github/ARC/`, you need to update the paths.

### Automatic Method (Recommended)

Run the path update script:

```bash
cd ~/Github/ARC  # or wherever your ARC is
./generate_config.sh
```

This will:
- Detect your ARC installation path
- Update all `exec` commands in `config/arc.yaml`
- Create a backup of your old config

### Manual Method

1. Find your ARC path:
   ```bash
   cd ~/Github/ARC  # or your ARC location
   pwd
   ```
   
2. Edit `config/arc.yaml` and replace all instances of:
   ```yaml
   exec: "/home/admin/Github/ARC/run_app.sh ...
   ```
   
   With your actual path:
   ```yaml
   exec: "/your/actual/path/to/ARC/run_app.sh ...
   ```

## Icon Paths

Icons also need absolute paths. The current config uses:

```yaml
icon: /home/admin/Icons/wifi_tools.png
```

If your icons are elsewhere:

1. **Option A: Use the standard location**
   ```bash
   sudo mkdir -p /home/admin/Icons
   cp ARC_DE/icons/* /home/admin/Icons/
   ```

2. **Option B: Update the config**
   - Edit `config/arc.yaml`
   - Replace `/home/admin/Icons/` with your icon directory path
   - Use absolute paths!

## Testing

To test if apps launch correctly:

1. **Test from project root:**
   ```bash
   cd ~/Github/ARC
   ./run_app.sh music_player main.py
   ```

2. **Test from different directory:**
   ```bash
   cd /tmp
   /home/admin/Github/ARC/run_app.sh music_player main.py
   ```

Both should work! If not, check:
- Is `run_app.sh` executable? (`chmod +x run_app.sh`)
- Does the virtual environment exist? (`ls -d venv/`)
- Are the paths in your config absolute?

## Adding New Apps

When adding a new app to `config/arc.yaml`:

```yaml
- name: My New App
  icon: /absolute/path/to/icon.png
  exec: "/absolute/path/to/ARC/run_app.sh MyApp main.py"
```

**Important:**
- Use absolute paths for both `icon` and `exec`
- The `exec` path should point to `run_app.sh` in your ARC directory
- The app directory (`MyApp`) should be relative to the ARC root

## Run App Script

The `run_app.sh` script is the key to making apps work from anywhere:

### Usage

```bash
./run_app.sh <app_directory> <script_name>
```

Example:
```bash
./run_app.sh music_player main.py
./run_app.sh Chatbot main.py
```

### What It Does

1. Finds the ARC root directory (where the script is located)
2. Activates `venv/bin/activate` if it exists
3. Adds ARC root to `PYTHONPATH`
4. Changes to `<app_directory>`
5. Runs `python3 <script_name>`

### Debug Output

The script prints helpful debug info:

```
[run_app] ARC root: /home/admin/Github/ARC
[run_app] Looking for: /home/admin/Github/ARC/music_player/main.py
[run_app] Activating virtual environment...
[run_app] Changing to: /home/admin/Github/ARC/music_player
[run_app] Running: python3 main.py
```

If an app doesn't launch, check this output for clues.

## Troubleshooting

### App doesn't start when clicked

1. **Check the config path:**
   ```bash
   grep "exec.*run_app.sh" config/arc.yaml
   ```
   Should show absolute paths.

2. **Test the command manually:**
   ```bash
   /home/admin/Github/ARC/run_app.sh AppName main.py
   ```

3. **Check permissions:**
   ```bash
   ls -l run_app.sh
   ```
   Should show `-rwxr-xr-x` (executable).

### "No such file or directory" error

- The path in your config is wrong
- Run `./generate_config.sh` to fix it

### "No virtual environment found" warning

- Your venv isn't set up
- Run: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

### Icons don't appear

- Icon paths in config are wrong or relative
- Copy icons to `/home/admin/Icons/` or update the config
- See `TROUBLESHOOTING.md` for more icon help

## Summary

✅ **All paths in config should be absolute**
✅ **Use `./generate_config.sh` after moving the project**
✅ **`run_app.sh` handles venv and working directory automatically**
✅ **Test apps from different directories to verify**

For more help, see:
- `TROUBLESHOOTING.md` - Common issues and fixes
- `README.md` - General project information
- `SETUP.md` - Installation and setup

