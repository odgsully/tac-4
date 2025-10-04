# Natural Language SQL Interface

A web application that converts natural language queries to SQL using AI, built with FastAPI and Vite + TypeScript.

## Features

- 🗣️ Natural language to SQL conversion using OpenAI or Anthropic
- 📁 Drag-and-drop file upload (.csv and .json)
- 📊 Interactive table results display
- 🔒 SQL injection protection
- ⚡ Fast development with Vite and uv

## Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key and/or Anthropic API key
- 'gh' github cli
- astral uv

## Setup

### 1. Install Dependencies

```bash
# Backend
cd app/server
uv sync --all-extras

# Frontend
cd app/client
npm install
```

### 2. Environment Configuration

Set up your API keys in the server directory:

```bash
cp .env.sample .env
```

and

```bash
cd app/server
cp .env.sample .env
# Edit .env and add your API keys
```

## Quick Start

Use the provided script to start both services:

```bash
./scripts/start.sh
```

Press `Ctrl+C` to stop both services.

The script will:
- Check that `.env` exists in `app/server/`
- Start the backend on http://localhost:8000
- Start the frontend on http://localhost:5173
- Handle graceful shutdown when you exit

## Manual Start (Alternative)

### Backend
```bash
cd app/server
# .env is loaded automatically by python-dotenv
uv run python server.py
```

### Frontend
```bash
cd app/client
npm run dev
```

## Usage

1. **Upload Data**: Click "Upload Data" to open the modal
   - Use sample data buttons for quick testing
   - Or drag and drop your own .csv or .json files
   - Uploading a file with the same name will overwrite the existing table
2. **Query Your Data**: Type a natural language query like "Show me all users who signed up last week"
   - Press `Cmd+Enter` (Mac) or `Ctrl+Enter` (Windows/Linux) to run the query
3. **View Results**: See the generated SQL and results in a table format
4. **Manage Tables**: Click the × button on any table to remove it

## Development

### Backend Commands
```bash
cd app/server
uv run python server.py      # Start server with hot reload
uv run pytest               # Run tests
uv add <package>            # Add package to project
uv remove <package>         # Remove package from project
uv sync --all-extras        # Sync all extras
```

### Frontend Commands
```bash
cd app/client
npm run dev                 # Start dev server
npm run build              # Build for production
npm run preview            # Preview production build
```

## Project Structure

```
.
├── app/                    # Main application
│   ├── client/             # Vite + TypeScript frontend
│   └── server/             # FastAPI backend
│
├── adws/                   # AI Developer Workflows - Core agent system
├── scripts/                # Utility scripts (start.sh, stop_apps.sh)
├── specs/                  # Feature specifications
├── ai_docs/                # AI/LLM documentation
├── agents/                 # Agent execution logging
└── logs/                   # Structured session logs
```

## ADWs

The ADW (AI Developer Workflow) system is an automated software development pipeline that monitors GitHub issues and uses Claude Code CLI to autonomously classify, plan, implement, and create pull requests for requested changes.

**Entry Point Scripts:**

- **Health & Diagnostics**
  - `uv run adws/health_check.py` - Validates ADW system configuration and dependencies
- **Triggers**
  - `uv run adws/trigger_webhook.py` - Real-time webhook server for instant GitHub event processing
  - `uv run adws/trigger_cron.py` - Polling-based monitor (checks issues every 20 seconds)
- **Workflow**
  - `uv run adws/adw_plan_build.py <issue-number>` - Process a specific issue manually

For detailed ADW documentation, see the sections below or [adws/README.md](adws/README.md).

## ADW Architecture

ADW is a meta-programming system that uses AI to write code. It monitors GitHub issues, analyzes requirements, generates implementation plans, executes changes, and creates pull requests—all autonomously.

**High-Level Architecture:**
- **Monitoring Layer**: Detects new issues via webhooks (real-time) or polling (every 20 seconds)
- **Classification Layer**: Uses Claude Code CLI to determine issue type (`/chore`, `/bug`, `/feature`)
- **Planning Layer**: Generates detailed implementation plans saved to `specs/`
- **Execution Layer**: Implements the plan with code changes, tests, and validation
- **Integration Layer**: Creates semantic branches, commits, and pull requests

