# Database MCP Servers Setup Guide

## Overview

Database MCP servers enable Claude Code to connect to and interact with various database systems, including PostgreSQL, MySQL, SQLite, and others. This guide covers installation, configuration, and best practices for database integrations.

## PostgreSQL MCP Server

### Installation

```bash
# Install via npm
npm install -g @modelcontextprotocol/server-postgres

# Or use npx (no installation)
# Configuration in settings.json will use npx
```

### Prerequisites

- PostgreSQL server (local or remote)
- Database credentials
- Network access to database

### Configuration

#### Claude Code Settings

**Basic Configuration**:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://username:password@localhost:5432/database_name"
      }
    }
  }
}
```

**Using Individual Parameters**:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "myuser",
        "POSTGRES_PASSWORD": "mypassword",
        "POSTGRES_DATABASE": "mydb",
        "POSTGRES_SSL": "false"
      }
    }
  }
}
```

**Secure Configuration (using external file)**:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "bash",
      "args": [
        "-c",
        "POSTGRES_CONNECTION_STRING=$(cat ~/.config/postgres/connection) npx -y @modelcontextprotocol/server-postgres"
      ]
    }
  }
}
```

Create connection string file:
```bash
mkdir -p ~/.config/postgres
echo "postgresql://user:pass@localhost:5432/db" > ~/.config/postgres/connection
chmod 600 ~/.config/postgres/connection
```

**SSL/TLS Configuration**:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@host:5432/db?sslmode=require",
        "POSTGRES_SSL_CA": "/path/to/ca-cert.pem",
        "POSTGRES_SSL_CERT": "/path/to/client-cert.pem",
        "POSTGRES_SSL_KEY": "/path/to/client-key.pem"
      }
    }
  }
}
```

### Available Operations

#### Schema Exploration

```sql
-- List all schemas
List all schemas in the database

-- List tables in a schema
List all tables in the public schema

-- Get table schema
Show me the schema for users table

-- List columns with data types
Describe the columns in the orders table

-- Get table constraints
Show all constraints on the products table

-- List indexes
Show all indexes on the users table

-- Get foreign key relationships
Show foreign key relationships for the orders table
```

#### Query Execution

```sql
-- Simple query
SELECT * FROM users WHERE active = true LIMIT 10

-- Complex query with joins
SELECT
  u.id, u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name
ORDER BY order_count DESC

-- Aggregation
SELECT
  DATE_TRUNC('day', created_at) as date,
  COUNT(*) as daily_orders
FROM orders
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY date
ORDER BY date
```

#### Data Modification

```sql
-- Insert
INSERT INTO users (name, email, created_at)
VALUES ('John Doe', 'john@example.com', NOW())

-- Update
UPDATE users
SET last_login = NOW()
WHERE id = 123

-- Delete
DELETE FROM logs
WHERE created_at < NOW() - INTERVAL '90 days'

-- Upsert (INSERT ... ON CONFLICT)
INSERT INTO settings (key, value)
VALUES ('theme', 'dark')
ON CONFLICT (key)
DO UPDATE SET value = EXCLUDED.value
```

#### Database Administration

```sql
-- Analyze table statistics
ANALYZE users

-- Vacuum table
VACUUM ANALYZE orders

-- Check table size
SELECT
  pg_size_pretty(pg_total_relation_size('users')) as total_size,
  pg_size_pretty(pg_relation_size('users')) as table_size,
  pg_size_pretty(pg_indexes_size('users')) as indexes_size

-- Check database size
SELECT
  pg_database.datname,
  pg_size_pretty(pg_database_size(pg_database.datname)) as size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC

-- Check active connections
SELECT * FROM pg_stat_activity
WHERE datname = 'mydb'

-- Kill long-running queries
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
  AND query_start < NOW() - INTERVAL '5 minutes'
```

### Best Practices

#### Security

1. **Never Hardcode Credentials**:
   ```bash
   # Use environment variables or credential files
   # Add to .gitignore
   echo ".config/" >> .gitignore
   echo "settings.json" >> .gitignore
   ```

