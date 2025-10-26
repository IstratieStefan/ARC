"""
ARC Connect Server - Comprehensive FastAPI backend for ARC device management
Integrates with the ARC Connect web interface
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
import os
import shutil
import subprocess
import platform
import psutil
from pathlib import Path
from typing import List, Optional
import asyncio
import json

app = FastAPI(
    title="ARC Connect API",
    description="Remote management and control interface for ARC device",
    version="2.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent.parent
UPLOAD_FOLDER = Path("/home/admin/uploads")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Serve static website
WEBSITE_DIR = BASE_DIR / "website" / "ARC_website" / "project" / "dist"
if WEBSITE_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEBSITE_DIR)), name="static")

# =====================
# Health & Status
# =====================

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "ARC Connect API",
        "version": "2.0",
        "status": "online",
        "message": "ARC Connect is running! Visit /docs for interactive API documentation",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "system": "/system/info",
            "files": "/files",
            "upload": "/upload",
            "terminal": "ws://{host}:5001/ws/terminal"
        }
    }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - Web Interface"""
    return await web_interface(request)

@app.get("/health")
async def health_check():
    """Health check endpoint for connectivity testing"""
    return {
        "status": "healthy",
        "message": "ARC Connect is running",
        "timestamp": psutil.boot_time()
    }

async def web_interface(request: Request):
    """Web interface for ARC Connect"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ARC Connect</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 800px;
                width: 100%;
                padding: 40px;
            }
            h1 {
                color: #667eea;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .status {
                background: #10b981;
                color: white;
                padding: 15px 25px;
                border-radius: 10px;
                display: inline-block;
                margin-bottom: 30px;
                font-weight: 600;
            }
            .card {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .card h3 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            .endpoint {
                background: white;
                padding: 12px 15px;
                border-radius: 8px;
                margin-bottom: 10px;
                border-left: 4px solid #667eea;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .endpoint code {
                color: #667eea;
                font-family: 'Courier New', monospace;
                font-weight: 600;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                display: inline-block;
                margin-top: 10px;
                font-weight: 600;
                transition: background 0.3s;
            }
            .btn:hover {
                background: #5568d3;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            .stat-label {
                color: #666;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ARC Connect</h1>
            <p class="subtitle">Remote Management Interface</p>
            
            <div class="status">
                ✅ Server Online
            </div>

            <div class="card">
                <h3>📊 System Status</h3>
                <div class="stats" id="stats">
                    <div class="stat-card">
                        <div class="stat-value" id="cpu">--</div>
                        <div class="stat-label">CPU Usage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="memory">--</div>
                        <div class="stat-label">Memory Usage</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="disk">--</div>
                        <div class="stat-label">Disk Usage</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>🔗 API Endpoints</h3>
                <div class="endpoint">
                    <code>GET /health</code>
                    <span>Health Check</span>
                </div>
                <div class="endpoint">
                    <code>GET /system/info</code>
                    <span>System Information</span>
                </div>
                <div class="endpoint">
                    <code>POST /upload</code>
                    <span>Upload Files</span>
                </div>
                <div class="endpoint">
                    <code>GET /files</code>
                    <span>List Files</span>
                </div>
                <div class="endpoint">
                    <code>WS /ws/terminal</code>
                    <span>Terminal WebSocket</span>
                </div>
                
                <a href="/docs" class="btn">📚 View Interactive API Docs</a>
            </div>

            <div class="card">
                <h3>💡 Quick Start</h3>
                <p style="color: #666; line-height: 1.6;">
                    <strong>API Documentation:</strong> Visit <a href="/docs" style="color: #667eea;">/docs</a> for interactive API testing<br>
                    <strong>Upload Files:</strong> POST to /upload with form-data<br>
                    <strong>Terminal Access:</strong> Connect to ws://[host]:5001/ws/terminal<br>
                    <strong>System Stats:</strong> GET /system/info for detailed metrics
                </p>
            </div>
        </div>

        <script>
            // Fetch and display system stats
            async function updateStats() {
                try {
                    const response = await fetch('/system/info');
                    const data = await response.json();
                    
                    document.getElementById('cpu').textContent = data.cpu_percent.toFixed(1) + '%';
                    document.getElementById('memory').textContent = data.memory.percent.toFixed(1) + '%';
                    document.getElementById('disk').textContent = data.disk.percent.toFixed(1) + '%';
                } catch (error) {
                    console.error('Failed to fetch stats:', error);
                }
            }

            // Update stats every 2 seconds
            updateStats();
            setInterval(updateStats, 2000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/system/info")
async def get_system_info():
    """Get system information"""
    try:
        return {
            "hostname": platform.node(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used,
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent,
            },
            "boot_time": psutil.boot_time(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")

# =====================
# File Management
# =====================

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file to the device"""
    try:
        file_path = UPLOAD_FOLDER / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "filename": file.filename,
            "path": str(file_path),
            "size": file_path.stat().st_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/files")
