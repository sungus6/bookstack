# Security & Backup
> Exported from BookStack on 2026-05-22
> Slug: security-backup

---

## Contents

- Backup Architecture Overview
- Backup Schedule
- Backup Locations on Moria
- Recovery Procedures
- SSH Keys & Access
- Credentials

---

### Backup Architecture Overview

Arda uses a **palantir-orchestrated, Moria-stored** backup system.

**palantir** (Debian, 192.168.99.21) is the orchestrator. It runs `/home/aule/scripts/backup-arda.sh` daily at 3 AM CDT, which collects from every machine and pushes to Moria.

**Moria** (Synology, 192.168.10.6) is the central backup target at `/volume1/backups/`. It uses SHR (Synology Hybrid RAID) for redundancy.

#### What Gets Backed Up

| Component | Method | Size | Target on Moria |
|-----------|--------|------|----------------|
| **MikroTik** | SSH export → .rsc | ~16 KB | /volume1/backups/network/mikrotik/ |
| **Zyxel GS1900** | HTTP download → .cfg | ~4 KB | /volume1/backups/network/zyxel/ |
| **Rivendell configs** | rsync → tar.gz (excludes .git, ollama models, grafana plugins, unifi logs) | ~960 MB | /volume1/backups/servers/rivendell/ |
| **BookStack DB** | docker exec mysqldump | ~2.7 MB | /volume1/backups/servers/rivendell/ |
| **UniFi** | rsync autobackup .unf files | ~15 MB | /volume1/backups/network/unifi/ |
| **Palantir home** | tar archive | ~240 MB | /volume1/backups/servers/palantir/ |

#### What Is NOT Backed Up (By Design)

- Ollama models (~21 GB) — redownloadable
- Docker images — pulled fresh on `docker compose up -d`
- Prometheus metrics history — expendable, low priority
- arda-voice Python deps + Whisper — rebuildable from Dockerfile

#### Retention

- **Local (palantir):** 30 days — archives older than 30 days are deleted
- **Moria:** indefinite — NAS disk management handles space

---

### Backup Schedule

| Time (CDT) | Machine | Script | Trigger |
|------------|---------|--------|---------|
| 3:00 AM daily | MikroTik → Moria | backup-arda.sh | cron on palantir |
| 3:00 AM daily | Zyxel → Moria | backup-arda.sh | cron on palantir |
| 3:00 AM daily | Rivendell configs + DB → Moria | backup-arda.sh | cron on palantir |
| 3:00 AM daily | UniFi backups → Moria | backup-arda.sh | cron on palantir |
| 3:00 AM daily | Palantir home → Moria | backup-arda.sh | cron on palantir |
| 3:00 AM daily | USB essentials | backup-arda.sh | cron on palantir |
| 8:00 AM daily | Health check report | Hermes cron (b4aead877c10) | Aulë → Telegram + Discord |

---

### Backup Locations on Moria

```
/volume1/backups/
├── network/
│   ├── mikrotik/mikrotik-YYYYMMDD.rsc
│   ├── zyxel/zyxel-YYYYMMDD.cfg
│   └── unifi/
│       └── autobackup/    (UniFi .unf files)
└── servers/
    ├── rivendell/
    │   ├── rivendell-configs-YYYYMMDD.tar.gz
    │   └── rivendell-bookstack-db-YYYYMMDD.sql.gz
    └── palantir/
        └── palantir-YYYYMMDD.tar.gz
```

---

### Recovery Procedures

#### Restore Rivendell (SSD Failure — Full Rebuild)

1. Install Debian, configure Docker. Images pull fresh.
2. Copy `/volume1/backups/servers/rivendell/rivendell-configs-latest.tar.gz` to the new machine.
3. Extract:
   ```bash
   tar -xzf rivendell-configs-latest.tar.gz
   ```
