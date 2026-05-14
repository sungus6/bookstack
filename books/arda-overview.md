# Arda Overview
> Exported from BookStack on 2026-05-14
> Slug: arda-overview

---

## Contents

- The Big Picture
- Machines Reference
- Network at a Glance
- External Access
- Managing Arda Documentation
- Aulë Quick Context

---

### The Big Picture

# The Big Picture

Arda is a home lab — a small private infrastructure that runs on hardware in the house.
This page gives a technical overview of how all the pieces fit together.

---

## The Three Layers

**Network layer** — controls how devices talk to each other and to the internet.
A MikroTik router handles routing and firewalling. A Zyxel managed switch handles
physical port assignment and VLAN tagging. UniFi access points handle Wi-Fi.
Traffic is segmented into three VLANs: trusted devices, IoT, and management.

**Compute layer** — the machines that run services.
Minasanor is the primary server, running all Docker-based workloads.
Moria is the NAS, providing storage and hosting the UniFi controller.
Home Assistant runs the smart home stack.

**Application layer** — the software people actually use.
Aulë (via Telegram), the BookStack wiki (library.sung.us), Grafana dashboards,
Home Assistant, and anything exposed externally via Cloudflare tunnel.

---

## How Traffic Flows

Internal traffic stays on the local network. External access (from outside the house)
goes through a Cloudflare tunnel running on Minasanor — no ports are opened on the
home router. This means the house IP address is never exposed directly.

---

## Key Design Principles

**Private by default.** Data stays on home hardware unless explicitly sent elsewhere.

**Segmented by trust.** IoT devices cannot reach trusted devices or the management plane.
Trusted devices cannot reach management directly — only through a controlled SSH tunnel.

**Resilient access.** A dedicated management VLAN (VLAN99) and a physical emergency port
on the router ensure administrative access even when the main network is broken.

**Documented.** This wiki exists so the system can be understood, maintained, and
eventually handed off without Dad being in the room.

---

## The Stack at a Glance

| Component | Hardware | Software | Role |
|---|---|---|---|
| Router | MikroTik RB750GL | RouterOS 7.22.1 | Routing, DHCP, DNS, firewall |
| Switch | Zyxel GS1900-24HP | Zyxel firmware | VLAN switching |
| Wi-Fi | UniFi APs (AC Pro + AC Lite x4) | UniFi controller on Moria | Wireless |
| Primary server | Rivendell (custom build) | Ubuntu 24.04 + Docker | AI, BookStack, apps |
| NAS | Moria (Synology DS1511+) | DSM 6.2.4 | Storage, UniFi controller |
| Smart home | Home Assistant (dedicated hardware) | HA OS | Smart home hub |
| External access | — | Cloudflare tunnel | Secure external access |
| AI | Rivendell GPU (GTX 1060 6GB) | Ollama + LiteLLM + openclaw | Local LLM inference |

---

### Machines Reference

# Machines Reference

A quick reference for every machine in Arda — what it is, where it lives, and how to reach it.

---

## Active Machines

### Rivendell
Primary Docker server. Runs all AI workloads, BookStack, and supporting infrastructure.

| | |
|---|---|
| OS | Ubuntu 24.04 LTS |
| IP | 192.168.10.4 |
| DNS | rivendell.lan |
| Access | SSH: `ssh aule@rivendell.lan` |
| Key services | Aulë (openclaw), Ollama, LiteLLM, BookStack, Grafana, Prometheus, Cloudflared, Portainer |
| GPU | GTX 1060 6GB (local inference) |
| Stacks | /mnt/work/ai-stack/, /mnt/work/infra-stack/, /mnt/work/book-stack/ |

---

### Moria
Synology NAS. Primary storage and UniFi controller host.

| | |
|---|---|
| OS | Synology DSM 6.2.4 |
| IP | 192.168.10.6 (NIC1), 192.168.10.7 (NIC2) |
| DNS | moria.lan |
| Web UI | http://moria.lan:5000 |
| Access | SSH: `ssh aule@moria.lan` |
| Key services | File storage, UniFi controller, Docker (Wyze cam only) |
| Shared folders | /volume1/backups/, /volume1/homes/ |

