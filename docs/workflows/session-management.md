# Advanced Session Management Guide

## Overview

Effective session management in Claude Code enables teams to maintain context across long-running tasks, coordinate multiple agents, and automate complex workflows. This guide covers advanced patterns for session management and automation.

## Session Lifecycle

### Session States

```
┌──────────┐    start     ┌────────┐    work      ┌────────────┐
│          │─────────────►│        │─────────────►│            │
│   New    │              │ Active │              │  Working   │
│          │◄─────────────│        │◄─────────────│            │
└──────────┘   cancel     └────────┘   idle       └────────────┘
                               │                        │
                               │ pause                  │ complete
                               ▼                        ▼
                          ┌────────┐              ┌──────────┐
                          │        │              │          │
                          │ Paused │              │ Complete │
                          │        │              │          │
                          └────────┘              └──────────┘
                               │                        │
                               │ resume                 │ archive
                               ▼                        ▼
                          ┌────────┐              ┌──────────┐
                          │        │              │          │
                          │ Active │              │ Archived │
                          │        │              │          │
                          └────────┘              └──────────┘
```

### Session Context

Sessions maintain:
1. **Conversation History**: All messages exchanged
2. **File Context**: Files read and modified
3. **Tool Usage**: MCP tools invoked
4. **State Variables**: Custom state data
5. **Background Tasks**: Running operations

## Session Resumption Strategies

### Strategy 1: Checkpoint-Based Resumption

Save checkpoints at key milestones:

```markdown
# Session Checkpoint: Feature Development

## Context
Working on: User authentication feature
Branch: feature/user-auth
Last completed: Implemented login endpoint

## Files Modified
- src/auth/login.ts (new)
- src/auth/types.ts (modified)
- tests/auth/login.test.ts (new)

## Next Steps
1. Implement logout endpoint
2. Add session management
3. Write integration tests

## Important Notes
- Using bcrypt for password hashing
- JWT tokens expire in 24 hours
- Need to add rate limiting

## Commands to Resume
```bash
cd /path/to/project
git checkout feature/user-auth
npm test
```
```

**Usage**:
```
Resume from checkpoint: Feature Development
```

**Implementation**:

Create a checkpoint system:

```bash
# .claude/checkpoint.sh
#!/bin/bash

CHECKPOINT_DIR=".claude/checkpoints"
mkdir -p "$CHECKPOINT_DIR"

save_checkpoint() {
    local name=$1
    local checkpoint_file="$CHECKPOINT_DIR/${name}.md"

    cat > "$checkpoint_file" <<EOF
# Checkpoint: $name
Generated: $(date)

## Git State
Branch: $(git branch --show-current)
Commit: $(git rev-parse HEAD)
Status:
$(git status --short)

## Working Files
$(git diff --name-only)

## Context
$(cat .claude/context.md 2>/dev/null || echo "No context file")

## Environment
PWD: $(pwd)
Node Version: $(node --version 2>/dev/null || echo "N/A")
Python Version: $(python --version 2>/dev/null || echo "N/A")
EOF

    echo "Checkpoint saved: $checkpoint_file"
}

list_checkpoints() {
    ls -1 "$CHECKPOINT_DIR"/*.md 2>/dev/null || echo "No checkpoints found"
}

load_checkpoint() {
    local name=$1
    cat "$CHECKPOINT_DIR/${name}.md"
}

# Usage
case "$1" in
    save)
        save_checkpoint "$2"
        ;;
    list)
        list_checkpoints
        ;;
    load)
        load_checkpoint "$2"
        ;;
    *)
        echo "Usage: checkpoint.sh {save|list|load} [name]"
        ;;
esac
```

### Strategy 2: Context Files

Maintain a `.claude/context.md` file:

