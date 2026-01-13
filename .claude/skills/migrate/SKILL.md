---
name: migrate
description: Migration planning workflow for database migrations, framework upgrades, and infrastructure changes with impact assessment and rollback plans
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Migrate Skill

Migration planning and execution workflow for database schema migrations, framework upgrades, library updates, and infrastructure changes.

## Workflow

### 1. Assess Impact

**Identify scope**:
- What is changing? (database, framework, infrastructure)
- How many components affected?
- Are there breaking changes?
- What's the blast radius?

**Check dependencies**:
```bash
# Find usages
grep -r "old_function" --include="*.py" --include="*.js"

# Check import statements
grep -r "from old_library" .

# Database dependencies
SELECT * FROM information_schema.table_constraints WHERE table_name = 'old_table';
```

### 2. Create Migration Plan

**Database Migration Plan Template**:
```markdown
## Migration: Add user_preferences table

### Changes
- Add new table: user_preferences
- Add foreign key: user_id → users.id
- Add indexes: user_id, preference_key

### Prerequisites
- Backup database
- Ensure no long-running transactions
- Schedule maintenance window

### Forward Migration
```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preference_key VARCHAR(50) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_user_preference UNIQUE (user_id, preference_key)
);

CREATE INDEX idx_user_prefs_user_id ON user_preferences(user_id);
```

### Rollback Migration
```sql
DROP TABLE IF EXISTS user_preferences CASCADE;
```

### Verification
```sql
-- Verify table created
SELECT * FROM information_schema.tables WHERE table_name = 'user_preferences';

-- Verify constraints
SELECT * FROM information_schema.table_constraints WHERE table_name = 'user_preferences';

-- Test insert
INSERT INTO user_preferences (user_id, preference_key, preference_value)
VALUES ((SELECT id FROM users LIMIT 1), 'theme', 'dark');
```

### Rollback Conditions
- Migration fails partway
- Application errors after migration
- Performance degradation
```

### 3. Database Migration Patterns

**Add Column (Safe)**:
```sql
-- Forward
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Rollback
ALTER TABLE users DROP COLUMN phone;
```

**Rename Column (Requires app changes)**:
```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Step 2: Copy data
UPDATE users SET email_address = email;

-- Step 3: Deploy app using new column

-- Step 4: Drop old column
ALTER TABLE users DROP COLUMN email;
```

**Change Column Type (Risky)**:
```sql
-- Step 1: Add new column
ALTER TABLE products ADD COLUMN price_new DECIMAL(10,2);

-- Step 2: Migrate data
UPDATE products SET price_new = CAST(price AS DECIMAL(10,2));

-- Step 3: Deploy app using new column

-- Step 4: Drop old, rename new
ALTER TABLE products DROP COLUMN price;
ALTER TABLE products RENAME COLUMN price_new TO price;
```

**Add Index (Can be slow on large tables)**:
```sql
-- Use CONCURRENTLY to avoid locking (PostgreSQL)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Check progress
SELECT * FROM pg_stat_progress_create_index;
```

### 4. Framework/Library Migration

**Example: React 17 → React 18**

```markdown
## Migration Plan: React 17 → 18

### Breaking Changes
1. ReactDOM.render → createRoot
2. Automatic batching
3. Concurrent features
4. Stricter hydration warnings

### Step 1: Update package.json
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  }
}
```

### Step 2: Update render method
```javascript
// Before
import ReactDOM from 'react-dom';
ReactDOM.render(<App />, document.getElementById('root'));

// After
import { createRoot } from 'react-dom/client';
const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

### Step 3: Test thoroughly
- Run full test suite
- Manual testing of key user flows
- Check console for warnings
- Performance testing

### Step 4: Address warnings
- Fix hydration mismatches
- Update deprecated lifecycle methods
- Review automatic batching impact

### Rollback
```bash
git revert <migration-commit>
npm install
npm test
```
```

### 5. Infrastructure Migration

**Example: EC2 → Kubernetes**

