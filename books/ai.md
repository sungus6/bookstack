# AI
> Exported from BookStack on 2026-05-14
> Slug: ai

---

## Contents

- New Page
**For Everyone**
- What is Aulë?
**For Techies**
- AI Stack Architecture
- Model Reference
- Memory System
**Operations**
- Aulë Operations & Troubleshooting
- ha_tools.py - Home Assistant

---

### New Page

_No markdown content. This page was edited in WYSIWYG mode._

---

## Chapter: For Everyone

### What is Aulë?

# What is Aulë?

Aulë is the Arda home AI assistant. You talk to it through Telegram.

In Tolkien's mythology, Aulë is the craftsman of the Valar — the one who creates
and builds things. It felt like the right name for an AI that helps build and
maintain the home network.

## How to Talk to Aulë

Open Telegram and find **@NavatarBot**. Just send it a message like you would any chat.

You can ask it:
- Questions about the house network ("why is the internet slow?")
- General questions ("what's a good recipe for X?")
- Help with tasks ("draft an email to...")
- Smart home control ("turn off the living room lights")
- Technical questions about Arda

## What Aulë Knows

Aulë has persistent memory about Arda — the network, the machines, the services.
It learns automatically from conversations and remembers facts across sessions and
even across full rebuilds. See the Memory System page for details.

Aulë does NOT have access to:
- Passwords or credentials (those stay in KeePass)
- Your personal messages or files
- Cameras or private devices

## Memory Commands

| Command | What it does |
|---|---|
| `!memories` | Show everything Aulë remembers |
| `!remember <fact>` | Manually save a personal memory |
| `!remember shared: <fact>` | Manually save a shared Arda memory |
| `!forget <keyword>` | Delete memories matching a keyword |
| `!reset` | Clear conversation history (memories are kept) |

## Model Commands

| Command | What it does |
|---|---|
| `!local` | Force local model (qwen2.5:7b on Rivendell GPU) |
| `!fast` | Force GPT-4o mini (OpenAI) |
| `!smart` | Force Claude Sonnet (Anthropic) |
| `!genius` | Force Claude Opus (Anthropic, best quality) |
| `!help` | Show all commands |

No command = Aulë auto-routes based on what you're asking.

## When Aulë Isn't Available

Aulë runs on Rivendell. If Rivendell is down or restarting, Aulë won't respond.
Wait a few minutes and try again.

If it's been more than 10 minutes, let Noah, Jacob, or Dan know.

## Aulë and Privacy

All conversations go through Telegram. When using local AI models, your messages
are processed entirely on Rivendell — nothing leaves the house. When using cloud
fallback (OpenAI or Anthropic), messages are sent to those services under Dan's account.


## Chapter: For Techies

---

## Chapter: For Techies

### AI Stack Architecture

# AI Stack Architecture

## Overview

The Arda AI stack provides local LLM inference with cloud fallback, persistent memory,
and home automation control. It runs entirely on Rivendell and is accessed via Telegram
through the Aulë bot (@NavatarBot).

## Components

| Component | Container | Port | Role |
|---|---|---|---|
| Ollama | ollama | 11434 | Local LLM inference (GTX 1060 6GB) |
| LiteLLM | litellm | 4000 | LLM proxy, model routing, cloud fallback |
| openclaw | openclaw | 7000 | Telegram bot, memory, tool orchestration |

## How It Works

```
User (Telegram)
    |
openclaw (Telegram bot — agent.py)
    |-- Identity resolution (who is this user?)
    |-- Memory injection (what does Aulë already know?)
    |
LiteLLM (router)
    |-- local: Ollama on Rivendell GPU
    |-- fast: gpt-4o-mini (OpenAI)
    |-- smart: claude-sonnet (Anthropic)
    +-- genius: claude-opus (Anthropic)
    |
Background (after each reply)
    +-- Memory extraction → memory.db (SQLite)
```

## Model Routing

Aulë auto-routes based on the request type:

| Route | Model | When used |
|---|---|---|
| local | qwen2.5:7b (Ollama) | General conversation, simple questions |
| smart | claude-sonnet | Tool use, home automation, complex tasks |
| fast | gpt-4o-mini | Forced via !fast |
| genius | claude-opus | Forced via !genius |

## GPU Details

Rivendell runs a GTX 1060 6GB for local inference.

| Model Size | Performance |
|---|---|
| 7B parameters | Runs comfortably on GPU |
| 13B parameters | Slow on GPU, may fall to CPU |
| 30B+ parameters | Cloud fallback required |

```bash
# Check GPU status
nvidia-smi

# Check what Ollama currently has loaded
curl http://localhost:11434/api/tags
```

## Stack Location

All AI stack files live at:

