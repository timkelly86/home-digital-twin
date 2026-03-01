"""
Configure automatic daily backups in Home Assistant via WebSocket API.
"""

import json
import os
import websocket

HA_URL = os.environ.get("HA_URL", "ws://192.168.1.74:8123/api/websocket")
HA_TOKEN = os.environ.get("HA_TOKEN", "")

MSG_ID = 0


def next_id():
    global MSG_ID
    MSG_ID += 1
    return MSG_ID


def send_and_receive(ws, payload):
    payload["id"] = next_id()
    ws.send(json.dumps(payload))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == payload["id"]:
            return resp


def authenticate(ws):
    auth_required = json.loads(ws.recv())
    assert auth_required["type"] == "auth_required"
    ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
    auth_result = json.loads(ws.recv())
    if auth_result["type"] != "auth_ok":
        raise RuntimeError(f"Auth failed: {auth_result}")
    print(f"Authenticated — HA version {auth_result.get('ha_version', 'unknown')}")


def configure_automatic_backups(ws):
    print("\n--- Configuring automatic backups ---")

    resp = send_and_receive(ws, {
        "type": "backup/config/update",
        "create_backup": {
            "agent_ids": ["backup.local"],
            "include_addons": None,
            "include_all_addons": True,
            "include_database": True,
            "include_folders": None,
            "name": None,
            "password": None,
        },
        "retention": {
            "copies": 5,
            "days": None,
        },
        "schedule": {
            "recurrence": "daily",
            "time": None,
        },
    })

    if resp.get("success"):
        print("  [ok] Automatic daily backups configured (keep last 5)")
    else:
        print(f"  [error] {resp.get('error', {}).get('message', json.dumps(resp))}")

    info_resp = send_and_receive(ws, {"type": "backup/config/info"})
    if info_resp.get("success"):
        config = info_resp.get("result", {}).get("config", {})
        print(f"  Schedule: {config.get('schedule', {})}")
        print(f"  Retention: {config.get('retention', {})}")
    else:
        print(f"  Could not verify config: {info_resp}")


def main():
    if not HA_TOKEN:
        raise RuntimeError("HA_TOKEN environment variable is required")

    ws = websocket.create_connection(HA_URL)
    try:
        authenticate(ws)
        configure_automatic_backups(ws)
    finally:
        ws.close()


if __name__ == "__main__":
    main()