---

### Home Assistant
Smart home hub. Runs on dedicated hardware.

| | |
|---|---|
| OS | Home Assistant OS |
| IP | 192.168.10.10 |
| DNS | homeassistant.lan |
| Web UI | http://homeassistant.lan:8123 |
| External | Via Nabu Casa remote access |

---

### Palantir
Management machine. Always on, always on VLAN99. Required for network recovery.

| | |
|---|---|
| OS | Debian / XFCE |
| IP | 192.168.99.21 |
| DNS | palantir.lan |
| VLAN | 99 (management only) |
| Physical port | Zyxel port 24 |
| Role | SSH jump host, Zyxel/MikroTik browser access during recovery |

---

### Minasmorgul
Windows workstation. Everyday management access via SSH tunnel through palantir.

| | |
|---|---|
| OS | Windows |
| IP | 192.168.10.16 |
| DNS | minasmorgul.lan |
| Role | Daily ops, management access via SSH tunnel |

---

## Legacy / Inactive Hardware

### Belegost
Buffalo LinkStation NAS. Exists but not actively used.

### Erebor
D-Link ShareCenter NAS. Exists but not actively used.

---

## Management Network

The MikroTik router and Zyxel switch are on VLAN99 (management).
Access from VLAN10 machines requires SSH tunnel through palantir.

| Device | IP | Access |
|---|---|---|
| MikroTik router | 192.168.99.1 | SSH (VLAN99 only), Winbox (VLAN99 only) |
| Zyxel switch | 192.168.99.2 | HTTP (VLAN99 only) |
| Palantir | 192.168.99.21 | SSH from VLAN10 (specifically allowed) |

For details on accessing these from VLAN10 machines, see the SSH tunnel setup in
the Network book → Operations chapter.

---

### Network at a Glance

# Network at a Glance

A quick reference for the Arda network. For full detail, see the Network book.

---

## VLANs

| VLAN | Name | Subnet | Who's on it |
|---|---|---|---|
| 10 | trusted | 192.168.10.0/24 | PCs, servers, NAS, APs, trusted devices |
| 20 | iot | 192.168.20.0/24 | Smart home devices, IoT gear |
| 99 | mgmt | 192.168.99.0/24 | Palantir, MikroTik, Zyxel |

IoT devices cannot reach trusted devices. Trusted devices cannot reach management
directly. VLAN99 has full access to everything for administration.

---

## Wi-Fi Networks

| SSID | VLAN | Use |
|---|---|---|
| wintermute | 10 (trusted) | Family devices, phones, laptops |
| neuromancer | 20 (iot) | Smart home devices, IoT |

Connect personal devices to **wintermute**.
Connect smart plugs, cameras, and IoT devices to **neuromancer**.
Passwords in Sung KeePass DB.

---

## IP Address Quick Reference

| IP | Hostname | What |
|---|---|---|
| 192.168.10.1 | — | MikroTik gateway (VLAN10) |
| 192.168.10.4 | rivendell.lan | Primary Docker server |
| 192.168.10.6 | moria.lan, unifi.lan | Synology NAS / UniFi controller |
| 192.168.10.10 | homeassistant.lan | Home Assistant |
| 192.168.10.16 | minasmorgul.lan | Windows management machine |
| 192.168.99.1 | — | MikroTik gateway (VLAN99) |
| 192.168.99.2 | — | Zyxel switch management |
| 192.168.99.21 | palantir.lan | Management machine |

---

## External Access

External services are published via Cloudflare tunnel — no ports are opened on the
home router. The tunnel runs on Rivendell.

| Service | External URL |
|---|---|
| BookStack wiki | https://wiki.sung.us |
| (other services) | See Book 5 → Docker & Applications |

