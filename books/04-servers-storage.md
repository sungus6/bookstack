# Servers & Storage
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
| openclaw | (custom) | 7000 | Deprecated — replaced by Hermes (formerly Aulë) |
| prometheus | prom/prometheus | 9090 | Metrics collection |
| grafana | grafana/grafana | 3001 → 3000 | Dashboards |
| cloudflared | cloudflare/cloudflared | — | Cloudflare tunnel |
| portainer | portainer/portainer-ce | 9443 | Container management UI |

#### Stack Locations

```
/mnt/work/
├── ai-stack/
│   └── docker-compose.yml      (ollama, litellm, hermes, grafana, prometheus)
├── infra-stack/
│   └── docker-compose.yml      (prometheus, grafana, cloudflared, portainer)
└── book-stack/
    └── docker-compose.yml      (bookstack, bookstack_db)
```

#### Common Operations

```bash
# Check all running containers
docker ps

# Check GPU status
nvidia-smi

# Check Ollama loaded models
curl http://localhost:11434/api/tags

# Check logs for a container
docker logs CONTAINER_NAME --tail 50

# Restart a single container
docker restart CONTAINER_NAME

# Restart entire stack
cd /mnt/work/ai-stack && docker compose down && docker compose up -d
```

#### Docker Compose Gotchas

- All stacks live under `/mnt/work/` with their own `docker-compose.yml` files.
- The grafana container in `ai-stack/` and the one in `infra-stack/` are the same container — the ai-stack compose includes it. Don't run both stacks simultaneously for grafana.

---

### Moria — NAS & Storage

Moria is the Synology NAS providing file storage, backups, and some Docker services.

#### Specs

| Field | Value |
|-------|-------|
| **Model** | Synology DS1511+ |
| **OS** | DSM 6.2.4 |
| **IP** | 192.168.10.6 (NIC1), 192.168.10.7 (NIC2) |
| **DNS** | moria.lan |
| **Web UI** | http://moria.lan:5000 |
| **VLAN** | 10 (trusted) |
| **SSH** | `ssh aule@moria.lan` |

#### Shared Folders

| Folder | Purpose |
|--------|---------|
| `/volume1/backups/` | Network and server backups |
| `/volume1/homes/` | User home directories |
| `/volume1/docker/UniFi/` | UniFi controller data (runs on Moria) |

#### Services on Moria

- **UniFi Controller** — runs as a Docker container on Moria (legacy, being migrated to Rivendell)
- **File storage** — primary NAS role
- **rsync target** — backups from palantir land here

#### rsync to Moria

```bash
# The --rsync-path flag is required for Synology compatibility
rsync -av -e "ssh -i ~/.ssh/id_moria" \
  SOURCE_FILE \
  aule@192.168.10.6:DEST_PATH \
  --rsync-path=/usr/bin/rsync
```

---

### Home Assistant

The smart home hub. See the Smart Home book for detailed operations and user guides.

#### Specs

| Field | Value |
|-------|-------|
| **OS** | Home Assistant OS |
| **IP** | 192.168.10.10 |
| **DNS** | homeassistant.lan |
| **Web UI** | http://homeassistant.lan:8123 |
| **VLAN** | 10 (trusted) |

#### Quick Operations

| Action | How |
|--------|-----|
| **Restart HA (not host)** | Settings → System → Restart → Restart Home Assistant |
| **Restart host** | Settings → System → Restart → Reboot Host |
| **Check logs** | Settings → System → Logs |
| **Add integration** | Settings → Devices & Services → Add Integration |
| **Backups** | Settings → System → Backups → Create Backup |

---

### Palantir — Management Machine

Palantir is the dedicated management machine. Always on, always on VLAN99. It is the anchor for network recovery and backup operations.

#### Specs

| Field | Value |
|-------|-------|
| **OS** | Debian / XFCE |
| **IP** | 192.168.99.21 |
| **DNS** | palantir.lan |
| **VLAN** | 99 (management only) |
| **Physical port** | Zyxel port 24 |

#### Role

- SSH jump host to MikroTik, Zyxel, and other VLAN99 devices
- Backup scripts run here (MikroTik config, palantir home dir)
- Backup anchor — local copies of all backups live here
- Zyxel management UI access via browser

#### SSH from VLAN10

```bash
# palantir is the only VLAN99 machine accessible from VLAN10
ssh aule@192.168.99.21
```

---

### Minasmorgul — Windows Workstation

Minasmorgul is the primary Windows workstation for daily management.

#### Specs

| Field | Value |
|-------|-------|
| **OS** | Windows |
| **IP** | 192.168.10.16 |
| **DNS** | minasmorgul.lan |
| **VLAN** | 10 (trusted) |

#### Role

- Daily operations and management
- BookStack documentation workflows (via PowerShell scripts)
- SSH tunnel through palantir to reach VLAN99 devices

---

### Isengard — Recovery Machine

Isengard is a recovery assistant machine that connects to the MikroTik emergency bridge port (ether5-EMERGENCY) during network recovery.

#### Emergency Bridge Access

```bash
# Connect Isengard to ether5-EMERGENCY on MikroTik
sudo ip addr add 192.168.88.50/24 dev enp1s0
sudo ip route add default via 192.168.88.1

# Now you can reach MikroTik at 192.168.88.1 for recovery
```

---

### Legacy NAS (Belegost, Erebor)

These machines exist but are not actively used in the current Arda setup. Notes preserved for reference.

#### Belegost (Buffalo LinkStation NAS)

| Field | Value |
|-------|-------|
| **Model** | LS421DE Series |
| **ID** | LS421DE327A |
| **IP** | 192.168.88.5 (Static) |
| **Admin page** | http://192.168.88.212/root.html |
| **Manual** | http://buffalo.jp/support_s/guide2/manual/ls/400/99/en/pc_index.html |
| **Role** | Redundant backup, Synology Photos, individual laptop backups |

#### Erebor (D-Link ShareCenter DNS-320)

| Field | Value |
|-------|-------|
| **IP** | 192.168.88.68 |
| **Purchased** | 8/15/2023 (used) |
| **Admin** | See KeePass (passwords on old sticker: w7ht!Sha1, wy3329h!Sha1) |
| **Setup** | https://support.dlink.com/resource/products/dns-320/REVA/ |
| **Software** | DNS-320_SETUPWIZARD_1.00.ZIP |
| **SMTP** | smtp-mail.outlook.com:25 |
| **Status** | Not actively part of current Arda operations |
