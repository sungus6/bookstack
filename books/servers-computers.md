# Servers & Computers
> Exported from BookStack on 2026-05-14
> Slug: servers-computers

---

## Contents

**Backups**
- Backup Strategy
**Servers**
- Rivendell - Docker Server
- Moria - NAS & Storage
- Belagost (Buffalo Link NAS)
- Erebor (Dlink Sharecenter NAS)
- Home Assistant
**Other Machines**
- Isengard
- Palantir — Management Machine
- Minasmorgul

---

## Chapter: Backups

### Backup Strategy

# Backup Strategy

## Overview

Arda uses a two-tier backup strategy:

**Tier 1 — Local on palantir** — always accessible during recovery, even if moria is down.
palantir is the first machine available during any network recovery.

**Tier 2 — Remote on moria** — long-term storage and redundancy.

Backup scripts run on palantir and push to moria. If moria is unreachable, the
local backup still exists and the script logs the failure.

## What's Backed Up

| Component | Method | Frequency | Script |
|---|---|---|---|
| MikroTik config | Automated script | On-demand / weekly | backup-mikrotik.sh |
| Zyxel config | Manual download | After any change | See procedure below |
| palantir home dir | Automated script | On-demand / weekly | backup-palantir.sh |
| UniFi | Auto (built-in) | Automatic | No script needed |
| Rivendell | TODO | TBD | Not yet written |

## Local Structure on palantir

```
/home/aule/backups/
├── mikrotik/
│   ├── latest/mikrotik-latest.rsc
│   └── archive/mikrotik-YYYYMMDD.rsc
├── zyxel/
│   ├── latest/zyxel-latest.cfg
│   ├── archive/zyxel-YYYYMMDD.cfg
│   └── README.md
├── palantir/
│   ├── latest/palantir-latest.tar.gz
│   └── archive/palantir-YYYYMMDD.tar.gz
├── unifi/
│   └── README.md
└── rivendell/
    └── (TODO)
```

## MikroTik Backup

Run from palantir:
```bash
/home/aule/scripts/backup-mikrotik.sh
cat /home/aule/logs/backup/backup-mikrotik.log
```

Restore from palantir:
```bash
scp /home/aule/backups/mikrotik/latest/mikrotik-latest.rsc mikrotik:mikrotik-latest.rsc
ssh mikrotik
/import file=mikrotik-latest.rsc
```

## Zyxel Backup — Manual

1. Open http://192.168.99.2 on palantir browser
2. Maintenance → Configuration → Source: Running Configuration, Method: HTTP
3. File downloads to palantir Downloads folder
4. If downloaded on minasmorgul, SCP to palantir:
   ```cmd
   scp C:\Users\aule\Downloads\zyxel-YYYYMMDD.cfg palantir:/home/aule/backups/zyxel/archive/zyxel-YYYYMMDD.cfg
   ```
5. On palantir:
   ```bash
   cp ~/backups/zyxel/archive/zyxel-YYYYMMDD.cfg ~/backups/zyxel/latest/zyxel-latest.cfg
   rsync -av -e "ssh -i /home/aule/.ssh/id_moria" \
     ~/backups/zyxel/archive/zyxel-YYYYMMDD.cfg \
     aule@192.168.10.6:/volume1/backups/network/zyxel/zyxel-YYYYMMDD.cfg \
     --rsync-path=/usr/bin/rsync
   ```

**Do this after every Zyxel config change.**

## palantir Backup

Run from palantir:
```bash
/home/aule/scripts/backup-palantir.sh
```

Archives entire home directory excluding logs and downloads. Includes scripts,
SSH keys, backup READMEs, and configs.

## UniFi Backup

UniFi creates automatic backups at:
`/volume1/docker/UniFi/data/backup/autobackup/`

For manual backup: UniFi controller → System Settings → Backup → Download Backup.
Store .unf files at `/volume1/backups/network/unifi/`.

## rsync Pattern (palantir to moria)

```bash
rsync -av -e "ssh -i /home/aule/.ssh/id_moria" \
  SOURCE_FILE \
  aule@192.168.10.6:DESTINATION_PATH \
  --rsync-path=/usr/bin/rsync
```

The `--rsync-path=/usr/bin/rsync` flag is required for Synology compatibility.

## Priority During a Crisis

If multiple things are broken at once, recover in this order:

1. **MikroTik first** — without the router nothing else works
2. **Zyxel second** — without switching, VLANs don't work
3. **palantir** — needed for management access
4. **UniFi** — WiFi, but wired still works without it
5. **Rivendell services** — AI, BookStack, etc. can wait

---

## Chapter: Servers

### Rivendell - Docker Server

# Rivendell - Docker Server

## Overview

