# Servers
> Slug: servers

---

## Contents

- Docker — Rivendell
- NAS — Moria
- NAS — Belegost
- NAS — Erebor
- Specialized Machines — Home Assistant
- Specialized Machines — palantir
- Specialized Machines — minasmorgul
- Specialized Machines — isengard

---

### Docker — Rivendell

Rivendell is the primary server in Arda. It runs all Docker-based workloads including the AI stack, BookStack wiki, monitoring, and external access.

#### Specs

| Field | Value |
|-------|-------|
| **OS** | Ubuntu 24.04 LTS |
| **IP** | 192.168.10.4 |
| **DNS** | rivendell.lan |
| **VLAN** | 10 (trusted) |
| **Access** | `ssh aule@rivendell.lan` |
| **GPU** | NVIDIA GTX 1060 6GB (local LLM inference) |

#### Docker Compose Layout

```
/mnt/work/
├── ai-stack/
│   └── docker-compose.yml      (ollama, litellm, hermes, grafana, prometheus)
├── infra-stack/
│   └── docker-compose.yml      (cloudflared, portainer)
└── book-stack/
    └── docker-compose.yml      (bookstack, bookstack_db)
```

#### Container Overview

All containers and their operations are documented in the **[Services](/books/services)** book (BookStack, Cloudflare Tunnel, Monitoring) and the **[AI](/books/ai)** book (AI stack).

| Container | Purpose | Docs |
|-----------|---------|------|
| bookstack, bookstack_db | Wiki | [Services](/books/services) |
| ollama, litellm, hermes | AI assistant stack | [AI](/books/ai) |
| prometheus, grafana | Monitoring | [Services](/books/services) |
| cloudflared | External access | [Services](/books/services) |
| portainer | Container management UI | [Services](/books/services) |

#### Compose Gotchas

- The grafana container in `ai-stack/` and the one in `infra-stack/` are the same container — the ai-stack compose includes it. Don't run both stacks simultaneously for grafana.

#### Backups

Rivendell is backed up nightly to Moria via automated script.

---

### NAS — Moria

Moria (Synology DS1511+) provides storage for the entire Arda network.

#### Specs

| Field | Value |
|-------|-------|
| **Model** | Synology DS1511+ |
| **OS** | DSM 6.2.4 |
| **IP** | 192.168.10.6 (NIC1), 192.168.10.7 (NIC2) |
| **DNS** | moria.lan |
| **VLAN** | 10 (trusted) |
| **Access** | SSH (aule@moria.lan) or DSM web UI (https://moria.lan:5001) |

#### Services

- **UniFi Controller** — runs as a Docker container on Moria (not Rivendell). URL: https://unifi.lan:8443
- **NFS shares** — mounted by Rivendell for Docker volume data, media, backups
- **Backup target** — nightly backups from Rivendell and other machines land here

#### Storage Layout

| Path | Purpose |
|------|---------|
| `/volume1/backups/` | Nightly backups from all machines |
| `/volume1/media/` | Shared media (music, photos, video) |
| `/volume1/docker/` | Docker volume data (exported via NFS) |

---

### NAS — Belegost

| Field | Value |
|-------|-------|
| **Model** | Older Synology |
| **Role** | Secondary storage / cold backups |

Older NAS unit still in service for secondary storage and cold backup retention.

---

### NAS — Erebor

| Field | Value |
|-------|-------|
| **Model** | Older Synology |
| **Role** | Media archive / secondary backup |

Older NAS unit used for media archive storage and as a secondary backup location.

---

### Specialized Machines — Home Assistant

Home Assistant runs on dedicated hardware and is the central hub for all smart home devices.

| Field | Value |
|-------|-------|
| **Host** | Dedicated hardware |
| **IP** | 192.168.10.10 |
| **Port** | 8123 |
| **Access** | Internal: http://192.168.10.10:8123, External: via Cloudflare tunnel |

Full smart home documentation (device inventory, automations, operations) is in the **[Smart Home](/books/smart-home)** book.

---

### Specialized Machines — palantir

palantir is the management workstation for administering Arda.

| Field | Value |
|-------|-------|
| **OS** | Windows 11 Pro |
| **VLAN** | 99 (management) |
| **IP** | 192.168.99.21 |
| **Role** | Management / admin workstation |
| **Access** | SSH keys, KeePass credential vault; RDP via Tailscale |

palantir has direct access to MikroTik (192.168.99.1) and Zyxel (192.168.99.2) management interfaces. For network admin procedures, see the **[Network](/books/network)** book.

---

### Specialized Machines — minasmorgul

minasmorgul is Manwë's personal Windows machine.

| Field | Value |
|-------|-------|
| **OS** | Windows 11 Pro |
| **VLAN** | 10 (trusted) |
| **IP** | 192.168.10.16 |
| **User** | Dan Sung |
| **Access** | RDP via Tailscale, credentials in KeePass |

---

### Specialized Machines — isengard

isengard is a dedicated recovery machine, kept offline except during disaster recovery operations.

| Field | Value |
|-------|-------|
| **OS** | Ubuntu (headless) |
| **Role** | Disaster recovery — stored offline |
| **Access** | Physical boot only |

Used for emergency network access via MikroTik ether5-EMERGENCY (see Network book Recovery Procedures).
