# Security & Access
> Exported from BookStack on 2026-05-14
> Slug: security-access

---

## Contents

- Security Overview
- Credential Management
- SSH Key Management
- Cloudflare Access
- Key Rotation Procedures
- Incident Response

---

### Security Overview

# Security Overview

## Security Principles

**Credentials in KeePass only.** No passwords in chat, documents, or this wiki.
The Sung KeePass DB is the single source of truth for all credentials.

**Network segmentation.** IoT devices cannot reach trusted devices. Trusted devices
cannot reach management. Each VLAN has only the access it needs. See Network book
for full firewall rule details.

**No open ports.** External access goes through Cloudflare tunnel only. No ports are
opened on the home router. The house IP is never directly exposed.

**Management plane isolation.** MikroTik and Zyxel admin is only accessible from
VLAN99 or the physical emergency bridge. Even trusted VLAN10 machines cannot directly
reach network admin interfaces — only via SSH tunnel through palantir.

**Local processing preferred.** Sensitive conversations with Aule use local Ollama
inference. Messages do not leave the house unless cloud fallback is triggered.

## Access Control Summary

| Resource | Who Can Access | How |
|---|---|---|
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

### Credential Management

# Credential Management

## KeePass DB

All Arda credentials are stored in the **Sung KeePass DB**. This is the single
source of truth. Never store credentials anywhere else.

Credentials stored in KeePass include:
- WiFi passwords (wintermute, neuromancer)
- Service logins (BookStack, Grafana, Portainer, Moria DSM, UniFi)
- External accounts (Cloudflare, domain registrar, Nabu Casa)
- SSH keys and passphrases
- API tokens (BookStack, OpenAI, Anthropic, Telegram bot)
- Any other Arda-related credential

**Never share credentials in Telegram, email, SMS, or this wiki.**

## API Tokens

| Token | Used By | Location |
|---|---|---|
| BookStack API token | export/upload scripts on minasmorgul | config.ps1 + KeePass |
| Telegram bot token | openclaw | openclaw .env + KeePass |
| OpenAI API key | LiteLLM | ai-stack .env + KeePass |
| Anthropic API key | LiteLLM | ai-stack .env + KeePass |
| Cloudflare API token | cloudflared | infra-stack .env + KeePass |

---

### SSH Key Management

# SSH Key Management

## Current Key Inventory

| Key Name | Location | Authorizes Access To | Purpose |
|---|---|---|---|
| id_moria | palantir:~/.ssh/id_moria | moria authorized_keys | palantir -> moria passwordless SSH/rsync |
| id_mikrotik | palantir:~/.ssh/id_mikrotik | MikroTik user key store | palantir -> MikroTik passwordless SSH |

## Adding a New SSH Key

**palantir to a new Linux host:**
```bash
# On palantir
ssh-keygen -t ed25519 -f ~/.ssh/id_HOSTNAME -C "palantir->HOSTNAME"
ssh-copy-id -i ~/.ssh/id_HOSTNAME.pub aule@HOSTNAME_IP
```

Then add to `~/.ssh/config` on palantir:
```
Host HOSTNAME
    HostName HOSTNAME_IP
    User aule
    IdentityFile /home/aule/.ssh/id_HOSTNAME
```

**palantir to MikroTik (special process):**
MikroTik does not support `ssh-copy-id`. Must copy key file first:
```bash
# On palantir
scp ~/.ssh/id_mikrotik.pub aule@192.168.99.1:id_mikrotik.pub
ssh aule@192.168.99.1
```
Then on MikroTik:
```
/user ssh-keys import public-key-file=id_mikrotik.pub user=aule
```

## Removing a Compromised Key

**From a Linux host:**
```bash
# Edit ~/.ssh/authorized_keys on the target host
# Remove the line containing the compromised public key
```

**From MikroTik:**
```
/user ssh-keys print
/user ssh-keys remove numbers=NUMBER
```

## Key Permissions