```markdown
# Project Context

## Current Work
Feature: Payment Processing
Status: In Progress (70% complete)
Branch: feature/payment-processing

## Architecture
- Using Stripe API
- Webhook handling in src/webhooks/stripe.ts
- Payment models in src/models/payment.ts

## Recent Decisions
- Decided to use Stripe instead of PayPal (2024-01-15)
- Implementing webhook retries with exponential backoff
- Storing payment history in PostgreSQL

## Known Issues
- [ ] Webhook signature verification failing in dev
- [ ] Need to add idempotency keys
- [x] Fixed decimal precision issue

## Dependencies
- stripe npm package v11.x
- PostgreSQL 14+
- Redis for webhook deduplication

## Testing Notes
- Use Stripe test mode keys
- Webhook testing via Stripe CLI
- Test cards in tests/fixtures/cards.ts

## Next Session
Continue with:
1. Implement refund logic
2. Add webhook retry mechanism
3. Write integration tests
```

**Auto-update hook**:

```bash
# hooks/update-context.sh
#!/bin/bash

CONTEXT_FILE=".claude/context.md"

update_context() {
    # Update git status
    sed -i '' "s/^Branch: .*/Branch: $(git branch --show-current)/" "$CONTEXT_FILE"

    # Update timestamp
    echo "Last updated: $(date)" >> "$CONTEXT_FILE"
}

# Run on git operations
update_context
```

### Strategy 3: Session Snapshots

Take full snapshots of session state:

```typescript
// .claude/snapshot.ts
interface SessionSnapshot {
  timestamp: string;
  branch: string;
  files: {
    path: string;
    hash: string;
    status: 'added' | 'modified' | 'deleted';
  }[];
  context: string;
  todos: string[];
  notes: string;
}

async function saveSnapshot(name: string): Promise<void> {
  const snapshot: SessionSnapshot = {
    timestamp: new Date().toISOString(),
    branch: await getCurrentBranch(),
    files: await getChangedFiles(),
    context: await readFile('.claude/context.md'),
    todos: await getTodos(),
    notes: '',
  };

  await writeFile(
    `.claude/snapshots/${name}.json`,
    JSON.stringify(snapshot, null, 2)
  );
}

async function loadSnapshot(name: string): Promise<SessionSnapshot> {
  const content = await readFile(`.claude/snapshots/${name}.json`);
  return JSON.parse(content);
}
```

## Context Management

### Context Compression

For long sessions, compress context to stay within limits:

**Automatic Summarization**:

```
Summarize the last 2 hours of work:

1. Read conversation history
2. Extract key points:
   - Files created/modified
   - Important decisions made
   - Issues encountered and resolved
   - Current state
3. Create compressed summary
4. Save as session-summary.md
5. Clear old messages
```

**Progressive Summarization**:

```
# Session Summary Layers

## Layer 1: Full History (0-1 hour old)
[Keep all messages]

## Layer 2: Detailed Summary (1-4 hours old)
### What was done
- Implemented user login
- Fixed authentication bug
- Added tests

### Key decisions
- Using JWT for tokens
- 24-hour expiration

### Current state
Login endpoint complete, working on logout

## Layer 3: Brief Summary (4+ hours old)
Implemented authentication system with JWT tokens

## Layer 4: Archived (completed sessions)
Session 2024-01-15: Authentication feature completed
```

### Context Partitioning

Split large projects into context partitions:

```
Project Partitions:

1. Frontend (/src/frontend)
   - React components
   - UI state management
   - Styling

2. Backend (/src/backend)
   - API routes
   - Business logic
   - Database models

3. Infrastructure (/infrastructure)
   - Deployment configs
   - CI/CD pipelines
   - Monitoring

4. Testing (/tests)
   - Unit tests
   - Integration tests
   - E2E tests

Working on partition: Backend
Load context: backend-context.md
```

### Context Injection

Inject relevant context at session start:

```bash
# hooks/session-start.sh
#!/bin/bash

echo "Loading project context..."

# Inject README
echo "=== Project README ==="
cat README.md

# Inject current context
echo "=== Current Work Context ==="
cat .claude/context.md

# Inject recent changes
echo "=== Recent Changes ==="
git log --oneline -10

# Inject current branch status
echo "=== Branch Status ==="
git status

# Inject relevant documentation
echo "=== Architecture Docs ==="
cat docs/ARCHITECTURE.md
```

