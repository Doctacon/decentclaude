# Video Tutorial Scripts for DecentClaude

Complete scripts for recording video tutorials. Each includes timing, screen actions, and narration.

## Tutorial 1: Getting Started (5 minutes)

**Target Audience**: New users setting up DecentClaude for the first time

**Learning Objectives**:
- Understand what DecentClaude is
- Complete basic installation
- Run first command successfully

### Script

**[0:00 - 0:30] Introduction**

*Screen: DecentClaude README*

"Welcome to DecentClaude - a comprehensive toolkit that makes data engineering with Claude Code incredibly productive. In this 5-minute tutorial, you'll learn what DecentClaude is and how to get started."

"DecentClaude provides 28 production-ready Skills, 7 specialized Subagents, pre-built hooks for automation, and over 40 BigQuery utilities. It's designed for world-class data engineers who demand excellence."

**[0:30 - 1:30] Prerequisites Check**

*Screen: Terminal showing prerequisite checks*

"Before we start, let's verify you have the required tools. You'll need:"

```bash
# Check Claude Code CLI
claude --version
# Output: claude version X.X.X

# Check Python 3.8+
python3 --version
# Output: Python 3.11.x

# Check Google Cloud credentials
gcloud auth list
# Should show authenticated account
```

"If any of these aren't installed, check the installation guide linked in the description."

**[1:30 - 3:00] Installation**

*Screen: Running setup-wizard.sh*

"Now let's install DecentClaude. We'll use the interactive setup wizard:"

```bash
git clone https://github.com/Doctacon/decentclaude.git
cd decentclaude
./bin/setup-wizard.sh
```

*Show wizard running through steps*

"The wizard will:"
- "Install Python dependencies"
- "Configure the BigQuery MCP server"
- "Install Claude Code Skills and hooks"
- "Set up shell completion"

"Just follow the prompts - it takes about 2 minutes."

**[3:00 - 4:30] First Command**

*Screen: Running bq-profile*

"Let's run your first command. We'll profile a BigQuery table:"

```bash
bin/data-utils/bq-profile bigquery-public-data.stackoverflow.posts_questions
```

*Show output*

"Notice how it shows:"
- "Row count and table size"
- "Column data types and nullability"
- "Data quality metrics"
- "Estimated query cost"

"All in one command instead of multiple console clicks or API calls."

**[4:30 - 5:00] Next Steps**

*Screen: docs/INDEX.md*

"You've completed the basics! Next steps:"
1. "Explore the Quick Start guide for common workflows"
2. "Try the Skills with `/data-lineage-doc` in Claude Code"
3. "Check out the BigQuery utilities for your datasets"

"See you in the next tutorial where we'll dive deep into BigQuery utilities!"

---

## Tutorial 2: BigQuery Utilities Deep Dive (10 minutes)

**Target Audience**: Users who completed Tutorial 1

**Learning Objectives**:
- Master core BigQuery utilities
- Understand when to use each tool
- Chain utilities for complex workflows

### Script

**[0:00 - 0:45] Overview**

*Screen: bin/data-utils/ directory listing*

"Welcome back! DecentClaude includes 23 BigQuery utilities that replace hundreds of lines of custom code. In this tutorial, we'll cover the 7 most important ones."

*Show utility categories*

"They're organized by purpose:"
- "Discovery: bq-profile, bq-lineage, bq-explain"
- "Comparison: bq-schema-diff, bq-table-compare"
- "Optimization: bq-optimize, bq-query-cost"

**[0:45 - 2:00] bq-profile: Your Starting Point**

*Screen: Running bq-profile on a production table*

"Let's start with `bq-profile` - this is your go-to for understanding any table:"

```bash
bq-profile myproject.analytics.user_events --format=markdown
```

*Show output sections*

"Notice it shows:"
- "Table metadata: size, row count, partitioning"
- "Schema with types and null percentages"
- "Data quality score and recommendations"
- "Related tables via foreign keys"

"Use this before writing any query - it prevents costly mistakes."

**[2:00 - 3:30] bq-lineage: Dependency Discovery**

*Screen: Running bq-lineage*

"Next is `bq-lineage` - essential for impact analysis:"

```bash
bq-lineage myproject.analytics.user_events --direction=downstream --format=mermaid
```

*Show Mermaid diagram rendering*

"This shows everything that depends on this table. Before making schema changes, always check downstream dependencies."

```bash
bq-lineage myproject.analytics.user_events --direction=upstream --depth=2
```

"And this shows the sources - great for understanding data pipelines."

**[3:30 - 5:00] bq-explain: Query Analysis**

*Screen: Running bq-explain on a slow query*

"When queries are slow or expensive, use `bq-explain`:"

```bash
bq-explain --file=slow_query.sql
```

*Show explanation output*

