# Network
> Exported from BookStack on 2026-05-21
> Slug: network

---

## Contents

- Physical Topology
- VLANs
- Wi-Fi Networks
- Firewall Rules & Access Control
- IP Address Reference
- DNS
- Router (MikroTik) Reference
- Switch (Zyxel) Reference
- SSH Tunnel Access (palantir)
- Operations & Common Tasks
- Recovery Procedures

---

### Physical Topology

```
Internet
    |
Xfinity Modem (wintermute_x) — 10.0.0.1
    |
MikroTik RB750GL
    ├── ether1-WAN         → Xfinity modem
    ├── ether2-TRUNK       → Zyxel port 1 (tagged trunk, all VLANs)
    ├── ether3             → Unused
    ├── ether4             → Unused
    └── ether5-EMERGENCY   → Emergency bridge (192.168.88.0/24)

Zyxel GS1900-24HP
    ├── Port 1             → MikroTik ether2-TRUNK
    ├── Ports 2-6          → UniFi APs (VLAN10 untagged, VLAN20 tagged)
    ├── Ports 7-20         → Trusted devices (VLAN10)
    ├── Ports 21-23        → IoT wired devices (VLAN20)
    └── Port 24            → palantir (VLAN99)
```

#### UniFi Controller

The UniFi controller runs as a Docker container on Rivendell (192.168.10.4:8443). APs adopt to the controller on VLAN10. If the controller is down after a Rivendell restart, APs continue serving Wi-Fi but changes to SSIDs/credentials won't take effect until it reconnects.

---

### VLANs

| VLAN | Name | Subnet | Gateway | DNS | Purpose |
|------|------|--------|---------|-----|---------|
| 10 | trusted | 192.168.10.0/24 | 192.168.10.1 | 192.168.10.1 | Trusted devices, PCs, servers |
| 20 | iot | 192.168.20.0/24 | 192.168.20.1 | 8.8.8.8, 8.8.4.4 | IoT devices, isolated |
| 99 | mgmt | 192.168.99.0/24 | 192.168.99.1 | 192.168.99.1 | Management machines only |
| N/A | emergency | 192.168.88.0/24 | 192.168.88.1 | 192.168.88.1 | Emergency access (MikroTik ether5) |

**Why IoT uses Google DNS directly:** IoT devices use 8.8.8.8 rather than MikroTik. This means they never need to reach MikroTik's admin interface for DNS, and vlan20-iot does not need to be in MikroTik's LAN interface list. This is intentional and more secure.

#### Switch Port Configuration

| Port | Device | PVID | Tagged VLANs | Frame Type | Role |
|------|--------|------|-------------|------------|------|
| Port 1 | MikroTik ether2-TRUNK | 1 | All | Tagged Only | Trunk uplink |
| Ports 2-6 | UniFi APs | 10 | 20 | All | WiFi APs |
| Ports 7-20 | Trusted devices | 10 | — | All | VLAN10 access |
| Ports 21-23 | IoT wired devices | 20 | — | All | VLAN20 access |
| Port 24 | palantir | 99 | — | All | VLAN99 management |

---

### Wi-Fi Networks

#### SSIDs

| SSID | UniFi Network | VLAN | Use |
|------|--------------|------|-----|
| wintermute | Default (untagged) | 10 via PVID | Family devices, phones, laptops |
| neuromancer | IoT (VLAN20) | 20 | Smart home devices, IoT |

Passwords in Sung KeePass DB.

#### Access Points

| AP | Model | Zyxel Port | IP |
|----|-------|-----------|-----|
| AP1 | UAP-AC-Pro | Port 2 | 192.168.10.11 |
| AP2 | UAP-AC-Lite | Port 3 | 192.168.10.12 |
| AP3 | UAP-AC-Lite | Port 4 | (DHCP) |
| AP4 | UAP-AC-Lite | Port 5 | (DHCP) |
| AP5 | UAP-AC-Lite | Port 6 | (DHCP) |

UniFi controller: https://192.168.10.4:8443 (Docker on Rivendell)

#### How VLAN Assignment Works for WiFi

AP ports (2-6) on the Zyxel have PVID=10 and VLAN20 as Tagged. Untagged frames from the AP land on VLAN10 via PVID. Tagged VLAN20 frames from the AP pass through to VLAN20.

wintermute clients send untagged frames → VLAN10 → 192.168.10.x addresses.
neuromancer clients send VLAN20-tagged frames → VLAN20 → 192.168.20.x addresses.

