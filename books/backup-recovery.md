# Backup & Recovery
> Exported from BookStack on 2026-05-14
> Slug: backup-recovery

---

## Contents

- Backup & Recovery Overview
- Backup Procedures
- Restore Procedures
- Disaster Recovery Scenarios
- Restore Testing

---

### Backup & Recovery Overview

# Backup & Recovery Overview

## Philosophy

**Two tiers, always.** Local on palantir for fast recovery during network outages,
remote on moria for redundancy and long-term retention.

**palantir is the anchor.** It is always on VLAN99, always reachable during any
network recovery. If moria is unreachable, palantir's local copy is what you use.

**No untested backups.** A backup that has never been restored is a hope, not a plan.
Run restore tests periodically (see Restore Testing section).

## What's Backed Up

| Component | Method | Where | Frequency |
|---|---|---|---|
| MikroTik config | Automated script | palantir + moria | On-demand / weekly |
| Zyxel config | Manual download | palantir + moria | After each change |
| palantir home dir | Automated script | palantir + moria | On-demand / weekly |
| UniFi | Built-in autobackup | moria autobackup folder | Automatic |
| Home Assistant | Built-in backup | HA local + moria | Manual / periodic |
| Rivendell | TODO | Not yet implemented | — |
| BookStack content | Export scripts (minasmorgul) | C:\bookstack-update\exports\ | On-demand |

## Backup Locations

**On palantir (always accessible during recovery):**
```
/home/aule/backups/
├── mikrotik/latest/mikrotik-latest.rsc
├── mikrotik/archive/mikrotik-YYYYMMDD.rsc
├── zyxel/latest/zyxel-latest.cfg
├── zyxel/archive/zyxel-YYYYMMDD.cfg
└── palantir/latest/palantir-latest.tar.gz
```

**On moria (long-term storage):**
```
/volume1/backups/
├── network/mikrotik/
├── network/zyxel/
├── network/unifi/
└── servers/palantir/
```

## Priority During a Crisis

If multiple things are broken at once, recover in this order:

1. **MikroTik first** — without the router nothing else works
2. **Zyxel second** — without switching, VLANs don't work
3. **palantir** — needed for management access
4. **UniFi** — WiFi, but wired still works without it
5. **Rivendell services** — AI, BookStack, etc. can wait

Full recovery runbooks are in the Network book.

---

### Backup Procedures

# Backup Procedures

## MikroTik Backup (Automated)

Run from palantir:
```bash
/home/aule/scripts/backup-mikrotik.sh
cat /home/aule/logs/backup/backup-mikrotik.log
```

The script:
1. SSH to MikroTik and runs `/export file=mikrotik-backup-DATE`
2. SCP file to palantir archive and latest folders
3. Pushes to moria via rsync

**Run this after any MikroTik config change.**

## Zyxel Backup (Manual)

The Zyxel has no CLI/API — backup is manual only.

1. Open http://192.168.99.2 on palantir browser
2. Maintenance -> Configuration -> Source: Running Configuration, Method: HTTP
3. File downloads to palantir Downloads folder
4. Move to archive:
   ```bash
   cp ~/Downloads/zyxel-YYYYMMDD.cfg ~/backups/zyxel/archive/zyxel-YYYYMMDD.cfg
   cp ~/backups/zyxel/archive/zyxel-YYYYMMDD.cfg ~/backups/zyxel/latest/zyxel-latest.cfg
   ```
5. Push to moria:
   ```bash
   rsync -av -e "ssh -i /home/aule/.ssh/id_moria" \
     ~/backups/zyxel/archive/zyxel-YYYYMMDD.cfg \
     aule@192.168.10.6:/volume1/backups/network/zyxel/zyxel-YYYYMMDD.cfg \
     --rsync-path=/usr/bin/rsync
   ```

**Run this after every Zyxel config change.**

## palantir Backup (Automated)

```bash
/home/aule/scripts/backup-palantir.sh
```

Archives entire home directory excluding logs and downloads.
Includes: scripts, SSH keys, backup READMEs, configs.

## UniFi Backup

UniFi auto-backups run automatically at:
`/volume1/docker/UniFi/data/backup/autobackup/`

For manual backup: UniFi controller -> System Settings -> Backup -> Download Backup.
Store .unf files at `/volume1/backups/network/unifi/`.

