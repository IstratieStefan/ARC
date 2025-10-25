#!/usr/bin/env python3
"""
Comprehensive icon loading test
Run this to diagnose icon loading issues
"""

import os
import sys

print("=" * 70)
print("ICON LOADING DIAGNOSTIC TEST")
print("=" * 70)
print()

# Test 1: Check if pygame can be imported
print("1. Testing pygame import...")
try:
    import pygame
    pygame.init()
    print("   ✓ pygame imported successfully")
    print(f"   Version: {pygame.version.ver}")
except Exception as e:
    print(f"   ✗ pygame import failed: {e}")
    sys.exit(1)

print()

# Test 2: Check config loading
print("2. Testing config loading...")
try:
    from arc.core import config
    print("   ✓ Config loaded successfully")
    print(f"   Config file: {config._config_path}")
    print(f"   Base dir: {config._base_dir}")
except Exception as e:
    print(f"   ✗ Config loading failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Check icon paths in config
print("3. Checking icon paths in config...")
print()
if hasattr(config, 'builtin_apps'):
    for i, app in enumerate(config.builtin_apps):
        if i >= 5:  # Only show first 5
            print(f"   ... and {len(config.builtin_apps) - 5} more apps")
            break
        
        icon_path = app.get('icon', 'NO ICON')
        print(f"   App: {app.get('name', 'UNKNOWN')}")
        print(f"     Icon path from config: {icon_path}")
        print(f"     Is absolute: {os.path.isabs(icon_path)}")
        print(f"     File exists: {os.path.exists(icon_path) if icon_path != 'NO ICON' else False}")
        
        if icon_path != 'NO ICON' and os.path.exists(icon_path):
            # Check if file is readable
            try:
                with open(icon_path, 'rb') as f:
                    header = f.read(8)
                    # PNG files start with: 89 50 4E 47 0D 0A 1A 0A
                    is_png = header.startswith(b'\x89PNG\r\n\x1a\n')
                    print(f"     Is PNG file: {is_png}")
                    if not is_png:
                        print(f"     ⚠ File exists but is not a PNG! First bytes: {header.hex()}")
            except Exception as e:
                print(f"     ✗ Error reading file: {e}")
        print()
else:
    print("   ✗ No builtin_apps in config!")

print()

# Test 4: Try loading an icon with pygame
print("4. Testing icon loading with pygame...")
if hasattr(config, 'builtin_apps') and len(config.builtin_apps) > 0:
    test_app = config.builtin_apps[0]
    test_icon = test_app.get('icon')
    
    print(f"   Testing: {test_app.get('name')}")
    print(f"   Icon path: {test_icon}")
    
    if test_icon and os.path.exists(test_icon):
        try:
            # Try to load the icon
            img = pygame.image.load(test_icon)
            print(f"   ✓ Successfully loaded icon!")
            print(f"   Image size: {img.get_size()}")
            print(f"   Image format: {img.get_bitsize()} bit")
        except Exception as e:
            print(f"   ✗ Failed to load icon: {e}")
            print(f"   Error type: {type(e).__name__}")
            
            # Try to get more info about the file
            import subprocess
            try:
                result = subprocess.run(['file', test_icon], capture_output=True, text=True)
                print(f"   File type: {result.stdout.strip()}")
            except:
                pass
    else:
        print(f"   ✗ Icon file doesn't exist at: {test_icon}")
else:
    print("   ✗ No apps to test!")

print()

# Test 5: Check all icon files exist
print("5. Checking all icon file locations...")
icon_dir = "/home/admin/Icons"
print(f"   Checking directory: {icon_dir}")

if os.path.exists(icon_dir):
    print(f"   ✓ Directory exists")
    
    # List files
    try:
        files = [f for f in os.listdir(icon_dir) if f.endswith('.png')]
        print(f"   Found {len(files)} PNG files:")
        for f in sorted(files)[:10]:
            full_path = os.path.join(icon_dir, f)
            size = os.path.getsize(full_path)
            print(f"     - {f} ({size} bytes)")
        if len(files) > 10:
            print(f"     ... and {len(files) - 10} more")
    except Exception as e:
        print(f"   ✗ Error listing files: {e}")
    
    # Check topbar
    topbar_dir = os.path.join(icon_dir, "topbar")
    if os.path.exists(topbar_dir):
        topbar_files = [f for f in os.listdir(topbar_dir) if f.endswith('.png')]
        print(f"   Found {len(topbar_files)} topbar PNG files")
    else:
        print(f"   ⚠ Topbar directory not found: {topbar_dir}")
else:
    print(f"   ✗ Directory does NOT exist!")
    print(f"   ")
    print(f"   Possible locations to check:")
    for possible in ["/home/admin/Icons", "~/ARC/Icons", "/home/admin/ARC/Icons"]:
        expanded = os.path.expanduser(possible)
        exists = os.path.exists(expanded)
        status = "✓ EXISTS" if exists else "✗ not found"
        print(f"     {status}: {expanded}")

print()

# Test 6: Permissions check
print("6. Checking file permissions...")
if hasattr(config, 'builtin_apps') and len(config.builtin_apps) > 0:
    test_icon = config.builtin_apps[0].get('icon')
    if test_icon and os.path.exists(test_icon):
        import stat
        st = os.stat(test_icon)
        mode = stat.filemode(st.st_mode)
        print(f"   File: {test_icon}")
        print(f"   Permissions: {mode}")
        print(f"   Readable: {os.access(test_icon, os.R_OK)}")
        print(f"   Size: {st.st_size} bytes")
    else:
        print(f"   ✗ Cannot check - file doesn't exist")

print()
print("=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print()
print("If icons still don't load, share this output!")

