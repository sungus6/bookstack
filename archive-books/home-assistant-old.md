# Home Assistant old
> Exported from BookStack on 2026-05-21
> Slug: home-assistant-old

---

## Contents

**Infrastructure & Setup**
- Installation
- Accounts
- Security
**Integrations**
- Z-Wave & Zigbee
- SmartThings
- Climate (Minisplit)
- Home Connect Alt (Bosch/Siemens appliances)
- Local Tuya Integration
- Ecobee
**Automations & Maintenance**
- Backups
- Automations
- Maintenace Log
**Add-ons**
- HACS

---

## Chapter: Infrastructure & Setup

### Installation

### Installation

**Created:** 2023-12-11

#### Hardware
Raspberry Pi 4 (rpi4-64)

#### OS
- **Installation method:** Home Assistant OS
- **Operating System:** 17.1
- **Frontend:** 20260312.0

#### System Info
- **Home Assistant Version:** 2026.3.3
- **Unit System:** Imperial (US)
- **Timezone:** America/Chicago
- **Location:** Home (Hawthorn Woods, IL)

#### Network
- **IP Address (Static):** 192.168.88.5
- **Access via Browser:** <http://homeassistant:8123>
      - or <http://192.168.88.5:8123>
- **Current Config Info:** 
[http://homeassistant:8123/config/info](http://homeassistant:8123/config/info)

---

### Accounts

### Accounts

| User Name | Group | Purpose | Note |
| :--- | :--- | :--- | :--- |
| Aule | Administrator | Administration | Password in Keepass DB |
| Kiosk | Kiosk | Used on the tablet kiosk | Password in Keepass DB |
| hassio | root | SSH & Web Terminal | Password in Keepass DB. This is an OS level account |
| usernames | User | Users | |

---

### Security

### Security

- **General:** Running agents on your computer is risky — harden your setup.
- **Reference:** [https://docs.openclaw.ai/security](https://docs.openclaw.ai/security)

#### Access Control
- **Home Assistant Cloud (Nabu Casa):**
- Provides Home Assistant access from the internet outside of the home network.
- **Monthly fee:** Approx $7 per month. Auto-paid through Chase checking.
- **URL and Passwords:** In Sung Keepass DB

#### OpenClaw Secrets
- **Client ID:** `2F9C694A6FEBB954FD2516399F834021B003E73E8C7AA217D9535842E19D56E3`
- **Client Secret:** `46D1AAFE8253B6141BB6F35E94D8B0848099078FCD46387B1E303B75B82FB9DD`
- **SingleKey-ID:** In Sung Keepass DB

---

## Chapter: Integrations

### Z-Wave & Zigbee

### Z-Wave & Zigbee

#### Z-Wave
- **Controller:** S2 USB Stick Controller
- **Model:** ZST10 (Zooz)

#### Zigbee
* [Details to be filled]

---

### SmartThings

### SmartThings

- **Integration Instructions:** [SmartThings - Home Assistant (home-assistant.io)](https://www.home-assistant.io)

#### Personal Access Token
- **Note:** HomeAssistant to SmartThings integration requires a Personal Access Token generated from `smartthings.com`.
- **Name:** Home Assistant
- **Token:** `44182e7d-413a-4425-b060-832742288ee7`

---

### Climate (Minisplit)

### Climate: Costway Minisplit

#### Overview
The Costway minisplit in the sunroom is controlled using a Broadlink IR remote.

#### Integration: SmartIR
- **HACS Integration:** [SmartIR](https://github.com/smartir-home-assistant/smartir) is used to create a virtual climate entity.
- **Hardware Dependency:**
- **Broadlink Remote:** Used for sending the IR signals.
- **Contact & Temp 7:** Used as the feedback sensor to provide the current temperature.
- **Key Files:**
- Configuration details and climate codes are mapped in `configuration.yaml` (or `climate.yaml` if you've split it).
- Ensure the *SmartIR* component is correctly referencing the specific JSON code file for your Costway model.

---

### Home Connect Alt (Bosch/Siemens appliances)

#### Application Credentials
- **Client ID:** `2F9C694A6FEBB954FD2516399F834021B003E73E8C7AA217D9535842E19D56E3`
- **Client Secret:** `46D1AAFE8253B6141BB6F35E94D8B0848099078FCD46387B1E303B75B82FB9DD`
- **SingleKey-ID:** In Sung Keepass DB

#### To View or Maintain Application Credentials
1. The Home Connect Developer Portal (Source). This is where the codes were originally generated. 
    - **Website:** developer.home-connect.com (https://developer.home-connect.com/)
    - **Where to look:** Log in and go to the "Applications" section. Verification: You should see an entry (likely named "Home Assistant") that lists the Client ID (it should match your 2F9C... code). The Client Secret will also be listed there, though it might be partially masked for security until you click to view it.
2. Within Home Assistant (Stored Config)

    If the integration is already set up and working, Home Assistant stores these credentials in a central location:
    - **Path:** Go to **Settings > Devices & Services.**  
    - **Menu:** Click the three dots (⋮) in the top right corner of the page.
    - **Selection:** Select Aplication Credentials.

---

### Local Tuya Integration

## Local Tuya Integration

For Feit devices

#### Authorization Key and Access Codes
In Sung Keepass DB

---

### Ecobee

## Authorization
- **Authorization Method:** ecobee PIN (VHPT-DLCF)
- **API Key:** In Sung Keepass DB
- **Instruction:**
  1. Select the Developer option from the hamburger menu on the top-right.
  2. Select Create New.
  3. Complete the form on the right. (Neither of the fields are referenced by Home Assistant)
	○ Name: Must be unique across all ecobee users.
	○ Summary: Does not need to be unique.
  4. Click Authorization method and select ecobee PIN.
  5. Click Create.

---

## Chapter: Automations & Maintenance

### Backups

### Backups

- **Strategy:** Automatic nightly backups via the Home Assistant Google Drive Backup addon.
- **Off-site:** Backups are also mirrored to [Location, e.g., Moria or Cloud].
- **Restore Procedure:**
1. Reinstall Home Assistant.
2. Install the Google Drive Backup addon.
3. Log in and restore from the latest snapshot.

### Restore
Home Assistant Backup Emergency Kit

This emergency kit contains your backup encryption key. You need this key to be able to restore your Home Assistant backups.

Date: January 20, 2025 at 5:02 PM

Instance:
Home

URL:
http://homeassistant.local:8123

Encryption key:
UFD2-BDZK-W62K-SMRF-AI88-6504-JXOT

For more information, visit https://www.home-assistant.io/more-info/backup-emergency-kit

---

### Automations

### Key Automations

- **[Automation Name 1]:** Briefly describe what it does (e.g., "Turns off sunroom minisplit when contact sensor opens").
- **[Automation Name 2]:** Briefly describe what it does.

*Tip: If you have complex YAML automations, store them in a separate `automations.yaml` file to keep the main config clean.*

---

### Maintenace Log

### Maintenance Log

| Date | Maintenance Task | Performed By | Notes |
| :--- | :--- | :--- | :--- |
| 2026-03-23 | Wiki Migration | Dan | Recreated "Smart Home" shelf and pages |

---

## Chapter: Add-ons

### HACS

## HACS authorization Code
C801-D57D

---