#### Critical: wintermute Must Be on "Default" Network in UniFi

**wintermute must be assigned to the "Default" network in UniFi, NOT "Trusted (VLAN10)".**

If wintermute is assigned to "Trusted (VLAN10)", the AP explicitly tags frames as VLAN10. But the Zyxel port PVID=10 already handles that for untagged frames — the explicit tag conflicts, and clients connect but get 169.254.x.x addresses with no internet.

Correct setup: wintermute → Default (untagged) → PVID=10 on Zyxel → VLAN10.

#### AP SSH Access

| Field | Value |
|-------|-------|
| Username | aule |
| Password | Sung KeePass DB |
| SSH command | `ssh aule@<ap-ip>` |
| set-inform | `/usr/bin/syswrapper.sh set-inform http://192.168.10.4:8080/inform` |

Use set-inform when an AP shows as disconnected after a controller migration or IP change.

---

### Firewall Rules & Access Control

#### Input Chain (to MikroTik itself)

- Accept established/related/untracked
- Drop invalid
- Accept ICMP from all LAN sources
- Drop all not from LAN interface list (critical gate — see Interface List Members below)
- Full access from VLAN99
- DNS (53) from trusted LAN and management
- Block admin ports from IoT and trusted LAN
- Drop all from WAN

#### Forward Chain (through MikroTik)

- Trusted LAN → WAN
- IoT → WAN
- Management → WAN — **DISABLED** intentionally (re-enable temporarily for `apt update`)
- Home Assistant → Moria (specific ports)
- IoT → Home Assistant (8123, 8009/8010/5353)
- Allow SSH from Trusted LAN to palantir specifically
- Block all inter-VLAN traffic (catch-all at end)

#### What Each VLAN Can Do

**VLAN10 (trusted) can:** internet, other VLAN10 devices, SSH to palantir:22, ping MikroTik, MikroTik DNS:53
**VLAN10 cannot:** MikroTik admin (SSH/Winbox/HTTP), VLAN20 devices, VLAN99 direct (except palantir SSH)

**VLAN20 (iot) can:** internet, Home Assistant (8123 TCP, 8009/8010/5353 UDP)
**VLAN20 cannot:** VLAN10 devices, VLAN99, MikroTik admin or DNS

**VLAN99 (mgmt) can:** Full MikroTik admin, Zyxel management (192.168.99.2), VLAN10 devices (RDP/management)
**VLAN99 cannot:** Internet access (intentionally disabled — re-enable temporarily for apt update)

#### Interface List Members — CRITICAL

Missing entries here cause subtle connectivity failures that are very hard to diagnose.

```
bridge-emergency → LAN    (emergency access treated as trusted)
ether1-WAN → WAN          (WAN interface)
vlan99-mgmt → LAN         (REQUIRED: palantir SSH to MikroTik)
vlan99-mgmt → MGMT        (management interface list)
bridge-emergency → MGMT   (emergency also in MGMT)
vlan10-trusted → LAN      (REQUIRED: VLAN10 DNS and routing)
```

**Why this matters:** MikroTik's default firewall rule 5 drops all input traffic from interfaces NOT in the LAN list. If vlan10-trusted is missing, VLAN10 clients can ping MikroTik but DNS times out and internet breaks. If vlan99-mgmt is missing, palantir cannot SSH into MikroTik.

**vlan20-iot is intentionally NOT in LAN.** IoT uses Google DNS directly.

Verify with:
```
/interface list member print
```

---

### IP Address Reference

| IP | Hostname | Device | VLAN |
|-----|----------|--------|------|
| 10.0.0.1 | — | Xfinity modem (wintermute_x) | WAN |
| 192.168.88.1 | router.lan | MikroTik emergency bridge | emergency |
| 192.168.10.1 | — | MikroTik VLAN10 gateway | 10 |
| 192.168.10.4 | rivendell.lan | Docker/AI server | 10 |
| 192.168.10.6 | moria.lan | Synology NAS NIC1 | 10 |
| 192.168.10.7 | — | Synology NAS NIC2 | 10 |
| 192.168.10.10 | homeassistant.lan | Home Assistant | 10 |
| 192.168.10.16 | minasmorgul.lan | Windows workstation | 10 |
| 192.168.20.1 | — | MikroTik VLAN20 gateway | 20 |
| 192.168.99.1 | — | MikroTik VLAN99 gateway | 99 |
| 192.168.99.2 | — | Zyxel management | 99 |
| 192.168.99.21 | palantir.lan | Management machine | 99 |

