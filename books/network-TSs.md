# Network
> Exported from BookStack on 2026-05-14
> Slug: network-TSs

---

## Contents

**Architecture**
- Architecture & Design
- WiFi Architecture
**Hardware**
- MikroTik Reference
- Zyxel Reference
- IP & DNS Reference
- Old/Misc Hardware
**Operations**
- Everyday Operations

---

## Chapter: Architecture

### Architecture & Design

# Architecture & Design

## Overview

The Arda network is a home network built around proper VLAN segmentation, managed switching, and a dedicated management plane. All routing, DHCP, and DNS is handled by a MikroTik RB750GL router. A Zyxel GS1900-24HP managed switch handles VLAN tagging and port assignment. UniFi APs provide wireless coverage across multiple SSIDs mapped to appropriate VLANs.

The network is designed with two core principles:

**Separation of trust.** IoT devices are isolated from trusted devices and cannot reach the management plane. Trusted devices cannot reach the management plane except through a controlled SSH tunnel. Only machines on VLAN99 have direct administrative access.

**Resilience during recovery.** A dedicated management VLAN (VLAN99) and a physical emergency bridge on MikroTik ensure that administrative access is always available even when the primary network is misconfigured or broken.

## Physical Topology

```
Internet
    |
Xfinity Modem (wintermute_x) — 10.0.0.1
    |
MikroTik RB750GL
    ├── ether1-WAN         → Xfinity modem
    ├── ether2-TRUNK       → Zyxel port 1 (tagged trunk, all VLANs)
    ├── ether3-unused
    ├── ether4-unused
    └── ether5-EMERGENCY   → Emergency bridge (192.168.88.0/24)

Zyxel GS1900-24HP
    ├── Port 1             → MikroTik ether2-TRUNK
    ├── Ports 2-6          → UniFi APs (VLAN10 untagged, VLAN20 tagged)
    ├── Ports 7-20         → Trusted devices (VLAN10)
    ├── Ports 21-23        → IoT wired devices (VLAN20)
    └── Port 24            → palantir (VLAN99)
```

## VLAN Design

| VLAN | Name | Subnet | Gateway | DNS | Purpose |
|---|---|---|---|---|---|
| 10 | trusted | 192.168.10.0/24 | 192.168.10.1 | 192.168.10.1 | Trusted devices, PCs, servers |
| 20 | iot | 192.168.20.0/24 | 192.168.20.1 | 8.8.8.8, 8.8.4.4 | IoT devices, isolated |
| 99 | mgmt | 192.168.99.0/24 | 192.168.99.1 | 192.168.99.1 | Management machines only |
| N/A | emergency | 192.168.88.0/24 | 192.168.88.1 | 192.168.88.1 | Emergency access, MikroTik ether5 |

**Why IoT uses Google DNS directly:** IoT devices use 8.8.8.8 rather than MikroTik. This means they never need to reach MikroTik's admin interface for DNS, and vlan20-iot does not need to be in MikroTik's LAN interface list. This is intentional and more secure.

## Security Model

**VLAN10 (trusted) can:**
- Access internet
- Access other VLAN10 devices
- SSH to palantir (192.168.99.21 port 22 specifically allowed)
- Ping MikroTik (ICMP allowed for diagnostics)
- Reach MikroTik DNS (port 53)

**VLAN10 cannot:**
- Access MikroTik admin (SSH, Winbox, HTTP blocked)
- Access VLAN20 devices
- Access VLAN99 devices directly (except palantir via SSH)

**VLAN20 (iot) can:**
- Access internet
- Reach Home Assistant on specific ports (8123 TCP, 8009/8010/5353 UDP)

**VLAN20 cannot:**
- Access VLAN10 devices
- Access VLAN99 devices
- Reach MikroTik admin or DNS

**VLAN99 (mgmt) can:**
- Full access to MikroTik admin
- Access Zyxel management (192.168.99.2)
- Access VLAN10 devices (for RDP and management)
- Internet access — DISABLED intentionally (re-enable temporarily for apt update)

---

### WiFi Architecture

# WiFi Architecture

## Access Points

Five UniFi APs provide wireless coverage throughout the house:

| AP | Model | Zyxel Port | IP |
|---|---|---|---|
| AP1 | UAP-AC-Pro | Port 2 | 192.168.10.11 |
| AP2 | UAP-AC-Lite | Port 3 | 192.168.10.12 |
| AP3 | UAP-AC-Lite | Port 4 | unknown |
| AP4 | UAP-AC-Lite | Port 5 | unknown |
| AP5 | UAP-AC-Lite | Port 6 | unknown |

