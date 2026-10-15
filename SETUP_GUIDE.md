# ARIA Zero-Cost Setup & Onboarding Guide

This guide walks you through provisioning all 100% permanent free-tier services required to run ARIA autonomously at \$0.00 TCO.

---

## Step 1: LLM Inference Accounts (Zero Cost)

### 1.1 Groq Cloud API Key
1. Go to [https://console.groq.com](https://console.groq.com) and create a free account (no credit card required).
2. Navigate to **API Keys** and generate a new key.
3. Save as `GROQ_API_KEY`.
4. **Limits:** 14,400 requests/day, 500k tokens/min on `llama-3.3-70b-versatile`.

### 1.2 Google AI Studio API Key
1. Go to [https://aistudio.google.com](https://aistudio.google.com).
2. Sign in with any Google account and click **Get API Key**.
3. Create a project key for Gemini 2.0 Flash (`gemini-2.0-flash-exp`).
4. Save as `GEMINI_API_KEY`.
5. **Limits:** 1,500 requests/day, 1M token context window.

---

## Step 2: Storage & State Persistence (Zero Cost)

### 2.1 Supabase PostgreSQL Database
1. Go to [https://supabase.com](https://supabase.com) and create a free account.
2. Create a new project (e.g. `aria-db`). Free tier includes:
   - 500MB Database storage
   - 1GB File storage
   - `pgvector` extension supported
3. Go to **Project Settings** -> **Database** and copy the **URI Connection String**.
4. Save as `SUPABASE_DB_URL`.

### 2.2 Cloudflare R2 & Workers
1. Go to [https://dash.cloudflare.com](https://dash.cloudflare.com).
2. Create a free account.
3. In **R2**, create a bucket named `aria-storage`. Free tier includes:
   - 10GB storage
   - **Zero egress fees**
4. Generate an R2 API Token (Read & Write permissions).
5. In **Workers & Pages**, deploy `cloudflare/worker.js` using Wrangler:
   ```bash
   cd cloudflare
   npx wrangler deploy
   ```

### 2.3 Upstash Redis (Optional Quota Counter)
1. Go to [https://upstash.com](https://upstash.com).
2. Create a free Serverless Redis database.
3. Free tier includes 10,000 commands/day.
4. Copy the REST URL and REST Token to `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`.

---

## Step 3: Git Repositories & Runner Configuration

### 3.1 Create Repositories
1. Create `aria-agent` (public repository — grants **unlimited** GitHub Actions runner minutes).
2. Create `aria-brain` (private repository for sensitive state, memory, and personal task queues).

### 3.2 Fine-Grained GitHub PAT
1. Go to **GitHub Settings** -> **Developer Settings** -> **Personal Access Tokens** -> **Fine-grained tokens**.
2. Name: `ARIA_AGENT_TOKEN`.
3. Resource Owner: Your account.
4. Repository Access: Only `aria-agent` and `aria-brain`.
5. Permissions:
   - Contents: Read and write
   - Issues: Read and write
   - Pull Requests: Read and write
   - Workflows: Read-only
   - **Secrets: NONE (Zero-trust isolation)**
6. Save as `GH_AGENT_PAT`.

### 3.3 Configure GitHub Secrets
In your `aria-agent` repository, navigate to **Settings** -> **Secrets and variables** -> **Actions** and add:

- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- `SUPABASE_DB_URL`
- `GH_AGENT_PAT`
- `EMAIL_ACCOUNT` (your Gmail address)
- `EMAIL_APP_PASSWORD` (generated at Google Account -> Security -> 2-Step Verification -> App passwords)
- `NTFY_TOPIC` (a private random slug, e.g. `aria-alerts-9x8q2k`)
- `UPSTASH_REDIS_REST_URL` (optional)
- `UPSTASH_REDIS_REST_TOKEN` (optional)

---

## Step 4: Persistent Real-Time Daemon (Oracle Cloud Always Free)

1. Sign up at [https://www.oracle.com/cloud/free/](https://www.oracle.com/cloud/free/).
2. Create an **Ampere A1 Compute Instance**:
   - Shape: `VM.Standard.A1.Flex`
   - OCPU: 4 cores
   - Memory: 24 GB RAM
   - OS: Ubuntu 24.04 ARM64
   - **Cost: $0.00 permanently**
3. SSH into the instance:
   ```bash
   sudo apt update && sudo apt install -y python3-pip git
   sudo git clone https://github.com/yourusername/aria-agent /opt/aria
   sudo cp /opt/aria/daemon/aria-daemon.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now aria-daemon
   ```
4. Install Ollama on the instance for local fallback inference:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2:3b
   ollama pull qwen2.5:7b
   ```

---

## Step 5: Verification & Launch

Trigger your first test run directly from GitHub Actions:
1. Go to **Actions** -> **ARIA Orchestrator Engine**.
2. Click **Run workflow**.
3. Select type `email`, task: `Inspect unread emails and record summary in memory`.
4. Inspect the workflow execution logs — state will be committed to `state/` automatically!
