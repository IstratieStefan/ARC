import asyncio
import os
import time
import socket
import psutil
import aiofiles
import paramiko
from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ARC connect")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

async def get_wifi_strength():
    proc = await asyncio.create_subprocess_shell(
        "iwconfig wlan0",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    out, _ = await proc.communicate()
    text = out.decode(errors='ignore')
    for part in text.split():
        if 'Signal' in part and '=' in part:
            try:
                lvl = int(part.split('=')[1])
                return max(0, min(100, 2 * (lvl + 100)))
            except ValueError:
                continue
    return 0

async def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except OSError:
        ip = "-"
    finally:
        s.close()
    return ip

async def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            t = int(f.read()) / 1000.0
        return f"{t:.1f}°C"
    except FileNotFoundError:
        return "-"

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
    body { margin:0; font-family:sans-serif; display:flex; height:100vh; background:#f0f2f5; }
    .sidebar { width:200px; background:#030712; color:#c7cbd0; display:flex; flex-direction:column; }
    .sidebar h1 { text-align:center; margin:20px 0; font-size:1.2em; }
    .nav-item { padding:15px; cursor:pointer; }
    .nav-item.active, .nav-item:hover { color:#fff }
    .content { flex:1; overflow:auto; padding:20px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fill, minmax(280px,1fr)); gap:20px; }
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
    #xterm { width:100%; height:400px; background:#000; }

    /* File Transfer Styles */
    .drop-zone {
      border: 2px dashed #0a84ff;
      padding: 40px;
      text-align: center;
      color: #555;
      border-radius: 8px;
      cursor: pointer;
      transition: background 0.2s;
    }
    .drop-zone.dragover {
      background: rgba(10, 132, 255, 0.1);
    }
    #fileList {
      list-style: none;
      padding: 0;
      margin: 10px 0;
      max-height: 200px;
      overflow-y: auto;
    }
    #fileList li {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      border-bottom: 1px solid #eee;
      font-size: 0.9em;
    }
    .progress-bar {
      width: 100%;
      height: 6px;
      background: #eee;
      border-radius: 3px;
      overflow: hidden;
      margin-top: 4px;
    }
    .progress-bar .progress {
      height: 100%;
      width: 0;
      background: #0a84ff;
      transition: width 0.2s;
    }
    #uploadBtn {
      margin-top: 10px;
      padding: 10px 20px;
      border: none;
      background: #0a84ff;
      color: #fff;
      border-radius: 4px;
      cursor: pointer;
    }
    #uploadBtn:disabled {
      background: #ccc;
      cursor: not-allowed;
    }

    /* Responsive for mobile */
    @media (max-width: 768px) {
      body { flex-direction:column; }
      .sidebar { width:100%; flex-direction:row; overflow-x:auto; }
      .nav-item { flex:1; text-align:center; }
      .content { padding:10px; }
      .grid { grid-template-columns:repeat(auto-fill, minmax(180px,1fr)); gap:10px; }
      .card { padding:15px; }
      #xterm { height:250px; }
    }
  </style>