The UniFi controller runs as a Docker container on Rivendell at https://192.168.10.4:8443.

## SSIDs

| SSID | UniFi Network | VLAN | Use |
|---|---|---|---|
| wintermute | Default (untagged) | 10 via PVID | Family devices, phones, laptops |
| neuromancer | IoT (VLAN20) | 20 | Smart home devices, IoT |

## How VLAN Assignment Works for WiFi

AP ports (2-6) on the Zyxel have PVID=10 and VLAN20 as Tagged. This means:

- **Untagged frames** from the AP land on VLAN10 automatically via PVID
- **Tagged VLAN20 frames** from the AP pass through to VLAN20

wintermute clients send untagged frames → land on VLAN10 → get 192.168.10.x addresses.
neuromancer clients send VLAN20-tagged frames → land on VLAN20 → get 192.168.20.x addresses.

## Critical: wintermute Must Be on "Default" Network in UniFi

**wintermute must be assigned to the "Default" network in UniFi, NOT "Trusted (VLAN10)".**

If wintermute is assigned to "Trusted (VLAN10)", the AP explicitly tags frames as VLAN10.
But the Zyxel port PVID=10 already handles that for untagged frames — the explicit tag
conflicts, and clients connect but get 169.254.x.x addresses with no internet.

The correct setup: wintermute → Default (untagged) → PVID=10 on Zyxel → VLAN10.

neuromancer correctly uses the IoT network with VLAN20 because VLAN20 is Tagged on AP ports.

## AP Management

APs manage themselves on VLAN10 (untagged, PVID=10) and get IPs from the VLAN10 pool.

## AP SSH Access

SSH credentials are managed globally by the UniFi controller and pushed to all APs.

| Field | Value |
|---|---|
| Username | aule |
| Password | (see password manager) |
| SSH command | `ssh aule@<ap-ip>` |
| set-inform command | `/usr/bin/syswrapper.sh set-inform http://192.168.10.4:8080/inform` |
| Device Auth URL | https://192.168.10.4:8443/manage/em6yfgq5/devices?resultId=deviceUpdatesAndSettings-static-6 |

Use set-inform when an AP shows as disconnected after a controller migration or IP change.

---

## Chapter: Hardware

### MikroTik Reference

# MikroTik Reference

## Hardware

| Field | Value |
|---|---|
| Model | MikroTik RB750GL |
| RouterOS | 7.22.1 |
| Serial | 467A022C49C2 |

## Interface Layout

| Interface | Name | Role |
|---|---|---|
| ether1 | ether1-WAN | WAN uplink to Xfinity modem |
| ether2 | ether2-TRUNK | Tagged trunk to Zyxel (all VLANs) |
| ether3 | ether3-unused | Unused, not bridged |
| ether4 | ether4-unused | Unused, not bridged |
| ether5 | ether5-EMERGENCY | Emergency bridge access |

## VLAN Interfaces

All VLAN interfaces run on ether2-TRUNK:

| Interface | VLAN ID | IP | Purpose |
|---|---|---|---|
| vlan10-trusted | 10 | 192.168.10.1/24 | Trusted LAN gateway |
| vlan20-iot | 20 | 192.168.20.1/24 | IoT gateway |
| vlan99-mgmt | 99 | 192.168.99.1/24 | Management gateway |

## Interface List Members — CRITICAL

This is one of the most important configuration items. Missing entries cause subtle
connectivity failures that are difficult to diagnose.

```
bridge-emergency → LAN    (emergency access treated as trusted)
ether1-WAN → WAN          (WAN interface)
vlan99-mgmt → LAN         (REQUIRED: palantir SSH to MikroTik)
vlan99-mgmt → MGMT        (management interface list)
bridge-emergency → MGMT   (emergency also in MGMT)
vlan10-trusted → LAN      (REQUIRED: VLAN10 DNS and routing)
```

**Why this matters:** MikroTik's default firewall rule 5 drops all input traffic from
interfaces NOT in the LAN list. If vlan10-trusted is missing, VLAN10 clients can ping
MikroTik but DNS times out and internet breaks. If vlan99-mgmt is missing, palantir
cannot SSH into MikroTik.

**vlan20-iot is intentionally NOT in LAN.** IoT uses Google DNS directly and has no
legitimate reason to reach MikroTik.

Verify with:
```
/interface list member print
```

## DHCP Pools

