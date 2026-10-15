# ARIA: Autonomous Reasoning & Interaction Agent

> **Total Cost of Ownership (TCO):** \$0.00 / month  
> **Infrastructure:** 100% Permanent Free-Tier Cloud & Open-Source Software  
> **Architecture Pattern:** Git-Native Stateful ReAct & Plan-and-Execute Agent  

---

## Overview

**ARIA** is a production-grade, fully autonomous personal AI assistant capable of managing email, reviewing pull requests, diagnosing repository issues, and self-maintaining code without incurring a single cent in infrastructure or LLM inference costs.

Unlike traditional agents that rely on expensive always-on server clusters or paid proprietary API tokens, ARIA bridges ephemeral serverless runners (GitHub Actions) with persistent state stores (Git + Supabase + Cloudflare R2) and ultra-fast free-tier LLM inference (Groq Cloud LPU + Google AI Studio).

---

## Free-Tier Infrastructure Architecture

| Layer | Component | Permanent Free Allocation | Purpose |
|---|---|---|---|
| **Primary LLM** | Groq Cloud (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`) | 14,400 requests/day | High-speed planning and tool execution |
| **Long Context LLM** | Google AI Studio (`gemini-2.0-flash-exp`) | 1,500 requests/day, 1M token window | Large-repo code reviews, context synthesis |
| **On-Premise LLM** | Ollama on Oracle Cloud ARM VM (`qwen2.5:7b`, `llama3.2:3b`) | 100% unlimited on-instance | Zero-quota emergency fallback |
| **Primary Compute** | GitHub Actions (`ubuntu-latest`) | Unlimited minutes (public repo) | Ephemeral graph runner execution |
| **Persistent Compute** | Oracle Cloud Always Free (4 vCPU, 24GB RAM ARM) | Permanent \$0.00 | IMAP IDLE real-time email push daemon |
| **Edge Gateway** | Cloudflare Workers | 100,000 requests/day | Webhook ingestion & OAuth proxy |
| **State & Memory** | GitHub Repos (`aria-brain`) + Supabase PostgreSQL | 500MB DB + Unlimited Git | Checkpoint resumption & semantic memory |
| **Object Store** | Cloudflare R2 | 10GB, **\$0 egress fees** | Large attachments & artifact backups |
| **Cache & Locks** | Upstash Redis | 10,000 commands/day | Quota enforcement & rate limits |
| **Security Gate** | Ntfy.sh | Unlimited instant mobile push | Out-of-band human approvals |

---

## System Architecture

```
                    ┌─────────────────────────┐
                    │ External Push Triggers  │
                    │ (Gmail, GitHub, Stripe) │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ Cloudflare Edge Gateway │
                    │   (worker.js - 100k/d)  │
                    └───────────┬─────────────┘
                                │ repository_dispatch
                                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                 GITHUB ACTIONS RUNNER                       │
  │                                                             │
  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
  │   │ Task Intake  │───▶│   Planner    │───▶│   Executor   │  │
  │   │  & Sanitizer │    │ (Groq 70B)   │    │  (Groq 8B)   │  │
  │   └──────────────┘    └──────────────┘    └───────┬──────┘  │
  │                                                   │         │
  │   ┌──────────────┐    ┌──────────────┐            ▼         │
  │   │ Checkpoint   │◀───│  Reflection  │◀─── [ Tool Suite ]   │
  │   │  (Supabase)  │    │  & Quota Chk │    (Email/Git/Code)  │
  │   └──────┬───────┘    └──────────────┘                      │
  └──────────┼──────────────────────────────────────────────────┘
             │ State Commits
             ▼
  ┌─────────────────────────────────────────────────────────────┐
  │         PERSISTENT GIT REPOSITORY (aria-brain)              │
  │  - JSONL Audit Logs    - Long-Term Vector Memory            │
  │  - Checkpoints         - Task Backlog & Quota Snapshots     │
  └─────────────────────────────────────────────────────────────┘
```

---

## Directory Layout

```
aria-agent/
├── .github/
│   └── workflows/
│       ├── aria-main.yml           # Ephemeral runner orchestrator (cron + dispatch)
│       └── aria-maintenance.yml    # Self-healing, dep updates & memory pruning
├── cloudflare/
│   ├── worker.js                   # Free-tier webhook & approval edge proxy
│   └── wrangler.toml               # Cloudflare configuration
├── config/
│   ├── agent_config.yaml           # Agent runtime parameters & guardrails
│   └── model_registry.yaml         # Multi-model routing priorities
├── daemon/
│   ├── daemon.py                   # OCI Always Free IMAP IDLE persistent daemon
│   └── aria-daemon.service         # Systemd service unit
├── src/aria/
│   ├── graph.py                    # LangGraph StateGraph topology
│   ├── nodes.py                    # Planner, Executor, Observer, Reflector nodes
│   ├── state.py                    # Pydantic schemas and AgentState
│   ├── llm/
│   │   ├── quota.py                # Zero-cost rate limiter & counter
│   │   └── router.py               # Dynamic model switcher (Groq/Gemini/Ollama)
│   ├── security/
│   │   ├── guards.py               # Prompt injection sanitizer & credential masker
│   │   └── approval.py             # Ntfy.sh human approval gate
│   ├── storage/
│   │   ├── checkpointer.py         # Supabase & JSON checkpoint manager
│   │   └── git_store.py            # Git-as-transaction-log persistence
│   └── tools/
│       ├── email_tools.py          # IMAP/SMTP email interactions
│       ├── github_tools.py         # Issues, PRs, and workflow dispatch
│       ├── memory_tools.py         # Semantic memory & vector retrieval
│       └── code_tools.py           # Sandboxed code execution & linting
├── tests/                          # Complete automated test suite
├── .env.example                    # Free-tier credentials template
├── pyproject.toml                  # Python package configuration
└── SETUP_GUIDE.md                  # Comprehensive setup walkthrough
```

---

## Quick Start

### 1. Local Verification (Mock / Dry-Run)
```bash
# Clone and enter directory
cd aria-agent

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Run test suite
pytest -v

# Run agent in dry-run mode
python -m aria.main --task "Review unread emails" --type email --dry-run
```

### 2. Full Free-Tier Deployment
Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) to register your free accounts and configure GitHub Secrets.
