"""
Reorganize HA areas to match actual house layout with HVAC zones.

HVAC Zones:
  Upstairs:   Ally's Craft Room, Charlie's Room, Zoey's Room, Playroom, Upstairs Bathrooms
  Downstairs: Kitchen, Living Room, Entry Hall, Laundry, Pantry, Dining Room
  Master:     Master Bedroom, Master Bath, Office, Gym / Guest Room
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


def get_areas(ws):
    resp = send_and_receive(ws, {"type": "config/area_registry/list"})
    return {a["name"].lower(): a for a in resp.get("result", [])}


def create_area(ws, name):
    resp = send_and_receive(ws, {"type": "config/area_registry/create", "name": name})
    if resp.get("success"):
        print(f"  [created] {name} -> {resp['result']['area_id']}")
        return resp["result"]
    else:
        print(f"  [error] {name}: {resp.get('error', {}).get('message', 'unknown')}")
        return None


def delete_area(ws, area_id, name):
    resp = send_and_receive(ws, {"type": "config/area_registry/delete", "area_id": area_id})
    if resp.get("success"):
        print(f"  [deleted] {name} ({area_id})")
    else:
        print(f"  [error deleting] {name}: {resp.get('error', {}).get('message', 'unknown')}")


def reassign_devices_from_area(ws, old_area_id, new_area_id):
    devices_resp = send_and_receive(ws, {"type": "config/device_registry/list"})
    devices = devices_resp.get("result", [])
    for d in devices:
        if d.get("area_id") == old_area_id:
            dev_name = d.get("name_by_user") or d.get("name") or "(unnamed)"
            resp = send_and_receive(ws, {
                "type": "config/device_registry/update",
                "device_id": d["id"],
                "area_id": new_area_id,
            })
            if resp.get("success"):
                print(f"    [moved] {dev_name} -> {new_area_id}")
            else:
                print(f"    [error] {dev_name}: {resp.get('error', {}).get('message', 'unknown')}")


def main():
    if not HA_TOKEN:
        raise RuntimeError("HA_TOKEN environment variable is required")

    ws = websocket.create_connection(HA_URL)
    try:
        authenticate(ws)

        areas = get_areas(ws)
        print(f"\nExisting areas: {list(areas.keys())}\n")

        # --- Create missing areas ---
        print("--- Creating new areas ---")
        new_areas = [
            "Ally's Craft Room",
            "Playroom",
            "Dining Room",
            "Laundry",
            "Pantry",
            "Master Bath",
        ]
        for name in new_areas:
            if name.lower() not in areas:
                result = create_area(ws, name)
                if result:
                    areas[name.lower()] = result
            else:
                print(f"  [exists] {name}")

        # --- Consolidate "Bedroom" into "Master Bedroom" ---
        print("\n--- Consolidating Bedroom -> Master Bedroom ---")
        bedroom = areas.get("bedroom")
        master = areas.get("master bedroom")

        if bedroom and master:
            print(f"  Moving devices from '{bedroom['name']}' ({bedroom['area_id']}) to '{master['name']}' ({master['area_id']})")
            reassign_devices_from_area(ws, bedroom["area_id"], master["area_id"])
            delete_area(ws, bedroom["area_id"], "Bedroom")
        elif bedroom and not master:
            print("  No 'Master Bedroom' area found; renaming 'Bedroom'")
            resp = send_and_receive(ws, {
                "type": "config/area_registry/update",
                "area_id": bedroom["area_id"],
                "name": "Master Bedroom",
            })
            if resp.get("success"):
                print(f"  [renamed] Bedroom -> Master Bedroom")
        else:
            print("  Nothing to consolidate")

        # --- Rename Entry Hall if Hallway exists ---
        print("\n--- Renaming Hallway -> Entry Hall ---")
        hallway = areas.get("hallway")
        if hallway:
            resp = send_and_receive(ws, {
                "type": "config/area_registry/update",
                "area_id": hallway["area_id"],
                "name": "Entry Hall",
            })
            if resp.get("success"):
                print(f"  [renamed] Hallway -> Entry Hall")
            else:
                print(f"  [error] {resp.get('error', {}).get('message', 'unknown')}")

        # --- Final area list ---
        print("\n--- Final area list ---")
        final_areas = get_areas(ws)
        for name, a in sorted(final_areas.items()):
            print(f"  {a['area_id']:25s} | {a['name']}")

    finally:
        ws.close()


if __name__ == "__main__":
    main()
