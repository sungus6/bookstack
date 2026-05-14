# Internet
> Exported from BookStack on 2026-05-14
> Slug: internet

---

## Contents

**Connectivity**
- Internet Overview
- Router Configuration
- Domain
- Cloudflare
**Security**
- Firewall Design

---

## Chapter: Connectivity

### Internet Overview

# Internet Overview

This document describes the internet connectivity architecture for the Arda homelab.

## Internet Provider

| Provider | Type  |
| -------- | ----- |
| Xfinity  | Cable |

### Account
Account number: 8771 1010 0033 0130
Account Holder: Dan Sung
Address: 6 James Dr, Hawthorn woods, IL 60047
Mobile Phone No.: 847.208.1833

User ID: See Keepass

PWD: See Keepass

### Modem
Activation

5/30/2025 
Admin account
ID: admin
Password: See keepass
Bridge Mode: enabled
### Xfinity Old Accounts
Account number: 8771 1005 1038 7234?
Round Lake account. Should be inactiveX. Still linked to 0130 account.

Account number: 8771 1010 0032 4554
Name: Fam Sung
Account number: 8771 1010 0032 4554
Mobile Number: (847) 208-1833
Personal email: [email protected]
Comcast email: [email protected]
1/7/2026  removed Mobile number and email from this account
Spoke with security tech Nary

Account #1 (disconnected when moving from Open Pkwy to JamesDr)
Acct No.:  8771101000311882
Address Transfer: 3/2/2019 Transferred from 61 Open Pkwy to 6 James
Received new account no.
Modem:
Cisco DPC3000
MAC Address: 0022CE9DB9F0
https://wiki.sung.us/link/53#bkmrk-%C2%A0

 

## Internet Gateway

The ISP gateway connects the home network to the internet.

Key responsibilities:

* WAN connectivity
* NAT translation
* Connection to internal router

---

### Router Configuration

# Router Configuration

The MikroTik router manages routing and firewall policies.

## Responsibilities

* VLAN routing
* Firewall filtering
* Network segmentation
* Internet gateway

## Internal Networks

| Network        | Subnet          |
| -------------- | --------------- |
| LAN            | 192.168.10.0/24 |
| IoT            | 192.168.20.0/24 |
| Infrastructure | 192.168.99.0/24 |

---

### Domain

_No markdown content. This page was edited in WYSIWYG mode._

---

### Cloudflare

_No markdown content. This page was edited in WYSIWYG mode._

---

## Chapter: Security

### Firewall Design

# Firewall Design

Firewall rules protect the internal network.

## Security Principles

* Default deny policy
* Allow required services only
* Isolate IoT devices

## Traffic Rules

| Source         | Destination | Action |
| -------------- | ----------- | ------ |
| LAN            | Internet    | Allow  |
| IoT            | LAN         | Deny   |
| Infrastructure | LAN         | Allow  |

---
