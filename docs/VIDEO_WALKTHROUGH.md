# Video Walkthrough Script

A 5-minute video tutorial for DecentClaude Data Workflows.

## Video Metadata

- **Title**: DecentClaude Data Workflows - 5 Minute Setup & Demo
- **Duration**: 5 minutes
- **Target Audience**: Data engineers, analytics engineers, dbt users
- **Prerequisites**: Basic knowledge of SQL and data warehouses

## Script Outline

### Opening (15 seconds)

**[Screen: Terminal with project README]**

> "Hi! In the next 5 minutes, I'll show you how to set up DecentClaude Data Workflows - a system that automates validation and quality checks for your data engineering work. You'll see how it catches errors before they happen, estimates costs before you run expensive queries, and keeps your data pipelines healthy."

### Part 1: What Is It? (30 seconds)

**[Screen: README.md features section]**

> "DecentClaude Data Workflows is a set of Claude Code hooks designed for data engineering. It gives you:
>
> - Automatic SQL validation before queries run
> - BigQuery cost estimation
> - Schema comparison tools
> - Table lineage tracking
> - Integration with dbt and SQLMesh
>
> All of this happens automatically as you work - no extra commands needed."

### Part 2: Installation (45 seconds)

**[Screen: Terminal showing setup wizard]**

> "Installation is easy. Just run the setup wizard:"

```bash
./bin/setup-wizard.sh
```

**[Show wizard running through the steps]**

> "The wizard checks your Python version, installs dependencies, and optionally sets up dbt, SQLMesh, and other tools. It takes about 2 minutes."

**[Show completion message]**

> "That's it! You're ready to go."

### Part 3: Demo 1 - Automatic SQL Validation (45 seconds)

**[Screen: Claude Code interface]**

> "Let's see it in action. Watch what happens when I ask Claude to run a query with a syntax error."

**[Type in Claude Code]**
```
Run this query: SELECT * FORM dataset.table WHERE date > '2024-01-01'
```

**[Show hook catching the error]**

> "Notice the hook caught the syntax error before running. It spotted 'FORM' instead of 'FROM'. This saves time and prevents errors in production."

**[Fix and run]**
```
Run this query: SELECT * FROM dataset.table WHERE date > '2024-01-01'
```

**[Show successful validation]**

> "Now with correct syntax, it validates and runs successfully."

### Part 4: Demo 2 - Cost Estimation (30 seconds)

**[Screen: Terminal]**

> "Before running an expensive query, you can estimate the cost:"

```bash
./bin/data-utils/bq-query-cost "SELECT * FROM bigquery-public-data.usa_names.usa_1910_current"
```

**[Show output with cost estimate]**

> "It shows you exactly how much data will be scanned and the estimated cost. This query would process 6.7 MB, costing less than a cent. But imagine if this was terabytes of data!"

### Part 5: Demo 3 - Schema Comparison (30 seconds)

**[Screen: Terminal]**

> "When tables change, you need to know what's different. Schema diff makes this easy:"

```bash
./bin/data-utils/bq-schema-diff project.dataset.table_v1 project.dataset.table_v2
```

**[Show output highlighting differences]**

> "It shows exactly what changed - new fields, removed fields, and type changes. Perfect for code reviews and understanding impact."

### Part 6: Demo 4 - Table Lineage (30 seconds)

**[Screen: Terminal]**

> "Before modifying a critical table, see what depends on it:"

```bash
./bin/data-utils/bq-lineage project.dataset.critical_table --direction=downstream
```

**[Show output with downstream dependencies]**

> "This shows all the views and tables that depend on this one. You can see the full dependency tree and understand the impact of your changes."

### Part 7: dbt Integration (30 seconds)

**[Screen: Claude Code with dbt project]**

> "If you use dbt, the hooks integrate seamlessly. Just ask Claude to compile your models:"

```
Run the dbt-compile hook
```

**[Show dbt compilation output]**

> "It compiles all your models and shows any errors. No need to leave Claude Code."

**[Show dbt test]**
```
Run the dbt-test hook
```

> "And run your tests the same way."

### Part 8: Common Workflows (30 seconds)

**[Screen: playbooks.md]**

