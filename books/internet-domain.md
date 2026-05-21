# Internet & Domain
> Slug: internet-domain

---

## Contents

- Internet Provider (Xfinity)
- Domain (sung.us)
- Cloudflare
- Router Configuration (MikroTik)

**This book is for Dan and technical family members. It contains provider account details, domain registration, and network configuration reference.**

---

### Internet Provider (Xfinity)

#### Current Account

| Field | Value |
|-------|-------|
| **Provider** | Xfinity (Cable) |
| **Account number** | 8771 1010 0033 0130 |
| **Account holder** | Dan Sung |
| **Address** | 6 James Dr, Hawthorn Woods, IL 60047 |
| **Phone** | 847.208.1833 |
| **User ID** | See KeePass |
| **Password** | See KeePass |

#### Modem

| Field | Value |
|-------|-------|
| **Activation** | 5/30/2025 |
| **Admin ID** | admin |
| **Admin PW** | See KeePass |
| **Mode** | Bridge Mode (enabled) |

The modem is in bridge mode — the MikroTik router handles all routing, NAT, and firewall. The modem is just a pass-through.

#### Old / Inactive Accounts

These are historical accounts that should be inactive but may still be linked:

| Account | Details |
|---------|---------|
| 8771 1005 1038 7234? | Round Lake account. May still be linked to current account. |
| 8771 1010 0032 4554 | Name: "Fam Sung". Old account. 1/7/2026 removed mobile/email. |
| 8771 1010 0311 882 | Disconnected when moving from Open Pkwy to James Dr. 3/2/2019 transferred. |

#### Old Modem

Cisco DPC3000 — MAC: 00:22:CE:9D:B9:F0. Replaced 5/30/2025.

---

### Domain (sung.us)

| Field | Value |
|-------|-------|
| **Domain** | sung.us |
| **Registrar** | Cloudflare |
| **Dashboard** | https://dash.cloudflare.com/85d2d33b87a78c0fcb69ffe02521de67/sung.us |
| **Zone ID** | f74122c6da88979c49e666fb2707db13 |
| **Account ID** | 85d2d33b87a78c0fcb69ffe02521de67 |
| **Account email** | See KeePass |
| **Password** | See KeePass |
| **Set up** | 2/14/2025 |
| **Renewal** | Every year in March |

#### Name Servers

| Type | Value |
|------|-------|
| NS | hal.ns.cloudflare.com |
| NS | mariah.ns.cloudflare.com |

---

### Cloudflare

Cloudflare provides security and access management for Arda's external services.

#### Zero Trust (Cloudflare Access)

| Field | Value |
|-------|-------|
| **Dashboard** | https://one.dash.cloudflare.com/85d2d33b87a78c0fcb69ffe02521de67/overview |
| **Team name** | sungus6 |
| **Team domain** | sungus6.cloudflareaccess.com |

Zero Trust sits in front of externally exposed services. It requires identity verification (email OTP) before passing traffic to the internal service.

#### Tunnels

Cloudflare tunnels provide secure external access to Arda services without opening any ports on the home router. Two tunnel containers have historically existed:

| Tunnel | Host | Status |
|--------|------|--------|
| Main (minastirith_tunnel) | Rivendell Docker | Active — all current subdomains through this |
| Legacy (Moria) | Moria Docker | Legacy — moria.sung.us originally through this. Goal is to consolidate everything under the main tunnel. |

The active tunnel runs via the `cloudflared` container on Rivendell.

#### WARP Client

WARP is a client app that connects devices to the home network via Cloudflare Tunnel. Install the appropriate WARP client for your device.

**Configuration:**
- Organization name: `sungus6` (from Zero Trust custom page team domain)

#### Email Routing

| Email | Forwarded To | Notes |
|-------|-------------|-------|
| aule@sung.us | sung.us@outlook.com | Used for BookStack wiki and Aulë system |

#### Adding a New Protected Application

1. Add a new tunnel route in Zero Trust → Networks → Tunnels → Arda → Public Hostname
2. Set the domain and internal target (e.g., http://192.168.10.4:PORT)
3. Create an Access Application in Zero Trust → Access → Applications
4. Set the policy (who can access — by email domain, specific emails, etc.)
5. Test external access

#### Managing Cloudflare Access

Log in to https://dash.cloudflare.com → Zero Trust → Access → Applications.

Credentials in Sung KeePass DB.

---

### Router Configuration (MikroTik)

#### Hardware

| Field | Value |
|-------|-------|
| **Model** | MikroTik RB750GL |
| **RouterOS** | 7.x |
| **Serial** | 467A022C49C2 |

#### Interface Layout

| Interface | Name | Role |
|-----------|------|------|
| ether1 | ether1-WAN | WAN uplink to Xfinity modem |
| ether2 | ether2-TRUNK | Tagged trunk to Zyxel (all VLANs) |
| ether3 | ether3-unused | Unused, not bridged |
| ether4 | ether4-unused | Unused, not bridged |
| ether5 | ether5-EMERGENCY | Emergency bridge access |

#### VLAN Interfaces

All VLAN interfaces run on ether2-TRUNK:

| Interface | VLAN ID | IP | Purpose |
|-----------|---------|----|---------|
| vlan10-trusted | 10 | 192.168.10.1/24 | Trusted LAN gateway |
| vlan20-iot | 20 | 192.168.20.1/24 | IoT gateway |
| vlan99-mgmt | 99 | 192.168.99.1/24 | Management gateway |

#### Internal Networks

| Network | Subnet |
|---------|--------|
| LAN | 192.168.10.0/24 |
| IoT | 192.168.20.0/24 |
| Infrastructure | 192.168.99.0/24 |

#### Security / Firewall

**VLAN10 (trusted) can:**
- Access internet
- Access other VLAN10 devices
- SSH to palantir (192.168.99.21 port 22 specifically allowed)
- Ping MikroTik (ICMP allowed for diagnostics)
- Reach MikroTik DNS (port 53)

**VLAN10 cannot:**
- Access MikroTik admin (SSH, Winbox, HTTP blocked)
- Access VLAN20 devices
- Access VLAN99 devices directly (except palantir via SSH)

**VLAN20 (iot) can:**
- Access internet
- Reach Home Assistant on specific ports (8123 TCP, 8009/8010/5353 UDP)

**VLAN20 cannot:**
- Access VLAN10 devices
- Access VLAN99 devices
- Reach MikroTik admin or DNS

**VLAN99 (mgmt) can:**
- Full access to MikroTik admin
- Access Zyxel management (192.168.99.2)
- Access VLAN10 devices (for RDP and management)
- Internet access — DISABLED intentionally (re-enable temporarily for apt update)

#### WiFi — Critical Gotcha

**wintermute** must be assigned to the **"Default"** network in UniFi, NOT "Trusted (VLAN10)".

If wintermute is assigned to "Trusted (VLAN10)", the AP explicitly tags frames as VLAN10. But the Zyxel port PVID=10 already handles that for untagged frames — the explicit tag conflicts, and clients connect but get 169.254.x.x addresses with no internet.

Correct setup: wintermute → Default (untagged) → PVID=10 on Zyxel → VLAN10.

neuromancer correctly uses the IoT network with VLAN20 because VLAN20 is Tagged on AP ports.

#### Accessing Router Admin

**From VLAN99 (palantir):** Direct SSH or Winbox to 192.168.99.1.

**From VLAN10 (normal machines):** SSH tunnel through palantir only. MikroTik admin ports are blocked from VLAN10.

**Emergency access:** Connect a machine to ether5 on the MikroTik. It gets an IP on the 192.168.88.0/24 emergency bridge network.
