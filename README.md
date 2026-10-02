<p align="center">
  <img src="assets/banner.png" alt="VAEL" width="100%">
</p>

# VAEL

> **VAEL is based on Hermes Agent by Nous Research (MIT license, Copyright (c) 2025 Nous Research). Upstream: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent). See [NOTICE](NOTICE) and [LICENSE](LICENSE).**

<p align="center">
  <a href="https://github.com/sunnatilla0717/vael-agent">VAEL</a> | <a href="https://github.com/sunnatilla0717/vael-agent">VAEL Desktop</a>
</p>
<p align="center">
  <a href="https://github.com/sunnatilla0717/vael-agent/tree/main/website/docs"><img src="https://img.shields.io/badge/Docs-local_website-docs-FFD700?style=for-the-badge" alt="Documentation"></a>
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://github.com/sunnatilla0717/vael-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://nousresearch.com"><img src="https://img.shields.io/badge/Built%20by-Nous%20Research-blueviolet?style=for-the-badge" alt="Built by Nous Research"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ur-pk.md"><img src="https://img.shields.io/badge/Lang-اردو-green?style=for-the-badge" alt="اردو"></a>
  <a href="README.es.md"><img src="https://img.shields.io/badge/Lang-Español-orange?style=for-the-badge" alt="Español"></a>
</p>

**The self-improving AI agent, part of the CyberAI product family.** It's the only agent with a built-in learning loop — it creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions. Run it on a $5 VPS, a GPU cluster, or serverless infrastructure that costs nearly nothing when idle. It's not tied to your laptop — talk to it from Telegram while it works on a cloud VM.

Use any model you want — OpenRouter, OpenAI, your own endpoint, and many others (see `website/docs/integrations/providers.md`). Switch with `vael model` — no code changes, no lock-in.

<table>
<tr><td><b>A real terminal interface</b></td><td>Full TUI with multiline editing, slash-command autocomplete, conversation history, interrupt-and-redirect, and streaming tool output.</td></tr>
<tr><td><b>Lives where you do</b></td><td>Telegram, Discord, Slack, WhatsApp, Signal, and CLI — all from a single gateway process. Voice memo transcription, cross-platform conversation continuity.</td></tr>
<tr><td><b>A closed learning loop</b></td><td>Agent-curated memory with periodic nudges. Autonomous skill creation after complex tasks. Skills self-improve during use. FTS5 session search with LLM summarization for cross-session recall. <a href="https://github.com/plastic-labs/honcho">Honcho</a> dialectic user modeling. Compatible with the <a href="https://agentskills.io">agentskills.io</a> open standard.</td></tr>
<tr><td><b>Scheduled automations</b></td><td>Built-in cron scheduler with delivery to any platform. Daily reports, nightly backups, weekly audits — all in natural language, running unattended.</td></tr>
<tr><td><b>Delegates and parallelizes</b></td><td>Spawn isolated subagents for parallel workstreams. Write Python scripts that call tools via RPC, collapsing multi-step pipelines into zero-context-cost turns.</td></tr>
<tr><td><b>Runs anywhere, not just your laptop</b></td><td>Seven terminal backends — local, Docker, SSH, Singularity, Modal, Daytona, and Vercel Sandbox. Daytona and Modal offer serverless persistence — your agent's environment hibernates when idle and wakes on demand, costing nearly nothing between sessions. Run it on a $5 VPS or a GPU cluster.</td></tr>
<tr><td><b>Research-ready</b></td><td>Batch trajectory generation, trajectory compression for training the next generation of tool-calling models.</td></tr>
</table>

---

## Quick Install

### VAEL — source dan yuklab olish

```bash
git clone https://github.com/sunnatilla0717/vael-agent.git
cd vael-agent
```

### Linux, macOS, WSL2

```bash
cd vael-agent
source ./activate
vael              # start chatting!
```

### Windows (PowerShell)

```powershell
cd vael-agent
. .\activate.ps1
vael              # start chatting!
```

After installation:

```bash
source ~/.bashrc    # reload shell (or: source ~/.zshrc)
vael                # start chatting!
```

### Troubleshooting

#### Windows Defender or antivirus flags `uv.exe` as malware

