# Docker & Applications
> Exported from BookStack on 2026-05-14
> Slug: docker-applications

---

## Contents

**Application Reference**
- BookStack
- Grafana & Prometheus
**Overview**
- Docker Overview
- Portainer
- Cloudflared
- openclaw

---

## Chapter: Application Reference

### BookStack

# BookStack

## What It Is

BookStack is the wiki you're reading right now. It organizes documentation into
Books > Chapters > Pages. All Arda documentation lives here.

## Access

| Method | URL |
|---|---|
| External | https://library.sung.us |
| Internal | http://192.168.10.4:6875 |

Admin credentials in Sung KeePass DB.

## Container Details

| Field | Value |
|---|---|
| Container | bookstack |
| Image | solidnerd/bookstack |
| Port | 6875 -> 8080 |
| Stack | /mnt/work/book-stack/ |
| Database | bookstack_db (MariaDB 10.11) |
| Data | /mnt/work/book-stack/bookstack-data/ |
| Logs | /mnt/work/book-stack/bookstack-logs/ |

## External Access

BookStack is exposed via Cloudflare tunnel at https://library.sung.us.
Cloudflare Access may prompt for email verification before reaching the login page.
SSL mode in Cloudflare is set to Full — do not change to Flexible.

## Documentation Workflow

The BookStack update workflow runs from Minasmorgul using PowerShell scripts:

```
C:\bookstack-update\
├── scripts\
│   ├── config.ps1               -- credentials and paths
│   ├── export-bookstack.ps1     -- pulls all books to exports\
│   └── upload-bookstack.ps1     -- pushes staging\ back to BookStack
├── exports\                     -- read-only snapshots from BookStack
├── staging\                     -- files being edited/updated
└── logs\                        -- dated log files
```

Workflow:
1. Run `export-bookstack.ps1` to pull current content to `exports\`
2. Copy books to update into `staging\`
3. Edit markdown files in `staging\`
4. Run `upload-bookstack.ps1 -DryRun` to preview changes
5. Run `upload-bookstack.ps1` to push to BookStack

## Troubleshooting

**BookStack not loading:**
```bash
docker logs bookstack --tail 30
docker logs bookstack_db --tail 30
```

**Reset admin password (emergency):**
```bash
docker exec -it bookstack php artisan bookstack:create-admin
```

**Database shell access:**
```bash
docker exec -it bookstack_db mysql -u bookstack -p bookstackapp
```

**Restart the stack:**
```bash
cd /mnt/work/book-stack
docker compose down && docker compose up -d
```

---

### Grafana & Prometheus

# Grafana & Prometheus

## What They Are

**Prometheus** collects metrics from rivendell and other systems on a schedule,
storing time-series data.

**Grafana** provides dashboards and visualization — CPU, memory, disk, network,
container health, and anything else instrumented.

## Access

| Service | URL |
|---|---|
| Grafana | http://192.168.10.4:3001 |
| Prometheus | http://192.168.10.4:9090 |

Admin credentials in Sung KeePass DB.

## Container Details

| Container | Image | Port | Stack |
|---|---|---|---|
| prometheus | prom/prometheus | 9090 | /mnt/work/infra-stack/ |
| grafana | grafana/grafana | 3001 -> 3000 | /mnt/work/infra-stack/ |

## What's Being Monitored

Check current scrape targets at: http://192.168.10.4:9090/targets

Any target showing as DOWN needs investigation — check that the exporter
or endpoint is running on the target machine.

## Adding a New Scrape Target

Edit `/mnt/work/infra-stack/prometheus/prometheus.yml`, add a job under `scrape_configs`,
then restart Prometheus:
```bash
docker restart prometheus
```

## Troubleshooting

```bash
docker logs prometheus --tail 30
docker logs grafana --tail 30
```

**Grafana shows "No data" on dashboards:**
1. Check Prometheus is running: `docker ps | grep prometheus`
2. Verify data source: Grafana -> Configuration -> Data Sources -> Test
3. Check Prometheus has data: http://192.168.10.4:9090/graph, query `up`

**Grafana login issues:**
Admin credentials in Sung KeePass DB. If lost, reset via:
```bash
docker exec -it grafana grafana-cli admin reset-admin-password NEWPASSWORD
```

---

## Chapter: Overview

### Docker Overview

# Docker Overview

## How Docker is Used in Arda

All services in Arda run as Docker containers on rivendell. Docker provides isolation,
easy updates, and consistent deployment. Containers are organized into stacks managed
by Docker Compose.

## Stack Organization

Each stack is a self-contained `docker-compose.yml` in `/mnt/work/`:

| Stack | Location | Contains |
|---|---|---|
| ai-stack | /mnt/work/ai-stack/ | Ollama, LiteLLM |
| infra-stack | /mnt/work/infra-stack/ | Prometheus, Grafana, Cloudflared, Portainer |
| book-stack | /mnt/work/book-stack/ | BookStack, MariaDB |
| openclaw | /data/compose/openclaw/ | openclaw (Aule Telegram bot) |

## Common Docker Commands

```bash
# List running containers
docker ps

# List all containers including stopped
docker ps -a

# View container logs
docker logs CONTAINER_NAME --tail 50
docker logs CONTAINER_NAME -f         # live follow

# Restart a container
docker restart CONTAINER_NAME

