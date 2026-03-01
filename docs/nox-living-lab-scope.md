# Nox Living Lab — Smart Home + Digital Twin Scope (Cursor Project)

> **Tagline:** A practical “living lab” that turns a normal house into a measurable, automatable system — and mirrors it into a **digital twin** (Autodesk Tandem) for monitoring, history, and experiments.

## 1) Why this exists

You’re building two things at once:

1. **A reliable smart home** (comfort, safety, convenience).
2. **A credible digital twin lab** that can:
   - ingest real data (polling + event-based),
   - normalize it,
   - store history,
   - visualize it (Home Assistant dashboards + Tandem),
   - and run repeatable experiments (scenarios, alerts, KPIs, automation strategies).

This repo is the “source of truth” for that system: architecture, conventions, configs, scripts, and a backlog.

---

## 2) North Star goals

### Outcomes (what “done” looks like)
- **Unified device model:** HomeKit / Home Assistant / Tandem share the *same* hierarchy: Areas → Rooms → Devices/Assets → Entities/Streams.
- **Events + timeseries captured:** Key systems generate both:
  - continuous telemetry (temp, runtime, power, battery, etc.)
  - discrete events (door open/close, lock state, alarm triggers, pump state changes)
- **One notification philosophy:** fewer pings, more signal. Alerts are explainable, actionable, and rate-limited.
- **Living lab loops:** you can run “what happened last night?” and “why did the house feel warm?” type investigations with real history.

### Non-goals (for now)
- No “AI magic” that controls the house without guardrails.
- No brittle automations that need weekly babysitting.
- No cloud dependence unless it buys real value (security, latency, resilience).

---

## 3) Current ecosystem and known integrations

### Core platforms
- **Home Assistant** as the real-time event bus + UX.
- **Apple Home / HomeKit** as the family-friendly control surface.
- **Homebridge** (where needed) to bridge ecosystem gaps and expose devices consistently.
- **Autodesk Tandem + Tandem Connect** as the digital twin, with:
  - scheduled polling for timeseries, and
  - HTTP gateway for event pushes.

### Known device domains (initial focus)
- **Security / entry:** Ring alarm kit + contact sensors + (likely) locks/cameras.
- **Garage:** MyQ.
- **HVAC:** Ecobee thermostats (including runtime / active equipment states).
- **Pool:** Pentair EasyTouch via ScreenLogic.

---

## 4) System architecture (target)

### 4.1 Logical data flow
**Devices → Home Assistant → (Normalization layer) → Storage → Dashboards + Digital Twin**

- Devices report state into Home Assistant (native integrations where possible).
- A normalization layer (MQTT + templates or Node-RED) creates stable, human-friendly signals.
- Tandem Connect ingests:
  - **timeseries** (polling): key sensors and metrics
  - **events** (push): state changes and alerts
- Optional long-term time-series storage (InfluxDB/Timescale) for richer analytics.

### 4.2 Why a normalization layer exists
Because device vendors love chaos.
Normalization gives you:
- consistent naming,
- consistent units,
- predictable payload shapes,
- and a clean mapping into Tandem Streams.

---

## 5) Core conventions (these prevent future pain)

### 5.1 Entity naming
**Format:**
`<domain>.<area>_<device>_<signal>`

Examples:
- `sensor.master_bedroom_ecobee_temperature`
- `binary_sensor.garage_door_contact`
- `lock.front_door_lock`

### 5.2 “Area” is sacred
Everything gets an Area in HA, HomeKit, and Tandem.
If you skip this, your future self will file a complaint.

### 5.3 MQTT topic structure (proposal)
```
nox/<site>/<area>/<device>/<signal>
```

Examples:
- `nox/home/garage/myq/door_state`
- `nox/home/hallway/ring/front_door_contact`
- `nox/home/upstairs/ecobee/zone1/temperature`

Include:
- `meta` topics (units, device ids)
- `health` topics (availability, battery, rssi)

---

## 6) Workstreams / Epics

### Epic A — Platform foundation & reliability
**Goal:** HA runs like a boring appliance.

Deliverables:
- Backup + restore plan
- Remote access strategy (secure) + local-first operation
- Update policy (monthly cadence + rollback notes)
- System monitoring (disk, memory, DB size, automation failures)

### Epic B — Inventory + hierarchy cleanup (HomeKit ↔ HA ↔ Tandem)
**Goal:** one consistent model of “what exists” and “where it lives.”

Deliverables:
- Home inventory table (rooms, devices, integrations, IDs, owner system)
- Naming conventions enforced (renames tracked in git)
- Tandem asset hierarchy aligned to HA Areas/Devices

### Epic C — Ring integration (security domain)
**Goal:** door/window contacts + locks + alarm states are reliable, visible, and actionable.

Deliverables:
- Restore Ring Retrofit contact sensors (battery/health)
- Surface:
  - contact open/close
  - battery
  - alarm state
  - lock state (if applicable)