"It analyzes:"
- "Execution plan and stages"
- "Bytes scanned and estimated cost"
- "Performance bottlenecks"
- "Optimization suggestions"

*Show implementing a suggestion*

"Here it suggests adding a partition filter. Let's see the impact:"

```bash
# Before: 10.2 TB scanned, $51.23
# After: 125 GB scanned, $0.63
```

"96% cost reduction from one change!"

**[5:00 - 6:30] bq-schema-diff: Safe Migrations**

*Screen: Comparing dev and prod schemas*

"Use `bq-schema-diff` before deploying schema changes:"

```bash
bq-schema-diff myproject.dev.users myproject.prod.users
```

*Show diff output*

"It detects:"
- "New columns (safe)"
- "Removed columns (breaking!)"
- "Type changes (review carefully)"
- "Compatibility assessment"

"This prevents the 'deploy to prod and break everything' scenario."

**[6:30 - 8:00] bq-optimize: Automatic Improvements**

*Screen: Running bq-optimize*

"Want automatic query optimization? Use `bq-optimize`:"

```bash
bq-optimize --file=query.sql
```

*Show original and optimized queries side-by-side*

"It automatically:"
- "Adds partition filters where possible"
- "Pushes down predicates"
- "Suggests clustering columns"
- "Estimates cost savings"

"Copy the optimized query and you're done."

**[8:00 - 9:15] bq-query-cost: Budget Control**

*Screen: Estimating costs before running*

"Prevent surprise bills with `bq-query-cost`:"

```bash
bq-query-cost --file=analytics_report.sql
```

*Show cost breakdown*

"Perfect for:"
- "CI/CD pipelines (fail if cost > threshold)"
- "Dashboards (estimate refresh costs)"
- "Ad-hoc analysis (know before you run)"

*Show CI integration example*

"Here's a GitHub Action that blocks PRs with expensive queries."

**[9:15 - 10:00] Chaining Utilities**

*Screen: Complex workflow example*

"The real power is chaining utilities:"

```bash
# Profile table
bq-profile $TABLE > profile.txt

# Check dependencies
bq-lineage $TABLE --format=json > deps.json

# Optimize all downstream queries
for query in $(jq -r '.downstream[]' deps.json); do
    bq-optimize --file=$query
done
```

"You've now mastered BigQuery utilities! Next tutorial: Skills and workflow automation."

---

## Tutorial 3: Skills and Workflow Automation (8 minutes)

**Target Audience**: Users who completed Tutorial 2

**Learning Objectives**:
- Understand Claude Code Skills architecture
- Use Skills for complex workflows
- Combine Skills with utilities
- Customize Skills for your needs

### Script

**[0:00 - 0:45] What are Skills?**

*Screen: .claude/skills/ directory*

"DecentClaude includes 28 Skills - reusable workflows that orchestrate utilities and guide Claude through complex tasks."

*Show a SKILL.md file*

"Skills are markdown files with:"
- "Frontmatter defining the Skill"
- "Step-by-step instructions for Claude"
- "Code examples and best practices"
- "Integration with DecentClaude utilities"

"Let's see them in action."

**[0:45 - 2:30] /data-lineage-doc: Auto-Documentation**

*Screen: Claude Code session using /data-lineage-doc*

"In Claude Code, invoke a Skill with a slash command:"

```
/data-lineage-doc myproject.analytics.user_events
```

*Show Claude executing the workflow*

"Watch as Claude:"
1. "Calls `bq-lineage` to discover dependencies"
2. "Calls `bq-profile` on each related table"
3. "Generates a Mermaid diagram"
4. "Writes comprehensive documentation"
5. "Suggests optimization opportunities"

*Show final output - docs/data-lineage/user_events.md*

"5 minutes of work done in 30 seconds. The Skill handled all the orchestration."

**[2:30 - 4:00] /sql-optimizer: Systematic Optimization**

*Screen: Using /sql-optimizer*

"Let's optimize a slow dashboard:"

```
/sql-optimizer --file=dashboard_queries.sql
```

*Show workflow execution*

"The Skill:"
1. "Analyzes each query with `bq-explain`"
2. "Identifies bottlenecks and expensive operations"
3. "Applies optimizations with `bq-optimize`"
4. "Validates improvements with cost estimates"
5. "Documents changes and savings"

*Show before/after metrics*

"Query time: 47s → 6s (87% faster)"
"Cost per run: $2.14 → $0.31 (86% cheaper)"

**[4:00 - 5:30] /troubleshoot: Debugging Workflow**

*Screen: Debugging a failing dbt model*

"When something breaks, use `/troubleshoot`:"

```
/troubleshoot
```

*Show Claude's systematic approach*

