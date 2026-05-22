# Backup & Recovery
> Slug: backup-recovery

---

## Contents

- Backup Architecture
- Recovery Runbooks
- Verifying Backup Health

---

### Backup Architecture

Arda has a centralized backup system. **palantir** (a Debian machine on VLAN99) orchestrates all backups daily at 3 AM CDT and pushes everything to **Moria** (the Synology NAS on VLAN10).

#### Why This Design

- **palantir** can reach every machine on both VLANs — MikroTik and Zyxel on VLAN99, Rivendell and Moria on VLAN10
- **Moria** has SHR RAID (survives single disk failure) and 5.7 TB free — it's the safest place to store data
- Each machine also keeps local copies on palantir's disk (208 GB free, 30-day retention) as a second layer
- A USB disk on Moria gets the most critical essentials for catastrophic scenarios

#### The Data Flow

```
palantir (orchestrator, 192.168.99.21)
  |
  +-- SSH over VLAN99 --> MikroTik (192.168.99.1)
  |     export config -> .rsc
  |     local archive (30d) + rsync -> Moria
  |
  +-- HTTP over VLAN99 --> Zyxel (192.168.99.2)
  |     download config -> .cfg
  |     local archive (30d) + rsync -> Moria
  |
  +-- SSH over VLAN10 --> Rivendell (192.168.10.4)
  |     docker exec mysqldump -> BookStack.sql.gz
  |     rsync /mnt/work/ -> tar.gz (excludes .git, ollama, grafana plugins, unifi logs)
  |     rsync unifi autobackup dir
  |     local archive (30d) + rsync -> Moria
  |
  +-- tar /home/aule/ -> palantir backup
  |     local archive (30d) + rsync -> Moria
  |
  +-- USB disk (/usbshare1/) if mounted
        copy latest essentials
```

#### What Gets Backed Up and What Doesnt

| Component | Backup Method | Size on Moria | Restore Method |
|-----------|--------------|---------------|----------------|
| **Rivendell configs** | rsync all compose stacks + .env + configs -> tar.gz | ~960 MB | Extract, docker compose up -d |
| **BookStack DB** | docker exec mysqldump | ~2.7 MB | mysql import |
| **MikroTik config** | SSH /export -> .rsc | ~16 KB | /file import on MikroTik |
| **Zyxel config** | HTTP download -> .cfg | ~4 KB | Upload via web UI |
| **UniFi backups** | rsync autobackup .unf files | ~15 MB | Restore via UniFi controller |
| **Palantir home dir** | tar /home/aule/ | ~240 MB | Extract on new machine |

**NOT backed up (by design):**
- Ollama models (~21 GB) -- just re-download with `ollama pull`
- Docker container images -- `docker compose up -d` pulls fresh
- Prometheus metrics history -- low value
- Whisper/voice model files -- rebuild from Dockerfile

#### Where Everything Lives on Moria

```
/volume1/backups/
+-- network/
|   +-- mikrotik/mikrotik-YYYYMMDD.rsc
|   +-- zyxel/zyxel-YYYYMMDD.cfg
|   +-- unifi/autobackup/autobackup_*.unf
+-- servers/
    +-- rivendell/
    |   +-- rivendell-configs-YYYYMMDD.tar.gz
    |   +-- rivendell-bookstack-db-YYYYMMDD.sql.gz
    +-- palantir/
        +-- palantir-YYYYMMDD.tar.gz
```

Each run writes dated files with YYYYMMDD suffix. Moria keeps everything indefinitely. palantir prunes local copies over 30 days old.

#### The Master Script

A single script on palantir runs everything:

**Location:** `/home/aule/scripts/backup-arda.sh`

**Execution order:**
1. Check Moria is reachable (aborts remote push if not, continues locally)
2. Export MikroTik config to local + Moria
3. Download Zyxel config to local + Moria
4. Dump BookStack DB from Rivendell to local + Moria
5. Rsync Rivendell /mnt/work/ -> tar.gz -> local + Moria
6. Sync UniFi autobackups -> local + Moria
7. Archive palantir home -> local + Moria
8. Copy latest essentials to USB disk (if mounted)
9. Prune local archives > 30 days old

**Scheduled via crontab on palantir:**
```
0 3 * * * bash /home/aule/scripts/backup-arda.sh
```

