# ARC Connect - Version 2.0 (ARC-Themed with Enhanced Metrics)

## 🎨 What's New

### **ARC Color Scheme**
- **Primary Accent**: Orange (#CC6324) - matches `accent_color` from `arc.yaml`
- **Background**: Dark (#141414) - matches `colors.background`
- **Text**: Light gray (#DCDCDC) - matches `colors.text`
- **Secondary**: Dark gray (#323232) - matches `colors.tab_bg`
- **Hover**: Darker orange (#B35620)

### **Enhanced Performance Metrics** (New!)

#### Dashboard now shows:

**1. CPU Usage**
   - Overall percentage
   - **CPU Frequency** (Current GHz)
   - **CPU Temperature** (Raspberry Pi thermal sensor)
   - Progress bar visualization

**2. Memory Usage**
   - RAM percentage
   - Used / Total breakdown
   - Cached and buffer memory
   - Progress bar

**3. Disk Usage**
   - Storage percentage
   - Used / Total space
   - Progress bar

**4. Network (NEW!)**
   - **Total data sent**
   - **Total data received**
   - **Packet counts** (sent/received)
   - **Network errors** (if any)

**5. Swap Memory (NEW!)**
   - Swap usage percentage
   - Used / Total swap
   - Progress bar

**6. System Uptime (NEW!)**
   - **Formatted uptime** (days, hours, minutes)
   - **Boot time** (date and time)
   - Real-time counter

**7. System Information**
   - Hostname
   - Platform (Linux)
   - Architecture (armv7l, aarch64, etc.)
   - **CPU Cores** (logical + physical count)
   - Total Memory
   - Total Disk

**8. CPU Per-Core Stats (Backend)**
   - Individual core usage (available via API)
   - Context switches
   - Interrupts

**9. Disk I/O (Backend)**
   - Read/Write bytes
   - Read/Write operation counts

## 📊 Metrics Comparison

| Metric | Old | New |
|--------|-----|-----|
| CPU % | ✅ | ✅ Enhanced |
| CPU Freq | ❌ | ✅ NEW |
| CPU Temp | ❌ | ✅ NEW |
| Memory % | ✅ | ✅ Enhanced |
| Mem Detail | Basic | ✅ Enhanced |
| Disk % | ✅ | ✅ |
| Network | ❌ | ✅ NEW |
| Swap | ❌ | ✅ NEW |
| Uptime | ❌ | ✅ NEW |
| Boot Time | ❌ | ✅ NEW |
| Per-Core CPU | ❌ | ✅ NEW |
| Disk I/O | ❌ | ✅ NEW |

## 🎨 Color Scheme

```yaml
# From arc.yaml config
accent_color: [204, 99, 36]  # #CC6324 (ARC Orange)

colors:
  background: [20, 20, 20]        # #141414
  tab_bg: [50, 50, 50]            # #323232
  tab_active: [100, 100, 100]     # #646464
  text: [220, 220, 220]           # #DCDCDC
  indicator: [180, 180, 180]      # #B4B4B4
```

## 🚀 Installation

### On Raspberry Pi:

```bash
cd /home/admin/ARC

# Copy updated files from your dev machine:
# - arc/apps/connect/server.py (enhanced /system/info endpoint)
# - arc/apps/connect/dashboard.html (new ARC-themed design)

# Restart server
./start_arc_connect.sh
```

## 🖥️ Screenshots Features

### Dashboard Tab
- **6 metric cards** with live data
- **Orange accent colors** matching ARC theme
- **Smooth progress bars** for percentages
- **System info table** at bottom
- **Auto-refresh** every 3 seconds

### Terminal Tab
- Real SSH connection
- Black terminal background with green text
- Command history (↑/↓ arrows)
- Tab completion
- Ctrl+C support

### Files Tab
- Orange-themed upload area
- File list with sizes
- Download/Delete buttons
- Drag & drop support

## 📡 Enhanced API Endpoints

### `/system/info` (Enhanced)

Now returns comprehensive system data:

```json
{
  // CPU
  "cpu_percent": 15.2,
  "cpu_percent_per_core": [12.5, 17.8, 14.3, 16.2],
  "cpu_freq_current": 1500.0,
  "cpu_temp": 48.5,
  "cpu_stats": {
    "ctx_switches": 1234567,
    "interrupts": 987654
  },
  
  // Memory
  "memory": {
    "percent": 65.4,
    "used": 542912512,
    "total": 830472192,
    "free": 198172672,
    "cached": 89387008,
    "buffers": 0
  },
  
  // Swap
  "swap": {
    "percent": 12.3,
    "used": 12582912,
    "total": 104857600,
    "free": 92274688
  },
  
  // Network
  "network": {
    "bytes_sent": 12345678,
    "bytes_recv": 98765432,
    "packets_sent": 45678,
    "packets_recv": 123456,
    "errin": 0,
    "errout": 0
  },
  
  // Disk I/O
  "disk_io": {
    "read_bytes": 1234567890,
    "write_bytes": 987654321,
    "read_count": 12345,
    "write_count": 6789
  },
  
  // System
  "uptime_seconds": 86400,
  "boot_time": 1729947474.0
}
```

## 🎯 Key Features

### Visual Design
✅ **ARC Orange** gradient header  
✅ **Dark theme** matching ARC desktop  
✅ **Smooth animations** and transitions  
✅ **Progress bars** for all metrics  
✅ **Custom scrollbars** (orange)  

### Performance
✅ **Lazy loading** (only active tab updates)  
✅ **Cached system info** (static data loaded once)  
✅ **3-second refresh** (reduced from 2s)  
✅ **Limited buffer** (1000 lines terminal max)  
✅ **~60MB RAM** usage  

### Functionality
✅ **Real SSH terminal** (paramiko)  
✅ **File upload/download**  
✅ **Live system metrics**  
✅ **Command history**  
✅ **Tab completion**  

## 📈 Performance Optimizations

1. **Dashboard only updates when visible**
2. **System info cached** (hostname, platform, etc.)
3. **Terminal buffer limited** to 1000 lines
4. **Network calls batched** (3-second intervals)
5. **Single worker process** (Uvicorn)
6. **Warning-level logging** only
7. **Connection limits** (50 concurrent max)

## 🔧 Technical Details

### Frontend (dashboard.html)
- Pure HTML/CSS/JavaScript (no frameworks)
- WebSocket for SSH terminal
- Fetch API for metrics
- Local storage for settings

### Backend (server.py)
- FastAPI with Uvicorn
- psutil for system metrics
- paramiko for SSH
- asyncio for WebSockets

### System Requirements
- Raspberry Pi (any model)
- Python 3.7+
- SSH server running
- 60MB+ free RAM

## 🐛 Troubleshooting

### Dashboard shows "--" for metrics
```bash
# Check server is running
curl http://localhost:5001/health

# Check system info endpoint
curl http://localhost:5001/system/info
```

### CPU temp not showing
```bash
# Normal on non-Raspberry Pi systems
# Pi should auto-detect thermal sensor
ls /sys/class/thermal/thermal_zone0/temp
```

### SSH not connecting
```bash
# Run SSH setup script
./setup_ssh_keys.sh

# Or manually:
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## 📝 Files Changed

1. **arc/apps/connect/server.py**
   - Added `time` import
   - Enhanced `/system/info` endpoint with:
     - CPU frequency, temp, per-core stats
     - Memory cached/buffers
     - Swap metrics
     - Network stats (bytes, packets, errors)
     - Disk I/O counters
     - Uptime calculation
     - Context switches, interrupts

2. **arc/apps/connect/dashboard.html**
   - Complete redesign with ARC colors
   - New metric cards: Network, Swap, Uptime
   - Enhanced CPU card with freq + temp
   - Better formatting functions
   - Orange accent throughout
   - Improved layout and typography

## 🎉 Result

**Before**: Basic metrics with purple/blue theme  
**After**: Comprehensive monitoring with ARC orange theme  

**Metrics**: 3 basic → 9+ detailed  
**Design**: Generic → ARC-branded  
**Performance**: Same (~60MB RAM)  

---

**Enjoy your fully-themed ARC Connect dashboard!** 🍊

