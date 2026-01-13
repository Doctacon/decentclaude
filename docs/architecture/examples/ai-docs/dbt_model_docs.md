# Model Documentation: dbt_model_example

**Source File:** `examples/sql/dbt_model_example.sql`

**Generated:** 2026-01-12T17:19:08.688222

---

## Configuration

- **materialization:** table
- **partition_by:** "field": "event_date",
      "data_type": "date"
- **cluster_by:** ['user_id', 'event_type']

## Dependencies

### Sources
- `analytics.events`

### Refs
- `users`