| Pool | Range | Interface |
|---|---|---|
| default-dhcp | 192.168.88.10-254 | bridge-emergency |
| pool-trusted | 192.168.10.10-200 | vlan10-trusted |
| pool-iot | 192.168.20.10-200 | vlan20-iot |
| pool-mgmt | 192.168.99.10-50 | vlan99-mgmt |

## Admin Access Restrictions

MikroTik admin services are restricted to VLAN99 and emergency bridge only:

```
SSH:    192.168.99.0/24 and 192.168.88.0/24 only
HTTP:   192.168.99.0/24 and 192.168.88.0/24 only
Winbox: 192.168.99.0/24 and 192.168.88.0/24 only
FTP:    disabled
Telnet: disabled
API:    disabled
```

VLAN10 machines (minasmorgul, osgiliath, etc.) cannot directly SSH or Winbox into
MikroTik. They must use the SSH tunnel via palantir.

## Firewall Rules Summary

**Input chain (to MikroTik itself):**
- Accept established/related/untracked
- Drop invalid
- Accept ICMP from all LAN sources
- Drop all not from LAN interface list (rule 5 — critical gate)
- Full access from VLAN99
- DNS (53) from trusted LAN and management
- Block admin ports from IoT and trusted LAN
- Drop all from WAN

**Forward chain (through MikroTik):**
- Trusted LAN to WAN
- IoT to WAN
- Management to WAN — **DISABLED** intentionally
- HA to Moria (specific ports)
- IoT to HA (8123, 8009/8010/5353)
- Allow SSH from Trusted LAN to palantir specifically
- Block all inter-VLAN traffic (catch-all at end)

## Syslog

MikroTik sends info logs to palantir (192.168.99.21) on UDP 514.
palantir runs rsyslog and writes MikroTik logs to `/var/log/mikrotik.log`.

To generate a test log entry:
```
/log info message="test from mikrotik"
```

## Emergency Bridge

Connect any machine to ether5-EMERGENCY with static IP 192.168.88.x/24, gateway 192.168.88.1.

On Linux (isengard):
```bash
sudo ip link set enp1s0 up
sudo ip addr add 192.168.88.50/24 dev enp1s0
sudo ip route add default via 192.168.88.1
ssh aule@192.168.88.1
```

## Common Commands

```
/export                              — export full config to terminal
/export file=filename                — export to file
/ip dhcp-server lease print          — show DHCP leases
/ip dns static print                 — show DNS entries
/ip firewall filter print stats      — show firewall rules with hit counts
/interface list member print         — show interface list members (CRITICAL)
/ip firewall filter enable NUMBER    — enable a disabled rule
/ip firewall filter disable NUMBER   — disable a rule
/log info message="test"             — generate a test log entry
```

## Temporarily Re-enabling palantir Internet Access

palantir internet access is intentionally disabled. Re-enable for apt update:
```
/ip firewall filter enable [find comment="Management to WAN (temporary)"]
```

Disable again immediately after:
```
/ip firewall filter disable [find comment="Management to WAN (temporary)"]
```

---

### Zyxel Reference

# Zyxel Reference

## Hardware

| Field | Value |
|---|---|
| Model | Zyxel GS1900-24HP |
| Management IP | 192.168.99.2 |
| Management VLAN | 99 |
| Login | admin / [password in KeePass] |

Access: http://192.168.99.2 from palantir directly,
or http://localhost:8080 via SSH tunnel from minasmorgul.

## Port Layout

| Port | Device | VLAN | Role |
|---|---|---|---|
| Port 1 | MikroTik ether2-TRUNK | Tagged (all) | Trunk uplink |
| Port 2 | UAP-AC-Pro | PVID 10, VLAN20 tagged | WiFi AP |
| Port 3 | UAP-AC-Lite 1 | PVID 10, VLAN20 tagged | WiFi AP |
| Port 4 | UAP-AC-Lite 2 | PVID 10, VLAN20 tagged | WiFi AP |
| Port 5 | UAP-AC-Lite 3 | PVID 10, VLAN20 tagged | WiFi AP |
| Port 6 | UAP-AC-Lite 4 | PVID 10, VLAN20 tagged | WiFi AP |
| Ports 7-20 | Trusted devices | PVID 10 | VLAN10 access |
| Ports 21-23 | IoT wired devices | PVID 20 | VLAN20 access |
| Port 24 | palantir | PVID 99 | VLAN99 management |

## VLAN Membership Tables

**VLAN10 (trusted)**

