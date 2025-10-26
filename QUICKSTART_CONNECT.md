# ARC Connect - Quick Start Guide

## 🚀 How It Works Now

**Simple:** Launch ARC Connect from the launcher → Everything works automatically!

```
┌─────────────────────────────────────────────────┐
│  Click "ARC connect" in launcher               │
│             ↓                                   │
│  App opens with QR code                        │
│             ↓                                   │
│  Webserver starts automatically (port 5001)    │
│             ↓                                   │
│  Scan QR code or visit URL                     │
│             ↓                                   │
│  Dashboard opens in browser                    │
│             ↓                                   │
│  View metrics, upload/download files           │
│             ↓                                   │
│  Close app (press ESC)                         │
│             ↓                                   │
│  Server stops automatically                    │
└─────────────────────────────────────────────────┘
```

## 📱 What You See

### **On Raspberry Pi Screen:**
```
        ARC Connect
        ● Server Running

    ┌─────────────────┐
    │                 │
    │   [QR CODE]     │
    │                 │
    └─────────────────┘

    http://192.168.1.100:5001/

  Scan QR code or visit URL in
  browser to access the ARC
  Connect Dashboard

IP: 192.168.1.100
```

### **On Your Phone/Laptop:**
After scanning QR or visiting URL:
- Full dashboard with metrics
- CPU, Memory, Disk, Network stats
- File upload/download
- Real-time updates

## 🎯 Usage Steps

### **Step 1: Launch App**
```bash
# From ARC Launcher, click "ARC connect"
# Or manually:
cd /home/admin/ARC
venv/bin/python -m arc.apps.connect.ip
```

### **Step 2: Access Dashboard**
Choose one:
- **Phone:** Scan QR code with camera
- **Laptop:** Type URL in browser
- **Pi:** Open browser to `http://localhost:5001/`

### **Step 3: Done**
Press ESC on Pi to close app
Server stops automatically

## 📊 Dashboard Features

**Metrics (9 cards + per-core):**
- CPU Usage (with frequency & temperature)
- Memory Usage
- Disk Usage
- Network Stats (sent/received data)
- Swap Memory
- System Uptime
- Disk I/O (read/write)
- Processes (count + threads)
- Load Average (1/5/15 min)
- CPU Per-Core Usage (grid view)

**Files:**
- Drag & drop upload
- Download files
- Delete files
- See file sizes

## 🔧 Technical Info

**Server:**
- Starts: When app opens
- Stops: When app closes
- Port: 5001
- Access: Any device on same network
- RAM: ~75MB total (app + server)

**QR Code:**
- Contains: Full dashboard URL
- Size: 180x180 pixels
- Format: `http://[pi-ip]:5001/`

## 🌐 Access URLs

**From Same Network:**
```
http://[your-pi-ip]:5001/
```

**From Pi Itself:**
```
http://localhost:5001/
or
http://127.0.0.1:5001/
```

**API Endpoints:**
```
http://[pi-ip]:5001/health         - Health check
http://[pi-ip]:5001/system/info    - System metrics JSON
http://[pi-ip]:5001/files          - List files
```

## 💡 Pro Tips

1. **Bookmark the URL** on your phone for quick access
2. **Share QR code** via screenshot to other devices
3. **Check firewall** if can't access: `sudo ufw allow 5001`
4. **Monitor remotely** from anywhere on your network
5. **Upload files** by dragging into browser

## 🐛 Common Issues

### **Can't Access Dashboard**
```bash
# 1. Check server is running on Pi
curl http://localhost:5001/health

# 2. Check firewall
sudo ufw status
sudo ufw allow 5001

# 3. Check same network
# Phone and Pi must be on same WiFi
```

### **QR Code Won't Scan**
- Try manual URL entry in browser
- Make sure camera has permission to scan QR codes
- Use better lighting if QR code is hard to read
- Try typing IP address manually

### **Port 5001 Already in Use**
```bash
# Kill any existing server
sudo lsof -i :5001
sudo kill -9 <PID>

# Then launch ARC Connect again
```

## 📁 Files Structure

```
/home/admin/ARC/
├── arc/
│   └── apps/
│       └── connect/
│           ├── ip.py              ← App display (modified)
│           ├── server.py          ← FastAPI backend
│           └── dashboard.html     ← Web dashboard
└── config/
    └── arc.yaml                   ← Launcher config
```

## 🎨 Customization

**Change Port:**
Edit `arc/apps/connect/ip.py`, line 52:
```python
port=5001,  # Change to your preferred port
```

**Change QR Size:**
Edit `arc/apps/connect/ip.py`, line 72:
```python
qr_surface = make_qr_code(dashboard_url, size=200)  # Change size
```

## ✅ What's New

**Before:**
- Launch app → Shows IP
- Manually start server in terminal
- QR code was just IP address
- Two separate processes to manage

**Now:**
- Launch app → Everything automatic
- Server starts/stops with app
- QR code is full URL to dashboard
- One simple process

## 📈 Resource Usage

**When App is Open:**
- RAM: ~75MB (app + server)
- CPU: 2-5% idle
- Disk: Minimal

**When App is Closed:**
- RAM: 0MB
- CPU: 0%
- Disk: 0%

## 🎉 Enjoy!

Your ARC Connect is now a **one-click remote monitoring and file management solution**!

Just launch the app, scan the QR code, and you're connected! 🍊📱