```markdown
## Migration: EC2 to Kubernetes

### Phase 1: Preparation
- Containerize application
- Create Kubernetes manifests
- Set up EKS cluster
- Configure networking (VPC, security groups)

### Phase 2: Parallel Run
- Deploy to K8s cluster
- Route 10% traffic to K8s
- Monitor metrics, logs, errors
- Gradually increase traffic

### Phase 3: Cutover
- Route 100% traffic to K8s
- Monitor for 24 hours
- Keep EC2 running as backup

### Phase 4: Cleanup
- Terminate EC2 instances
- Remove old infrastructure code
- Update documentation

### Rollback Plan
- Route traffic back to EC2
- Scale up EC2 instances if needed
- Investigate issues
```

### 6. Zero-Downtime Migration Strategies

**Blue-Green Deployment**:
```
1. Deploy new version (green) alongside old (blue)
2. Test green environment
3. Switch load balancer to green
4. Monitor for issues
5. Keep blue for quick rollback
6. After verification, decommission blue
```

**Canary Deployment**:
```
1. Deploy to small subset (5%)
2. Monitor metrics
3. Gradually increase (10%, 25%, 50%, 100%)
4. Rollback if issues detected
```

**Feature Flags**:
```python
# Gradual rollout with feature flag
if feature_flag.is_enabled('new_algorithm', user_id):
    return new_algorithm()
else:
    return old_algorithm()
```

### 7. Test Migration

**Test in staging first**:
```bash
# Restore production backup to staging
pg_restore -d staging_db prod_backup.dump

# Run migration in staging
./migrate.sh up

# Run tests
pytest tests/

# Verify data integrity
./scripts/verify_migration.sh
```

**Dry run**:
```bash
# PostgreSQL: Use transaction
BEGIN;
-- Run migration
-- Verify changes
ROLLBACK;  # Don't commit, just test

# MySQL
START TRANSACTION;
-- Run migration
-- Verify
ROLLBACK;
```

### 8. Execute Migration

**Pre-migration checklist**:
- [ ] Backup database
- [ ] Notify stakeholders
- [ ] Schedule maintenance window (if needed)
- [ ] Test migration in staging
- [ ] Prepare rollback scripts
- [ ] Monitor dashboards ready
- [ ] Team on standby

**Execution**:
```bash
# 1. Backup
pg_dump -h prod-db -U admin -d mydb > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Enable maintenance mode (if needed)
kubectl apply -f maintenance-mode.yaml

# 3. Run migration
./migrate.sh up

# 4. Verify
./scripts/verify.sh

# 5. Deploy application changes
kubectl apply -f deployment.yaml

# 6. Disable maintenance mode
kubectl delete -f maintenance-mode.yaml

# 7. Monitor
# Watch error rates, latency, logs for 30 minutes
```

### 9. Rollback if Needed

```bash
# 1. Enable maintenance mode
kubectl apply -f maintenance-mode.yaml

# 2. Rollback code
kubectl rollout undo deployment/myapp

# 3. Rollback database
./migrate.sh down
# Or restore from backup
psql -h prod-db -U admin -d mydb < backup_20240115_103000.sql

# 4. Verify rollback
./scripts/verify.sh

# 5. Disable maintenance mode
kubectl delete -f maintenance-mode.yaml
```

### 10. Post-Migration

**Verification**:
- [ ] All tests passing
- [ ] Key user flows working
- [ ] Performance metrics normal
- [ ] Error rates normal
- [ ] No data loss

**Documentation**:
```markdown
# Migration Report: User Preferences Table

**Date**: 2024-01-15
**Duration**: 15 minutes
**Downtime**: None

## What Changed
- Added user_preferences table
- Added foreign key constraint
- Updated UserService to use new table

## Results
- Migration successful
- All tests passing
- No errors in production
- Performance impact: negligible

## Issues Encountered
- None

## Lessons Learned
- Testing in staging caught index naming issue
- Concurrent index creation avoided locking
```

**Cleanup**:
- Remove migration scripts (or archive)
- Update documentation
- Remove old code paths
- Remove feature flags if used

## Best Practices

- **Always backup before migration**
- **Test in staging first**
- **Have rollback plan ready**
- **Minimize downtime** with online migrations
- **Communicate clearly** to stakeholders
- **Monitor closely** after migration
- **Document everything**
- **Keep migrations small** and focused
- **Version migrations** properly
- **Never skip migrations** in sequence
