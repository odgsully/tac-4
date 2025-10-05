# ADW Complete Setup Guide
**End-to-End Repository Setup for AI Developer Workflows**

This guide provides step-by-step instructions to set up the ADW (AI Developer Workflow) system in any new repository, enabling autonomous issue processing via AI agents.

---

## Table of Contents
1. [Requirements](#requirements)
2. [Critical Setup Pitfalls](#critical-setup-pitfalls) ⚠️ **READ THIS FIRST**
3. [Account Setup](#account-setup)
4. [Local Machine Setup](#local-machine-setup)
5. [Repository Setup](#repository-setup)
6. [ADW System Installation](#adw-system-installation)
7. [Webhook Server Setup](#webhook-server-setup)
8. [GitHub Integration](#github-integration)
9. [Testing & Validation](#testing--validation)
10. [Production Deployment](#production-deployment)
11. [Troubleshooting](#troubleshooting)

---

## Requirements

### Hardware Requirements
- **Development Machine** (Laptop/Desktop)
  - Any modern OS (macOS, Linux, Windows)
  - 4GB+ RAM
  - Internet connection

- **Server/Agent Machine** (Optional but recommended for production)
  - Always-on computer (Mac Mini, Mac Studio, Linux server, cloud VM)
  - 8GB+ RAM recommended
  - Stable internet connection
  - SSH access from development machine

### Software Requirements
- **Node.js** 18+ (for Claude Code CLI)
- **Python** 3.10+ (for ADW system)
- **Git** 2.30+
- **GitHub CLI** (`gh`) 2.0+
- **uv** (Python package manager)
- **Claude Code CLI** (Anthropic)
- **Cloudflare Tunnel** (for webhook exposure, optional)

### Account Requirements
- **GitHub Account #1** (Human/Owner)
  - Example: `odgsully`
  - Purpose: Create issues, review PRs, own repositories
  - Required permissions: Repository admin

- **GitHub Account #2** (Bot/Agent)
  - Example: `odgsully-agents`
  - Purpose: Post comments, create PRs, commit code
  - Required permissions: Repository write access

- **Anthropic Account**
  - Active API key with Claude Sonnet access
  - Billing enabled
  - Sufficient credits/quota

- **Cloudflare Account** (Optional, for webhooks)
  - Free tier sufficient
  - Tunnel configured

---

## Critical Setup Pitfalls

⚠️ **READ THIS BEFORE STARTING** - These are the TOP 4 issues that cause ADW setup failures. Understanding these will save you hours of debugging.

### Pitfall #1: Cloudflare Tunnel Missing Ingress Rules

**Problem:** Tunnel runs but doesn't route traffic to webhook server

**Symptoms:**
```
WRN No ingress rules were defined in provided config
cloudflared will return 503 for all incoming HTTP requests
```

**Why it happens:** Cloudflare tunnel doesn't know where to send GitHub webhooks

**Solution:** Always create `~/.cloudflared/config.yml` with ingress rules (covered in Step 15)
```yaml
tunnel: <your-tunnel-id>
credentials-file: /Users/ADW/.cloudflared/<tunnel-id>.json
ingress:
  - service: http://localhost:8001
```

**How to verify:** `curl https://your-tunnel-url/health` should return `{"status":"healthy"}`

---

### Pitfall #2: Git Remote Points to Wrong Repository

**Problem:** If you forked/copied ADW from another user's repo, git remote still points to THEIR repository

**Symptoms:**
```
GraphQL: Could not resolve to a Repository with the name 'original-user/tac-4'
Error fetching issue: 404 Not Found
```

**Why it happens:** Git remote URL preserved from original repository

**How to detect:**
```bash
git remote -v
# ❌ BAD: origin  https://github.com/someone-else/my-repo.git
# ✅ GOOD: origin  https://github.com/YOUR-USERNAME/my-repo.git
```

**Solution:** Update git remote to YOUR repository (covered in Step 14)
```bash
git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
```

**Critical:** Do this IMMEDIATELY after cloning if you forked/copied from another user

---

### Pitfall #3: CLAUDE_CODE_PATH Not Set or Wrong

**Problem:** Webhook listener starts without CLAUDE_CODE_PATH environment variable

**Symptoms:**
```
Error: Missing required environment variables: CLAUDE_CODE_PATH
ADW agents fail to execute
```

**Why it happens:**
1. `.env` file doesn't exist or is empty
2. Webhook listener started BEFORE `.env` was configured
3. Wrong path to Claude Code binary

**Solution:**
1. Run `which claude` to get the correct path
2. Add to `.env`: `CLAUDE_CODE_PATH=/path/from/which/command`
3. **RESTART webhook listener** after editing `.env` (changes don't apply to running processes)

**How to verify:**
```bash
source .env
echo $CLAUDE_CODE_PATH
# Should show: /Users/YourUser/.nvm/versions/node/vX.X.X/bin/claude
```

---

### Pitfall #4: GITHUB_PAT Overrides gh CLI Authentication ⚠️ **MOST COMMON**

**Problem:** GITHUB_PAT in `.env` has insufficient permissions or overrides working `gh` CLI auth

**Symptoms:**
```
Error posting comment: GraphQL: Resource not accessible by personal access token (addComment)
Error creating PR: Not Found (HTTP 404)
```

**Why it happens:**
- When `GITHUB_PAT` is set in `.env`, ADW uses it INSTEAD of `gh` CLI authentication
- The PAT might not have the required `repo` scope or comment permissions
- This overrides your perfectly working `gh auth login` setup

**Authentication Flow:**
```
IF GITHUB_PAT exists in .env:
    ✗ Use GITHUB_PAT (might lack permissions)
    ✗ Ignore gh CLI authentication
ELSE:
    ✓ Use gh CLI authentication (usually has full permissions)
```

**Solution: KEEP GITHUB_PAT COMMENTED OUT unless you need a different GitHub account**
```bash
# .env file - DEFAULT CONFIGURATION
# (OPTIONAL) GitHub PAT - LEAVE COMMENTED OUT to use gh CLI auth
# GITHUB_PAT=ghp_xxxxx...
```

**When to use GITHUB_PAT:**
- Only when you need ADW to use a DIFFERENT GitHub account than what `gh auth login` is configured for
- If you must use it, ensure it has these scopes:
  - `repo` (full control)
  - `workflow` (update GitHub Actions)
  - `read:org` (read organization data)

**How to verify authentication:**
```bash
# Check which account gh CLI uses
gh auth status
# Should show: Logged in to github.com as YOUR-BOT-ACCOUNT

# Check if GITHUB_PAT is interfering
grep "^GITHUB_PAT" .env
# Should show: (no output) or commented line starting with #
```

---

### Setup Success Checklist

Before proceeding with setup, ensure you understand:
- [ ] Cloudflare tunnel needs `config.yml` with ingress rules
- [ ] Git remote must point to YOUR repository (not forked source)
- [ ] `.env` must be configured BEFORE starting webhook listener
- [ ] GITHUB_PAT should be COMMENTED OUT (use `gh` CLI auth instead)
- [ ] Any service restart is needed after changing `.env` file

**If you hit issues during setup, refer back to these 4 pitfalls first!**

---

## Account Setup

### Step 1: Create GitHub Bot Account

**Device:** Your laptop
**Account:** Your personal browser session

1. **Log out of GitHub** or use **incognito/private browsing**
2. Go to: https://github.com/signup
3. **Create account:**
   - Username: `{yourusername}-agents` (e.g., `odgsully-agents`)
   - Email: Use a dedicated email or GitHub's email aliases
   - Password: Use a strong, unique password (save to password manager)
4. **Verify email** and complete GitHub onboarding
5. **Configure profile:**
   - Set profile picture (robot/AI icon recommended)
   - Bio: "Autonomous development agent powered by Claude Code"
   - Location: (optional)
6. **Enable 2FA** (recommended for security)

### Step 2: Get Anthropic API Key

**Device:** Your laptop
**Account:** Your Anthropic account

1. Go to: https://console.anthropic.com/
2. Log in or create account
3. Navigate to: **Settings** → **API Keys**
4. Click **"Create Key"**
5. **Name:** `adw-production` (or similar)
6. **Copy the API key** (starts with `sk-ant-api03-...`)
7. **Store securely** in password manager
8. **Set billing limits** (recommended):
   - Go to **Settings** → **Billing**
   - Set monthly spending limit (e.g., $100)
   - Enable billing alerts

### Step 3: Install GitHub CLI on All Machines

**Device:** Both laptop AND server/agent machine
**Account:** System user

#### On macOS (both machines):
```bash
brew install gh
```

#### On Ubuntu/Debian (server):
```bash
sudo apt update
sudo apt install gh
```

#### On Windows (laptop):
```bash
winget install --id GitHub.cli
```

**Verify installation:**
```bash
gh --version
# Should show: gh version 2.x.x
```

### Step 4: Authenticate GitHub CLI

#### On Laptop (as human user):
**Device:** Laptop
**Account:** Your main GitHub account (e.g., `odgsully`)

```bash
gh auth login
```

**Select options:**
- Account: `GitHub.com`
- Protocol: `HTTPS`
- Authenticate: `Login with a web browser`
- Follow browser prompts
- **Authorize** GitHub CLI

**Verify:**
```bash
gh auth status
# Should show: Logged in to github.com as odgsully
```

#### On Server/Agent Machine (as bot user):
**Device:** Server (Mac Studio, Linux server, etc.)
**Account:** Bot GitHub account (e.g., `odgsully-agents`)

```bash
# SSH into server from laptop
ssh user@server-hostname

# Authenticate as bot account
gh auth login
```

**Select options:**
- Account: `GitHub.com`
- Protocol: `HTTPS`
- Authenticate: `Login with a web browser`
- **IMPORTANT:** The browser will open on the SERVER
  - If headless server, use `Paste an authentication token` instead
  - Generate token at: https://github.com/settings/tokens
  - Scopes needed: `repo`, `workflow`, `read:org`

**Verify:**
```bash
gh auth status
# Should show: Logged in to github.com as odgsully-agents
```

---

## Local Machine Setup

### Step 5: Install Claude Code CLI

**Device:** Both laptop AND server
**Account:** System user

#### On macOS:
```bash
# Download from Anthropic
# Visit: https://docs.anthropic.com/en/docs/claude-code

# Or use npm (if available)
npm install -g @anthropic/claude-code

# Verify installation
claude --version
```

#### On Linux:
```bash
# Download from Anthropic
curl -fsSL https://docs.anthropic.com/install.sh | sh

# Verify installation
claude --version
```

**Find Claude Code path (needed later):**
```bash
which claude
# Example output: /Users/ADW/.nvm/versions/node/v22.20.0/bin/claude
# Save this path for .env configuration
```

### Step 6: Install Python uv

**Device:** Both laptop AND server
**Account:** System user

#### On macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to shell profile
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc

# Reload shell
source ~/.zshrc  # or source ~/.bashrc
```

#### On Windows:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify:**
```bash
uv --version
# Should show: uv 0.x.x
```

### Step 7: Install Cloudflare Tunnel (Optional)

**Device:** Server only (for webhook exposure)
**Account:** System user

#### On macOS:
```bash
brew install cloudflare/cloudflare/cloudflared
```

#### On Linux:
```bash
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

**Verify:**
```bash
cloudflared --version
```

---

## Repository Setup

### Step 8: Create New Repository

**Device:** Laptop
**Account:** Main GitHub account (e.g., `odgsully`)

1. Go to: https://github.com/new
2. **Configure repository:**
   - Owner: Your account (e.g., `odgsully`)
   - Repository name: `my-new-project`
   - Description: (optional)
   - Visibility: Public or Private
   - ✅ Initialize with README
   - ✅ Add .gitignore: Python
   - License: (optional, e.g., MIT)
3. Click **"Create repository"**

### Step 9: Add Bot Collaborator

**Device:** Laptop
**Account:** Main GitHub account (e.g., `odgsully`)

1. Go to repository: `https://github.com/odgsully/my-new-project`
2. Click **Settings** → **Collaborators**
3. Click **"Add people"**
4. Search for: `odgsully-agents` (your bot account)
5. Select role: **Write** (minimum required)
6. Click **"Add [username] to this repository"**

**Accept invitation (as bot):**

**Device:** Laptop (incognito/private browser)
**Account:** Bot GitHub account (`odgsully-agents`)

1. Log in as bot account
2. Go to: https://github.com/notifications
3. Accept the collaboration invitation

### Step 10: Clone Repository

#### On Laptop:
**Device:** Laptop
**Account:** Main GitHub account

```bash
cd ~/projects  # or your preferred directory
gh repo clone odgsully/my-new-project
cd my-new-project
```

#### On Server:
**Device:** Server (via SSH)
**Account:** Bot GitHub account

```bash
cd ~  # or your preferred directory
gh repo clone odgsully/my-new-project
cd my-new-project
```

---

## ADW System Installation

### Step 11: Copy ADW Files to New Repository

**Device:** Laptop
**Account:** Main GitHub account

**Option A: Manual Copy (from existing ADW repo like tac-4)**
```bash
# Assuming you have tac-4 cloned already
cd ~/projects/my-new-project

# Copy ADW system files
cp -r ~/projects/tac-4/adws ./
cp -r ~/projects/tac-4/.claude ./
cp -r ~/projects/tac-4/specs ./
cp ~/projects/tac-4/.env.sample ./
cp ~/projects/tac-4/ADW_SETUP_GUIDE.md ./  # This guide

# Create required directories
mkdir -p agents logs
```

**Option B: Use Git Subtree (from existing ADW repo)**
```bash
# Add tac-4 as remote
git remote add tac4-adw https://github.com/odgsully/tac-4.git
git fetch tac4-adw

# Cherry-pick ADW files (alternative approach)
git checkout tac4-adw/main -- adws .claude specs .env.sample
```

**Option C: Start Fresh (create ADW files manually)**
- Follow the detailed file structure in the ADW documentation
- Reference: `tac-4/adws/README.md`

### Step 12: Configure Environment Variables

**Device:** Both laptop AND server
**Account:** Respective users

**⚠️ CRITICAL:** This step directly relates to [Pitfall #3](#pitfall-3-claude_code_path-not-set-or-wrong) and [Pitfall #4](#pitfall-4-github_pat-overrides-gh-cli-authentication--most-common). Read those sections first!

#### On Server (Agent Machine):
```bash
cd ~/my-new-project

# Copy sample env
cp .env.sample .env

# Edit .env file
nano .env  # or vim, code, etc.
```

**Add required values:**
```bash
# File: ~/my-new-project/.env
# Location: Project root directory

# ============================================================
# REQUIRED: Anthropic API key
# Get from: https://console.anthropic.com/ → Settings → API Keys
# ============================================================
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE

# ============================================================
# REQUIRED: Claude Code CLI path
# Get by running: which claude
# Example output: /Users/ADW/.nvm/versions/node/v22.20.0/bin/claude
# ⚠️ See Pitfall #3 - Must be exact path from 'which claude'
# ============================================================
CLAUDE_CODE_PATH=/Users/ADW/.nvm/versions/node/v22.20.0/bin/claude

# ============================================================
# GITHUB_PAT - ⚠️ KEEP COMMENTED OUT (See Pitfall #4)
# Only uncomment if you need ADW to use a DIFFERENT GitHub
# account than what 'gh auth login' is configured for.
# When set, this OVERRIDES gh CLI authentication!
# Required scopes if used: repo, workflow, read:org
# ============================================================
# GITHUB_PAT=ghp_xxxxx

# ============================================================
# OPTIONAL: E2B for sandboxed code execution
# Get from: https://e2b.dev/
# ============================================================
# E2B_API_KEY=e2b_xxxxx

# ============================================================
# OPTIONAL: Cloudflare tunnel token (for webhook mode)
# Get from: Cloudflare Dashboard → Zero Trust → Tunnels
# See Step 15 for setup instructions
# ============================================================
# CLOUDFLARED_TUNNEL_TOKEN=xxxxx

# ============================================================
# OPTIONAL: Claude Code OAuth token
# Get from: Claude Code CLI authentication flow
# ============================================================
# CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-xxxxx
```

**Save and verify:**
```bash
# Test environment loading
source .env
echo $ANTHROPIC_API_KEY
# ✅ Expected: sk-ant-api03-jT-C_NOhbx7tUZh... (your actual key)
# ❌ Bad: (empty output) - means variable not set

echo $CLAUDE_CODE_PATH
# ✅ Expected: /Users/ADW/.nvm/versions/node/v22.20.0/bin/claude
# ❌ Bad: (empty output) - See Pitfall #3

# Verify GITHUB_PAT is NOT set (should be commented out)
grep "^GITHUB_PAT" .env
# ✅ Expected: (no output) - means line is commented
# ❌ Bad: GITHUB_PAT=ghp_xxx - See Pitfall #4, comment this out!
```

**Important:** Add `.env` to `.gitignore`:
```bash
# Ensure .env is never committed (contains secrets!)
echo ".env" >> .gitignore

# Verify
git status
# .env should NOT appear in "Changes to be committed" or "Untracked files"
```

**Cross-reference:** See also:
- [Pitfall #3: CLAUDE_CODE_PATH Not Set](#pitfall-3-claude_code_path-not-set-or-wrong)
- [Pitfall #4: GITHUB_PAT Overrides gh CLI Auth](#pitfall-4-github_pat-overrides-gh-cli-authentication--most-common)

#### On Laptop (Optional - for testing):
**Device:** Laptop

```bash
cd ~/projects/my-new-project

# Copy and configure .env
cp .env.sample .env
nano .env

# Add your Anthropic API key
# Add your Claude Code path
```

### Step 13: Install Python Dependencies

**Device:** Both laptop AND server
**Account:** Respective users

```bash
cd ~/my-new-project

# Sync all dependencies
uv sync --all-extras

# Verify installation
uv run adws/health_check.py
```

**Expected output:**
```
✅ Environment variables configured
✅ Git repository valid
✅ Claude Code CLI functional
✅ GitHub CLI authenticated
```

**If errors occur, troubleshoot:**
- Missing ANTHROPIC_API_KEY → Check `.env` file
- Claude Code not found → Verify `CLAUDE_CODE_PATH`
- GitHub CLI not authenticated → Run `gh auth login`

### Step 14: Configure Git Remote

**Device:** Server
**Account:** Bot account

**⚠️ CRITICAL:** This step directly relates to [Pitfall #2](#pitfall-2-git-remote-points-to-wrong-repository). If you forked/copied ADW from another user, this WILL cause errors!

**Verify current remote URL:**
```bash
cd ~/my-new-project
git remote -v
```

**Expected output:**
```
origin  https://github.com/YOUR-USERNAME/my-new-project.git (fetch)
origin  https://github.com/YOUR-USERNAME/my-new-project.git (push)
```

**If remote points to WRONG repository** (e.g., forked source):
```
❌ BAD:
origin  https://github.com/disler/tac-4.git (fetch)
origin  https://github.com/disler/tac-4.git (push)
```

**Fix it immediately:**
```bash
# Replace with YOUR repository
git remote set-url origin https://github.com/YOUR-USERNAME/my-new-project.git

# Verify the change
git remote -v
# ✅ Should now show YOUR-USERNAME, not the original source
```

**Why this matters:**
- ADW will try to push commits/PRs to the repository in the git remote URL
- If it points to someone else's repo, you'll get 404/403 errors
- Error message: `GraphQL: Could not resolve to a Repository with the name 'wrong-user/repo'`

**Verification checklist:**
- [ ] Remote URL contains YOUR GitHub username
- [ ] Remote URL contains YOUR repository name
- [ ] NOT the username/repo you forked from

**Cross-reference:** See [Pitfall #2: Git Remote Points to Wrong Repository](#pitfall-2-git-remote-points-to-wrong-repository)

---

## Webhook Server Setup

### Step 15: Set Up Cloudflare Tunnel

**Device:** Server
**Account:** System user

**⚠️ CRITICAL:** This step directly relates to [Pitfall #1](#pitfall-1-cloudflare-tunnel-missing-ingress-rules). Missing ingress rules = 503 errors on all webhook requests!

#### Create Cloudflare Tunnel:

1. **Log in to Cloudflare Dashboard:**
   - URL: https://one.dash.cloudflare.com/
   - Navigate to: **Zero Trust** → **Networks** → **Tunnels**

2. **Create Tunnel:**
   - Click **"Create a tunnel"**
   - Name: `adw-webhook-{project}`
     - Example: `adw-webhook-my-new-project`
   - Click **"Save tunnel"**

3. **Install Connector (on server):**
   ```bash
   # Cloudflare will show a command like this:
   cloudflared service install eyJhIjoiNThmMGI1ZTE0Yzl...

   # Or save token to .env for manual runs:
   nano ~/my-new-project/.env
   # Add: CLOUDFLARED_TUNNEL_TOKEN="eyJhIjoiNThmMGI1ZTE0Yzl..."
   ```

4. **Configure Public Hostname:**
   - Click **"Add a public hostname"**
   - **Subdomain:** `adw-my-new-project`
   - **Domain:** Select your domain from dropdown
   - **Path:** (leave empty)
   - **Service Type:** `HTTP`
   - **URL:** `localhost:8001` ⚠️ Must match webhook server port!
   - Click **"Save tunnel"**

5. **Save Tunnel Details** (you'll need these):
   - **Tunnel ID:** Copy from URL or dashboard (e.g., `5740df70-fda1-433d-b8dd-71188f8ac566`)
   - **Public URL:** (e.g., `https://adw-my-new-project.yourdomain.com`)
   - **Token:** Already in .env from step 3

#### Create Cloudflare Config File (REQUIRED for named tunnels)

**⚠️ This is Pitfall #1 - Without this file, tunnel returns 503!**

**Device:** Server

```bash
# Create config directory
mkdir -p ~/.cloudflared

# Get your tunnel ID (from Cloudflare dashboard or tunnel command output)
TUNNEL_ID="5740df70-fda1-433d-b8dd-71188f8ac566"  # Replace with YOUR tunnel ID

# Create config file
cat > ~/.cloudflared/config.yml << EOF
# File: ~/.cloudflared/config.yml
# Purpose: Routes Cloudflare tunnel traffic to webhook server
# ⚠️ See Pitfall #1 - This file is REQUIRED!

tunnel: $TUNNEL_ID
credentials-file: /Users/ADW/.cloudflared/${TUNNEL_ID}.json

ingress:
  - service: http://localhost:8001
EOF

# Verify file was created
cat ~/.cloudflared/config.yml
```

**Expected config.yml content:**
```yaml
tunnel: 5740df70-fda1-433d-b8dd-71188f8ac566
credentials-file: /Users/ADW/.cloudflared/5740df70-fda1-433d-b8dd-71188f8ac566.json

ingress:
  - service: http://localhost:8001
```

**Download credentials file:**
- Go to Cloudflare dashboard: **Tunnels** → Your tunnel → **Configure**
- Look for: **"Download credentials file"** or **".json file"**
- Save to: `~/.cloudflared/<TUNNEL-ID>.json`
  - Example path: `~/.cloudflared/5740df70-fda1-433d-b8dd-71188f8ac566.json`

**Verify credentials file exists:**
```bash
ls -la ~/.cloudflared/*.json
# ✅ Expected: Shows your <TUNNEL-ID>.json file
# ❌ Bad: No such file or directory - download from Cloudflare dashboard
```

**Why this matters (Pitfall #1 explained):**
Without `config.yml` with ingress rules, cloudflared shows this WARNING:
```
WRN No ingress rules were defined in provided config
cloudflared will return 503 for all incoming HTTP requests
```

This means:
- Tunnel runs without errors
- GitHub webhooks reach Cloudflare
- But Cloudflare doesn't know where to route them (no ingress rules!)
- Result: All requests get HTTP 503 Service Unavailable

**Cross-reference:** See [Pitfall #1: Cloudflare Tunnel Missing Ingress Rules](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)

### Step 16: Test Webhook Server Locally

**Device:** Server
**Account:** Bot account

**⚠️ IMPORTANT:** Webhook listener must be restarted if you edited .env file! See [Pitfall #3](#pitfall-3-claude_code_path-not-set-or-wrong) for details.

**Start webhook listener:**
```bash
cd ~/my-new-project

# Ensure .env is loaded in this shell session
source .env

# Start webhook server
uv run adws/trigger_webhook.py
```

**✅ Expected output (successful start):**
```
Starting ADW Webhook Trigger on port 8001
Starting server on http://0.0.0.0:8001
Webhook endpoint: POST /gh-webhook
Health check: GET /health
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**❌ If you see errors:**
```
Error: Missing required environment variables: CLAUDE_CODE_PATH
```
→ See [Pitfall #3](#pitfall-3-claude_code_path-not-set-or-wrong) - Check .env file

```
Error: Could not find Claude Code at: /wrong/path/claude
```
→ Run `which claude` and update CLAUDE_CODE_PATH in .env, then restart server

**In another terminal (or new SSH session), test health endpoint:**
```bash
# Open new terminal/SSH session
curl http://localhost:8001/health
```

**✅ Expected response (healthy):**
```json
{
  "status": "healthy",
  "service": "adw-webhook-trigger",
  "health_check": {
    "success": true,
    "warnings": [],
    "errors": []
  }
}
```

**❌ If you get connection refused:**
```
curl: (7) Failed to connect to localhost port 8001: Connection refused
```
→ Webhook server not running. Check terminal for startup errors.

**Test with JSON response formatting:**
```bash
curl http://localhost:8001/health | jq .
# Requires 'jq' installed: brew install jq (macOS) or apt install jq (Linux)
```

**Verification checklist:**
- [ ] Server started without errors
- [ ] Health endpoint returns `"status": "healthy"`
- [ ] No "Missing environment variables" errors
- [ ] Port 8001 is listening (check with `lsof -i :8001`)

**Check which process is using port 8001:**
```bash
lsof -i :8001
# Should show: python (or uv) process owned by your user
```

**Stop the server:** `Ctrl+C` in the terminal running trigger_webhook.py

**Cross-reference:**
- [Pitfall #3: CLAUDE_CODE_PATH Not Set](#pitfall-3-claude_code_path-not-set-or-wrong)
- [Troubleshooting: Webhook Not Receiving Events](#webhook-not-receiving-events)

### Step 17: Start Cloudflare Tunnel

**Device:** Server
**Account:** System user

**Prerequisites:**
- ✅ Webhook server is running (Step 16)
- ✅ `~/.cloudflared/config.yml` exists with ingress rules (Step 15)
- ✅ Credentials file exists at `~/.cloudflared/<TUNNEL-ID>.json`

**Option A: Quick Tunnel (Temporary URL, testing only):**
```bash
cloudflared tunnel --url http://localhost:8001
```

**✅ Expected output:**
```
2025-10-04T12:00:00Z INF Thank you for trying Cloudflare Tunnel. Doing so, without a Cloudflare account, is a quick way to experiment and try it out. However, be aware that these account-less Tunnels have no uptime guarantee.
2025-10-04T12:00:00Z INF Requesting new quick Tunnel on trycloudflare.com...
2025-10-04T12:00:01Z INF +--------------------------------------------------------------------------------------------+
2025-10-04T12:00:01Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2025-10-04T12:00:01Z INF |  https://random-words-here.trycloudflare.com                                                |
2025-10-04T12:00:01Z INF +--------------------------------------------------------------------------------------------+
```

**Note:** Quick tunnels are temporary and URL changes on restart. Use for testing only!

**Option B: Named Tunnel (Production, persistent URL) - RECOMMENDED:**
```bash
# Ensure webhook server is running first!
# Run in separate terminal or background

cloudflared tunnel run adw-webhook-my-new-project
```

**✅ Expected output (with config.yml):**
```
2025-10-04T12:00:00Z INF Starting tunnel tunnelID=5740df70-fda1-433d-b8dd-71188f8ac566
2025-10-04T12:00:00Z INF Version 2024.9.1
2025-10-04T12:00:00Z INF GOOS: darwin, GOVersion: go1.22.0, GoArch: arm64
2025-10-04T12:00:01Z INF Registered tunnel connection connIndex=0 connection=xxxxx
2025-10-04T12:00:01Z INF Registered tunnel connection connIndex=1 connection=xxxxx
2025-10-04T12:00:01Z INF Registered tunnel connection connIndex=2 connection=xxxxx
2025-10-04T12:00:01Z INF Registered tunnel connection connIndex=3 connection=xxxxx
2025-10-04T12:00:01Z INF Updated to new configuration config="{\"ingress\":[{\"service\":\"http://localhost:8001\"}],\"warp-routing\":{}}"
```

**❌ If you see this WARNING:**
```
WRN No ingress rules were defined in provided config
cloudflared will return 503 for all incoming HTTP requests
```
→ **CRITICAL ERROR:** See [Pitfall #1](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)
→ You're missing `~/.cloudflared/config.yml` or it has no ingress rules
→ Go back to Step 15 and create config.yml

**Keep tunnel running in background:**

**Option 1: screen (simple)**
```bash
# Start screen session
screen -S cloudflared

# Run tunnel
cloudflared tunnel run adw-webhook-my-new-project

# Detach: Ctrl+A, then D
# Reattach: screen -r cloudflared
```

**Option 2: systemd/LaunchAgent (production)**
See [Step 23 (Linux)](#step-23-set-up-systemd-service-linux-server) or [Step 24 (macOS)](#step-24-set-up-launchagent-macos-server)

**Test public URL:**
```bash
# From your laptop or any machine
curl https://adw-my-new-project.yourdomain.com/health
```

**✅ Expected response:**
```json
{
  "status": "healthy",
  "service": "adw-webhook-trigger",
  "health_check": {
    "success": true,
    "warnings": [],
    "errors": []
  }
}
```

**❌ If you get errors:**

```
curl: (6) Could not resolve host: adw-my-new-project.yourdomain.com
```
→ DNS not propagated yet. Wait 1-5 minutes and try again.

```
curl: (52) Empty reply from server
```
→ Tunnel running but webhook server is down. Check Step 16.

```
HTTP 503 Service Unavailable
```
→ **CRITICAL:** See [Pitfall #1](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)
→ Missing or incorrect ingress rules in `~/.cloudflared/config.yml`

**Verification checklist:**
- [ ] Tunnel shows "Registered tunnel connection" messages (4 connections)
- [ ] No "No ingress rules" warning
- [ ] Public URL health check returns 200 OK
- [ ] `{"status": "healthy"}` in response
- [ ] Both webhook server AND tunnel are running simultaneously

**View tunnel logs in real-time:**
```bash
# If running in systemd (Linux)
sudo journalctl -u cloudflared-tunnel -f

# If running in LaunchAgent (macOS)
tail -f ~/Library/Logs/cloudflared.log

# If running in screen
screen -r cloudflared
```

**Cross-reference:**
- [Pitfall #1: Cloudflare Tunnel Missing Ingress Rules](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)
- [Step 15: Set Up Cloudflare Tunnel](#step-15-set-up-cloudflare-tunnel)

---

## GitHub Integration

### Step 18: Configure GitHub Webhook

**Device:** Laptop
**Account:** Main GitHub account (e.g., `odgsully`)

1. **Go to repository settings:**
   - URL: `https://github.com/odgsully/my-new-project/settings/hooks`

2. **Click "Add webhook"**

3. **Configure webhook:**
   - **Payload URL:** `https://adw-my-new-project.yourdomain.com/gh-webhook`
     - (Use your Cloudflare tunnel URL + `/gh-webhook`)
   - **Content type:** `application/json`
   - **Secret:** (leave empty for now)
   - **SSL verification:** ✅ Enable SSL verification
   - **Which events would you like to trigger this webhook?**
     - Select: **"Let me select individual events"**
     - ✅ **Issues**
     - ✅ **Issue comments**
   - **Active:** ✅ (checked)

4. **Click "Add webhook"**

5. **Verify webhook:**
   - GitHub will send a test "ping" event
   - Check **"Recent Deliveries"** tab
   - Should show: ✅ Green checkmark (200 response)
   - Body should show: `{"status":"ignored","reason":"Not a triggering event (event=ping, action=)"}`

### Step 19: Set Up Branch Protection

**Device:** Laptop
**Account:** Main GitHub account

1. **Go to:** `https://github.com/odgsully/my-new-project/settings/branches`
2. **Click "Add branch protection rule"**
3. **Configure:**
   - Branch name pattern: `main` (or `master`)
   - ✅ **Require pull request reviews before merging**
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
   - ✅ **Include administrators** (optional)
4. **Click "Create"**

This ensures ADW-created PRs must be reviewed before merging.

---

## Testing & Validation

### Step 20: Test Manual ADW Execution

**Device:** Server
**Account:** Bot account

**Create a test issue:**

**Device:** Laptop (browser)
**Account:** Main GitHub account

1. Go to: `https://github.com/YOUR-USERNAME/my-new-project/issues/new`
2. **Title:** `Test ADW Integration`
3. **Body:**
   ```markdown
   /chore

   Please add a test file at `test_adw.md` with basic ADW documentation.
   ```
4. Click **"Submit new issue"**
5. **Note the issue number** (e.g., #1) - you'll need this

**Run ADW manually on server:**

**Device:** Server
**Account:** Bot account

```bash
cd ~/my-new-project

# Run ADW agent for issue #1
uv run adws/adw_plan_build.py 1
# Replace '1' with your actual issue number
```

**✅ Expected console output:**
```
INFO - Starting ADW for issue #1
INFO - Issue fetched: Test ADW Integration
INFO - Classification: /chore
INFO - Generating plan...
INFO - Plan saved: specs/test-adw-integration-plan.md
INFO - Running implementation...
INFO - Implementation complete
INFO - Creating pull request...
INFO - Created pull request: https://github.com/YOUR-USERNAME/my-new-project/pull/2
INFO - ADW workflow completed successfully for issue #1
```

**Check execution logs:**
```bash
# Find the ADW ID (8-character UUID) from output
# Logs are at: agents/<ADW-ID>/adw_plan_build/execution.log

# List recent ADW runs
ls -lt agents/

# View most recent execution log
cat agents/*/adw_plan_build/execution.log | tail -50
```

**Example log file path:**
```
agents/cfb58bfd/adw_plan_build/execution.log
```

**Log file should contain:**
```
2025-10-04 15:35:14 - INFO - Starting ADW workflow for issue #1
2025-10-04 15:35:14 - INFO - issue_command: /chore
2025-10-04 15:37:05 - INFO - plan_file_path: specs/test-adw-integration-plan.md
2025-10-04 15:42:31 - INFO - implement_response: Successfully implemented changes
2025-10-04 15:43:42 - INFO - Created pull request: https://github.com/YOUR-USERNAME/my-new-project/pull/2
2025-10-04 15:43:43 - INFO - ADW workflow completed successfully for issue #1
```

**Check GitHub issue #1:**

**Device:** Laptop (browser)
**Account:** Main GitHub account

1. Go to: `https://github.com/YOUR-USERNAME/my-new-project/issues/1`
2. **Expected comments from bot (`YOUR-USERNAME-agents`):**
   - Classification comment: "Classified as: /chore"
   - Plan comment: Link to plan file in `specs/`
   - Implementation comment: Summary of changes made
   - PR link comment: Link to pull request

**Review Pull Request:**
1. Click PR link from issue comments
2. **Verify:**
   - ✅ Branch name contains ADW ID (e.g., `adw-cfb58bfd-test-adw-integration`)
   - ✅ Commit message includes ADW ID and issue reference
   - ✅ Changes match what was described in the plan
   - ✅ File `test_adw.md` was created (as requested)
   - ✅ PR description includes "🤖 Generated with Claude Code"
3. **Merge if acceptable** or request changes

**Verification checklist:**
- [ ] ADW command completed without errors
- [ ] Plan file created in `specs/` directory
- [ ] Bot posted comments to GitHub issue
- [ ] Pull request was created
- [ ] PR contains expected file changes
- [ ] Execution log shows "completed successfully"

**❌ Common errors:**

```
Error posting comment: GraphQL: Resource not accessible by personal access token
```
→ See [Pitfall #4](#pitfall-4-github_pat-overrides-gh-cli-authentication--most-common)
→ GITHUB_PAT is set but lacks permissions. Comment it out in .env and use gh CLI auth instead.

```
Error fetching issue: 404 Not Found
```
→ See [Pitfall #2](#pitfall-2-git-remote-points-to-wrong-repository)
→ Git remote points to wrong repository. Check `git remote -v`

```
Error: Claude Code CLI not found
```
→ See [Pitfall #3](#pitfall-3-claude_code_path-not-set-or-wrong)
→ CLAUDE_CODE_PATH not set or incorrect in .env

**Cross-reference:**
- [agents/<ADW-ID>/adw_plan_build/execution.log](#step-20-test-manual-adw-execution) - Execution logs location
- [specs/](#step-20-test-manual-adw-execution) - Generated plan files location

### Step 21: Test Webhook Trigger (End-to-End)

**Device:** Server
**Account:** Bot account

**Prerequisites:**
- ✅ Cloudflare tunnel is running (Step 17)
- ✅ Public URL health check works
- ✅ GitHub webhook is configured (Step 18)

**Start webhook server (if not already running):**
```bash
cd ~/my-new-project

# Start in background (or use screen/tmux)
uv run adws/trigger_webhook.py &

# Save process ID for later
WEBHOOK_PID=$!
echo "Webhook server PID: $WEBHOOK_PID"
```

**Or start in screen (recommended for testing):**
```bash
screen -S webhook
cd ~/my-new-project
uv run adws/trigger_webhook.py
# Detach: Ctrl+A, then D
```

**Verify both services are running:**
```bash
# Check webhook server
lsof -i :8001
# Should show: python/uv process on port 8001

# Check tunnel (in separate terminal)
ps aux | grep cloudflared
# Should show: cloudflared tunnel run command
```

**Create new test issue:**

**Device:** Laptop (browser)
**Account:** Main GitHub account

1. Go to: `https://github.com/YOUR-USERNAME/my-new-project/issues/new`
2. **Title:** `Test Webhook ADW Integration`
3. **Body:**
   ```markdown
   /feature

   Add a README section explaining how the webhook integration works.
   Include setup instructions and troubleshooting tips.
   ```
4. Click **"Submit new issue"**
5. **Note the issue number** (e.g., #2)

**Watch webhook server receive the event:**

**Option 1: If running in screen:**
```bash
# Reattach to screen
screen -r webhook
# You should see: "Received webhook for issue #2"
```

**Option 2: If running in background:**
```bash
# Check logs directory (if configured)
tail -f logs/webhook.log

# Or check system logs
# The webhook process will print to stdout/stderr
```

**Expected webhook server output:**
```
INFO:     POST /gh-webhook HTTP/1.1
INFO:     Received GitHub webhook event: issues
INFO:     Action: opened
INFO:     Issue #2: Test Webhook ADW Integration
INFO:     Triggering ADW for issue #2
INFO:     ADW workflow started in background (PID: 12345)
```

**Monitor ADW execution in real-time:**
```bash
# Watch for new ADW directories
watch -n 1 'ls -lt agents/ | head -5'

# Once ADW starts, find its ID and tail the log
# Replace <ADW-ID> with actual ID (e.g., cfb58bfd)
tail -f agents/<ADW-ID>/adw_plan_build/execution.log
```

**Example real-time log output:**
```
2025-10-04 15:45:10 - INFO - Starting ADW workflow for issue #2
2025-10-04 15:45:10 - INFO - issue_command: /feature
2025-10-04 15:45:15 - INFO - Classifying issue...
2025-10-04 15:45:20 - INFO - Classification: feature request
2025-10-04 15:47:30 - INFO - Generating plan...
2025-10-04 15:47:45 - INFO - plan_file_path: specs/test-webhook-adw-integration-plan.md
2025-10-04 15:50:15 - INFO - Running implementation...
2025-10-04 15:52:20 - INFO - Implementation complete
2025-10-04 15:52:45 - INFO - Creating pull request...
2025-10-04 15:53:10 - INFO - Created pull request: https://github.com/YOUR-USERNAME/my-new-project/pull/3
2025-10-04 15:53:11 - INFO - ADW workflow completed successfully for issue #2
```

**Check GitHub webhook delivery:**

**Device:** Laptop (browser)
**Account:** Main GitHub account

1. Go to: `https://github.com/YOUR-USERNAME/my-new-project/settings/hooks`
2. Click on your webhook
3. Click **"Recent Deliveries"** tab
4. **Find the delivery for issue #2:**
   - ✅ Response code: **200 OK**
   - ✅ Response body: `{"status":"success","message":"ADW triggered for issue #2"}`
   - ✅ Delivery timestamp matches when you created the issue

**Verify GitHub issue #2 comments:**

1. Go to: `https://github.com/YOUR-USERNAME/my-new-project/issues/2`
2. **Expected bot comments** (from `YOUR-USERNAME-agents`):
   - 🤖 "Acknowledged issue #2, processing with ADW ID: `<ADW-ID>`"
   - 📋 "Plan created: [View plan](../blob/.../specs/...)"
   - ✅ "Implementation complete"
   - 🔗 "Pull request created: #3"

**Verify Pull Request:**
1. Click PR link from issue
2. **Check PR details:**
   - ✅ Title includes issue number and task description
   - ✅ Branch name: `adw-<ADW-ID>-test-webhook-adw-integration`
   - ✅ README has new webhook section
   - ✅ PR description includes ADW ID and issue reference

**Verification checklist:**
- [ ] Webhook server received POST request from GitHub
- [ ] ADW workflow triggered automatically (no manual command)
- [ ] Execution log created in `agents/<ADW-ID>/adw_plan_build/execution.log`
- [ ] Plan file created in `specs/` directory
- [ ] Bot posted comments to GitHub issue
- [ ] Pull request created and linked
- [ ] GitHub webhook delivery shows 200 OK

**❌ Common webhook errors:**

```
GitHub webhook delivery shows: 503 Service Unavailable
```
→ **CRITICAL:** See [Pitfall #1](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)
→ Cloudflare tunnel missing ingress rules

```
GitHub webhook delivery shows: Connection refused
```
→ Webhook server not running. Check `lsof -i :8001`

```
GitHub webhook delivery shows: 200 OK but ADW didn't trigger
```
→ See [Pitfall #3](#pitfall-3-claude_code_path-not-set-or-wrong)
→ Webhook server started before .env was configured. Restart webhook server.

```
ADW triggered but no comments posted
```
→ See [Pitfall #4](#pitfall-4-github_pat-overrides-gh-cli-authentication--most-common)
→ GITHUB_PAT interfering with authentication

**Alternative test - Comment trigger:**

1. Go to any existing issue (e.g., issue #1 from Step 20)
2. Add a new comment with just: `adw`
3. **Expected behavior:**
   - Webhook receives `issue_comment` event
   - ADW triggers for that issue
   - Bot posts new comments
   - New PR created (if changes needed)

**File locations reference:**
- Webhook server code: `adws/trigger_webhook.py`
- Execution logs: `agents/<ADW-ID>/adw_plan_build/execution.log`
- Plan files: `specs/<issue-title-slug>-plan.md`
- Session logs: `logs/adw_<ADW-ID>.json`

**Cross-reference:**
- [Step 16: Test Webhook Server Locally](#step-16-test-webhook-server-locally)
- [Step 17: Start Cloudflare Tunnel](#step-17-start-cloudflare-tunnel)
- [Step 18: Configure GitHub Webhook](#step-18-configure-github-webhook)
- [Troubleshooting: Webhook Not Receiving Events](#webhook-not-receiving-events)

### Step 22: Test Cron Mode (Optional)

**Device:** Server
**Account:** Bot account

**Stop webhook server** (if running):
```bash
pkill -f trigger_webhook.py
```

**Start cron trigger:**
```bash
cd ~/my-new-project
uv run adws/trigger_cron.py
```

**Create test issue:**
- Same as above
- Cron will detect within 20 seconds

**Verify:**
- ✅ Issue detected and processed
- ✅ Works without webhooks

---

## Production Deployment

### Step 23: Set Up Systemd Service (Linux Server)

**Device:** Server
**Account:** System user (with sudo)

**Create webhook service:**
```bash
sudo nano /etc/systemd/system/adw-webhook.service
```

**Add content:**
```ini
[Unit]
Description=ADW Webhook Trigger
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/my-new-project
Environment="PATH=/home/your-username/.local/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/home/your-username/my-new-project/.env
ExecStart=/home/your-username/.local/bin/uv run adws/trigger_webhook.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Create tunnel service:**
```bash
sudo nano /etc/systemd/system/cloudflared-tunnel.service
```

**Add content:**
```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=your-username
ExecStart=/usr/local/bin/cloudflared tunnel run adw-webhook-my-new-project
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable adw-webhook cloudflared-tunnel
sudo systemctl start adw-webhook cloudflared-tunnel
```

**Check status:**
```bash
sudo systemctl status adw-webhook
sudo systemctl status cloudflared-tunnel
```

**View logs:**
```bash
sudo journalctl -u adw-webhook -f
sudo journalctl -u cloudflared-tunnel -f
```

### Step 24: Set Up LaunchAgent (macOS Server)

**Device:** Mac server (Mac Studio, Mac Mini)
**Account:** System user

**Create webhook LaunchAgent:**
```bash
nano ~/Library/LaunchAgents/com.adw.webhook.plist
```

**Add content:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.adw.webhook</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/ADW/.local/bin/uv</string>
        <string>run</string>
        <string>adws/trigger_webhook.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/ADW/my-new-project</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/ADW/.local/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/ADW/my-new-project/logs/webhook.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/ADW/my-new-project/logs/webhook.error.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

**Load and start:**
```bash
launchctl load ~/Library/LaunchAgents/com.adw.webhook.plist
launchctl start com.adw.webhook
```

**Check status:**
```bash
launchctl list | grep adw
tail -f ~/my-new-project/logs/webhook.log
```

**Similarly for Cloudflare tunnel:**
```bash
nano ~/Library/LaunchAgents/com.cloudflared.tunnel.plist
```

### Step 25: Set Up Monitoring & Alerts

**Device:** Server
**Account:** System user

**Create monitoring script:**
```bash
nano ~/adw-monitor.sh
```

**Add content:**
```bash
#!/bin/bash
# ADW Health Monitor

cd ~/my-new-project

# Check webhook server
if ! curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "ADW webhook server is down!" | mail -s "ADW Alert" your@email.com
fi

# Check tunnel
if ! curl -s https://adw-my-new-project.yourdomain.com/health | grep -q "healthy"; then
    echo "ADW tunnel is down!" | mail -s "ADW Alert" your@email.com
fi

# Check recent ADW runs for errors
ERROR_COUNT=$(find agents -name "execution.log" -mtime -1 -exec grep -l "ERROR" {} \; | wc -l)
if [ $ERROR_COUNT -gt 0 ]; then
    echo "ADW had $ERROR_COUNT errors in the last 24h" | mail -s "ADW Alert" your@email.com
fi
```

**Make executable:**
```bash
chmod +x ~/adw-monitor.sh
```

**Add to crontab (runs every 5 minutes):**
```bash
crontab -e
```

**Add line:**
```
*/5 * * * * /Users/ADW/adw-monitor.sh
```

### Step 26: Configure Log Rotation

**Device:** Server
**Account:** System user

**Create logrotate config (Linux):**
```bash
sudo nano /etc/logrotate.d/adw
```

**Add content:**
```
/home/your-username/my-new-project/logs/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 0644 your-username your-username
}
```

**For macOS, use a cron job:**
```bash
# Add to crontab
0 0 * * * find /Users/ADW/my-new-project/logs -name "*.log" -mtime +7 -delete
```

---

## Troubleshooting

**⚠️ IMPORTANT:** Before troubleshooting, review the [Critical Setup Pitfalls](#critical-setup-pitfalls) section - 80% of issues are covered there!

### Common Issues

#### Webhook Not Receiving Events
**Symptoms:** GitHub webhook shows errors, ADW not triggered

**Step-by-step diagnosis:**

1. **Check webhook server is running:**
   ```bash
   curl http://localhost:8001/health
   # ✅ Expected: {"status":"healthy"}
   # ❌ Connection refused: Server not running
   ```

2. **Check public tunnel is working:**
   ```bash
   curl https://adw-my-new-project.yourdomain.com/health
   # ✅ Expected: {"status":"healthy"}
   # ❌ 503 Service Unavailable: See Pitfall #1
   # ❌ Connection refused: Tunnel not running
   ```

3. **Check GitHub webhook deliveries:**
   - Go to: `https://github.com/YOUR-USERNAME/YOUR-REPO/settings/hooks`
   - Click your webhook → **Recent Deliveries** tab
   - Look for response codes:
     - ✅ 200 OK - Working correctly
     - ❌ 503 - See [Pitfall #1](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)
     - ❌ 502/504 - Webhook server timeout (server crashed or slow)
     - ❌ Connection refused - Tunnel or server down

4. **Verify both services are running:**
   ```bash
   # Check webhook server process
   lsof -i :8001
   # Should show: python or uv process

   # Check tunnel process
   ps aux | grep cloudflared
   # Should show: cloudflared tunnel run
   ```

**Solutions by error type:**

**Error: "503 Service Unavailable"**
→ See [Pitfall #1: Missing Ingress Rules](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)
→ Check `~/.cloudflared/config.yml` exists and has ingress rules

**Error: "Connection refused"**
→ Webhook server not running
→ Restart: `uv run adws/trigger_webhook.py`

**Error: "200 OK but ADW doesn't trigger"**
→ See [Pitfall #3: CLAUDE_CODE_PATH Not Set](#pitfall-3-claude_code_path-not-set-or-wrong)
→ Webhook server started before .env was configured
→ Solution: Kill webhook server, verify .env, restart webhook server

**Webhook server logs location:**
- If running in systemd: `sudo journalctl -u adw-webhook -f`
- If running in screen: `screen -r webhook`
- If running in background: Check stdout/stderr in terminal
- Production logs: `~/my-new-project/logs/webhook.log` (if configured)

**Cloudflare tunnel logs location:**
- If running in systemd: `sudo journalctl -u cloudflared-tunnel -f`
- If running in LaunchAgent: `~/Library/Logs/cloudflared.log`
- If running in screen: `screen -r cloudflared`

**Cross-reference:**
- [Pitfall #1: Cloudflare Tunnel Missing Ingress Rules](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)
- [Pitfall #3: CLAUDE_CODE_PATH Not Set](#pitfall-3-claude_code_path-not-set-or-wrong)
- [Step 16: Test Webhook Server Locally](#step-16-test-webhook-server-locally)
- [Step 17: Start Cloudflare Tunnel](#step-17-start-cloudflare-tunnel)

#### ADW Fails to Post Comments
**Symptoms:** ADW runs but no comments appear on GitHub issues

**⚠️ MOST COMMON CAUSE:** See [Pitfall #4: GITHUB_PAT Overrides gh CLI Auth](#pitfall-4-github_pat-overrides-gh-cli-authentication--most-common)

**Step-by-step diagnosis:**

1. **Check execution log for errors:**
   ```bash
   # Find most recent ADW run
   ls -lt agents/

   # Check for authentication errors
   cat agents/<adw_id>/adw_plan_build/execution.log | grep -i error
   ```

2. **Look for this specific error:**
   ```
   Error posting comment: GraphQL: Resource not accessible by personal access token (addComment)
   Error creating PR: Not Found (HTTP 404)
   ```
   → **This is Pitfall #4!** GITHUB_PAT is set but lacks permissions

3. **Verify GitHub authentication:**
   ```bash
   # Check which account gh CLI is authenticated as
   gh auth status
   # ✅ Expected: Logged in to github.com as YOUR-BOT-ACCOUNT
   # ❌ Bad: Not logged in
   ```

4. **Check if GITHUB_PAT is interfering:**
   ```bash
   # This should return NOTHING (line should be commented)
   grep "^GITHUB_PAT" .env

   # ✅ Expected: (no output) - means GITHUB_PAT is commented
   # ❌ Bad: GITHUB_PAT=ghp_xxxxx - This is the problem!
   ```

**Solutions by error type:**

**Error: "Resource not accessible by personal access token"**
→ **CRITICAL:** See [Pitfall #4](#pitfall-4-github_pat-overrides-gh-cli-authentication--most-common)
→ Solution:
```bash
# 1. Comment out GITHUB_PAT in .env
nano .env
# Change: GITHUB_PAT=ghp_xxxxx
# To:     # GITHUB_PAT=ghp_xxxxx

# 2. Restart webhook server to pick up .env changes
pkill -f trigger_webhook.py
uv run adws/trigger_webhook.py &
```

**Error: "Not logged in to github.com"**
→ GitHub CLI not authenticated
→ Solution:
```bash
# Authenticate as bot account
gh auth login
# Select: GitHub.com, HTTPS, Login with browser
# Verify: gh auth status
```

**Error: "403 Forbidden" or "Not Found"**
→ Bot account lacks write access to repository
→ Solution:
1. Go to: `https://github.com/YOUR-USERNAME/YOUR-REPO/settings/access`
2. Verify bot account is listed as collaborator
3. Verify bot has **Write** or **Admin** permissions

**How to verify it's working:**
```bash
# Test GitHub CLI can post comments
gh issue comment 1 --body "Test comment from bot"

# ✅ Expected: Comment appears on issue #1
# ❌ Error: Check authentication and permissions
```

**Authentication precedence (most important to understand):**
```
IF .env has GITHUB_PAT=xxx (uncommented):
    ✗ Uses GITHUB_PAT for all GitHub operations
    ✗ IGNORES gh auth login authentication
    ✗ GITHUB_PAT must have 'repo' scope or it will fail
ELSE:
    ✓ Uses gh CLI authentication (from gh auth login)
    ✓ Usually has all required permissions
```

**File to check:**
- `.env` - Look for uncommented GITHUB_PAT
- `adws/github.py:40-50` - See get_github_env() function for authentication logic
- `agents/<adw_id>/adw_plan_build/execution.log` - Check for error messages

**Cross-reference:**
- [Pitfall #4: GITHUB_PAT Overrides gh CLI Authentication](#pitfall-4-github_pat-overrides-gh-cli-authentication--most-common) ⚠️ **READ THIS**
- [Step 4: Authenticate GitHub CLI](#step-4-authenticate-github-cli)
- [Step 12: Configure Environment Variables](#step-12-configure-environment-variables)

#### Claude Code CLI Not Found
**Symptoms:** `Error: Claude Code CLI not found`

**Check:**
```bash
# Verify Claude Code is installed
which claude

# Check .env file
cat .env | grep CLAUDE_CODE_PATH
```

**Solutions:**
- Install Claude Code: https://docs.anthropic.com/en/docs/claude-code
- Update CLAUDE_CODE_PATH in `.env`
- Ensure PATH includes Claude Code location

#### Rate Limit Exceeded
**Symptoms:** GitHub API errors about rate limits

**Check:**
```bash
gh api rate_limit
```

**Solutions:**
- Switch from cron to webhook mode (more efficient)
- Increase polling interval in `trigger_cron.py`
- Wait for rate limit reset
- Use authenticated requests (ensure gh auth is working)

---

## Next Steps

Once your ADW system is fully operational:

1. **Create comprehensive documentation** in your repository's README
2. **Set up monitoring dashboards** (Grafana, Datadog, etc.)
3. **Configure backup systems** for agent outputs and logs
4. **Establish review processes** for ADW-generated PRs
5. **Train team members** on how to interact with ADW
6. **Monitor costs** (Anthropic API usage, GitHub Actions if used)
7. **Iterate on ADW configuration** based on performance

---

## Reference Checklist

Use this checklist when setting up ADW in a new repository:

### Pre-Setup
- [ ] GitHub bot account created (`{user}-agents`)
- [ ] Anthropic API key obtained
- [ ] Cloudflare account set up (for webhooks)
- [ ] Server/agent machine prepared

### Software Installation
- [ ] GitHub CLI installed (laptop)
- [ ] GitHub CLI installed (server)
- [ ] Claude Code CLI installed (laptop)
- [ ] Claude Code CLI installed (server)
- [ ] Python uv installed (laptop)
- [ ] Python uv installed (server)
- [ ] Cloudflare tunnel installed (server)

### Account Authentication
- [ ] GitHub CLI authenticated as main user (laptop)
- [ ] GitHub CLI authenticated as bot user (server)
- [ ] Bot added as collaborator to repository

### Repository Setup
- [ ] Repository created
- [ ] Repository cloned (laptop)
- [ ] Repository cloned (server)
- [ ] ADW files copied to new repository
- [ ] `.env` configured on server
- [ ] `.env` added to `.gitignore`
- [ ] Dependencies installed (`uv sync`)

### Webhook Configuration
- [ ] Cloudflare tunnel created
- [ ] Tunnel credentials saved
- [ ] Webhook server tested locally
- [ ] Tunnel tested publicly
- [ ] GitHub webhook configured
- [ ] Webhook delivery verified

### Testing
- [ ] Health check passes (`uv run adws/health_check.py`)
- [ ] Manual ADW execution works
- [ ] Webhook trigger works
- [ ] Comments posted successfully
- [ ] PR created successfully

### Production Deployment
- [ ] Systemd/LaunchAgent service created
- [ ] Services enabled and started
- [ ] Monitoring configured
- [ ] Log rotation set up
- [ ] Alerts configured
- [ ] Branch protection rules enabled

### Documentation
- [ ] README updated with ADW information
- [ ] Team trained on ADW usage
- [ ] Runbook created for common issues

---

## File Locations & Architecture Reference

This section provides a complete reference of where all ADW files, logs, and components are located.

### Project Directory Structure

```
~/my-new-project/                      # Repository root
├── .env                               # Environment variables (NEVER commit!)
├── .env.sample                        # Template for .env file
├── .gitignore                         # Should include .env
│
├── adws/                              # ADW Core System (copy from tac-4)
│   ├── adw_plan_build.py             # Main workflow orchestrator
│   ├── trigger_webhook.py            # Webhook server (port 8001)
│   ├── trigger_cron.py               # Cron-based trigger (polling mode)
│   ├── health_check.py               # System health validator
│   ├── github.py:40-50               # GitHub auth logic (GITHUB_PAT vs gh CLI)
│   └── sdlc_*.py                     # SDLC agent modules
│
├── agents/                            # ADW execution logs (generated)
│   └── <ADW-ID>/                     # 8-char UUID (e.g., cfb58bfd)
│       └── adw_plan_build/
│           └── execution.log         # Complete workflow log
│
├── specs/                             # Generated plan files
│   └── <issue-title-slug>-plan.md   # Planning phase output
│
├── logs/                              # Session logs (optional)
│   ├── adw_<ADW-ID>.json            # Structured session data
│   └── webhook.log                   # Webhook server logs (if configured)
│
├── .claude/                           # Claude Code configuration
│   └── ...                           # Claude Code settings
│
├── app/                               # Your application code
│   ├── server/                       # Backend
│   └── client/                       # Frontend
│
└── ADW_SETUP_GUIDE.md                # This guide
```

### System Configuration Files

**Environment Variables:**
- **Location:** `~/my-new-project/.env`
- **Purpose:** API keys, paths, authentication
- **Key variables:**
  - `ANTHROPIC_API_KEY` - Required for Claude Code
  - `CLAUDE_CODE_PATH` - Path to Claude CLI binary
  - `GITHUB_PAT` - ⚠️ Should be COMMENTED OUT
  - `CLOUDFLARED_TUNNEL_TOKEN` - For webhook mode
- **Cross-reference:** [Step 12](#step-12-configure-environment-variables), [Pitfall #3](#pitfall-3-claude_code_path-not-set-or-wrong), [Pitfall #4](#pitfall-4-github_pat-overrides-gh-cli-authentication--most-common)

**Cloudflare Tunnel Config:**
- **Location:** `~/.cloudflared/config.yml`
- **Purpose:** Routes tunnel traffic to webhook server
- **Required content:**
  ```yaml
  tunnel: <TUNNEL-ID>
  credentials-file: /Users/ADW/.cloudflared/<TUNNEL-ID>.json
  ingress:
    - service: http://localhost:8001
  ```
- **Cross-reference:** [Step 15](#step-15-set-up-cloudflare-tunnel), [Pitfall #1](#pitfall-1-cloudflare-tunnel-missing-ingress-rules)

**Tunnel Credentials:**
- **Location:** `~/.cloudflared/<TUNNEL-ID>.json`
- **Purpose:** Tunnel authentication
- **How to get:** Download from Cloudflare dashboard

**Git Configuration:**
- **Check remote:** `git remote -v`
- **Must point to:** Your repository (not forked source)
- **Cross-reference:** [Step 14](#step-14-configure-git-remote), [Pitfall #2](#pitfall-2-git-remote-points-to-wrong-repository)

### ADW Execution Artifacts

**Execution Logs:**
- **Pattern:** `agents/<ADW-ID>/adw_plan_build/execution.log`
- **Example:** `agents/cfb58bfd/adw_plan_build/execution.log`
- **Contains:**
  - Workflow start/end times
  - Issue classification
  - Plan generation output
  - Implementation results
  - PR creation confirmation
- **How to find most recent:**
  ```bash
  ls -lt agents/ | head -5
  cat agents/*/adw_plan_build/execution.log | tail -50
  ```

**Plan Files:**
- **Pattern:** `specs/<issue-title-slug>-plan.md`
- **Example:** `specs/test-adw-integration-plan.md`
- **Contains:** Step-by-step implementation plan from sdlc_planner agent

**Branch Names:**
- **Pattern:** `adw-<ADW-ID>-<issue-title-slug>`
- **Example:** `adw-cfb58bfd-test-adw-integration`
- **Contains:** All code changes for the issue

**Commit Messages:**
- **Pattern:** `<commit-message> [ADW-<ADW-ID>] [Issue #<number>]`
- **Example:** `Add test documentation [ADW-cfb58bfd] [Issue #5]`

### Service Logs

**Webhook Server:**
- **If running in systemd (Linux):**
  ```bash
  sudo journalctl -u adw-webhook -f
  ```
- **If running in LaunchAgent (macOS):**
  ```bash
  tail -f ~/my-new-project/logs/webhook.log
  ```
- **If running in screen:**
  ```bash
  screen -r webhook
  ```

**Cloudflare Tunnel:**
- **If running in systemd (Linux):**
  ```bash
  sudo journalctl -u cloudflared-tunnel -f
  ```
- **If running in LaunchAgent (macOS):**
  ```bash
  tail -f ~/Library/Logs/cloudflared.log
  ```
- **If running in screen:**
  ```bash
  screen -r cloudflared
  ```

### GitHub Integration Points

**Webhook Configuration:**
- **URL:** `https://github.com/YOUR-USERNAME/YOUR-REPO/settings/hooks`
- **Payload URL:** `https://your-tunnel-url.com/gh-webhook`
- **Events:** Issues, Issue comments
- **Deliveries:** Settings → Hooks → Your webhook → Recent Deliveries

**Bot Account Comments:**
- **Pattern:** Posted by `YOUR-USERNAME-agents` (bot account)
- **Location:** On each processed issue
- **Contains:** Classification, plan link, implementation summary, PR link

**Pull Requests:**
- **Created by:** Bot account (`YOUR-USERNAME-agents`)
- **Title pattern:** Derived from issue title
- **Branch:** `adw-<ADW-ID>-<issue-title-slug>`
- **Description includes:** "🤖 Generated with Claude Code"

### Network Ports & URLs

**Webhook Server:**
- **Local port:** 8001
- **Local URL:** `http://localhost:8001`
- **Health endpoint:** `http://localhost:8001/health`
- **Webhook endpoint:** `http://localhost:8001/gh-webhook` (POST)

**Cloudflare Tunnel:**
- **Public URL:** `https://your-subdomain.yourdomain.com`
- **Health check:** `https://your-subdomain.yourdomain.com/health`
- **Webhook endpoint:** `https://your-subdomain.yourdomain.com/gh-webhook`

### ADW ID Tracking

The **ADW ID** is an 8-character UUID that uniquely identifies each workflow execution. It appears in:

1. **Execution log directory:** `agents/cfb58bfd/`
2. **Branch name:** `adw-cfb58bfd-issue-title`
3. **Commit messages:** `[ADW-cfb58bfd]`
4. **GitHub comments:** "Processing with ADW ID: cfb58bfd"
5. **Session logs:** `logs/adw_cfb58bfd.json`

This allows complete traceability from GitHub issue → logs → branch → commit → PR.

### Quick Reference Commands

**Find most recent ADW run:**
```bash
ls -lt agents/ | head -1
```

**View latest execution log:**
```bash
cat agents/*/adw_plan_build/execution.log | tail -50
```

**Check webhook server status:**
```bash
lsof -i :8001
```

**Check tunnel status:**
```bash
ps aux | grep cloudflared
```

**Test health endpoints:**
```bash
curl http://localhost:8001/health              # Local webhook server
curl https://your-tunnel-url.com/health        # Public tunnel
```

**Check git remote:**
```bash
git remote -v
```

**Check environment variables:**
```bash
grep -E "^(ANTHROPIC|CLAUDE|GITHUB)" .env
```

**Check GitHub authentication:**
```bash
gh auth status
```

**Find all ADW-related branches:**
```bash
git branch -a | grep adw-
```

**Count ADW executions:**
```bash
ls -1 agents/ | wc -l
```

### Important Source Code References

**Authentication logic:**
- File: `adws/github.py`
- Lines: 40-50
- Function: `get_github_env()`
- Behavior: Returns GITHUB_PAT if set, else uses gh CLI auth

**Webhook server:**
- File: `adws/trigger_webhook.py`
- Port: 8001
- Endpoints: `/health`, `/gh-webhook`

**Main workflow:**
- File: `adws/adw_plan_build.py`
- Entry point: `main(issue_number)`
- Creates: Plan → Implementation → PR

**Health check:**
- File: `adws/health_check.py`
- Validates: Environment, Git, Claude CLI, GitHub CLI

---

## Support & Resources

- **ADW Documentation:** See `adws/README.md` in this repository
- **Claude Code Docs:** https://docs.anthropic.com/en/docs/claude-code
- **GitHub CLI Docs:** https://cli.github.com/manual/
- **Cloudflare Tunnel Docs:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

### Getting Help

1. **First, check:** [Critical Setup Pitfalls](#critical-setup-pitfalls) section
2. **Then check:** [Troubleshooting](#troubleshooting) section
3. **Review logs:**
   - Execution: `agents/<ADW-ID>/adw_plan_build/execution.log`
   - Webhook: `sudo journalctl -u adw-webhook -f` or `screen -r webhook`
   - Tunnel: `sudo journalctl -u cloudflared-tunnel -f` or `screen -r cloudflared`
4. **Verify configuration:**
   - `.env` file settings
   - `~/.cloudflared/config.yml` ingress rules
   - `git remote -v` points to correct repo
   - `gh auth status` shows correct account

---

**Last Updated:** 2025-10-04
**Version:** 2.0.0
**Maintainer:** ADW System
**Contributors:** odgsully, Claude Code