External access is protected by Cloudflare Access policies. Some services require
additional authentication beyond the app login.

---

## DNS

MikroTik handles local DNS for all VLAN10 and VLAN99 machines.
The `.lan` suffix resolves to local IPs (e.g. `moria.lan` → 192.168.10.6).
IoT devices use Google DNS (8.8.8.8) directly — they do not resolve `.lan` names.

Upstream DNS: 9.9.9.9 (Quad9) and 1.1.1.1 (Cloudflare).

---

### External Access

# External Access

How to reach Arda services from outside the house.

---

## How It Works

Arda uses a **Cloudflare tunnel** for external access. A small agent (cloudflared)
runs on Minasanor and maintains an outbound connection to Cloudflare. When you visit
an Arda service externally, the request flows through Cloudflare to that tunnel —
the house IP address is never exposed.

This means:
- No ports need to be opened on the home router
- The public internet cannot directly reach any home server
- All traffic passes through Cloudflare's edge before arriving at Arda

---

## Available External Services

| Service | URL | Who can access |
|---|---|---|
| BookStack wiki | https://wiki.sung.us | Family (with login) |

Additional services may be available. Check with Dad or look in Portainer for active
cloudflared tunnel routes.

---

## Authentication

External services use **Cloudflare Access** for authentication. You may be prompted
to verify your identity (email OTP or other method) before reaching the login page
of the service itself.

If you see a Cloudflare authentication screen, that's normal — enter the email
associated with your Cloudflare Access policy and complete the verification.

Credentials for each service are in the Sung KeePass DB.

---

## If External Access Isn't Working

1. Check if the service works internally (on home Wi-Fi)
   - If yes internally but not externally → likely a Cloudflare tunnel issue
   - If no internally either → the service or server is down
2. Check if cloudflared container is running on Minasanor:
   ```bash
   ssh aule@minasanor.lan
   docker ps | grep cloudflared
   ```
3. If the container is not running: `docker start cloudflared`
4. If it won't start, check logs: `docker logs cloudflared --tail 50`

---

## Aulë on Telegram

Aulë is accessible via Telegram at **@NavatarBot**. Telegram handles its own external
connectivity — no Cloudflare tunnel is involved. As long as Minasanor is up and
openclaw is running, Aulë is reachable from anywhere with internet access.

---

### Managing Arda Documentation

# Doc mgmt moved to Minasmorgul. This doc needs to be updated.

How this wiki is organized, maintained, and updated.

---

## Where the Content Lives

The source of truth for all documentation is a folder structure on Minasmorgul:

```
/mnt/work/book-stack/docs/books/
├── arda-welcome/
├── arda-overview/
├── arda-network/
├── arda-servers-storage/
├── arda-docker-applications/
├── arda-aule-ai/
├── arda-smart-home/
├── arda-security-access/
└── arda-backup-recovery/
```

Each folder is a book. Subfolders are chapters. `.md` files are pages.
Numeric prefixes (`01-`, `02-`) control display order.

---

## How Content Gets Into BookStack

A custom upload script (`bookstack_upload.py`) reads the local folder structure
and syncs it to BookStack via API. It creates new pages, updates changed ones,
and skips identical ones. It never deletes.

```bash
# Upload everything
python3 /mnt/work/book-stack/bookstack_upload.py

# Upload a specific book
python3 /mnt/work/book-stack/bookstack_upload.py --books arda-welcome
```

The script uses an API token stored in `/mnt/work/book-stack/.env`.
The token is also in the Sung KeePass DB.

---

## How Exports Work

A companion service (`bookstack-file-exporter`) pulls content FROM BookStack
and saves it as markdown files to:

```
/mnt/work/book-stack/docs/exports/YYYY-MM-DD/
```

This runs on a nightly schedule and provides a backup of what's actually in BookStack.

---

## Aulë's Role in Documentation

Aulë can draft new documentation pages. The workflow:

