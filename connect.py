import logging
import os
import time
import socket
import asyncio
import threading
import json
from typing import Optional

import paramiko
import psutil
import aiofiles

from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="ARC connect")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active SSH connections globally
ssh_connections = {}
current_credentials = {}  # Store current session credentials

# Ensure static directory exists
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


async def get_wifi_strength():
    try:
        proc = await asyncio.create_subprocess_shell(
            "iwconfig wlan0",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )
        out, _ = await proc.communicate()
        text = out.decode(errors="ignore")
        for part in text.split():
            if 'Signal' in part and '=' in part:
                try:
                    lvl = int(part.split('=')[1])
                    return max(0, min(100, 2 * (lvl + 100)))
                except ValueError:
                    continue
    except Exception:
        pass
    return 0


async def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


async def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            t = int(f.read()) / 1000.0
        return f"{t:.1f}°C"
    except FileNotFoundError:
        return "N/A"


# Store credentials endpoint
@app.post("/api/store-credentials")
async def store_credentials(request: Request):
    """Store credentials for the current session"""
    global current_credentials
    data = await request.json()
    current_credentials = {
        "ip": data.get("ip"),
        "user": data.get("user"),
        "pass": data.get("pass")
    }
    return {"status": "success"}


# Get stored credentials endpoint
@app.get("/api/get-credentials")
async def get_credentials():
    """Get stored credentials for the current session"""
    global current_credentials
    if current_credentials:
        return current_credentials
    return {"error": "No credentials stored"}


# Test SSH connection endpoint
@app.post("/test-ssh")
async def test_ssh_connection(request: Request):
    """Test SSH connection without WebSocket"""
    data = await request.json()
    host = data.get("host")
    port = data.get("port", 22)
    username = data.get("username")
    password = data.get("password")

    if not all([host, username, password]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=10
        )

        client.close()
        return {"status": "success", "message": f"Successfully connected to {username}@{host}"}

    except paramiko.AuthenticationException:
        raise HTTPException(status_code=401, detail="Authentication failed")
    except paramiko.SSHException as e:
        raise HTTPException(status_code=500, detail=f"SSH connection failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection error: {str(e)}")


