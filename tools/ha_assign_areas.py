"""
Assign Ring camera devices to their correct areas in Home Assistant.
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


def main():
    if not HA_TOKEN:
        raise RuntimeError("HA_TOKEN environment variable is required")

    ws = websocket.create_connection(HA_URL)
    try:
        authenticate(ws)

        areas_resp = send_and_receive(ws, {"type": "config/area_registry/list"})
        area_lookup = {a["name"].lower(): a["area_id"] for a in areas_resp.get("result", [])}
        print(f"\nAreas: {json.dumps(area_lookup, indent=2)}")

        devices_resp = send_and_receive(ws, {"type": "config/device_registry/list"})
        devices = devices_resp.get("result", [])

        assignment_rules = {
            "front door": "front_porch",
            "back door": "backyard / pool",
            "backyard": "backyard / pool",
            "garage": "garage",
            "hallway": "hallway",
        }

        print("\n--- Assigning devices to areas ---")
        for d in devices:
            dev_name = (d.get("name_by_user") or d.get("name") or "").lower()
            dev_id = d.get("id", "")
            current_area = d.get("area_id")
            manufacturer = (d.get("manufacturer") or "").lower()

            if current_area:
                print(f"  [skip] {dev_name} (already in area: {current_area})")
                continue

            matched_area = None
            for keyword, area_name in assignment_rules.items():
                if keyword in dev_name:
                    matched_area = area_lookup.get(area_name)
                    break

            if matched_area:
                resp = send_and_receive(ws, {
                    "type": "config/device_registry/update",
                    "device_id": dev_id,
                    "area_id": matched_area,
                })
                if resp.get("success"):
                    print(f"  [assigned] {dev_name} -> {matched_area}")
                else:
                    print(f"  [error] {dev_name}: {resp.get('error', {}).get('message', 'unknown')}")
            else:
                print(f"  [unmatched] {dev_name} (manufacturer: {manufacturer})")

    finally:
        ws.close()


if __name__ == "__main__":
    main()
