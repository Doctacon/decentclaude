# Data Catalog Integration

Sync BigQuery metadata, lineage, and data quality information to data catalogs.

## Supported Catalogs

- **Datahub** - Open source metadata platform with rich lineage support
- **Amundsen** - Data discovery and metadata platform by Lyft
- **Atlan** - Active metadata platform with data governance features

## Features

### Metadata Synchronization
- Table schema (columns, types, descriptions)
- Partitioning configuration (time-based, range-based)
- Clustering configuration
- Table statistics (row count, size)
- Labels and tags
- Creation and modification timestamps

### Lineage Tracking
- **Upstream lineage**: Tables referenced in view definitions
- **Downstream lineage**: Views and tables that reference this table
- Multi-level dependency traversal
- Automatic extraction from SQL queries

### Documentation Sync
- Table descriptions
- Column descriptions
- Markdown documentation integration
- Template-based documentation standards

### Data Quality Scores
- Table-level quality checks:
  - Table existence verification
  - Data presence validation
  - Schema documentation completeness
  - Data freshness (for partitioned tables)
- Column-level quality checks:
  - Null percentage analysis
  - Uniqueness ratio calculation
  - Distribution analysis
- Integration with existing `data_quality.py` framework

### Discoverability
- Searchable metadata in catalog UI
- Tag-based classification
- Usage statistics tracking
- Owner and steward assignment

## Installation

### Prerequisites

```bash
# Install required Python packages
pip install google-cloud-bigquery requests

# For Datahub
pip install acryl-datahub

# For Amundsen
pip install amundsen-databuilder

# For Atlan
# Use REST API (no additional package needed)
```

### Environment Setup

```bash
# Datahub
export DATAHUB_GMS_URL="http://localhost:8080"
export DATAHUB_TOKEN="your-token-here"

# Amundsen
export AMUNDSEN_METADATA_URL="http://localhost:5002"

# Atlan
export ATLAN_API_URL="https://your-tenant.atlan.com"
export ATLAN_API_TOKEN="your-api-token-here"

# Google Cloud
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Usage

### Command Line Interface

The `catalog-sync` utility is located in `bin/data-utils/catalog-sync`.

#### Basic Examples

```bash
# Sync a single table to Datahub
catalog-sync --catalog datahub --table my-project.my_dataset.my_table

# Sync entire dataset to Amundsen
catalog-sync --catalog amundsen --project my-project --dataset my_dataset

# Sync with lineage to Atlan
catalog-sync --catalog atlan --table my-project.my_dataset.my_table --include-lineage

# Sync without quality scores
catalog-sync --catalog datahub --dataset-id my-project.my_dataset --no-quality

# Use configuration file
catalog-sync --catalog datahub --table my-table --config-file config.json

# Get JSON output
catalog-sync --catalog datahub --table my-table --output json
```

#### Command Options

```
Required:
  --catalog {datahub,amundsen,atlan}
                        Target catalog system

Table/Dataset Selection (choose one):
  --table TABLE         Fully-qualified table ID (project.dataset.table)
  --project PROJECT --dataset DATASET
                        Project and dataset names
  --dataset-id DATASET_ID
                        Fully-qualified dataset ID (project.dataset)

Optional:
  --include-lineage     Include lineage information (default: True)
  --no-lineage          Skip lineage synchronization
  --include-quality     Include data quality scores
  --no-quality          Skip quality scores (default: True)
  --output {text,json}  Output format (default: text)
  --config-file FILE    Path to catalog configuration file (JSON)
```

### Configuration Files

Configuration files can be used to store catalog connection details and sync options.

Example configurations are in `examples/`:
- `catalog-config-datahub.json`
- `catalog-config-amundsen.json`
- `catalog-config-atlan.json`

**Datahub Configuration:**
```json
{
  "catalog_type": "datahub",
  "gms_url": "http://localhost:8080",
  "token": "${DATAHUB_TOKEN}",
  "sync_options": {
    "metadata": true,
    "lineage": true,
    "documentation": true,
    "quality": true
  }
}
```

**Amundsen Configuration:**
```json
{
  "catalog_type": "amundsen",
  "metadata_url": "http://localhost:5002",
  "sync_options": {
    "metadata": true,
    "lineage": true,
    "documentation": true,
    "quality": false
  }
}
```

**Atlan Configuration:**
```json
{
  "catalog_type": "atlan",
  "api_url": "https://your-tenant.atlan.com",
  "api_token": "${ATLAN_API_TOKEN}",
  "sync_options": {
    "metadata": true,
    "lineage": true,
    "documentation": true,
    "quality": true
  }
}
```

### Python API

You can also use the catalog integration directly from Python:

```python
from catalog_sync import get_catalog_adapter, sync_table

