# ADW Webhook Setup Guide

Complete step-by-step guide to set up the ADW webhook system with Cloudflare Tunnel and GitHub.

## Overview

This setup enables GitHub to automatically trigger the ADW (AI Developer Workflow) system when:
- A new issue is created
- Someone comments "adw" on an issue

## Architecture

```
GitHub → Cloudflare Tunnel → Mac Studio (localhost:8001) → trigger_webhook.py → adw_plan_build.py
```

## Prerequisites

- Cloudflare account (free tier works)
- GitHub repository with issues enabled
- Mac Studio with webhook server running
- SSH access to Mac Studio from laptop

---

## Part 1: Mac Studio Setup

### Step 1: Install Cloudflared

```bash
# On Mac Studio
brew install cloudflare/cloudflare/cloudflared

# Verify installation
cloudflared --version
```

### Step 2: Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

This will:
- Open a browser window
- Ask you to log in to Cloudflare
- Select a domain (or use the default)
- Download a cert file to `~/.cloudflared/cert.pem`

### Step 3: Create a Named Tunnel

```bash
cloudflared tunnel create adw-webhook
```

Expected output:
```
Tunnel credentials written to /Users/yourname/.cloudflared/<TUNNEL-ID>.json
Created tunnel adw-webhook with id <TUNNEL-ID>
```

**Important:** Save the `<TUNNEL-ID>` shown in the output.

### Step 4: Configure the Tunnel

Create a configuration file:

```bash
mkdir -p ~/.cloudflared
nano ~/.cloudflared/config.yml
```

Add this content (replace `<TUNNEL-ID>` with your actual tunnel ID):

```yaml
tunnel: <TUNNEL-ID>
credentials-file: /Users/yourname/.cloudflared/<TUNNEL-ID>.json

ingress:
  - hostname: adw-webhook.yourdomain.com  # Optional: use a custom subdomain
    service: http://localhost:8001
  - service: http_status:404
```

**OR** for a simpler setup without custom domain:

```yaml
tunnel: <TUNNEL-ID>
credentials-file: /Users/yourname/.cloudflared/<TUNNEL-ID>.json

ingress:
  - service: http://localhost:8001
```

Save and exit (Ctrl+X, then Y, then Enter).

### Step 5: Get Your Tunnel Token

```bash
cloudflared tunnel token adw-webhook
```

This outputs a very long token string starting with `eyJ...`

**Copy this entire token** - you'll need it next.

### Step 6: Add Token to Environment

```bash
# In your project directory on Mac Studio
cd /path/to/tac-4

# Copy the sample env file if you haven't already
cp .env.sample .env

# Edit .env
nano .env
```

Find the line:
```bash
CLOUDFLARED_TUNNEL_TOKEN=
```

Paste your token after the `=`:
```bash
CLOUDFLARED_TUNNEL_TOKEN=eyJhIjoiYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY3ODkwIiwidCI6ImFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6MTIzNDU2Nzg5MCIsInMiOiJhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ejEyMzQ1Njc4OTAifQ==
```

Save and exit.

### Step 7: Start the Webhook Server

Open a terminal window on Mac Studio:

```bash
cd /path/to/tac-4
uv run adws/trigger_webhook.py
```

Expected output:
```
Starting ADW Webhook Trigger on port 8001
Starting server on http://0.0.0.0:8001
Webhook endpoint: POST /gh-webhook
Health check: GET /health
```

**Keep this terminal running.**

### Step 8: Start the Cloudflare Tunnel

Open a **NEW** terminal window on Mac Studio:

```bash
cd /path/to/tac-4
./scripts/expose_webhook.sh
```

**OR** run manually:

```bash
cloudflared tunnel run adw-webhook
```

Expected output:
```
2024-01-15T10:30:45Z INF Starting tunnel tunnelID=<TUNNEL-ID>
2024-01-15T10:30:46Z INF Registered tunnel connection connIndex=0
2024-01-15T10:30:46Z INF +--------------------------------------------------------------------------------------------+
2024-01-15T10:30:46Z INF |  Your quick Tunnel has been created! Visit it at:                                          |
2024-01-15T10:30:46Z INF |  https://adw-webhook-abc-def.trycloudflare.com                                             |
2024-01-15T10:30:46Z INF +--------------------------------------------------------------------------------------------+
```

**⚠️ IMPORTANT: Copy the URL shown** (e.g., `https://adw-webhook-abc-def.trycloudflare.com`)

**Keep this terminal running.**

### Step 9: Test the Setup

In a **third** terminal window or from your laptop:

```bash
# Test health endpoint
curl https://your-tunnel-url.trycloudflare.com/health

# Should return:
# {"status":"healthy","service":"adw-webhook-trigger",...}
```

---

## Part 2: GitHub Configuration

### Step 10: Configure GitHub Webhook

1. Go to your GitHub repository
2. Click **Settings** → **Webhooks** → **Add webhook**

3. Fill in:
   - **Payload URL**: `https://your-tunnel-url.trycloudflare.com/gh-webhook`
   - **Content type**: `application/json`
   - **Secret**: Leave blank (optional: add for security)
   - **Which events**: Select "Let me select individual events"
     - ✅ Issues
     - ✅ Issue comments
   - ✅ Active

4. Click **Add webhook**