# Stop and start a container
docker stop CONTAINER_NAME
docker start CONTAINER_NAME

# Restart entire stack
cd /mnt/work/STACK_NAME
docker compose down
docker compose up -d

# Pull latest images and restart stack
cd /mnt/work/STACK_NAME
docker compose pull
docker compose up -d

# View resource usage
docker stats

# Execute a command inside a running container
docker exec -it CONTAINER_NAME bash
```

## Container Data Persistence

Container data is persisted via bind mounts to specific paths on rivendell.
Deleting a container does NOT delete its data — the directories remain.

To find where a container stores its data:
```bash
docker inspect CONTAINER_NAME | grep -A 10 Mounts
```

## Updating Containers

```bash
cd /mnt/work/STACK_NAME
docker compose pull CONTAINER_NAME
docker compose up -d CONTAINER_NAME

# Verify it started correctly
docker logs CONTAINER_NAME --tail 20
```


## Chapter: Application Reference

---

### Portainer

# Portainer

## What It Is

Portainer provides a web UI for Docker management. Useful for viewing container status,
logs, and resource usage without needing SSH access to rivendell.

## Access

https://192.168.10.4:9443

Admin credentials in Sung KeePass DB.

## Container Details

| Field | Value |
|---|---|
| Container | portainer |
| Image | portainer/portainer-ce |
| Port | 9443 |
| Stack | /mnt/work/infra-stack/ |

## What You Can Do in Portainer

- View all running and stopped containers
- Start, stop, restart containers
- View live and historical container logs
- Browse container environment variables and mounts
- View resource usage (CPU, memory, network)
- Access container console (exec shell)
- Manage Docker networks and volumes

## When to Use Portainer vs SSH

Use Portainer when:
- You want a quick status overview
- You need to restart a container and don't have SSH handy
- You want to check logs without setting up a terminal

Use SSH when:
- You need to edit files on rivendell
- You need to run docker compose commands
- You need to do anything Portainer doesn't expose

## Troubleshooting

If Portainer itself is not accessible:
```bash
ssh aule@rivendell.lan
docker restart portainer
```

---

### Cloudflared

# Cloudflared

## What It Is

Cloudflared runs the Cloudflare tunnel that exposes internal Arda services to the
internet without opening any ports on the home router. The house IP is never directly
exposed — all traffic goes through Cloudflare's network.

## Container Details

| Field | Value |
|---|---|
| Container | cloudflared |
| Image | cloudflare/cloudflared |
| Stack | /mnt/work/infra-stack/ |

## Services Exposed

| External URL | Internal Target |
|---|---|
| https://library.sung.us | http://192.168.10.4:6875 (BookStack) |

Additional services can be added via the Cloudflare dashboard.

## Cloudflare Access

Some services are protected by Cloudflare Access (identity verification) in addition
to their own login. Managed at dash.cloudflare.com under the Arda tunnel.
Credentials in Sung KeePass DB.

## Troubleshooting

**External access not working:**
```bash
docker logs cloudflared --tail 30
```

Look for connection errors or authentication failures. If the tunnel is down:
```bash
docker restart cloudflared
```

**Check tunnel status:**
Log in to dash.cloudflare.com -> Zero Trust -> Networks -> Tunnels.
The Arda tunnel should show as Healthy.

**SSL mode:**
Cloudflare SSL/TLS mode must be set to Full (not Flexible) for BookStack.
If changed to Flexible, BookStack will redirect loop.

---

### openclaw

# openclaw

## What It Is

openclaw is the Telegram bot that powers Aule — the Arda home AI assistant.
It receives messages from Telegram, forwards them to LiteLLM for routing,
and returns responses to the user.

The bot is named @NavatarBot in Telegram.

## Container Details

| Field | Value |
|---|---|
| Container | openclaw |
| Image | python:3.11-slim |
| Port | 7000 |
| Stack | /data/compose/openclaw/ |

## How It Connects

```
Telegram user
    |
@NavatarBot (Telegram API)
    |
openclaw (port 7000 on rivendell)
    |
LiteLLM (port 4000 on rivendell)
    |
Ollama (local GPU) or cloud APIs (OpenAI / Anthropic)
```

## Configuration

Config lives in `/data/compose/openclaw/docker-compose.yml` and associated `.env`.

Key settings:
- **Telegram bot token** — connects to @NavatarBot. In Sung KeePass DB.
- **LiteLLM endpoint** — points to http://litellm:4000 (internal Docker network)
- **Default model** — which LiteLLM model to use by default
- **System prompt** — Aule's personality and context about Arda

## Operations

```bash
# Check status
docker ps | grep openclaw

# View logs
docker logs openclaw --tail 50
docker logs openclaw -f    # live follow

# Restart
docker restart openclaw

# Full stack restart
cd /data/compose/openclaw
docker compose down && docker compose up -d
```

## Testing

```bash
# Health check
curl http://localhost:7000/health

# Test LiteLLM is reachable from openclaw
docker exec -it openclaw curl http://litellm:4000/health
```

If Aule is not responding in Telegram:
1. Check openclaw is running: `docker ps | grep openclaw`
2. Check logs: `docker logs openclaw --tail 30`
3. Check LiteLLM: `curl http://localhost:4000/health`
4. Restart: `docker restart openclaw`

---
