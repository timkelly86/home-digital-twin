# Task Walkthrough — Home Digital Twin

A single ordered list of what’s done and what to do next. Use this as your main checklist.

---

## Done

- [x] **HA on Pi** — 2026.2.3, OS 17.1, running and stable
- [x] **Areas** — 19 rooms mapped (Upstairs / Downstairs / Master zones + exterior)
- [x] **Ring** — 4 cameras + base station in HA; assigned to areas
- [x] **Ecobee** — 3 thermostats + 4 remote sensors (temp, humidity, AQI, CO2, VOC, occupancy)
- [x] **Sonos** — Living Room speaker
- [x] **Backups** — Daily automatic, keep 5, encrypted; key stored in `.env`
- [x] **Z-Wave** — Zooz 800 LR stick configured in HA (Apps → Z-Wave JS); **no devices paired yet**

---

## Your tasks (in order)

### 1. Add Z-Wave devices (locks, Leviton switches, Ring Retrofit sensors)

**Goal:** Move Kwikset locks, Leviton switches, and Ring Retrofit contact sensors from the Ring hub to the Zooz stick so they appear in HA.

**Steps (per device):**

1. **Exclude from Ring**  
   In the Ring app (or on the Ring Alarm hub), remove the device from the Ring network (exclusion / remove device). Follow Ring’s instructions for that device type.

2. **Include in HA**  
   - In HA: **Settings → Z-Wave** (or **Devices & services → Z-Wave → Configure**).  
   - Click **Add device** (stick goes into inclusion mode).  
   - Put the **device** in inclusion mode (see device manual: button press, keypad sequence, etc.).  
   - Wait for HA to confirm. Assign the new device to the correct **area** when prompted.

3. **Locks only:** When HA asks for a PIN/DSK, use the 5‑digit PIN from the lock or its manual (S2 secure inclusion).

**Order suggestion:** Do one contact sensor first (easiest), then switches, then locks (they often ask for PIN).

**Ref:** [Z-Wave runbook](runbooks/zwave-zooz-800-setup.md#adding-devices-locks-leviton-switches-ring-retrofit-sensors).

---

### 2. Lutron Caseta (lights)

**Goal:** Get Lutron lights into HA so you can control them and add them to dashboards.

**Steps:**

1. **Hardware** — Lutron bridge powered and on the same network as the Pi.
2. **Settings → Devices & services → Add integration** → search **Lutron Caseta**.
3. When prompted, **press the button on the back of the Lutron bridge** (within the time window).
4. HA will discover the bridge and pull in all paired lights. Assign each device to the right **area**.

**Note:** If you have the standard (non‑Pro) bridge, use **HomeKit Controller** instead: add the bridge to the Apple Home app first, then in HA add the **HomeKit Controller** integration and pair the bridge.

---

### 3. Dashboards (Epic G)

**Goal:** One “house cockpit” plus a few focused views.

**Suggested dashboards:**

| Dashboard   | Purpose |
|------------|---------|
| **Overview** | Main view: security (doors/locks), HVAC zones, key lights, “Problems” (offline, low battery). |
| **Security** | Ring cameras, locks, contact sensors, alarm state. |
| **HVAC / Comfort** | Ecobee thermostats and sensors by zone; setpoints. |
| **Pool** | Add when Pentair is integrated (Epic F). |
| **Problems** | Low battery, unavailable devices, Z-Wave failures. |

**Steps:** **Settings → Dashboards → Create dashboard** (or edit the default). Add cards by entity/device/area. Use **Mosaic** or **Grid** layout for a clean cockpit.

---

### 4. MyQ (garage door) — Epic D

**Goal:** Garage door state and “left open” / “night check” type automations.

**Options:**

- **MyQ integration (cloud)** — Add via **Settings → Devices & services → Add integration → MyQ**. Log in with Chamberlain/MyQ account. Easiest but cloud‑dependent.
- **ratgdo (local)** — Small hardware dongle that talks to the opener locally; more reliable long‑term, no cloud. Purchase + install when you’re ready.

**Suggestion:** Start with the MyQ integration to get state and one or two automations; consider ratgdo later if the cloud API is flaky.

---

### 5. Pentair / pool — Epic F

**Goal:** Pump, water temp, heater (if any), and basic alerts (e.g. pump outside schedule, freeze).

**Steps:** When you’re ready: **Add integration → Pentair** (or **ScreenLogic**). You’ll need the ScreenLogic protocol adapter on the pool equipment and its IP. Document the IP and credentials in your secrets (not in git).

---

### 6. Tandem (digital twin) — Phase 2

**Goal:** Mirror key HA data (assets + streams + events) into Autodesk Tandem for history and experiments.

**When:** After the mini‑PC and Tandem Connect Outpost are in place. Use the [device inventory](device-inventory.md) and area/entity list to define Tandem assets and streams; align naming with HA (e.g. `area_device_signal`).

---

## Quick reference

| I want to…                    | Where to go |
|------------------------------|-------------|
| Add a Z-Wave device          | Settings → Z-Wave → Add device |
| Add an integration           | Settings → Devices & services → Add integration |
| Manage apps (e.g. Z-Wave JS) | Settings → Apps |
| Edit areas                  | Settings → Areas, labels & zones |
| Create/edit dashboards      | Settings → Dashboards |
| Back up Z-Wave network      | Settings → Z-Wave → ⋮ → Backup |

---

## Optional / later

- **ESP32 devices** — Get esp-switch-001 and ESP32-button back online (power/network), then they’ll show up again in HA.
- **Ring Retrofit batteries** — Replace batteries in contact sensors so they report reliably before or after moving them to Z-Wave.
- **Naming cleanup** — Align entity names with `domain.area_device_signal` and track renames in git (Epic B).
- **Runbooks** — [Backups](runbooks/) (and others as you add them) for upgrades, restore, and “something broke” triage.
