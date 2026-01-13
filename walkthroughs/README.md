# Common Task Walkthroughs

This directory contains step-by-step walkthroughs for frequently performed tasks in DecentClaude. Each walkthrough is designed to be practical and actionable.

## Available Walkthroughs

### Data Engineering Tasks

1. **[Creating a New dbt Model](01-create-dbt-model.md)**
   - When: Adding new transformations
   - Time: 15 minutes
   - Difficulty: Beginner

2. **[Adding Schema Tests](02-add-schema-tests.md)**
   - When: Ensuring data quality
   - Time: 10 minutes
   - Difficulty: Beginner

3. **[Optimizing BigQuery Costs](03-optimize-bigquery-costs.md)**
   - When: Query costs are high
   - Time: 20 minutes
   - Difficulty: Intermediate

4. **[Creating Incremental Models](04-create-incremental-model.md)**
   - When: Working with large datasets
   - Time: 30 minutes
   - Difficulty: Intermediate

5. **[Setting Up Partitioning](05-setup-partitioning.md)**
   - When: Improving query performance
   - Time: 15 minutes
   - Difficulty: Intermediate

### Data Quality Tasks

6. **[Writing Custom Data Quality Checks](06-custom-quality-checks.md)**
   - When: Standard tests aren't enough
   - Time: 25 minutes
   - Difficulty: Intermediate

7. **[Debugging Failed Tests](07-debug-failed-tests.md)**
   - When: Tests are failing
   - Time: 15 minutes
   - Difficulty: Beginner

8. **[Creating Data Quality Reports](08-quality-reports.md)**
   - When: Need to track quality over time
   - Time: 20 minutes
   - Difficulty: Intermediate

### Operations Tasks

9. **[Performing a Schema Migration](09-schema-migration.md)**
   - When: Changing table structures
   - Time: 30 minutes
   - Difficulty: Advanced

10. **[Running a Backfill](10-run-backfill.md)**
    - When: Loading historical data
    - Time: 45 minutes
    - Difficulty: Advanced

11. **[Responding to an Incident](11-incident-response.md)**
    - When: Production issues occur
    - Time: Varies
    - Difficulty: Advanced

12. **[Deploying to Production](12-deploy-to-production.md)**
    - When: Promoting changes
    - Time: 20 minutes
    - Difficulty: Intermediate

## How to Use These Walkthroughs

1. **Choose the relevant walkthrough** for your task
2. **Read the prerequisites** to ensure you're ready
3. **Follow each step** in order
4. **Check the validation** section to verify success
5. **Review troubleshooting** if you encounter issues

## Walkthrough Structure

Each walkthrough follows this format:

- **Overview**: What you'll accomplish
- **Prerequisites**: What you need before starting
- **Time Estimate**: How long it typically takes
- **Steps**: Numbered, sequential instructions
- **Validation**: How to verify success
- **Troubleshooting**: Common issues and solutions
- **Related Resources**: Links to further reading

## Quick Reference

### Need to...

- Add a new table? → [Creating a New dbt Model](01-create-dbt-model.md)
- Fix a failing test? → [Debugging Failed Tests](07-debug-failed-tests.md)
- Reduce costs? → [Optimizing BigQuery Costs](03-optimize-bigquery-costs.md)
- Handle production issue? → [Responding to an Incident](11-incident-response.md)
- Deploy changes? → [Deploying to Production](12-deploy-to-production.md)

## Contributing

Have a common task that's not documented? Create a walkthrough:

1. Copy the template: `templates/walkthrough-template.md`
2. Follow the standard structure
3. Test the steps yourself
4. Submit for review

## Related Documentation

- [Data Engineering Patterns](../data-engineering-patterns.md) - Best practices
- [Playbooks](../playbooks.md) - Operational procedures
- [Tutorials](../tutorials/) - Interactive learning modules