**Workflow Pipeline:**
```
1. Trigger Detection (webhook/cron/manual)
   └─> New issue or "adw" comment detected
2. Issue Classification (issue_classifier agent)
   └─> Determines /chore, /bug, or /feature
3. Plan Generation (sdlc_planner agent)
   └─> Creates implementation plan in specs/
4. Implementation (sdlc_implementor agent)
   └─> Executes plan with code changes
5. PR Creation (branch_generator + pr_creator agents)
   └─> Commits changes and creates pull request
```

Each workflow run is assigned a unique 8-character ADW ID (e.g., `a1b2c3d4`) that appears in GitHub comments, log files, branch names, and commits for complete traceability.

## ADW Core Components

The ADW system is built on eight Python modules that handle different aspects of the automated workflow:

**Core Workflow & Integration:**
- **adw_plan_build.py** (535 lines) - Main orchestrator that coordinates the entire workflow
  - Manages multi-agent pipeline from classification to PR creation
  - Handles error checking and GitHub issue commenting throughout process
  - Uses specialized agents: `issue_classifier`, `sdlc_planner`, `plan_finder`, `sdlc_implementor`, `branch_generator`, `pr_creator`

- **agent.py** (263 lines) - Claude Code CLI integration layer
  - Executes prompts programmatically via Claude Code CLI
  - Manages environment variables and API authentication
  - Parses JSONL output streams and converts to structured JSON
  - Saves prompts to disk for debugging and reproducibility

**Data & GitHub Integration:**
- **data_types.py** (144 lines) - Type-safe Pydantic models
  - GitHub API response models: `GitHubIssue`, `GitHubUser`, `GitHubComment`
  - Agent communication models: `AgentPromptRequest`, `AgentPromptResponse`
  - Slash command type definitions for workflow stages

- **github.py** (281 lines) - GitHub operations via gh CLI
  - Fetches issues and comments using GitHub CLI
  - Posts status updates and comments to issues
  - Extracts repository URL from git remote configuration
  - Handles authentication via `GITHUB_PAT` or `gh auth login`

**Utilities & Infrastructure:**
- **utils.py** (79 lines) - Core utilities
  - Generates unique 8-character ADW IDs using UUID
  - Configures structured logging (console: INFO+, file: DEBUG+)
  - Creates organized log directory structure per ADW run

- **health_check.py** (397 lines) - System health validation
  - Validates required environment variables (`ANTHROPIC_API_KEY`, etc.)
  - Checks git repository configuration and working directory
  - Tests Claude Code CLI functionality and version
  - Verifies GitHub CLI authentication status
  - Can post diagnostic results to GitHub issues

**Trigger Mechanisms:**
- **trigger_webhook.py** (207 lines) - FastAPI webhook server
  - Receives GitHub webhook events (issues opened, issue comments)
  - Launches `adw_plan_build.py` in background process
  - Provides `/health` endpoint for monitoring
  - Responds within GitHub's 10-second webhook timeout

- **trigger_cron.py** (224 lines) - Polling-based trigger
  - Polls GitHub every 20 seconds for new or updated issues
  - Detects issues with no comments or latest comment "adw"
  - Tracks processed issues to prevent duplicate runs
  - Handles graceful shutdown on `SIGINT`/`SIGTERM`

## ADW Workflow Details

The ADW system executes a five-stage pipeline, with each stage handled by specialized AI agents that use Claude Code's slash command interface:

### 1. Trigger Stage
**How Issues Are Detected:**
- **Webhook Mode** (`trigger_webhook.py`): Real-time GitHub events trigger instant processing
  - Listens for "issues.opened" and "issue_comment.created" events
  - Processes immediately when "adw" appears in comment
- **Cron Mode** (`trigger_cron.py`): Polls GitHub every 20 seconds
  - Detects new issues with no comments
  - Detects issues where latest comment is "adw"
- **Manual Mode** (`adw_plan_build.py`): Direct execution for specific issue numbers

### 2. Classification Stage
**Agent:** `issue_classifier` (via `/classify_issue` slash command)
- Analyzes issue title, body, and labels
- Determines appropriate workflow type:
  - `/chore` - Documentation, refactoring, maintenance, tests
  - `/bug` - Bug fixes, error corrections, patches
  - `/feature` - New functionality, enhancements, features
- Posts classification to GitHub issue with ADW ID tracking comment

