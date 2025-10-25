import smbus2
import time

bus = smbus2.SMBus(1)
address = 0x32

while True:
    try:
        data = bus.read_i2c_block_data(address, 0, 8)
        layer = data[0]
        keycodes = data[1:]
        keys = [chr(k) for k in keycodes if k != 0]
        print(f"Layer: {layer}, Keys: {keys}")
    except Exception as e:
        print("Error:", e)
    time.sleep(0.1)