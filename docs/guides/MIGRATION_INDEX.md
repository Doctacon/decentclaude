# Migration Documentation Index

Complete index of all migration-related documentation and utilities.

## Documentation

### Primary Guides

1. **[MIGRATION.md](./MIGRATION.md)** - Comprehensive migration guide
   - Overview and benefits
   - Migration from bq CLI
   - Migration from custom Python scripts
   - Migration from BigQuery console
   - Migration from legacy data quality tools
   - Migration strategy (4 phases)
   - Common pitfalls and solutions
   - Validation and rollback procedures
   - Success metrics and ROI

2. **[MIGRATION_QUICK_START.md](./MIGRATION_QUICK_START.md)** - Fast-track guide
   - 5-minute quick start
   - Common migration patterns
   - Migration checklist
   - Quick commands reference

## Migration Utilities

Located in: `bin/migration-utils/`

### 1. analyze-legacy-usage.py

Analyzes existing BigQuery usage patterns to prioritize migration.

**Purpose**: Identify what needs to be migrated and in what order

**Key Features**:
- Scans codebase for bq CLI commands
- Detects Python BigQuery client usage
- Identifies Great Expectations patterns
- Prioritizes by impact and complexity
- Generates HTML reports and JSON data

**Usage**:
```bash
./analyze-legacy-usage.py --scan-dir scripts/ --output-report report.html
```

**Outputs**:
- HTML report with migration candidates
- JSON file for programmatic processing
- Console summary with recommendations

### 2. convert-bq-script.py

Converts legacy bq CLI scripts to DecentClaude utilities.

**Purpose**: Automate script conversion where possible

**Key Features**:
- Detects common bq CLI patterns
- Suggests appropriate utilities
- Can auto-convert simple scripts
- Generates migration comments
- Creates conversion reports

**Usage**:
```bash
./convert-bq-script.py --input legacy.sh --output migrated.sh
```

**Conversions**:
- `bq query --dry_run` → `bq-query-cost`
- `bq show` → `bq-profile`
- `bq ls` → `bq-explore`
- Schema diffs → `bq-schema-diff`

### 3. migration-report.py

Generates migration assessment and progress tracking reports.

**Purpose**: Plan migration and track progress

**Key Features**:
- Initial migration assessment
- Effort and cost estimates
- Risk analysis
- Progress tracking
- Phase completion tracking
- Recommendations

**Usage**:
```bash
# Assessment
./migration-report.py --mode=assessment --output-report plan.html

# Progress tracking
./migration-report.py --mode=progress --baseline baseline.json --output-report progress.html
```

**Outputs**:
- HTML reports for stakeholder review
- JSON files for automation
- Recommendations based on progress

## Example Scripts

Located in: `bin/migration-utils/examples/`

### Legacy Examples

1. **legacy-profiler.sh** - Legacy shell script using bq CLI
   - Shows typical patterns to migrate
   - 10+ separate bq commands
   - No caching, no error handling
   - 2-5 minutes runtime

2. **legacy-quality-check.py** - Legacy Python data quality script
   - Manual quality check logic
   - 5+ separate API calls
   - No structured output
   - 30-60 seconds runtime

### Migrated Examples

1. **migrated-profiler.sh** - Migrated version using bq-profile
   - Single command instead of many
   - Built-in caching
   - Consistent error handling
   - 10-30 seconds runtime (instant if cached)

2. **migrated-quality-check.sh** - Migrated version using bq-profile
   - Single API call
   - Structured JSON output
   - Better for CI/CD
   - 5-10 seconds runtime

## File Structure

```
mayor/rig/
├── docs/
│   └── guides/
│       ├── MIGRATION.md                    # Comprehensive guide
│       ├── MIGRATION_QUICK_START.md        # Fast-track guide
│       └── MIGRATION_INDEX.md              # This file
│
└── bin/
    └── migration-utils/
        ├── README.md                       # Utilities documentation
        ├── analyze-legacy-usage.py         # Usage analysis tool
        ├── convert-bq-script.py            # Script conversion tool
        ├── migration-report.py             # Assessment & tracking tool
        │
        └── examples/
            ├── legacy-profiler.sh          # Legacy shell example
            ├── migrated-profiler.sh        # Migrated shell example
            ├── legacy-quality-check.py     # Legacy Python example
            └── migrated-quality-check.sh   # Migrated shell example
```