2. **Use Read-Only Accounts**: For analysis and reporting
   ```sql
   -- Create read-only user
   CREATE USER claude_readonly WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE mydb TO claude_readonly;
   GRANT USAGE ON SCHEMA public TO claude_readonly;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO claude_readonly;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public
     GRANT SELECT ON TABLES TO claude_readonly;
   ```

3. **Use SSL/TLS**: Always for production connections
   ```
   POSTGRES_CONNECTION_STRING=postgresql://user:pass@host:5432/db?sslmode=require
   ```

4. **Restrict Network Access**: Use firewalls and VPNs
   ```bash
   # PostgreSQL pg_hba.conf
   host    mydb    claude_user    10.0.0.0/8    md5
   ```

#### Performance

1. **Use EXPLAIN for Query Analysis**:
   ```sql
   EXPLAIN ANALYZE
   SELECT * FROM large_table
   WHERE indexed_column = 'value'
   ```

2. **Limit Result Sets**:
   ```sql
   -- Always use LIMIT for exploration
   SELECT * FROM large_table LIMIT 100
   ```

3. **Use Indexes Effectively**:
   ```sql
   -- Check if index is being used
   EXPLAIN SELECT * FROM users WHERE email = 'test@example.com'

   -- Create index if needed
   CREATE INDEX idx_users_email ON users(email)
   ```

4. **Connection Pooling**: For production environments
   ```json
   {
     "env": {
       "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/db?pool_size=10"
     }
   }
   ```

#### Query Safety

1. **Use Transactions**: For data modifications
   ```sql
   BEGIN;
   UPDATE accounts SET balance = balance - 100 WHERE id = 1;
   UPDATE accounts SET balance = balance + 100 WHERE id = 2;
   COMMIT;
   ```

2. **Backup Before Modifications**:
   ```sql
   -- Create backup table
   CREATE TABLE users_backup AS SELECT * FROM users;

   -- Or export specific data
   COPY (SELECT * FROM users WHERE active = false)
   TO '/tmp/inactive_users.csv' CSV HEADER;
   ```

3. **Validate Before Deletes**:
   ```sql
   -- First, SELECT to verify
   SELECT COUNT(*) FROM logs WHERE created_at < '2024-01-01';

   -- Then delete
   DELETE FROM logs WHERE created_at < '2024-01-01';
   ```

## MySQL MCP Server

### Installation

```bash
# Install via npm
npm install -g @modelcontextprotocol/server-mysql

# Or use npx
npx -y @modelcontextprotocol/server-mysql
```

### Configuration

```json
{
  "mcpServers": {
    "mysql": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-mysql"],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "password",
        "MYSQL_DATABASE": "mydb"
      }
    }
  }
}
```

**Using Connection String**:

```json
{
  "mcpServers": {
    "mysql": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-mysql"],
      "env": {
        "MYSQL_CONNECTION_STRING": "mysql://user:password@localhost:3306/database"
      }
    }
  }
}
```

### MySQL-Specific Features

```sql
-- Show table status
SHOW TABLE STATUS LIKE 'users'

-- Show processlist
SHOW FULL PROCESSLIST

-- Analyze table
ANALYZE TABLE users

-- Optimize table
OPTIMIZE TABLE users

-- Check table
CHECK TABLE users

-- Show indexes
SHOW INDEXES FROM users

-- Show create table
SHOW CREATE TABLE users

-- Show variables
SHOW VARIABLES LIKE '%cache%'

-- Show status
SHOW STATUS LIKE '%thread%'
```

## SQLite MCP Server

### Installation

```bash
# Install via npm
npm install -g @modelcontextprotocol/server-sqlite

# Or use npx
npx -y @modelcontextprotocol/server-sqlite
```

### Configuration

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "/path/to/database.db"
      ]
    }
  }
}
```

**Multiple Databases**:

```json
{
  "mcpServers": {
    "sqlite-app": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "./app.db"]
    },
    "sqlite-analytics": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "./analytics.db"]
    }
  }
}
```

### SQLite-Specific Features

```sql
-- List tables
SELECT name FROM sqlite_master WHERE type='table'