#### Static DHCP Leases

| IP | MAC | Machine |
|-----|-----|---------|
| 192.168.10.4 | AC:22:0B:75:E9:31 | rivendell |
| 192.168.10.6 | 00:11:32:0B:D9:C9 | moria NIC1 |
| 192.168.10.7 | 00:11:32:0B:D9:CA | moria NIC2 |
| 192.168.10.10 | E4:5F:01:3F:B5:AC | homeassistant |
| 192.168.10.16 | 00:21:CC:D5:89:C8 | minasmorgul |
| 192.168.99.21 | D4:BE:D9:27:84:9A | palantir |

---

### DNS

MikroTik handles local DNS for VLAN10 and VLAN99 machines. The `.lan` suffix resolves to local IPs. IoT devices (VLAN20) use Google DNS (8.8.8.8) directly — they do not resolve `.lan` names.

Upstream DNS: 9.9.9.9 (Quad9) and 1.1.1.1 (Cloudflare).

| Hostname | IP | Notes |
|----------|-----|-------|
| router.lan | 192.168.88.1 | MikroTik emergency bridge |
| moria.lan | 192.168.10.6 | Synology NAS |
| unifi.lan | 192.168.10.6 | UniFi controller on moria |
| homeassistant.lan | 192.168.10.10 | Home Assistant |
| palantir.lan | 192.168.99.21 | Management machine |
| minasmorgul.lan | 192.168.10.16 | Windows workstation |
| rivendell.lan | 192.168.10.4 | Docker/AI server |

---

### Router (MikroTik) Reference

#### Hardware

| Field | Value |
|-------|-------|
| **Model** | MikroTik RB750GL |
| **RouterOS** | 7.22.1 |
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

| Interface | VLAN ID | IP | Purpose |
|-----------|---------|-----|---------|
| vlan10-trusted | 10 | 192.168.10.1/24 | Trusted LAN gateway |
| vlan20-iot | 20 | 192.168.20.1/24 | IoT gateway |
| vlan99-mgmt | 99 | 192.168.99.1/24 | Management gateway |

#### DHCP Pools

| Pool | Range | Interface |
|------|-------|-----------|
| default-dhcp | 192.168.88.10-254 | bridge-emergency |
| pool-trusted | 192.168.10.10-200 | vlan10-trusted |
| pool-iot | 192.168.20.10-200 | vlan20-iot |
| pool-mgmt | 192.168.99.10-50 | vlan99-mgmt |

#### Admin Access Restrictions

MikroTik admin services are restricted to VLAN99 and emergency bridge only:

```
SSH:    192.168.99.0/24 and 192.168.88.0/24 only
HTTP:   192.168.99.0/24 and 192.168.88.0/24 only
Winbox: 192.168.99.0/24 and 192.168.88.0/24 only
```

#### Syslog

MikroTik sends info logs to palantir (192.168.99.21) on UDP 514. palantir runs rsyslog and writes MikroTik logs to `/var/log/mikrotik.log`.

Test log entry:
```
/log info message="test from mikrotik"
```

#### Common MikroTik Commands

```
/export                              — export full config to terminal
/export file=filename                — export to file
/ip dhcp-server lease print          — show DHCP leases
/ip dns static print                 — show DNS entries
/ip firewall filter print stats      — show firewall rules with hit counts
/interface list member print         — show interface list members (CRITICAL)
/ip firewall filter enable NUMBER    — enable a disabled rule
/ip firewall filter disable NUMBER   — disable a rule
/log info message="test"             — generate a test log entry
```

---

### Switch (Zyxel) Reference

#### Hardware

| Field | Value |
|-------|-------|
| **Model** | Zyxel GS1900-24HP |
| **Management IP** | 192.168.99.2 |
| **Management VLAN** | 99 |
| **Login** | admin / (Sung KeePass DB) |

#### Port Layout

| Port | Device | VLAN | Role |
|------|--------|------|------|
| Port 1 | MikroTik ether2-TRUNK | Tagged (all) | Trunk uplink |
| Port 2 | UAP-AC-Pro | PVID 10, VLAN20 tagged | WiFi AP |
| Port 3 | UAP-AC-Lite | PVID 10, VLAN20 tagged | WiFi AP |
| Port 4 | UAP-AC-Lite | PVID 10, VLAN20 tagged | WiFi AP |
| Port 5 | UAP-AC-Lite | PVID 10, VLAN20 tagged | WiFi AP |
| Port 6 | UAP-AC-Lite | PVID 10, VLAN20 tagged | WiFi AP |
| Ports 7-20 | Trusted devices | PVID 10 | VLAN10 access |
| Ports 21-23 | IoT wired devices | PVID 20 | VLAN20 access |
| Port 24 | palantir | PVID 99 | VLAN99 management |

