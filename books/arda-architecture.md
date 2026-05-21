# Arda Architecture
> Slug: arda-architecture

---

## Contents

- The Big Picture
- Machines Reference
- Network at a Glance
- External Access
- Security Model
- Managing Arda Documentation

---

### The Big Picture

| Component | Hardware | Software | Role |
|-----------|----------|----------|------|
| Router | MikroTik RB750GL | RouterOS 7.x | Routing, DHCP, DNS, firewall |
| Switch | Zyxel GS1900-24HP | Zyxel firmware | VLAN switching |
| Wi-Fi | UniFi APs (AC Pro + AC Lite x4) | UniFi controller on Rivendell | Wireless |
| Primary server | Rivendell (custom build) | Ubuntu 24.04 + Docker | AI, BookStack, apps |
| NAS | Moria (Synology DS1511+) | DSM 6.2.4 | Storage, UniFi controller |
| Smart home | Home Assistant (dedicated hardware) | HA OS | Smart home hub |
| External access | — | Cloudflare tunnel | Secure external access |
| AI | Rivendell GPU (GTX 1060 6GB) | Ollama + LiteLLM + Hermes | Local LLM inference, AI assistant gateway |

---

### Machines Reference

A quick reference for every machine in Arda — what it is, where it lives, and how to reach it.

#### Rivendell

Primary Docker server. Runs all AI workloads, BookStack, and supporting infrastructure.

| | |
|---|---|
| **OS** | Ubuntu 24.04 LTS |
| **IP** | 192.168.10.4 |
| **DNS** | rivendell.lan |
| **VLAN** | 10 (trusted) |
| **Access** | `ssh aule@rivendell.lan` |
| **GPU** | NVIDIA GTX 1060 6GB |
| **Key services** | Aulë (Hermes agent), Ollama, LiteLLM, BookStack, Grafana, Prometheus, Cloudflared, Portainer, UniFi controller |
| **Stacks** | `/mnt/work/ai-stack/`, `/mnt/work/infra-stack/`, `/mnt/work/book-stack/` |

#### Moria

Synology NAS. Primary storage and UniFi controller host.

| | |
|---|---|
| **OS** | Synology DSM 6.2.4 |
| **IP** | 192.168.10.6 (NIC1), 192.168.10.7 (NIC2) |
| **DNS** | moria.lan |
| **Web UI** | http://moria.lan:5000 |
| **VLAN** | 10 (trusted) |
| **Access** | `ssh aule@moria.lan` |
| **Key services** | File storage, some Docker containers |
| **Shared folders** | `/volume1/backups/`, `/volume1/homes/` |

#### Home Assistant

Smart home hub. Runs on dedicated hardware.

| | |
|---|---|
| **OS** | Home Assistant OS |
| **IP** | 192.168.10.10 |
| **DNS** | homeassistant.lan |
| **Web UI** | http://homeassistant.lan:8123 |
| **External** | Via Nabu Casa remote access |

#### Palantir

Management machine. Always on, always on VLAN99. Required for network recovery.

| | |
|---|---|
| **OS** | Debian / XFCE |
| **IP** | 192.168.99.21 |
| **DNS** | palantir.lan |
| **VLAN** | 99 (management only) |
| **Physical port** | Zyxel port 24 |
| **Role** | SSH jump host, Zyxel/MikroTik browser access during recovery, backup anchor |

#### Minasmorgul

Windows workstation. Everyday management access.

| | |
|---|---|
| **OS** | Windows |
| **IP** | 192.168.10.16 |
| **DNS** | minasmorgul.lan |
| **VLAN** | 10 (trusted) |
| **Role** | Daily ops, BookStack doc management via SSH tunnel |

#### Isengard

Recovery assistant — a laptop that connects to the emergency bridge port for network recovery.

| | |
|---|---|
| **IP (emergency bridge)** | 192.168.88.x |
| **Role** | Recovery, factory reset procedures |

#### Legacy / Inactive Hardware

| Machine | Type | Notes |
|---------|------|-------|
| Belegost | Buffalo LinkStation NAS | Exists but not actively used |
| Erebor | D-Link ShareCenter NAS | Exists but not actively used |

#### Management Network

The MikroTik router and Zyxel switch are on VLAN99 (management). Access from VLAN10 machines requires SSH tunnel through palantir.

| Device | IP | Access |
|--------|----|--------|
| MikroTik router | 192.168.99.1 | SSH (VLAN99 only), Winbox (VLAN99 only) |
| Zyxel switch | 192.168.99.2 | HTTP (VLAN99 only) |
| Palantir | 192.168.99.21 | SSH from VLAN10 (specifically allowed) |

---

### Network at a Glance

The Arda network uses three VLANs (trusted, IoT, management), a MikroTik RB750GL router, a Zyxel GS1900-24HP switch, and UniFi Wi-Fi. For full detail — topology, VLAN config, firewall rules, MikroTik and Zyxel reference, WiFi APs, SSH tunnel access, and operations — see the dedicated **[Network](/books/network)** book.

#### Quick Reference

**VLANs:**

| VLAN | Name | Subnet |
|------|------|--------|
| 10 | trusted | 192.168.10.0/24 |
| 20 | iot | 192.168.20.0/24 |
| 99 | mgmt | 192.168.99.0/24 |

