#!/usr/bin/env python3
"""
Fix config paths to use absolute paths
This ensures icons load regardless of where launcher is run from
"""

import os
import yaml

# Get ARC root directory (where this script is)
ARC_ROOT = os.path.dirname(os.path.abspath(__file__))
print(f"ARC Root: {ARC_ROOT}")

# Config file location
CONFIG_FILE = os.path.join(ARC_ROOT, "config", "arc.yaml")

if not os.path.exists(CONFIG_FILE):
    print(f"Error: Config file not found at {CONFIG_FILE}")
    exit(1)

print(f"Config file: {CONFIG_FILE}")

# Load config
with open(CONFIG_FILE, 'r') as f:
    config = yaml.safe_load(f)

print("\nFixing paths...")

# Fix icon paths
if 'icons' in config:
    for key, path in config['icons'].items():
        if not os.path.isabs(path):
            abs_path = os.path.join(ARC_ROOT, path)
            config['icons'][key] = abs_path
            print(f"  icons.{key}: {path} -> {abs_path}")

# Fix builtin app paths
if 'builtin_apps' in config:
    for app in config['builtin_apps']:
        if 'icon' in app:
            path = app['icon']
            if not os.path.isabs(path):
                abs_path = os.path.join(ARC_ROOT, path)
                app['icon'] = abs_path
                print(f"  {app['name']}: {path} -> {abs_path}")

# Fix topbar icon paths
if 'topbar' in config:
    topbar = config['topbar']
    
    # Single icons
    for key in ['icon_battery', 'icon_mobile', 'icon_bt_on', 'icon_bt_off', 'icon_bt_connected']:
        if key in topbar:
            path = topbar[key]
            if not os.path.isabs(path):
                abs_path = os.path.join(ARC_ROOT, path)
                topbar[key] = abs_path
                print(f"  topbar.{key}: {path} -> {abs_path}")
    
    # WiFi icons list
    if 'wifi_icons' in topbar:
        new_wifi_icons = []
        for path in topbar['wifi_icons']:
            if not os.path.isabs(path):
                abs_path = os.path.join(ARC_ROOT, path)
                new_wifi_icons.append(abs_path)
                print(f"  topbar.wifi_icon: {path} -> {abs_path}")
            else:
                new_wifi_icons.append(path)
        topbar['wifi_icons'] = new_wifi_icons

# Fix font path
if 'font' in config and 'name' in config['font']:
    path = config['font']['name']
    if not os.path.isabs(path):
        abs_path = os.path.join(ARC_ROOT, path)
        config['font']['name'] = abs_path
        print(f"  font.name: {path} -> {abs_path}")

# Backup original
backup_file = CONFIG_FILE + ".backup"
if not os.path.exists(backup_file):
    with open(backup_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    print(f"\nBackup saved to: {backup_file}")

# Write updated config
with open(CONFIG_FILE, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print(f"\nConfig updated: {CONFIG_FILE}")
print("\nVerifying paths exist:")

# Verify icon files exist
errors = []
for app in config.get('builtin_apps', []):
    icon_path = app.get('icon')
    if icon_path and not os.path.exists(icon_path):
        errors.append(f"  ✗ {app['name']}: {icon_path}")
    elif icon_path:
        print(f"  ✓ {app['name']}: {icon_path}")

if errors:
    print("\nErrors found:")
    for error in errors:
        print(error)
    print("\nRun: bash quick_fix.sh to copy icons to correct location")
else:
    print("\n✓ All icon paths verified!")
    print("\nNow run: python3 launcher.py")