| Port | Setting |
|---|---|
| Port 1 | Tagged |
| Ports 2-20 | Untagged |
| Ports 21-23 | Excluded |
| Port 24 | Excluded |
| LAG1-8 | Excluded |

**VLAN20 (iot)**

| Port | Setting |
|---|---|
| Port 1 | Tagged |
| Ports 2-6 | Tagged |
| Ports 7-20 | Excluded |
| Ports 21-23 | Untagged |
| Port 24 | Excluded |
| LAG1-8 | Excluded |

**VLAN99 (mgmt)**

| Port | Setting |
|---|---|
| Port 1 | Tagged |
| Ports 2-23 | Excluded |
| Port 24 | Untagged |
| LAG1-8 | Excluded |

## VLAN Port Settings

| Port | PVID | Accept Frame Type | Ingress Check | VLAN Trunking |
|---|---|---|---|---|
| Port 1 | 1 | Tagged Only | Enable | Enable |
| Ports 2-6 | 10 | All | Enable | Enable |
| Ports 7-20 | 10 | All | Enable | Disable |
| Ports 21-23 | 20 | All | Enable | Disable |
| Port 24 | 99 | All | Enable | Disable |
| LAG1-8 | 1 | All | Disable | Disable |

## Saving Configuration

Always save to flash after any change. Without this, changes are lost on power cycle.

Maintenance → Configuration → Source: Running Configuration → Destination: Startup Configuration → Apply

## Backing Up Configuration

Maintenance → Configuration → Source: Running Configuration → Method: HTTP → Apply

Downloads a .cfg file. Follow the backup procedure in Book 9 → Backup & Recovery.

## Critical Rule — Never Exclude VLAN1

Never exclude VLAN1 from any ports. This has caused complete lockouts requiring
factory reset multiple times. VLAN1 is used internally by the Zyxel regardless of
the management VLAN setting.

---

### IP & DNS Reference

# IP & DNS Reference

## IP Address Table

| IP | Hostname | Device | VLAN |
|---|---|---|---|
| 10.0.0.1 | — | Xfinity modem (wintermute_x) | WAN |
| 192.168.88.1 | router.lan | MikroTik emergency bridge | emergency |
| 192.168.10.1 | — | MikroTik VLAN10 gateway | 10 |
| 192.168.10.4 | rivendell.lan | Docker/AI server | 10 |
| 192.168.10.6 | moria.lan, unifi.lan | Synology NAS NIC1 | 10 |
| 192.168.10.7 | — | Synology NAS NIC2 | 10 |
| 192.168.10.8 | minastirith.lan | Legacy Ubuntu server | 10 |
| 192.168.10.10 | homeassistant.lan | Home Assistant | 10 |
| 192.168.10.16 | minasmorgul.lan | Windows management machine | 10 |
| 192.168.20.1 | — | MikroTik VLAN20 gateway | 20 |
| 192.168.99.1 | — | MikroTik VLAN99 gateway | 99 |
| 192.168.99.2 | — | Zyxel management | 99 |
| 192.168.99.21 | palantir.lan | Management machine | 99 |

## Static DHCP Leases

| IP | MAC | Machine | Pool |
|---|---|---|---|
| 192.168.10.4 | AC:22:0B:75:E9:31 | rivendell | dhcp-trusted |
| 192.168.10.6 | 00:11:32:0B:D9:C9 | moria NIC1 | dhcp-trusted |
| 192.168.10.7 | 00:11:32:0B:D9:CA | moria NIC2 | dhcp-trusted |
| 192.168.10.8 | 00:19:B9:62:2B:63 | minastirith | dhcp-trusted |
| 192.168.10.10 | E4:5F:01:3F:B5:AC | homeassistant | dhcp-trusted |
| 192.168.10.16 | 00:21:CC:D5:89:C8 | minasmorgul | dhcp-trusted |
| 192.168.99.21 | D4:BE:D9:27:84:9A | palantir | dhcp-mgmt |

## DNS Static Entries

| Hostname | IP | Notes |
|---|---|---|
| router.lan | 192.168.88.1 | MikroTik emergency bridge |
| moria / moria.lan | 192.168.10.6 | Synology NAS |
| unifi / unifi.lan | 192.168.10.6 | UniFi controller on moria |
| homeassistant / homeassistant.lan | 192.168.10.10 | Home Assistant |
| minastirith / minastirith.lan | 192.168.10.8 | Ubuntu server (wildcard) |
| palantir / palantir.lan | 192.168.99.21 | Management machine |
| minasmorgul / minasmorgul.lan | 192.168.10.16 | Windows machine |
| rivendell / rivendell.lan | 192.168.10.4 | Docker/AI server |