> "The repository includes comprehensive playbooks for common workflows:
>
> - Adding new tables
> - Handling schema changes
> - Backfilling data
> - Responding to incidents
>
> Each playbook has step-by-step instructions and example commands."

### Closing (15 seconds)

**[Screen: QUICKSTART.md]**

> "Everything we covered is in the Quick Start Guide. Get started in 5 minutes with the setup wizard, explore the playbooks, and check out the best practices guide.
>
> Links in the description. Happy data engineering!"

## B-Roll Suggestions

Throughout the video, show:
- Terminal output with syntax highlighting
- Claude Code interface
- Quick cuts of different commands running
- Visual highlights of key output (errors, costs, differences)

## Visual Elements to Add in Post

1. **Timestamp overlays** for each section
2. **Highlight boxes** around important output
3. **Annotations** for key concepts (e.g., "Error caught before execution")
4. **Lower thirds** with command syntax
5. **End screen** with links to:
   - GitHub repository
   - Documentation
   - Quick Start Guide

## Recording Tips

### Terminal Setup
```bash
# Use a clean, readable font
# Recommend: Fira Code, JetBrains Mono, or Inconsolata

# Terminal colors
# Use a theme with good contrast (e.g., Solarized Dark, Dracula)

# Font size
# 16-18pt for recordings (larger than normal)

# Window size
# 1280x720 minimum for good readability
```

### Screen Recording Settings
- **Resolution**: 1920x1080 (1080p)
- **Frame rate**: 30fps
- **Format**: MP4 (H.264)
- **Audio**: 48kHz, 16-bit

### Speaking Tips
- Speak clearly and at moderate pace
- Pause briefly between sections
- Emphasize key benefits and features
- Keep energy high and enthusiastic

## Companion Materials

Create these to accompany the video:

1. **GitHub Gist** with all commands from the demo
2. **Sample data** for viewers to try with
3. **Timestamp chapters** in video description
4. **Written transcript** for accessibility

## Video Description Template

```
DecentClaude Data Workflows - Automated validation and quality checks for data engineering

In this 5-minute tutorial, you'll learn how to:
✓ Set up automated SQL validation
✓ Estimate BigQuery query costs
✓ Compare table schemas
✓ Track table dependencies
✓ Integrate with dbt and SQLMesh

🔗 Resources:
- Repository: [GitHub URL]
- Quick Start: [Link to QUICKSTART.md]
- Documentation: [Link to README.md]
- Playbooks: [Link to playbooks.md]

⏱ Timestamps:
0:00 - Introduction
0:15 - What is DecentClaude?
0:45 - Installation
1:30 - SQL Validation Demo
2:15 - Cost Estimation Demo
2:45 - Schema Comparison Demo
3:15 - Table Lineage Demo
3:45 - dbt Integration
4:15 - Common Workflows
4:30 - Closing

📦 Installation:
git clone [repo-url]
cd decentclaude
./bin/setup-wizard.sh

🎯 Use Cases:
- Data engineers automating validation
- Analytics engineers working with dbt
- Data teams managing BigQuery costs
- Anyone who wants better data quality

#dataengineering #bigquery #dbt #sql #claude #ai
```

## Thumbnail Design

**Elements:**
- Large text: "Data Workflows"
- Subtext: "Automated in 5 Minutes"
- Icon/image: Terminal with checkmarks or data flow diagram
- Color scheme: Match GitHub syntax highlighting (dark background, green/blue accents)
- Include: Claude Code logo if permitted

**Dimensions:** 1280x720 (16:9 ratio)

## Follow-up Video Ideas

After the quick start, consider these topics:

1. **Deep Dive: Custom Hooks** (10 min)
   - Creating custom validation rules
   - Adding new hooks
   - Extending the framework

2. **Real-World Workflows** (15 min)
   - Migration case study
   - Production incident response
   - Cost optimization walkthrough

3. **Best Practices** (10 min)
   - Table design patterns
   - Testing strategies
   - Team collaboration tips

4. **Advanced Features** (12 min)
   - SQLMesh integration
   - Complex lineage tracking
   - Automated documentation

## Alternative Format: Live Stream

Consider doing this as a live coding session:
- Interactive Q&A
- Real troubleshooting
- Viewer requests
- Longer format (30-60 min)
