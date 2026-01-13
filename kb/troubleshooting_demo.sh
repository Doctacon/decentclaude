#!/bin/bash
# Demo script showing troubleshooting tree usage examples

echo "========================================================================"
echo "TROUBLESHOOTING DECISION TREE - DEMO"
echo "========================================================================"
echo ""

# Show help
echo "1. Showing help..."
echo "------------------------------------------------------------------------"
python troubleshooting_tree.py --help
echo ""
echo ""

# Show search functionality
echo "2. Searching for 'permission denied' issues..."
echo "------------------------------------------------------------------------"
python troubleshooting_tree.py --search "permission denied"
echo ""
echo ""

# Show quick reference
echo "3. Quick reference guide..."
echo "------------------------------------------------------------------------"
head -50 ../docs/guides/troubleshooting-quick-ref.md
echo ""
echo "[... truncated for demo ...]"
echo ""
echo ""

# Show decision tree structure
echo "4. Decision tree documentation (first 30 lines)..."
echo "------------------------------------------------------------------------"
head -30 ../docs/guides/troubleshooting-tree.md
echo ""
echo "[... full documentation available in troubleshooting-tree.md ...]"
echo ""
echo ""

# Show MCP tools integration
echo "5. Example MCP tool commands from the guide..."
echo "------------------------------------------------------------------------"
cat << 'EOF'
# Find tables with a specific column
python -c "from mayor.rig.mcp import find_tables_with_column; print(find_tables_with_column('user_id'))"

# Check NULL percentages
python -c "from mayor.rig.mcp import get_table_null_percentages; print(get_table_null_percentages('project.dataset.table'))"

# Check for duplicates
python -c "from mayor.rig.mcp import get_uniqueness_details; print(get_uniqueness_details('project.dataset.table', 'id'))"

# Compare schemas
python -c "from mayor.rig.mcp import compare_schemas; print(compare_schemas('table_a', 'table_b'))"

# Check data freshness
python -c "from mayor.rig.mcp import get_data_freshness; print(get_data_freshness('project.dataset.table', 'timestamp_col'))"

# Estimate query cost
python -c "from mayor.rig.mcp import estimate_query_cost; print(estimate_query_cost('SELECT ...'))"
EOF
echo ""
echo ""

echo "========================================================================"
echo "INTERACTIVE MODE"
echo "========================================================================"
echo ""
echo "To start interactive troubleshooting, run:"
echo ""
echo "    python troubleshooting_tree.py"
echo ""
echo "Or jump directly to a category:"
echo ""
echo "    python troubleshooting_tree.py --category sql"
echo "    python troubleshooting_tree.py --category performance"
echo "    python troubleshooting_tree.py --category cost"
echo "    python troubleshooting_tree.py --category quality"
echo "    python troubleshooting_tree.py --category tool"
echo ""
echo "========================================================================"