#### VLAN Membership Tables

**VLAN10 (trusted):** Port 1 Tagged, Ports 2-20 Untagged, Ports 21-24 Excluded

**VLAN20 (iot):** Port 1 Tagged, Ports 2-6 Tagged, Ports 7-20 Excluded, Ports 21-23 Untagged, Port 24 Excluded

**VLAN99 (mgmt):** Port 1 Tagged, Ports 2-23 Excluded, Port 24 Untagged

#### Saving Configuration

Always save to flash after any change. Without this, changes are lost on power cycle.

Maintenance → Configuration → Source: Running Configuration → Destination: Startup Configuration → Apply

#### Backing Up Configuration

Maintenance → Configuration → Source: Running Configuration → Method: HTTP → Apply

Downloads a .cfg file. Push the backup to Moria.

---

### SSH Tunnel Access (palantir)

palantir (192.168.99.21) is the only machine with direct access to network admin interfaces. To manage MikroTik or Zyxel from a VLAN10 machine (like minasmorgul), you must SSH tunnel through palantir.

#### Setup (minasmorgul)

SSH config at `C:\Users\sungu\.ssh\config`:

```
Host palantir
    HostName 192.168.99.21
    User aule
    LocalForward 8080 192.168.99.2:80
    LocalForward 8081 192.168.99.1:80
```

#### Usage

1. Open PowerShell: `ssh palantir` (keep the window open)
2. Browse http://localhost:8080 → Zyxel management UI
3. Browse http://localhost:8081 → MikroTik web interface

Verify tunnel: `netstat -an | findstr 8080` should show LISTENING.

#### palantir SSH Keys

| Key | Path | Purpose |
|-----|------|---------|
| id_moria | ~/.ssh/id_moria | Passwordless SSH/rsync to moria |
| id_mikrotik | ~/.ssh/id_mikrotik | Passwordless SSH to MikroTik as aule |

palantir SSH config (`~/.ssh/config`):

```
Host moria
    HostName 192.168.10.6
    User aule
    IdentityFile /home/aule/.ssh/id_moria

Host mikrotik
    HostName 192.168.99.1
    User aule
    IdentityFile /home/aule/.ssh/id_mikrotik
```

#### palantir WiFi Must Be Disabled

If WiFi is active on palantir, routing breaks — SSH replies go out via WiFi instead of wired VLAN99.

```bash
nmcli radio wifi           # check
sudo nmcli radio wifi off  # disable
```

Wired interface enp1s0 should have metric 100 in NetworkManager.

#### Emergency Access

If palantir or VLAN99 is unreachable, connect to **ether5-EMERGENCY** on the MikroTik with a static IP:

```bash
sudo ip link set enp1s0 up
sudo ip addr add 192.168.88.50/24 dev enp1s0
sudo ip route add default via 192.168.88.1
ssh aule@192.168.88.1
```

---

### Operations & Common Tasks

#### Making Config Changes

1. Take a backup before changing anything
2. Make the change
3. Verify it works
4. Save to flash (Zyxel) or config is already live (MikroTik)
5. Take another backup after
6. Push backup to moria

#### Temporarily Re-enabling palantir Internet Access

palantir internet is intentionally disabled for security. Enable for `apt update`:

```
/ip firewall filter enable [find comment="Management to WAN (temporary)"]
```

Disable immediately after:

```
/ip firewall filter disable [find comment="Management to WAN (temporary)"]
```

#### Access Quick Reference

| Target | From | Method |
|--------|------|--------|
| Zyxel UI | palantir | http://192.168.99.2 directly |
| Zyxel UI | minasmorgul | SSH tunnel → http://localhost:8080 |
| MikroTik UI | palantir | http://192.168.99.1 directly |
| MikroTik UI | minasmorgul | SSH tunnel → http://localhost:8081 |
| MikroTik SSH | palantir | `ssh mikrotik` |
| MikroTik SSH | minasmorgul | SSH palantir, then `ssh mikrotik` |
| Moria SSH | palantir | `ssh moria` |
| palantir SSH | minasmorgul | `ssh palantir` |
| VLAN10 devices | minasmorgul | Direct (same VLAN) |

