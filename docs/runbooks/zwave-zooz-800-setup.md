# Z-Wave Setup: Zooz 800 Series Long Range S2 Stick

> **Hardware:** Zooz ZST39 800 Series Z-Wave Long Range S2 USB stick  
> **Host:** Raspberry Pi running Home Assistant OS  
> **Integration:** Z-Wave JS (native in HA 2026.x)

---

## Before you start

**Zooz best practices (reduces RF issues):**

- Use a **3–6 ft USB 2.0 extension cable** between the Pi and the stick (avoid plugging the stick directly into the Pi).
- Prefer a **USB 2.0 port** if your Pi has both; USB 3.0 can cause RF noise.
- Place the stick in a **central location** at desk/shelf height, away from metal racks and Wi‑Fi routers (3–6 ft separation).

---

## Option A: Automatic setup (stick already plugged in)

1. Open **Home Assistant** in your browser: `http://192.168.1.74:8123` (or your Pi’s IP).
2. If HA detected the stick, you should see a **notification** or a **dialog** about a new device (e.g. “Z-Wave controller” or “Silicon Labs”).
3. Choose **“Configure”** or **“Recommended installation”**.
4. HA will:
   - Install the **Z-Wave JS** app (add-on) if needed.
   - Pair the integration with the stick.
5. When asked for **network security keys**:
   - **First-time setup:** leave all fields empty and click **Submit**. HA will generate S0/S2 keys. **Copy and store them somewhere safe** (e.g. password manager or the repo’s encrypted backup); you need them if you ever move the stick or restore.
   - **Restoring an existing network:** enter your existing **S0 Legacy key** (16 hex bytes). S2 keys can be regenerated if you don’t have them.
6. Assign the controller device to an **area** (e.g. **Office** or **Entry Hall** where the Pi lives), then **Finish**.

You’re done. Go to **Settings → Z-Wave** to add devices.

---

## Option B: Manual setup (no prompt or stick not detected)

### Step 1: Confirm the stick is visible to the Pi

On the Pi (SSH or console), or from **Settings → System → Hardware** in HA:

- Look for a USB serial device, e.g.:
  - `ttyUSB0`, or
  - `ttyACM0`, or
  - Something under **Serial** (e.g. by path or by-id).

If nothing appears, try:

- A different USB port (prefer USB 2.0).
- The 3–6 ft USB 2.0 extension cable.
- Rebooting the Pi with the stick plugged in.

### Step 2: Install the Z-Wave JS app (add-on)

1. Go to **Settings → Add-ons → Add-on store**.
2. Search for **“Z-Wave JS”** (or **“Z-Wave”**).
3. Install **“Z-Wave JS”** (the official add-on that runs the Z-Wave JS server).
4. Before starting, open **Configuration** and set:
   - **Serial port:**  
     - Often `/dev/ttyUSB0` or `/dev/ttyACM0`, or  
     - A persistent path like `/dev/serial/by-id/usb-Silicon_Labs_...` (exact path from Step 1).
   - Leave other options at defaults unless you have a reason to change them.
5. **Save**, then **Start** the add-on.
6. Optionally turn **“Start on boot”** (and similar) **On**.

### Step 3: Add the Z-Wave integration

1. Go to **Settings → Devices & services**.
2. Click **Add integration**.
3. Search for **“Z-Wave”** or **“Z-Wave JS”**.
4. Select it. The wizard should offer to **use the Z-Wave JS server** (your add-on).
5. Confirm; it will connect to the add-on (e.g. `ws://localhost:3000` or the port shown in the add-on).
6. If prompted for **network security keys**, follow the same rules as in Option A (empty for first time, or S0 key when restoring).
7. Assign the controller to an area and finish.

You should now see **Settings → Z-Wave** and the controller in **Devices & services**.

---

## Adding devices (locks, Leviton switches, Ring Retrofit sensors)

Your Kwikset locks, Leviton switches, and Ring Retrofit contact sensors are currently on the **Ring hub**. To use them with the Zooz stick you must:

1. **Exclude** each device from the Ring hub (Ring app or hub: put device in “exclusion” / “remove” mode, then run exclusion on the hub).
2. **Include** each device in the new Z-Wave network (HA + Zooz stick).

**In Home Assistant:**

1. Go to **Settings → Z-Wave** (or **Devices & services → Z-Wave → Configure**).
2. Click **Add device** (or **Add a new device**). The stick enters inclusion mode.
3. Put the **device** in inclusion mode (see device manual: often a button press or sequence; locks may use a keypad sequence).
4. Wait for HA to confirm the device was added. Entities can take a few seconds to a few minutes to appear; battery devices may need a wake-up (button press).
5. Assign the new device to the correct **area** (e.g. Front Porch for front door lock, Living Room for a switch).

**SmartStart (if supported):** If the device has a SmartStart QR code, you can scan it in the Z-Wave screen first, then power the device; it will join when it wakes.

**Secure inclusion (S2):** For locks, HA will often ask for the device’s **DSK** or **PIN** (on the device or in the manual). Enter it when prompted so the lock is added with S2 security.

---

## After setup: what to do in this repo

- Update **`docs/device-inventory.md`**: set Z-Wave (Zooz 800) to **Active**, list each lock/switch/sensor and its area.
- Back up the Z-Wave network: **Settings → Z-Wave → … menu → Backup**. Store the backup file somewhere safe (e.g. same place as your HA backups).

---

## Troubleshooting

| Issue | What to try |
|-------|-------------|
| No “new device” prompt | Use Option B: install Z-Wave JS add-on, set serial port, then add Z-Wave integration. |
| Stick not in Hardware list | Use USB 2.0 port + extension cable; reboot Pi; try another USB port. |
| “Cannot open serial port” | Confirm the path in the add-on config (e.g. `/dev/ttyUSB0`). No other add-on or integration should use the same port. |
| Device doesn’t join | Put device in exclusion mode first, run “Remove” in HA, then try inclusion again. Or factory-reset the device per its manual. |
| Locks ask for PIN | Use the 5-digit PIN from the device or manual (S2 secure inclusion). |

**Official references:**

- [Z-Wave JS integration](https://www.home-assistant.io/integrations/zwave_js/)
- [Zooz ZST39 support](https://www.support.getzooz.com/kb/section/384/)
