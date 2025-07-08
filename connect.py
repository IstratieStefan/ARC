import asyncio
import json
import time

import psutil
import websockets
import paramiko
from aiohttp import web
from pathlib import Path
import os


HOST = '0.0.0.0'
WS_PORT = 5000
HTTP_PORT = 5001
UPLOAD_DIR = Path('/home/pi/uploads')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def collect_metrics():
    vm = psutil.virtual_memory()
    du = psutil.disk_usage('/')
    load1, _, _ = psutil.getloadavg()
    cores = psutil.cpu_count(logical=True)

    # Uptime
    boot = psutil.boot_time()
    uptime_secs = int(time.time() - boot)
    h, rem = divmod(uptime_secs, 3600)
    m, s = divmod(rem, 60)
    uptime = f"{h}h {m}m {s}s"

    # Temperature (if available)
    temps = (psutil.sensors_temperatures().get('coretemp')
             or psutil.sensors_temperatures().get('cpu-thermal')
             or [])
    temp = round(temps[0].current, 1) if temps else None

    return {
        'memory': {
            'total': round(vm.total / 2**30, 2),
            'used':  round((vm.total - vm.available) / 2**30, 2)
        },
        'cpu': {
            'load':  load1,
            'cores': cores
        },
        'disk': {
            'total': round(du.total / 2**30, 2),
            'used':  round(du.used / 2**30, 2)
        },
        'uptime': uptime,
        'temp':   temp
    }


async def metrics(request):
    data = await collect_metrics()
    return web.json_response(data)


async def upload(request):
    reader = await request.multipart()
    field = await reader.next()
    if not field or field.name != 'file':
        return web.Response(text='No file', status=400)
    filepath = UPLOAD_DIR / field.filename
    with open(filepath, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)
    return web.Response(text='File uploaded')


async def list_files(request):
    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return web.json_response(files)


async def download(request):
    name = request.match_info.get('name')
    path = UPLOAD_DIR / name
    if not path.exists() or not path.is_file():
        raise web.HTTPNotFound()
    return web.FileResponse(path)


async def handle_connection(ws, path):
    ssh = None
    chan = None
    reader_task = None

    async def ssh_reader():
        try:
            while True:
                if chan and chan.recv_ready():
                    data = chan.recv(1024).decode(errors='ignore')
                    await ws.send(json.dumps({'type': 'output', 'data': data}))
                else:
                    await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass

    try:
        async for msg in ws:
            data = json.loads(msg)
            t = data.get('type')

            if t == 'auth':
                ssh_host = data.get('host', 'localhost')
                ssh_port = data.get('port', 22)
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    ssh.connect(
                        ssh_host,
                        port=ssh_port,
                        username=data['username'],
                        password=data['password'],
                        timeout=5,
                        look_for_keys=False,
                        allow_agent=False
                    )
                except paramiko.AuthenticationException:
                    await ws.send(json.dumps({'type': 'auth-failure'}))
                    return
                except Exception as e:
                    await ws.send(json.dumps({'type': 'auth-failure',
                                               'message': f'Could not reach {ssh_host}:{ssh_port}'}))
                    return

                chan = ssh.get_transport().open_session()
                chan.get_pty(term='xterm', width=80, height=24)
                chan.invoke_shell()

                await ws.send(json.dumps({'type': 'auth-success'}))
                reader_task = asyncio.create_task(ssh_reader())

            elif t == 'input' and chan and chan.send_ready():
                chan.send(data['data'])

            elif t == 'resize' and chan:
                chan.resize_pty(width=data.get('cols', 80), height=data.get('rows', 24))

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
    # HTTP metrics server
    app = web.Application()
    app.router.add_get('/metrics', metrics)
    app.router.add_post('/upload', upload)
    app.router.add_get('/files', list_files)
    app.router.add_get('/download/{name}', download)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, HTTP_PORT)
    await site.start()
    print(f"API server running on http://{HOST}:{HTTP_PORT}")

    # WebSocket SSH proxy
    ws_server = await websockets.serve(handle_connection, HOST, WS_PORT)
    print(f"SSH WebSocket proxy running on ws://{HOST}:{WS_PORT}")

    # run forever
    await asyncio.Future()

if __name__ == '__main__':
    # Dependencies: aiohttp, psutil, websockets, paramiko
    asyncio.run(main())