```
/mnt/work/ai-stack/
├── docker-compose.yml       ← ollama, litellm, openclaw, grafana, prometheus
├── .env                     ← API keys, bot token
├── litellm/config.yaml      ← model routing config
├── openclaw/
│   ├── agent.py             ← main bot logic, memory system, tool orchestration
│   ├── ha_tools.py          ← Home Assistant integration
│   ├── system_tools.py      ← Rivendell system tools
│   ├── memory.db            ← persistent SQLite memory (backed up to Moria)
│   └── requirements.txt
├── ollama/                  ← model storage
├── grafana/                 ← dashboards
└── prometheus.yml
```

## Environment and Config

All config is in `/mnt/work/ai-stack/.env` and the docker-compose.yml.
API keys for OpenAI and Anthropic are stored there.
All credentials in Sung KeePass DB.

## Logs

```bash
docker logs ollama --tail 50
docker logs litellm --tail 50
docker logs openclaw --tail 50
```

## Restarting the AI Stack

```bash
cd /mnt/work/ai-stack
docker compose restart

# Restart a single container
docker restart openclaw
```

---

### Model Reference

# Model Reference

## Currently Installed Models (Ollama)

```bash
docker exec -it ollama ollama list
```

## Model Management

```bash
# Pull a new model
docker exec -it ollama ollama pull MODEL_NAME

# Remove a model
docker exec -it ollama ollama rm MODEL_NAME

# Show model details
docker exec -it ollama ollama show MODEL_NAME
```

## Recommended Models for GTX 1060 6GB

| Model | Size | Use Case | Speed |
|---|---|---|---|
| qwen2.5:7b | ~4.5GB | General purpose, default | Fast |
| mistral:7b | ~4GB | General purpose | Fast |
| llama3:8b | ~4.7GB | Good quality | Fast |
| phi3:mini | ~2.3GB | Quick tasks | Very fast |
| codellama:7b | ~3.8GB | Code assistance | Fast |

Models larger than ~5GB will exceed VRAM and fall back to CPU (very slow).

## Cloud Models (via LiteLLM)

| Model | Alias | Provider | Notes |
|---|---|---|---|
| gpt-4o-mini | fast | OpenAI | Cost-effective, reliable JSON output |
| claude-sonnet | smart | Anthropic | Higher quality, used for tool calls |
| claude-opus | genius | Anthropic | Highest quality, highest cost |

Cloud models require valid API keys in `/mnt/work/ai-stack/.env`.
API keys in Sung KeePass DB.

## Adding a New Model to LiteLLM Routing

1. Pull the model: `docker exec -it ollama ollama pull MODEL_NAME`
2. Edit `/mnt/work/ai-stack/litellm/config.yaml`
3. Add model definition to the model list
4. Restart LiteLLM: `docker restart litellm`
5. Test: `curl http://localhost:4000/chat/completions -H "Content-Type: application/json" -d '{"model": "MODEL_NAME", "messages": [{"role": "user", "content": "Hello"}]}'`


## Chapter: Operations

---

### Memory System

# Memory System

## Overview

Aulë has two layers of memory:

| Layer | Storage | Scope | Survives reset? | Survives rebuild? |
|---|---|---|---|---|
| Conversation history | SQLite messages table | Per chat session | ❌ (!reset clears it) | ✅ (volume mounted) |
| Persistent memory | SQLite memories table | Shared + per user | ✅ | ✅ |

## How Memory Works

**Automatic extraction:** After every conversation turn, Aulë runs a background call
to GPT-4o mini to extract facts worth remembering. No user action required.

**Automatic injection:** Every message Aulë receives is silently prefixed with
relevant shared memories and the user's personal memories before the LLM sees it.
This is invisible to the user — Aulë simply knows.

**Two scopes:**
- `shared` — facts about Arda that everyone benefits from (IPs, topology, TODOs)
- `<user_id>` — personal facts about a specific user (preferences, context)

## User Identity

Aulë maps channel identities to named users. The same person talking via Telegram
today and a web UI tomorrow will share the same memories.

| User | user_id | Channel |
|---|---|---|
| Dan | manwe | Telegram |
| Noah | (self-registers on first message) | — |
| Jacob | (self-registers on first message) | — |

New users are asked for their name on first contact and registered automatically.

## Current Shared Memories

*Last updated: 2026-05-06*

- Arda is a home lab running on personal hardware with Tolkien-themed naming. Owner: Dan (manwe). Technical support: Noah and Jacob.
- Rivendell is the primary server running Ubuntu/Docker at 192.168.10.4.
- Moria is the NAS running Synology DSM at 192.168.10.6 / .7.
- Palantir is the management machine running Debian at 192.168.99.21.
- Minasmorgul is a Windows workstation at 192.168.10.16.
- MikroTik RB750GL is the router at 192.168.99.1.
- Zyxel GS1900-24HP is the switch at 192.168.99.2.
- Home Assistant manages smart home features at 192.168.10.10.
- Key services on Rivendell: Ollama (GTX 1060 6GB GPU inference), LiteLLM, openclaw (Telegram bot), Prometheus, Grafana, Portainer, Cloudflared.
- BookStack wiki is available at https://wiki.sung.us.
- Outstanding TODOs: BookStack nightly exporter, scheduled backups via openclaw, clean up /data/compose -OLD-REMOVE dirs, Smart Home device inventory, verify minasanor DHCP lease on MikroTik.

