# Servers & Storage
> Exported from BookStack on 2026-05-21
> Slug: servers-storage

---

## Contents

- Rivendell — Docker Server
- Moria — NAS & Storage
- Home Assistant
- Palantir — Management Machine
- Minasmorgul — Windows Workstation
- Isengard — Recovery Machine
- Legacy NAS (Belegost, Erebor)

---

### Rivendell — Docker Server

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

#### Docker Containers

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| bookstack | solidnerd/bookstack | 6875 → 8080 | Wiki/documentation |
| bookstack_db | mariadb:10.11 | — | BookStack database |
| ollama | ollama/ollama | 11434 | Local LLM inference |
| litellm | ghcr.io/berriai/litellm | 4000 | LLM proxy/router |
| prometheus | prom/prometheus | 9090 | Metrics collection |
| grafana | grafana/grafana | 3001 → 3000 | Dashboards |
| cloudflared | cloudflare/cloudflared | — | Cloudflare tunnel |
| portainer | portainer/portainer-ce | 9443 | Container management UI |

> **Note:** The Hermes AI agent container is documented in the [Docker & Services](/books/docker-services) book, where its full architecture and operations are covered.

#### Directory Layout

```
/mnt/work/
├── ai-stack/
│   └── docker-compose.yml      (ollama, litellm, hermes, grafana, prometheus)
├── infra-stack/
│   └── docker-compose.yml      (prometheus, grafana, cloudflared, portainer)
└── book-stack/
    └── docker-compose.yml      (bookstack, bookstack_db)
```

#### Docker Compose Gotchas

- All stacks live under `/mnt/work/` with their own `docker-compose.yml` files.
- The grafana container in `ai-stack/` and the one in `infra-stack/` are the same container — the ai-stack compose includes it. Don't run both stacks simultaneously for grafana.

---

### Moria — NAS & Storage

Moria (Synology DS1511+) provides storage for the entire Arda network.

#### Specs

| Field | Value |
|-------|-------|
| **Model** | Synology DS1511+ |
| **OS** | DSM 6.2.4 |
| **IP** | 192.168.10.6 |
| **DNS** | moria.lan |
| **VLAN** | 10 (trusted) |
| **Access** | SSH (aule@moria.lan) or DSM web UI (https://moria.lan:5001) |

#### Services

- **UniFi Controller** — runs as a Docker container on Moria, not Rivendell
- **NFS shares** — mounted by Rivendell for Docker volume data, media, backups
- **Backup target** — nightly backups from Rivendell and other machines land here

#### Storage Layout

| Path | Purpose | Capacity |
|------|---------|----------|
| `/volume1/backups/` | Nightly backups from all machines | Allocated from pool |
| `/volume1/media/` | Shared media (music, photos, video) | Allocated from pool |
| `/volume1/docker/` | Docker volume data (exported via NFS) | Allocated from pool |

---

### Home Assistant

Home Assistant runs on dedicated hardware and is the central hub for all smart home devices.

| Field | Value |
|-------|-------|
| **Host** | Dedicated hardware |
| **IP** | 192.168.10.10 |
| **Port** | 8123 |
| **Access** | Internal: http://192.168.10.10:8123, External: via Cloudflare tunnel |

#### Integration

Full smart home documentation (device inventory, automations, operations) is in the [Smart Home](/books/smart-home) book.

---

### Palantir — Management Machine

Palantir is the management workstation for administering Arda.

| Field | Value |
|-------|-------|
| **OS** | Windows 11 Pro |
| **Role** | Management / admin workstation |
| **Access** | SSH keys, KeePass credential vault; RDP via Tailscale |

---

### Minasmorgul — Windows Workstation

Minasmorgul is Manwë's personal Windows machine.

| Field | Value |
|-------|-------|
| **OS** | Windows 11 Pro |
| **User** | Dan Sung |
| **Access** | RDP via Tailscale, credentials in KeePass |

---

### Isengard — Recovery Machine

Isengard is a dedicated recovery machine, kept offline except during disaster recovery operations.

| Field | Value |
|-------|-------|
| **OS** | Ubuntu (headless) |
| **Role** | Disaster recovery — stored offline |
| **Access** | Physical boot only |

---

### Legacy NAS (Belegost, Erebor)

Older NAS units that are still in service for specific purposes.

| Name | Model | Role |
|------|-------|------|
| **Belegost** | (older Synology) | Secondary storage / cold backups |
| **Erebor** | (older Synology) | Media archive / secondary backup |

---
