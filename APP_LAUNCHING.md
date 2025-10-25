# App Launching Configuration

This document explains how apps are launched in the ARC system and how to ensure they work from anywhere.

## How It Works

When you click an app icon in the launcher, the system:

1. **Reads the config** (`config/arc.yaml`) to get the app's `exec` command
2. **Executes the command** which:
   - Changes to the app's directory (`cd /path/to/app/`)
   - Sets `PYTHONPATH` to include the project root
   - Runs the app using the virtual environment's Python interpreter (`venv/bin/python`)

## Using Absolute Paths

For apps to work from anywhere (regardless of your current directory), all paths must be absolute.

### Current Configuration

Your config now uses absolute paths with direct Python execution:

```yaml
builtin_apps:
  - name: Music
    icon: /home/admin/Icons/music.png
    exec: "bash -c 'cd /home/admin/Github/ARC/music_player && PYTHONPATH=/home/admin/Github/ARC /home/admin/Github/ARC/venv/bin/python main.py'"
```

This means:
- ✅ Works when launched from any directory
- ✅ Uses the virtual environment Python directly
- ✅ Sets the correct working directory for the app
- ✅ No wrapper script needed

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
   cd ~/Github/ARC/music_player
   PYTHONPATH=~/Github/ARC ~/Github/ARC/venv/bin/python main.py
   ```

2. **Test from different directory:**
   ```bash
   cd /tmp
   bash -c 'cd /home/admin/Github/ARC/music_player && PYTHONPATH=/home/admin/Github/ARC /home/admin/Github/ARC/venv/bin/python main.py'
   ```

Both should work! If not, check:
- Does the virtual environment exist? (`ls -d ~/Github/ARC/venv/`)
- Are the paths in your config absolute?
- Is the app directory correct?

## Adding New Apps

When adding a new app to `config/arc.yaml`:

```yaml
- name: My New App
  icon: /absolute/path/to/icon.png
  exec: "bash -c 'cd /absolute/path/to/ARC/MyApp && PYTHONPATH=/absolute/path/to/ARC /absolute/path/to/ARC/venv/bin/python main.py'"
```

**Important:**
- Use absolute paths for `icon`, app directory, and Python interpreter
- Set `PYTHONPATH` to the ARC root directory
- Change directory to the app's folder before running
- Replace `/absolute/path/to/ARC` with your actual ARC installation path

## Troubleshooting

### App doesn't start when clicked

1. **Check the config format:**
   ```bash
   grep "exec.*bash -c" config/arc.yaml
   ```
   Should show absolute paths in the bash -c command.

2. **Test the command manually:**
   Copy the exact `exec` line from your config and run it in terminal.

3. **Check Python path:**
   ```bash
   ls -l /home/admin/Github/ARC/venv/bin/python
   ```
   Should exist and be executable.

### "No such file or directory" error

- The path in your config is wrong
- Run `./generate_config.sh` to fix it
- Check that the app directory actually exists

### "No module named..." error

- Your venv isn't set up properly
- Run: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- Or PYTHONPATH isn't set correctly in the exec command

### Icons don't appear

- Icon paths in config are wrong or relative
- Copy icons to `/home/admin/Icons/` or update the config
- See `TROUBLESHOOTING.md` for more icon help

## Summary

✅ **All paths in config should be absolute**
✅ **Use `./generate_config.sh` after moving the project**
✅ **Apps launch directly with venv Python - no wrapper needed**
✅ **Test apps from different directories to verify**

For more help, see:
- `TROUBLESHOOTING.md` - Common issues and fixes
- `README.md` - General project information
- `SETUP.md` - Installation and setup

