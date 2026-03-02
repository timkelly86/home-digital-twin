"""
Create areas for Ecobee-discovered rooms and assign all Ecobee devices.
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


def ensure_areas(ws, area_names):
    existing = send_and_receive(ws, {"type": "config/area_registry/list"})
    existing_map = {a["name"].lower(): a["area_id"] for a in existing.get("result", [])}

    for name in area_names:
        if name.lower() in existing_map:
            print(f"  [exists] {name} -> {existing_map[name.lower()]}")
            continue
        resp = send_and_receive(ws, {"type": "config/area_registry/create", "name": name})
        if resp.get("success"):
            area_id = resp["result"]["area_id"]
            existing_map[name.lower()] = area_id
            print(f"  [created] {name} -> {area_id}")
        else:
            print(f"  [error] {name}: {resp.get('error', {}).get('message', 'unknown')}")

    return existing_map


def assign_devices(ws, area_lookup):
    devices_resp = send_and_receive(ws, {"type": "config/device_registry/list"})
    devices = devices_resp.get("result", [])

    rules = {
        "charlie": "charlie's room",
        "zoey": "zoey's room",
        "gym": "gym",
        "downstairs": "downstairs",
        "upstairs": "upstairs",
        "bedroom": "master bedroom",
        "office": "office",
    }

    print("\n--- Assigning Ecobee devices ---")
    for d in devices:
        dev_name = (d.get("name_by_user") or d.get("name") or "").lower()
        dev_id = d.get("id", "")
        current_area = d.get("area_id")
        manufacturer = (d.get("manufacturer") or "").lower()

        if "ecobee" not in manufacturer:
            continue

        if current_area:
            print(f"  [skip] {dev_name} (already in: {current_area})")
            continue

        matched_area = None
        for keyword, area_name in rules.items():
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
            print(f"  [unmatched] {dev_name}")


def main():
    if not HA_TOKEN:
        raise RuntimeError("HA_TOKEN environment variable is required")

    ws = websocket.create_connection(HA_URL)
    try:
        authenticate(ws)

        print("--- Ensuring areas ---")
        new_areas = ["Charlie's Room", "Zoey's Room", "Gym", "Downstairs"]
        area_lookup = ensure_areas(ws, new_areas)

        assign_devices(ws, area_lookup)

    finally:
        ws.close()


if __name__ == "__main__":
    main()
