import asyncio
import os
from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import psutil
import aiofiles

app = FastAPI(title="PiCockpit")

# Serve static files (if you add assets to 'static/' directory)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>PiCockpit Dashboard</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        pre { background: #f4f4f4; padding: 10px; overflow: auto; }
        #terminal { width: 100%; height: 300px; background: #000; color: #0f0; padding: 10px; overflow-y: scroll; }
        #cmd { width: calc(100% - 80px); }
      </style>
    </head>
    <body>
      <h1>PiCockpit Dashboard</h1>
      <h2>System Info</h2>
      <pre id="sysinfo">Loading...</pre>

      <h2>Terminal</h2>
      <div id="terminal"></div>
      <input type="text" id="cmd" placeholder="Enter command" />
      <button onclick="sendCmd()">Send</button>

      <h2>File Transfer</h2>
      <form id="uploadForm">
        <input type="file" id="fileInput" />
        <button type="button" onclick="uploadFile()">Upload</button>
      </form>
      <script>
        // WebSocket for terminal
        const ws = new WebSocket(`ws://${location.host}/ws/terminal`);
        const term = document.getElementById('terminal');
        ws.onmessage = e => { term.innerText += e.data; term.scrollTop = term.scrollHeight; };
        function sendCmd() {
          const input = document.getElementById('cmd');
          ws.send(input.value + '\n');
          input.value = '';
        }
        // Poll system info
        async function loadSysInfo() {
          const res = await fetch('/api/system');
          const data = await res.json();
          document.getElementById('sysinfo').innerText = JSON.stringify(data, null, 2);
        }
        setInterval(loadSysInfo, 2000);
        loadSysInfo();
        // File upload
        async function uploadFile() {
          const file = document.getElementById('fileInput').files[0];
          if (!file) return;
          const form = new FormData(); form.append('file', file);
          const res = await fetch('/api/upload', { method: 'POST', body: form });
          const txt = await res.json();
          alert('Uploaded: ' + txt.filename);
        }
      </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

@app.get("/api/system")
async def system_info():
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "mem": {
            "total": psutil.virtual_memory().total,
            "used": psutil.virtual_memory().used,
            "percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "total": psutil.disk_usage("/").total,
            "used": psutil.disk_usage("/").used,
            "percent": psutil.disk_usage("/").percent,
        },
    }

@app.websocket("/ws/terminal")
async def websocket_terminal(ws: WebSocket):
    await ws.accept()
    # Start a bash shell
    proc = await asyncio.create_subprocess_shell(
        '/bin/bash',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    async def read_stdout():
        while True:
            data = await proc.stdout.read(1024)
            if not data:
                break
            await ws.send_text(data.decode(errors='ignore'))
    read_task = asyncio.create_task(read_stdout())
    try:
        while True:
            msg = await ws.receive_text()
            proc.stdin.write(msg.encode())
            await proc.stdin.drain()
    except Exception:
        pass
    finally:
        read_task.cancel()
        proc.kill()
        await proc.wait()

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    upload_dir = 'uploads'
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, file.filename)
    async with aiofiles.open(path, 'wb') as f:
        await f.write(await file.read())
    return {"filename": file.filename}

@app.get("/api/download/{filepath:path}")
async def download_file(filepath: str):
    full = os.path.join('uploads', filepath)
    if not os.path.isfile(full):
        raise HTTPException(status_code=404, detail='Not found')
    return FileResponse(full)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=5000)
