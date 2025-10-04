# ADW Complete Setup Guide
**End-to-End Repository Setup for AI Developer Workflows**

This guide provides step-by-step instructions to set up the ADW (AI Developer Workflow) system in any new repository, enabling autonomous issue processing via AI agents.

---

## Table of Contents
1. [Requirements](#requirements)
2. [Account Setup](#account-setup)
3. [Local Machine Setup](#local-machine-setup)
4. [Repository Setup](#repository-setup)
5. [ADW System Installation](#adw-system-installation)
6. [Webhook Server Setup](#webhook-server-setup)
7. [GitHub Integration](#github-integration)
8. [Testing & Validation](#testing--validation)
9. [Production Deployment](#production-deployment)
10. [Troubleshooting](#troubleshooting)

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
# (REQUIRED) Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE

# (REQUIRED) Claude Code path from `which claude`
CLAUDE_CODE_PATH=/Users/ADW/.nvm/versions/node/v22.20.0/bin/claude

# (OPTIONAL) GitHub PAT - COMMENT OUT to use gh CLI auth
# GITHUB_PAT=ghp_xxxxx

# (OPTIONAL) E2B for sandboxed execution
# E2B_API_KEY=e2b_xxxxx

# (OPTIONAL) Cloudflare tunnel token
# CLOUDFLARED_TUNNEL_TOKEN=xxxxx

# (OPTIONAL) Claude Code OAuth
# CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-xxxxx
```

**Save and verify:**
```bash
# Test environment loading
source .env
echo $ANTHROPIC_API_KEY
# Should show: sk-ant-api03-...
```

**Important:** Add `.env` to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

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

**Verify remote URL:**
```bash
git remote -v
# Should show: origin  https://github.com/odgsully/my-new-project.git
```

**Important:** Ensure the remote points to the correct repository for the bot to push changes.

---

## Webhook Server Setup

### Step 15: Set Up Cloudflare Tunnel

**Device:** Server
**Account:** System user

#### Create Cloudflare Tunnel:

1. **Log in to Cloudflare Dashboard:**
   - Go to: https://one.dash.cloudflare.com/
   - Navigate to: **Zero Trust** → **Networks** → **Tunnels**

2. **Create Tunnel:**
   - Click **"Create a tunnel"**
   - Name: `adw-webhook-{project}` (e.g., `adw-webhook-my-new-project`)
   - Click **"Save tunnel"**

3. **Install Connector (on server):**
   ```bash
   # Cloudflare will provide a command like:
   cloudflared service install <TOKEN>

   # Or save token for manual runs:
   export CLOUDFLARED_TUNNEL_TOKEN="<TOKEN>"
   ```

4. **Configure Public Hostname:**
   - Click **"Add a public hostname"**
   - Subdomain: `adw-my-new-project`
   - Domain: Select your domain
   - Path: (leave empty)
   - Service Type: `HTTP`
   - URL: `localhost:8001`
   - Click **"Save"**

5. **Save Tunnel Details:**
   - Tunnel ID: (copy this, e.g., `5740df70-fda1-433d-b8dd-71188f8ac566`)
   - Public URL: (e.g., `https://adw-my-new-project.yourdomain.com`)
   - Token: (already saved to .env)

#### Create Cloudflare Config (if using named tunnel):

**Device:** Server

```bash
mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: <TUNNEL-ID>
credentials-file: /Users/ADW/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: "*"
    service: http://localhost:8001
  - service: http_status:404
EOF
```

**Download credentials file:**
- Get from Cloudflare dashboard: **Tunnels** → Your tunnel → **Configure** → Download JSON
- Save to: `~/.cloudflared/<TUNNEL-ID>.json`

### Step 16: Test Webhook Server Locally

**Device:** Server
**Account:** Bot account

**Start webhook listener:**
```bash
cd ~/my-new-project
uv run adws/trigger_webhook.py
```

**Expected output:**
```
Starting ADW Webhook Trigger on port 8001
Starting server on http://0.0.0.0:8001
Webhook endpoint: POST /gh-webhook
Health check: GET /health
INFO:     Uvicorn running on http://0.0.0.0:8001
```

**In another terminal (or SSH session), test health endpoint:**
```bash
curl http://localhost:8001/health
```

**Expected response:**
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

**Stop the server:** `Ctrl+C`

### Step 17: Start Cloudflare Tunnel

**Device:** Server
**Account:** System user

**Option A: Quick Tunnel (Temporary URL, testing only):**
```bash
cloudflared tunnel --url http://localhost:8001
```

**Output will show:**
```
Your quick Tunnel has been created! Visit it at:
https://random-words-here.trycloudflare.com
```

**Option B: Named Tunnel (Production, persistent URL):**
```bash
cloudflared tunnel run adw-webhook-{project}
```

**Keep this running in background (screen/tmux/systemd).**

**Test public URL:**
```bash
curl https://adw-my-new-project.yourdomain.com/health
```

Should return same health check JSON.

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

1. Go to: `https://github.com/odgsully/my-new-project/issues/new`
2. Title: `Test ADW Integration`
3. Body:
   ```
   /chore

   Please add a test file at `test_adw.md` with basic ADW documentation.
   ```
4. Click **"Submit new issue"**
5. Note the issue number (e.g., #1)

**Run ADW manually on server:**

**Device:** Server
**Account:** Bot account

```bash
cd ~/my-new-project
uv run adws/adw_plan_build.py 1
```

**Watch for:**
- ✅ Issue fetched successfully
- ✅ Classification: `/chore`
- ✅ Plan created in `specs/`
- ✅ Implementation runs
- ✅ Comments posted to issue
- ✅ PR created

**Check GitHub issue #1:**
- Should see comments from `odgsully-agents`
- Should see PR link in final comment

**Review PR:**
- Verify changes match the plan
- Merge if acceptable

### Step 21: Test Webhook Trigger

**Device:** Server
**Account:** Bot account

**Start webhook server:**
```bash
cd ~/my-new-project
uv run adws/trigger_webhook.py &
```

**Start Cloudflare tunnel (if not already running):**
```bash
cloudflared tunnel run adw-webhook-{project} &
```

**Create new test issue:**

**Device:** Laptop (browser)
**Account:** Main GitHub account

1. Create issue #2: `Test Webhook ADW Integration`
2. Body: `/feature - Add README section about webhooks`
3. Submit

**Watch server logs:**
```bash
# The webhook server should receive the event and trigger ADW
# Check logs in: agents/<adw_id>/adw_plan_build/execution.log
```

**Verify:**
- ✅ Webhook received (check server output)
- ✅ ADW triggered automatically
- ✅ Comments posted to issue
- ✅ PR created

**Alternative test - Comment trigger:**
1. Go to any existing issue
2. Add comment: `adw`
3. ADW should trigger and process the issue

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

### Common Issues

#### Webhook Not Receiving Events
**Symptoms:** GitHub webhook shows errors, ADW not triggered

**Check:**
```bash
# 1. Verify webhook server is running
curl http://localhost:8001/health

# 2. Verify tunnel is running
curl https://adw-my-new-project.yourdomain.com/health

# 3. Check GitHub webhook deliveries
# Go to: Settings → Webhooks → Recent Deliveries
```

**Solutions:**
- Restart webhook server: `systemctl restart adw-webhook`
- Restart tunnel: `systemctl restart cloudflared-tunnel`
- Check firewall rules
- Verify webhook URL in GitHub settings

#### ADW Fails to Post Comments
**Symptoms:** ADW runs but no comments appear on GitHub issues

**Check:**
```bash
# Verify GitHub authentication
gh auth status

# Check execution log
cat agents/<adw_id>/adw_plan_build/execution.log | grep -i error
```

**Solutions:**
- Re-authenticate: `gh auth login`
- Verify bot has write access to repository
- Check if GITHUB_PAT is interfering (comment out in `.env`)

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

## Support & Resources

- **ADW Documentation:** See `adws/README.md` in this repository
- **Claude Code Docs:** https://docs.anthropic.com/en/docs/claude-code
- **GitHub CLI Docs:** https://cli.github.com/manual/
- **Cloudflare Tunnel Docs:** https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/

---

**Last Updated:** 2025-10-04
**Version:** 1.0.0
**Maintainer:** ADW System