## DNS Notes

MikroTik handles local DNS for VLAN10 and VLAN99 machines.
The `.lan` suffix resolves to local IPs (e.g. `moria.lan` → 192.168.10.6).
IoT devices (VLAN20) use Google DNS (8.8.8.8) directly — they do not resolve `.lan` names.

Upstream DNS: 9.9.9.9 (Quad9) and 1.1.1.1 (Cloudflare).

## Port Reference

| Service | Port | Protocol | Where accessible from |
|---|---|---|---|
| MikroTik SSH | 22 | TCP | VLAN99 and emergency only |
| MikroTik HTTP | 80 | TCP | VLAN99 and emergency only |
| MikroTik Winbox | 8291 | TCP | VLAN99 and emergency only |
| Zyxel HTTP | 80 | TCP | VLAN99 only |
| UniFi HTTP | 8080 | TCP | VLAN10 |
| UniFi HTTPS | 8443 | TCP | VLAN10 |
| Ollama | 11434 | TCP | VLAN10 |
| LiteLLM | 4000 | TCP | VLAN10 |
| openclaw | 7000 | TCP | VLAN10 |
| BookStack | 6875 | TCP | VLAN10 |
| Prometheus | 9090 | TCP | VLAN10 |
| Grafana | 3001 | TCP | VLAN10 |
| Portainer | 9443 | TCP | VLAN10 |
| MikroTik syslog | 514 | UDP | palantir receives |

---

### Old/Misc Hardware

_No markdown content. This page was edited in WYSIWYG mode._

---

## Chapter: Operations

### Everyday Operations

# Everyday Operations

## Access Table

| Target | From | Method |
|---|---|---|
| Zyxel UI | palantir | http://192.168.99.2 directly |
| MikroTik UI | palantir | http://192.168.99.1 directly |
| MikroTik SSH | palantir | `ssh mikrotik` |
| Moria SSH | palantir | `ssh moria` |
| Zyxel UI | minasmorgul | SSH tunnel → http://localhost:8080 |
| MikroTik UI | minasmorgul | SSH tunnel → http://localhost:8081 |
| palantir SSH | minasmorgul | `ssh palantir` |
| MikroTik SSH | minasmorgul | SSH into palantir, then `ssh mikrotik` |
| Any VLAN10 device | minasmorgul | Direct (same VLAN) |

## SSH Tunnel Setup (minasmorgul)

The SSH tunnel gives minasmorgul browser access to Zyxel and MikroTik UIs despite
being on VLAN10, which is blocked from direct admin access.

SSH config files:
- `C:\Users\sungu\.ssh\config`
- `C:\Users\aule\.ssh\config`

Contents:
```
Host palantir
    HostName 192.168.99.21
    User aule
    LocalForward 8080 192.168.99.2:80
    LocalForward 8081 192.168.99.1:80
```

Usage:
1. Open PowerShell: `ssh palantir` (keep window open)
2. Browse http://localhost:8080 → Zyxel
3. Browse http://localhost:8081 → MikroTik

To verify tunnel is active: `netstat -an | findstr 8080` should show LISTENING.

## palantir SSH Keys

| Key | Path | Purpose |
|---|---|---|
| id_moria | ~/.ssh/id_moria | Passwordless SSH/rsync to moria |
| id_mikrotik | ~/.ssh/id_mikrotik | Passwordless SSH to MikroTik as aule |

palantir SSH config (`~/.ssh/config`):
```
Host moria
    HostName 192.168.10.6
    User aule
    IdentityFile /home/aule/.ssh/id_moria

Host mikrotik
    HostName 192.168.99.1
    User aule
    IdentityFile /home/aule/.ssh/id_mikrotik
```

## Making Config Changes

Always follow this sequence for any network config change:

1. Take a backup before changing anything
2. Make the change
3. Verify it works
4. Save to flash (Zyxel) or config is already live (MikroTik)
5. Take another backup after the change
6. Push backup to moria

## palantir Notes

palantir must always have WiFi disabled. If WiFi is active, routing breaks — SSH
replies go out via WiFi instead of wired VLAN99.

```bash
# Check WiFi status
nmcli radio wifi

# Disable WiFi
sudo nmcli radio wifi off
```

Wired interface enp1s0 should have metric 100 in NetworkManager:
```bash
ip route show
# Should show enp1s0 default route at metric 100
```

---
