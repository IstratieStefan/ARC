"""
ARC Connect - Minimal, Low-Resource Server with Real SSH
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import os
import shutil
import psutil
from pathlib import Path
import asyncio
import paramiko
from io import StringIO

app = FastAPI(title="ARC Connect", docs_url="/api")

# Minimal CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent.parent.parent
UPLOAD_FOLDER = Path("/home/admin/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Serve minimal dashboard
@app.get("/", response_class=HTMLResponse)
async def root():
    dashboard_path = Path(__file__).parent / "dashboard_minimal.html"
    with open(dashboard_path, 'r') as f:
        return HTMLResponse(content=f.read())

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/system/info")
async def system_info():
    """Minimal system info - only what's needed"""
    return {
        "hostname": os.uname().nodename,
        "architecture": os.uname().machine,
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory": {"percent": psutil.virtual_memory().percent},
        "disk": {"percent": psutil.disk_usage('/').percent},
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        path = UPLOAD_FOLDER / file.filename
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return {"filename": file.filename, "size": path.stat().st_size}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/files")
async def list_files():
    files = []
    for item in UPLOAD_FOLDER.iterdir():
        if item.is_file():
            files.append({
                "name": item.name,
                "size": item.stat().st_size,
                "is_dir": False
            })
    return {"files": files}

@app.get("/files/download/{filename}")
async def download(filename: str):
    path = UPLOAD_FOLDER / filename
    if not path.exists():
        raise HTTPException(404)
    return FileResponse(path, filename=filename)

@app.delete("/files/{filename}")
async def delete(filename: str):
    path = UPLOAD_FOLDER / filename
    if path.exists():
        path.unlink()
    return {"ok": True}

# Real SSH WebSocket
class SSHSession:
    def __init__(self):
        self.client = None
        self.channel = None
        
    def connect(self, host='localhost', port=22, username='admin', password=None):
        """Connect to SSH server"""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            self.client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=10,
                allow_agent=False,
                look_for_keys=False
            )
            
            # Open interactive shell
            self.channel = self.client.invoke_shell(
                term='xterm',
                width=120,
                height=40
            )
            self.channel.settimeout(0.1)
            return True
        except Exception as e:
            return False
    
    def send_command(self, command: str):
        """Send command to SSH shell"""
        if self.channel:
            self.channel.send(command + '\n')
    
    def read_output(self):
        """Read output from SSH shell"""
        if not self.channel:
            return ''
        
        output = ''
        try:
            while self.channel.recv_ready():
                data = self.channel.recv(4096).decode('utf-8', errors='ignore')
                output += data
        except:
            pass
        return output
    
    def close(self):
        """Close SSH connection"""
        if self.channel:
            self.channel.close()
        if self.client:
            self.client.close()

@app.websocket("/ws/ssh")
async def websocket_ssh(websocket: WebSocket):
    """Real SSH terminal via WebSocket"""
    await websocket.accept()
    
    ssh = SSHSession()
    
    try:
        # Wait for connection parameters or connect to localhost
        try:
            # Try to receive initial connection data (for compatibility)
            data = await asyncio.wait_for(websocket.receive_text(), timeout=2.0)
            import json
            params = json.loads(data)
            host = params.get('host', 'localhost')
            username = params.get('username', 'admin')
            password = params.get('password', '')
        except:
            # Default to localhost
            host = 'localhost'
            username = os.getenv('USER', 'admin')
            password = None
        
        # Connect to SSH
        if not ssh.connect(host, 22, username, password):
            await websocket.send_text('[ERROR] SSH connection failed\n')
            await websocket.send_text(f'Could not connect to {username}@{host}\n')
            await websocket.send_text('Check credentials and try again.\n')
            return
        
        await websocket.send_text(f'Connected to {username}@{host}\n\n')
        
        # Read initial output (login banner, prompt, etc.)
        await asyncio.sleep(0.5)
        initial = ssh.read_output()
        if initial:
            await websocket.send_text(initial)
        
        # Main loop - bidirectional communication
        while True:
            # Check for commands from websocket
            try:
                command = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                ssh.send_command(command)
            except asyncio.TimeoutError:
                pass
            except WebSocketDisconnect:
                break
            
            # Read and send SSH output
            output = ssh.read_output()
            if output:
                await websocket.send_text(output)
            
            await asyncio.sleep(0.05)  # Small delay to reduce CPU usage
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(f'\n[ERROR] {str(e)}\n')
        except:
            pass
    finally:
        ssh.close()

if __name__ == "__main__":
    import uvicorn
    # Minimal configuration for low resource usage
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001,
        log_level="warning",  # Less logging
        access_log=False,     # No access logs
        workers=1,            # Single worker
        limit_concurrency=10  # Limit concurrent connections
    )

