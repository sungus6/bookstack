# Smart Home
> Slug: smart-home

---

## Contents

- For Everyone — Using the Smart Home
- For Techies — Architecture & Integrations
- Operations — Maintenance, Troubleshooting, Configuration

---

### For Everyone — Using the Smart Home

The smart home runs on **Home Assistant**. It connects and controls devices throughout the house — lights, switches, thermostats, sensors, and more.

#### How to Control Things

**Ask Aulë:** The easiest way. Any family member can message Aulë on Telegram or Discord and say things like:
- "Turn off the living room lights"
- "Set the thermostat to 72"
- "Lock the front door" (if configured)
- "What's the temperature in the kitchen?"

**Home Assistant app:** Download "Home Assistant" from your phone's app store. Log in with your own account. Credentials are in the Sung KeePass DB.

**Web browser:** Go to http://homeassistant.lan:8123 while on wintermute Wi-Fi.

**Physical controls:** Everything still works the old-fashioned way. Wall switches, thermostat buttons, pull chains — none of those are affected. The smart home is an addition, not a replacement.

#### What You Can Do

- **Lights** — turn on/off, dim, change color (if supported)
- **Thermostat** — set temperature, switch between heat/cool/auto
- **Sensors** — check temperature, humidity, motion, door/window status
- **Automations** — things happen automatically (lights on at sunset, etc.)

Most things just work. If something behaves unexpectedly, ask Aulë.

#### If Something's Not Working

1. **Check the physical control** — does the light switch still work? If yes, it's a smart home issue, not a power issue.
2. **Ask Aulë** — describe what's not working
3. **Check Home Assistant directly** — http://homeassistant.lan:8123
4. **Home Assistant offline?** — Let Dan or Noah know

---

### For Techies — Architecture & Integrations

#### Hardware

| Field | Value |
|-------|-------|
| **Platform** | Home Assistant OS |
| **IP** | 192.168.10.10 |
| **Web UI** | http://homeassistant.lan:8123 |
| **VLAN** | 10 (trusted) — communicates with IoT devices on VLAN20 |

#### Integrations

| Integration | Devices | Notes |
|-------------|---------|-------|
| **Z-Wave** | Various | S2 USB stick controller on HA host |
| **Zigbee** | Various | USB coordinator on HA host |
| **Ecobee** | Ecobee thermostat | Connected via cloud integration |
| **SmartThings** | Various | Legacy integration, some sensors |
| **Local Tuya** | Tuya devices | Local API where supported |
| **Home Connect Alt** | Bosch/Siemens appliances | Washer, dryer, dishwasher |

All device details (make, model, firmware) and their integration setup steps are documented in the Home Assistant system itself under Settings → Devices & Services.

#### Network Configuration

Home Assistant is on VLAN10 (trusted). It communicates with IoT devices on VLAN20 through the firewall:
- TCP 8123 (HA web UI) — allowed from VLAN20
- UDP 8009, 8010 — allowed from VLAN20 (Z-Wave/Zigbee)
- UDP 5353 — allowed from VLAN20 (mDNS discovery)

This means IoT devices can reach Home Assistant, but cannot reach any other VLAN10 machine.

#### Users

| Username | Role | Device |
|----------|------|--------|
| aule | Administrator | Administration — password in KeePass DB |
| kiosk | Kiosk | Dashboard tablet |

#### Voice

Alexa is not currently integrated. Two Echo Dots exist in the house but are used as dumb speakers only, with Alexa disabled.

#### Nabu Casa

Home Assistant Cloud (Nabu Casa) provides external remote access. This is the simplest way for family members to reach the smart home from outside the house.

| Field | Value |
|-------|-------|
| **URL** | Via Nabu Casa remote access |
| **Monthly fee** | ~$7/month, auto-paid through Chase checking |
| **Account** | Sung KeePass DB |

---

### Device Inventory

A complete inventory of all smart home devices, organized by category, with integration and maintenance notes.

#### Lights