If your antivirus (Bitdefender, Windows Defender, etc.) quarantines `uv.exe` from the Hermes `bin` folder (`%LOCALAPPDATA%\hermes\bin\uv.exe`), this is a **false positive**. The file is Astral's `uv` — the Rust Python package manager Hermes bundles to manage its Python environment. ML-based antivirus engines commonly flag unsigned Rust binaries that download and install packages.

**To verify your copy is authentic:**

```powershell
# Install GitHub CLI if needed
winget install --id GitHub.cli

# Login to GitHub
gh auth login

# Run verification
$uv = "$env:LOCALAPPDATA\hermes\bin\uv.exe"
$ver = (& $uv --version).Split(' ')[1]
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$zip = "$env:TEMP\uv.zip"
Invoke-WebRequest "https://github.com/astral-sh/uv/releases/download/$ver/uv-x86_64-pc-windows-msvc.zip" -OutFile $zip -UseBasicParsing
gh attestation verify $zip --repo astral-sh/uv
Expand-Archive $zip "$env:TEMP\uv_x" -Force
(Get-FileHash "$env:TEMP\uv_x\uv.exe").Hash -eq (Get-FileHash $uv).Hash
```

If attestation says "Verification succeeded" and the last line prints `True`, you're good.

**To whitelist Hermes:**
- **Windows Defender:** Run PowerShell as Admin → `Add-MpPreference -ExclusionPath "$env:LOCALAPPDATA\hermes\bin"`
- **Bitdefender:** Add an exception in the Bitdefender console (Protection > Antivirus > Settings > Manage Exceptions)
- Whitelist the **folder**, not the file hash — Hermes updates `uv` and the hash changes every version