## Home Assistant Backup

From HA web UI: Settings -> System -> Backups -> Create Backup.

Download the backup file and copy to moria:
```bash
# Copy .tar file from HA to moria
rsync -av -e "ssh -i /home/aule/.ssh/id_moria" \
  /path/to/homeassistant-backup.tar \
  aule@192.168.10.6:/volume1/backups/servers/homeassistant/ \
  --rsync-path=/usr/bin/rsync
```

## BookStack Content Backup

From minasmorgul, run the export script:
```powershell
cd C:\bookstack-update\scripts
.\export-bookstack.ps1
```

Exports all books as markdown files to `C:\bookstack-update\exports\`.

---

### Restore Procedures

# Restore Procedures

## MikroTik Restore

**From palantir (VLAN99 working):**
```bash
scp /home/aule/backups/mikrotik/latest/mikrotik-latest.rsc mikrotik:mikrotik-latest.rsc
ssh mikrotik
/import file=mikrotik-latest.rsc
```

**Via emergency bridge (after factory reset):**
```bash
# On isengard connected to ether5-EMERGENCY
sudo ip addr add 192.168.88.50/24 dev enp1s0
sudo ip route add default via 192.168.88.1
scp /home/aule/backups/mikrotik/latest/mikrotik-latest.rsc admin@192.168.88.1:mikrotik-latest.rsc
ssh admin@192.168.88.1
/import file=mikrotik-latest.rsc
```

After import, always verify:
```
/interface list member print
```
See Network book Recovery Runbook for full procedure.

## Zyxel Restore

1. Open Zyxel UI (http://192.168.99.2 from palantir, or http://192.168.1.1 after factory reset)
2. Maintenance -> Configuration -> Source: [backup file] -> Destination: Running Configuration
3. After factory reset: complete the full Zyxel recovery runbook FIRST, then restore

See Network book Recovery Runbook Part 2 for the full factory reset procedure.

## palantir Restore (Fresh Debian Install)

1. Install Debian, create aule user with sudo
2. `sudo apt install rsync openssh-server`
3. `sudo nmcli radio wifi off`
4. Get backup from moria or USB drive
5. Extract: `cd / && sudo tar -xzf palantir-latest.tar.gz`
6. Fix SSH key permissions:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/id_moria ~/.ssh/id_mikrotik
   chmod 644 ~/.ssh/id_moria.pub ~/.ssh/id_mikrotik.pub
   ```
7. Fix NetworkManager wired metric (route-metric=100 in enp1s0 connection file)
8. Verify: `ssh moria echo ok` and `ssh mikrotik /quit`

## UniFi Restore

1. Open UniFi controller: http://192.168.10.4:8080
2. System Settings -> Backup -> Restore -> upload .unf file
3. After restore verify wintermute SSID is set to Default network (NOT Trusted/VLAN10)
4. If APs need re-adoption: `ssh ubnt@AP_IP` then `set-inform http://192.168.10.4:8080/inform`

## Home Assistant Restore

Settings -> System -> Backups -> upload backup .tar file -> Restore.

HA will restart during restore. Give it a few minutes to come back online.

## BookStack Restore (from markdown files)

From minasmorgul, copy updated files to staging and upload:
```powershell
cd C:\bookstack-update\scripts
.\upload-bookstack.ps1 -DryRun   # preview first
.\upload-bookstack.ps1           # upload
```

---

### Disaster Recovery Scenarios

# Disaster Recovery Scenarios

## Scenario 1 — Router Dead (MikroTik hardware failure)

**Impact:** No internet, no inter-VLAN routing, no DHCP for anything.

**Recovery:**
1. Replace MikroTik hardware with another RB750GL (or compatible model)
2. Connect isengard to ether5-EMERGENCY with static IP 192.168.88.50/24
3. SSH to 192.168.88.1 as admin
4. Restore from backup: `scp` the .rsc file, `/import file=mikrotik-latest.rsc`
5. Verify interface list members
6. Verify DHCP, DNS, firewall rules

**Backup needed:** `mikrotik-latest.rsc` from palantir or moria.

## Scenario 2 — Switch Dead (Zyxel hardware failure)

**Impact:** No switching, no VLANs, most devices offline.