| Name | Entity ID | Integration | Protocol | Location | Notes |
|------|-----------|-------------|----------|----------|-------|
| Red Series Dimmer | `light.red_series_dimmer` | Z-Wave | Z-Wave | — | Inovelli Red Series dimmer switch. Brightness 0-255. If unresponsive: reset Z-Wave stick or re-pair device. |
| Hallway Table Lamp | `light.light_sengled_1_light` | Z-Wave | Z-Wave | Hallway | Sengled bulb. Brightness 0-255. If unresponsive: check Z-Wave network health. |
| Family Room Lamp Stand | `light.light_tuya_1` | Local Tuya | Wi-Fi (neuromancer) | Family Room | Color temp + HS color. Currently unavailable — check Tuya account credentials in HA and device Wi-Fi. |
| Living Room Lamp Gear | `light.light_tuya_3` | Local Tuya | Wi-Fi (neuromancer) | Living Room | Unavailable — same troubleshooting as other Tuya devices. |
| Family Room Table Lamp | `light.light_tuya_7` | Local Tuya | Wi-Fi (neuromancer) | Family Room | Unavailable. |
| Light (TUYA) 2 | `light.light_tuya_2` | Local Tuya | Wi-Fi (neuromancer) | — | Unavailable. |
| Light (Tuya) 6 | `light.light_tuya_6` | Local Tuya | Wi-Fi (neuromancer) | — | Unavailable. |
| RGBICW Floor Lamp | `light.rgbicw_floor_lamp_basi` | Local Tuya | Wi-Fi (neuromancer) | — | RGBICW color. Unavailable. |
| Blueair 7400 LED | `light.blueair_7400_led_light` | Blueair | Wi-Fi | Office | Air purifier light. On/off only. |
| DustMagnet LED | `light.blueair_dustmagnet_led_light` | Blueair | Wi-Fi | — | Air purifier light. Unavailable. |
| Ceiling Lights (3) | `light.ceiling_light_*_light` | Z-Wave | Z-Wave | — | Center/right/left. Unavailable — check Z-Wave stick. |

**Tuya troubleshooting:** If Local Tuya devices show `unavailable`, check the Tuya IoT Platform account credentials and local key. Re-authenticate in HA: Settings → Devices & Services → Local Tuya. Ensure device is on neuromancer Wi-Fi (VLAN20) and online in the Smart Life app.

**Z-Wave troubleshooting:** If Z-Wave devices show `unavailable`, check the S2 USB Stick Controller status sensor (`sensor.s2_usb_stick_controller_status`). If not `ready`, restart the Z-Wave integration or reboot HA host.

#### Switches & Plugs

| Name | Entity ID | Integration | Protocol | Location | Notes |
|------|-----------|-------------|----------|----------|-------|
| Sunroom Heater | `switch.sunroom_heater` | — | Wi-Fi | Sunroom | Controls heater. On by automation when temp drops. |
| Siren Alarm | `switch.siren_alarm` | Z-Wave | Z-Wave | Foyer/Utility | Siren for alerts (moisture, smoke). Manual on/off switch. |
| Peanut Switch 1 | `switch.securifi_ltd_unk_model_switch` | Z-Wave | Z-Wave | Bedroom 1 | Securifi Peanut plug. Controls Bedroom 1 thermostat/heater. |
| Peanut Switch 2 | `switch.peanut_switch_2_switch_2` | Z-Wave | Z-Wave | Bedroom 2 | Controls Bedroom 2 thermostat. |
| Peanut Switch 3 | `switch.peanut_switch_3_switch_2` | Z-Wave | Z-Wave | Bedroom 3 | Controls Bedroom 3 thermostat. |
| Switch 4 (Sylvania) | `switch.switch_4_sylvania_switch` | Z-Wave | Z-Wave | Living Room | Sylvania plug. Unavailable. |
| Switch 5 (Sylvania) | `switch.switch_5_sylvania_switch` | Z-Wave | Z-Wave | Bedroom 4 | Sylvania plug. Unavailable. |
| Patio Plug | `switch.outdoor_plug_feit_1_socket_1` | Z-Wave | Z-Wave | Patio | FEIT outdoor plug. Unavailable — check if weather-affected. |
| Outdoor Plug (FEIT) 2 | `switch.outdoor_plug_feit_2_socket_1` | Z-Wave | Z-Wave | Outdoors | Unavailable. |
| leakSMART Water Valve | `switch.leaksmart_water_valve_switch` | Z-Wave | Z-Wave | Utility Room | Main water shutoff valve. **Always on** when open. If closed, water to house is shut off. |
| Switch (TUYA) 1 | `switch.switch_tuya_1_socket_1` | Local Tuya | Wi-Fi (neuromancer) | — | Unavailable. |
| Switch (TUYA) 2 | `switch.switch_tuya_2_socket_1` | Local Tuya | Wi-Fi (neuromancer) | — | Unavailable. |
| Switch (TUYA) 3 | `switch.dining_room_cabinet_socket_1` | Local Tuya | Wi-Fi (neuromancer) | Dining Room | Unavailable. |
| Moria Surveillance Home Mode | `switch.moria_surveillance_station_home_mode` | Synology | Wired | Moria | Toggles Surveillance Station between home/away mode. |
| Motion Switch (Garage) | `switch.motion_switch_garage*` | Z-Wave | Z-Wave | Garage | Includes motion sensor + LED. Unavailable. |

