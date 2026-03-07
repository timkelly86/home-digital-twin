# Device Inventory

> Last updated from Home Assistant API: 2026-03-02
> HA Version: 2026.2.3 | HA OS: 17.1 | Host: Raspberry Pi | IP: 192.168.1.74
> Total entities: 98

---

## HVAC Zones & Room Layout

### Upstairs Zone (Ecobee "Upstairs" thermostat)

| Room | Sensors | Notes |
|---|---|---|
| Upstairs (landing/common) | Thermostat: 71.7°F, 55% humidity, occupancy | Ecobee thermostat |
| Ally's Craft Room | — | No sensor yet |
| Charlie's Room | 73.1°F, occupancy | Ecobee remote sensor |
| Zoey's Room | 71.1°F, occupancy | Ecobee remote sensor |
| Playroom | — | No sensor yet |

### Downstairs Zone (Ecobee "Downstairs" thermostat)

| Room | Sensors | Notes |
|---|---|---|
| Living Room | Thermostat: 72.8°F, 52% humidity, AQI 81, CO2 814ppm, VOC 1021 | Ecobee thermostat + Sonos speaker |
| Kitchen | — | No sensor yet |
| Entry Hall | Ring Alarm base station (siren) | Renamed from Hallway |
| Dining Room | — | No sensor yet |
| Laundry | — | No sensor yet |
| Pantry | — | No sensor yet |

### Master Zone (Ecobee "Bedroom" thermostat)

| Room | Sensors | Notes |
|---|---|---|
| Master Bedroom | Thermostat: 69.9°F, 63% humidity, AQI 98, CO2 981ppm, VOC 1489 | Ecobee thermostat |
| Master Bath | — | No sensor yet |
| Office | 70.9°F, occupancy | Ecobee remote sensor + ESP32 devices |
| Gym / Guest Room | 70.2°F, occupancy | Ecobee remote sensor |

### Outdoor / Exterior

| Area | Devices | Notes |
|---|---|---|
| Front Porch | Ring Video Doorbell (camera, ding, motion, battery) | |
| Garage | Ring camera (camera, motion, siren, battery 100%) | |
| Backyard / Pool | Ring Back door camera + Ring Backyard camera | Pentair pool planned |

---

## Integration Status

| Integration | Status | Entity Count | Notes |
|---|---|---|---|
| **Ring** | Active | ~25 | 4 cameras + base station (siren, volume). Locks/sensors need Z-Wave |
| **Ecobee** | Active | ~30 | 3 thermostats, 4 remote sensors. Temp, humidity, AQI, CO2, VOC, occupancy |
| **Sonos** | Active | ~7 | Living Room speaker |
| **ESPHome** | Active (offline) | ~3 | ESP32-button + esp-switch-001, both unavailable |
| **Nabu Casa Cloud** | Active | ~3 | Remote UI, TTS, STT |
| **Met Weather** | Active | ~1 | Forecast |
| **Backup** | Active | ~5 | Daily automatic, keep 5, encrypted |

---

## Ecobee Sensor Detail

### Thermostats (with built-in sensors)

| Thermostat | Zone | Temp | Humidity | AQI | CO2 (ppm) | VOC (ppb) | Mode |
|---|---|---|---|---|---|---|---|
| Bedroom | Master | 69.9°F | 63% | 98 | 981 | 1489 | cool |
| Downstairs | Downstairs | 72.8°F | 52% | 81 | 814 | 1021 | heat_cool |
| Upstairs | Upstairs | 71.7°F | 55% | — | — | — | cool |

### Remote Sensors (temperature + occupancy only)

| Sensor | Room | Temp | Occupancy |
|---|---|---|---|
| Charlie's Room Sensor | Charlie's Room | 73.1°F | off |
| Zoey's Room Sensor | Zoey's Room | 71.1°F | off |
| Gym | Gym / Guest Room | 70.2°F | on |
| Office | Office | 70.9°F | on |

---

## Ring Device Detail

| Device | Area | Camera | Motion | Siren | Battery | Other |
|---|---|---|---|---|---|---|
| Front Door (doorbell) | Front Porch | live view | motion event | — | sensor | ding event, volume |
| Back door | Backyard / Pool | live view | motion event | siren | sensor | volume |
| Backyard | Backyard / Pool | live view | motion event | siren | sensor | volume |
| Garage | Garage | live view | motion event | siren | 100% | volume |
| Hallway (base station) | Entry Hall | — | — | siren | — | volume |

---

## Areas (19 total)

| Area ID | Area Name | HVAC Zone | Assigned Devices |
|---|---|---|---|
| ally_s_craft_room | Ally's Craft Room | Upstairs | — |
| backyard_pool | Backyard / Pool | Exterior | Ring Back door, Ring Backyard |
| charlie_s_room | Charlie's Room | Upstairs | Ecobee sensor |
| dining_room | Dining Room | Downstairs | — |
| downstairs | Downstairs | Downstairs | — |
| hallway | Entry Hall | Downstairs | Ring Alarm base station |
| front_porch | Front Porch | Exterior | Ring Doorbell |
| garage | Garage | Exterior | Ring camera |
| gym | Gym / Guest Room | Master | Ecobee sensor |
| kitchen | Kitchen | Downstairs | — |
| laundry | Laundry | Downstairs | — |
| living_room | Living Room | Downstairs | Sonos, Ecobee Downstairs thermostat |
| master_bath | Master Bath | Master | — |
| master_bedroom | Master Bedroom | Master | Ecobee Bedroom thermostat |
| office | Office | Master | Ecobee sensor, ESP32 devices (x2) |
| pantry | Pantry | Downstairs | — |
| playroom | Playroom | Upstairs | — |
| upstairs | Upstairs | Upstairs | Ecobee Upstairs thermostat |
| zoey_s_room | Zoey's Room | Upstairs | Ecobee sensor |

---

## Devices Needing Z-Wave Stick

| Device | Brand | Type | Current Hub | Target |
|---|---|---|---|---|
| Door locks | Kwikset | Z-Wave lock | Ring Alarm | Z-Wave (Pi direct) |
| Light switches | Leviton | Z-Wave switch | Ring Alarm | Z-Wave (Pi direct) |
| Contact sensors | Ring Retrofit kit | Z-Wave sensor | Ring Alarm | Z-Wave (Pi direct) |

---

## Pending Integrations

| Integration | Status | Blocked On |
|---|---|---|
| **Lutron Caseta** | Pending | Hardware setup (bridge pairing) |
| **Z-Wave JS** | In progress | Zooz 800 LR S2 stick plugged into Pi — see [runbook](runbooks/zwave-zooz-800-setup.md) |
| **Pentair ScreenLogic** | Future | Pool season / Epic F |
| **MyQ** | Future | Evaluate ratgdo vs cloud API |
| **MQTT (Mosquitto)** | Future | Normalization layer (Phase 2) |
| **InfluxDB** | Future | Long-term history (Phase 2) |

---

## Hardware

| Item | Status | Notes |
|---|---|---|
| Zooz 800 Series Z-Wave Long Range S2 stick | **Acquired, plugged into Pi** | Setup via HA UI — [runbook](runbooks/zwave-zooz-800-setup.md). Use USB 2.0 extension (3–6 ft) if possible. |

---

## System Health

| Component | Version | Status |
|---|---|---|
| HA Core | 2026.2.3 | Current |
| HA OS | 17.1 | Current |
| Supervisor | Current | Up to date |
| Backups | Daily / keep 5 | Active, encrypted |
| Next backup | 2026-03-03 ~11:05 AM | Scheduled |