</head>
<body>
  <div class="sidebar">
    <h1>ARC connect</h1>
    <div class="nav-item active" data-target="dashboard">Dashboard</div>
    <div class="nav-item" data-target="ssh">SSH</div>
    <div class="nav-item" data-target="files">File Transfer</div>
  </div>
  <div class="content">
    <!-- Dashboard View -->
    <div id="dashboard" class="view">
      <div class="grid">
        <!-- Memory Card -->
        <div class="card">
          <h2>Memory Usage <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="ram-gauge">
              <svg><circle class="bg" cx="50" cy="50" r="45" /><circle class="fg" cx="50" cy="50" r="45" /></svg>
            </div>
            <div class="gauge-value" id="ram">0%</div>
          </div>
          <div class="info" id="ram-info">-</div>
        </div>
        <!-- Wi-Fi Card -->
        <div class="card">
          <h2>WiFi Strength <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="wifi-gauge">
              <svg><circle class="bg" cx="50" cy="50" r="45" /><circle class="fg" cx="50" cy="50" r="45" /></svg>
            </div>
            <div class="gauge-value" id="wifi">0%</div>
          </div>
          <div class="info">IP: <span id="ip">-</span></div>
        </div>
        <!-- CPU Card -->
        <div class="card">
          <h2>CPU Load <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="cpu-gauge">
              <svg><circle class="bg" cx="50" cy="50" r="45" /><circle class="fg" cx="50" cy="50" r="45" /></svg>
            </div>
            <div class="gauge-value" id="cpu">0%</div>
          </div>
          <div class="info">per core</div>
        </div>
        <!-- Disk Card -->
        <div class="card">
          <h2>Disk Usage <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="disk-gauge">
              <svg><circle class="bg" cx="50" cy="50" r="45" /><circle class="fg" cx="50" cy="50" r="45" /></svg>
            </div>
            <div class="gauge-value" id="disk">0%</div>
          </div>
          <div class="info" id="disk-info">-</div>
        </div>
        <!-- Uptime Card -->
        <div class="card">
          <h2>System Uptime <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="card-value" id="uptime">-</div>
          </div>
        </div>
        <!-- Temperature Card -->
        <div class="card">
          <h2>CPU Temp <span class="ellipsis">⋯</span></h2>
          <div class="gauge-container">
            <div class="gauge" id="temp-gauge">
              <svg><circle class="bg" cx="50" cy="50" r="45" /><circle class="fg" cx="50" cy="50" r="45" /></svg>
            </div>
            <div class="gauge-value" id="temp">0°C</div>
          </div>
          <div class="info" id="temp-info">-</div>
        </div>
      </div>
    </div>
    <!-- SSH terminal View -->
    <div id="ssh" class="view" style="display:none;">
      <div id="xterm"></div>
    </div>
    <!-- Enhanced File transfer View -->
    <div id="files" class="view" style="display:none;">
      <div class="card">
        <h2>File Transfer</h2>
        <div id="dropZone" class="drop-zone">Drag & drop files here or click to select</div>
        <input type="file" id="fileInput" multiple style="display:none;" />
        <ul id="fileList"></ul>
        <button id="uploadBtn" disabled>Upload All</button>
      </div>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/xterm/lib/xterm.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit/lib/xterm-addon-fit.js"></script>
  <script>
    // Navigation logic
    const views = document.querySelectorAll('.view'), navs = document.querySelectorAll('.nav-item');
    navs.forEach(n => n.onclick = () => {
      navs.forEach(x => x.classList.remove('active'));
      n.classList.add('active');
      views.forEach(v => v.style.display = 'none');
      document.getElementById(n.dataset.target).style.display = 'block';
      if (n.dataset.target === 'ssh') fitAddon.fit();
    });

    // Gauge helper
    function setGauge(id, pct) {
      const circle = document.querySelector(`#${id}-gauge .fg`);
      const radius = Number(circle.getAttribute('r'));
      const circumference = 2 * Math.PI * radius;
      circle.style.strokeDasharray = circumference;
      circle.style.strokeDashoffset = circumference * (1 - pct / 100);
    }

    // Load system metrics
    async function load() {
      const res = await fetch('/api/system');
      const d = await res.json();
      document.getElementById('ram').innerText = d.ram.percent + '%'; setGauge('ram', d.ram.percent);
      document.getElementById('ram-info').innerText = `${(d.ram.used/1024/1024).toFixed(1)} MiB / ${(d.ram.total/1024/1024).toFixed(1)} MiB`;
      document.getElementById('wifi').innerText = d.wifi + '%'; document.getElementById('ip').innerText = d.ip; setGauge('wifi', d.wifi);
      document.getElementById('cpu').innerText = d.cpu_percent + '%'; setGauge('cpu', d.cpu_percent);
      document.getElementById('disk').innerText = d.disk.percent + '%'; setGauge('disk', d.disk.percent);
      document.getElementById('disk-info').innerText = `${(d.disk.used/1024/1024/1024).toFixed(1)} GiB / ${(d.disk.total/1024/1024/1024).toFixed(1)} GiB`;
      document.getElementById('uptime').innerText = d.uptime;
      document.getElementById('temp').innerText = d.temp; setGauge('temp', parseFloat(d.temp) || 0);
    }
    load(); setInterval(load, 5000);

    // SSH terminal setup
    const term = new Terminal(), fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon); term.open(document.getElementById('xterm')); fitAddon.fit();
    const ws = new WebSocket(`ws://${location.host}/ws/ssh`);
    term.onData(data => ws.send(data)); ws.onmessage = e => term.write(e.data);

    // Enhanced File transfer logic
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const uploadBtn = document.getElementById('uploadBtn');
    let files = [];

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', e => {
      e.preventDefault(); dropZone.classList.remove('dragover'); handleFiles(Array.from(e.dataTransfer.files));
    });
    fileInput.addEventListener('change', () => handleFiles(Array.from(fileInput.files)));

    function handleFiles(selected) {
      selected.forEach(f => {
        if (!files.find(x => x.name === f.name && x.size === f.size)) {
          files.push(f);
          const li = document.createElement('li');
          li.innerHTML = `<span>${f.name}</span><div class=\"progress-bar\"><div class=\"progress\"></div></div>`;
          fileList.appendChild(li);
        }
      });
      uploadBtn.disabled = files.length === 0;
    }

    uploadBtn.addEventListener('click', () => {
      files.forEach((f, idx) => {
        const li = fileList.children[idx];
        uploadFile(f, li.querySelector('.progress'));
      });
    });

    function uploadFile(file, progressEl) {
      const xhr = new XMLHttpRequest();
      const form = new FormData(); form.append('file', file);
      xhr.open('POST', '/api_upload');
      xhr.upload.addEventListener('progress', e => {
        if (e.lengthComputable) {
          progressEl.style.width = `${(e.loaded/e.total)*100}%`;
        }
      });
      xhr.onload = () => {
        if (xhr.status === 200) progressEl.style.background = '#4caf50'; else progressEl.style.background = '#f44336';
      };
      xhr.send(form);
    }
  </script>
