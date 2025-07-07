import asyncio, json, websockets, paramiko, os, shutil

HOST, PORT = "0.0.0.0", 5000

def get_metrics():
    # Memory usage from /proc/meminfo
    meminfo = {}
    with open('/proc/meminfo') as f:
        for line in f:
            key, val = line.split(':')
            meminfo[key] = int(val.strip().split()[0])  # kB
    total_kb = meminfo.get('MemTotal', 0)
    free_kb = meminfo.get('MemFree', 0) + meminfo.get('Buffers', 0) + meminfo.get('Cached', 0)
    used_kb = total_kb - free_kb
    memory = {"used": round(used_kb / 1024**2, 2), "total": round(total_kb / 1024**2, 2)}

    # Disk usage
    du = shutil.disk_usage('/')
    disk = {"used": round(du.used / 1024**3, 2), "total": round(du.total / 1024**3, 2)}

    # CPU load (1 minute avg) and core count
    load1, _, _ = os.getloadavg()
    cpu = {"load": round(load1, 2), "cores": os.cpu_count() or 1}

    # Uptime
    with open('/proc/uptime') as f:
        secs = float(f.read().split()[0])
    days = int(secs // 86400)
    hours = int((secs % 86400) // 3600)
    mins = int((secs % 3600) // 60)
    uptime = f"{days} days, {hours}:{mins:02d}"

    # CPU temperature (if available)
    temp_val = None
    try:
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            temp_val = round(int(f.read()) / 1000, 1)
    except:
        pass

    return {"memory": memory, "disk": disk, "cpu": cpu, "uptime": uptime, "temp": temp_val}

async def process_request(path, request_headers):
    # HTTP endpoint for metrics
    if path == '/metrics':
        metrics = get_metrics()
        body = json.dumps(metrics).encode()
        return 200, [("Content-Type", "application/json")], body
    # proceed with WebSocket upgrade otherwise
    return None

async def handle_connection(ws):
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
        except:
            pass

    try:
        async for msg in ws:
            data = json.loads(msg)

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
                    await ws.send(json.dumps({"type": "auth-failure"}))
                    return
                except Exception as e:
                    await ws.send(json.dumps({
                        "type": "auth-failure",
                        "message": f"Could not reach {data['host']}:{data['port']}"
                    }))
                    return

                chan = ssh.get_transport().open_session()
                chan.get_pty(term="xterm", width=80, height=24)
                chan.invoke_shell()
                await ws.send(json.dumps({"type": "auth-success"}))
                reader_task = asyncio.create_task(ssh_reader())

            elif data.get("type") == "input":
                if chan and chan.send_ready():
                    chan.send(data["data"])

            elif data.get("type") == "resize":
                if chan:
                    chan.resize_pty(width=data.get("cols", 80), height=data.get("rows", 24))

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
    async with websockets.serve(
        handle_connection,
        HOST,
        PORT,
        process_request=process_request
    ):
        print(f"Server running on ws://{HOST}:{PORT} (and HTTP GET on /metrics)")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())