## Typical Workflow

### Phase 1: Analysis (Week 0)

1. Run usage analysis:
   ```bash
   ./analyze-legacy-usage.py --scan-dir scripts/ --output-report analysis.html
   ```

2. Generate migration plan:
   ```bash
   ./migration-report.py --mode=assessment --output-report plan.html
   ```

3. Review with team and get approval

### Phase 2: Initial Migrations (Weeks 1-2)

1. Convert high-priority scripts:
   ```bash
   ./convert-bq-script.py --input legacy.sh --output migrated.sh
   ```

2. Test and validate:
   ```bash
   # Compare outputs
   diff <(./legacy.sh args) <(./migrated.sh args)
   ```

3. Run in parallel for validation period

### Phase 3: Rollout (Weeks 3-6)

1. Update CI/CD pipelines
2. Train team on new utilities
3. Track progress weekly:
   ```bash
   ./migration-report.py --mode=progress --baseline baseline.json --output-report week3.html
   ```

### Phase 4: Completion (Weeks 7-8)

1. Archive legacy scripts
2. Update all documentation
3. Run final analysis to verify 0% legacy usage
4. Measure and celebrate success!

## Migration Patterns by Use Case

### Data Profiling

- **Legacy**: Multiple bq commands, manual aggregation
- **Migrated**: `bq-profile` single command
- **Guide**: MIGRATION.md "Example 2: Table Profiling"

### Cost Estimation

- **Legacy**: `bq query --dry_run` with manual calculation
- **Migrated**: `bq-query-cost` with recommendations
- **Guide**: MIGRATION.md "Example 1: Query Analysis"

### Schema Management

- **Legacy**: Manual diff of schema JSON files
- **Migrated**: `bq-schema-diff` with compatibility check
- **Guide**: MIGRATION.md "Example 3: Schema Management"

### Data Quality

- **Legacy**: Great Expectations or custom scripts
- **Migrated**: `bq-profile` with quality checks
- **Guide**: MIGRATION.md "Migration from Legacy Data Quality Tools"

### Query Optimization

- **Legacy**: Trial and error in console
- **Migrated**: `bq-explain` + `bq-optimize` workflow
- **Guide**: MIGRATION.md "Migration from BigQuery Console"

## Success Metrics

Track these throughout migration:

### Cost Metrics
- Monthly query costs (target: 25% reduction)
- API call costs (target: 60% reduction)
- Engineering time (target: 20 hours/month saved)

### Performance Metrics
- Profiling runtime (target: 70% reduction)
- Query development cycle time (target: 50% reduction)
- Data quality check runtime (target: 70% reduction)

### Adoption Metrics
- Legacy script usage (target: 0%)
- Utility usage (target: 100% of team)
- Team satisfaction (target: >80%)

## Support and Resources

### Documentation
- Full migration guide: [MIGRATION.md](./MIGRATION.md)
- Quick start: [MIGRATION_QUICK_START.md](./MIGRATION_QUICK_START.md)
- Utilities README: [bin/migration-utils/README.md](../../bin/migration-utils/README.md)

### Examples
- All example scripts: `bin/migration-utils/examples/`
- Before/after comparisons included

### Tools
- Usage analyzer: `bin/migration-utils/analyze-legacy-usage.py`
- Script converter: `bin/migration-utils/convert-bq-script.py`
- Progress tracker: `bin/migration-utils/migration-report.py`

### Getting Help
- Create GitHub issue with `migration` label
- Slack: #decentclaude-support
- Email: data-eng@example.com

## Version History

- **v1.0** (2024-01-13): Initial release
  - Comprehensive migration guide
  - Three migration utilities
  - Example scripts (legacy and migrated)
  - Quick start guide

---

*For the most up-to-date information, see the individual documentation files.*