### 3. Planning Stage
**Agents:** `sdlc_planner` + `plan_finder`
- **sdlc_planner** (via `/chore`, `/bug`, or `/feature` slash command):
  - Analyzes codebase and issue requirements
  - Creates detailed implementation plan with:
    - Technical approach and architecture decisions
    - Step-by-step implementation tasks
    - File modifications with specific line numbers
    - Validation commands (tests, builds, checks)
  - Saves plan to `specs/{issue-slug}-plan.md`
- **plan_finder**: Locates the generated plan file in specs/ directory

### 4. Implementation Stage
**Agent:** `sdlc_implementor` (via `/implement` slash command)
- Reads the implementation plan from specs/
- Executes each step systematically:
  - Reads relevant files and analyzes code structure
  - Makes precise code changes using Edit/Write tools
  - Runs tests and validation commands
  - Fixes any errors or test failures
- Ensures all validation commands pass before completion
- Posts progress updates to GitHub issue

### 5. Integration Stage
**Agents:** `branch_generator` + `pr_creator`
- **branch_generator**: Creates semantic branch name
  - Format: `{type}-{issue_number}-{adw_id}-{slug}`
  - Example: `feat-456-e5f6g7h8-add-user-authentication`
- **pr_creator** (via `/pull_request` slash command):
  - Generates PR title and summary from commits
  - Creates commit with ADW ID tracking
  - Opens pull request linked to original issue
  - Posts PR URL to GitHub issue

### ADW ID Tracking System
Every workflow run gets a unique 8-character identifier (e.g., `a1b2c3d4`) that enables complete traceability:
- **GitHub Comments**: `a1b2c3d4_ops: ✅ Classification complete: /feature`
- **Log Files**: `agents/a1b2c3d4/adw_plan_build/execution.log`
- **Branch Names**: `feat-123-a1b2c3d4-new-feature`
- **Commits**: `feat: implement new feature\n\nGenerated with ADW ID: a1b2c3d4`
- **Agent Outputs**: `agents/a1b2c3d4/sdlc_planner/raw_output.jsonl`

## ADW Environment Setup

### Required Environment Variables
```bash
# Required - Anthropic API key for Claude Code CLI
export ANTHROPIC_API_KEY="sk-ant-xxxxx..."

# Optional - Path to claude binary (defaults to "claude")
export CLAUDE_CODE_PATH="/path/to/claude"

# Optional - Only needed if using different GitHub account than gh CLI
export GITHUB_PAT="ghp_xxxxx..."
```

### Optional Environment Variables
```bash
# For sandbox execution environments
export E2B_API_KEY="e2b_xxxxx..."

# For webhook tunnel setup (cloudflared)
export CLOUDFLARED_TUNNEL_TOKEN="xxxxx..."
```

### Installation Steps

**1. Install GitHub CLI**
```bash
# macOS
brew install gh

# Ubuntu/Debian
sudo apt install gh

# Windows
winget install --id GitHub.cli
```

**2. Install Claude Code CLI**
- Download and install from: https://docs.anthropic.com/en/docs/claude-code
- Verify installation: `claude --version`

**3. Install Python uv (dependency manager)**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**4. Authenticate with GitHub**
```bash
gh auth login
# Follow prompts to authenticate
```

**5. Set up Environment Variables**
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export ANTHROPIC_API_KEY="your-key-here"

# Or use a .env file in project root
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

**6. Verify Installation**
```bash
uv run adws/health_check.py
# Should report all checks passing
```

For detailed setup instructions and troubleshooting, see [adws/README.md](adws/README.md).

## ADW Usage

ADW can operate in three modes depending on your workflow needs:

### 1. Manual Mode - Process Specific Issues
Process a single GitHub issue on demand:
```bash
uv run adws/adw_plan_build.py 123
```

**Use case:** Direct control over which issues to process, useful for testing or handling high-priority issues immediately.

**Example workflow:**
```bash
# User reports bug in issue #789
uv run adws/adw_plan_build.py 789
# ADW classifies as /bug, creates fix plan, implements, and opens PR
```

### 2. Cron Mode - Continuous Monitoring
Automatically process new issues and "adw" triggers:
```bash
uv run adws/trigger_cron.py
```

**Use case:** Continuous integration where ADW monitors for new work every 20 seconds.