**Version control:** Git repo at `/mnt/work/backups/scripts/` on Rivendell.

#### Daily Health Check

Every morning at 8AM CDT, Aule sends a backup health report to the Telegram Home channel and Discord #general. It looks like:

All MikroTik configs on Moria
All BookStack DB dumps on Moria
All Rivendell configs on Moria (963 MB)
All Palantir home on Moria

Status: ALL GOOD

If anything failed, the message says ISSUES FOUND and highlights what to check.

#### Retention & Pruning

- palantir (local): 30 days -- older archives auto-deleted
- Moria: indefinite -- 5.7 TB free, disk management via DSM
- USB: latest essential files only, no history

---

### Recovery Runbooks

#### Rivendell SSD Dies (Full Rebuild)

Worst case: Rivendells SSD is dead and needs a fresh Debian install. This restores every service.

**Prerequisites:** Access to Moria's /volume1/backups/ either via SSH from palantir or the Synology web UI.

**Steps:**

1. Install Debian 12 on the new SSD with Docker

   ```
   apt update && apt install -y docker.io docker-compose-v2 git
   ```

2. Get the latest backup files from Moria

   ```
   # From the new machine or from palantir
   scp aule@192.168.10.6:/volume1/backups/servers/rivendell/rivendell-configs-latest.tar.gz .
   scp aule@192.168.10.6:/volume1/backups/servers/rivendell/rivendell-bookstack-db-latest.sql.gz .
   ```

3. Extract configs into place

   ```
   mkdir -p /mnt/work
   tar -xzf rivendell-configs-latest.tar.gz -C /mnt/work/
   ```

4. Start each Docker stack

   ```
   cd /mnt/work/ai-stack && docker compose up -d
   cd /mnt/work/network-stack && docker compose up -d
   # Repeat for any other stacks under /mnt/work/
   ```

5. Restore BookStack database

   ```
   gunzip < rivendell-bookstack-db-latest.sql.gz | docker exec -i bookstack_db mysql -u root -p"$DB_PASSWORD" bookstackapp
   ```

6. Restore UniFi via its controller UI at https://newip:8443
   - System Settings -> Backup -> Restore
   - Pick the .unf file from /volume1/backups/network/unifi/autobackup/

7. Re-establish the backup chain from palantir

   ```
   ssh aule@192.168.99.21
   ssh-copy-id -i ~/.ssh/id_rivendell aule@192.168.10.4
   ssh aule@192.168.10.4 "echo ok" # verify
   ```

#### palantir Dies (Debian Rebuild)

Whats lost: the backup scripts (in git), SSH keys to MikroTik/Moria/Rivendell, the crontab, and local 30-day archive cache (Moria still has the long-term copies).

**Steps:**

1. Install Debian + XFCE on the new palantir
2. Grab scripts from the git repo on Rivendell

   ```
   # From palantir, if SSH to Rivendell is possible (use password if needed)
   scp -r aule@192.168.10.4:/mnt/work/backups/scripts /home/aule/
   ```
   Or read each file individually:
   ```
   ssh aule@192.168.10.4 "cat /mnt/work/backups/scripts/backup-arda.sh" > /home/aule/scripts/backup-arda.sh
   # Repeat for backup-mikrotik.sh, backup-rivendell.sh, backup-palantir.sh
   chmod +x /home/aule/scripts/*.sh
   ```

3. Regenerate SSH keys. The authorized keys on each target machine need to be updated:

   ```
   ssh-keygen -t ed25519 -f ~/.ssh/id_moria
   ssh-keygen -t ed25519 -f ~/.ssh/id_mikrotik
   ssh-keygen -t ed25519 -f ~/.ssh/id_rivendell
   ```

   **MikroTik** - add the new key:
   ```
   ssh-copy-id -i ~/.ssh/id_mikrotik admin@192.168.99.1
   ```

   **Rivendell** - add the new key:
   ```
   ssh-copy-id -i ~/.ssh/id_rivendell aule@192.168.10.4
   ```

   **Moria** - Synology DSM, no ssh-copy-id. Use the web UI:
   - Go to Control Panel > File Services > SSH keys
   - Or paste into `/volume1/homes/aule/.ssh/authorized_keys` via File Station