Rivendell (formerly minasanor) is the primary server in Arda. It runs all Docker-based
workloads including the AI stack, BookStack wiki, monitoring, and external access.

| Field | Value |
|---|---|
| OS | Ubuntu 24.04 LTS |
| IP | 192.168.10.4 |
| DNS | rivendell.lan |
| VLAN | 10 (trusted) |
| Access | `ssh aule@rivendell.lan` |
| GPU | NVIDIA GTX 1060 6GB (local LLM inference) |

## Docker Containers

| Container | Image | Port | Purpose |
|---|---|---|---|
| bookstack | solidnerd/bookstack | 6875 | Wiki/documentation |
| bookstack_db | mariadb:10.11 | - | BookStack database |
| ollama | ollama/ollama:0.3.12 | 11434 | Local LLM inference |
| litellm | ghcr.io/berriai/litellm | 4000 | LLM proxy/router |
| openclaw | python:3.11-slim | 7000 | Aule Telegram bot |
| prometheus | prom/prometheus | 9090 | Metrics collection |
| grafana | grafana/grafana | 3001 | Dashboards |
| cloudflared | cloudflare/cloudflared | - | Cloudflare tunnel |
| portainer | portainer/portainer-ce | 9443 | Container management UI |

## Stack Locations

```
/mnt/work/
??? ai-stack/
?   ??? docker-compose.yml     (ollama, litellm)
??? infra-stack/
?   ??? docker-compose.yml     (prometheus, grafana, cloudflared, portainer)
??? book-stack/
?   ??? docker-compose.yml     (bookstack, bookstack_db)
??? /data/compose/
    ??? openclaw/
        ??? docker-compose.yml
```

## Common Operations

```bash
# Check all running containers
docker ps

# Check a specific container's logs
docker logs CONTAINER_NAME --tail 50
docker logs CONTAINER_NAME -f    # follow live

# Restart a container
docker restart CONTAINER_NAME

# Restart an entire stack
cd /mnt/work/ai-stack
docker compose down && docker compose up -d

# Pull latest images and restart
cd /mnt/work/ai-stack
docker compose pull && docker compose up -d

# Check GPU usage (for Ollama)
nvidia-smi

# Check resource usage across all containers
docker stats
```

## Storage Mounts

Persistent data lives in bind-mounted directories on rivendell - not inside containers.
Deleting a container does NOT delete its data.

```bash
# Find where a container stores data
docker inspect CONTAINER_NAME | grep -A 10 Mounts

# Check disk usage
df -h /mnt/work
```

## Portainer

Portainer provides a web UI for Docker management without SSH.
Access: https://192.168.10.4:9443
Admin credentials in Sung KeePass DB.

Useful for: viewing container status, logs, resource usage, restarting containers,
and browsing volume contents without touching the command line.

## Hardware Notes

- CPU: handles Docker workloads comfortably
- GPU: GTX 1060 6GB - supports 7B parameter models in Ollama comfortably.
  Larger models (13B+) fall back to CPU or cloud.
- Storage: check available space regularly - Ollama models are large (4-8GB each)

```bash
# Check disk space
df -h

# See Ollama model sizes
docker exec -it ollama ollama list
```

---

### Moria - NAS & Storage

# Moria - NAS & Storage

## Overview

Moria is the Synology NAS. It provides shared storage for the network, hosts the
UniFi controller, and serves as Tier 2 (long-term) backup storage.
Named after the great dwarf kingdom - an appropriate choice for the hoarder of data.

| Field | Value |
|---|---|
| Model | Synology DS1511+ |
| OS | DSM 6.2.4 |
| IP (NIC1) | 192.168.10.6 |
| IP (NIC2) | 192.168.10.7 |
| DNS | moria.lan / unifi.lan |
| Web UI | http://moria.lan:5000 |
| SSH | `ssh aule@moria.lan` (from palantir) |

## Shared Folders

| Folder | Path | Purpose |
|---|---|---|
| backups | /volume1/backups | Network and server config backups |
| homes | /volume1/homes | User home directories |
| docker | /volume1/docker | Docker container data (UniFi, Wyze) |

## Backup Structure on Moria

```
/volume1/backups/
??? network/
?   ??? mikrotik/     - MikroTik .rsc exports
?   ??? zyxel/        - Zyxel .cfg backups
?   ??? unifi/        - UniFi .unf backups
??? servers/
    ??? palantir/     - palantir home directory archives
    ??? rivendell/    - rivendell backups (TODO)
    ??? minastirith/
        ??? bookstack/
```

## UniFi Controller

The UniFi controller runs as a Docker container on Moria.

```bash
ssh aule@moria.lan

# Check status
docker ps | grep unifi

# Restart if needed
docker restart unifi

# View logs
docker logs unifi --tail 50
```

