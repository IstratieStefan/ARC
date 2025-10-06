import subprocess

def get_wifi_strength():
    try:
        out = subprocess.check_output([
            'nmcli', '-t', '-f', 'ACTIVE,SIGNAL',
            'device', 'wifi', 'list'
        ], stderr=subprocess.DEVNULL, text=True)
        for line in out.splitlines():
            parts = line.split(':')
            if parts[0] == 'yes' and len(parts) >= 2:
                try:
                    return int(parts[1])
                except ValueError:
                    continue
    except Exception:
        pass
    return 0


def get_bt_status():
    """
    Returns:
      0 - Bluetooth OFF
      1 - Bluetooth ON, not connected
      2 - Bluetooth ON, at least one device connected
    """
    try:
        out = subprocess.check_output(['bluetoothctl', 'show'], stderr=subprocess.DEVNULL, text=True)
        powered = False
        for line in out.splitlines():
            if line.strip().startswith("Powered:"):
                powered = "yes" in line
                break
        if not powered:
            return 0  # OFF

        out = subprocess.check_output(['bluetoothctl', 'devices'], stderr=subprocess.DEVNULL, text=True)
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                addr = parts[1]
                info = subprocess.check_output(['bluetoothctl', 'info', addr], stderr=subprocess.DEVNULL, text=True)
                for il in info.splitlines():
                    if il.strip().startswith("Connected:") and "yes" in il:
                        return 2  # CONNECTED

        return 1  # ON, but not connected
    except Exception:
        return 0  # If any error, treat as OFF