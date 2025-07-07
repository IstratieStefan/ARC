import asyncio
import websockets
import json
import paramiko

HOST = "0.0.0.0"
PORT = 5000

async def handle_connection(ws):
    ssh = None
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
                    await ws.send(json.dumps({"type": "auth-success"}))
                except paramiko.AuthenticationException:
                    await ws.send(json.dumps({"type": "auth-failure"}))
                    return
                except Exception as e:
                    await ws.send(json.dumps({
                        "type":    "auth-failure",
                        "message": f"Could not reach {ssh_host}:{ssh_port}"
                    }))
                    return

            elif data["type"] == "input":
                if not ssh:
                    await ws.send(json.dumps({
                        "type":    "error",
                        "message": "Not authenticated"
                    }))
                    continue

                chan = ssh.get_transport().open_session()
                chan.exec_command(data["data"])
                out = chan.recv(65535).decode()
                err = chan.recv_stderr(65535).decode()
                await ws.send(json.dumps({
                    "type": "output", "data": out + err
                }))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if ssh:
            ssh.close()

async def main():
    async with websockets.serve(handle_connection, HOST, PORT):
        print(f"ARC WebSocket SSH proxy running on ws://{HOST}:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
