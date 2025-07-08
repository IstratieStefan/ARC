import asyncio
import json
import websockets
import paramiko

#Ports
HOST = "0.0.0.0"
PORT = 5000

async def handle_connection(ws):
    ssh = None
    chan = None
    reader_task = None

    async def ssh_reader():
        # continuously read from the SSH channel and push to WS
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
                # 1) Establish SSH + pty + shell
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
                except Exception as e:
                    await ws.send(json.dumps({
                        "type":    "auth-failure",
                        "message": f"Could not reach {ssh_host}:{ssh_port}"
                    }))
                    return

                # open an interactive shell
                chan = ssh.get_transport().open_session()
                # request a PTY of reasonable default size
                chan.get_pty(term="xterm", width=80, height=24)
                chan.invoke_shell()

                # tell the client we're good
                await ws.send(json.dumps({"type": "auth-success"}))

                # start background reader
                reader_task = asyncio.create_task(ssh_reader())

            elif data["type"] == "input":
                # send keypresses / commands straight into the shell
                if chan and chan.send_ready():
                    chan.send(data["data"])
                else:
                    await ws.send(json.dumps({
                        "type": "error",
                        "message": "Not authenticated or channel closed"
                    }))

            elif data["type"] == "resize":
                # handle terminal resize events
                if chan:
                    cols = data.get("cols", 80)
                    rows = data.get("rows", 24)
                    chan.resize_pty(width=cols, height=rows)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # clean up
        if reader_task:
            reader_task.cancel()
        if chan:
            chan.close()
        if ssh:
            ssh.close()

async def main():
    async with websockets.serve(handle_connection, HOST, PORT):
        print(f"ARC WebSocket SSH proxy running on ws://{HOST}:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