**Processing triggers:**
- New issues with no comments are processed automatically
- Any issue where the latest comment is "adw" will be processed

**Example deployment with systemd:**
```ini
# /etc/systemd/system/adw-cron.service
[Unit]
Description=ADW Cron Trigger
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/tac-4
Environment="ANTHROPIC_API_KEY=your-key"
ExecStart=/home/your-user/.local/bin/uv run adws/trigger_cron.py
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable adw-cron
sudo systemctl start adw-cron
```

### 3. Webhook Mode - Real-Time Event Processing
Receive instant GitHub webhooks for immediate processing:
```bash
uv run adws/trigger_webhook.py
# Server starts on http://localhost:8001
```

**Use case:** Production environments requiring instant response to GitHub events.

**Endpoints:**
- `POST /gh-webhook` - Receives GitHub webhook events
- `GET /health` - Health check for monitoring

**GitHub Webhook Configuration:**
1. Go to your repository Settings → Webhooks → Add webhook
2. Set Payload URL: `https://your-server.com/gh-webhook`
3. Content type: `application/json`
4. Select events: `Issues` and `Issue comments`
5. Save webhook

**Cloudflare Tunnel Setup (for local development):**
```bash
export CLOUDFLARED_TUNNEL_TOKEN="your-token"
cloudflared tunnel --url http://localhost:8001
# Use the generated URL in GitHub webhook settings
```

## Common ADW Scenarios

**Scenario 1: Process bug report immediately**
```bash
# Bug reported in issue #456
uv run adws/adw_plan_build.py 456
# Review the PR when complete
```

**Scenario 2: Enable automatic processing**
```bash
# Start monitoring service
uv run adws/trigger_cron.py &
# All new issues are now processed automatically
```

**Scenario 3: Re-trigger processing with comment**
```bash
# Navigate to GitHub issue
# Add comment: "adw"
# ADW will detect and reprocess the issue
```

**Scenario 4: Deploy webhook server for production**
```bash
# Set up environment
export ANTHROPIC_API_KEY="your-key"
# Start webhook server
uv run adws/trigger_webhook.py
# Configure GitHub webhook to point to your server
```

## ADW Logging & Debugging

ADW generates comprehensive structured logs for every workflow run, enabling complete debugging and traceability.

### Output Directory Structure
```
agents/
├── {adw_id}/                          # e.g., a1b2c3d4
│   ├── adw_plan_build/
│   │   └── execution.log              # Main workflow execution log
│   ├── issue_classifier/
│   │   ├── raw_output.jsonl           # Claude Code output stream
│   │   ├── raw_output.json            # Parsed JSON array
│   │   └── prompts/
│   │       └── classify_issue.txt     # Prompt sent to agent
│   ├── sdlc_planner/
│   │   ├── raw_output.jsonl
│   │   ├── raw_output.json
│   │   └── prompts/
│   │       └── chore.txt              # /chore, /bug, or /feature
│   ├── plan_finder/
│   │   └── raw_output.jsonl
│   ├── sdlc_implementor/
│   │   ├── raw_output.jsonl
│   │   ├── raw_output.json
│   │   └── prompts/
│   │       └── implement.txt
│   ├── branch_generator/
│   │   └── raw_output.jsonl
│   └── pr_creator/
│       ├── raw_output.jsonl
│       └── prompts/
│           └── pull_request.txt
```

### Log Levels
- **Console Output**: INFO and above (shows workflow progress)
- **File Logs**: DEBUG and above (captures everything for deep debugging)

### Finding Logs for a Specific Run
1. **From GitHub Issue**: Look for ADW ID in issue comments (e.g., `a1b2c3d4_ops: ✅ Starting...`)
2. **Navigate to Logs**: `agents/a1b2c3d4/adw_plan_build/execution.log`
3. **View Agent Outputs**: Check individual agent directories for detailed outputs

### Debugging Workflow Failures

**Check main execution log:**
```bash
# Find your ADW ID from GitHub issue comment
cat agents/a1b2c3d4/adw_plan_build/execution.log
```

**Inspect agent output:**
```bash
# View raw JSONL stream
cat agents/a1b2c3d4/sdlc_planner/raw_output.jsonl

# View parsed JSON (easier to read)
cat agents/a1b2c3d4/sdlc_planner/raw_output.json | jq .

# View the exact prompt sent to agent
cat agents/a1b2c3d4/sdlc_planner/prompts/chore.txt
```