4. Set up SSH config

   ```
   cat > ~/.ssh/config << 'EOF'
   Host mikrotik
       HostName 192.168.99.1
       User admin
       IdentityFile ~/.ssh/id_mikrotik
   Host moria
       HostName 192.168.10.6
       User aule
       IdentityFile ~/.ssh/id_moria
   Host rivendell
       HostName 192.168.10.4
       User aule
       IdentityFile ~/.ssh/id_rivendell
   EOF
   ```

5. Set up crontab

   ```
   crontab -e
   # add: 0 3 * * * bash /home/aule/scripts/backup-arda.sh
   ```

6. Re-authorize Aules (Hermes) health check access

   ```
   # From Rivendell:
   ssh-copy-id -i /opt/data/.ssh/id_ed25519_hermes aule@192.168.99.21
   ```

#### Moria Dies (NAS Failure)

This is the worst single point of failure. Mitigations:

- palantir retains the last 30 days of archives on local disk
- The USB essentials disk has the latest configs and DB dumps
- The backup script detects Moria unreachable and continues locally (harmlessly failing the rsync step)

If Moria dies:
1. Fix or replace the NAS hardware first
2. Re-restore from palantir local archives once Moria is back
3. Run a manual backup to repopulate: `bash /home/aule/scripts/backup-arda.sh`

#### MikroTik Dies (Full Hardware Replacement)

1. Get latest config from Moria or palantir:

   ```
   # From palantir:
   scp moria:/volume1/backups/network/mikrotik/mikrotik-20260522.rsc .
   # Or local copy:
   cp /home/aule/backups/mikrotik/latest/mikrotik-latest.rsc .
   ```

2. Upload to new MikroTik:

   ```
   scp mikrotik-latest.rsc admin@192.168.88.1:/
   ```

3. On the MikroTik:

   ```
   /file import mikrotik-latest.rsc
   ```

#### BookStack Data Loss (Accidental Delete)

Restore just the database:

```
# On Rivendell:
scp aule@192.168.10.6:/volume1/backups/servers/rivendell/rivendell-bookstack-db-20260522.sql.gz /tmp/
gunzip < /tmp/rivendell-bookstack-db-20260522.sql.gz | docker exec -i bookstack_db mysql -u root -p"$DB_PASSWORD" bookstackapp
```

---

### Verifying Backup Health

#### Quick Check

If youre in the Telegram or Discord home channel, wait for the daily 8AM CDT backup report from Aule. If nothing appears by 8:15 AM, something may be wrong -- ask Dan.

#### Check via SSH to palantir

**Is the latest backup log clean?**

```
ssh aule@192.168.99.21
cat /home/aule/logs/backup/backup-arda-$(date +%Y%m%d).log | grep -E "Duration|COMPLETE|FAILED|WARNING"
```

Expected: Duration < 10 minutes, "COMPLETE" at end, no FAILED entries.

**Is data on Moria?**

```
ssh -i ~/.ssh/id_moria aule@192.168.10.6 \
  "find /volume1/backups/ -name \"*$(date +%Y%m%d)*\" -type f"
```

You should see files from today in every backup category.

**Disk space check:**

```
df -h /home/aule          # palantir local -- should have >60% free
ssh moria "df -h /volume1" # Moria -- 5.7 TB total
```

#### Check via Aule

Ask me directly:
- "Aule, check the backup health"
- "Aule, did the backup run last night?"

I will SSH through the chain and report full status.

#### Failure Symptoms Quick Reference

| Log Entry | Likely Cause | Fix |
|-----------|-------------|-----|
| MikroTik export FAILED | MikroTik down or SSH key expired | Check MikroTik, re-auth SSH key |
| Zyxel download FAILED | HTTP endpoint changed | Non-critical -- switch works without backup |
| BookStack DB dump FAILED | BookStack container not running | Run `docker restart bookstack_db` on Rivendell |
| Moria push FAILED | NAS unreachable or SSH broken | Check Moria, re-auth id_moria key |
| USB disk not found | USB not mounted at /usbshare1/ | Plug in USB or ignore |
| Rivendell unreachable | Host down or SSH broken | Fix Rivendell first |
| Palantir archive FAILED | Disk full | `df -h /home/aule`, free space |

---
