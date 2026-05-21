# Welcome to Arda
> Slug: welcome-to-arda

---

## Contents

- What is Arda?
- Aulë — Your AI Assistant
- Using the Smart Home
- Accounts & Passwords
- If Something Isn't Working

---

### What is Arda?

Arda is our family's home technology system — a network of computers, storage, and software running quietly in our house.

It handles things like:

- **Aulë** — a private AI assistant the whole family can use via Telegram or Discord
- **Smart home** — lights, thermostats, sensors, and automations around the house
- **Family storage** — photos, documents, and shared files stored on our own hardware
- **This wiki** — the documentation you're reading right now

Everything runs on hardware we own, in our home. Your conversations with Aulë stay here. Your files stay here. Nothing goes to a big tech company's servers unless we've explicitly chosen it.

#### The Names

Everything in Arda is named after places and characters from Tolkien's world (The Lord of the Rings and The Silmarillion). If you're curious, that's a rabbit hole worth exploring — but you don't need to know any of it to use the system.

#### Who Manages It

**Dan** set it up and maintains it. **Noah** and **Jacob** can help if something needs technical attention. For everyday questions, just ask Aulë.

#### Where to Go From Here

- **Want to use the AI assistant?** → See [Aulë — Your AI Assistant](#)
- **Something not working?** → See [If Something Isn't Working](#)
- **Control your smart home?** → See [Using the Smart Home](#)

---

### Aulë — Your AI Assistant

Aulë (pronounced "Ow-leh") is our private AI assistant. Think of it as a family ChatGPT — but one that runs on our own computer at home, not on someone else's servers.

#### How to Use It

**Via Telegram:**
1. Open **Telegram** on your phone or computer
2. Search for **@NavatarBot**
3. Tap **Start** if it's your first time
4. Type your message and send

**Via Discord:**
1. Open **Discord** on your phone or computer
2. Join the **Sung Family** Discord server (ask Dan for an invite link if you haven't joined)
3. Go to the **#aule** channel
4. Type your message

Discord handles conversations better with threaded replies — you can reply directly to Aulë's response to keep a conversation organized.

Aulë responds within a few seconds on either platform.

#### What Aulë Can Do

- Answer questions on almost any topic
- Help with writing, research, ideas, and explanations
- Control smart home devices ("turn off the living room lights")
- Remember your previous messages in the same conversation
- Keep your conversations private from other family members

#### Good to Know

- **Your conversation is private.** Each family member has their own separate memory. Aulë does not share what you said with anyone else.
- **It remembers context.** You can say "what did we just talk about?" and it'll know.
- **It's available 24/7.** Aulë runs on our home server and is always on.
- **It occasionally uses cloud AI.** When the local model can't handle a request, Aulë quietly escalates to a more capable model. This is automatic and transparent to you.

#### If Aulë Isn't Responding

- Wait a minute and try again — the server may be restarting
- If it's been more than 10 minutes, let Noah, Jacob, or Dan know

#### For Power Users: Model Commands

Type any of these in chat to switch Aulë's brain:

| Command | What it does |
|---------|-------------|
| `!local` | Force local model (runs on our GPU) |
| `!fast` | Force GPT-4o mini (cheap, fast) |
| `!smart` | Force Claude Sonnet (best quality) |
| `!help` | Show all available commands |

No command = Aulë chooses automatically.

---

### Using the Smart Home

The smart home runs on **Home Assistant**. It connects and controls smart devices throughout the house — lights, switches, thermostats, sensors, and more.

#### How to Control Things

**Ask Aulë:** The easiest way. Just say "turn off the living room lights" or "set the thermostat to 72."

**Home Assistant app:** Download "Home Assistant" from your phone's app store. Log in with your own account (credentials are in the Sung KeePass DB, or ask Dan).

**Web browser:** Go to http://homeassistant.lan:8123 on home Wi-Fi.

**Physical controls:** Everything still works manually — switches, buttons, thermostats. The smart home is an addition, not a replacement.

#### Wi-Fi for Smart Devices

New smart home devices (plugs, bulbs, cameras) should be on the **neuromancer** Wi-Fi network, not **wintermute**. This keeps them isolated from family computers and phones.

If you're setting up a new smart device, let Dan or Noah know so it can be added to Home Assistant.

#### If Something Isn't Working

**A single device:** Try turning it off and on physically. If it's a bulb, try the physical switch.

**Multiple devices or automations:** Home Assistant may be restarting. Check http://homeassistant.lan:8123 — if it doesn't load, wait a few minutes.

**Ask Aulë:** Describe what's not working and Aulë may be able to help.

---

### Accounts & Passwords

Almost everything in Arda is protected by a password. This page explains how that's organized and where to find what you need.

#### The Sung KeePass Database

All Arda credentials are stored in a password manager called **KeePass**. The database file is called the **Sung KeePass DB**.

If you need a password for anything Arda-related — a login, a Wi-Fi password, an app credential — it's in there.

**Ask Dan, Noah, or Jacob for access to the KeePass DB if you don't already have it.**

#### What's in the KeePass DB

- Wi-Fi passwords (wintermute, neuromancer)
- Arda service logins (this wiki, Grafana, etc.)
- External accounts (Cloudflare, domain registrar, etc.)
- SSH keys and API tokens
- Any other credentials that keep Arda running

#### What Aulë Can and Can't Do With Passwords

Aulë does **not** have access to the KeePass database. If you ask Aulë for a password, it won't know it.

What Aulë *can* do is help you figure out *which* KeePass entry you're looking for.

#### If You're Locked Out

1. Check the Sung KeePass DB first
2. Ask Dan, Noah, or Jacob

---

### If Something Isn't Working

A quick guide for when things go wrong.

#### Start Here

**Ask Aulë first.** Even if Aulë itself is having trouble, try sending it a message — it can often diagnose its own situation or point you in the right direction.

If Aulë isn't responding at all, move to the checklist below.

#### Quick Checklist

**Is the internet working?**
Try loading a website on your phone using mobile data (turn off Wi-Fi first). If that works, the internet is fine — the issue is local.

**Are you on the right Wi-Fi?**
Home devices should be on **wintermute**. If you're on a neighbor's network or a guest network, some Arda features won't work.

**Has it been less than 5 minutes?**
Servers occasionally restart for updates. Wait a few minutes and try again before escalating.

**Is it just one thing, or everything?**
- Just Aulë → see below
- Just smart home → see above
- Everything → likely a network issue, contact Noah, Jacob, or Dan

#### Aulë Isn't Responding

1. Wait 2–3 minutes and try again
2. On Telegram, send `/start` to @NavatarBot to reset the session
3. If still nothing after 10 minutes — let Noah, Jacob, or Dan know

Aulë runs on **Rivendell** (the home server). If that machine is down, Aulë will be unavailable until it comes back up.

#### App or Website Not Loading

If an Arda service (wiki, Grafana, etc.) won't load:

1. Check if you're on **wintermute** Wi-Fi
2. Try the internal URL directly (e.g., http://wiki.sung.us)
3. If nothing works, the server may be down — let Dan or Noah know
