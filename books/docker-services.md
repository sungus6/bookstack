# Docker & Services
> Exported from BookStack on 2026-05-21
> Slug: docker-services

---

## Contents

- Container List
- BookStack Wiki
- Aulë & AI Stack
- Monitoring (Grafana & Prometheus)
- Portainer
- Cloudflare Tunnel

---

### Container List

All Docker containers run on **Rivendell** (192.168.10.4).

| Stack | Directory | Compose File | Key Containers |
|-------|-----------|-------------|----------------|
| AI stack | `/mnt/work/ai-stack/` | `docker-compose.yml` | ollama, litellm, hermes, grafana, prometheus |
| Infra stack | `/mnt/work/infra-stack/` | `docker-compose.yml` | cloudflared, portainer |
| Book stack | `/mnt/work/book-stack/` | `docker-compose.yml` | bookstack, bookstack_db |

#### Container Ports

| Container | Host Port | Internal Port | Access Notes |
|-----------|-----------|---------------|--------------|
| bookstack | 6875 | 8080 | Internal only (cloudflared handles external) |
| ollama | 11434 | 11434 | VLAN10 only |
| litellm | 4000 | 4000 | VLAN10 only |
| grafana | 3001 | 3000 | VLAN10 only |
| portainer | 9443 | 9443 | VLAN10 only, HTTPS |
| prometheus | 9090 | 9090 | VLAN10 only |

#### Common Docker Operations

```bash
# Check all running containers
docker ps

# See resource usage
docker stats --no-stream

# Check logs
docker logs CONTAINER_NAME --tail 100

# Restart a container
docker restart CONTAINER_NAME

# Restart a stack
cd /mnt/work/ai-stack && docker compose down && docker compose up -d

# View compose logs (AI stack example)
cd /mnt/work/ai-stack && docker compose logs --tail=50 -f
```

---

### BookStack Wiki

This wiki is running on BookStack (https://github.com/solidnerd/docker-bookstack).

#### Architecture

Two containers:
- **bookstack** — the web application (PHP/Laravel)
- **bookstack_db** — MariaDB database

Docker compose is at `/mnt/work/book-stack/docker-compose.yml`.

#### Git Workflow

The wiki content is managed via markdown files in a git repository at `/home/aule/bookstack/` on Rivendell. Managed books are exported to markdown, edited, and re-uploaded.

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

#### Direct Access

- **Internal:** http://192.168.10.4:6875 or http://library.sung.us
- **External:** https://library.sung.us (via Cloudflare tunnel)
- **Login:** Credentials in Sung KeePass DB

#### Backups

BookStack and its database are backed up nightly to Moria via the Rivendell backup script.

---

### Aulë & AI Stack

Aulë is the family AI assistant, running on Rivendell via the Hermes agent.

#### Architecture

```
hermes (gateway)
  ├── Telegram bot (@NavatarBot)
  ├── Discord bot (Aulë#6535)
  └── Tools layer (BookStack, Home Assistant, etc.)
        │
        ▼
litellm (LLM proxy)
  ├── ollama (local) — qwen2.5:3b
  ├── DeepSeek V4 (primary cloud)
  └── Fallbacks: gpt-4o-mini → claude-sonnet-4
```

#### Component Details

**ollama** runs the local LLM for inference:
- Port: 11434
- Loaded model: qwen2.5:3b (num_ctx=32768)
- GPU: GTX 1060 6GB

**LiteLLM** is the proxy/routing layer between Hermes and the LLM backends. Config: `/mnt/work/ai-stack/config/litellm.yaml`

**Hermes** is the Aulë agent itself — the gateway, memory, tools, and interfaces to Telegram and Discord. It runs as the `hermes` Docker container in the AI stack.

**Grafana** monitors AI usage metrics (model usage, latency, error rates) alongside infrastructure. URL: http://192.168.10.4:3001

#### Model Aliases (for LiteLLM admin)

| Alias | Actual Model | Priority |
|-------|-------------|----------|
| default | DeepSeek V4 | Primary |
| local | qwen2.5:3b (Ollama) | Falls back to fast → smart |
| fast | gpt-4o-mini | Cheap, fast, smart |
| smart | claude-sonnet-4 | Best quality, slower |
| genius | claude-opus-4-7 | Best of all, most expensive |
| haiku | claude-haiku-4-5 | Fast, cheap |

#### Common Operations

```bash
# Check ai-stack status
cd /mnt/work/ai-stack && docker compose ps

# Check LLM proxy is responding
curl http://localhost:4000/v1/models

# Check what models Ollama has loaded
curl http://localhost:11434/api/tags

# Restart Hermes
docker restart hermes

# Full AI stack restart
cd /mnt/work/ai-stack && docker compose down && docker compose up -d

# View Hermes logs
docker logs hermes --tail 100
```

---

### Monitoring (Grafana & Prometheus)

Arda uses Prometheus for metrics collection and Grafana for dashboards.

#### Architecture

prometheus (collector) → grafana (dashboard)

- Prometheus scrapes metrics from configured endpoints on the local network
- Grafana provides dashboards for system resources, network, and AI usage
- Both run in Docker on Rivendell

#### Access

- **Grafana:** http://192.168.10.4:3001
- **Prometheus:** http://192.168.10.4:9090

Credentials in Sung KeePass DB.

---

### Portainer

Portainer provides a web UI for Docker container management.

- **URL:** https://192.168.10.4:9443
- **Access:** VLAN10 only (internal)
- **Credentials:** Sung KeePass DB

Portainer connects to the local Docker socket on Rivendell and can manage all containers on that host. It does not manage containers on other machines (Moria's UniFi container is managed separately).

---

### Cloudflare Tunnel

The cloudflare tunnel provides secure external access to Arda services. It runs as a Docker container on Rivendell.

#### Container

```bash
docker ps | grep cloudflared
```

The container is part of the infra-stack at `/mnt/work/infra-stack/`.

#### Configuration

The tunnel is managed through the Cloudflare Zero Trust dashboard:
https://one.dash.cloudflare.com/

Tunnel ID and credentials are stored in the Sung KeePass DB and mounted into the container.

#### Adding a New Service to the Tunnel

1. In Cloudflare Zero Trust → Networks → Tunnels → Arda, add a Public Hostname
2. Set subdomain, domain, and internal target (e.g., http://192.168.10.4:PORT)
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