4. This gives you all compose files, .env files, configs, and config files.
5. Run `docker compose up -d` in each stack directory.
6. Restore BookStack DB:
   ```bash
   gunzip < rivendell-bookstack-db-latest.sql.gz | docker exec -i bookstack_db mysql bookstackapp
   ```

#### Restore MikroTik

Copy `.rsc` from Moria or palantir, upload to MikroTik, and import:
```bash
/file import mikrotik-YYYYMMDD.rsc
```

#### Restore UniFi

Use the controller UI at `https://192.168.10.6:8443`:
- System Settings → Backup → Restore
- Upload the .unf file from `/volume1/backups/network/unifi/`

---

### SSH Keys & Access

#### Key Distribution

| Key | Used For | Location |
|-----|----------|----------|
| `id_ed25519_hermes` | Aulë (Hermes container) → Rivendell host SSH | /opt/data/.ssh/ on Hermes |
| `id_moria` | Palantir → Moria SSH (backup push) | /home/aule/.ssh/ on palantir |
| `id_mikrotik` | Palantir → MikroTik SSH (config export) | /home/aule/.ssh/ on palantir |
| `id_rivendell` | Palantir → Rivendell SSH (config rsync) | /home/aule/.ssh/ on palantir |
| `id_ed25519` (personal) | User → Rivendell direct SSH | Users' ~/.ssh/ |

#### Access Paths

**From the internet (Noah, Jacob):**
```bash
# Connect via Cloudflare WARP, then SSH to internal IPs
ssh aule@192.168.10.4    # Rivendell
ssh aule@192.168.99.21   # Palantir (via jump host if needed)
```

No direct SSH is exposed via Cloudflare Tunnel.

**From Aulë (Hermes container):**
```bash
# Hermes → Rivendell host
ssh -i /opt/data/.ssh/id_ed25519_hermes aule@172.18.0.1

# Hermes → Rivendell → Palantir
ssh -i /opt/data/.ssh/id_ed25519_hermes aule@172.18.0.1 \
  "ssh aule@192.168.99.21 <command>"

# Hermes → Rivendell → Palantir → Moria
ssh -i /opt/data/.ssh/id_ed25519_hermes aule@172.18.0.1 \
  "ssh aule@192.168.99.21 'ssh -i ~/.ssh/id_moria aule@192.168.10.6 <command>'"
```

#### Automated Backup Scripts

All backup scripts live on **palantir** at `/home/aule/scripts/`:

| Script | Purpose | Last Updated |
|--------|---------|-------------|
| `backup-arda.sh` | **Master orchestrator** — runs all phases | May 22, 2026 |
| `backup-mikrotik.sh` | MikroTik export (legacy sub-script) | May 2026 |
| `backup-rivendell.sh` | Rivendell backup (legacy sub-script) | May 2026 |
| `backup-palantir.sh` | Palantir self-backup (legacy sub-script) | May 2026 |

The scripts are version-controlled in a git repo at `/mnt/work/backups/scripts/` on Rivendell.

---

### Credentials

All Arda credentials follow one rule: **the Sung KeePass DB is the single source of truth.**

- **Every password, API key, and token** is stored in the KeePass DB
- **No passwords** are in this wiki, in chat logs, or in plain config files
- If you need a credential, it's in KeePass

#### What's in the KeePass DB

- Wi-Fi passwords (wintermute, neuromancer)
- Service logins (BookStack, Grafana, Portainer, Home Assistant)
- External accounts (Cloudflare, Xfinity, domain registrar)
- SSH private keys
- Docker registries
- API tokens (Cloudflare, OpenAI, Claude, Home Assistant)
- Email accounts and passwords

#### Getting Access

Ask Dan, Noah, or Jacob for access to the Sung KeePass DB.

#### One Exception: Emergency Bridge Network

The MikroTik emergency bridge (192.168.88.0/24) has a fixed admin password. This allows recovery even when the KeePass DB isn't accessible.

This password is **not documented here** — it's on the physical MikroTik unit and in the Sung KeePass DB.

---
