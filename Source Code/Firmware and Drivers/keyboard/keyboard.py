### cirucit python uart/usb keyboard firmware

import time
import board
import digitalio
import usb_hid
import busio
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# ---- UART SETUP (GP0=TX, GP1=RX) ----
uart = busio.UART(board.GP0, board.GP1, baudrate=115200)

ROW_PINS = [board.GP28, board.GP27, board.GP26, board.GP15, board.GP14]
COL_PINS = [board.GP13, board.GP12, board.GP11, board.GP10, board.GP9,
            board.GP4, board.GP5, board.GP6, board.GP3, board.GP8]

# --------- LAYER KEY CLASS -----------
class LayerKey:
    def __init__(self, layer_num, mode='momentary'):
        self.layer = layer_num
        self.mode = mode  # 'momentary' or 'toggle'
    def __eq__(self, other):
        return isinstance(other, LayerKey) and self.layer == other.layer and self.mode == other.mode
    def __hash__(self):
        return hash((self.layer, self.mode))
    def __repr__(self):
        return f"<LayerKey layer={self.layer} mode={self.mode}>"

# --- Example special keys
LAYER1_MO = LayerKey(1, 'momentary')  # momentary Layer 1
LAYER2_TG = LayerKey(2, 'toggle')     # toggle Layer 2

# ----------- KEYMAPS (customize as needed) ------------
LAYER_0 = [
    [Keycode.ESCAPE, Keycode.APPLICATION, Keycode.HOME, Keycode.LEFT_ARROW, None, None, None, None, None, None],
    [Keycode.Q, Keycode.W, Keycode.E, Keycode.R, Keycode.T, Keycode.Y, Keycode.U, Keycode.I, Keycode.O, Keycode.P],
    [Keycode.A, Keycode.S, Keycode.D, Keycode.F, Keycode.G, Keycode.H, Keycode.J, Keycode.K, Keycode.L, None],
    [Keycode.LEFT_SHIFT, Keycode.Z, Keycode.X, Keycode.C, Keycode.V, Keycode.B, Keycode.N, Keycode.M, None, Keycode.BACKSPACE],
    [Keycode.LEFT_CONTROL, Keycode.LEFT_GUI, LAYER1_MO, None, Keycode.SPACE, None, None, LAYER2_TG, Keycode.RIGHT_ALT, Keycode.ENTER],
]

LAYER_1 = [
    [Keycode.TAB, Keycode.APPLICATION, Keycode.HOME, Keycode.LEFT_ARROW, None, None, None, None, None, None],
    [Keycode.ONE, Keycode.TWO, Keycode.THREE, Keycode.FOUR, Keycode.FIVE, Keycode.SIX, Keycode.SEVEN, Keycode.EIGHT, Keycode.NINE, Keycode.ZERO],
    [Keycode.A, Keycode.S, Keycode.D, Keycode.F, Keycode.G, Keycode.H, Keycode.J, Keycode.K, Keycode.L, None],
    [Keycode.LEFT_SHIFT, Keycode.Z, Keycode.X, Keycode.C, Keycode.V, Keycode.B, Keycode.N, Keycode.M, None, Keycode.BACKSPACE],
    [Keycode.LEFT_CONTROL, Keycode.LEFT_GUI, LAYER1_MO, None, Keycode.SPACE, None, None, LAYER2_TG, Keycode.RIGHT_ALT, Keycode.ENTER],
]

LAYER_2 = [
    [Keycode.F1, Keycode.F2, Keycode.F3, Keycode.F4, None, None, None, None, None, None],
    [None, Keycode.UP_ARROW, None, None, None, None, None, Keycode.A, Keycode.S, None],
    [Keycode.LEFT_ARROW, Keycode.DOWN_ARROW, Keycode.RIGHT_ARROW, None, None, None, Keycode.X, Keycode.Z, None, None],
    [Keycode.LEFT_SHIFT, None, None, None, None, None, None, None, None, Keycode.BACKSPACE],
    [Keycode.LEFT_CONTROL, Keycode.LEFT_GUI, LAYER1_MO, None, Keycode.SPACE, None, None, LAYER2_TG, Keycode.ENTER, Keycode.ENTER],
]

KEYMAPS = [LAYER_0, LAYER_1, LAYER_2]

# ----------- SETUP -------------
rows = []
for pin in ROW_PINS:
    r = digitalio.DigitalInOut(pin)
    r.direction = digitalio.Direction.OUTPUT
    r.value = False
    rows.append(r)

cols = []
for pin in COL_PINS:
    c = digitalio.DigitalInOut(pin)
    c.direction = digitalio.Direction.INPUT
    c.pull = digitalio.Pull.DOWN
    cols.append(c)

kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
pressed_last = set()

# --- State for layer keys ---
active_layers = set()   # Set of currently pressed momentary layers
toggle_layers = set()   # Set of toggled layers

def scan_keys():
    pressed_now = set()
    for row_idx, row in enumerate(rows):
        for r in rows:
            r.value = False
        row.value = True
        for col_idx, col in enumerate(cols):
            if col.value:
                pressed_now.add((row_idx, col_idx))
    return pressed_now

def get_active_layer():
    # If any momentary layers are held, use the highest number (highest-priority layer)
    if active_layers:
        return max(active_layers)
    elif toggle_layers:
        return max(toggle_layers)
    return 0

def send_uart(event_type, row, col, layer):
    # event_type: 1=press, 0=release
    # You can send as simple bytes or format as a string
    msg = f"{event_type},{row},{col},{layer}\n"
    uart.write(msg.encode("utf-8"))

while True:
    pressed_now = scan_keys()
    new_keys = pressed_now - pressed_last
    released_keys = pressed_last - pressed_now

    # --- 1. Handle LayerKey presses from ALL LAYERS (for momentary and toggle) ---
    for row, col in new_keys:
        for l in range(len(KEYMAPS)):
            kc = KEYMAPS[l][row][col]
            if isinstance(kc, LayerKey):
                if kc.mode == 'momentary':
                    active_layers.add(kc.layer)
                elif kc.mode == 'toggle':
                    if kc.layer in toggle_layers:
                        toggle_layers.remove(kc.layer)
                    else:
                        toggle_layers.add(kc.layer)

    for row, col in released_keys:
        for l in range(len(KEYMAPS)):
            kc = KEYMAPS[l][row][col]
            if isinstance(kc, LayerKey) and kc.mode == 'momentary':
                if kc.layer in active_layers:
                    active_layers.remove(kc.layer)

    # --- 2. Decide active layer ---
    layer = get_active_layer()
    keymap = KEYMAPS[layer]

    # --- 3. Handle regular keys ---
    for row, col in new_keys:
        kc = keymap[row][col]
        if kc is not None and not isinstance(kc, LayerKey):
            try:
                if isinstance(kc, tuple):
                    kbd.press(*kc)
                elif isinstance(kc, ConsumerControlCode):
                    cc.send(kc)
                else:
                    kbd.press(kc)
                send_uart(1, row, col, layer)  # 1 = pressed
            except ValueError:
                pass

    for row, col in released_keys:
        kc = keymap[row][col]
        if kc is not None and not isinstance(kc, LayerKey):
            try:
                if isinstance(kc, tuple):
                    kbd.release(*kc)
                else:
                    kbd.release(kc)
                send_uart(0, row, col, layer)  # 0 = released
            except ValueError:
                pass

    pressed_last = pressed_now
    time.sleep(0.01)