Configure in `settings.json`:
```json
{
  "hooks": {
    "sessionStart": "./hooks/session-start.sh"
  }
}
```

## Background Task Patterns

### Pattern 1: Long-Running Analysis

```
Start background analysis of codebase:

1. Create analysis task:
   - Scan all source files
   - Identify code smells
   - Calculate complexity metrics
   - Find security issues

2. Run in background:
   - Update progress periodically
   - Save intermediate results
   - Handle interruptions gracefully

3. Notify on completion:
   - Generate report
   - Highlight critical issues
   - Provide recommendations
```

**Implementation**:

```typescript
// .claude/tasks/analysis.ts
import { BackgroundTask } from '@claude/tasks';

class CodeAnalysisTask extends BackgroundTask {
  async run() {
    const files = await this.getAllSourceFiles();
    const total = files.length;

    for (let i = 0; i < total; i++) {
      const file = files[i];

      // Check if task cancelled
      if (this.isCancelled()) {
        this.saveState({ processedFiles: i });
        return;
      }

      // Analyze file
      const issues = await this.analyzeFile(file);
      this.results.push({ file, issues });

      // Update progress
      this.updateProgress({
        current: i + 1,
        total,
        message: `Analyzing ${file}`,
      });
    }

    // Generate report
    await this.generateReport();
    this.complete();
  }

  async resume() {
    const state = await this.loadState();
    const files = await this.getAllSourceFiles();

    // Resume from where we left off
    for (let i = state.processedFiles; i < files.length; i++) {
      // Continue analysis...
    }
  }
}
```

### Pattern 2: Incremental Processing

Process large datasets incrementally:

```
Process all database tables:

1. Get list of all tables
2. For each table:
   - Process in chunks of 1000 rows
   - Save progress after each chunk
   - Handle errors gracefully
   - Resume from last checkpoint if interrupted

3. Generate summary report
```

### Pattern 3: Scheduled Tasks

Run tasks on a schedule:

```typescript
// .claude/tasks/scheduled.ts
import { ScheduledTask } from '@claude/tasks';

class DailyHealthCheck extends ScheduledTask {
  schedule = '0 9 * * *'; // Every day at 9 AM

  async run() {
    // Check application health
    const healthReport = {
      database: await this.checkDatabase(),
      api: await this.checkAPI(),
      dependencies: await this.checkDependencies(),
      tests: await this.runTests(),
    };

    // Save report
    await this.saveReport(healthReport);

    // Notify if issues found
    if (this.hasIssues(healthReport)) {
      await this.notify('Health check found issues');
    }
  }
}
```

## Multi-Agent Coordination

### Pattern 1: Specialized Agents

Coordinate multiple specialized agents:

```
Project: E-commerce Platform

Agents:
1. Frontend Agent
   - Focuses on React components
   - UI/UX implementation
   - Styling

2. Backend Agent
   - API development
   - Database design
   - Business logic

3. DevOps Agent
   - CI/CD setup
   - Deployment automation
   - Monitoring

4. QA Agent
   - Test writing
   - Bug investigation
   - Quality assurance

Coordination:
- Shared context via .claude/shared-context.md
- Agent handoffs at integration points
- Regular sync meetings (automated)
```

**Handoff Protocol**:

```markdown
# Agent Handoff: Frontend → Backend

## From: Frontend Agent
Completed: User profile UI
Files: src/components/UserProfile.tsx

## Needs from Backend:
- GET /api/users/:id endpoint
- PUT /api/users/:id endpoint
- User model definition

## Acceptance Criteria:
- Returns user data in format: { id, name, email, avatar }
- Supports profile updates
- Proper error handling (404, 400, 500)

## To: Backend Agent
Please implement the required endpoints.
See API spec: docs/api-spec.md#user-endpoints
```

### Pattern 2: Pipeline Agents

Chain agents in a pipeline:

