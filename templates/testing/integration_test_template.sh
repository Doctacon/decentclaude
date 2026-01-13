#!/bin/bash
# Template for integration test script
# Tests complete data pipeline from raw to marts

set -e  # Exit on error
set -u  # Error on undefined variables

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
TEST_DATASET="integration_test_$(date +%s)"
DBT_TARGET="${DBT_TARGET:-integration_test}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up test dataset..."
    bq rm -r -f -d "${PROJECT_ID}:${TEST_DATASET}" || true
}

# Register cleanup on exit
trap cleanup EXIT

# Main test flow
main() {
    log_info "Starting integration tests..."
    log_info "Test dataset: ${TEST_DATASET}"

    # Step 1: Set up test environment
    log_info "Step 1: Setting up test environment..."
    export DBT_SCHEMA="${TEST_DATASET}"

    # Create test dataset
    bq mk --dataset "${PROJECT_ID}:${TEST_DATASET}"

    # Step 2: Load test data (seeds)
    log_info "Step 2: Loading test data..."
    dbt seed --target "${DBT_TARGET}" --profiles-dir .

    # Step 3: Run dbt models
    log_info "Step 3: Running dbt models..."
    dbt run --target "${DBT_TARGET}" --profiles-dir .

    # Step 4: Run dbt tests
    log_info "Step 4: Running dbt tests..."
    dbt test --target "${DBT_TARGET}" --profiles-dir .

    # Step 5: Run custom validation queries
    log_info "Step 5: Running custom validations..."
    run_custom_validations

    # Step 6: Validate data quality
    log_info "Step 6: Running data quality checks..."
    run_data_quality_checks

    # Step 7: Test idempotency (run again, verify same results)
    log_info "Step 7: Testing idempotency..."
    test_idempotency

    log_info "All integration tests passed!"
}

# Custom validation queries
run_custom_validations() {
    # Validation 1: Check row counts
    local raw_count=$(bq query --use_legacy_sql=false --format=csv \
        "SELECT COUNT(*) FROM \`${PROJECT_ID}.${TEST_DATASET}.raw_orders\`" | tail -n 1)
    local staging_count=$(bq query --use_legacy_sql=false --format=csv \
        "SELECT COUNT(*) FROM \`${PROJECT_ID}.${TEST_DATASET}.stg_orders\`" | tail -n 1)
    local marts_count=$(bq query --use_legacy_sql=false --format=csv \
        "SELECT COUNT(*) FROM \`${PROJECT_ID}.${TEST_DATASET}.fct_orders\`" | tail -n 1)

    log_info "Row counts: raw=$raw_count, staging=$staging_count, marts=$marts_count"

    # Assert staging has >= 95% of raw (some filtering expected)
    local min_staging=$(echo "$raw_count * 0.95" | bc | cut -d'.' -f1)
    if [ "$staging_count" -lt "$min_staging" ]; then
        log_error "Staging count ($staging_count) is less than 95% of raw ($raw_count)"
        return 1
    fi

    # Assert marts equals staging
    if [ "$marts_count" -ne "$staging_count" ]; then
        log_error "Marts count ($marts_count) doesn't match staging ($staging_count)"
        return 1
    fi

    log_info "Row count validation passed"

    # Validation 2: Check for nulls in critical columns
    local null_count=$(bq query --use_legacy_sql=false --format=csv \
        "SELECT COUNT(*) FROM \`${PROJECT_ID}.${TEST_DATASET}.fct_orders\`
         WHERE order_id IS NULL OR customer_id IS NULL" | tail -n 1)

    if [ "$null_count" -ne "0" ]; then
        log_error "Found $null_count rows with null critical values"
        return 1
    fi

    log_info "Null validation passed"

    # Validation 3: Revenue reconciliation
    local query="
    WITH source_revenue AS (
      SELECT SUM(order_total) as revenue
      FROM \`${PROJECT_ID}.${TEST_DATASET}.raw_orders\`
    ),
    transformed_revenue AS (
      SELECT SUM(order_total) as revenue
      FROM \`${PROJECT_ID}.${TEST_DATASET}.fct_orders\`
    )
    SELECT
      ABS(s.revenue - t.revenue) / s.revenue as pct_diff
    FROM source_revenue s, transformed_revenue t
    "

    local pct_diff=$(bq query --use_legacy_sql=false --format=csv "$query" | tail -n 1)
    local threshold=$(echo "0.01" | bc -l)

    if (( $(echo "$pct_diff > $threshold" | bc -l) )); then
        log_error "Revenue mismatch: ${pct_diff}%"
        return 1
    fi

    log_info "Revenue reconciliation passed"
}

# Data quality checks using the data_quality.py script
run_data_quality_checks() {
    if command -v python3 &> /dev/null; then
        if [ -f "scripts/data_quality.py" ]; then
            log_info "Running data quality checks..."
            python3 scripts/data_quality.py
        else
            log_warn "data_quality.py not found, skipping quality checks"
        fi
    else
        log_warn "Python not found, skipping quality checks"
    fi
}

# Test idempotency by running pipeline twice
test_idempotency() {
    log_info "Running pipeline first time..."
    local checksum1=$(get_table_checksum "${PROJECT_ID}.${TEST_DATASET}.fct_orders")

    log_info "Running pipeline second time (without new data)..."
    dbt run --target "${DBT_TARGET}" --profiles-dir .

    local checksum2=$(get_table_checksum "${PROJECT_ID}.${TEST_DATASET}.fct_orders")

    if [ "$checksum1" != "$checksum2" ]; then
        log_error "Pipeline is not idempotent! Checksums differ:"
        log_error "  First run:  $checksum1"
        log_error "  Second run: $checksum2"
        return 1
    fi

    log_info "Idempotency test passed"
}

# Get table checksum for comparison
get_table_checksum() {
    local table_id=$1
    local query="
    SELECT
      TO_HEX(MD5(TO_JSON_STRING(
        STRUCT(
          COUNT(*) as row_count,
          SUM(FARM_FINGERPRINT(TO_JSON_STRING(t))) as content_hash
        )
      ))) as checksum
    FROM \`${table_id}\` t
    "
    bq query --use_legacy_sql=false --format=csv "$query" | tail -n 1
}

# Run main function
main "$@"
