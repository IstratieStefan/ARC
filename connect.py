import asyncio
import json
import paramiko
import os
import shutil
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import uvicorn

HOST = "0.0.0.0"
WS_PORT = 5000
HTTP_PORT = 5001

def get_metrics():
    # Memory (GB)
    meminfo = {}
    with open('/proc/meminfo') as f:
        for line in f:
            k, v = line.split(':')
            meminfo[k] = int(v.split()[0])  # kB
    total = meminfo['MemTotal'] / 1024**2
    free  = (meminfo['MemFree'] + meminfo['Buffers'] + meminfo['Cached']) / 1024**2
    used  = total - free

    # Disk (GB)
    du = shutil.disk_usage('/')
    disk = {"used": du.used / 1024**3, "total": du.total / 1024**3}

    # CPU load & cores
    load1, _, _ = os.getloadavg()
    cpu = {"load": load1, "cores": os.cpu_count() or 1}

    # Uptime
    with open('/proc/uptime') as f:
        secs = float(f.read().split()[0])
    days = int(secs // 86400)
    hrs  = int((secs % 86400) // 3600)
    mins = int((secs % 3600) // 60)
    uptime = f"{days}d {hrs}h {mins}m"

    # Temperature (°C)
    temp = None
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            temp = int(f.read()) / 1000
    except:
        pass

    return {
        "memory": {"used": round(used,2), "total": round(total,2)},
        "disk":   {"used": round(disk["used"],2), "total": round(disk["total"],2)},
        "cpu":    {"load": round(cpu["load"],2), "cores": cpu["cores"]},
        "uptime": uptime,
        "temp":   round(temp,1) if temp is not None else None
    }

app = FastAPI()

@app.get("/metrics")
async def metrics():
    return JSONResponse(get_metrics())

# 3) WebSocket SSH proxy
async def ws_handler(ws: WebSocket):
    await ws.accept()
    ssh = None
    chan = None
    reader = None

    async def ssh_reader():
        try:
            while True:
                if chan.recv_ready():
                    out = chan.recv(1024).decode(errors='ignore')
                    await ws.send_text(json.dumps({"type":"output","data":out}))
                else:
                    await asyncio.sleep(0.01)
        except:
            pass

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)

            if data.get("type") == "auth":
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect(
                        data["host"], port=data["port"],
                        username=data["username"], password=data["password"],
                        look_for_keys=False, allow_agent=False
                    )
                except paramiko.AuthenticationException:
                    await ws.send_text(json.dumps({"type":"auth-failure"}))
                    return
                chan = ssh.get_transport().open_session()
                chan.get_pty(term="xterm", width=80, height=24)
                chan.invoke_shell()
                await ws.send_text(json.dumps({"type":"auth-success"}))
                reader = asyncio.create_task(ssh_reader())

            elif data.get("type") == "input" and chan:
                chan.send(data["data"])

            elif data.get("type") == "resize" and chan:
                chan.resize_pty(width=data["cols"], height=data["rows"])

    except:
        pass
    finally:
        if reader: reader.cancel()
        if chan:    chan.close()
        if ssh:     ssh.close()

app.websocket("/ws")(ws_handler)

async def main():
    # Start WebSocket + HTTP in one loop
    config = uvicorn.Config(app, host=HOST, port=HTTP_PORT, log_level="info")
    server = uvicorn.Server(config)

    ws_server = websockets.serve(    # raw WebSockets on 5000
        lambda ws, path: ws_handler(ws),
        HOST, WS_PORT
    )
    await asyncio.gather(
        server.serve(),  # HTTP /metrics + WebSocket at /ws on HTTP_PORT
        ws_server
    )

if __name__ == "__main__":
    asyncio.run(main())