</body>
</html>

"""
    return HTMLResponse(html)

@app.get('/api/system')
async def system_info():
    cpu = psutil.cpu_percent(interval=0.1)
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    upt = time.time() - psutil.boot_time()
    wifi = await get_wifi_strength()
    ip = await get_ip_address()
    temp = await get_cpu_temp()

    return {
        'cpu_percent': cpu,
        'ram': {'total': vm.total, 'used': vm.used, 'percent': vm.percent},
        'disk': {'total': disk.total, 'used': disk.used, 'percent': disk.percent},
        'wifi': wifi,
        'ip': ip,
        'uptime': f"{int(upt//3600)}h{int((upt%3600)//60)}m",
        'temp': temp
    }

@app.websocket('/ws/ssh')
async def ws_ssh(ws: WebSocket):
    await ws.accept()
    ssh = paramiko.SSHClient(); ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('localhost', username=os.getlogin())
    chan = ssh.invoke_shell()

    async def recv_loop():
        while True:
            data = chan.recv(1024)
            if not data: break
            await ws.send_text(data.decode(errors='ignore'))

    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, lambda: asyncio.run(recv_loop()))

    try:
        while True:
            msg = await ws.receive_text()
            chan.send(msg)
    except:
        pass
    finally:
        chan.close()
        ssh.close()

@app.post('/api_upload')
async def api_upload(file: UploadFile = File(...)):
    d = 'uploads'; os.makedirs(d, exist_ok=True)
    p = os.path.join(d, file.filename)
    async with aiofiles.open(p, 'wb') as f:
        await f.write(await file.read())
    return {'filename': file.filename}

@app.get('/api/download/{p:path}')
async def api_download(p: str):
    f = os.path.join('uploads', p)
    if not os.path.isfile(f): raise HTTPException(404)
    return FileResponse(f)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
