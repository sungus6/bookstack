# Smart Home
> Exported from BookStack on 2026-05-14
> Slug: smart-home-UD1

---

## Contents

**For Everyone**
- Using the Smart Home
**Operations**
- Home Assistant Operations
- Device Inventory
- Automation Reference
- Smart Home Overview
- Home Assistant
- IoT Network
- Smart Home Troubleshooting

---

## Chapter: For Everyone

### Using the Smart Home

# Using the Smart Home

A guide for everyone on how to use the smart home features.

## The Basics

The smart home runs on **Home Assistant**. It connects and controls smart devices
throughout the house — lights, switches, thermostats, cameras, and more.

## How to Control Things

**Voice (if configured):** Ask your phone assistant or smart speaker.

**Home Assistant app:** Download the Home Assistant app on your phone.
Log in with your credentials (in Sung KeePass DB or ask Dad).

**Web browser:** Go to http://homeassistant.lan:8123 on home Wi-Fi.

**Physical controls:** Everything still works manually — switches, buttons, thermostats.
The smart home is an addition, not a replacement for physical controls.

## Wi-Fi for Smart Devices

Smart home devices (plugs, bulbs, cameras, sensors) should be on the **neuromancer**
Wi-Fi network, NOT wintermute. This keeps them isolated from family computers and phones.

If you're setting up a new smart device:
1. Connect it to **neuromancer** during setup
2. Let Dad or Noah know so it can be added to Home Assistant

## If Something Isn't Working

**A single device:** Try turning it off and on physically. If it's a bulb, try the
physical switch. If it's a plug, unplug and replug.

**Multiple devices or automations:** Home Assistant may be down or restarting.
Check http://homeassistant.lan:8123 — if it doesn't load, wait a few minutes.

**Ask Aulë:** Describe what's not working and Aulë may be able to help diagnose it.

## Automations

Various automations run on schedules or triggers. If an automation seems to be
running unexpectedly or not at all, let Dad or Noah know.

---

## Chapter: Operations

### Home Assistant Operations

# Home Assistant Operations

## Access

| Method | URL |
|---|---|
| Internal | http://homeassistant.lan:8123 |
| External | Via Nabu Casa remote access |
| App | Home Assistant app (iOS/Android) |

Admin credentials in Sung KeePass DB.

## Architecture

Home Assistant runs on dedicated hardware on VLAN10 at 192.168.10.10.
It communicates with IoT devices on VLAN20 via the firewall rules that allow
HA to receive IoT traffic on specific ports (8123, 8009, 8010, 5353).

## Checking HA Status

```bash
# SSH into Home Assistant (if SSH addon is installed)
ssh root@homeassistant.lan

# Check system health in UI
Settings → System → Health
```

## Backups

Home Assistant creates automatic backups. Access them at:
Settings → System → Backups

For offsite backup, download and store on moria at `/volume1/backups/servers/`.

## Common Operations

**Restart Home Assistant (not the host):**
Settings → System → Restart → Restart Home Assistant

**Restart the host:**
Settings → System → Restart → Reboot Host

**Check logs:**
Settings → System → Logs

**Add a new integration:**
Settings → Devices & Services → Add Integration

## IoT VLAN Firewall Rules

Devices on VLAN20 can reach Home Assistant on these ports:
- TCP 8123 (HA web UI and API)
- UDP 8009, 8010, 5353 (casting and discovery)

HA can initiate connections to VLAN20 devices as needed (established/related traffic
is accepted by the firewall).

## Automations

Automations are configured in the HA UI under Settings → Automations & Scenes.
Complex automations may use Node-RED or AppDaemon addons if installed.

---

### Device Inventory

# Device Inventory

## Template — Fill In with Actual Devices

This page tracks all smart home devices. Update when adding or removing devices.

## Zigbee Devices

| Device | Brand/Model | Room | Purpose |
|---|---|---|---|
| Fill in | Fill in | Fill in | Fill in |

## WiFi Devices (VLAN20)