```
Development Pipeline:

1. Requirement Analysis Agent
   ↓ (produces: requirements.md)

2. Architecture Design Agent
   ↓ (produces: architecture.md, data-models.md)

3. Implementation Agent
   ↓ (produces: source code)

4. Testing Agent
   ↓ (produces: tests, test reports)

5. Documentation Agent
   ↓ (produces: API docs, user guides)

6. Deployment Agent
   ↓ (produces: deployed application)
```

**Pipeline Execution**:

```bash
# .claude/pipeline.sh
#!/bin/bash

run_pipeline() {
    echo "Starting development pipeline..."

    # Stage 1: Requirements
    claude-agent requirements analyze "$1" > requirements.md
    if [ $? -ne 0 ]; then
        echo "Requirements analysis failed"
        exit 1
    fi

    # Stage 2: Architecture
    claude-agent architecture design requirements.md > architecture.md
    if [ $? -ne 0 ]; then
        echo "Architecture design failed"
        exit 1
    fi

    # Stage 3: Implementation
    claude-agent implement architecture.md
    if [ $? -ne 0 ]; then
        echo "Implementation failed"
        exit 1
    fi

    # Stage 4: Testing
    claude-agent test
    if [ $? -ne 0 ]; then
        echo "Testing failed"
        exit 1
    fi

    # Stage 5: Documentation
    claude-agent document

    echo "Pipeline completed successfully"
}

run_pipeline "$@"
```

### Pattern 3: Parallel Agents

Run multiple agents in parallel:

```
Parallel Analysis:

1. Security Agent
   - Scan for vulnerabilities
   - Check dependencies
   - Review auth/authz

2. Performance Agent
   - Profile code
   - Find bottlenecks
   - Suggest optimizations

3. Quality Agent
   - Check code style
   - Find code smells
   - Calculate metrics

All agents run simultaneously, results merged at end.
```

## Session Hooks and Automation

### Pre-Session Hooks

Run before session starts:

```bash
# hooks/pre-session.sh
#!/bin/bash

echo "Preparing workspace..."

# Update dependencies
npm install

# Pull latest changes
git pull origin main

# Check environment
if [ ! -f .env ]; then
    echo "Warning: .env file not found"
fi

# Check database connection
if ! pg_isready -h localhost -p 5432; then
    echo "Warning: Database not available"
fi

# Load context
cat .claude/context.md
```

### Post-Session Hooks

Run after session ends:

```bash
# hooks/post-session.sh
#!/bin/bash

echo "Cleaning up..."

# Save session summary
claude-session-summary > ".claude/sessions/$(date +%Y-%m-%d-%H-%M).md"

# Commit changes
if [ -n "$(git status --porcelain)" ]; then
    git add .
    git commit -m "Session: $(date +%Y-%m-%d-%H-%M)"
fi

# Update context file
./hooks/update-context.sh

# Run tests
npm test

# Clean temporary files
rm -rf .tmp/
```

### Checkpoint Hooks

Run at regular intervals:

```bash
# hooks/checkpoint.sh
#!/bin/bash

# Auto-save every 30 minutes
while true; do
    sleep 1800  # 30 minutes

    # Save checkpoint
    ./hooks/save-checkpoint.sh "auto-$(date +%Y-%m-%d-%H-%M)"

    # Commit work-in-progress
    git add .
    git commit -m "WIP: Auto-checkpoint $(date +%Y-%m-%d-%H-%M)" || true
done
```

### Error Hooks

Run when errors occur:

```bash
# hooks/on-error.sh
#!/bin/bash

ERROR_MSG="$1"
ERROR_CONTEXT="$2"

echo "Error occurred: $ERROR_MSG"

# Save error context
cat > ".claude/errors/$(date +%Y-%m-%d-%H-%M).log" <<EOF
Error: $ERROR_MSG
Time: $(date)
Context: $ERROR_CONTEXT

Git Status:
$(git status)

Recent Commits:
$(git log --oneline -5)

Environment:
$(env | grep -v PASSWORD | grep -v SECRET)
EOF

# Notify team
if [ -n "$SLACK_WEBHOOK" ]; then
    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"Claude Code error: $ERROR_MSG\"}"
fi
```

## Advanced Patterns

### Session Templates