**Recovery:**
1. Replace with another GS1900-24HP (same model strongly recommended)
2. Follow the full Zyxel recovery runbook from Network book
3. Restore config from .cfg backup
4. palantir must be on port 24 throughout

**Backup needed:** `zyxel-latest.cfg` from palantir or moria.

## Scenario 3 — palantir Dead (management machine failure)

**Impact:** No management access to MikroTik/Zyxel from network, no SSH tunnel, no backup scripts.

**Recovery:**
1. Plug isengard into port 24 temporarily for emergency management access
2. Set isengard static IP to 192.168.99.21 temporarily: `sudo ip addr add 192.168.99.21/24 dev enp1s0`
3. SSH to MikroTik and Zyxel to verify network health
4. Restore palantir on replacement hardware from backup (see Restore Procedures)
5. Move backup back to port 24 and remove isengard

**Backup needed:** `palantir-latest.tar.gz` from moria.

## Scenario 4 — Rivendell Dead (server hardware failure)

**Impact:** No BookStack, no AI/Aule, no Grafana, no Cloudflared (no external access).

**Recovery:**
1. Install Ubuntu 24.04 LTS on replacement hardware
2. Install Docker and Docker Compose
3. Restore stack configs from backup (once rivendell backup is implemented)
4. Restore BookStack data and database
5. Start all stacks: `docker compose up -d` in each stack directory
6. Verify Cloudflare tunnel reconnects

**Temporary workaround while rebuilding:**
- BookStack content is exported to `C:\bookstack-update\exports\` on minasmorgul
- Aule can fall back to using only cloud APIs (OpenAI/Anthropic) without local Ollama

## Scenario 5 — Moria Dead (NAS failure)

**Impact:** Loss of long-term backup storage. Local backups on palantir still intact.

**Recovery:**
1. Replace or repair Moria hardware
2. Re-create backup folder structure on new volume
3. Rsync local palantir backups to new Moria
4. Re-point UniFi Docker container to new volume path if needed

**Note:** DSM 6.2.4 is old — if replacing Moria hardware, consider upgrading to
a newer Synology model with a supported DSM version.

---

### Restore Testing

# Restore Testing

## Why Test Restores

An untested backup is a hope, not a plan. Backups must be verified periodically
to ensure they are complete, uncorrupted, and can actually be used for recovery.

## Testing Schedule

| Component | Test Frequency | Method |
|---|---|---|
| MikroTik config | Quarterly | Import to test MikroTik or verify file integrity |
| Zyxel config | After each backup | Verify file is non-zero and parseable |
| palantir backup | Quarterly | Extract to /tmp and verify key files present |
| UniFi backup | Semi-annually | Restore to test controller instance |
| BookStack | Monthly | Run export, verify page count matches live |

## MikroTik Config Verification

```bash
# On palantir
# Verify backup file exists and is non-empty
ls -la ~/backups/mikrotik/latest/mikrotik-latest.rsc

# Verify it looks like a valid MikroTik export (check first few lines)
head -20 ~/backups/mikrotik/latest/mikrotik-latest.rsc

# Should start with:
# # RouterOS configuration export
# /interface ...
```

## palantir Backup Verification

```bash
# Verify archive exists and is non-empty
ls -lh ~/backups/palantir/latest/palantir-latest.tar.gz

# List contents (don't extract -- just verify structure)
tar -tzf ~/backups/palantir/latest/palantir-latest.tar.gz | head -30

# Verify key files are present
tar -tzf ~/backups/palantir/latest/palantir-latest.tar.gz | grep -E "ssh|scripts|backups"
```

## BookStack Export Verification

From minasmorgul:
```powershell
# Run export
.\export-bookstack.ps1

# Count files exported
Get-ChildItem C:\bookstack-update\exports\ -Filter "*.md" | Measure-Object | Select-Object Count

# Verify file sizes are non-zero
Get-ChildItem C:\bookstack-update\exports\ -Filter "*.md" | Where-Object Length -eq 0
# Should return nothing (no zero-byte files)
```

## Log Review

Check backup logs regularly for failures:
```bash
# On palantir
cat /home/aule/logs/backup/backup-mikrotik.log
cat /home/aule/logs/backup/backup-palantir.log
```

Look for lines containing ERROR or FAILED.

---
