import serial
import uinput
import time

# Define the same keymaps as the Pico (simplified for demo)
KEYMAPS = [
    [
        [uinput.KEY_ESC, uinput.KEY_MENU, uinput.KEY_HOME, uinput.KEY_LEFT, None, None, None, None, None, None],
        [uinput.KEY_Q, uinput.KEY_W, uinput.KEY_E, uinput.KEY_R, uinput.KEY_T, uinput.KEY_Y, uinput.KEY_U, uinput.KEY_I,
         uinput.KEY_O, uinput.KEY_P],
        [uinput.KEY_A, uinput.KEY_S, uinput.KEY_D, uinput.KEY_F, uinput.KEY_G, uinput.KEY_H, uinput.KEY_J, uinput.KEY_K,
         uinput.KEY_L, None],
        [uinput.KEY_LEFTSHIFT, uinput.KEY_Z, uinput.KEY_X, uinput.KEY_C, uinput.KEY_V, uinput.KEY_B, uinput.KEY_N,
         uinput.KEY_M, None, uinput.KEY_BACKSPACE],
        [uinput.KEY_LEFTCTRL, uinput.KEY_LEFTMETA, None, None, uinput.KEY_SPACE, None, None, None, uinput.KEY_RIGHTALT,
         uinput.KEY_ENTER],
    ],
    [
        [uinput.KEY_TAB, uinput.KEY_MENU, uinput.KEY_HOME, uinput.KEY_LEFT, None, None, None, None, None, None],
        [uinput.KEY_1, uinput.KEY_2, uinput.KEY_3, uinput.KEY_4, uinput.KEY_5, uinput.KEY_6, uinput.KEY_7, uinput.KEY_8,
         uinput.KEY_9, uinput.KEY_0],
        [uinput.KEY_A, uinput.KEY_S, uinput.KEY_D, uinput.KEY_F, uinput.KEY_G, uinput.KEY_H, uinput.KEY_J, uinput.KEY_K,
         uinput.KEY_L, None],
        [uinput.KEY_LEFTSHIFT, uinput.KEY_Z, uinput.KEY_X, uinput.KEY_C, uinput.KEY_V, uinput.KEY_B, uinput.KEY_N,
         uinput.KEY_M, None, uinput.KEY_BACKSPACE],
        [uinput.KEY_LEFTCTRL, uinput.KEY_LEFTMETA, None, None, uinput.KEY_SPACE, None, None, None, uinput.KEY_RIGHTALT,
         uinput.KEY_ENTER],
    ],
    [
        [uinput.KEY_F1, uinput.KEY_F2, uinput.KEY_F3, uinput.KEY_F4, None, None, None, None, None, None],
        [None, uinput.KEY_UP, None, None, None, None, None, uinput.KEY_A, uinput.KEY_S, None],
        [uinput.KEY_LEFT, uinput.KEY_DOWN, uinput.KEY_RIGHT, None, None, None, uinput.KEY_X, uinput.KEY_Z, None, None],
        [uinput.KEY_LEFTSHIFT, None, None, None, None, None, None, None, None, uinput.KEY_BACKSPACE],
        [uinput.KEY_LEFTCTRL, uinput.KEY_LEFTMETA, None, None, uinput.KEY_SPACE, None, None, None, uinput.KEY_ENTER,
         uinput.KEY_ENTER],
    ]
]

# Serial UART setup (mini UART on GPIO 36=TX, 33=RX = GPIO16, GPIO13)
SERIAL_PORT = "/dev/ttyS0"
BAUDRATE = 115200

# Flatten key events to include all from all layers
device = uinput.Device([
    key for layer in KEYMAPS for row in layer for key in row if key
])

# Open serial port
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

print("Listening on UART for key events...")

while True:
    try:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) != 4:
            continue

        event_type, row, col, layer = map(int, parts)
        try:
            key = KEYMAPS[layer][row][col]
        except IndexError:
            continue
        if key is None:
            continue

        if event_type == 1:
            device.emit(key, 1)  # Press
        else:
            device.emit(key, 0)  # Release

    except Exception as e:
        print("Error:", e)
        time.sleep(0.5)