- Event push into Tandem (state changes + notable events)

### Epic D — MyQ integration (garage domain)
**Goal:** garage door is trustworthy and safety-aware.

Deliverables:
- Decide: native vs Homebridge route
- States in HA:
  - door open/closed/unknown
  - last-change timestamp
- Automations:
  - “door left open” (time + presence-aware)
  - “night check” reminder

### Epic E — Ecobee integration (HVAC domain)
**Goal:** comfort + runtime history + efficiency insights.

Deliverables:
- Capture:
  - temperature, humidity, setpoints
  - HVAC mode
  - active equipment / runtime (e.g., compressor, fan)
- Tandem streams + simple derived metrics:
  - daily runtime totals
  - comfort deviation (actual vs setpoint band)

### Epic F — Pentair / pool automation integration
**Goal:** pool becomes observable (and less mysterious).

Deliverables:
- Surface:
  - pump state/schedule
  - water temp (if available)
  - heater state (if available)
- Alerts:
  - pump running outside schedule
  - freeze protection active
- Tandem ingestion for history + correlation with weather/usage

### Epic G — Dashboards & control surfaces
**Goal:** one “house cockpit” and a few targeted panels.

Deliverables:
- HA dashboards:
  - Home overview
  - Security
  - HVAC / comfort
  - Pool
  - “Problems” (low battery, unavailable, abnormal)
- Optional wall tablet / kiosk mode

### Epic H — Living Lab experiments (the fun science part)
**Goal:** instrument → hypothesize → test → learn.

Examples:
- Presence detection strategy bake-off (phone trackers vs Bayesian vs BLE beacons)
- Notification tuning (reduce spam by 70% while catching real issues)
- Comfort optimization experiments (schedule tweaks, humidity control)
- “Operational readiness” drills: simulate a failure and verify observability + response steps

---

## 7) Repo structure (suggested)

```
nox-living-lab/
  README.md
  docs/
    architecture.md
    conventions.md
    device-inventory.md
    tandem-mapping.md
    runbooks/
      backups.md
      upgrades.md
      incident-response.md
  home-assistant/
    packages/              # HA packages (if using)
    dashboards/            # YAML or exported dashboards
    blueprints/            # automation blueprints
    templates/
  integrations/
    mqtt/
      topic-map.yaml
      examples/
    tandem/
      connect/
        pipelines/
        mappings/
      scripts/
  tools/
    export/
    normalize/
    validation/
  data/
    samples/
      events/
      timeseries/
```

---

## 8) Backlog (prioritized next steps)

### “Do this next” (fast wins)
- Build the **device inventory** (even if ugly at first).
- Lock in **naming conventions** and start renaming.
- Define **MQTT topic taxonomy** + payload schema.
- Pick **MyQ integration path** and implement it.
- Fix **Ring Retrofit batteries** and confirm contacts are reporting.

### “Then this”
- Implement Tandem mapping (assets + streams) with a repeatable script/template.
- Add dashboards (Home overview + “Problems”).
- Add event push (door open/close → Tandem Events).

---

## 9) Risks & guardrails

- **Vendor cloud fragility:** Some integrations fail when vendors change APIs.
  - Mitigation: prefer local integrations (Matter, Zigbee, ESPHome) for future expansions.
- **Automation safety:** Garage + locks + alarm actions need explicit safety rules.
- **Identity drift:** device IDs change; keep a mapping file and version it.

---

## 10) Ideas to incorporate later (inspiration list)
These are proven “smart home classics” that tend to pay off:
- Presence detection: multi-signal (Wi‑Fi + GPS + BLE) with confidence scoring
- Adaptive lighting + circadian scenes
- Leak detection + automatic shutoff (if/when you add a valve)
- Energy monitoring (whole-home + major circuits) feeding the Energy dashboard
- A “house health score” (availability %, low battery count, critical sensors online)

---

## 11) Definition of Done (v1)
- Inventory exists and is current.
- Core domains (Ring/MyQ/Ecobee/Pool) are integrated, named, dashboarded.
- Tandem shows:
  - asset hierarchy
  - at least 10 useful streams
  - at least 5 event types
- One runbook exists for:
  - backups/restore
  - upgrades
  - “something broke” triage

---

## Appendix A — Minimal MQTT payload schema (proposal)

**Timeseries payload:**
```json
{
  "ts": "2026-02-28T12:34:56Z",
  "value": 72.4,
  "unit": "F",
  "source": "home_assistant",
  "entity_id": "sensor.master_bedroom_ecobee_temperature"
}
```

**Event payload:**
```json
{
  "ts": "2026-02-28T12:34:56Z",
  "event": "door_opened",
  "area": "garage",
  "device": "myq",
  "details": {
    "previous": "closed",
    "current": "open"
  }
}
```