**Check for specific errors:**
```bash
# Search for errors across all logs
grep -r "ERROR" agents/a1b2c3d4/

# Find failed validation commands
grep -r "FAILED" agents/a1b2c3d4/
```

### Running Health Checks
Validate your ADW system configuration before running workflows:
```bash
uv run adws/health_check.py

# Expected output:
# ✅ Environment variables configured
# ✅ Git repository valid
# ✅ Claude Code CLI functional
# ✅ GitHub CLI authenticated
```

To post health check results to a GitHub issue:
```bash
uv run adws/health_check.py --issue 123
# Results will be posted as a comment on issue #123
```

### Common Debug Scenarios

**Agent execution failed:**
```bash
# Check the agent's raw output for error messages
cat agents/{adw_id}/sdlc_implementor/raw_output.jsonl | tail -20
```

**Plan file not found:**
```bash
# Check if plan was generated
ls -la specs/
# View plan_finder output
cat agents/{adw_id}/plan_finder/raw_output.jsonl
```

**Tests failing during implementation:**
```bash
# Review implementor logs for test output
grep -A 10 "pytest" agents/{adw_id}/sdlc_implementor/raw_output.jsonl
```

## ADW Configuration

### Slash Commands
ADW uses Claude Code's slash command system to interface with the codebase. Commands are defined in `.claude/commands/`:

**Available Commands:**
- `/classify_issue` - Analyzes GitHub issue and determines type
- `/chore` - Creates implementation plan for maintenance tasks
- `/bug` - Creates implementation plan for bug fixes
- `/feature` - Creates implementation plan for new features
- `/implement <plan-file>` - Executes implementation plan
- `/pull_request` - Creates PR from current changes

### Model Selection
Edit `adws/agent.py:129` to change the Claude model:
```python
# Default: Fast and cost-effective
model="sonnet"

# Alternative: More capable for complex tasks
model="opus"
```

### Branch Naming Convention
ADW generates semantic branch names following this pattern:
```
{type}-{issue_number}-{adw_id}-{slug}
```

**Examples:**
- `feat-456-e5f6g7h8-add-user-authentication`
- `bug-789-a1b2c3d4-fix-login-error`
- `chore-123-f9e8d7c6-update-documentation`

**Components:**
- `type`: feat/bug/chore (from classification)
- `issue_number`: GitHub issue number
- `adw_id`: Unique 8-character workflow identifier
- `slug`: Kebab-case issue title summary

### Commit Message Format
ADW commits include tracking information:
```
{type}: {description}

Implements #{issue_number}

Generated with ADW ID: {adw_id}
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Extending ADW with Custom Agents

**1. Create a new slash command:**
```bash
# Create command file
mkdir -p .claude/commands
cat > .claude/commands/my_custom_agent.md << 'EOF'
---
name: my_custom_agent
description: Custom agent for specialized tasks
---

# Instructions for the agent
Your custom prompt and instructions here.
EOF
```

**2. Add agent invocation in adw_plan_build.py:**
```python
from adws.agent import run_prompt

# Execute custom agent
result = run_prompt(
    agent_name="my_custom_agent",
    command="/my_custom_agent",
    adw_id=adw_id,
    cwd=os.getcwd()
)
```

**3. Parse and use agent output:**
```python
import json
output_file = f"agents/{adw_id}/my_custom_agent/raw_output.json"
with open(output_file) as f:
    data = json.load(f)
    # Process agent response
