# Troubleshooting Guide

Common issues and how to resolve them.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Python and Dependencies](#python-and-dependencies)
- [BigQuery Connection](#bigquery-connection)
- [CLI Utilities](#cli-utilities)
- [dbt Issues](#dbt-issues)
- [Hook Errors](#hook-errors)
- [Performance Issues](#performance-issues)
- [Error Messages](#error-messages)

---

## Installation Issues

### Setup wizard fails to run

**Error:**
```
bash: ./bin/setup-wizard.sh: Permission denied
```

**Solution:**
```bash
chmod +x ./bin/setup-wizard.sh
./bin/setup-wizard.sh
```

### Python version too old

**Error:**
```
Python 3.6 found, but 3.7+ required
```

**Solution:**

**macOS:**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3.11
```

**Windows:**
Download from https://www.python.org/downloads/

### pip not found

**Error:**
```
pip3: command not found
```

**Solution:**

**macOS:**
```bash
python3 -m ensurepip --upgrade
```

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-pip
```

**Verify:**
```bash
pip3 --version
```

---

## Python and Dependencies

### Module not found errors

**Error:**
```
ModuleNotFoundError: No module named 'sqlparse'
```

**Solution:**
```bash
pip3 install sqlparse
```

**Check installation:**
```bash
python3 -c "import sqlparse; print('✓ sqlparse installed')"
```

### Multiple Python versions conflict

**Error:**
```
ImportError: cannot import name 'xyz' from 'module'
```

**Solution:**

**Use virtual environment:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install sqlparse google-cloud-bigquery

# Run your commands
./bin/data-utils/bq-query-cost --help
```

### Permission denied during pip install

**Error:**
```
Permission denied: /usr/local/lib/python3.x/site-packages
```

**Solution:**

**Option 1: User install (recommended)**
```bash
pip3 install --user sqlparse
```

**Option 2: Virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install sqlparse
```

**Option 3: sudo (not recommended)**
```bash
sudo pip3 install sqlparse
```

---

## BigQuery Connection

### Authentication failed

**Error:**
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**Solution:**

**Option 1: gcloud auth (recommended)**
```bash
gcloud auth login
gcloud auth application-default login
```

**Option 2: Service account**
```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/keyfile.json"

# Add to shell config for persistence
echo 'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/keyfile.json"' >> ~/.bashrc
source ~/.bashrc
```

**Verify authentication:**
```bash
gcloud auth list
```

### Project not set

**Error:**
```
google.api_core.exceptions.BadRequest: Project ID not found
```

**Solution:**
```bash
# Set default project
gcloud config set project your-project-id

# Verify
gcloud config get-value project
```

### Permission denied on BigQuery

**Error:**
```
google.api_core.exceptions.Forbidden: 403 Access Denied
```

**Solution:**

**Check permissions:**
```bash
gcloud projects get-iam-policy your-project-id
```

**Required roles:**
- `roles/bigquery.user` - Run queries
- `roles/bigquery.dataViewer` - Read data
- `roles/bigquery.jobUser` - Create jobs

**Request access:**
Contact your GCP project administrator to grant these roles.

### Table not found

**Error:**
```
google.api_core.exceptions.NotFound: 404 Table project:dataset.table not found
```

**Solution:**

**Check table ID format:**
Must be `project.dataset.table` (with dots, not colons)

**Verify table exists:**
```bash
bq ls project:dataset
```

**Check permissions:**
```bash
# Try listing datasets
bq ls --project_id=your-project-id
```

---

## CLI Utilities

### Command not found

**Error:**
```
bq-query-cost: command not found
```

**Solution:**

**Option 1: Use full path**
```bash
./bin/data-utils/bq-query-cost --help
```

**Option 2: Add to PATH**
```bash
export PATH="$PATH:$(pwd)/bin/data-utils"

# Test
bq-query-cost --help

# Make permanent
echo 'export PATH="$PATH:/full/path/to/decentclaude/bin/data-utils"' >> ~/.bashrc
source ~/.bashrc
```

**Option 3: Create symlinks**
```bash
sudo ln -s "$(pwd)/bin/data-utils/bq-query-cost" /usr/local/bin/bq-query-cost
```

### Python interpreter error

**Error:**
```
/usr/bin/env: 'python3': No such file or directory
```

**Solution:**

**Fix shebang in script:**
```bash
# Find your Python path
which python3

# Edit script to use correct path
# Change #!/usr/bin/env python3
# To your actual path, e.g., #!/usr/bin/python3
```

### Import error in CLI utilities

**Error:**
```
ImportError: No module named 'google.cloud'
```

**Solution:**
```bash
pip3 install google-cloud-bigquery

# Verify
python3 -c "from google.cloud import bigquery; print('✓ BigQuery client works')"
```

---

## dbt Issues

### dbt not found

**Error:**
```
dbt: command not found
```

**Solution:**
```bash
pip3 install dbt-core dbt-bigquery

# Verify
dbt --version
```

### Profile not found

**Error:**
```
Profile 'default' not found
```

**Solution:**

**Create profile:**
```bash
mkdir -p ~/.dbt

cat > ~/.dbt/profiles.yml << EOF
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      project: your-project-id
      dataset: your_dataset
      threads: 4
      method: oauth
EOF
```

**Verify:**
```bash
dbt debug
```

### dbt compilation fails

**Error:**
```
Compilation Error in model my_model
  Could not find relation 'source_table'
```

**Solution:**

**Check sources.yml:**
```yaml
version: 2

sources:
  - name: analytics
    database: project-id
    schema: dataset_name
    tables:
      - name: source_table
```

**Verify table exists:**
```bash
bq show project-id:dataset_name.source_table
```

### dbt test failures

**Error:**
```
Failure in test not_null_users_user_id
```

**Solution:**

**Investigate:**
```sql
-- Run the actual test query
SELECT *
FROM your_project.your_dataset.users
WHERE user_id IS NULL
```

**Fix data or test:**
- Fix data issue, or
- Adjust test if expectation was wrong

---

## Hook Errors

### Hook not running

**Problem:**
Hooks don't seem to execute when expected.

**Solution:**

**Check hook configuration:**
Look for `.claude/settings.json` - but this repository doesn't use hooks in the standard way.

**Verify hook exists:**
```bash
ls .git-hooks/
```

**Check hook permissions:**
```bash
chmod +x .git-hooks/*
```

### Hook fails silently

**Problem:**
Hook runs but you don't see output.

**Solution:**

**Run hook manually:**
```bash
# Test pre-commit hook
.git-hooks/pre-commit
```

**Check exit code:**
```bash
echo $?
# 0 = success
# non-zero = failure
```

### Python script in hook fails

**Error:**
```
python: can't open file 'scripts/data_quality.py': [Errno 2] No such file or directory
```

**Solution:**

**Check working directory:**
```bash
# Hooks run from repo root
cd /path/to/decentclaude

# Run script
python3 scripts/data_quality.py
```

**Verify file exists:**
```bash
ls -la scripts/data_quality.py
```

---

## Performance Issues

### Queries are slow

**Problem:**
BigQuery queries take too long.

**Solution:**

**1. Check query cost/bytes:**
```bash
./bin/data-utils/bq-query-cost --file=slow_query.sql
```

**2. Add partition filter:**
```sql
-- Before
SELECT * FROM project.dataset.events

-- After
SELECT * FROM project.dataset.events
WHERE _PARTITIONTIME >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

**3. Check partitioning:**
```bash
./bin/data-utils/bq-partition-info project.dataset.events
```

**4. Consider clustering:**
```sql
CREATE OR REPLACE TABLE project.dataset.events
PARTITION BY DATE(event_timestamp)
CLUSTER BY user_id, event_type
AS SELECT * FROM project.dataset.events_backup
```

### CLI utilities timeout

**Problem:**
`bq-lineage` or other utilities timeout.

**Solution:**

**Increase timeout:**

Edit the script and increase timeout values, or run with smaller scope:

```bash
# Limit lineage depth
./bin/data-utils/bq-lineage project.dataset.table --depth=1

# Only check downstream
./bin/data-utils/bq-lineage project.dataset.table --direction=downstream
```

### Setup wizard is slow

**Problem:**
`pip install` takes forever.

**Solution:**

**Use faster mirror:**
```bash
pip3 install --index-url https://pypi.org/simple sqlparse
```

**Install without dependencies:**
```bash
pip3 install --no-deps sqlparse
```

**Skip optional tools:**
When wizard asks about dbt/sqlmesh, choose 'N' and install later if needed.

---

## Error Messages

### "INVALID_ARGUMENT: Invalid table ID"

**Cause:**
Wrong table ID format.

**Solution:**
Use `project.dataset.table` (dots, not colons):

```bash
# Wrong
bq-schema-diff project:dataset.table1 project:dataset.table2

# Correct
./bin/data-utils/bq-schema-diff project.dataset.table1 project.dataset.table2
```

### "Syntax error at line X"

**Cause:**
SQL syntax error in query.

**Solution:**

**Check the specific line:**
Error message shows line number. Common issues:
- Missing comma
- Typo in keyword (FORM instead of FROM)
- Unclosed quote or parenthesis

**Validate syntax:**
Ask Claude to check:
```
Validate this SQL for syntax errors: SELECT * FORM table
```

Hook will catch the error automatically.

### "Cannot find module 'X'"

**Cause:**
Missing Python dependency.

**Solution:**
```bash
# Common dependencies
pip3 install sqlparse
pip3 install google-cloud-bigquery
pip3 install sqlfluff
pip3 install dbt-core dbt-bigquery
```

### "No such file or directory"

**Cause:**
Wrong working directory or path.

**Solution:**

**Check current directory:**
```bash
pwd
# Should be in decentclaude repo root
```

**Use absolute paths:**
```bash
# Instead of
./bin/setup-wizard.sh

# Use
/full/path/to/decentclaude/bin/setup-wizard.sh
```

### "Access denied" or "Permission denied"

**Cause:**
File permissions or authentication issue.

**Solution:**

**For scripts:**
```bash
chmod +x bin/setup-wizard.sh
chmod +x bin/data-utils/*
```

**For BigQuery:**
```bash
gcloud auth login
gcloud auth application-default login
```

### "Table X does not exist"

**Cause:**
Table not found in BigQuery.

**Solution:**

**Verify table exists:**
```bash
bq show project:dataset.table
```

**Check dataset:**
```bash
bq ls project:dataset
```

**Check project:**
```bash
bq ls --project_id=project
```

---

## Still Having Issues?

### Diagnostic Steps

1. **Check Python version:**
```bash
python3 --version
# Should be 3.7 or higher
```

2. **Check installed packages:**
```bash
pip3 list | grep -E 'sqlparse|google-cloud-bigquery|dbt|sqlfluff'
```

3. **Check authentication:**
```bash
gcloud auth list
gcloud config get-value project
```

4. **Test BigQuery connection:**
```bash
python3 << EOF
from google.cloud import bigquery
client = bigquery.Client()
for dataset in client.list_datasets():
    print(dataset.dataset_id)
EOF
```

5. **Check file permissions:**
```bash
ls -la bin/
ls -la scripts/
```

### Getting Help

If you're still stuck:

1. **Check the logs:**
```bash
# Git hook logs (if any)
cat .git-hooks/*.log 2>/dev/null
```

2. **Run in verbose mode:**
```bash
# Add -x for bash debugging
bash -x ./bin/setup-wizard.sh
```

3. **Isolate the issue:**
- Test each component separately
- Disable hooks temporarily
- Try in a fresh virtual environment

4. **Document your issue:**
When asking for help, include:
- Operating system and version
- Python version
- Error message (full output)
- Steps to reproduce
- What you've already tried

### Common Gotchas

1. **Virtual environments:**
If using venv, activate it before running commands.

2. **Environment variables:**
Some tools need `GOOGLE_APPLICATION_CREDENTIALS` set.

3. **Path issues:**
CLI utilities need executable permissions and correct PATH.

4. **Table naming:**
Use dots (.) not colons (:) in table IDs: `project.dataset.table`

5. **Authentication:**
Run both `gcloud auth login` AND `gcloud auth application-default login`.

6. **dbt profiles:**
Profile must match your target in `dbt_project.yml`.

7. **Python path:**
Some systems have `python` vs `python3` - use `python3` explicitly.

---

## Quick Reference

### Essential Commands

```bash
# Installation
./bin/setup-wizard.sh

# Verify setup
python3 -c "import sqlparse; print('OK')"
python3 -c "from google.cloud import bigquery; print('OK')"

# Authentication
gcloud auth login
gcloud auth application-default login

# Test CLI
./bin/data-utils/bq-query-cost --help

# dbt
dbt debug
dbt compile
dbt test
```

### File Locations

- Setup wizard: `./bin/setup-wizard.sh`
- CLI utilities: `./bin/data-utils/`
- Quality checks: `./scripts/data_quality.py`
- Git hooks: `./.git-hooks/`
- dbt profile: `~/.dbt/profiles.yml`

### Environment Variables

```bash
# BigQuery authentication
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/keyfile.json"

# Add to PATH
export PATH="$PATH:/path/to/decentclaude/bin/data-utils"

# Python path (for SQLMesh)
export PYTHONPATH=.
```

---

Need more help? Check:
- README.md: Full documentation
- QUICKSTART.md: Getting started guide
- playbooks.md: Workflow patterns
- examples/: Example SQL and configs