@app.get("/")
async def index():
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ARC connect</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm/css/xterm.css" />
  <style>
    :root { --gauge-radius:45; }
    body { margin:0; font-family:sans-serif; display:flex; min-height:100vh; background:#f0f2f5; }
    .sidebar { width:200px; background:#030712; color:#c7cbd0; display:flex; flex-direction:column; align-items:center;}
    .sidebar h1 { text-align:center; margin:20px 0; font-size:1.2em; }
    .nav-item { padding:15px; cursor:pointer; align-items:center; }
    .nav-item.active, .nav-item:hover { color:#fff; }
    .content { flex:1; overflow:auto; padding:20px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:20px; }
    .card { background:#fff; border-radius:8px; padding:20px; box-shadow:0 2px 8px rgba(0,0,0,0.1); position:relative; }
    .card h2 { margin:0 0 10px; font-size:1em; color:#333; }
    .ellipsis { position:absolute; top:20px; right:20px; cursor:pointer; }
    .gauge-container { display:flex; align-items:center; justify-content:center; margin:10px 0; }
    .gauge { width:100px; height:100px; }
    .gauge svg { transform:rotate(-90deg); width:100px; height:100px; }
    .gauge circle.bg { fill:none; stroke:#eee; stroke-width:8; }
    .gauge circle.fg { fill:none; stroke:#0a84ff; stroke-width:8; stroke-linecap:round; transition:stroke-dashoffset 0.6s ease; }
    .gauge-value, .card-value { margin-left:12px; font-size:1.4em; font-weight:bold; color:#333; }
    .card .info { text-align:center; margin-top:6px; color:#555; font-size:0.9em; }
    #xterm { width:100%; min-height:500px; height:70vh; background:#000; border-radius:8px; }
    .drop-zone { border:2px dashed #0a84ff; padding:80px; text-align:center; color:#555; border-radius:8px; cursor:pointer; transition:background 0.2s; }
    .drop-zone.dragover { background:rgba(10,132,255,0.1); }
    #fileList { list-style:none; padding:0; margin:10px 0; max-height:200px; overflow-y:auto; }
    #fileList li { display:flex; justify-content:space-between; align-items:center; padding:8px 12px; border-bottom:1px solid #eee; font-size:0.9em; }
    .progress-bar { width:100%; height:6px; background:#eee; border-radius:3px; overflow:hidden; margin-top:4px; }
    .progress-bar .progress { height:100%; width:0; background:#0a84ff; transition:width 0.2s; }
    #uploadBtn { margin-top:10px; padding:10px 20px; border:none; background:#0a84ff; color:#fff; border-radius:4px; cursor:pointer; }
    #uploadBtn:disabled { background:#ccc; cursor:not-allowed; }
    .connection-info { background:#e8f4fd; padding:10px; border-radius:4px; margin-bottom:10px; font-size:0.9em; }
    .connection-info.error { background:#fee; color:#c53030; }
    .connection-info.success { background:#e6fffa; color:#2d7d32; }
    .reconnect-btn { margin-top:10px; padding:8px 16px; border:none; background:#0a84ff; color:#fff; border-radius:4px; cursor:pointer; }
    .credential-form { background:#f9f9f9; padding:15px; border-radius:4px; margin-bottom:15px; }
    .credential-form input { width:100%; padding:8px; margin:5px 0; border:1px solid #ddd; border-radius:4px; }
    .credential-form button { padding:8px 16px; background:#0a84ff; color:white; border:none; border-radius:4px; cursor:pointer; }
    @media (max-width:768px) {
  body { flex-direction:column; }
  .sidebar { width:100%; flex-direction:row; overflow-x:auto; justify-content:center;}
  .nav-item { flex:1; text-align:center; }
  .content { padding:10px; }
  .grid { grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:10px; }
  .card { padding:15px; }
  #xterm { 
    height:60vh; 
    min-height:400px; 
  }
  #ssh .card {
    min-height:70vh;
  }
}

@media (max-width:480px) {
  .grid { grid-template-columns:1fr; gap:8px; }
  .gauge { width:120px; height:120px; }
  #xterm { 
    height:50vh; 
    min-height:300px; 
  }
  #ssh .card {
    min-height:60vh;
  }
}
  </style>
</head>
<body>
  <div class="sidebar">
    <h1 style="padding:10px; font-weight:bold;">[ARC] connect</h1>
    <div class="nav-item active" data-target="dashboard">Dashboard</div>
    <div class="nav-item" data-target="ssh">SSH</div>
    <div class="nav-item" data-target="files">File Transfer</div>
  </div>

  <div class="content">
    <div id="dashboard" class="view">
      <div class="grid">
        <div class="card">
          <h2>Memory Usage <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="ram-gauge"><svg><circle class="bg" cx="50" cy="50" r="45"/><circle class="fg" cx="50" cy="50" r="45"/></svg></div>
            <div class="gauge-value" id="ram">0%</div>
          </div>
          <div class="info" id="ram-info">-</div>
        </div>
        <div class="card">
          <h2>WiFi Strength <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="wifi-gauge"><svg><circle class="bg" cx="50" cy="50" r="45"/><circle class="fg" cx="50" cy="50" r="45"/></svg></div>
            <div class="gauge-value" id="wifi">0%</div>
          </div>
          <div class="info">IP: <span id="ip">-</span></div>
        </div>
        <div class="card">
          <h2>CPU Load <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="cpu-gauge"><svg><circle class="bg" cx="50" cy="50" r="45"/><circle class="fg" cx="50" cy="50" r="45"/></svg></div>
            <div class="gauge-value" id="cpu">0%</div>
          </div>
          <div class="info">per core</div>
        </div>
        <div class="card">
          <h2>Disk Usage <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="disk-gauge"><svg><circle class="bg" cx="50" cy="50" r="45"/><circle class="fg" cx="50" cy="50" r="45"/></svg></div>
            <div class="gauge-value" id="disk">0%</div>
          </div>
          <div class="info" id="disk-info">-</div>
        </div>
        <div class="card">
          <h2>System Uptime <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container"><div class="card-value" id="uptime">-</div></div>
        </div>
        <div class="card">
          <h2>CPU Temp <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="temp-gauge"><svg><circle class="bg" cx="50" cy="50" r="45"/><circle class="fg" cx="50" cy="50" r="45"/></svg></div>
            <div class="gauge-value" id="temp">0°C</div>
          </div>
          <div class="info" id="temp-info">-</div>
        </div>
      </div>
    </div>

    <div id="ssh" class="view" style="display:none;">
      <div class="card">
        <h2>SSH Terminal</h2>
        <div id="connectionInfo" class="connection-info"></div>

        <!-- Credential form for manual entry -->
        <div id="credentialForm" class="credential-form" style="display:none;">
          <h3>Enter SSH Credentials</h3>
          <input type="text" id="manualIp" placeholder="IP Address (e.g., 127.0.0.1)" />
          <input type="text" id="manualUser" placeholder="Username" />
          <input type="password" id="manualPass" placeholder="Password" />
          <button onclick="connectWithManualCredentials()">Connect</button>
        </div>

        <div id="xterm"></div>
        <button id="reconnectBtn" class="reconnect-btn" style="display:none;">Reconnect</button>
      </div>
    </div>

    <div id="files" class="view" style="display:none;">
      <div class="card">
        <h2>File Transfer</h2>
        <div id="dropZone" class="drop-zone">Drag &amp; drop files here or click to select</div>
        <input type="file" id="fileInput" multiple style="display:none;" />
        <ul id="fileList"></ul>
        <button id="uploadBtn" disabled>Upload All</button>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/xterm/lib/xterm.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit/lib/xterm-addon-fit.js"></script>
  <script>
    // Terminal setup
    const term = new Terminal({ 
      cursorBlink: true,
      fontSize: 14,
      fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
      theme: {
        background: '#000000',
        foreground: '#ffffff',
        cursor: '#ffffff',
        selection: '#ffffff33'
      }
    });
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById("xterm"));
    fitAddon.fit();

    // Connection management
    let sshWs = null;
    let isConnected = false;
    const connectionInfo = document.getElementById('connectionInfo');
    const reconnectBtn = document.getElementById('reconnectBtn');
    const credentialForm = document.getElementById('credentialForm');

    function updateConnectionStatus(message, type = 'info') {
      connectionInfo.textContent = message;
      connectionInfo.className = `connection-info ${type}`;
      reconnectBtn.style.display = type === 'error' ? 'block' : 'none';
    }

    // Try to get credentials from server-side storage first, then localStorage
    async function getCredentials() {
      try {
        // First try to get from server
        const response = await fetch('/api/get-credentials');
        if (response.ok) {
          const serverCreds = await response.json();
          if (serverCreds && !serverCreds.error) {
            return serverCreds;
          }
        }
      } catch (e) {
        console.log('No server credentials found');
      }

      // Fall back to localStorage
      const saved = localStorage.getItem('arcConnection');
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch (e) {
          console.log('Error parsing localStorage credentials:', e);
        }
      }

      return null;
    }

    async function connectSSH() {
      const credentials = await getCredentials();

      if (!credentials || !credentials.ip || !credentials.user || !credentials.pass) {
        updateConnectionStatus('No saved credentials found.', 'error');
        credentialForm.style.display = 'block';
        return;
      }

      credentialForm.style.display = 'none';
      updateConnectionStatus(`Connecting to ${credentials.user}@${credentials.ip}...`, 'info');

      // Connect to WebSocket endpoint
      sshWs = new WebSocket(`ws://localhost:5000/ws/ssh`);

      sshWs.onopen = () => {
        updateConnectionStatus('Connected to proxy, authenticating...', 'info');
        sshWs.send(JSON.stringify({
          host: credentials.ip,
          port: 22,
          username: credentials.user,
          password: credentials.pass
        }));
      };

      sshWs.onmessage = (event) => {
        if (event.data === 'SSH_READY') {
          updateConnectionStatus(`Connected to ${credentials.user}@${credentials.ip}`, 'success');
          isConnected = true;
          term.focus();
        } else if (event.data.startsWith('ERROR:')) {
          updateConnectionStatus(event.data, 'error');
          isConnected = false;
          credentialForm.style.display = 'block';
        } else {
          term.write(event.data);
        }
      };

      sshWs.onerror = (error) => {
        updateConnectionStatus('Connection error occurred', 'error');
        isConnected = false;
        credentialForm.style.display = 'block';
      };

      sshWs.onclose = () => {
        if (isConnected) {
          updateConnectionStatus('Connection closed', 'error');
        }
        isConnected = false;
      };
    }

    // Manual credential connection
    async function connectWithManualCredentials() {
      const ip = document.getElementById('manualIp').value.trim();
      const user = document.getElementById('manualUser').value.trim();
      const pass = document.getElementById('manualPass').value;

      if (!ip || !user || !pass) {
        alert('Please fill in all fields');
        return;
      }

      // Store credentials in localStorage and server
      const credentials = { ip, user, pass };
      localStorage.setItem('arcConnection', JSON.stringify(credentials));

      try {
        await fetch('/api/store-credentials', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(credentials)
        });
      } catch (e) {
        console.log('Failed to store credentials on server:', e);
      }

      // Clear form
      document.getElementById('manualIp').value = '';
      document.getElementById('manualUser').value = '';
      document.getElementById('manualPass').value = '';

      // Connect
      connectSSH();
    }

    // Terminal input handling
    term.onData((data) => {
      if (sshWs && isConnected) {
        sshWs.send(data);
      }
    });

    // Reconnect button handler
    reconnectBtn.addEventListener('click', () => {
      if (sshWs) {
        sshWs.close();
      }
      term.clear();
      connectSSH();
    });

    // Navigation
    const views = document.querySelectorAll('.view'),
          navs  = document.querySelectorAll('.nav-item');
    navs.forEach(n => n.onclick = () => {
      navs.forEach(x => x.classList.remove('active'));
      n.classList.add('active');
      views.forEach(v => v.style.display = 'none');
      document.getElementById(n.dataset.target).style.display = 'block';
      if (n.dataset.target === 'ssh') {
        fitAddon.fit();
        if (!isConnected) {
          connectSSH();
        }
      }
    });

    // Gauges
    function setGauge(id,pct){
      const c = document.querySelector(`#${id}-gauge .fg`),
            r = +c.getAttribute('r'),
            circ = 2*Math.PI*r;
      c.style.strokeDasharray = circ;
      c.style.strokeDashoffset = circ*(1-pct/100);
    }

    async function loadSystemInfo(){
      try {
        const d = await (await fetch('/api/system')).json();
        document.getElementById('ram').innerText = d.ram.percent+'%';
        setGauge('ram',d.ram.percent);
        document.getElementById('ram-info').innerText =
          `${(d.ram.used/1024/1024).toFixed(1)} MiB / ${(d.ram.total/1024/1024).toFixed(1)} MiB`;
        document.getElementById('wifi').innerText = d.wifi+'%';
        document.getElementById('ip').innerText   = d.ip;
        setGauge('wifi',d.wifi);
        document.getElementById('cpu').innerText  = d.cpu_percent+'%';
        setGauge('cpu',d.cpu_percent);
        document.getElementById('disk').innerText = d.disk.percent+'%';
        setGauge('disk',d.disk.percent);
        document.getElementById('disk-info').innerText =
          `${(d.disk.used/1024/1024/1024).toFixed(1)} GiB / ${(d.disk.total/1024/1024/1024).toFixed(1)} GiB`;
        document.getElementById('uptime').innerText = d.uptime;
        document.getElementById('temp').innerText   = d.temp;
        setGauge('temp',parseFloat(d.temp)||0);
      } catch (error) {
        console.error('Failed to load system info:', error);
      }
    }

    loadSystemInfo(); 
    setInterval(loadSystemInfo, 5000);

    // Resize handler
    window.addEventListener('resize', () => {
      fitAddon.fit();
    });

    // File transfer logic
    const dropZone   = document.getElementById('dropZone');
    const fileInput  = document.getElementById('fileInput');
    const fileList   = document.getElementById('fileList');
    const uploadBtn  = document.getElementById('uploadBtn');
    let   files      = [];

    dropZone.addEventListener('click', () => fileInput.click());
    ['dragover','dragenter'].forEach(evt =>
      dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.add('dragover'); })
    );
    ['dragleave','drop'].forEach(evt =>
      dropZone.addEventListener(evt, e => { e.preventDefault(); dropZone.classList.remove('dragover'); })
    );
    dropZone.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
    fileInput.addEventListener('change', e => { handleFiles(e.target.files); fileInput.value = ''; });

    function handleFiles(selected) {
      for (const f of selected) {
        if (!files.some(x => x.name===f.name && x.size===f.size)) files.push(f);
      }
      renderFileList();
    }

    function renderFileList() {
      fileList.innerHTML = '';
      files.forEach((file, idx) => {
        const li = document.createElement('li');
        li.className = 'flex justify-between items-center';
        const name = document.createElement('span');
        name.textContent = file.name;
        li.appendChild(name);
        const remove = document.createElement('button');
        remove.textContent = '✖';
        remove.className = 'ml-2';
        remove.onclick = () => { files.splice(idx,1); renderFileList(); };
        li.appendChild(remove);
        const pb = document.createElement('div'); pb.className = 'progress-bar';
        const p  = document.createElement('div'); p.className = 'progress';
        pb.appendChild(p); li.appendChild(pb);
        file._progressElem = p;
        fileList.appendChild(li);
      });
      uploadBtn.disabled = !files.length;
    }

    function uploadFile(file) {
      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/api_upload');
        xhr.upload.addEventListener('progress', e => {
          if (e.lengthComputable) file._progressElem.style.width = (e.loaded/e.total*100)+'%';
        });
        xhr.onreadystatechange = () => {
          if (xhr.readyState === 4) {
            if (xhr.status === 200) resolve(JSON.parse(xhr.response).filename);
            else reject(xhr.statusText);
          }
        };
        const form = new FormData();
        form.append('file', file);
        xhr.send(form);
      });
    }

    uploadBtn.addEventListener('click', async () => {
      uploadBtn.disabled = true;
      for (const f of files) {
        try { await uploadFile(f); }
        catch (err) { console.error('Upload failed for', f.name, err); }
      }
      files = []; renderFileList();
    });
  </script>
</body>
</html>
"""
    return HTMLResponse(html)


@app.get("/api/system")
async def system_info():
    cpu = psutil.cpu_percent(interval=0.1)
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    upt = time.time() - psutil.boot_time()
    wifi = await get_wifi_strength()
    ip = await get_ip_address()
    temp = await get_cpu_temp()

    return {
        "cpu_percent": cpu,
        "ram": {"total": vm.total, "used": vm.used, "percent": vm.percent},
        "disk": {"total": disk.total, "used": disk.used, "percent": disk.percent},
        "wifi": wifi,
        "ip": ip,
        "uptime": f"{int(upt // 3600)}h{int((upt % 3600) // 60)}m",
        "temp": temp
    }


@app.websocket("/ws/ssh")
async def ws_ssh(ws: WebSocket):
    await ws.accept()
    logging.info("🔌 WebSocket connection accepted")

    try:
        # Wait for authentication data
        auth_data = await ws.receive_json()
        host = auth_data["host"]
        port = auth_data.get("port", 22)
        username = auth_data["username"]
        password = auth_data["password"]

        logging.info(f"🔐 SSH connection attempt: {username}@{host}:{port}")

        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to SSH server
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                look_for_keys=False,
                allow_agent=False,
                timeout=10
            )
            logging.info(f"✅ SSH connection established to {host}")

            # Create interactive shell
            chan = client.invoke_shell(term='xterm-256color', width=80, height=24)

            # Send ready signal
            await ws.send_text("SSH_READY")

            # Set up bidirectional communication
            loop = asyncio.get_event_loop()

            def ssh_to_websocket():
                """Read from SSH and send to WebSocket"""
                try:
                    while True:
                        if chan.recv_ready():
                            data = chan.recv(1024)
                            if not data:
                                break
                            asyncio.run_coroutine_threadsafe(
                                ws.send_text(data.decode('utf-8', errors='ignore')),
                                loop
                            )
                        time.sleep(0.01)
                except Exception as e:
                    logging.error(f"SSH read error: {e}")

            # Start SSH reader thread
            ssh_thread = threading.Thread(target=ssh_to_websocket, daemon=True)
            ssh_thread.start()

            # Handle WebSocket messages (user input)
            while True:
                try:
                    message = await ws.receive_text()
                    if chan.send_ready():
                        chan.send(message)
                except WebSocketDisconnect:
                    logging.info("🔌 WebSocket disconnected")
                    break
                except Exception as e:
                    logging.error(f"WebSocket error: {e}")
                    break

        except paramiko.AuthenticationException:
            await ws.send_text("ERROR: Authentication failed")
            logging.error("❌ SSH authentication failed")
        except paramiko.SSHException as e:
            await ws.send_text(f"ERROR: SSH connection failed: {str(e)}")
            logging.error(f"❌ SSH connection failed: {e}")
        except Exception as e:
            await ws.send_text(f"ERROR: Connection error: {str(e)}")
            logging.error(f"❌ Connection error: {e}")
        finally:
            if 'chan' in locals():
                chan.close()
            client.close()

    except Exception as e:
        logging.error(f"❌ WebSocket error: {e}")
        await ws.send_text(f"ERROR: {str(e)}")
    finally:
        await ws.close()


@app.post("/api_upload")
async def api_upload(file: UploadFile = File(...)):
    uploads = "uploads"
    os.makedirs(uploads, exist_ok=True)
    path = os.path.join(uploads, file.filename)
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())
    return {"filename": file.filename}


@app.get("/api/download/{path:path}")
async def api_download(path: str):
    full = os.path.join("uploads", path)
    if not os.path.isfile(full):
        raise HTTPException(404, detail="File not found")
    return FileResponse(full)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")