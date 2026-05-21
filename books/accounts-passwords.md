# Accounts & Passwords
> Exported from BookStack on 2026-05-21
> Slug: accounts-passwords

---

## Contents

- Internet Accounts
- Cellphone (Google Fi)
- Password Vault (KeePass)
- LAN Accounts

---

### Internet Accounts

#### Online Accounts

There are three primary family accounts used for online services:

- **Microsoft:** sung.us@outlook.com
- **Google:** sung.us.hw@gmail.com
- **Facebook:** sung.us@outlook.com

#### Passwords

All account passwords are stored in the Sung KeePass database. See the [Password Vault (KeePass)](#password-vault-keepass) page for access instructions.

#### Related

- See the **Internet** book for ISP, domain, and connectivity details.
- See the **LAN Accounts** page in this book for internal/system accounts.

---

### Cellphone (Google Fi)

#### Carrier

**Google Fi**

#### Account

| Field | Value |
|-------|-------|
| **Account Holder** | Sheewon Sung |
| **Passcode** | 7535 |
| **Login Email** | sheewon.sung@gmail.com |

Login via the Google Fi app on your phone using the Gmail account above.

#### Line Assignments

| Name | Number | Role |
|------|--------|------|
| Sheewon (Owner) | 847.208.1833 | Account owner |
| Mary | 847.208.1834 | Family line |
| Allison | 847.431.0397 | Family line |
| Noah | 847.207.0038 | Family line |
| Jacob | 847.220.0915 | Family line |

#### Notes

- **Grandma** is on **Tello** (pre-paid, ~$8/mo), not part of Google Fi. If Google Fi pricing changes to be competitive, she could be added to the plan.

---

### Password Vault (KeePass)

#### Overview

All family account and password information is maintained in a **KeePass** database stored on Moria. KeePass is an open-source password manager that stores credentials locally (unlike browser-based managers that sync to vendor servers).

- **KeePass website:** https://keepass.info/

#### KeePass Apps

| Platform | App |
|----------|-----|
| Windows | KeePassXC — https://keepassxc.org/ |
| Android | KeePass2Android |
| iOS | Keepassium |

#### Sung KeePass Database

| Field | Value |
|-------|-------|
| **Database Name** | sung.kdbx |
| **Location** | \\\\moria\\famdoc\\Keepass |
| **Password** | Sung@keepass |

#### KeeShare (Read-Only Access)

You can gain read-only access to the passwords without logging into Moria as sung.us by using KeeShare. This requires your own local KeePass database.

**Setup steps:**
1. Create a new group in your KeePass DB
2. Set **Type:** Import
3. Set **Path:** \\\\moria\\famdoc\\Keepass\\KeeShare\\sung.keeshare.kdbx
4. **Name:** Whatever you like
5. **Password:** Same as sung.kdbx (Sung@keepass)
6. In the **KeeShare section**, configure the import

**Available extract groups:**

| Extract | Contents |
|---------|----------|
| **sung.family** | Family shared passwords |
| **sung.home** | Home-related accounts (finance, utilities, etc.) |
| **sung.arda** | Hometech (network, internet, ai, seervices) passwords and secrets, tokens |

> Note: KeeShare is currently set to one-way export from the master DB. When passwords change in sung.kdbx, they update automatically in your imported copy.

---

### LAN Accounts

These are internal accounts used to manage the Arda network, servers, and computers.

#### Accounts

| Account | Purpose | Notes |
|---------|---------|-------|
| **aule** | Internal admin account | Primary admin on most servers and computers. Passwords vary by machine — see KeePass. |
| **sung.us** | Family account | Fallback admin on some machines. See KeePass for passwords. |
| **kiosk** | Home Assistant kiosk | Used for the Home Assistant dashboard displays. |

Passwords for all LAN accounts are stored in the Sung KeePass database. See the [Password Vault (KeePass)](#password-vault-keepass) page for access.

---
