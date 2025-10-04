# Chore: Document the ADW Directory

## Chore Description
Create comprehensive documentation for the ADW (AI Developer Workflow) system in the README.md file. The ADW directory (`adws/`) contains a sophisticated automated development workflow system that integrates GitHub issues with Claude Code CLI to classify issues, generate plans, implement solutions, and create pull requests. The documentation needs to explain the architecture, components, workflow, and how developers can use and extend the system.

## Relevant Files
Use these files to resolve the chore:

### Existing Files
- **README.md** - Project root README that needs to be updated with ADW documentation
  - Currently has minimal ADW section with basic script listing
  - Needs comprehensive architecture, workflow, and usage documentation
  - Should explain how ADW integrates with the rest of the application

- **adws/README.md** - Detailed ADW system documentation
  - Contains quick start guide, script usage, workflow explanation
  - Environment setup instructions
  - Common usage scenarios and troubleshooting
  - This content should be referenced/summarized in the main README

- **adws/adw_plan_build.py** - Main orchestration script (535 lines)
  - Coordinates the entire workflow from issue classification to PR creation
  - Uses multiple specialized agents (classifier, planner, implementor, branch generator, PR creator)
  - Handles error checking and GitHub issue commenting throughout the process

- **adws/agent.py** - Claude Code CLI integration (263 lines)
  - Executes prompts programmatically via Claude Code CLI
  - Manages environment variables and authentication
  - Handles JSONL output parsing and conversion to JSON
  - Saves prompts and manages output directories

- **adws/data_types.py** - Pydantic models (144 lines)
  - Defines GitHub API response models (GitHubIssue, GitHubUser, GitHubComment, etc.)
  - Agent request/response models (AgentPromptRequest, AgentPromptResponse)
  - Slash command type definitions
  - Ensures type safety throughout the system

- **adws/github.py** - GitHub operations (281 lines)
  - Fetches issues and comments using GitHub CLI
  - Posts comments and manages issue status
  - Handles repository URL extraction from git remote
  - Manages GitHub authentication via GITHUB_PAT or gh CLI

- **adws/utils.py** - Utility functions (79 lines)
  - Generates unique ADW IDs for workflow tracking
  - Sets up structured logging to both console and file
  - Creates organized log directory structure

- **adws/health_check.py** - System health validation (397 lines)
  - Validates environment variables
  - Checks git repository configuration
  - Tests Claude Code CLI functionality
  - Verifies GitHub CLI authentication
  - Can post health check results to GitHub issues

- **adws/trigger_webhook.py** - FastAPI webhook server (207 lines)
  - Receives GitHub webhook events (issues opened, comments with "adw")
  - Launches adw_plan_build.py in background
  - Provides health check endpoint
  - Responds within GitHub's 10-second timeout requirement

- **adws/trigger_cron.py** - Polling-based trigger (224 lines)
  - Polls GitHub every 20 seconds for new issues
  - Detects issues with no comments or latest comment "adw"
  - Tracks processed issues to avoid duplicates
  - Handles graceful shutdown on SIGINT/SIGTERM

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create ADW Architecture Section
- Add a new "## ADW Architecture" section to README.md after the "## ADWs" section
- Explain the high-level architecture:
  - ADW is an automated software development system that monitors GitHub issues
  - Uses Claude Code CLI to execute specialized agents for different workflow stages
  - Integrates with GitHub via gh CLI and webhooks/polling
  - Produces structured logs and outputs for debugging and tracking
- Include a workflow diagram explanation (text-based):
  1. Trigger Detection (webhook/cron/manual)
  2. Issue Classification (determines /chore, /bug, or /feature)
  3. Plan Generation (creates implementation plan in specs/)
  4. Implementation (executes the plan with code changes)
  5. PR Creation (commits changes and creates pull request)

### Step 2: Document Core Components
- Add a new "## ADW Core Components" section to README.md
- Document each Python module with its purpose:
  - **adw_plan_build.py** - Main workflow orchestrator that coordinates all agents
  - **agent.py** - Claude Code CLI integration layer for executing AI agents
  - **data_types.py** - Type-safe models for GitHub API and agent communication
  - **github.py** - GitHub operations via gh CLI (issues, comments, authentication)
  - **utils.py** - Logging and ID generation utilities
  - **health_check.py** - System validation and diagnostics
  - **trigger_webhook.py** - FastAPI server for real-time GitHub events
  - **trigger_cron.py** - Polling-based issue monitoring
- For each component, include:
  - Purpose and responsibility
  - Key functions/classes
  - Dependencies and integrations

### Step 3: Add ADW Workflow Details
- Add a new "## ADW Workflow Details" section to README.md
- Explain each workflow stage in detail:
  - **Trigger Stage**: How issues are detected (webhook vs cron vs manual)
  - **Classification Stage**: Issue type determination using the classifier agent
  - **Planning Stage**: Plan generation using the planner agent, saved to specs/
  - **Implementation Stage**: Code changes using the implementor agent
  - **Integration Stage**: Branch creation, commits, and PR creation
- Document the specialized agents used:
  - issue_classifier - Analyzes issue and determines type
  - sdlc_planner - Creates implementation plan
  - plan_finder - Locates generated plan file
  - sdlc_implementor - Executes the implementation
  - branch_generator - Creates semantic branch names
  - pr_creator - Generates and creates pull requests
- Explain ADW ID tracking system (8-char UUID that appears in comments, logs, branches)

### Step 4: Document Environment Setup
- Add a new "## ADW Environment Setup" section to README.md
- Document required environment variables:
  - ANTHROPIC_API_KEY (required) - For Claude Code CLI
  - CLAUDE_CODE_PATH (optional) - Path to claude binary, defaults to "claude"
  - GITHUB_PAT (optional) - Only needed if using different account than gh CLI