"The Skill follows a hypothesis-driven method:"
1. "Reproduce the error"
2. "Search knowledge base for similar issues"
3. "Form hypothesis"
4. "Test hypothesis with minimal changes"
5. "Validate fix"
6. "Document root cause"

*Show resolution*

"Issue found: missing partition filter causing timeout. Fix applied and validated."

**[5:30 - 6:45] Combining Skills and Utilities**

*Screen: Complex workflow example*

"Skills can call utilities directly. Let's trace a data quality issue:"

```
/troubleshoot
```

*Show Claude's execution*

"Claude uses:"
- "`bq-profile` to check data quality metrics"
- "`bq-lineage` to trace upstream sources"
- "`bq-table-compare` to compare with yesterday"
- "Knowledge base search for similar patterns"

"Then provides root cause analysis and fix."

**[6:45 - 8:00] Customizing Skills**

*Screen: Editing a SKILL.md file*

"Skills are just markdown - customize them for your team:"

```markdown
---
name: custom-deployment-check
description: Pre-deployment validation for analytics tables
allowed-tools: [Bash, Read]
---

# Custom Deployment Check

## Step 1: Schema Validation
Run: bin/data-utils/bq-schema-diff dev.table prod.table

## Step 2: Data Quality
Run: bin/data-utils/bq-profile dev.table
Ensure quality_score > 85

## Step 3: Cost Check
Run: bin/data-utils/bq-query-cost --file=query.sql
Ensure cost_usd < 10.00
```

"Save to `.claude/skills/custom-deployment-check/SKILL.md` and it's ready to use."

"Next tutorial: See Skills in action during an incident response!"

---

## Tutorial 4: Incident Response Workflow (7 minutes)

**Target Audience**: Users who completed Tutorial 3

**Learning Objectives**:
- Execute incident response workflow
- Use Skills under pressure
- Document incident resolution
- Prevent recurrence

### Script

**[0:00 - 0:30] Scenario Setup**

*Screen: Alert showing dashboard broken*

"It's 2am. Your executive dashboard is broken. Revenue numbers are missing. Let's see how DecentClaude helps you resolve this quickly."

"The alert shows: 'Query timeout on revenue_summary view'"

**[0:30 - 2:00] Initial Triage with /triage-incident**

*Screen: Claude Code using /triage-incident*

"Start with the incident triage Skill:"

```
/triage-incident
```

*Show Claude's systematic triage*

"The Skill guides Claude through:"
1. "Assess severity (P1 - revenue reporting down)"
2. "Check dependencies with `bq-lineage revenue_summary`"
3. "Identify scope: 3 downstream dashboards affected"
4. "Form initial hypotheses"

*Show lineage diagram*

"Upstream source: `raw_events` table (1.2 TB, 50M rows/day)"

**[2:00 - 3:30] Root Cause Analysis**

*Screen: Using bq-profile and bq-explain*

"Claude investigates using utilities:"

```bash
# Profile the problematic view
bq-profile myproject.analytics.revenue_summary
# Shows: No partition filter, scanning full table

# Explain the underlying query
bq-explain --table=myproject.analytics.revenue_summary
# Shows: 47 TB scanned, 8 min execution time
```

*Show the issue*

"Root cause found: partition filter was removed in yesterday's deployment."

**[3:30 - 4:45] Immediate Mitigation**

*Screen: Applying quick fix*

"First, restore service. Claude suggests:"

```sql
-- Add partition filter to limit scan
CREATE OR REPLACE VIEW analytics.revenue_summary AS
SELECT * FROM analytics.revenue_base
WHERE date >= CURRENT_DATE() - 7  -- Limit to last week
```

"Deploy with validation:"

```bash
# Verify cost is acceptable
bq-query-cost --query="SELECT * FROM analytics.revenue_summary LIMIT 1"
# Output: $0.23 (acceptable)

# Verify data looks correct
bq query "SELECT COUNT(*) FROM analytics.revenue_summary"
# Output: 1.2M rows
```

*Show dashboard recovering*

"Dashboard restored in 4 minutes."

**[4:45 - 5:45] Prevention and Documentation**

*Screen: Using /document to create incident report*

"Now prevent recurrence. Use `/document` Skill:"

```
/document --type=incident-report
```

*Show generated report*

"Claude creates:"
- "Timeline of incident (detection to resolution)"
- "Root cause analysis"
- "Action items to prevent recurrence"
- "Monitoring improvements needed"

*Show suggested prevention*

"Recommended: Add partition filter check to CI/CD:"

```yaml
# .github/workflows/schema-check.yml
- name: Validate Views Have Partition Filters
  run: |
    bin/data-utils/bq-lint --check=partition-filter analytics.*
```

**[5:45 - 6:45] Post-Incident Review**

*Screen: Knowledge base update*

"Add to knowledge base so future incidents resolve faster:"

