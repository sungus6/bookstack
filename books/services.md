# Services
> Slug: services

---

## Contents

- BookStack Wiki
- Home Assistant
- Cloudflare Tunnel
- Monitoring (Grafana & Prometheus)
- Portainer

---

### BookStack Wiki

This wiki is running on BookStack (https://github.com/solidnerd/docker-bookstack). It's the central documentation hub for the entire family — tech documentation, family profiles, medical info, contacts, and more.

#### Architecture

Two containers:
- **bookstack** — the web application (PHP/Laravel) on port 6875
- **bookstack_db** — MariaDB database

Docker compose at `/mnt/work/book-stack/docker-compose.yml`.

#### Access

- **Internal:** http://192.168.10.4:6875 or http://library.sung.us
- **External:** https://library.sung.us (via Cloudflare tunnel)
- **Login:** Credentials in Sung KeePass DB

#### Git Workflow

The wiki content is managed via markdown files in a git repository at `/home/aule/bookstack/` on Rivendell.

```bash
# Full workflow
cd /home/aule/bookstack

# Get latest
git pull

# Export current wiki to markdown
python3 scripts/export.py

# Edit markdown files in books/

# Preview changes
python3 scripts/upload.py --dry-run

# Upload to BookStack
python3 scripts/upload.py

# Push changes
git add -A && git commit -m "description"
git push
```

The upload script only processes books listed in `managed_books.json`.

#### Content Management

- **Tier 1 books** (Arda shelf, Family profiles) — managed via git. Edit markdown, upload, push.
- **Tier 2 books** (all others) — edited directly in the BookStack WYSIWYG editor. Not git-managed.
- Aulë can also create and update content in the wiki directly via the BookStack API.

#### Backups

BookStack and its database are backed up nightly to Moria via the Rivendell backup script.

#### Container Operations

```bash
# Check status
docker ps | grep bookstack

# View logs
docker logs bookstack --tail 100

# Restart
docker restart bookstack
```

---

### Home Assistant

Home Assistant is the smart home hub for Arda. It runs on dedicated hardware in the house.

#### Quick Reference

| Field | Value |
|-------|-------|
| **Host** | Dedicated hardware (192.168.10.10) |
| **Port** | 8123 |
| **URL** | http://homeassistant.lan:8123 |
| **External** | Via Cloudflare tunnel |
| **Version** | 2026.5.2 |

#### Device & Automation Documentation

Full smart home inventory (lights, switches, sensors, climate) and automation reference are in the **[Smart Home](/books/smart-home)** book.

#### Integration with Aulë

Aulë can control Home Assistant devices. See the **[AI](/books/ai)** book for details on what Aulë can do with smart home devices.

#### Container Operations

Home Assistant does not run in Docker — it's a dedicated HA OS installation. Manage it through its own web UI or SSH add-on.

---

### Cloudflare Tunnel

The Cloudflare tunnel provides secure external access to Arda services without opening any ports on the home router.

#### Container

```bash
docker ps | grep cloudflared
```

The container runs as part of the infra-stack at `/mnt/work/infra-stack/`. Image: `cloudflare/cloudflared`.

#### Configuration

The tunnel is managed through the Cloudflare Zero Trust dashboard:
https://one.dash.cloudflare.com/

Tunnel ID and credentials are stored in the Sung KeePass DB and mounted into the container.

#### Adding a New Service

1. In Cloudflare Zero Trust → Networks → Tunnels → Arda, add a Public Hostname
2. Set subdomain, domain, and internal target (e.g., `http://192.168.10.4:PORT`)
3. Set an Access Application policy (who can reach it) in Zero Trust → Access → Applications
4. Test externally

#### Troubleshooting

```bash
# Check if container is running
docker ps | grep cloudflared

# View logs
docker logs cloudflared --tail 50

# Restart
docker restart cloudflared
```

---

### Monitoring (Grafana & Prometheus)

Arda uses Prometheus for metrics collection and Grafana for dashboards.

#### Architecture

```
prometheus (collector) → grafana (dashboard)
```

- Prometheus scrapes metrics from configured endpoints on the local network
- Grafana provides dashboards for system resources, network, and AI usage
- Both run in Docker on Rivendell

#### Access

- **Grafana:** http://192.168.10.4:3001
- **Prometheus:** http://192.168.10.4:9090

Credentials in Sung KeePass DB. VLAN10 only.

#### Operations

```bash
# Check status
cd /mnt/work/ai-stack && docker compose ps | grep -E 'grafana|prometheus'

# View Grafana logs
docker logs grafana --tail 50

# Restart
docker restart grafana
```

---

### Portainer

Portainer provides a web UI for Docker container management on Rivendell.

- **URL:** https://192.168.10.4:9443
- **Access:** VLAN10 only (internal)
- **Credentials:** Sung KeePass DB

Portainer connects to the local Docker socket on Rivendell and can manage all containers on that host. It does not manage containers on other machines (Moria's UniFi container is managed separately).