| Device | Brand/Model | IP | Room | Purpose |
|---|---|---|---|---|
| Fill in | Fill in | Fill in | Fill in | Fill in |

## IR Devices (via Broadlink)

| Device | Type | Room | Notes |
|---|---|---|---|
| Fill in | Fill in | Fill in | Fill in |

## Other Devices

| Device | Protocol | Room | Purpose |
|---|---|---|---|
| Fill in | Fill in | Fill in | Fill in |

---

### Automation Reference

# Automation Reference

## Template — Fill In with Actual Automations

This page documents the active automations in Home Assistant.
Update when adding, modifying, or removing automations.

## Lighting Automations

| Name | Trigger | Action | Notes |
|---|---|---|---|
| Fill in | Fill in | Fill in | Fill in |

## Climate Automations

| Name | Trigger | Action | Notes |
|---|---|---|---|
| Fill in | Fill in | Fill in | Fill in |

## Security / Presence Automations

| Name | Trigger | Action | Notes |
|---|---|---|---|
| Fill in | Fill in | Fill in | Fill in |

## Other Automations

| Name | Trigger | Action | Notes |
|---|---|---|---|
| Fill in | Fill in | Fill in | Fill in |

## Notes on Automation Management

Automations are stored in `/config/automations.yaml` on the HA host.
They can be edited via:
- Home Assistant UI: Settings -> Automations
- File Editor add-on (direct YAML edit)
- Node-RED (if installed) for visual flow-based automations

Always test automations after editing. Check the HA log for errors:
Settings -> System -> Logs.


## Chapter: Troubleshooting

---

### Smart Home Overview

# Smart Home Overview

## Purpose

The Arda smart home environment provides centralized control of lights, climate,
security sensors, and other connected devices. All automation logic runs locally
on Home Assistant — no cloud dependency for core functionality.

## Core Principles

- **Local first.** Automations run on the home server, not in the cloud.
  Internet outages do not affect most automations.
- **IoT isolation.** All smart devices are on VLAN20, isolated from trusted
  devices and management. They cannot reach the home network or the internet
  except through controlled rules.
- **Single pane of glass.** Home Assistant is the only interface needed for
  device control and automation management.

## Key Components

| Component | Role |
|---|---|
| Home Assistant | Central automation engine and dashboard |
| Zigbee coordinator | Connects Zigbee sensors and switches |
| WiFi IoT devices | Smart plugs, cameras, etc. on VLAN20 |
| Broadlink | IR blaster for controlling IR devices (TV, AC) |
| Nabu Casa | Remote access to Home Assistant (cloud) |

## Access

| Method | URL |
|---|---|
| Internal | http://homeassistant.lan:8123 |
| External | Via Nabu Casa remote access |


## Chapter: Platform

---

### Home Assistant

# Home Assistant

## Overview

Home Assistant (HA) runs on dedicated hardware on VLAN10 at 192.168.10.10.
It is the central controller for all smart home devices.

| Field | Value |
|---|---|
| OS | Home Assistant OS |
| IP | 192.168.10.10 |
| DNS | homeassistant.lan |
| Web UI | http://homeassistant.lan:8123 |
| External | Via Nabu Casa |

## Key Integrations

| Integration | Purpose | Notes |
|---|---|---|
| Zigbee (ZHA or Z2M) | Zigbee device network | Fill in coordinator type |
| Broadlink | IR remote control | Fill in device model |
| HACS | Community integrations | Community Add-on store |
| Nabu Casa | Remote access | Paid subscription |

## Updating Home Assistant

From the HA web UI: Settings -> System -> Updates.

For manual update via SSH:
```bash
ha core update
```

## Backup and Restore

Home Assistant has built-in backup: Settings -> System -> Backups -> Create Backup.

Backups can be downloaded and stored on Moria at:
`/volume1/backups/servers/homeassistant/`

To restore: upload a backup from Settings -> System -> Backups.

## Configuration Files