### Step 11: Verify Webhook

GitHub will send a test ping. Check:

1. In the webhook settings, you should see a green checkmark ✅
2. In your Mac Studio terminal (running `trigger_webhook.py`), you might see a log entry

---

## Part 3: Testing the System

### Step 12: Test with a New Issue

1. Create a new issue in your GitHub repository
2. Watch the Mac Studio terminal running `trigger_webhook.py`

Expected output:
```
Received webhook: event=issues, action=opened, issue_number=123
Launching background process: uv run adws/adw_plan_build.py 123 a1b2c3d4
Background process started for issue #123 with ADW ID: a1b2c3d4
```

3. Check the issue - ADW should add a comment and start working
4. After a few minutes, a pull request should be created

### Step 13: Test with "adw" Comment

1. On any existing issue, add a comment with just: `adw`
2. Watch the webhook server terminal

Expected output:
```
Received webhook: event=issue_comment, action=created, issue_number=456
Comment body: 'adw'
Launching background process: uv run adws/adw_plan_build.py 456 e5f6g7h8
```

---

## Part 4: Laptop Access (Optional)

### Step 14: SSH Tunnel from Laptop

If you want to manage the webhook from your laptop:

```bash
# From laptop
ssh mac-studio

# Once connected, navigate to project
cd /path/to/tac-4

# Check if webhook is running
lsof -i :8001

# View webhook logs
tail -f logs/webhook.log  # if you set up logging

# Check tunnel status
ps aux | grep cloudflared
```

---

## Troubleshooting

### Webhook not receiving events

1. **Check tunnel is running**:
   ```bash
   ps aux | grep cloudflared
   ```

2. **Check webhook server is running**:
   ```bash
   lsof -i :8001
   ```

3. **Test endpoint manually**:
   ```bash
   curl https://your-tunnel-url.trycloudflare.com/health
   ```

4. **Check GitHub webhook deliveries**:
   - Go to Settings → Webhooks → Click on your webhook
   - Click "Recent Deliveries" tab
   - Look for error messages

### Tunnel keeps disconnecting

**Problem**: Named tunnel URL changes between restarts.

**Solution**: Make sure you're using a named tunnel (not quick tunnel):
```bash
# Check running tunnel
cloudflared tunnel list

# Should show your tunnel as "active"
```

### Port 8001 already in use

```bash
# Find what's using the port
lsof -i :8001

# Kill the process
kill -9 <PID>

# Or use the helper script
./scripts/kill_trigger_webhook.sh
```

### Environment variables not loading

```bash
# Verify .env file exists in project root
ls -la .env

# Check the token is set
grep CLOUDFLARED_TUNNEL_TOKEN .env

# Should show: CLOUDFLARED_TUNNEL_TOKEN=eyJ...
```

### ADW workflow not starting

1. **Check logs**:
   ```bash
   ls -la agents/*/adw_plan_build/
   cat agents/<adw-id>/adw_plan_build/execution.log
   ```

2. **Verify environment variables**:
   ```bash
   # Check required vars
   env | grep -E "(GITHUB_REPO_URL|ANTHROPIC_API_KEY|CLAUDE_CODE_PATH)"
   ```

3. **Test manually**:
   ```bash
   uv run adws/adw_plan_build.py <issue-number>
   ```

---

## Production Deployment

### Running as a Service (systemd)

Create `/etc/systemd/system/adw-webhook.service`:

```ini
[Unit]
Description=ADW Webhook Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/tac-4
Environment=PATH=/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/local/bin/uv run adws/trigger_webhook.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/adw-tunnel.service`:

```ini
[Unit]
Description=Cloudflare Tunnel for ADW
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/usr/local/bin/cloudflared tunnel run adw-webhook
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable adw-webhook
sudo systemctl enable adw-tunnel
sudo systemctl start adw-webhook
sudo systemctl start adw-tunnel

# Check status
sudo systemctl status adw-webhook
sudo systemctl status adw-tunnel
```

---

## Security Best Practices

1. **Add webhook secret**: In GitHub webhook settings, add a secret and validate it in `trigger_webhook.py`
2. **Use environment variables**: Never commit `.env` file
3. **Restrict tunnel access**: Use Cloudflare Access to add authentication
4. **Monitor logs**: Set up log rotation and monitoring
5. **Rate limiting**: Add rate limiting to webhook endpoint
6. **Branch protection**: Require PR reviews for ADW changes

---

## Quick Reference

### Starting Everything

```bash
# Terminal 1: Webhook server
cd /path/to/tac-4
uv run adws/trigger_webhook.py

# Terminal 2: Cloudflare tunnel
./scripts/expose_webhook.sh
```

### Stopping Everything

```bash
# Stop webhook
./scripts/kill_trigger_webhook.sh

# Stop tunnel
pkill cloudflared

# Or stop all
./scripts/stop_apps.sh
```

### Checking Status

```bash
# Check webhook server
curl http://localhost:8001/health

# Check tunnel
curl https://your-tunnel-url.trycloudflare.com/health

# Check GitHub webhook
gh api repos/OWNER/REPO/hooks
```

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs in `agents/*/adw_plan_build/execution.log`
3. Test components individually (webhook server, tunnel, GitHub webhook)
4. Verify all environment variables are set correctly
