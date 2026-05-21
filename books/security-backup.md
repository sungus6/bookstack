# Security & Backup
> Exported from BookStack on 2026-05-21
> Slug: security-backup

---

## Contents

- Backup Strategy & Schedule
- Machine-Level Backups
- SSH Keys & Access
- Credentials

---

### Backup Strategy & Schedule

Arda uses a layered backup approach: local storage on Moria, with machines backing up to their own local targets and a central anchor on palantir.

#### Three-Layer Strategy

1. **Local snapshots** — each machine keeps its own recent data
2. **Network backups** — machines back up critical data to Moria nightly
3. **Palantir anchor** — palantir aggregates and validates backups

#### Backup Schedule

| Machine | What's Backed Up | Target | Frequency |
|---------|-----------------|--------|-----------|
| Rivendell | Docker compose files, configs, databases | Moria `/volume1/backups/` | Nightly |
| Moria | Critical shared folders | Cross-volume sync | Weekly manual |
| Palantir | Home dir, MikroTik config | Local + Moria | Nightly |
| Home Assistant | Full config | Built-in backup | On config change |
| MikroTik | RouterOS config | Palantir | On config change |

#### Backup Locations on Moria

```
/volume1/backups/
├── rivendell/        # Docker configs, DB dumps, compose files
├── palantir/         # Palantir home dir backups
└── network/          # Router configs, VLAN configs
```

---

### Machine-Level Backups

#### Rivendell Backup

Rivendell's backup script runs nightly via cron. It covers:
- Docker compose files and config
- BookStack database dump
- Key application configs
- Container volume data (where practical)

Manual backup:
```bash
# SSH to Rivendell
ssh aule@rivendell.lan

# Backup is managed via cron — check status
ls -la /mnt/work/ai-stack/backups/
```

#### Moria (NAS) Backup

Moria stores the backups of other machines. Moria itself should have its critical shared folders periodically synced for redundancy.

| Shared Folder | Location | Redundancy |
|--------------|----------|------------|
| Backups | /volume1/backups/ | SHR (Synology Hybrid RAID) |
| Homes | /volume1/homes/ | SHR |

#### Palantir Backup

Palantir is the management anchor. It holds:
- Local copies of backups
- MikroTik and Zyxel config exports
- SSH keys for VLAN99 access

Backups from palantir go to Moria nightly via rsync.

```bash
# Manual rsync to Moria
rsync -av -e "ssh -i ~/.ssh/id_moria" \
  /home/aule/backups/ \
  aule@192.168.10.6:/volume1/backups/palantir/ \
  --rsync-path=/usr/bin/rsync
```

#### Home Assistant Backup

Create a full backup through the UI:
```
Settings → System → Backups → Create Backup
```

Backups include configuration, automations, scenes, scripts, dashboards, and add-on data.

#### MikroTik Backup

RouterOS config backup is done through Winbox or CLI:
```
/system backup save name=arda-config-YYMMDD
```

The `.backup` file can be uploaded to palantir. For recovery, upload back to the MikroTik and use Restore.
For password-less restore, `/export` the config to a `.rsc` file — this is human-readable and can be edited.

---

### SSH Keys & Access

#### Key Distribution

| Key | Used For | Location |
|-----|----------|----------|
| `id_ed25519_hermes` | Aulë (Hermes) → Rivendell SSH | Hermes container |
| `id_moria` | Palantir → Moria rsync | Palantir |
| `id_ed25519` (personal) | User → Rivendell | Authorized keys on Rivendell |

Authorized keys on each machine define who can SSH in.

#### Access Paths

**VLAN10 → Rivendell:**
```bash
ssh aule@rivendell.lan          # Direct from VLAN10
ssh aule@192.168.10.4           # IP also works
```

**VLAN10 → Moria:**
```bash
ssh aule@moria.lan              # Direct from VLAN10
```

**VLAN10 → VLAN99 (palantir):**
```bash
ssh aule@192.168.99.21          # Specially allowed through firewall
```

From palantir, you can reach MikroTik and Zyxel directly on VLAN99.

---

### Credentials

#### Password Architecture

All Arda credentials follow one rule: **the Sung KeePass DB is the single source of truth.**

What this means:
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