Key config files (accessible via File Editor add-on or SSH):
```
/config/
├── configuration.yaml    -- main config
├── automations.yaml      -- automations
├── scripts.yaml          -- scripts
├── scenes.yaml           -- scenes
└── .storage/             -- entity registry, device registry
```

## Useful Add-ons

| Add-on | Purpose |
|---|---|
| File Editor | Edit config files from browser |
| Terminal & SSH | SSH access to HA host |
| Node-RED | Advanced visual automation editor |
| Mosquitto | Local MQTT broker |


## Chapter: Devices

---

### IoT Network

# IoT Network

## Network Details

All smart home devices are isolated on VLAN20.

| Field | Value |
|---|---|
| VLAN | 20 (IoT) |
| Subnet | 192.168.20.0/24 |
| Gateway | 192.168.20.1 |
| DNS | 8.8.8.8 (Google — IoT does not use MikroTik DNS) |
| WiFi SSID | neuromancer |

## What IoT Devices Can Reach

IoT devices on VLAN20 are restricted by MikroTik firewall rules:

| Destination | Access |
|---|---|
| Internet | Allowed |
| Home Assistant (192.168.10.10) | Allowed on ports 8123, 8009, 8010, 5353 |
| VLAN10 trusted devices | Blocked |
| VLAN99 management | Blocked |
| MikroTik admin | Blocked |

## Adding a New IoT Device

1. Connect device to **neuromancer** WiFi (VLAN20) or plug into Zyxel ports 21-23
2. Device will get a 192.168.20.x address from DHCP
3. Add device to Home Assistant via the appropriate integration
4. If device needs a specific firewall rule (e.g. reaches a port not already allowed),
   update MikroTik firewall and document here

## Static DHCP for IoT Devices

For devices that need a predictable IP (e.g. cameras, smart hubs):
1. Note the device MAC address
2. On MikroTik: `/ip dhcp-server lease add address=192.168.20.X mac-address=XX:XX:XX:XX:XX:XX comment="device name"`
3. Document the lease in this page

| IP | MAC | Device |
|---|---|---|
| Fill in | Fill in | Fill in |


## Chapter: Automations

---

### Smart Home Troubleshooting

# Smart Home Troubleshooting

## Home Assistant Not Accessible

**Check if HA is running:**
```bash
ping homeassistant.lan
```

If no response, the HA hardware may need a reboot. Physical access required.

**Check from another VLAN10 device:**
```bash
curl http://192.168.10.10:8123
```

**External access not working:**
Check Nabu Casa subscription status: Settings -> Home Assistant Cloud.

## Device Shows as Unavailable

1. Check device has power
2. Check device is connected to the correct WiFi (neuromancer) or Zigbee
3. Check VLAN20 is working: connect a test device to neuromancer and verify it gets a 192.168.20.x address
4. Restart the relevant integration: Settings -> Devices & Services -> [integration] -> Reload

## Zigbee Device Not Pairing

1. Put device in pairing mode (device-specific — check manual)
2. In HA: Settings -> Devices & Services -> Zigbee -> Add Device
3. Keep device close to the coordinator during pairing
4. If pairing fails, check coordinator is working: Settings -> Devices & Services -> Zigbee -> Coordinator info

## Automation Not Firing

1. Check automation is enabled: Settings -> Automations -> [automation] -> verify toggle is on
2. Check the trigger conditions manually
3. View automation trace: Settings -> Automations -> [automation] -> Traces
4. Check HA log for errors: Settings -> System -> Logs

## IR Commands Not Working (Broadlink)

1. Verify Broadlink device is online: check in HA Devices list
2. Check IR blaster has line of sight to the target device
3. Re-learn the IR code if needed: Settings -> Devices -> Broadlink -> Learn Command

## General HA Errors

View the Home Assistant log:
Settings -> System -> Logs

Filter by level (Warning, Error) to find issues quickly.

For persistent issues, restart Home Assistant:
Settings -> System -> Restart -> Restart Home Assistant.

---