```bash
kb add solution \
  --title="View Query Timeout Due to Missing Partition Filter" \
  --category=performance \
  --solution="Add WHERE date >= CURRENT_DATE() - N filter to limit scan" \
  --validation="Run bq-query-cost to verify acceptable cost"
```

"Next time `/troubleshoot` encounters a similar error, it'll find this solution immediately."

**[6:45 - 7:00] Summary**

*Screen: Incident metrics*

"Incident resolved in 12 minutes total:"
- "4 min: Triage and root cause"
- "4 min: Fix and validation"
- "4 min: Documentation and prevention"

"Without DecentClaude:"
- "Manual BigQuery console navigation: 15-20 min"
- "Writing custom analysis scripts: 30-45 min"
- "Documentation: Often skipped due to time pressure"

"DecentClaude Skills guide you through the full process systematically."

"Thanks for watching! Check out the documentation for 24 more Skills and 7 specialized Subagents."

---

## Production Notes

### Recording Setup

**Screen Recording**:
- Tool: QuickTime Player (macOS) or OBS Studio (cross-platform)
- Resolution: 1920x1080
- Frame rate: 30 fps
- Audio: Built-in mic or USB mic for narration

**Terminal Setup**:
- Font: Menlo or Monaco, 14pt
- Color scheme: Dark theme with good contrast
- Window size: 100x30 (fills frame comfortably)
- Zoom: Increase font size for readability

**Code Editor**:
- VS Code with Material Theme
- Font: Fira Code, 16pt
- Hide sidebar during recording
- Enable breadcrumbs for context

### Editing Guidelines

**Pacing**:
- Keep narration steady (not rushed)
- Pause 1-2 seconds between sections
- Allow viewers to read output (3-5 seconds per screen)

**Cuts**:
- Cut out long command execution times (show start, cut, show result)
- Remove typos and corrections
- Keep natural pauses for emphasis

**Annotations**:
- Add text callouts for key points (yellow boxes)
- Highlight important lines in terminal (colored arrows)
- Zoom in on small text when needed

**Music**:
- Soft background music at 10% volume
- Royalty-free from YouTube Audio Library
- Fade out during narration, fade up during demo

### Upload Checklist

- [ ] Title: "DecentClaude Tutorial [N]: [Topic]"
- [ ] Description: Include links to docs, commands used, timestamps
- [ ] Tags: claude-code, bigquery, data-engineering, python, automation
- [ ] Thumbnail: Custom with tutorial number and topic
- [ ] Captions: Auto-generate and review for accuracy
- [ ] Playlist: Add to "DecentClaude Tutorials" playlist
- [ ] Cards: Link to next tutorial and documentation

### File Naming

- `decentclaude-tutorial-1-getting-started.mp4`
- `decentclaude-tutorial-2-bigquery-utilities.mp4`
- `decentclaude-tutorial-3-skills-automation.mp4`
- `decentclaude-tutorial-4-incident-response.mp4`

### Hosting Options

**YouTube** (Recommended for public):
- Largest audience reach
- Good analytics
- Free hosting
- Searchable

**Vimeo** (Recommended for enterprise):
- Professional appearance
- Better privacy controls
- Higher quality encoding
- No ads

**Internal Platform** (For teams):
- Full control
- Integration with internal docs
- Access restricted to team
- May need to host video files

---

## Recording Checklist

Before you record:

- [ ] Test all commands in script (they should work as shown)
- [ ] Set up clean terminal environment (clear history, hide sensitive info)
- [ ] Prepare sample data (use public datasets or anonymized data)
- [ ] Test screen recording software
- [ ] Do a practice run (catch awkward phrasing)
- [ ] Check audio levels
- [ ] Close notification apps
- [ ] Ensure stable internet (for any cloud operations)

During recording:

- [ ] Record in one take per section (easier to edit)
- [ ] Speak clearly and at moderate pace
- [ ] Pause between sections
- [ ] Show commands before running them (let viewers read)
- [ ] Highlight important output
- [ ] Stay positive and enthusiastic

After recording:

- [ ] Review footage for errors
- [ ] Edit out dead time and mistakes
- [ ] Add annotations and callouts
- [ ] Sync captions
- [ ] Export at high quality (1080p, H.264)
- [ ] Upload with complete metadata
- [ ] Test video playback on different devices

---

## Support Materials

All supporting materials for these tutorials are included in DecentClaude:

- **Sample data**: Use `bigquery-public-data.stackoverflow.*` (no setup needed)
- **Commands**: All utilities in `bin/data-utils/`
- **Skills**: All Skills in `.claude/skills/`
- **Documentation**: All docs in `docs/`
- **Examples**: Working examples in `examples/`

These tutorials are designed to be recorded as-is with minimal preparation.