```

### Customizing Workflow Behavior

**Modify polling interval (trigger_cron.py):**
```python
# Change from 20 seconds to 60 seconds
await asyncio.sleep(60)  # Line 156
```

**Adjust webhook port (trigger_webhook.py):**
```bash
PORT=3000 uv run adws/trigger_webhook.py
```

**Customize issue classification criteria:**
Edit `.claude/commands/classify_issue.md` to adjust how issues are categorized.

## ADW Security & Best Practices

### Security Considerations

**API Token Management:**
- Store `ANTHROPIC_API_KEY` and `GITHUB_PAT` as environment variables, never in code
- Use `.env` files for local development (ensure `.env` is in `.gitignore`)
- Use secure secret management for production (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate API keys regularly

**GitHub Token Permissions:**
- Use fine-grained personal access tokens with minimal required scopes:
  - `repo` - Full control (for creating branches and PRs)
  - `issues` - Read/write (for commenting and status updates)
- Avoid using classic tokens with full account access
- Create separate tokens for different environments (dev/staging/prod)

**Repository Security:**
- Enable branch protection rules for main/master branches
- Require pull request reviews before merging ADW-generated code
- Enable status checks (tests must pass before merge)
- Restrict who can approve and merge ADW PRs
- Consider requiring signed commits

**Code Review Requirements:**
- **Always review ADW-generated code** before merging
- Verify that implementations match the approved plan
- Check for security vulnerabilities or unintended changes
- Test functionality in a staging environment first
- Review all file changes, not just the summary

### Operational Best Practices

**Before Deployment:**
- Run health check to validate configuration: `uv run adws/health_check.py`
- Test with low-priority issues first to verify system behavior
- Set up monitoring and alerting for ADW processes
- Document your ADW deployment and configuration

**Monitoring & Alerts:**
- Monitor API usage and costs (Anthropic + GitHub)
- Set up billing alerts for API usage thresholds
- Track ADW success/failure rates via logs
- Monitor webhook delivery and response times
- Alert on repeated failures or errors

**Rate Limiting:**
- GitHub API: 5000 requests/hour (authenticated)
- Anthropic API: Varies by plan tier
- Implement exponential backoff for retries (already in adw_plan_build.py)
- Space out cron polling intervals if hitting rate limits
- Consider using webhook mode for production (more efficient)

**Workflow Management:**
- Review generated plans in `specs/` before implementation runs
- Use manual mode for critical or high-risk changes
- Keep Claude Code CLI updated to latest version
- Maintain a changelog of ADW system changes
- Backup agent outputs and logs periodically

**Testing & Validation:**
- Validate all ADW changes pass tests before merging
- Use test issues to verify ADW configuration changes
- Test webhook endpoints with GitHub's webhook testing feature
- Run health checks after any configuration changes
- Validate branch protection rules are enforced

**Incident Response:**
- Know how to quickly disable ADW (stop cron/webhook services)
- Have rollback procedures for problematic ADW changes
- Keep agent outputs for forensic analysis
- Document common failure modes and resolutions
- Establish clear escalation paths for ADW issues

## ADW Troubleshooting

### Common Issues and Solutions

**"Claude Code CLI not found"**
```bash
# Check if Claude Code is installed
which claude

# If not found, install from:
# https://docs.anthropic.com/en/docs/claude-code

# Or set custom path
export CLAUDE_CODE_PATH="/path/to/claude"
```

**"Missing ANTHROPIC_API_KEY"**
```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# Set in environment
export ANTHROPIC_API_KEY="sk-ant-xxxxx..."

# Or add to .env file in project root
echo "ANTHROPIC_API_KEY=sk-ant-xxxxx..." >> .env
```

**"GitHub CLI not authenticated"**
```bash
# Check authentication status
gh auth status

# If not authenticated, log in
gh auth login

# Or set GITHUB_PAT (optional)
export GITHUB_PAT=$(gh auth token)
```

**"Agent execution failed"**
```bash
# Find your ADW ID from GitHub issue comment
# Check the agent's output for error details
cat agents/{adw_id}/{agent_name}/raw_output.jsonl | tail -20

# Check main execution log
cat agents/{adw_id}/adw_plan_build/execution.log

