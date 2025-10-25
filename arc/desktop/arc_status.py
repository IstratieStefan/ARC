import subprocess
import platform

IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'

def get_wifi_strength():
    if IS_MACOS:
        # macOS airport utility for WiFi signal strength
        try:
            out = subprocess.check_output([
                '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport',
                '-I'
            ], stderr=subprocess.DEVNULL, text=True)
            for line in out.splitlines():
                if 'agrCtlRSSI' in line:
                    rssi = int(line.split(':')[1].strip())
                    # Convert RSSI to percentage (approximate)
                    # RSSI typically ranges from -90 (weak) to -30 (strong)
                    strength = min(100, max(0, (rssi + 90) * 100 // 60))
                    return strength
        except Exception:
            pass
        return 0
    elif IS_LINUX:
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
    return 0


def get_bt_status():
    """
    Returns:
      0 - Bluetooth OFF
      1 - Bluetooth ON, not connected
      2 - Bluetooth ON, at least one device connected
    """
    if IS_MACOS:
        # macOS Bluetooth status
        try:
            # Check if Bluetooth is powered on
            out = subprocess.check_output([
                'system_profiler', 'SPBluetoothDataType'
            ], stderr=subprocess.DEVNULL, text=True, timeout=5)
            # Simple heuristic: if we can run the command, BT is available
            # For development, just return 1 (ON but not connected)
            return 1
        except Exception:
            return 0
    elif IS_LINUX:
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
    return 0