SSH keys must have correct permissions or SSH refuses to use them:
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_*          # private keys
chmod 644 ~/.ssh/id_*.pub      # public keys
chmod 600 ~/.ssh/authorized_keys
chmod 644 ~/.ssh/known_hosts
```

---

### Cloudflare Access

# Cloudflare Access

## Overview

Cloudflare Access sits in front of externally exposed services. It requires
identity verification (email OTP or other method) before passing traffic to
the internal service. This is the first layer of protection for BookStack.

## Managing Cloudflare Access

Log in to dash.cloudflare.com -> Zero Trust -> Access -> Applications.

Credentials in Sung KeePass DB.

## Current Policies

| Application | Policy | Notes |
|---|---|---|
| library.sung.us (BookStack) | Email OTP for allowed domains | Fill in allowed email domains |

## Adding a New Protected Application

1. Add the new tunnel route in Zero Trust -> Networks -> Tunnels -> Arda -> Public Hostname
2. Add the domain and internal target (e.g. http://192.168.10.4:PORT)
3. Create an Access Application in Zero Trust -> Access -> Applications
4. Set the policy (who can access — by email domain, specific emails, etc.)
5. Test external access

## Bypass / Whitelist

If an application should be accessible without Cloudflare Access verification,
remove or set a bypass policy in Access -> Applications.

Be careful — removing Access protection means only the application's own login
stands between the internet and the service.

---

### Key Rotation Procedures

# Key Rotation Procedures

## When to Rotate

- A device is decommissioned or sold
- A team member's access should be revoked
- A credential may have been compromised
- Annual rotation as good practice

## Rotating BookStack API Token

1. Log in to BookStack at https://library.sung.us
2. Profile (top right) -> API Tokens
3. Delete the old token
4. Create a new token — copy ID and Secret immediately (shown once only)
5. Update `C:\bookstack-update\scripts\config.ps1` on minasmorgul
6. Update KeePass DB
7. Test: run `.\export-bookstack.ps1 -DryRun` on minasmorgul

## Rotating Telegram Bot Token

1. In Telegram, open @BotFather
2. Send `/mybots` -> select @NavatarBot -> API Token -> Revoke current token
3. Copy new token
4. Update openclaw .env file on rivendell: `/data/compose/openclaw/.env`
5. Update KeePass DB
6. Restart openclaw: `docker restart openclaw`
7. Test: send a message to @NavatarBot in Telegram

## Rotating OpenAI / Anthropic API Keys

1. Generate new key in the provider's dashboard (platform.openai.com or console.anthropic.com)
2. Update the LiteLLM config .env file on rivendell: `/mnt/work/ai-stack/.env`
3. Update KeePass DB
4. Restart LiteLLM: `docker restart litellm`
5. Test: send a message to Aule via Telegram and verify cloud fallback works

## Rotating SSH Keys (palantir)

1. Generate new key pair on palantir:
   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/id_HOSTNAME_new -C "palantir->HOSTNAME"
   ```
2. Install new public key on target host (before removing old key)
3. Test new key: `ssh -i ~/.ssh/id_HOSTNAME_new aule@HOSTNAME`
4. Update `~/.ssh/config` to point to new key
5. Remove old key from target host's `authorized_keys`
6. Delete old key files from palantir
7. Update KeePass DB

---

### Incident Response

# Incident Response

## If You Think Something is Compromised

1. **Disconnect** the affected device from the network immediately
2. **Contact Dad** — do not attempt to investigate or fix unless you know what you're doing
3. **Do not** reuse any credentials that may have been exposed
4. **Check MikroTik logs** via palantir for unusual traffic:
   ```bash
   tail -200 /var/log/mikrotik.log
   ```
5. **Check container logs** on rivendell for unusual activity:
   ```bash
   docker logs CONTAINER_NAME --tail 100
   ```

## Suspicious Network Traffic

To check current DHCP leases (look for unknown devices):
```
/ip dhcp-server lease print
```

To check active connections through MikroTik:
```
/ip firewall connection print
```

To temporarily block a suspicious IP:
```
/ip firewall address-list add list=blocked address=SUSPICIOUS_IP
```
Then add a drop rule referencing the `blocked` list, or disconnect the device physically.

## Credential Exposure Response

If a credential (password, API key, SSH key) may have been exposed:

1. Rotate the credential immediately (see Key Rotation Procedures)
2. Check logs for any unauthorized use
3. Update KeePass DB with new credential
4. Notify affected parties if the credential was shared

## Account Lockout

If locked out of a service:

- **BookStack:** `docker exec -it bookstack php artisan bookstack:create-admin`
- **Grafana:** `docker exec -it grafana grafana-cli admin reset-admin-password NEWPASSWORD`
- **MikroTik:** factory reset via emergency bridge — see Network book Recovery Runbook
- **Zyxel:** factory reset — see Network book Recovery Runbook
- **Moria DSM:** physical console access required

---