#### Port Reference

| Service | Port | Protocol | Accessible From |
|---------|------|----------|-----------------|
| MikroTik SSH | 22 | TCP | VLAN99 and emergency only |
| MikroTik HTTP | 80 | TCP | VLAN99 and emergency only |
| MikroTik Winbox | 8291 | TCP | VLAN99 and emergency only |
| Zyxel HTTP | 80 | TCP | VLAN99 only |
| UniFi HTTP | 8080 | TCP | VLAN10 |
| UniFi HTTPS | 8443 | TCP | VLAN10 |
| Ollama | 11434 | TCP | VLAN10 |
| LiteLLM | 4000 | TCP | VLAN10 |
| BookStack | 6875 | TCP | VLAN10 |
| Prometheus | 9090 | TCP | VLAN10 |
| Grafana | 3001 | TCP | VLAN10 |
| Portainer | 9443 | TCP | VLAN10 |
| MikroTik syslog | 514 | UDP | palantir receives |

---

### Recovery Procedures

#### MikroTik — Full Factory Reset and Rebuild

**When to use this:** Complete lockout, corrupted config, or when you need to start from scratch. This is the procedure that took weeks to get right.

1. **Physical access**: Connect a machine (isengard) to **ether5-EMERGENCY** on the MikroTik. No switch or Zyxel needed — direct cable to the router.

2. **Set static IP**: On isengard:

    ```bash
    sudo ip addr add 192.168.88.50/24 dev enp1s0
    sudo ip link set enp1s0 up
    ```

3. **Factory reset** via Netinstall (Windows on minasmorgul, or use the button method):
   - Hold the reset button on the MikroTik while powering it on
   - Release when the USR LED starts flashing
   - The router defaults to 192.168.88.1 on ether5
   - Verify: `ping 192.168.88.1`

4. **Initial access via WebFig**: http://192.168.88.1 (no password, default admin)

5. **First boot checklist** — apply in this exact order:

    a. **Change admin password** — System → Password
    
    b. **Set WAN interface** — Interfaces → ether1, set to `ether1-WAN`
    
    c. **Create VLAN interfaces**:
       - Interface → VLAN → Add New
       - vlan10-trusted: VLAN ID=10, Interface=ether2-TRUNK
       - vlan20-iot: VLAN ID=20, Interface=ether2-TRUNK
       - vlan99-mgmt: VLAN ID=99, Interface=ether2-TRUNK
    
    d. **Set IP addresses** on each VLAN interface:
       - vlan10-trusted: 192.168.10.1/24
       - vlan20-iot: 192.168.20.1/24
       - vlan99-mgmt: 192.168.99.1/24
    
    e. **Create the emergency bridge**:
       - Bridge → Add → Name=bridge-emergency
       - Ports → Add → Interface=ether5-EMERGENCY, Bridge=bridge-emergency
       - Set IP on bridge: 192.168.88.1/24
    
    f. **Set up DHCP server** on each interface:
       - IP → DHCP Server → DHCP Setup
       - pool-trusted: 192.168.10.10-200, interface=vlan10-trusted, gateway=192.168.10.1
       - pool-iot: 192.168.20.10-200, interface=vlan20-iot, gateway=192.168.20.1
       - pool-mgmt: 192.168.99.10-50, interface=vlan99-mgmt, gateway=192.168.99.1
       - default-dhcp: 192.168.88.10-254, interface=bridge-emergency, gateway=192.168.88.1
    
    g. **Add WAN DHCP client**: IP → DHCP Client → Interface=ether1-WAN
    
    h. **Set up interface list members** — **this is the step that caused weeks of pain if missed:**
       ```
       /interface list member add list=LAN interface=bridge-emergency
       /interface list member add list=WAN interface=ether1-WAN
       /interface list member add list=LAN interface=vlan99-mgmt
       /interface list member add list=MGMT interface=vlan99-mgmt
       /interface list member add list=MGMT interface=bridge-emergency
       /interface list member add list=LAN interface=vlan10-trusted
       ```
       
       **Do NOT add vlan20-iot to LAN.** IoT uses Google DNS directly.

    i. **Restrict admin access** to VLAN99 and emergency only:
       ```
       /ip services set ssh address=192.168.99.0/24,192.168.88.0/24
       /ip services set www address=192.168.99.0/24,192.168.88.0/24
       /ip services set winbox address=192.168.99.0/24,192.168.88.0/24
       /ip services set ftp disabled=yes
       /ip services set telnet disabled=yes
       /ip services set api disabled=yes
       ```

    j. **Apply firewall rules** (see Firewall Rules section above). The critical minimum:
       - Accept established/related/untracked
       - Drop invalid
       - Rule 5: Drop all input not from LAN list
       - Allow VLAN99 full access
       - Allow DNS from VLAN10 and MGMT
       - Block admin ports from non-MGMT
       - Block inter-VLAN forwarding (with SSH exception for palantir)

    k. **Set up DNS**: IP → DNS → Servers=9.9.9.9,1.1.1.1, allow-remote-requests=yes
    
    l. **Reboot and verify** — connect palantir to ether5-EMERGENCY first, verify admin access works, then move palantir to Zyxel port 24 once the switch is configured.