-- Get table info
PRAGMA table_info(users)

-- Get indexes
PRAGMA index_list(users)

-- Get foreign keys
PRAGMA foreign_key_list(orders)

-- Database integrity check
PRAGMA integrity_check

-- Analyze query plan
EXPLAIN QUERY PLAN
SELECT * FROM users WHERE id = 1

-- Vacuum database
VACUUM

-- Get database size
SELECT page_count * page_size as size
FROM pragma_page_count(), pragma_page_size()

-- Attach another database
ATTACH DATABASE 'other.db' AS other_db
```

### SQLite Best Practices

1. **Use WAL Mode**: For better concurrency
   ```sql
   PRAGMA journal_mode=WAL
   ```

2. **Enable Foreign Keys**:
   ```sql
   PRAGMA foreign_keys=ON
   ```

3. **Optimize Queries**:
   ```sql
   ANALYZE
   ```

4. **Regular Vacuum**: Reclaim space
   ```sql
   VACUUM
   ```

## Database Connection Patterns

### Multiple Database Connections

Configure multiple database servers:

```json
{
  "mcpServers": {
    "postgres-prod": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@prod-host:5432/db"
      }
    },
    "postgres-staging": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@staging-host:5432/db"
      }
    },
    "mysql-analytics": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-mysql"],
      "env": {
        "MYSQL_CONNECTION_STRING": "mysql://user:pass@analytics-host:3306/analytics"
      }
    }
  }
}
```

### Read Replicas

```json
{
  "mcpServers": {
    "postgres-primary": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@primary:5432/db"
      }
    },
    "postgres-replica": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://readonly:pass@replica:5432/db"
      }
    }
  }
}
```

Usage:
```
# Use replica for read-only queries
Query the postgres-replica for user statistics

# Use primary for writes
Insert new user into postgres-primary
```

### SSH Tunneling

For secure access to remote databases:

```bash
# Create SSH tunnel
ssh -L 5432:localhost:5432 user@remote-host -N -f

# Or use autossh for persistent tunnels
autossh -M 0 -L 5432:localhost:5432 user@remote-host -N
```

Configure Claude Code to use tunneled connection:
```json
{
  "mcpServers": {
    "postgres-remote": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "remoteuser",
        "POSTGRES_PASSWORD": "password",
        "POSTGRES_DATABASE": "remotedb"
      }
    }
  }
}
```

## Common Workflows

### Data Analysis

```sql
-- Explore schema
List all tables in the database

-- Profile a table
Show me:
1. Schema for users table
2. Row count
3. Sample 100 rows
4. Column statistics
5. Index information

-- Find anomalies
Analyze the orders table and:
1. Find duplicate entries
2. Identify null values
3. Check for orphaned records
4. Validate foreign key relationships
```

### Data Migration

```sql
-- Pre-migration validation
1. Compare schemas between staging and production
2. Check row counts for all tables
3. Verify indexes exist
4. Check constraints

-- Post-migration validation
1. Compare row counts
2. Validate data integrity
3. Check for missing indexes
4. Run test queries
```

### Performance Tuning

```sql
-- Identify slow queries
For PostgreSQL:
SELECT
  query,
  calls,
  total_time,
  mean_time,
  max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10

-- Analyze table statistics
ANALYZE verbose users

-- Check index usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY tablename
```

### Data Quality Checks

```sql
-- Check for duplicates
SELECT email, COUNT(*)
FROM users
GROUP BY email
HAVING COUNT(*) > 1

-- Check for null values
SELECT
  COUNT(*) as total,
  COUNT(email) as has_email,
  COUNT(*) - COUNT(email) as missing_email
FROM users

-- Check referential integrity
SELECT o.id, o.user_id
FROM orders o
LEFT JOIN users u ON o.user_id = u.id
WHERE u.id IS NULL

-- Check data ranges
SELECT
  MIN(created_at) as earliest,
  MAX(created_at) as latest,
  COUNT(*) as total
