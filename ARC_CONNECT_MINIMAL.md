# ARC Connect - Minimal Mode

Lightweight version with real SSH terminal, minimal resource usage, and clean interface.

## Features

✅ **Real SSH Terminal** - Full SSH session with interactive shell  
✅ **Low Resource Usage** - Single worker, minimal logging, optimized  
✅ **Clean Interface** - Terminal-style UI, simple and fast  
✅ **File Transfer** - Upload/download files  
✅ **System Metrics** - CPU, memory, disk stats  

## Installation

```bash
cd /home/admin/ARC

# Install dependencies
venv/bin/pip install paramiko

# Copy files
# Make sure these files are in arc/apps/connect/:
# - server_minimal.py
# - dashboard_minimal.html
```

## Start Server

```bash
cd /home/admin/ARC
./start_arc_connect_minimal.sh
```

Or manually:

```bash
cd /home/admin/ARC
venv/bin/python arc/apps/connect/server_minimal.py
```

## Access

Open browser: `http://[your-pi-ip]:5001/`

### Three Tabs:

1. **STATS** - System metrics (CPU, RAM, Disk)
2. **SSH** - Real interactive SSH terminal
3. **FILES** - Upload/download/delete files

## SSH Terminal

The SSH terminal:
- ✅ Connects to localhost by default (current device)
- ✅ Uses your current user credentials
- ✅ Full interactive shell (bash/zsh)
- ✅ Real-time output
- ✅ Command history
- ✅ Colors and formatting preserved

Just type commands like a normal terminal:
```
ls -la
cd /home/admin
ps aux
top
```

## Configuration

Edit `server_minimal.py` to customize:

```python
# Change default SSH connection
host = 'localhost'      # SSH host
username = 'admin'      # SSH username
port = 22              # SSH port
```

## Resource Usage

Optimized for Raspberry Pi:
- **CPU**: ~1-2% idle, ~5-10% active
- **Memory**: ~30-50 MB
- **Single worker** process
- **No access logs** (less disk I/O)
- **Minimal UI** (less browser memory)

## Autostart

Add to `~/.config/openbox/autostart`:

```bash
/home/admin/ARC/venv/bin/python /home/admin/ARC/arc/apps/connect/server_minimal.py > /tmp/arc_connect.log 2>&1 &
```

Or create systemd service:

```ini
[Unit]
Description=ARC Connect Minimal
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=/home/admin/ARC
ExecStart=/home/admin/ARC/venv/bin/python /home/admin/ARC/arc/apps/connect/server_minimal.py
Restart=always
StandardOutput=null
StandardError=null

[Install]
WantedBy=multi-user.target
```

## API Endpoints

Minimal set:
- `GET /` - Dashboard UI
- `GET /health` - Health check
- `GET /system/info` - System stats
- `POST /upload` - Upload file
- `GET /files` - List files
- `GET /files/download/{name}` - Download
- `DELETE /files/{name}` - Delete
- `WS /ws/ssh` - SSH WebSocket

## Troubleshooting

### SSH not connecting

1. Check if SSH is installed:
```bash
which ssh
sudo systemctl status ssh
```

2. Test SSH locally:
```bash
ssh localhost
```

3. Check user permissions

### Terminal colors not working

The terminal preserves ANSI colors. If you see raw codes, your SSH server might need:
```bash
export TERM=xterm-256color
```

### High resource usage

The minimal version should use <50MB RAM. If higher:
1. Close unused browser tabs
2. Restart the server
3. Check for zombie processes

## Compare: Minimal vs Full

| Feature | Minimal | Full |
|---------|---------|------|
| RAM Usage | ~40MB | ~80MB |
| CPU Usage | 1-2% | 3-5% |
| UI Size | 10KB | 50KB |
| SSH | Real SSH | Simulated |
| File Transfer | ✅ | ✅ |
| Metrics | Basic | Detailed |
| WebSocket | SSH only | SSH + Terminal |
| Logging | Minimal | Full |

---

**Use Minimal Mode for:**
- Raspberry Pi Zero/1/2
- Low memory situations  
- Production deployments
- Remote SSH access
- Simple file transfers

**Use Full Mode for:**
- Development
- Feature-rich interface
- Multiple simultaneous users
- WebSocket terminal experiments