- Document optional environment variables:
  - E2B_API_KEY - For sandbox environments
  - CLOUDFLARED_TUNNEL_TOKEN - For webhook tunnel setup
- Add installation steps:
  - GitHub CLI: `brew install gh` (or platform equivalent)
  - Claude Code CLI: Link to https://docs.anthropic.com/en/docs/claude-code
  - Python uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Authenticate: `gh auth login`
- Reference the adws/README.md for detailed setup instructions

### Step 5: Add Usage Examples
- Add a new "## ADW Usage" section to README.md
- Document three usage modes:
  1. **Manual Mode**: `uv run adws/adw_plan_build.py <issue-number>`
     - Use case: Process a specific issue on demand
     - Example: `uv run adws/adw_plan_build.py 123`
  2. **Cron Mode**: `uv run adws/trigger_cron.py`
     - Use case: Continuous monitoring, polls every 20 seconds
     - Processes new issues and issues with "adw" comment
     - Example for systemd deployment
  3. **Webhook Mode**: `uv run adws/trigger_webhook.py`
     - Use case: Real-time event processing
     - Requires webhook configuration in GitHub repo settings
     - Endpoints: POST /gh-webhook, GET /health
- Include common scenarios:
  - Process a bug report immediately
  - Enable automatic processing for new issues
  - Trigger processing by commenting "adw" on an issue
  - Deploy webhook server for instant response

### Step 6: Document Logging and Debugging
- Add a new "## ADW Logging & Debugging" section to README.md
- Explain the output structure:
  ```
  agents/
  ├── {adw_id}/
  │   ├── {agent_name}/
  │   │   ├── raw_output.jsonl - Claude Code output stream
  │   │   ├── raw_output.json - Parsed JSON array
  │   │   └── prompts/
  │   │       └── {command}.txt - Prompt used
  │   └── adw_plan_build/
  │       └── execution.log - Structured workflow log
  ```
- Document how to:
  - Find logs for a specific ADW run (use the adw_id from issue comments)
  - Inspect agent outputs and prompts
  - Debug failures using execution.log
  - Run health checks: `uv run adws/health_check.py`
- Explain log levels:
  - Console: INFO and above
  - File: DEBUG and above (captures everything)

### Step 7: Add Configuration and Customization
- Add a new "## ADW Configuration" section to README.md
- Document customization options:
  - Model selection in agent.py (sonnet vs opus)
  - Custom slash commands in .claude/commands/
  - Branch naming convention: {type}-{issue_number}-{adw_id}-{slug}
  - Commit message format with ADW tracking
- Explain the slash command system:
  - /chore - Maintenance, documentation, refactoring
  - /bug - Bug fixes and corrections
  - /feature - New features and enhancements
  - /classify_issue - Analyzes issue type
  - /implement - Executes implementation plan
  - /pull_request - Creates PR with summary
- Document how to extend with new agents and commands

### Step 8: Add Security and Best Practices
- Add a new "## ADW Security & Best Practices" section to README.md
- Document security considerations:
  - Store tokens as environment variables, never in code
  - Use GitHub fine-grained tokens with minimal permissions
  - Set up branch protection rules for ADW-created branches
  - Require PR reviews for ADW changes
  - Monitor API usage and set billing alerts (Anthropic + GitHub)
- Add operational best practices:
  - Review ADW-generated plans before implementation
  - Test webhook endpoints with GitHub's webhook testing feature
  - Use health checks to validate system before deploying
  - Monitor logs for errors and rate limit issues
  - Keep Claude Code CLI updated

### Step 9: Update Existing ADWs Section
- Update the existing "## ADWs" section in README.md
- Add context that these are entry point scripts
- Group scripts by purpose:
  - **Health & Diagnostics**: health_check.py
  - **Triggers**: trigger_webhook.py, trigger_cron.py
  - **Workflow**: adw_plan_build.py
- Add links to the new detailed sections
- Keep the existing uv run commands

### Step 10: Add Troubleshooting Section
- Add a new "## ADW Troubleshooting" section to README.md
- Document common issues and solutions:
  - "Claude Code CLI not found" → Set CLAUDE_CODE_PATH or install Claude Code
  - "Missing ANTHROPIC_API_KEY" → Set in .env file or environment
  - "GitHub CLI not authenticated" → Run `gh auth login` or set GITHUB_PAT
  - "Agent execution failed" → Check logs in agents/{adw_id}/
  - "Webhook not triggering" → Verify webhook configuration and tunnel
  - "Rate limit exceeded" → Check API quotas and add delays
- Add reference to health check script for diagnostics
- Include link to adws/README.md for detailed troubleshooting

## Validation Commands
Execute every command to validate the chore is complete with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate no regressions in the main application
- `uv run adws/health_check.py` - Validate ADW system health and configuration
- `git diff README.md` - Review the documentation changes for accuracy and completeness

## Notes
- The ADW system is a sophisticated meta-programming tool - the documentation should emphasize that it's an AI system that writes code via AI agents
- The architecture is event-driven and asynchronous (webhooks) or polling-based (cron)
- Each workflow run is uniquely identified by an 8-character ADW ID that appears in GitHub comments, logs, branches, and commits
- The system uses Claude Code CLI slash commands defined in .claude/commands/ - these are the interface between ADW and the codebase
- All agent interactions are logged in structured JSONL format for debugging and analysis
- The documentation should help users understand both how to use the system and how to extend it with new agents and commands
- Keep the README.md concise - detailed information is in adws/README.md, link to it for deep dives