# Look for specific error patterns
grep -i "error" agents/{adw_id}/*/raw_output.jsonl
```

**"Webhook not triggering"**
```bash
# 1. Verify webhook server is running
curl http://localhost:8001/health
# Should return: {"status": "healthy"}

# 2. Check GitHub webhook configuration
# Go to: Settings → Webhooks → Recent Deliveries
# Look for failed deliveries and error messages

# 3. Verify tunnel is active (if using cloudflared)
ps aux | grep cloudflared

# 4. Test webhook locally
curl -X POST http://localhost:8001/gh-webhook \
  -H "Content-Type: application/json" \
  -d '{"action":"opened","issue":{"number":123}}'
```

**"Rate limit exceeded"**
```bash
# Check GitHub API rate limit
gh api rate_limit

# Solutions:
# - Use webhook mode instead of cron (more efficient)
# - Increase polling interval in trigger_cron.py
# - Wait for rate limit reset (shown in gh api output)
```

**"Tests failing during implementation"**
```bash
# Check which tests failed
grep -A 20 "FAILED" agents/{adw_id}/sdlc_implementor/raw_output.jsonl

# Review the implementation plan
cat specs/{plan-file}.md

# Manually run tests to debug
cd app/server && uv run pytest -v
```

**"Plan file not found"**
```bash
# Check if plan was generated
ls -la specs/ | grep -i {issue-title-keywords}

# View plan_finder output
cat agents/{adw_id}/plan_finder/raw_output.jsonl

# Check planner output for errors
cat agents/{adw_id}/sdlc_planner/raw_output.jsonl | tail -50
```

**"Branch already exists"**
```bash
# List existing branches
git branch -a | grep {issue_number}

# Delete old branch if safe to do so
git branch -D {branch-name}
git push origin --delete {branch-name}

# Or use a different issue to test
```

### Diagnostic Commands

**Run comprehensive health check:**
```bash
uv run adws/health_check.py
# Validates environment, git, Claude CLI, and GitHub auth
```

**Check ADW system status:**
```bash
# List all ADW runs
ls -la agents/

# Count successful vs failed runs
grep -r "ERROR" agents/*/adw_plan_build/execution.log | wc -l
grep -r "SUCCESS" agents/*/adw_plan_build/execution.log | wc -l

# Check recent activity
ls -lt agents/ | head -10
```

**Verify API connectivity:**
```bash
# Test GitHub CLI
gh api user

# Test Claude Code CLI
claude --version

# Check repository access
gh repo view
```

### Getting Help

If issues persist after troubleshooting:

1. **Check logs thoroughly**: All agent outputs are in `agents/{adw_id}/`
2. **Review detailed docs**: See [adws/README.md](adws/README.md) for in-depth troubleshooting
3. **Run health check**: `uv run adws/health_check.py` for diagnostic info
4. **Verify configuration**: Ensure all environment variables are set correctly
5. **Test with simple issue**: Create a minimal test issue to isolate the problem

## API Endpoints

- `POST /api/upload` - Upload CSV/JSON file
- `POST /api/query` - Process natural language query
- `GET /api/schema` - Get database schema
- `POST /api/insights` - Generate column insights
- `GET /api/health` - Health check

## Security

### SQL Injection Protection

The application implements comprehensive SQL injection protection through multiple layers:

1. **Centralized Security Module** (`core/sql_security.py`):
   - Identifier validation for table and column names
   - Safe query execution with parameterized queries
   - Proper escaping for identifiers using SQLite's square bracket notation
   - Dangerous operation detection and blocking

2. **Input Validation**:
   - All table and column names are validated against a whitelist pattern
   - SQL keywords cannot be used as identifiers
   - File names are sanitized before creating tables
   - User queries are validated for dangerous operations

3. **Query Execution Safety**:
   - Parameterized queries used wherever possible
   - Identifiers (table/column names) are properly escaped
   - Multiple statement execution is blocked
   - SQL comments are not allowed in queries

4. **Protected Operations**:
   - File uploads with malicious names are sanitized
   - Natural language queries cannot inject SQL
   - Table deletion uses validated identifiers
   - Data insights generation validates all inputs

### Security Best Practices for Development

When adding new SQL functionality:
1. Always use the `sql_security` module functions
2. Never concatenate user input directly into SQL strings
3. Use `execute_query_safely()` for all database operations
4. Validate all identifiers with `validate_identifier()`
5. For DDL operations, use `allow_ddl=True` explicitly

### Testing Security

Run the comprehensive security tests:
```bash
cd app/server
uv run pytest tests/test_sql_injection.py -v
```


### Additional Security Features

- CORS configured for local development only
- File upload validation (CSV and JSON only)
- Comprehensive error logging without exposing sensitive data
- Database operations are isolated with proper connection handling

## Troubleshooting

**Backend won't start:**
- Check Python version: `python --version` (requires 3.12+)
- Verify API keys are set: `echo $OPENAI_API_KEY`

**Frontend errors:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (requires 18+)

**CORS issues:**
- Ensure backend is running on port 8000
- Check vite.config.ts proxy settings