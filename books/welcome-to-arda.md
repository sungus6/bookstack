# Welcome to Arda
> Exported from BookStack on 2026-05-14
> Slug: welcome-to-arda

---

## Contents

- What is Arda?
- Aulë — Your Home AI
- Accounts & Passwords
- If Something Isn't Working

---

### What is Arda?

# What is Arda?

Arda is our home technology system — a small network of computers, storage, and software
that runs quietly in the background of our house.

It handles things like:

- **Aulë** — a private AI assistant the whole family can use, available on your phone
- **Smart home** — lights, thermostats, sensors, and automations around the house
- **Family storage** — photos, documents, and shared files stored on our own hardware
- **This wiki** — the documentation you're reading right now

Everything runs on hardware we own, in our home. Your conversations with Aulë stay here.
Your files stay here. Nothing goes to a big tech company's servers unless we've explicitly
chosen it.

---

## The Names

Everything in Arda is named after places and characters from Tolkien's world. If you're
curious, that's a rabbit hole worth exploring — but you don't need to know any of it to
use the system.

---

## Who Manages It

Dad set it up and maintains it. Noah and Jacob can help if something needs technical
attention. For everyday questions, just ask Aulë.

---

## Where to Go From Here

- **Want to use the AI assistant?** → See [Aulë — Your Home AI](02-aule-your-home-ai.md)
- **Something not working?** → See [If Something Isn't Working](04-if-something-isnt-working.md)
- **Looking for a password?** → See [Accounts & Passwords](03-accounts-and-passwords.md)

---

### Aulë — Your Home AI

# Aulë — Your Home AI

Aulë (pronounced "Ow-leh") is our private AI assistant. Think of it like a family
ChatGPT — but one that runs on our own computer at home, not on someone else's servers.

---

## How to Use It

1. Open **Telegram** on your phone or computer
2. Search for **@NavatarBot**
3. Tap **Start** if it's your first time
4. Type your message and send

That's it. Aulë will respond within a few seconds.

---

## What Aulë Can Do

- Answer questions on almost any topic
- Help with writing, research, ideas, and explanations
- Remember your last several messages so you can refer back to earlier parts of the conversation
- Keep your conversations completely private from other family members

---

## Good to Know

- **Your conversation is private.** Each family member has their own separate memory.
  Aulë does not share what you said with anyone else.
- **It remembers context.** You can say "what did we just talk about?" or refer back
  to something earlier in the same conversation.
- **It's available 24/7.** Aulë runs on our home server and is always on.
- **It occasionally uses cloud AI.** When the local model can't handle a request,
  Aulë quietly escalates to a more capable (cloud-based) model. This is automatic
  and transparent to you.

---

## If Aulë Isn't Responding

- Wait a minute and try again — the server may be restarting
- If it's been more than 10 minutes, let Noah, Jacob, or Dad know

---

### Accounts & Passwords

# Accounts & Passwords

Almost everything in Arda is protected by a password. This page explains how that's organized and where to find what you need.

---

## The Sung KeePass Database

All Arda credentials are stored in a password manager called **KeePass**. The database file is called the **Sung KeePass DB**.

If you need a password for anything Arda-related — a login, a Wi-Fi password, an app credential — it's in there.

**Ask Dad, Noah, or Jacob for access to the KeePass DB if you don't already have it.**

---

## What's in the KeePass DB

- Wi-Fi passwords (home networks)
- Arda service logins (this wiki, Grafana, etc.)
- External accounts associated with Arda (Cloudflare, domain registrar, etc.)
- SSH keys and API tokens for technical use
- Any other credentials that keep Arda running

---

## What Aulë Can and Can't Do With Passwords

Aulë does **not** have access to the KeePass database. If you ask Aulë for a password, it won't know it.

What Aulë *can* do is help you figure out *which* entry in KeePass you're looking for, or walk you through how to use a credential once you have it.

---

## If You're Locked Out of Something

1. Check the Sung KeePass DB first
2. Ask Aulë — it may be able to help you navigate the login process
3. Ask Dad, Noah, or Jacob

---

## A Note on Security

Passwords for Arda services are not shared in this wiki, in chat, or in any document that isn't the KeePass DB. If someone sends you a password in a message and says it's for Arda, treat that with skepticism and verify with Dad.

---

### If Something Isn't Working

# If Something Isn't Working

A quick guide for when things go wrong.

---

## Start Here

**Ask Aulë first.** Even if Aulë itself is having trouble, try sending it a message — it can often diagnose its own situation or point you in the right direction.

If Aulë isn't responding at all, move to the checklist below.

---

## Quick Checklist

**Is the internet working?**
Try loading a website on your phone using mobile data (turn off Wi-Fi first). If that works, the internet is fine — the issue is local.

**Are you on the right Wi-Fi?**
Home devices should be on **wintermute**. If you're on a neighbor's network or a guest network, some Arda features won't work.

**Has it been less than 5 minutes?**
Servers occasionally restart for updates. Wait a few minutes and try again before escalating.

**Is it just one thing, or everything?**
- Just Aulë → see below
- Just smart home → see below
- Everything → likely a network issue, contact Noah, Jacob, or Dad

---

## Aulë Isn't Responding

1. Wait 2–3 minutes and try again
2. Send the message `/start` to @NavatarBot in Telegram to reset the session
3. If still nothing after 10 minutes — let Noah, Jacob, or Dad know

Aulë runs on the home server (Minasanor). If that machine is down or restarting, Aulë will be unavailable until it comes back up.

---

## Smart Home Isn't Working

(lights, thermostats, automations, etc.)

1. Check if the device works manually (physical switch, thermostat buttons, etc.)
2. Try the Home Assistant app if you have it
3. If multiple devices are affected — the Home Assistant server may be down. Contact Noah, Jacob, or Dad.

---

## This Wiki Isn't Loading

The wiki (library.sung.us) runs on the home server. If you can't reach it:

1. Try from inside the house on Wi-Fi
2. If it works at home but not remotely — there may be a Cloudflare or internet issue
3. If it doesn't work at home either — the server may be down. Contact Noah, Jacob, or Dad.

---

## Who to Contact

| Situation | Contact |
|---|---|
| Quick question or general help | Ask Aulë |
| Technical problem, server down | Noah or Jacob |
| Something critical or unknown | Dad |

---

## What to Tell Them

When you reach out for help, it's useful to include:
- What you were trying to do
- What happened (or didn't happen)
- Whether it worked before, and when it last worked
- What device and network you're on

---