Web UI: http://192.168.10.:8080 or https://192.168.10.6:8443

UniFi autobackups stored at:
`/volume1/docker/UniFi/data/backup/autobackup/`

## SSH Access from palantir

palantir has passwordless SSH to moria via dedicated key:
```bash
ssh moria          # uses ~/.ssh/config alias
ssh aule@moria.lan # explicit
```

Key: `~/.ssh/id_moria` on palantir.

## rsync to Moria

Always use `--rsync-path` flag - required for Synology compatibility:
```bash
rsync -av -e "ssh -i /home/aule/.ssh/id_moria" \
  SOURCE \
  aule@192.168.10.6:DESTINATION \
  --rsync-path=/usr/bin/rsync
```

Without `--rsync-path`, rsync fails with permission denied even with a valid SSH key.

## Notes

- DSM 6.2.4 - older but stable. Upgrade path requires careful planning.
- NIC1 and NIC2 are separate interfaces, not bonded.
- Both NICs have static DHCP leases on VLAN10 (.6 and .7).
- Docker on Moria is minimal (UniFi + Wyze only). May be removed in future as
  services migrate fully to rivendell.
  Synology Drive Client
This is like private cloud (like Onedrive and Google drive). Like Onedrive, this creates replicated folders locally and synchs to Synology folders when connected. This is not required and sometimes can complicate things. But if you would like to set it up and use it, reference the following information.

Install Synology Drive Client
Download and install Synology Drive Client
Windows: Not found in Windows Store. Download from https://www.synology.com/en-us/support/download/DS1511+?version=6.2#system
Android: Google Play
iOS: Apple Store
Settings
Connection
Synology NAS: moria
Shared with me: Just use default folder location
Sync Tasks
My Drive
Syncs to your Home\drive 
famdocs
This is a family shared drive  
Team Folders
Tese are folders on moria that can be shared with the team. We have the following folders. All should be accessible to the group 'family'
famdoc
This is the common family folder where the following, but not limited to, are stored

keepass - all Keepass related stuff
software - software installation files
movie
Movies

music
Music

photo
Photos

usbshare1
An external drive connected to moria via usb connection. Used to backup photos.

video
Family videos

Miscellaneous
Marius Hosting
Marius Hosting has a number of websites that are very helpful for installing things on Synology Docker and others. He asks for donation in return for a password to various resources. 

Password
ThankYou

1/23/2026 
 Thanks for donating €5.00 EUR to
 LIXANDRU MARIUS-BOGDAN PERSOANA FIZICA AUTORIZATA
 
 Transaction ID: 40D6970016921554K

---

### Belagost (Buffalo Link NAS)

_No markdown content. This page was edited in WYSIWYG mode._

---

### Erebor (Dlink Sharecenter NAS)

_No markdown content. This page was edited in WYSIWYG mode._

---

### Home Assistant

## Home Assistant

| Field | Value |
|---|---|
| OS | Home Assistant OS |
| IP | 192.168.10.10 (static DHCP) |
| DNS | homeassistant.lan |
| Web UI | http://homeassistant.lan:8123 |
| External | Via Nabu Casa remote access |

Runs on dedicated hardware on VLAN10. Manages all smart home automations and device control.
See Book 7 — Smart Home for full documentation.

---

## Chapter: Other Machines

### Isengard

## Isengard — Recovery Assistant

| Field | Value |
|---|---|
| OS | Debian / XFCE |
| IP | DHCP dynamic |
| VLAN | 10 (trusted) normally; VLAN99 or emergency bridge during recovery |

Isengard's primary role is recovery support. It gets plugged into specific ports during
Zyxel or MikroTik recovery operations and given temporary static IPs.

During Zyxel recovery it sits on port 21 with a manual static IP (192.168.1.50)
to access the freshly reset Zyxel at its factory default address (192.168.1.1).

See Network book — Recovery Runbook for full usage.

---

### Palantir — Management Machine

# Palantir — Management Machine

## Overview

Palantir is the dedicated management machine. It lives permanently on VLAN99
and is required for any network recovery operation. It must always be on, always
on port 24, and always have WiFi disabled.

| Field | Value |
|---|---|
| OS | Debian / XFCE |
| IP | 192.168.99.21 (static DHCP) |
| DNS | palantir.lan |
| VLAN | 99 (management) |
| Physical port | Zyxel port 24 — never change |
| Interface | enp1s0 (wired), wlp2s0 (WiFi — always disabled) |

## Critical Rules

**WiFi must always be disabled.** If WiFi is active, SSH replies from VLAN10 machines
go out via WiFi instead of wired VLAN99, causing connections to hang after handshake.

