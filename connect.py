import asyncio
import json
import time

import psutil
import websockets
import paramiko

HOST = "0.0.0.0"
PORT = 5000

async def collect_metrics():
    vm = psutil.virtual_memory()
    du = psutil.disk_usage("/")
    load1, _, _ = psutil.getloadavg()
    cores = psutil.cpu_count(logical=True)

    # Uptime
    boot = psutil.boot_time()
    secs = int(time.time() - boot)
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    uptime = f"{h}h {m}m {s}s"

    # Temperature (if available)
    temps = psutil.sensors_temperatures().get("coretemp") \
            or psutil.sensors_temperatures().get("cpu-thermal") or []
    temp = round(temps[0].current, 1) if temps else None

    return {
        "memory": { "total": round(vm.total / 2**30, 2), "used": round((vm.total - vm.available) / 2**30, 2) },
        "cpu":    { "load": load1, "cores": cores },
        "disk":   { "total": round(du.total / 2**30, 2),  "used": round(du.used / 2**30, 2) },
        "uptime": uptime,
        "temp":   temp
    }

async def process_request(path, request_headers):
    if path == "/metrics":
        data = await collect_metrics()
        body = json.dumps(data).encode()
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(body))),
        ]
        return 200, headers, body

    # otherwise, proceed with WebSocket handshake
    return None

async def handle_connection(ws, path):
    ssh = None
    chan = None
    reader_task = None

    async def ssh_reader():
        try:
            while True:
                if chan.recv_ready():
                    data = chan.recv(1024).decode(errors='ignore')
                    await ws.send(json.dumps({"type": "output", "data": data}))
                else:
                    await asyncio.sleep(0.01)
        except Exception:
            pass

    try:
        async for msg in ws:
            data = json.loads(msg)

            if data["type"] == "auth":
                ssh_host = data.get("host", "localhost")
                ssh_port = data.get("port", 22)
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect(
                        ssh_host,
                        port=ssh_port,
                        username=data["username"],
                        password=data["password"],
                        timeout=5,
                        look_for_keys=False,
                        allow_agent=False
                    )
                except paramiko.AuthenticationException:
                    await ws.send(json.dumps({"type": "auth-failure"}))
                    return
                except Exception:
                    await ws.send(json.dumps({
                        "type":    "auth-failure",
                        "message": f"Could not reach {ssh_host}:{ssh_port}"
                    }))
                    return

                chan = ssh.get_transport().open_session()
                chan.get_pty(term="xterm", width=80, height=24)
                chan.invoke_shell()

                await ws.send(json.dumps({"type": "auth-success"}))
                reader_task = asyncio.create_task(ssh_reader())

            elif data["type"] == "input":
                if chan and chan.send_ready():
                    chan.send(data["data"])
                else:
                    await ws.send(json.dumps({
                        "type":    "error",
                        "message": "Not authenticated or channel closed"
                    }))

            elif data["type"] == "resize" and chan:
                chan.resize_pty(width=data.get("cols", 80),
                                height=data.get("rows", 24))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if reader_task:
            reader_task.cancel()
        if chan:
            chan.close()
        if ssh:
            ssh.close()

async def main():
    await websockets.serve(
        handle_connection,
        HOST,
        PORT,
        process_request=process_request
    )
    print(f"Server listening on ws://{HOST}:{PORT} (and HTTP /metrics)")
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())