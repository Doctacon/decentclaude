# DecentClaude Tutorial System

Welcome to the DecentClaude interactive tutorial system! This directory contains hands-on learning modules designed to help you master data engineering with Claude Code.

## Tutorial Structure

Each tutorial follows a consistent structure:

- **README.md** - Overview, prerequisites, and learning objectives
- **steps/** - Sequential lesson files with explanations
- **examples/** - Working code examples you can run
- **exercises/** - Practice assignments to test your understanding
- **solutions/** - Reference solutions for exercises

## Available Tutorials

### 1. Getting Started
**Path**: `getting-started/`
**Duration**: 30 minutes
**Prerequisites**: None

Learn the basics of DecentClaude, including:
- Project setup and environment configuration
- Understanding the codebase structure
- Your first data pipeline
- Using Claude Code effectively

### 2. dbt Basics
**Path**: `dbt-basics/`
**Duration**: 1 hour
**Prerequisites**: Getting Started

Master dbt fundamentals:
- Creating models and transformations
- Testing data quality
- Documentation best practices
- Deployment workflows

### 3. BigQuery Optimization
**Path**: `bigquery-optimization/`
**Duration**: 45 minutes
**Prerequisites**: dbt Basics

Optimize your BigQuery usage:
- Partitioning and clustering strategies
- Cost management and monitoring
- Query optimization techniques
- Performance tuning

### 4. Incident Response
**Path**: `incident-response/`
**Duration**: 1 hour
**Prerequisites**: dbt Basics

Handle production issues effectively:
- Incident classification and triage
- Debugging techniques
- Root cause analysis
- Post-incident reviews

## Learning Paths

### Junior Data Engineer Path
1. Getting Started → dbt Basics → BigQuery Optimization

### Senior Data Engineer Path
1. Getting Started → dbt Basics → Incident Response → BigQuery Optimization

### Operations Engineer Path
1. Getting Started → Incident Response → BigQuery Optimization

## How to Use These Tutorials

1. **Choose your tutorial** based on your learning path or interest
2. **Read the README** in the tutorial directory for prerequisites
3. **Follow the steps** in order - they build on each other
4. **Try the examples** - hands-on practice is essential
5. **Complete exercises** to validate your understanding
6. **Check solutions** only after attempting exercises yourself

## Getting Help

- Check the main [Data Engineering Patterns](../data-engineering-patterns.md) guide
- Review [Playbooks](../playbooks.md) for operational procedures
- Consult [Data Testing Patterns](../data-testing-patterns.md) for testing guidance

## Progress Tracking

To track your progress through tutorials, use the progression system:

```bash
# View your current progress
python progress-tracking/analytics/view_progress.py

# Mark a tutorial as completed
python progress-tracking/analytics/complete_tutorial.py <tutorial-name>
```

## Contributing

Found a bug or have an improvement? Tutorials are living documents:

1. Submit feedback via issues
2. Suggest improvements to existing content
3. Contribute new exercises or examples
4. Help keep tutorials up-to-date with best practices