```bash
# Check WiFi status
nmcli radio wifi

# Disable WiFi
sudo nmcli radio wifi off
```

**Wired interface must have metric 100.** Prevents routing preference for WiFi
if it accidentally becomes active.

Check: `ip route show` — should show `enp1s0` default route at metric 100.

Fix if wrong — edit `/etc/NetworkManager/system-connections/enp1s0.nmconnection`:
```
[ipv4]
route-metric=100
```
Then: `sudo systemctl restart NetworkManager`

## Key Software

| Software | Purpose |
|---|---|
| XFCE desktop | Browser access to Zyxel/MikroTik during recovery |
| rsyslog | Receives MikroTik syslog on UDP 514 |
| openssh-server | Accepts SSH tunnels from VLAN10 machines |
| rsync | Pushes backups to moria |

## Scripts and Backup Tools

```
/home/aule/
├── scripts/
│   ├── backup-mikrotik.sh    — automated MikroTik config backup
│   └── backup-palantir.sh    — automated palantir home dir backup
├── backups/
│   ├── mikrotik/latest/mikrotik-latest.rsc
│   ├── zyxel/latest/zyxel-latest.cfg
│   └── palantir/latest/palantir-latest.tar.gz
└── logs/
    └── backup/
```

## SSH Keys

| Key | Path | Purpose |
|---|---|---|
| id_moria | ~/.ssh/id_moria | Passwordless SSH/rsync to moria |
| id_mikrotik | ~/.ssh/id_mikrotik | Passwordless SSH to MikroTik as aule |

SSH config (`~/.ssh/config`):
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

## MikroTik Syslog

palantir runs rsyslog receiving MikroTik logs on UDP 514.
Logs written to `/var/log/mikrotik.log`. Rotation: weekly, 8 rotations kept.

```bash
# View recent MikroTik log entries
tail -50 /var/log/mikrotik.log

# Watch live
tail -f /var/log/mikrotik.log
```

## Restoring palantir After Fresh Debian Install

1. Install Debian, create aule user with sudo
2. `sudo apt install rsync openssh-server`
3. `sudo nmcli radio wifi off`
4. Get backup from moria or USB
5. Extract: `cd / && sudo tar -xzf palantir-latest.tar.gz`
6. Fix SSH key permissions:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/id_moria ~/.ssh/id_mikrotik
   chmod 644 ~/.ssh/id_moria.pub ~/.ssh/id_mikrotik.pub
   ```
7. Fix NetworkManager wired metric (see above)
8. Verify: `ssh moria echo ok` and `ssh mikrotik /quit`

---

### Minasmorgul

## Minasmorgul — Windows Management Machine\r
\r
| Field | Value |\r
|---|---|\r
| OS | Windows 11 Pro (22H2, build 22621) |\r
| IP | 192.168.10.16 (static DHCP) |\r
| DNS | minasmorgul.lan |\r
| VLAN | 10 (trusted) |\r
| CPU | Intel Core i5-2520M @ 2.50 GHz (2C/4T) |\r
| RAM | 8 GB |\r
| Storage | Unknown (no SSD detected — likely HDD) |\r
| Network | Intel 82579LM Gigabit — 1 Gbps |\r
| Users | aule, sung.us@outlook.com |\r
\r
Primary management machine. Used for network admin (SSH tunnel to palantir for Zyxel\r
and MikroTik UI), BookStack export/upload scripts, and general Windows tasks.\r\nHas SSH tunnel configured to palantir for Zyxel and\r
MikroTik UI access from VLAN10.\r
\r
SSH config (`C:\Users\aule\.ssh\config` and `C:\Users\sungu\.ssh\config`):\r
```\r
Host palantir\r
    HostName 192.168.99.21\r
    User aule\r
    LocalForward 8080 192.168.99.2:80\r
    LocalForward 8081 192.168.99.1:80\r
```\r
\r
Usage: `ssh palantir` (keep window open), then browse http://localhost:8080 (Zyxel)\r
and http://localhost:8081 (MikroTik).

---

### Osgiliath

## Osgiliath — Windows Workstation

| Field | Value |
|---|---|
| OS | Windows 11 Pro (Insider, build 26200) |
| IP | 192.168.10.20 (dynamic DHCP) |
| CPU | Intel Core i5-8350U @ 1.70 GHz (4C/8T) |
| RAM | 8 GB |
| Storage | Samsung MZVLW256HEHP-000H1 NVMe SSD (238 GB) |
| Network | Dell Gigabit Ethernet — 1 Gbps |
| VLAN | 10 (trusted) |

General-purpose Windows workstation. Better suited than Minasmorgul for CPU-intensive tasks — the i5-8350U has twice the cores/threads and a faster NVMe SSD.

---
