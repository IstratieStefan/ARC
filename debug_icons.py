#!/usr/bin/env python3
"""
Debug script to check icon paths on Raspberry Pi
Run this on your Pi to diagnose icon loading issues
"""

import os
import sys

print("=" * 60)
print("ARC Icon Path Debugger")
print("=" * 60)

# Get project root
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"\n1. Project Root: {project_root}")

# Check if arc/assets/icons exists
icons_dir = os.path.join(project_root, "arc", "assets", "icons")
print(f"\n2. Icons Directory: {icons_dir}")
print(f"   Exists: {os.path.exists(icons_dir)}")
print(f"   Is Directory: {os.path.isdir(icons_dir)}")

if os.path.exists(icons_dir):
    icons = [f for f in os.listdir(icons_dir) if f.endswith('.png')]
    print(f"   Icon count: {len(icons)}")
    print(f"   First 10 icons: {icons[:10]}")

# Test config loading
print("\n3. Testing Config Loading:")
try:
    from arc.core import config
    print(f"   ✓ Config loaded successfully")
    print(f"   Config file: {config.get('_config_path', 'unknown')}")
    
    # Test some icon paths
    print("\n4. Testing Icon Paths in Config:")
    test_icons = [
        ('wifi_locked', config.icons.wifi_locked),
        ('wifi_unlocked', config.icons.wifi_unlocked),
    ]
    
    for name, path in test_icons:
        exists = os.path.exists(path) if path else False
        print(f"   {name}: {path}")
        print(f"      Exists: {exists}")
        print(f"      Absolute: {os.path.abspath(path) if path else 'N/A'}")
    
    # Test builtin app icons
    print("\n5. Testing Builtin App Icons:")
    for app in config.builtin_apps[:5]:  # First 5 apps
        icon_path = app.get('icon', '')
        exists = os.path.exists(icon_path) if icon_path else False
        print(f"   {app.get('name')}: {icon_path}")
        print(f"      Exists: {exists}")
        
except Exception as e:
    print(f"   ✗ Error loading config: {e}")
    import traceback
    traceback.print_exc()

# Check working directory
print(f"\n6. Current Working Directory: {os.getcwd()}")

# Test pygame icon loading
print("\n7. Testing Pygame Icon Loading:")
try:
    import pygame
    pygame.init()
    test_icon = os.path.join(icons_dir, "terminal.png")
    if os.path.exists(test_icon):
        try:
            img = pygame.image.load(test_icon)
            print(f"   ✓ Successfully loaded test icon: {test_icon}")
            print(f"   Image size: {img.get_size()}")
        except Exception as e:
            print(f"   ✗ Failed to load icon: {e}")
    else:
        print(f"   ✗ Test icon not found: {test_icon}")
except ImportError:
    print("   ✗ Pygame not available")

print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)

