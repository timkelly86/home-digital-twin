# Device Inventory

> Last updated from Home Assistant API: 2026-03-01
> HA Version: 2026.2.3 | HA OS: 17.1 | Host: Raspberry Pi | IP: 192.168.1.74

## Integration status

| Integration | Status | Devices | Notes |
|---|---|---|---|
| **Ring** | Active | 4 cameras + base station | Cameras only; locks/sensors/switches need Z-Wave |
| **Sonos** | Active | 1 speaker (Living Room) | Working |
| **Lutron Caseta** | Pending setup | Light switches (unknown count) | User has bridge; adding via HA UI |
| **Ecobee** | Pending setup | Thermostat(s) | Needs OAuth through HA UI |
| **ESPHome** | Active | 2 devices (ESP32-button, esp-switch-001) | Both currently unavailable/offline |
| **Nabu Casa Cloud** | Active | Remote UI, TTS, STT | Remote access enabled |
| **Met Weather** | Active | Forecast | Default weather |
| **Backup** | Active | Daily automatic, keep 5 | Encryption key stored |

## Devices needing Z-Wave stick

These are currently paired to the Ring Alarm hub and not accessible via the Ring HA integration.
A dedicated Z-Wave USB stick (e.g., Zooz ZST39 or Silicon Labs UZB-7) on the Pi will allow
direct local control.

| Device | Brand | Type | Current Hub | Target |
|---|---|---|---|---|
| Door locks | Kwikset | Z-Wave lock | Ring Alarm | Z-Wave (Pi direct) |
| Light switches | Leviton | Z-Wave switch | Ring Alarm | Z-Wave (Pi direct) |
| Contact sensors | Ring Retrofit kit | Z-Wave sensor | Ring Alarm | Z-Wave (Pi direct) |

## Ring cameras (4) — all active

| Device | Area | Entities |
|---|---|---|
| Front Door (doorbell) | Front Porch | camera, ding event, motion event, battery, volume, motion detection |
| Back door | Backyard / Pool | camera, motion event, siren, battery, volume, motion detection |
| Backyard | Backyard / Pool | camera, motion event, siren, battery, volume, motion detection |
| Garage | Garage | camera, motion event, siren, battery, volume, motion detection |
| Hallway (base station) | Hallway | siren |

## Areas configured

| Area | Assigned Devices |
|---|---|
| Living Room | Sonos speaker |
| Kitchen | (empty — future) |
| Bedroom | (empty — future) |
| Master Bedroom | (empty — Ecobee planned) |
| Garage | Ring Garage camera |
| Front Porch | Ring Front Door doorbell |
| Backyard / Pool | Ring Back door camera, Ring Backyard camera, Pentair (future) |
| Upstairs | (empty — Ecobee sensor planned) |
| Hallway | Ring Alarm base station |
| Office | ESPHome devices (x2) |

## System health

| Component | Version | Status |
|---|---|---|
| HA Core | 2026.2.3 | Current |
| HA OS | 17.1 | Current |
| Supervisor | Current | Current |
| Backups | Daily / keep 5 | Active, encrypted |

## Hardware shopping list

| Item | Purpose | Est. cost | Priority |
|---|---|---|---|
| Z-Wave USB stick (Zooz ZST39 or SiLabs UZB-7) | Local control of locks, Leviton switches, Ring sensors | ~$30 | High |