Create reusable session templates:

```markdown
# Template: Feature Development

## Setup Phase
- [ ] Create feature branch
- [ ] Update dependencies
- [ ] Review requirements
- [ ] Plan architecture

## Implementation Phase
- [ ] Implement core logic
- [ ] Add tests
- [ ] Add documentation
- [ ] Local testing

## Review Phase
- [ ] Self-review
- [ ] Fix issues
- [ ] Create PR
- [ ] Address feedback

## Completion Phase
- [ ] Merge PR
- [ ] Deploy to staging
- [ ] Verify deployment
- [ ] Update documentation
```

**Usage**:
```
Start session from template: Feature Development
Feature: User notifications
```

### Session Branching

Handle multiple concurrent tasks:

```
Main Session: Feature Development
├── Branch: Bug Fix (urgent)
│   └── Fix critical login bug
│       └── Return to main session
├── Branch: Code Review
│   └── Review PR #123
│       └── Return to main session
└── Continue: Feature Development
```

**Implementation**:

```typescript
// .claude/session-manager.ts
class SessionManager {
  private stack: Session[] = [];

  async branch(name: string, task: string): Promise<void> {
    // Save current session state
    const current = this.getCurrentSession();
    await current.saveState();

    // Create new session
    const branch = new Session(name, task);
    branch.parent = current;
    this.stack.push(branch);

    await branch.start();
  }

  async returnToParent(): Promise<void> {
    // Complete current session
    const current = this.stack.pop();
    await current.complete();

    // Restore parent session
    const parent = this.stack[this.stack.length - 1];
    await parent.restoreState();
  }
}
```

### Session Replay

Replay sessions for debugging or learning:

```typescript
// .claude/session-replay.ts
class SessionReplay {
  async replay(sessionId: string, options?: ReplayOptions): Promise<void> {
    const session = await this.loadSession(sessionId);

    for (const event of session.events) {
      if (options?.skipToolCalls && event.type === 'tool_call') {
        continue;
      }

      // Replay event
      await this.replayEvent(event);

      if (options?.stepByStep) {
        await this.waitForUserInput();
      }
    }
  }

  private async replayEvent(event: SessionEvent): Promise<void> {
    console.log(`[${event.timestamp}] ${event.type}: ${event.description}`);

    if (event.type === 'file_edit') {
      console.log(`  File: ${event.file}`);
      console.log(`  Changes: ${event.diff}`);
    }

    if (event.type === 'tool_call') {
      console.log(`  Tool: ${event.tool}`);
      console.log(`  Args: ${JSON.stringify(event.args)}`);
      console.log(`  Result: ${event.result}`);
    }
  }
}
```

## Best Practices

### Session Hygiene

1. **Regular Checkpoints**: Save progress frequently
2. **Clear Context**: Keep context files updated
3. **Clean State**: Remove temporary files
4. **Commit Often**: Small, focused commits
5. **Document Decisions**: Record why, not just what

### Context Optimization

1. **Prune Old Context**: Archive completed work
2. **Use References**: Link to docs instead of copying
3. **Layer Information**: Detail where needed, summaries elsewhere
4. **Structured Format**: Consistent markdown structure
5. **Version Context**: Track context file changes

### Collaboration

1. **Shared Context**: Team-accessible context files
2. **Handoff Documentation**: Clear handoff protocols
3. **Session Logs**: Reviewable session history
4. **Knowledge Base**: Build shared knowledge
5. **Best Practices**: Document team patterns

### Error Recovery

1. **Checkpoint Before Risky Operations**: Save state first
2. **Atomic Operations**: All-or-nothing changes
3. **Rollback Plans**: Know how to undo
4. **Error Logging**: Comprehensive error tracking
5. **Graceful Degradation**: Continue when possible

## Resources

- [Session Management Best Practices](https://docs.claude.com/session-management)
- [Context Window Optimization](https://docs.claude.com/context-optimization)
- [Multi-Agent Systems](https://docs.claude.com/multi-agent)
- [Background Tasks](https://docs.claude.com/background-tasks)