async def list_files(directory: Optional[str] = None):
    """List files in upload directory or specified directory"""
    try:
        target_dir = Path(directory) if directory else UPLOAD_FOLDER
        
        if not target_dir.exists():
            raise HTTPException(status_code=404, detail="Directory not found")
        
        files = []
        for item in target_dir.iterdir():
            stat = item.stat()
            files.append({
                "name": item.name,
                "path": str(item),
                "is_dir": item.is_dir(),
                "size": stat.st_size if item.is_file() else 0,
                "modified": stat.st_mtime,
            })
        
        return {
            "directory": str(target_dir),
            "files": sorted(files, key=lambda x: (not x['is_dir'], x['name']))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/files/download/{filename}")
async def download_file(filename: str, directory: Optional[str] = None):
    """Download a file from the device"""
    try:
        target_dir = Path(directory) if directory else UPLOAD_FOLDER
        file_path = target_dir / filename
        
        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file"""
    try:
        file_path = UPLOAD_FOLDER / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_path.is_dir():
            shutil.rmtree(file_path)
        else:
            file_path.unlink()
        
        return {"success": True, "message": f"Deleted {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# =====================
# Command Execution
# =====================

@app.post("/execute")
async def execute_command(command: dict):
    """Execute a shell command (use with caution!)"""
    try:
        cmd = command.get("command", "")
        if not cmd:
            raise HTTPException(status_code=400, detail="No command provided")
        
        # Security: Whitelist of allowed commands
        allowed_commands = ["ls", "pwd", "whoami", "date", "uptime", "df", "free", "ps"]
        cmd_name = cmd.split()[0]
        
        if cmd_name not in allowed_commands:
            raise HTTPException(
                status_code=403,
                detail=f"Command '{cmd_name}' not allowed. Allowed: {', '.join(allowed_commands)}"
            )
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return {
            "command": cmd,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

# =====================
# WebSocket Terminal
# =====================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/terminal")
async def websocket_terminal(websocket: WebSocket):
    """WebSocket endpoint for terminal emulation"""
    await manager.connect(websocket)
    try:
        await websocket.send_text("Connected to ARC device terminal. Type 'help' for commands.")
        
        while True:
            data = await websocket.receive_text()
            
            # Handle special commands
            if data.strip() == "help":
                help_text = """
Available commands:
- sysinfo: Display system information
- files: List uploaded files  
- clear: Clear terminal
- exit: Close connection
                """
                await manager.send_personal_message(help_text, websocket)
            elif data.strip() == "sysinfo":
                info = await get_system_info()
                await manager.send_personal_message(json.dumps(info, indent=2), websocket)
            elif data.strip() == "files":
                files = await list_files()
                await manager.send_personal_message(json.dumps(files, indent=2), websocket)
            elif data.strip() == "exit":
                await websocket.send_text("Goodbye!")
                break
            else:
                await manager.send_personal_message(f"Echo: {data}", websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/ssh")
async def websocket_ssh(websocket: WebSocket):
    """WebSocket endpoint for SSH connection (for website compatibility)"""
    await manager.connect(websocket)
    try:
        # Send ready signal
        await websocket.send_text("SSH_READY")
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Validate SSH credentials (basic check)
            if message.get('username') and message.get('password'):
                await websocket.send_text("Connection established")
            else:
                await websocket.send_text("ERROR: Invalid credentials")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_text(f"ERROR: {str(e)}")

# =====================
# ARC Specific Endpoints
# =====================

@app.get("/arc/apps")
async def list_arc_apps():
    """List installed ARC applications"""
    try:
        apps_dir = BASE_DIR / "arc" / "apps"
        apps = []
        
        if apps_dir.exists():
            for app_dir in apps_dir.iterdir():
                if app_dir.is_dir() and (app_dir / "main.py").exists():
                    apps.append({
                        "name": app_dir.name,
                        "path": str(app_dir),
                        "has_main": True
                    })
        
        return {"apps": apps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/arc/launch/{app_name}")
async def launch_arc_app(app_name: str):
    """Launch an ARC application"""
    try:
        # This would need proper implementation based on your app launching mechanism
        app_path = BASE_DIR / "arc" / "apps" / app_name / "main.py"
        
        if not app_path.exists():
            raise HTTPException(status_code=404, detail=f"App '{app_name}' not found")
        
        # Launch the app
        venv_python = BASE_DIR / "venv" / "bin" / "python"
        subprocess.Popen(
            [str(venv_python), "-m", f"arc.apps.{app_name}.main"],
            cwd=str(BASE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        return {"success": True, "message": f"Launched {app_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001, log_level="info")

