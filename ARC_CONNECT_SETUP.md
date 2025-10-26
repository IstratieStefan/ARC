# ARC Connect Setup Guide

Complete guide for setting up the ARC Connect web interface and backend server.

## What is ARC Connect?

ARC Connect is a comprehensive web-based management interface for your ARC device that provides:

- 📁 **File Management** - Upload, download, and manage files remotely
- 💻 **System Monitoring** - Real-time CPU, memory, and disk usage
- 🚀 **App Management** - Launch and manage ARC applications
- 🖥️ **Terminal Access** - WebSocket-based terminal emulation
- 📊 **System Info** - Detailed hardware and software information
- 🔗 **API Access** - Full REST API with auto-generated documentation

## Installation

### 1. Install Dependencies

On your Raspberry Pi:

```bash
cd /home/admin/ARC

# Activate venv
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn[standard] python-multipart websockets psutil
```

Or install from requirements.txt:

```bash
cd /home/admin/ARC
venv/bin/pip install -r requirements.txt
```

### 2. Run the Server

#### Manual Start (for testing):

```bash
cd /home/admin/ARC
venv/bin/uvicorn arc.apps.connect.server:app --host 0.0.0.0 --port 5001 --reload
```

#### Start on Boot (Systemd Service):

Create `/etc/systemd/system/arc-connect.service`:

```ini
[Unit]
Description=ARC Connect Web Server
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/ARC
Environment="PATH=/home/admin/ARC/venv/bin"
ExecStart=/home/admin/ARC/venv/bin/uvicorn arc.apps.connect.server:app --host 0.0.0.0 --port 5001
Restart=always
RestartSec=10
StandardOutput=append:/home/admin/arc_connect.log
StandardError=append:/home/admin/arc_connect.log

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable arc-connect.service
sudo systemctl start arc-connect.service
sudo systemctl status arc-connect.service
```

#### Add to Openbox Autostart:

Edit `~/.config/openbox/autostart` and add:

```bash
# Start ARC Connect server
/home/admin/ARC/venv/bin/uvicorn arc.apps.connect.server:app --host 0.0.0.0 --port 5001 > /home/admin/arc_connect.log 2>&1 &
```

## Usage

### Access the Web Interface

Once the server is running:

1. **From the same device:**
   - Open browser: `http://localhost:5001/`

2. **From another device on the network:**
   - Find your Pi's IP: `hostname -I`
   - Open browser: `http://[your-pi-ip]:5001/`

3. **Using ARC Connect page:**
   - Go to website ARC Connect page
   - Enter your Pi's IP address
   - Enter SSH credentials
   - Click "Connect to ARC"

### API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: `http://[your-pi-ip]:5001/docs`
- **ReDoc**: `http://[your-pi-ip]:5001/redoc`

### Display QR Code with IP

Launch the IP display app from the ARC launcher or run:

```bash
/home/admin/ARC/venv/bin/python -m arc.apps.connect.ip
```

This shows your IP address with a QR code for easy connection.

## API Endpoints

### Health & Status

- `GET /` - API information
- `GET /health` - Health check (used by website)
- `GET /system/info` - System information (CPU, memory, disk)

### File Management

- `POST /upload` - Upload files
- `GET /files` - List files
- `GET /files/download/{filename}` - Download file
- `DELETE /files/{filename}` - Delete file

### Command Execution

- `POST /execute` - Execute whitelisted commands

### WebSocket Endpoints

- `ws://[ip]:5001/ws/terminal` - Terminal emulation
- `ws://[ip]:5001/ws/ssh` - SSH connection (for website)

### ARC Specific

- `GET /arc/apps` - List ARC applications
- `POST /arc/launch/{app_name}` - Launch ARC app

## Features

### 1. File Upload/Download

Upload files to `/home/admin/uploads/`:

```bash
curl -X POST -F "file=@myfile.txt" http://localhost:5001/upload
```

Download files:

```bash
curl http://localhost:5001/files/download/myfile.txt -o myfile.txt
```

### 2. System Monitoring

Get real-time system stats:

```bash
curl http://localhost:5001/system/info
```

Returns:
```json
{
  "hostname": "raspberrypi",
  "cpu_percent": 15.2,
  "memory": {
    "total": 4147200000,
    "percent": 45.3
  },
  "disk": {
    "total": 62725623808,
    "percent": 23.1
  }
}
```

### 3. Real SSH Terminal

The terminal provides a **real SSH connection** to your device:

**Features:**
- ✅ Full interactive shell (bash/zsh/fish)
- ✅ All commands work: `ls`, `cd`, `vim`, `nano`, `htop`, etc.
- ✅ ANSI colors preserved
- ✅ Tab completion (press Tab)
- ✅ Command history (Arrow Up/Down)
- ✅ Ctrl+C to interrupt
- ✅ Real-time output streaming