1. Aulë writes draft content to `/mnt/work/book-stack/docs/staging/`
2. Dad reviews and approves
3. Approved content is promoted to `/mnt/work/book-stack/docs/books/`
4. Upload script syncs it to BookStack

Aulë can also trigger the upload script directly once that integration is configured.

---

## BookStack Admin Access

- URL: https://library.sung.us
- Local: http://192.168.10.4:6875
- Admin credentials: Sung KeePass DB

BookStack uses Cloudflare Access for external login. The SSL mode is set to Full
(not Flexible) — do not change this in Cloudflare.

---

## Adding or Updating Pages

**Manual edits:** Edit the `.md` file directly in `/mnt/work/book-stack/docs/books/`,
then run the upload script.

**New page:** Create a new `.md` file with the correct numeric prefix. Run upload script.

**New chapter:** Create a new subfolder inside the book folder with a numeric prefix.
Add `.md` files inside it. Run upload script.

**New book:** Create a new folder under `docs/books/`. Create the matching book in
BookStack UI first (the script matches by slug, not name). Then run upload script.

---

## 9-Book Structure

| # | Book | Audience |
|---|---|---|
| 1 | Welcome to Arda | Everyone |
| 2 | Arda Overview | Techies + Dad |
| 3 | Network | Techies + Dad |
| 4 | Servers & Storage | Techies + Dad |
| 5 | Docker & Applications | Techies + Dad |
| 6 | Aulë & AI | Everyone + Techies |
| 7 | Smart Home | Everyone + Techies |
| 8 | Security & Access | Dad + Techies |
| 9 | Backup & Recovery | Dad + Techies |

---

### Aulë Quick Context

# Aulë Quick Context

*This page is a machine-readable context block. Paste it into a Claude conversation
to give Claude immediate working knowledge of Arda without re-explaining everything.*

---

## PASTE BELOW THIS LINE

You are helping with the Arda home lab. Here is essential context:

**What Arda is:** A home lab running on personal hardware. MikroTik router, Zyxel managed switch, UniFi APs. Primary server is Rivendell (Ubuntu, Docker). NAS is Moria (Synology). Smart home runs on Home Assistant.

**Naming:** Everything is Tolkien-themed. Machines: Rivendell (Docker server, 192.168.10.4), Moria (NAS, 192.168.10.6/.7), Palantir (management, 192.168.99.21), Minasmorgul (Windows workstation, 192.168.10.16), Home Assistant (192.168.10.10), Minastirith (legacy Ubuntu, 192.168.10.8). Networks: wintermute (trusted WiFi), neuromancer (IoT WiFi).

**VLANs:** VLAN10 trusted (192.168.10.0/24), VLAN20 IoT (192.168.20.0/24), VLAN99 management (192.168.99.0/24). IoT cannot reach trusted. Trusted cannot reach management admin directly — SSH tunnel through palantir only.

**AI stack on Rivendell:** Ollama (local inference, GTX 1060 6GB), LiteLLM (proxy), openclaw (Telegram bot = @NavatarBot = Aulë). Fallback chain: local-fast → gpt-4o-mini → claude-sonnet → claude-opus.

**External access:** Cloudflare tunnel via cloudflared container on Rivendell. No ports open on home router. library.sung.us = BookStack wiki.

**Management access:** Zyxel at 192.168.99.2, MikroTik at 192.168.99.1. Only accessible from VLAN99 or emergency bridge (192.168.88.1 via ether5). From VLAN10 machines: SSH tunnel through palantir (`ssh palantir`, then localhost:8080/8081).

**Critical MikroTik gotcha:** vlan10-trusted AND vlan99-mgmt must both be in the LAN interface list or DNS/SSH breaks. Check with `/interface list member print`.

**Credentials:** All in Sung KeePass DB. Never in this wiki or in chat.

**Documentation:** Source in /mnt/work/book-stack/docs/books/ on Rivendell. Upload script: bookstack_upload.py. 9-book structure in BookStack at library.sung.us.

**Owner:** Dad (aule). Technical support: Noah, Jacob.

---