## Memory File Location

```
/mnt/work/ai-stack/openclaw/memory.db
```

This file is volume-mounted into the openclaw container and is included in the
Rivendell backup script (backed up to Palantir and Moria nightly).

## Memory Commands (Telegram)

```
!memories              — show all shared and personal memories
!remember <fact>       — save a personal memory manually
!remember shared: <fact>  — save a shared Arda memory manually
!forget <keyword>      — delete memories matching keyword
!reset                 — clear conversation history (NOT memories)
```

## Updating This Page

This page should be updated manually when significant new Arda facts are established.
The `!memories` command always shows the live state of Aulë's memory.

---

## Chapter: Operations

### Aulë Operations & Troubleshooting

# Aulë Operations & Troubleshooting

## Checking Stack Health

```bash
# Quick status check — all should show "Up"
docker ps | grep -E "ollama|litellm|openclaw"

# If any show "Exited" or "Restarting" — check logs
docker logs CONTAINER_NAME --tail 30
```

## Restarting Individual Components

```bash
docker restart openclaw   # Telegram bot + memory
docker restart litellm    # LLM router
docker restart ollama     # Local inference (clears VRAM)
```

## Full Stack Restart

```bash
cd /mnt/work/ai-stack
docker compose down && docker compose up -d
```

## Testing Each Layer

**Test Ollama directly:**
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "Say hello",
  "stream": false
}'
```

**Test LiteLLM:**
```bash
curl http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-local-dev" \
  -d '{"model": "local", "messages": [{"role": "user", "content": "Hello"}]}'
```

**Test openclaw:**
```bash
curl http://localhost:7000/
```

## Common Issues

**Aulë not responding in Telegram:**
1. Check openclaw is running: `docker ps | grep openclaw`
2. Check logs: `docker logs openclaw --tail 30`
3. Check LiteLLM is reachable: `curl http://localhost:4000/health`
4. Restart: `docker restart openclaw`

**Memory not extracting (check with `docker logs openclaw 2>&1 | grep memory`):**
- Should see `[memory] saved [scope]: fact` lines after each conversation
- If silent, check LiteLLM connectivity and API keys

**Slow responses:**
- GPU may be under load: `nvidia-smi`
- Ollama loading a model from disk: first request after idle is slow
- Check if cloud fallback is active: `docker logs litellm --tail 20`

**Out of GPU memory:**
```bash
docker restart ollama   # clears loaded models from VRAM
```

**LiteLLM routing issues:**
```bash
docker logs litellm --tail 50 -f
```

**Cloud API errors:**
- Check API keys are valid and have credits
- Keys in `/mnt/work/ai-stack/.env` and Sung KeePass DB

## openclaw Configuration

All config in `/mnt/work/ai-stack/docker-compose.yml` and `.env`.

Key settings:
- `TELEGRAM_BOT_TOKEN` — bot token from BotFather
- `OPENAI_BASE_URL` — points to LiteLLM (http://litellm:4000/v1)
- `HA_URL` / `HA_TOKEN` — Home Assistant access
- `AULE_SYSTEM_PROMPT` — Aulë's personality (optional override)

To update system prompt: set `AULE_SYSTEM_PROMPT` in `.env`, then `docker restart openclaw`.

---

### ha_tools.py - Home Assistant

# ha_tools.py — Home Assistant Integration

Aulë can control Home Assistant entities directly from Telegram.

## Available Functions

| Function | Description |
|---|---|
| `get_state(entity_id)` | Get current state of any HA entity |
| `get_all_states(domains)` | Get states filtered by domain |
| `turn_on(entity_id)` | Turn on lights, switches, etc. |
| `turn_off(entity_id)` | Turn off lights, switches, etc. |
| `trigger_scene(scene_id)` | Activate a scene |
| `set_climate(entity_id, temperature, hvac_mode)` | Control thermostats |
| `trigger_automation(automation_id)` | Trigger an automation |
| `trigger_script(script_id)` | Run a HA script |

## Configuration

```
HA_URL=http://192.168.10.10:8123
HA_TOKEN=<long-lived access token>
```

Both set in `/mnt/work/ai-stack/.env` and Sung KeePass DB.

## Example Telegram Usage

```
turn off the living room lights
set the thermostat to 70
activate the good night scene
what's the temperature downstairs?
```

Aulë will call the appropriate HA function automatically — no special syntax needed.

---