**Technical:**
- Uses paramiko for SSH connections
- Connects to localhost by default
- xterm-256color terminal emulation
- WebSocket-based bidirectional communication

```javascript
// Example: Connect to SSH terminal
const ws = new WebSocket('ws://192.168.1.100:5001/ws/terminal');

ws.onmessage = (event) => {
  console.log('SSH Output:', event.data);
};

// Send command
ws.send('ls -la\n');

// Send Ctrl+C
ws.send('\x03');
```

### 4. Launch ARC Apps

```bash
# List apps
curl http://localhost:5001/arc/apps

# Launch music player
curl -X POST http://localhost:5001/arc/launch/music_player
```

## Performance & Resource Usage

**RAM-Optimized Features:**
- Dashboard updates only when tab is active
- Limited terminal output buffer (1000 lines max)
- System info cached after first load
- Single worker process
- Reduced update frequency (3 seconds vs 2)
- Lazy loading for file list

**Expected Resource Usage:**
- **RAM**: ~60MB (fancy UI with SSH)
- **CPU**: 2-5% idle, 10-15% during SSH use
- **Network**: Minimal when idle
- **Disk I/O**: Low (warning-level logging only)

**Optimizations Applied:**
- Single uvicorn worker
- Connection limit: 50 concurrent
- Keep-alive timeout: 30s
- Warning-level logging (not info/debug)
- WebSocket with small delays to reduce CPU

## Security Notes

⚠️ **Important Security Considerations:**

1. **SSH Access** - Real SSH connection (requires SSH credentials)
2. **Command Execution** - Only whitelisted commands in /execute endpoint
3. **Network Access** - Server binds to 0.0.0.0 (all interfaces)
4. **CORS** - Currently allows all origins (*)
5. **File Upload** - Files go to `/home/admin/uploads/`

For production use, consider:
- Adding authentication (JWT tokens)
- Restricting CORS to specific domains
- Using HTTPS with SSL certificates
- Implementing rate limiting
- SSH key authentication instead of passwords

## Troubleshooting

### Server won't start

Check if port 5001 is already in use:

```bash
sudo lsof -i :5001
```

View server logs:

```bash
tail -f /home/admin/arc_connect.log
```

### Can't connect from another device

1. Check firewall:
```bash
sudo ufw allow 5001
```

2. Verify server is listening:
```bash
netstat -tulpn | grep 5001
```

3. Test connectivity:
```bash
curl http://localhost:5001/health
```

### SSH Terminal not connecting

1. **Check SSH service is running:**
```bash
sudo systemctl status ssh
sudo systemctl start ssh
sudo systemctl enable ssh
```

2. **Test SSH locally:**
```bash
ssh localhost
```

3. **Install OpenSSH server if missing:**
```bash
sudo apt-get install openssh-server
```

4. **Check SSH configuration:**
```bash
sudo nano /etc/ssh/sshd_config
# Make sure PasswordAuthentication is set to yes
sudo systemctl restart ssh
```

### WebSocket connection fails

Make sure you're using `ws://` (not `wss://`) unless you have SSL configured.

### Terminal colors not showing

The terminal uses xterm-256color. If colors don't work:
```bash
export TERM=xterm-256color
```

### Permission errors

Ensure the uploads directory exists and is writable:

```bash
mkdir -p /home/admin/uploads
chmod 755 /home/admin/uploads
```

## Development

### Run in Development Mode

```bash
cd /home/admin/ARC
venv/bin/uvicorn arc.apps.connect.server:app --host 0.0.0.0 --port 5001 --reload
```

The `--reload` flag auto-restarts the server when code changes.

### Test API Endpoints

Using curl:

```bash
# Health check
curl http://localhost:5001/health

# System info
curl http://localhost:5001/system/info

# Upload file
curl -X POST -F "file=@test.txt" http://localhost:5001/upload

# List files
curl http://localhost:5001/files

# Execute command
curl -X POST http://localhost:5001/execute -H "Content-Type: application/json" -d '{"command":"uptime"}'
```

## Integration with ARC Connect Website

The server is designed to work with the ARC Connect web interface in `/website/`.

The website expects:
- Server on port **5001** (not 5000)
- `/health` endpoint for connectivity check
- WebSocket at `/ws/ssh` for SSH authentication
- After successful connection, redirects to web interface

## Next Steps

1. **Build the website** (if you want to serve static files):
```bash
cd website/ARC_website/project
npm install
npm run build
```

2. **Add SSL/HTTPS** for secure remote access

3. **Implement authentication** for production use

4. **Add more features** - The API is extensible!

---

**For more information, visit the API docs at: `http://[your-pi-ip]:5001/docs`**