For more context, see the upstream Astral reports: [astral-sh/uv#13553](https://github.com/astral-sh/uv/issues/13553), [astral-sh/uv#15011](https://github.com/astral-sh/uv/issues/15011), [astral-sh/uv#10079](https://github.com/astral-sh/uv/issues/10079).

---

## Getting Started

```bash
vael              # Interactive CLI — start a conversation
vael model        # Choose your LLM provider and model
vael tools        # Configure which tools are enabled
vael config set   # Set individual config values
vael config get   # Print individual config values
vael gateway      # Start the messaging gateway (Telegram, Discord, etc.)
vael setup        # Run the full setup wizard (configures everything at once)
vael claw migrate # Migrate from OpenClaw (if coming from OpenClaw)
vael update       # Update to the latest version
vael doctor       # Diagnose any issues
```

📖 **Full documentation lives in this repo: [`website/docs/`](website/docs/)**

---

## Skip the API-key collection — Nous Portal (optional)

VAEL works with whatever provider you want — that's not changing. But if you'd rather not collect five separate API keys for the model, web search, image generation, TTS, and a cloud browser, **Nous Portal** covers all of them under one subscription:

- **300+ models** — pick any of them with `/model <name>`
- **Tool Gateway** — web search, image generation (FAL), text-to-speech (OpenAI), cloud browser (Browser Use), all routed through your sub. No extra accounts.

One command from a fresh install:

```bash
vael setup --portal
```

That logs you in via OAuth, sets Nous as your provider, and turns on the Tool Gateway. Check what's wired up any time with `vael portal info`. Full details in [`website/docs/user-guide/features/tool-gateway.md`](website/docs/user-guide/features/tool-gateway.md).

You can still bring your own keys per-tool whenever you want — the gateway is per-backend, not all-or-nothing.

---

## CLI vs Messaging Quick Reference

VAEL has two entry points: start the terminal UI with `vael`, or run the gateway and talk to it from Telegram, Discord, Slack, WhatsApp, Signal, or Email. Once you're in a conversation, many slash commands are shared across both interfaces.

| Action                         | CLI                                       | Messaging platforms                                                          |
| ------------------------------ | ----------------------------------------- | ---------------------------------------------------------------------------- |
| Start chatting                 | `vael`                                    | Run `vael gateway setup` + `vael gateway start`, then send the bot a message |
| Start fresh conversation       | `/new` or `/reset`                            | `/new` or `/reset`                                                               |
| Change model                   | `/model [provider:model]`                     | `/model [provider:model]`                                                        |
| Set a personality              | `/personality [name]`                         | `/personality [name]`                                                            |
| Retry or undo the last turn    | `/retry`, `/undo`                             | `/retry`, `/undo`                                                                |
| Compress context / check usage | `/compress`, `/usage`, `/insights [--days N]` | `/compress`, `/usage`, `/insights [days]`                                        |
| Browse skills                  | `/skills` or `/<skill-name>`                  | `/<skill-name>`                                                                  |
| Interrupt current work         | `Ctrl+C` or send a new message                | `/stop` or send a new message                                                    |
| Platform-specific status       | `/platforms`                                  | `/status`, `/sethome`                                                            |

For the full command lists, see the CLI guide (`website/docs/user-guide/cli.md`) and the Messaging Gateway guide (`website/docs/user-guide/messaging.md`).

---

## Documentation

All documentation lives in this repo under [`website/docs/`](website/docs/):

| Section              | What's Covered                                             |
| -------------------- | ---------------------------------------------------------- |
| Quickstart           | `website/docs/getting-started/quickstart.md` — install → setup → first conversation in 2 minutes |
| CLI Usage            | `website/docs/user-guide/cli.md` — commands, keybindings, personalities, sessions |
| Configuration        | `website/docs/user-guide/configuration.md` — config file, providers, models, all options |
| Messaging Gateway    | `website/docs/user-guide/messaging.md` — Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| Security             | `website/docs/user-guide/security.md` — command approval, DM pairing, container isolation |
| Tools & Toolsets     | `website/docs/user-guide/features/tools.md` — 40+ tools, toolset system, terminal backends |
| Skills System        | `website/docs/user-guide/features/skills.md` — procedural memory, Skills Hub, creating skills |
| Memory               | `website/docs/user-guide/features/memory.md` — persistent memory, user profiles, best practices |
| MCP Integration      | `website/docs/user-guide/features/mcp.md` — connect any MCP server for extended capabilities |
| Cron Scheduling      | `website/docs/user-guide/features/cron.md` — scheduled tasks with platform delivery |
| Context Files        | `website/docs/user-guide/features/context-files.md` — project context that shapes every conversation |
| Architecture         | `website/docs/developer-guide/architecture.md` — project structure, agent loop, key classes |
| Contributing         | `website/docs/developer-guide/contributing.md` — development setup, PR process, code style |
| CLI Reference        | `website/docs/reference/cli-commands.md` — all commands and flags |
| Environment Variables| `website/docs/reference/environment-variables.md` — complete env var reference |

---

## Migrating from OpenClaw

If you're coming from OpenClaw, VAEL can automatically import your settings, memories, skills, and API keys.

**During first-time setup:** The setup wizard (`vael setup`) automatically detects `~/.openclaw` and offers to migrate before configuration begins.

**Anytime after install:**

```bash
vael claw migrate              # Interactive migration (full preset)
vael claw migrate --dry-run    # Preview what would be migrated
vael claw migrate --preset user-data   # Migrate without secrets
vael claw migrate --overwrite  # Overwrite existing conflicts
```

What gets imported:

- **SOUL.md** — persona file
- **Memories** — MEMORY.md and USER.md entries
- **Skills** — user-created skills → `~/.hermes/skills/openclaw-imports/`
- **Command allowlist** — approval patterns
- **Messaging settings** — platform configs, allowed users, working directory
- **API keys** — allowlisted secrets (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS assets** — workspace audio files
- **Workspace instructions** — AGENTS.md (with `--workspace-target`)

See `vael claw migrate --help` for all options, or use the `openclaw-migration` skill for an interactive agent-guided migration with dry-run previews.

---

## Contributing

We welcome contributions! See the [Contributing Guide](CONTRIBUTING.md) for development setup, code style, and PR process.

Start with the [PM developer workflow](website/docs/reference/package-management.md#developer-workflow)
for activation, daily use, dependency changes, and leaving the environment.
[Development Setup](CONTRIBUTING.md#development-setup) covers the separate test environment and verification commands.

---

## Community

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/sunnatilla0717/vael-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — Linux desktop-control MCP server for VAEL and other MCP hosts, with AT-SPI accessibility trees, Wayland/X11 input, screenshots, and compositor window targeting.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Community WeChat bridge: Run VAEL Agent and OpenClaw on the same WeChat account.

---

## License

MIT — see [LICENSE](LICENSE).

Built by [Nous Research](https://nousresearch.com).