#### Zyxel — Full Factory Reset and Rebuild

**When to use this:** Complete lockout, VLAN1 exclusion disaster, or corrupted config.

1. **Physical access**: Press and hold the reset button on the front panel for 10+ seconds until the LEDs flash. The switch resets to:
   - IP: 192.168.1.1 (DHCP) or 192.168.1.2 (fallback)
   - Login: admin / 1234

2. **Find the switch**: Set your machine to 192.168.1.x/24 and ping 192.168.1.1 (or check DHCP). If you can't find it, connect directly port-to-port and use a static IP.

3. **Initial access**: http://192.168.1.1 → admin / 1234

4. **Change admin password** immediately.

5. **First boot checklist:**

    a. **Set management VLAN to 99**: Switch → Management → VLAN Stacking → Management VLAN ID = 99
    
    b. **Configure port 1 (trunk to MikroTik):**
       - Port 1 → PVID=1 (default)
       - Accept Frame Type = Tagged Only
       - Ingress Check = Enable
       - VLAN Trunking = Enable
    
    c. **Configure AP ports (2-6):**
       - PVID=10
       - Accept Frame Type = All
       - Ingress Check = Enable
       - VLAN Trunking = Enable
    
    d. **Configure trusted ports (7-20):**
       - PVID=10
       - Accept Frame Type = All
       - Ingress Check = Enable
       - VLAN Trunking = Disable
    
    e. **Configure IoT ports (21-23):**
       - PVID=20
       - Accept Frame Type = All
       - Ingress Check = Enable
       - VLAN Trunking = Disable
    
    f. **Configure port 24 (palantir mgmt):**
       - PVID=99
       - Accept Frame Type = All
       - Ingress Check = Enable
       - VLAN Trunking = Disable

    g. **Set up VLAN membership tables:**
       - **VLAN10 (trusted):** Port 1 Tagged, Ports 2-20 Untagged, Ports 21-24 Excluded
       - **VLAN20 (iot):** Port 1 Tagged, Ports 2-6 Tagged, Ports 7-20 Excluded, Ports 21-23 Untagged, Port 24 Excluded
       - **VLAN99 (mgmt):** Port 1 Tagged, Ports 2-23 Excluded, Port 24 Untagged
    
    h. **CRITICAL — Never exclude VLAN1.** VLAN1 is used internally by the Zyxel regardless of the management VLAN setting. Excluding VLAN1 from any port has caused complete lockouts requiring factory reset multiple times. Leave VLAN1 at its defaults on all ports.

    i. **Save to flash**: Maintenance → Configuration → Source: Running Configuration → Destination: Startup Configuration → Apply

6. **Verify**: Connect palantir to port 24. It should get a DHCP lease on 192.168.99.x. Verify you can reach http://192.168.99.2 from palantir.

#### When Only Part of the Network Is Down

**Wi-Fi works but VLAN10 wired devices can't reach the internet:**
- Check MikroTik interface list members (`/interface list member print`). vlan10-trusted must be in the LAN list.
- Check MikroTik firewall rule 5 is not blocking (`/ip firewall filter print stats`).

**palantir can't reach MikroTik:**
- Check vlan99-mgmt is in both LAN and MGMT interface lists.
- Check palantir WiFi is off (`nmcli radio wifi`).
- Verify palantir is plugged into Zyxel port 24.

**Can't reach anything at all:**
- Plug into ether5-EMERGENCY on MikroTik directly (bypasses the switch entirely).
- If MikroTik responds, the problem is the Zyxel or the cabling.
- If MikroTik doesn't respond even on ether5, the router may need a factory reset.

---