# Initialize adapter
config = {
    "gms_url": "http://localhost:8080",
    "token": "your-token"
}
adapter = get_catalog_adapter("datahub", config)

# Sync a table
options = {
    "metadata": True,
    "lineage": True,
    "quality": True
}
result = sync_table(adapter, "project.dataset.table", options)

print(f"Metadata pushed: {result['metadata']}")
print(f"Lineage pushed: {result['lineage']}")
print(f"Quality pushed: {result['quality']}")
```

### Quality Check Integration

The catalog integration includes a quality check bridge that connects the existing `data_quality.py` framework with catalog sync.

```bash
# Run quality checks and get catalog-ready payload
python scripts/catalog_quality_bridge.py my-project.my_dataset.my_table

# Include column-level checks
python scripts/catalog_quality_bridge.py my-project.my_dataset.my_table --include-columns

# Get JSON output
python scripts/catalog_quality_bridge.py my-project.my_dataset.my_table --output json
```

**Python API:**
```python
from catalog_quality_bridge import get_catalog_quality_payload

# Get complete quality payload
payload = get_catalog_quality_payload(
    "project.dataset.table",
    include_columns=True
)

# Use with catalog sync
adapter.push_quality_scores("project.dataset.table", payload["table_checks"])
```

## Workflow Integration

### dbt Integration

Add catalog sync as a post-hook in your dbt project:

```yaml
# dbt_project.yml
models:
  +post-hook:
    - "{{ catalog_sync('{{ this }}') }}"
```

Or use it in a macro:

```sql
{% macro catalog_sync(model_name) %}
  {% set table_id = target.project ~ '.' ~ target.schema ~ '.' ~ model_name %}
  {{ run_command('catalog-sync --catalog datahub --table ' ~ table_id) }}
{% endmacro %}
```

### SQLMesh Integration

Add catalog sync to your SQLMesh hooks:

```python
# config.py
from sqlmesh import Config

config = Config(
    post_statements=[
        "!catalog-sync --catalog datahub --table @this"
    ]
)
```

### CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Sync to Catalog
  run: |
    catalog-sync \
      --catalog datahub \
      --project ${{ env.GCP_PROJECT }} \
      --dataset ${{ env.DATASET }} \
      --output json > catalog-sync-results.json

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: catalog-sync-results
    path: catalog-sync-results.json
```

### Claude Code Hook Integration

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "after-table-update": {
      "command": "catalog-sync --catalog datahub --table @table_id"
    },
    "after-schema-change": {
      "command": "catalog-sync --catalog datahub --table @table_id --include-lineage"
    }
  }
}
```

## Catalog-Specific Features

### Datahub

**Strengths:**
- Rich lineage visualization
- Data quality assertions support
- Tag and glossary management
- Impact analysis tools

**API Format:**
- Uses Metadata Change Events (MCE)
- LinkedIn Pegasus Avro schema
- GMS (Generalized Metadata Service) endpoint

**Example:**
```bash
catalog-sync \
  --catalog datahub \
  --table my-project.my_dataset.fact_orders \
  --include-lineage \
  --include-quality
```

### Amundsen

**Strengths:**
- User-friendly search interface
- Table popularity tracking
- User bookmarks and favorites
- Data previews

**Limitations:**
- No native quality score support (uses tags instead)
- Basic lineage features

**Example:**
```bash
catalog-sync \
  --catalog amundsen \
  --project my-project \
  --dataset analytics \
  --no-quality
```

### Atlan

**Strengths:**
- Active metadata platform
- Data governance features
- Rich API and SDK
- Business glossary integration

**API Format:**
- REST API
- Entity-based model
- Built on Apache Atlas

**Example:**
```bash
catalog-sync \
  --catalog atlan \
  --table my-project.my_dataset.dim_customers \
  --include-lineage \
  --include-quality
```

## Architecture

### Components

```
catalog-sync (CLI)
├── CatalogAdapter (Base Class)
│   ├── get_table_metadata()
│   ├── get_lineage()
│   └── push_*() methods
├── DatahubAdapter
├── AmundsenAdapter
└── AtlanAdapter

