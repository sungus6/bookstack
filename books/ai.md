# AI
> Slug: ai

---

## Contents

- What is Aulë?
- Architecture
- Model Aliases & Providers
- Platforms (Telegram, Discord)
- Capabilities & Privacy
- Troubleshooting
- Operations
- Configuration Reference

---

### What is Aulë?

Aulë (pronounced "Ow-leh") is the family AI assistant. It's a private, always-on assistant that the whole family can use via Telegram or Discord.

Think of it as a family ChatGPT — but one that runs on our own computer at home. Your conversations with Aulë stay on our hardware. Nothing goes to a big tech company's servers unless the local model can't handle a request and it temporarily escalates to a cloud model.

Aulë responds within a few seconds on either platform.

#### Quick Start for Family Members

- **Telegram:** Search for @NavatarBot and start chatting. One conversation at a time.
- **Discord:** In the #aule channel on the Sung Family server. Better for threaded replies.
- **No command needed** — Aulë picks the best model automatically. You can override:
  - `use local` — forces local only (slower, but stays in the house)
  - `use fast` — fast cloud model (gpt-4o-mini)
  - `use smart` — best model (claude-sonnet-4)
  - `use genius` — most capable, most expensive (claude-opus-4-7)

#### What Aulë Can Do

- Answer questions using general knowledge
- Control smart home devices ("turn off the living room lights")
- Look up information stored in the family wiki
- Search the web when needed
- Help with passwords (knows *which* KeePass entry, but cannot access the vault itself)
- Diagnose its own problems

#### What Aulë Cannot Do

- Access the KeePass password vault directly
- Remember what you said in another family member's conversation (each person has separate memory)
- Control devices it doesn't know about (ask Dan to add new ones)

#### Privacy

Each family member has their own separate memory. Aulë does not share what you said with anyone else. Conversations are private to you. The local model runs entirely on Rivendell's GPU — when using `use local`, no data leaves the house.

---

### Architecture

```
hermes (gateway)
  ├── Telegram bot (@NavatarBot)
  ├── Discord bot (Aulë#6535)
  └── Tools layer (BookStack, Home Assistant, Google, etc.)
        │
        ▼
litellm (LLM proxy / router)
  ├── ollama (local) — qwen2.5:3b
  ├── DeepSeek V4 (primary cloud)
  └── Fallbacks: gpt-4o-mini → claude-sonnet-4 → claude-opus-4-7
```

#### Component Details

**Hermes** — the Aulë agent itself. Runs as a Docker container (`hermes`) in the ai-stack. It's the gateway that handles:
- Incoming messages from Telegram and Discord
- Tool execution (BookStack API, Home Assistant API, web search)
- Memory persistence per user
- Model routing via LiteLLM

**LiteLLM** — the LLM proxy/routing layer between Hermes and the LLM backends. Config: `/mnt/work/ai-stack/config/litellm.yaml`. It handles:
- Model routing (local → cloud → fallback)
- Key management for cloud providers
- Rate limiting and failover

**Ollama** — runs the local LLM for inference. Port 11434. Uses the NVIDIA GTX 1060 6GB GPU. Currently loaded model: `qwen2.5:3b` with context window set to 32768 tokens.

| Component | Port | Docker Image | Config |
|-----------|------|-------------|--------|
| ollama | 11434 | ollama/ollama | `/mnt/work/ai-stack/config/` |
| litellm | 4000 | ghcr.io/berriai/litellm | `/mnt/work/ai-stack/config/litellm.yaml` |
| hermes | — | (custom Dockerfile) | `/mnt/work/ai-stack/config.yaml` |

All components are in the ai-stack Docker compose at `/mnt/work/ai-stack/docker-compose.yml`.

---

### Model Aliases & Providers

| Alias | Actual Model | Priority | Notes |
|-------|-------------|----------|-------|
| `default` | DeepSeek V4 | Primary | Good balance of speed and quality |
| `local` | qwen2.5:3b (Ollama) | Falls back: fast → smart | Runs entirely on home GPU. Slower but private |
| `fast` | gpt-4o-mini | Cheap, fast | Best for quick answers |
| `smart` | claude-sonnet-4 | Best quality | Slower but most capable for complex tasks |
| `genius` | claude-opus-4-7 | Most expensive | Best of the best, use sparingly |
| `haiku` | claude-haiku-4-5 | Fast, cheap | Good for simple queries |

**Provider resolution order by alias:**
- `local`: ollama → gpt-4o-mini → claude-sonnet-4
- `default`: DeepSeek V4 → claude-sonnet-4 → claude-opus-4-7
- `fast`: gpt-4o-mini → claude-sonnet-4 → claude-opus-4-7
- `smart`: claude-sonnet-4 → claude-opus-4-7

If a provider key is missing, the alias falls through to the next in chain. "No connected db" errors mean an LLM provider key is missing.

#### Provider Accounts

| Provider | Purpose | Key Location |
|----------|---------|-------------|
| OpenRouter | DeepSeek V4, Claude models | Sung KeePass DB |
| OpenAI | gpt-4o-mini | Sung KeePass DB |
| Anthropic | Claude models | Sung KeePass DB |
| Ollama | Local (free) | N/A — runs on Rivendell |

---

### Platforms (Telegram, Discord)

#### Telegram (@NavatarBot)

- **Bot:** @NavatarBot
- **Single conversation** — no threading
- Always available if Rivendell is up

#### Discord (Aulë#6535)