**Peanut/Sylvania plug reset:** Unplug for 10 seconds, plug back in. If still not connecting, exclude and re-include via Z-Wave interface. Exclusion: Settings → Devices → Z-Wave → Remove Device, then press button on plug.

**leakSMART Water Valve:** If valve won't open/close, check that the controller is powered and within Z-Wave range. Manual override available at the valve itself (consult manual).

#### Climate

| Name | Entity ID | Integration | Notes |
|------|-----------|-------------|-------|
| Whole House Thermostat | `climate.ecobee` | Ecobee (cloud) | Controls main HVAC. Presets: home, away, sleep, away_indefinitely. Current: heat_cool (70.5°F low, 75.5°F high). If unresponsive: check Ecobee cloud integration status. |
| Minisplit | `climate.minisplit` | Home Connect Alt? | Currently off. |
| Bedroom 1 Thermostat | `climate.bedroom_1_thermostat` | Z-Wave | Controlled via Peanut Switch 1. Heat only. |
| Bedroom 2 Thermostat | `climate.bedroom_2_thermostat` | Z-Wave | Controlled via Peanut Switch 2. Off. |
| Bedroom 3 Thermostat | `climate.bedroom_3_thermostat` | Z-Wave | Controlled via Peanut Switch 3. Off. |
| Bedroom 4 Thermostat | `climate.bedroom_4_thermostat` | Z-Wave | Via Switch 5 (Sylvania). Off. |
| Living Room | `climate.living_room` | Z-Wave | Via Switch 4 (Sylvania). Off. |

**Ecobee maintenance:** Replace air filter every 3 months (Ecobee sends reminders). If HVAC isn't responding, check Ecobee equipment status: `sensor.ecobee_temperature`, `sensor.ecobee_humidity`. The Ecobee sensor tracks occupancy in the main living area.

#### Fans & Air Quality

| Name | Entity ID | Integration | Location | Notes |
|------|-----------|-------------|----------|-------|
| Blueair 7400 Fan | `fan.blueair_7400_fan` | Blueair | Office | Office air purifier. Fan speed adjustable via HA. Filter at 42% life — replace when <10%. |
| DustMagnet Fan | `fan.blueair_dustmagnet_fan` | Blueair | — | Second air purifier. Unavailable. |

**Blueair filter replacement:** When `sensor.blueair_7400_filter_life` drops below 10%, order replacement filters (Blueair 7400 series). Filter access: open front panel, remove old filter, insert new. Reset filter counter in Blueair app after replacement.

#### Sensors

##### Smoke & CO Detectors (Z-Wave)

| Name | Location | Battery | Notes |
|------|----------|---------|-------|
| Smoke & CO 1 | — | 96% | First Alert ZCombo. Last seen recently. |
| Smoke & CO 2 | — | 96% | Last seen recently. |
| Smoke & CO 3 | — | 94% | Currently showing Smoke Alarm Test active — may need investigation. |
| Smoke & CO 4 | — | 100% | Showing Smoke Alarm Test active. |
| Smoke & CO 5 | — | 89% | Healthy. |

**Maintenance:** All Z-Wave smoke/CO detectors are First Alert ZCombo units. Test monthly (press Test button). Replace batteries when `battery_level` drops below 20%. Replace entire unit at 10-year end-of-life. If `Maintenance required, dust in device` appears: vacuum dust ports gently.

##### Moisture / Leak Sensors (Z-Wave)

| Name | Location | Battery | Last Reading |
|------|----------|---------|-------------|
| Moisture 1 | Powder Room | 38.5% | 68.8°F, No moisture |
| Moisture 2 | Basement Window | 54% | 63.2°F, No moisture |
| Moisture 3 | Master Bath Kitchen | 84.5% | 69.2°F, No moisture |
| Moisture 4 | 2nd Bath Sink | 92.5% | 69.6°F, No moisture |
| Moisture 5 | HVAC Window | 54% | 66.3°F, No moisture |
| Moisture 6 | Laundry | 38.5% | 65.7°F, No moisture |
| Moisture 7 | Kitchen Sink | 84.5% | 69.0°F, No moisture |
| Moisture 8 | Ejector Pump | **7.5%** | 62.6°F — **Replace battery soon!** |
| Moisture 9 | Theatre Window | 84.5% | 61.5°F, No moisture |
| Moisture 10 | Sump Pump | 54% | 60.3°F, No moisture |
| Moisture 11 | Salt Level | 84.5% | 67.6°F, No moisture |