catalog_quality_bridge
├── BigQueryTableQualityCheck
├── ColumnQualityCheck
└── get_catalog_quality_payload()
```

### Data Flow

```
BigQuery Table
    │
    ├──> Metadata Extraction (schema, partitioning, stats)
    ├──> Lineage Extraction (upstream/downstream dependencies)
    ├──> Quality Checks (table & column level)
    │
    └──> Catalog Adapter
         │
         ├──> Format for target catalog
         ├──> Push via API
         └──> Return results
```

### Extensibility

To add support for a new catalog:

1. Create a new adapter class extending `CatalogAdapter`
2. Implement required methods:
   - `push_metadata()`
   - `push_lineage()`
   - `push_documentation()`
   - `push_quality_scores()`
3. Add to `get_catalog_adapter()` factory function
4. Update documentation and examples

Example:

```python
class NewCatalogAdapter(CatalogAdapter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")

    def push_metadata(self, table_id: str, metadata: Dict[str, Any]) -> bool:
        # Implement catalog-specific metadata push
        pass

    # Implement other required methods...
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to catalog
```
Error: Failed to push metadata: Connection refused
```

**Solution:**
- Verify catalog service is running
- Check environment variables are set correctly
- Confirm network access to catalog endpoint
- Validate API tokens/credentials

### Authentication Errors

**Problem:** Authentication failed
```
Error: 401 Unauthorized
```

**Solution:**
- Verify API token is correct and not expired
- Check token has required permissions
- For Datahub: ensure token has `MANAGE_METADATA` privilege
- For Atlan: verify API key has appropriate role

### Lineage Extraction Issues

**Problem:** Lineage not extracted
```
Warning: Could not extract full lineage for table
```

**Solution:**
- Verify table is a view (base tables have no upstream lineage)
- Check INFORMATION_SCHEMA access permissions
- For complex queries, lineage extraction may be limited
- Use `--no-lineage` to skip if not needed

### Quality Check Failures

**Problem:** Quality checks timing out
```
Error: Query timeout exceeded
```

**Solution:**
- Use `--no-quality` to skip quality checks
- Reduce check complexity by limiting columns
- Increase timeout in configuration file
- Run quality checks separately and push results

## Performance Considerations

### Batch Processing

For large datasets, process in batches:

```bash
# Get list of tables
bq ls --max_results 1000 my-project:my_dataset | tail -n +3 | \
while read table_id rest; do
  catalog-sync --catalog datahub --table "my-project.my_dataset.$table_id"
  sleep 1  # Rate limiting
done
```

### Parallel Execution

Use GNU parallel for faster processing:

```bash
bq ls --format=csv my-project:my_dataset | tail -n +2 | \
parallel -j 5 "catalog-sync --catalog datahub --table my-project.my_dataset.{}"
```

### Incremental Sync

Track last sync time and only sync changed tables:

```bash
# Get tables modified since last sync
bq ls --max_results 1000 \
  --filter "lastModifiedTime>$(date -d '1 day ago' +%s)000" \
  my-project:my_dataset | \
while read table_id rest; do
  catalog-sync --catalog datahub --table "my-project.my_dataset.$table_id"
done
```

## Best Practices

1. **Regular Syncs**: Schedule daily or after schema changes
2. **Quality Integration**: Enable quality checks for critical tables
3. **Lineage First**: Sync lineage for understanding dependencies
4. **Documentation Standards**: Use templates from `docs/templates/`
5. **Monitoring**: Track sync success rates in your observability platform
6. **Access Control**: Use least-privilege service accounts
7. **Testing**: Test on dev datasets before production
8. **Error Handling**: Implement retry logic for transient failures

## Related Tools

- `bq-lineage`: Standalone lineage extraction tool
- `bq-schema-diff`: Schema comparison utility
- `data_quality.py`: Quality check framework
- `bq-partition-info`: Partition analysis tool

## References

- [Datahub Documentation](https://datahubproject.io/docs/)
- [Amundsen Documentation](https://www.amundsen.io/amundsen/)
- [Atlan Documentation](https://ask.atlan.com/)
- [BigQuery Python Client](https://googleapis.dev/python/bigquery/latest/)

## Support

For issues or feature requests:
- Check the troubleshooting section above
- Review example configurations in `examples/`
- Run tests: `python tests/test_catalog_integration.py`
- Check existing quality checks in `scripts/data_quality.py`
