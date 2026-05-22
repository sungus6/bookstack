# Security & Access
> Slug: security-backup

---

## Contents

- SSH Keys & Access
- Credentials

---

### SSH Keys & Access

#### Key Distribution

| Key | Used For | Location |
|-----|----------|----------|
| id_ed25519_hermes | Aule (Hermes container) to Rivendell host SSH | /opt/data/.ssh/ on Hermes |
| id_moria | Palantir to Moria SSH (backup push) | /home/aule/.ssh/ on palantir |
| id_mikrotik | Palantir to MikroTik SSH (config export) | /home/aule/.ssh/ on palantir |
| id_rivendell | Palantir to Rivendell SSH (config rsync) | /home/aule/.ssh/ on palantir |
| id_ed25519 (personal) | User to Rivendell direct SSH | Users ~/.ssh/ |

#### Access Paths

**From the internet (Noah, Jacob):**
```
ssh aule@192.168.10.4    # Connect via Cloudflare WARP first, then SSH to internal IPs
ssh aule@192.168.99.21   # Palantir similarly via WARP
```

No direct SSH is exposed via Cloudflare Tunnel. WARP acts as the VPN layer.

**From Aule (Hermes container SSH chain):**
```
# Hermes to Rivendell host:
ssh -i /opt/data/.ssh/id_ed25519_hermes aule@172.18.0.1

# Hermes to Rivendell to Palantir:
ssh -i /opt/data/.ssh/id_ed25519_hermes aule@172.18.0.1 \
  "ssh aule@192.168.99.21 <command>"

# Hermes to Rivendell to Palantir to Moria:
ssh -i /opt/data/.ssh/id_ed25519_hermes aule@172.18.0.1 \
  "ssh aule@192.168.99.21 'ssh -i ~/.ssh/id_moria aule@192.168.10.6 <command>'"
```

---

### Credentials

All Arda credentials follow one rule: **the Sung KeePass DB is the single source of truth.**

- Every password, API key, and token is stored in the KeePass DB
- No passwords are in this wiki, in chat logs, or in plain config files
- If you need a credential, it is in KeePass

#### What is in the KeePass DB

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

The MikroTik emergency bridge (192.168.88.0/24) has a fixed admin password for recovery when KeePass is not accessible.

This password is **not documented here** -- it is on the physical MikroTik unit and in KeePass.

---