- **Channel:** #aule on the Sung Family server
- **Threaded replies** — you can reply directly to Aulë's response to keep context
- Better for organized conversations
- Bot ID: 1506432794149130453

#### If Aulë Isn't Responding

1. Check if Rivendell is power-cycled — Aulë runs on the server. If Rivendell is down, Aulë is down.
2. Type any model command: `use local`, `use fast`, `use smart`, `use genius`
3. If nothing works, try Telegram and Discord both — one may work if the other is having a connection issue
4. Still broken? Ask Dan or check Rivendell:
   ```bash
   docker ps | grep hermes
   docker logs hermes --tail 50
   ```

#### Model Switching

Type any of these in chat to switch Aulë's brain:

```
use local     — Forces local Ollama model only (slower but private)
use fast      — gpt-4o-mini (cheap, fast)
use smart     — claude-sonnet-4 (best quality)
use genius    — claude-opus-4-7 (most capable, most expensive)
use haiku     — claude-haiku-4-5 (fast, cheap)
```

No command = Aulë chooses automatically (default alias).

---

### Capabilities & Privacy

#### Smart Home Control

Aulë can control Home Assistant devices. Just say things like:
- "Turn off the living room lights"
- "Set the thermostat to 72"
- "Lock the front door"

Requires Rivendell to be running and Home Assistant to be online. Aulë uses the Home Assistant API to execute commands — it cannot control devices that aren't added to Home Assistant.

#### BookStack Wiki Access

Aulë can read from and write to the family wiki. It looks up information when you ask questions like "What's the WiFi password?" or "Who is our internet provider?"

#### Web Access

Aulë can search the web for current information when needed. This only happens when explicitly useful — Aulë doesn't phone home for every query.

#### Memory

Each family member has their own separate memory. Aulë remembers facts you've told it across conversations, but does not share your memory with other family members. Memory can be cleared on request.

#### Password Handling

Aulë does **not** have access to the KeePass database. If you ask Aulë for a password, it won't know the actual value. What it *can* do is help you figure out *which* KeePass entry you're looking for — e.g., "your Netflix password is in KeePass under 'Streaming Services'."

---

### Troubleshooting

#### Aulë Stops Responding

1. **Try a different model:** `use fast` or `use smart`
2. **Try the other platform:** If Discord is down, try Telegram, or vice versa
3. **Check Rivendell:**

   ```bash
   ssh aule@rivendell.lan
   docker ps | grep hermes
   ```

   If hermes isn't running:
   ```bash
   cd /mnt/work/ai-stack
   docker compose ps
   docker compose logs --tail=50
   ```

4. **Check LiteLLM is routing properly:**
   ```bash
   curl http://localhost:4000/v1/models
   ```
   Empty response = LiteLLM is down or misconfigured.

5. **Check Ollama is running:**
   ```bash
   curl http://localhost:11434/api/tags
   curl http://localhost:11434/api/generate -d '{"model":"qwen2.5:3b","prompt":"hello"}'
   ```

#### "No connected db" Errors

This means an LLM provider key is missing or expired. Check:
- OpenRouter API key in LiteLLM config
- Claude/Anthropic API key
- OpenAI API key

All keys are in the Sung KeePass DB. After updating, restart LiteLLM:
```bash
docker restart litellm
```

#### GPU Issues

If Ollama is running slow or erroring:
```bash
# Check GPU is visible to Docker
docker exec ollama nvidia-smi

# Check Ollama logs
docker logs ollama --tail 50

# Restart Ollama
docker restart ollama
```

---

### Operations

```bash
# Check ai-stack status
cd /mnt/work/ai-stack && docker compose ps

# Check LLM proxy is responding
curl http://localhost:4000/v1/models

# Check what models Ollama has loaded
curl http://localhost:11434/api/tags

# Restart Hermes (Aulë)
docker restart hermes

# Restart LiteLLM
docker restart litellm

# Restart Ollama
docker restart ollama

# View Hermes logs
docker logs hermes --tail 100

# Full AI stack restart
cd /mnt/work/ai-stack && docker compose down && docker compose up -d

# View all logs at once
cd /mnt/work/ai-stack && docker compose logs --tail=50 -f
```

#### Updating a Model Alias

Edit `/mnt/work/ai-stack/config/litellm.yaml` and restart LiteLLM:
```bash
docker restart litellm
```

#### Adding a New Cloud Provider

1. Get API key from the provider
2. Add key to `/mnt/work/ai-stack/config/litellm.yaml`
3. Add the key to Sung KeePass DB
4. Add a model alias in the config
5. Restart LiteLLM: `docker restart litellm`

---

### Configuration Reference

#### Key Files

| File | Purpose |
|------|---------|
| `/mnt/work/ai-stack/docker-compose.yml` | All AI containers |
| `/mnt/work/ai-stack/config/litellm.yaml` | LLM routing, providers, aliases |
| `/mnt/work/ai-stack/config.yaml` | Hermes agent configuration (models, tools, skills) |
| `/mnt/work/ai-stack/config/hermes.env` | Environment secrets for Hermes |

#### LiteLLM Model Config Structure

```yaml
model_list:
  - model_name: "deepseek-v4"
    litellm_params:
      model: "openrouter/deepseek/deepseek-v4"
      api_key: "${OPENROUTER_API_KEY}"

router_settings:
  routing_strategy: "latency-based-routing"
  fallbacks:
    - "deepseek-v4": ["claude-sonnet-4"]
    - "claude-sonnet-4": ["claude-opus-4-7"]
```