**Moisture sensor reset:** If a sensor incorrectly shows moisture, dry the sensor pads and press the reset button on the unit. Replace CR123A battery when below 20%. **Moisture 8 (Ejector Pump)** critically low at 7.5%.

##### Motion / Temperature Sensors (Z-Wave)

| Name | Location | Battery | Notes |
|------|----------|---------|-------|
| Motion Temp 1 | Master Bedroom | 100% | Multi-sensor: motion, temperature, light. |
| Motion Temp 2 | — | 72.5% | — |
| Motion Temp 3 | — | 91% | — |
| Motion Temp 4 | — | 91% | Bosch ISW-ZPR1-WP13. |
| H5104 2678 | — | 33% | Temp/humidity only. Replace battery soon. |
| H5104 7322 | — | 37% | Temp/humidity only. Replace battery soon. |

##### Contact Sensors (Z-Wave)

| Name | Location | Battery | Status |
|------|----------|---------|--------|
| Contact & Temp 1 | — | 77% | **Open** — door/window currently open |
| Contact & Temp 2 | — | Unknown | Closed |
| Contact & Temp 3 | — | Unknown | Closed |
| Contact & Temp 4 | — | **22%** | Closed — **Replace battery soon** |
| Contact & Temp 6 | — | 92.5% | Open |
| Contact & Temp 7 | — | 84.5% | Open |
| Contact & Temp 8 | — | Unavailable | Unknown |

##### Air Quality

| Sensor | Location | Reading | Notes |
|--------|----------|---------|-------|
| Airthings Wave2 149108 | Basement | Radon 1-day: **8.37 pCi/L (Poor)**, Longterm: 5.238 pCi/L (Poor), Humidity: 31.5%, Temp: 72.6°F | **Radon levels elevated.** Long-term average above 4 pCi/L (EPA action level). Track monthly. Mitigation may be needed. Battery: 63%. |

##### Printer

| Sensor | Value |
|--------|-------|
| **Brother DCP-L2550DW** | Status: toner low, Black toner remaining: 7%, Drum: 79% remaining (9377 pages) |
| **Page counter** | 2,623 total (duplex: 900) |

**Maintenance:** Order TN-730 toner when below 5%. Replace DR-730 drum unit when below 10% or error appears. Printer IP via DHCP on VLAN10.

#### Thermostat Scheduler Switches

These are helper switches that enable/disable scheduling rules for the room thermostats:

| Switch | Purpose |
|--------|---------|
| `switch.schedule_master_bedroom_to_economy_during_the_day` | Master scheduler — currently on. |
| `switch.schedule_27617a` | Off |
| `switch.schedule_a6644a` | Off |
| `switch.schedule_c4ac43` | Off |
| `switch.schedule_ed8a58` | Off |

#### Audio / Voice Devices

| Device | Entity | Notes |
|--------|--------|-------|
| Dan's Echo Dot | Various | Illuminance sensor, DND switch. Connected. |
| Office Echo | Various | Unavailable — check connectivity. |
| Dan's Fire TV Stick | Various | Unavailable. |
| Dan's 2nd Fire TV | Various | Unavailable. |

---

### Automation Reference

A summary of every active automation in the smart home.

#### Safety & Security

| Automation | State | What It Does |
|-----------|-------|-------------|
| **Smoke Alert** | 🟢 On | When any Z-Wave smoke detector triggers: activates Siren Alarm and sends notification. |
| **Smoke Alert** (2nd) | 🟢 On | Duplicate — triggers on different smoke sensor group for redundancy. |
| **Turn on Siren Alarm when moisture detected** | 🟢 On | When any moisture sensor detects water: activates Siren Alarm for 2 minutes and sends notification. Last triggered 5/13 for moisture. |
| **Low battery level** | 🟢 On | Daily check at 10 AM. Notifies when any sensor battery drops below 20%. Last checked 5/17. |
| **Salt Level Check** | 🟢 On | Monitors water softener salt level sensor. Notifies when salt is low. Last triggered 5/13. |
| **Salt Level Reset** | 🔴 Off | Manual counter reset after refilling salt. |

