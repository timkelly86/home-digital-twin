"""
Home Assistant setup script — creates areas, assigns devices,
and performs initial configuration via the WebSocket API.
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
    assert auth_required["type"] == "auth_required", f"Unexpected: {auth_required}"
    ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
    auth_result = json.loads(ws.recv())
    if auth_result["type"] != "auth_ok":
        raise RuntimeError(f"Auth failed: {auth_result}")
    print(f"Authenticated — HA version {auth_result.get('ha_version', 'unknown')}")


def create_areas(ws, area_names):
    print("\n--- Creating Areas ---")
    existing = send_and_receive(ws, {"type": "config/area_registry/list"})
    existing_names = {a["name"].lower() for a in existing.get("result", [])}

    for name in area_names:
        if name.lower() in existing_names:
            print(f"  [skip] {name} (already exists)")
            continue
        resp = send_and_receive(ws, {
            "type": "config/area_registry/create",
            "name": name,
        })
        if resp.get("success"):
            print(f"  [created] {name} -> {resp['result']['area_id']}")
        else:
            print(f"  [error] {name} -> {resp.get('error', {}).get('message', 'unknown')}")


def list_devices(ws):
    print("\n--- Device Registry ---")
    resp = send_and_receive(ws, {"type": "config/device_registry/list"})
    devices = resp.get("result", [])
    for d in devices:
        area = d.get("area_id") or "(no area)"
        name = d.get("name_by_user") or d.get("name") or "(unnamed)"
        dev_id = d.get("id", "")
        print(f"  {name:40s} | area: {area:20s} | id: {dev_id}")
    return devices


def list_entities(ws):
    print("\n--- Entity Registry ---")
    resp = send_and_receive(ws, {"type": "config/entity_registry/list"})
    entities = resp.get("result", [])
    for e in entities:
        area = e.get("area_id") or "(device default)"
        eid = e.get("entity_id", "")
        platform = e.get("platform", "")
        print(f"  {eid:50s} | platform: {platform:15s} | area: {area}")
    return entities


def assign_device_to_area(ws, device_id, area_id):
    resp = send_and_receive(ws, {
        "type": "config/device_registry/update",
        "device_id": device_id,
        "area_id": area_id,
    })
    if resp.get("success"):
        print(f"  [assigned] device {device_id} -> area {area_id}")
    else:
        print(f"  [error] {resp.get('error', {}).get('message', 'unknown')}")


def main():
    if not HA_TOKEN:
        raise RuntimeError("HA_TOKEN environment variable is required")

    ws = websocket.create_connection(HA_URL)
    try:
        authenticate(ws)

        areas_to_create = [
            "Living Room",
            "Master Bedroom",
            "Kitchen",
            "Garage",
            "Front Porch",
            "Backyard / Pool",
            "Upstairs",
            "Hallway",
            "Office",
        ]
        create_areas(ws, areas_to_create)

        devices = list_devices(ws)
        list_entities(ws)

        # Build area lookup
        areas_resp = send_and_receive(ws, {"type": "config/area_registry/list"})
        area_lookup = {a["name"].lower(): a["area_id"] for a in areas_resp.get("result", [])}
        print(f"\n--- Area lookup: {area_lookup} ---")

        # Auto-assign known devices
        for d in devices:
            dev_name = (d.get("name_by_user") or d.get("name") or "").lower()
            dev_id = d.get("id", "")
            current_area = d.get("area_id")

            if current_area:
                continue

            if "living room" in dev_name or "sonos" in dev_name:
                assign_device_to_area(ws, dev_id, area_lookup.get("living room", ""))
            elif "esp32" in dev_name or "esphome" in dev_name:
                assign_device_to_area(ws, dev_id, area_lookup.get("office", ""))

    finally:
        ws.close()


if __name__ == "__main__":
    main()
