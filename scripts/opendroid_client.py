#!/usr/bin/env python3
"""
opendroid_client.py — Hermes → OpenDroid (Galaxy A16) vía MCP del teléfono.

Requisitos: estar en el tailnet, teléfono con OpenDroid fork corriendo,
OPENDROID_MCP_BIND=0.0.0.0 activo y token MCP_ACCESS_TOKEN del build.

Uso:
    python3 opendroid_client.py device_info
    python3 opendroid_client.py list_actions
    python3 opendroid_client.py execute_action open_app '{"target":"whatsapp"}'
    python3 opendroid_client.py terminal_create / terminal_write <id> <cmd>

Protocolo: JSON-RPC 2.0 over HTTP a POST /mcp, header x-opendroid-token.
"""
import json
import sys
import urllib.request

PHONE = "100.104.144.75"          # Galaxy A16 en el tailnet
PORT = 8765
TOKEN_FILE = "/root/.android-build/mcp_token.txt"

def token() -> str:
    try:
        return open(TOKEN_FILE).read().strip()
    except FileNotFoundError:
        sys.exit(f"Token no encontrado en {TOKEN_FILE} — re-build con MCP_ACCESS_TOKEN")

def call(method: str, params: dict | None = None, _id: int = 1) -> dict:
    payload = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params:
        payload["params"] = params
    req = urllib.request.Request(
        f"http://{PHONE}:{PORT}/mcp",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-opendroid-token": token()},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def tools_list() -> dict:
    return call("tools/list")

def run_tool(name: str, arguments: dict) -> dict:
    return call("tools/call", {"name": name, "arguments": arguments})

def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "tools":
        print(json.dumps(tools_list(), indent=2, ensure_ascii=False))
    elif cmd == "device_info":
        print(json.dumps(run_tool("device_info", {}).get("result", {}), indent=2, ensure_ascii=False))
    elif cmd == "list_actions":
        r = run_tool("list_actions", {})
        actions = json.loads(r["result"]["content"][0]["text"])
        for a in sorted(actions["actions"]):
            print(" -", a)
    elif cmd == "execute_action" and len(sys.argv) >= 3:
        action = sys.argv[2]
        params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        r = run_tool("execute_action", {"action": action, "params": params})
        print(json.dumps(r["result"], indent=2, ensure_ascii=False))
    elif cmd == "terminal_create":
        print(json.dumps(run_tool("terminal_create", {}), indent=2, ensure_ascii=False))
    elif cmd == "terminal_write" and len(sys.argv) == 4:
        r = run_tool("terminal_write", {"sessionId": sys.argv[2], "command": sys.argv[3]})
        print(json.dumps(r["result"], indent=2, ensure_ascii=False))
    elif cmd == "terminal_read" and len(sys.argv) == 3:
        r = run_tool("terminal_read", {"sessionId": sys.argv[2]})
        print(json.dumps(r["result"], indent=2, ensure_ascii=False))
    else:
        print(__doc__)

if __name__ == "__main":
    main()