FROM users
WHERE created_at > NOW() OR created_at < '2000-01-01'
```

### Schema Management

```sql
-- Export schema
pg_dump -s -h localhost -U user dbname > schema.sql

-- Compare schemas
1. Get table list from database A
2. Get table list from database B
3. For each table in both:
   - Compare column definitions
   - Compare indexes
   - Compare constraints
4. Report differences

-- Generate migration script
Based on schema differences:
1. Generate ALTER TABLE statements
2. Generate CREATE INDEX statements
3. Generate constraint additions
4. Provide rollback script
```

## Troubleshooting

### Connection Issues

**Error**: `Connection refused`

**Solution**:
```bash
# Check if database is running
pg_isready -h localhost -p 5432  # PostgreSQL
mysqladmin ping -h localhost     # MySQL

# Check network connectivity
telnet localhost 5432

# Verify credentials
psql -h localhost -U username -d database  # PostgreSQL
mysql -h localhost -u username -p          # MySQL

# Check firewall rules
sudo ufw status
```

**Error**: `SSL required`

**Solution**:
```json
{
  "env": {
    "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@host:5432/db?sslmode=require"
  }
}
```

**Error**: `Too many connections`

**Solution**:
```sql
-- Check connection limit
SHOW max_connections;  -- PostgreSQL
SHOW VARIABLES LIKE 'max_connections';  -- MySQL

-- Check current connections
SELECT COUNT(*) FROM pg_stat_activity;  -- PostgreSQL
SHOW PROCESSLIST;  -- MySQL

-- Increase connection limit (requires restart)
-- PostgreSQL: postgresql.conf
max_connections = 200

-- MySQL: my.cnf
max_connections = 200
```

### Query Issues

**Error**: `Query timeout`

**Solution**:
```sql
-- Set statement timeout
SET statement_timeout = '30s';  -- PostgreSQL

-- Kill long-running query
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid = 12345;  -- PostgreSQL

KILL 12345;  -- MySQL
```

**Error**: `Out of memory`

**Solution**:
```sql
-- Use cursor for large result sets
BEGIN;
DECLARE large_cursor CURSOR FOR SELECT * FROM large_table;
FETCH 1000 FROM large_cursor;
CLOSE large_cursor;
COMMIT;

-- Use pagination
SELECT * FROM large_table
ORDER BY id
LIMIT 1000 OFFSET 0;
```

### Permission Issues

**Error**: `Permission denied`

**Solution**:
```sql
-- Check user permissions
-- PostgreSQL
SELECT
  grantee,
  privilege_type
FROM information_schema.role_table_grants
WHERE table_name='users';

-- MySQL
SHOW GRANTS FOR 'username'@'localhost';

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON database.table TO 'username';
```

## Advanced Usage

### Custom Data Types

```sql
-- PostgreSQL: JSON operations
SELECT
  id,
  data->>'name' as name,
  data->>'email' as email
FROM users
WHERE data->>'status' = 'active'

-- PostgreSQL: Array operations
SELECT *
FROM products
WHERE 'electronics' = ANY(tags)

-- PostgreSQL: Full-text search
SELECT *
FROM articles
WHERE to_tsvector('english', content) @@ to_tsquery('database & performance')
```

### Window Functions

```sql
-- Running totals
SELECT
  date,
  amount,
  SUM(amount) OVER (ORDER BY date) as running_total
FROM sales

-- Ranking
SELECT
  user_id,
  score,
  RANK() OVER (ORDER BY score DESC) as rank
FROM leaderboard

-- Moving average
SELECT
  date,
  value,
  AVG(value) OVER (
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) as moving_avg_7day
FROM metrics
```

### CTEs (Common Table Expressions)

```sql
-- Recursive CTE for hierarchical data
WITH RECURSIVE org_tree AS (
  SELECT id, name, manager_id, 1 as level
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  SELECT e.id, e.name, e.manager_id, ot.level + 1
  FROM employees e
  JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT * FROM org_tree ORDER BY level, name
```

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQL Style Guide](https://www.sqlstyle.guide/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [MySQL Performance Best Practices](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