#### Comfort & Climate

| Automation | State | What It Does |
|-----------|-------|-------------|
| **Keep sunroom warm** | 🟢 On | If sunroom temperature drops below threshold: turns on Sunroom Heater. Last triggered 5/17. |
| **Scheduler Thermostats** | 🟢 On | Manages schedule for Master Bedroom thermostat. On=schedule active, off=manual override. |

#### Physical Controls (Z-Wave Scene Controllers)

| Automation | State | What It Does |
|-----------|-------|-------------|
| **Theatre Switch Short Press** | 🟢 On | Short press the theatre switch: toggles theatre room lights scene. |
| **Theatre Switch Double Press** | 🟢 On | Double press: alternate scene (e.g., full brightness). |
| **Theatre Switch Long Press** | 🟢 On | Long press: dim all lights or activate movie scene. |
| **LUMI Cube - Face 1** | 🟢 On | Xiaomi Cube controller: face 1 orientation triggers "Good Morning" scene. |
| **Cube test** | 🟢 On | Test automation for Xiaomi Cube gesture recognition. |

#### Pet & Daily Life

| Automation | State | What It Does |
|-----------|-------|-------------|
| **Bruno Needs To Go #1** | 🟢 On | If Bruno hasn't been outside by a certain time: sends notification. Last triggered 12/27. |
| **Reset Bruno Activity Datetime at Midnight** | 🟢 On | Resets Bruno's last-activity timestamp at midnight so the next day starts fresh. |
| **On the Move** (Mary) | 🟢 On | When Mary's phone leaves/arrives home zone: sends arrival/departure notification. Last triggered today. |
| **Mary on the Move** | 🔴 Off | Disabled — superseded by "On the Move" above. |
| **Mary on the Move - Snooze Reminder** | 🟢 On | Resends "On the Move" notification if Mary doesn't interact within timeout. |
| **Allison on the Move** | 🔴 Off | Disabled. |

#### Announcements

| Automation | State | What It Does |
|-----------|-------|-------------|
| **Speaker Announcement** | 🟢 On | Sends TTS announcements to connected speakers. Used for alerts, reminders, and notifications. Last triggered 5/20. |

#### Summary

**19 automations total:**
- 🟢 14 active
- 🔴 5 disabled

**Automations to review:**
- `smoke_alert` and `smoke_alert_2` are duplicative — consider consolidating
- `Cube test` was likely a test-only automation and may be stale
- `Mary on the Move` and `Allison on the Move` are disabled in favor of `On the Move`
- Theatre switch automations haven't triggered since 2024

---

### Operations — Maintenance, Troubleshooting, Configuration

#### Backups

Home Assistant can create full backups including configuration, automations, and integrations.

```bash
# Through the UI:
Settings → System → Backups → Create Backup
```

Backups include: configuration, automations, scenes, scripts, dashboards, and add-on data. Backups are stored locally on Home Assistant hardware and are included in nightly Rivendell backups to Moria.

#### Restarting

| Action | How |
|--------|-----|
| **Restart Home Assistant (soft)** | Settings → System → Restart → Restart Home Assistant |
| **Rebuild config** | Settings → System → Restart → Quick Reload |
| **Reboot host** | Settings → System → Restart → Reboot Host |

#### Adding New Devices

**Z-Wave / Zigbee:**
1. Put the device in pairing mode (follow the device manual)
2. In Home Assistant: Settings → Devices & Services → Z-Wave/Zigbee → Add Device
3. Home Assistant will discover and prompt for configuration

**Wi-Fi smart devices:**
1. Connect the device to **neuromancer** Wi-Fi (VLAN20)
2. Use the device's app to configure it, then add via Home Assistant integration
3. Let Dan or Noah know so it can be added to the proper Home Assistant integration

#### Troubleshooting

**Device not responding:**
1. Check if it works in the vendor app
2. Check Home Assistant: Developer Tools → States, search for the entity
3. Restart the integration: Settings → Devices & Services → Integration → Configure → Reload

**Home Assistant itself:**
1. Try http://homeassistant.lan:8123 — does it load?
2. If not, check if the HA host is on and responding to ping
3. If HA is stuck, try the soft restart (Settings → System → Restart)
4. If the host needs reboot: Settings → System → Restart → Reboot Host

**Z-Wave/Zigbee coordinator issues:**
1. Check the USB stick is connected to the HA host
2. Restart the Z-Wave/Zigbee integration
3. If the stick isn't detected, reboot the HA host