**Wi-Fi:**

| SSID | VLAN | Use |
|------|------|-----|
| wintermute | 10 (trusted) | Family devices, phones, laptops |
| neuromancer | 20 (iot) | Smart home devices, IoT |

**Key IPs:**

| IP | Hostname | What |
|----|----------|------|
| 192.168.10.4 | rivendell.lan | Primary Docker server |
| 192.168.10.6 | moria.lan | Synology NAS |
| 192.168.10.10 | homeassistant.lan | Home Assistant |
| 192.168.99.21 | palantir.lan | Management machine |
| 192.168.99.1 | — | MikroTik gateway (VLAN99) |
| 192.168.99.2 | — | Zyxel switch management |

---

### External Access

How to reach Arda services from outside the house.

#### How It Works

Arda uses a **Cloudflare tunnel** for external access. A small agent (cloudflared) runs on Rivendell and maintains an outbound connection to Cloudflare. When you visit an Arda service externally, the request flows through Cloudflare to that tunnel — the house IP address is never exposed.

This means:
- No ports need to be opened on the home router
- The public internet cannot directly reach any home server
- All traffic passes through Cloudflare's edge before arriving at Arda

#### Available External Services

| Service | URL | Who can access |
|---------|-----|----------------|
| BookStack wiki | https://library.sung.us | Family (with login) |
| Additional services | Check Portainer for tunnel routes | Varies |

#### Authentication

External services use **Cloudflare Access** for authentication. You may be prompted to verify your identity (email OTP) before reaching the service's own login page.

If you see a Cloudflare authentication screen, that's normal — enter the email associated with your Cloudflare Access policy and complete the verification.

Credentials for each service are in the Sung KeePass DB.

#### If External Access Isn't Working

1. Check if the service works internally (on home Wi-Fi)
   - Works internally but not externally → likely a Cloudflare tunnel issue
   - Doesn't work internally → the service or server is down
2. Check if cloudflared container is running on Rivendell:
   ```bash
   ssh aule@rivendell.lan
   docker ps | grep cloudflared
   ```
3. If the container isn't running: `docker start cloudflared`
4. If it won't start, check logs: `docker logs cloudflared --tail 50`

#### Aulë on Telegram & Discord

Aulë is accessible via Telegram (@NavatarBot) and Discord (#aule channel). These platforms handle their own external connectivity — no Cloudflare tunnel is involved. As long as Rivendell is up and the Hermes container is running, Aulë is reachable from anywhere.

---

### Security Model

#### Principles

**Credentials in KeePass only.** No passwords in chat, documents, or this wiki. The Sung KeePass DB is the single source of truth.

**Network segmentation.** IoT devices cannot reach trusted devices. Trusted devices cannot reach management. Each VLAN has only the access it needs.

**No open ports.** External access goes through Cloudflare tunnel only. No ports are opened on the home router.

**Management plane isolation.** MikroTik and Zyxel admin is only accessible from VLAN99 or the physical emergency bridge. Even trusted VLAN10 machines cannot directly reach network admin interfaces — only via SSH tunnel through palantir.

**Local processing preferred.** Sensitive conversations with Aulë use local Ollama inference. Messages do not leave the house unless cloud fallback is triggered.

#### Access Control Summary

| Resource | Who Can Access | How |
|----------|---------------|-----|
| MikroTik admin | palantir (VLAN99) only | Direct SSH/HTTP |
| MikroTik admin | VLAN10 machines | SSH tunnel through palantir only |
| Zyxel admin | palantir (VLAN99) only | Direct HTTP |
| Zyxel admin | VLAN10 machines | SSH tunnel through palantir only |
| BookStack | Anyone with credentials | https://library.sung.us (Cloudflare tunnel) |
| Grafana | VLAN10 only | http://192.168.10.4:3001 |
| Portainer | VLAN10 only | https://192.168.10.4:9443 |
| Home Assistant | VLAN10 + Nabu Casa | http://homeassistant.lan:8123 or remote |
| Moria DSM | VLAN10 only | http://moria.lan:5000 |

---

### Managing Arda Documentation

This wiki is maintained through a git-based workflow. The source repository is at https://github.com/sungus6/bookstack.

#### How Content Works

Books are managed as markdown files in the `books/` directory of the repo. Each `.md` file is one BookStack book. Pages within a book are separated by `###` headings.

#### Workflow

```bash
# 1. Pull latest from GitHub
cd /home/aule/bookstack
git pull

# 2. Export current wiki content (ensures fresh markdown)
python3 scripts/export.py

# 3. Edit markdown files in books/
# (edit books/<slug>.md)

# 4. Preview changes
python3 scripts/upload.py --dry-run

# 5. Upload to BookStack
python3 scripts/upload.py

# 6. Commit and push
git add -A && git commit -m "..."
git push
```

This workflow is run from Rivendell (SSH access) or from the Hermes container.

#### Aulë's Role

Aulë can draft and update documentation. The workflow is:
1. Aulë writes draft content
2. Dan reviews and approves
3. Approved content is uploaded and committed

#### Managed Books

Only books listed in `managed_books.json` are processed by the upload script. If a new book needs to be managed, add its slug to that file.
