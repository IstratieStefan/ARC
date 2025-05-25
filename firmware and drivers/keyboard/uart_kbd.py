import serial
import uinput
import time

# rx = pin 36, gpio 16
# tx = pin 33, gpio 13

SERIAL_PORT = '/dev/serial0'
BAUDRATE = 115200

# Define your keymaps
KEYMAPS = [
    [
        [uinput.KEY_ESC, uinput.KEY_MENU, uinput.KEY_HOME, uinput.KEY_LEFT, None, None, None, None, None, None],
        [uinput.KEY_Q, uinput.KEY_W, uinput.KEY_E, uinput.KEY_R, uinput.KEY_T, uinput.KEY_Y, uinput.KEY_U, uinput.KEY_I, uinput.KEY_O, uinput.KEY_P],
        [uinput.KEY_A, uinput.KEY_S, uinput.KEY_D, uinput.KEY_F, uinput.KEY_G, uinput.KEY_H, uinput.KEY_J, uinput.KEY_K, uinput.KEY_L, None],
        [uinput.KEY_LEFTSHIFT, uinput.KEY_Z, uinput.KEY_X, uinput.KEY_C, uinput.KEY_V, uinput.KEY_B, uinput.KEY_N, uinput.KEY_M, None, uinput.KEY_BACKSPACE],
        [uinput.KEY_LEFTCTRL, uinput.KEY_LEFTMETA, None, None, uinput.KEY_SPACE, None, None, None, uinput.KEY_RIGHTALT, uinput.KEY_ENTER],
    ],
    [
        [uinput.KEY_TAB, uinput.KEY_MENU, uinput.KEY_HOME, uinput.KEY_LEFT, None, None, None, None, None, None],
        [uinput.KEY_1, uinput.KEY_2, uinput.KEY_3, uinput.KEY_4, uinput.KEY_5, uinput.KEY_6, uinput.KEY_7, uinput.KEY_8, uinput.KEY_9, uinput.KEY_0],
        [uinput.KEY_A, uinput.KEY_S, uinput.KEY_D, uinput.KEY_F, uinput.KEY_G, uinput.KEY_H, uinput.KEY_J, uinput.KEY_K, uinput.KEY_L, None],
        [uinput.KEY_LEFTSHIFT, uinput.KEY_Z, uinput.KEY_X, uinput.KEY_C, uinput.KEY_V, uinput.KEY_B, uinput.KEY_N, uinput.KEY_M, None, uinput.KEY_BACKSPACE],
        [uinput.KEY_LEFTCTRL, uinput.KEY_LEFTMETA, None, None, uinput.KEY_SPACE, None, None, None, uinput.KEY_RIGHTALT, uinput.KEY_ENTER],
    ],
    [
        [uinput.KEY_F1, uinput.KEY_F2, uinput.KEY_F3, uinput.KEY_F4, None, None, None, None, None, None],
        [None, uinput.KEY_UP, None, None, None, None, None, uinput.KEY_A, uinput.KEY_S, None],
        [uinput.KEY_LEFT, uinput.KEY_DOWN, uinput.KEY_RIGHT, None, None, None, uinput.KEY_X, uinput.KEY_Z, None, None],
        [uinput.KEY_LEFTSHIFT, None, None, None, None, None, None, None, None, uinput.KEY_BACKSPACE],
        [uinput.KEY_LEFTCTRL, uinput.KEY_LEFTMETA, None, None, uinput.KEY_SPACE, None, None, None, uinput.KEY_ENTER, uinput.KEY_ENTER],
    ]
]

# Collect all unique keys used in the keymaps
ALL_KEYS = set()
for layer in KEYMAPS:
    for row in layer:
        for k in row:
            if k:
                ALL_KEYS.add(k)

# Create the virtual keyboard device
device = uinput.Device(list(ALL_KEYS))

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

print("Listening for UART keyboard events...")

while True:
    line = ser.readline().decode('utf-8').strip()
    if not line:
        continue
    try:
        event_type, row, col, layer = map(int, line.split(","))
        keymap = KEYMAPS[layer] if layer < len(KEYMAPS) else KEYMAPS[0]
        key = None
        if 0 <= row < len(keymap) and 0 <= col < len(keymap[row]):
            key = keymap[row][col]
        if not key:
            continue
        if event_type == 1:  # Press
            device.emit(key, 1)
        elif event_type == 0:  # Release
            device.emit(key, 0)
    except Exception as e:
        print(f"Parse error: {line} ({e})")
