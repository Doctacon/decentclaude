---
name: optimize
description: Performance optimization workflow including profiling, bottleneck identification, optimization implementation, and benchmarking
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
---

# Optimize Skill

Performance optimization workflow that profiles code, identifies bottlenecks, suggests optimizations (algorithms, caching, queries), implements changes, and validates improvements through benchmarking.

## Workflow

### 1. Measure Baseline Performance

**Never optimize without measuring first.**

```bash
# Python profiling
python -m cProfile -o profile.stats script.py
python -m pstats profile.stats

# JavaScript profiling
node --prof app.js
node --prof-process isolate-*-v8.log > profile.txt

# Go profiling
go test -cpuprofile=cpu.prof -bench=.
go tool pprof cpu.prof
```

**Web application profiling**:
```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/endpoint

# Or use wrk
wrk -t4 -c100 -d30s http://localhost:8000/api/endpoint

# Or Artillery
artillery quick --count 100 --num 10 http://localhost:8000/api/endpoint
```

**Document baseline metrics**:
```
Endpoint: GET /api/users
Response time (p50): 250ms
Response time (p95): 450ms
Response time (p99): 850ms
Throughput: 40 req/s
CPU usage: 45%
Memory usage: 512MB
Database queries: 15 per request
```

### 2. Profile and Identify Bottlenecks

#### CPU Profiling

**Python**:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
process_data()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions by cumulative time
```

**JavaScript/Node.js**:
```javascript
const profiler = require('v8-profiler-next');

profiler.startProfiling('CPU profile');

// Your code here
processData();

const profile = profiler.stopProfiling();
profile.export((error, result) => {
  require('fs').writeFileSync('profile.cpuprofile', result);
});

// View in Chrome DevTools: chrome://inspect
```

**Go**:
```go
import _ "net/http/pprof"

func main() {
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()
    // Your code
}

// Then:
// go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

#### Memory Profiling

**Python**:
```python
from memory_profiler import profile

@profile
def process_data():
    # Your code
    pass

# Run with: python -m memory_profiler script.py
```

**JavaScript**:
```bash
node --expose-gc --inspect app.js
# Take heap snapshot in Chrome DevTools
```

**Go**:
```bash
go tool pprof http://localhost:6060/debug/pprof/heap
```

#### Database Query Profiling

**PostgreSQL**:
```sql
EXPLAIN ANALYZE
SELECT * FROM users
WHERE email = 'user@example.com';

-- Enable slow query log
ALTER SYSTEM SET log_min_duration_statement = 100;  -- Log queries >100ms
```

**MySQL**:
```sql
EXPLAIN
SELECT * FROM users
WHERE email = 'user@example.com';

-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 0.1;  -- Log queries >100ms
```

**MongoDB**:
```javascript
db.users.find({ email: 'user@example.com' }).explain('executionStats');
```

### 3. Common Performance Issues and Fixes

#### A. Algorithmic Complexity

**Issue: O(n²) algorithm**

```python
# SLOW: O(n²)
def find_duplicates(items):
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items):
            if i != j and item == other:
                duplicates.append(item)
    return duplicates

# FAST: O(n)
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

**Issue: Unnecessary sorting**

```javascript
// SLOW: O(n log n) when O(n) is sufficient
function findMax(numbers) {
  return numbers.sort((a, b) => b - a)[0];
}

// FAST: O(n)
function findMax(numbers) {
  return Math.max(...numbers);
}
```

#### B. Database Query Optimization

**Issue: N+1 query problem**

```python
# SLOW: N+1 queries
def get_users_with_posts():
    users = User.query.all()  # 1 query
    for user in users:
        user.posts = Post.query.filter_by(user_id=user.id).all()  # N queries
    return users

# FAST: 2 queries with eager loading
def get_users_with_posts():
    users = User.query.options(joinedload(User.posts)).all()
    return users
```

**Issue: Missing index**

```sql
-- SLOW: Full table scan
SELECT * FROM users WHERE email = 'user@example.com';

-- FAST: With index
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'user@example.com';
```

**Issue: SELECT ***

```sql
-- SLOW: Fetching unnecessary columns
SELECT * FROM users;

-- FAST: Only needed columns
SELECT id, email, name FROM users;
```

**Issue: Inefficient joins**

```sql
-- SLOW: Cartesian product
SELECT * FROM orders o, items i WHERE o.id = i.order_id;

-- FAST: Explicit join with indexes
SELECT o.*, i.* FROM orders o
INNER JOIN items i ON o.id = i.order_id
WHERE o.created_at > '2024-01-01';
```

#### C. Caching

**Application-level caching**:

```python
from functools import lru_cache

# SLOW: Recalculates every time
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# FAST: Memoized
@lru_cache(maxsize=None)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Redis caching**:

```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379)

def get_user(user_id):
    # Try cache first
    cached = cache.get(f'user:{user_id}')
    if cached:
        return json.loads(cached)

    # Cache miss: fetch from DB
    user = User.query.get(user_id)
    cache.setex(f'user:{user_id}', 3600, json.dumps(user.to_dict()))
    return user
```

**HTTP caching**:

```python
from flask import make_response

@app.route('/api/public-data')
def public_data():
    response = make_response(jsonify(data))
    response.headers['Cache-Control'] = 'public, max-age=3600'
    response.headers['ETag'] = hashlib.md5(str(data).encode()).hexdigest()
    return response
```

#### D. Lazy Loading and Pagination

**Issue: Loading too much data**

```python
# SLOW: Load all 1M users
users = User.query.all()

# FAST: Paginate
users = User.query.paginate(page=1, per_page=50)
```

**Issue: Eager loading when not needed**

```python
# SLOW: Always load related data
posts = Post.query.options(joinedload(Post.comments)).all()

# FAST: Lazy load when needed
posts = Post.query.all()
# Only load comments when accessed
for post in posts:
    if post.needs_comments:
        comments = post.comments
```

#### E. Parallel Processing

**Python parallel processing**:

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# SLOW: Sequential processing
results = [process_item(item) for item in items]

# FAST: Parallel (I/O bound)
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(process_item, items))

# FAST: Parallel (CPU bound)
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_item, items))
```

**JavaScript async parallel**:

```javascript
// SLOW: Sequential
for (const item of items) {
  await processItem(item);
}

// FAST: Parallel
await Promise.all(items.map(item => processItem(item)));

// FAST: Parallel with concurrency limit
const pLimit = require('p-limit');
const limit = pLimit(10);
await Promise.all(items.map(item => limit(() => processItem(item))));
```

#### F. Data Structure Optimization

**Issue: Wrong data structure**

```python
# SLOW: List lookup O(n)
items = ['a', 'b', 'c', 'd', ...]
if 'x' in items:  # Linear search
    pass

# FAST: Set lookup O(1)
items = {'a', 'b', 'c', 'd', ...}
if 'x' in items:  # Hash lookup
    pass
```

**Issue: Inefficient string concatenation**

```python
# SLOW: Creates new string each iteration
result = ""
for item in items:
    result += str(item)

# FAST: Join at the end
result = "".join(str(item) for item in items)
```

#### G. Batch Operations

**Database batch inserts**:

```python
# SLOW: Individual inserts
for user_data in users_data:
    db.session.add(User(**user_data))
    db.session.commit()

# FAST: Bulk insert
users = [User(**data) for data in users_data]
db.session.bulk_save_objects(users)
db.session.commit()
```

**API batch requests**:

```javascript
// SLOW: Sequential API calls
for (const id of userIds) {
  await api.getUser(id);
}

// FAST: Batch request
const users = await api.getUsers(userIds);
```

### 4. Frontend Performance

**Code splitting**:

```javascript
// Instead of importing everything
import { hugeLibrary } from 'huge-library';

// Lazy load
const hugeLibrary = () => import('huge-library');
```

**Image optimization**:

```html
<!-- Use appropriate formats -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <source srcset="image.jpg" type="image/jpeg">
  <img src="image.jpg" alt="Description">
</picture>

<!-- Lazy loading -->
<img src="image.jpg" loading="lazy" alt="Description">

<!-- Responsive images -->
<img
  srcset="small.jpg 480w, medium.jpg 800w, large.jpg 1200w"
  sizes="(max-width: 600px) 480px, (max-width: 1000px) 800px, 1200px"
  src="large.jpg"
  alt="Description">
```

**Debouncing and throttling**:

```javascript
// Debounce: Execute after delay if no new calls
function debounce(func, delay) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), delay);
  };
}

// Throttle: Execute at most once per delay
function throttle(func, delay) {
  let lastCall = 0;
  return function(...args) {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      func.apply(this, args);
    }
  };
}

// Usage
input.addEventListener('input', debounce(handleSearch, 300));
window.addEventListener('scroll', throttle(handleScroll, 100));
```

### 5. Benchmark and Validate

**Create benchmarks**:

```python
import timeit

def benchmark(func, *args, iterations=1000):
    timer = timeit.Timer(lambda: func(*args))
    execution_time = timer.timeit(number=iterations)
    return execution_time / iterations

# Compare implementations
time_old = benchmark(old_function, input_data)
time_new = benchmark(new_function, input_data)

print(f"Old: {time_old*1000:.2f}ms")
print(f"New: {time_new*1000:.2f}ms")
print(f"Improvement: {(time_old/time_new):.2f}x faster")
```

**Load testing**:

```bash
# Before optimization
ab -n 1000 -c 10 http://localhost:8000/api/endpoint
# Requests per second: 40

# After optimization
ab -n 1000 -c 10 http://localhost:8000/api/endpoint
# Requests per second: 120 (3x improvement!)
```

### 6. Document Optimizations

```markdown
# Performance Optimization Report

## Before

- Response time (p95): 450ms
- Throughput: 40 req/s
- CPU usage: 45%
- Database queries: 15 per request

## Optimizations Applied

### 1. Fixed N+1 Query Problem
- Used eager loading for user posts
- Reduced queries from 15 to 2 per request
- **Impact**: 30% latency reduction

### 2. Added Database Index
```sql
CREATE INDEX idx_users_email ON users(email);
```
- **Impact**: 50% faster user lookups

### 3. Implemented Caching
- Added Redis caching for frequently accessed data
- TTL: 5 minutes
- **Impact**: 40% reduction in database load

### 4. Algorithm Optimization
- Replaced O(n²) duplicate detection with O(n) hash-based approach
- **Impact**: 10x faster for large datasets

## After

- Response time (p95): 180ms (60% improvement)
- Throughput: 120 req/s (3x improvement)
- CPU usage: 25% (44% reduction)
- Database queries: 2 per request (87% reduction)

## Benchmark Results

```
Old implementation: 450ms average
New implementation: 180ms average
Improvement: 2.5x faster
```
```

## Performance Monitoring

**Set up monitoring**:
- Application Performance Monitoring (APM): Datadog, New Relic
- Real User Monitoring (RUM): for frontend performance
- Database query monitoring
- Resource utilization metrics

**Set performance budgets**:
```
API endpoints: p95 < 200ms
Page load time: < 2s
Time to Interactive: < 3s
Database queries: < 5 per request
```

## Best Practices

- **Measure first**: Never optimize without profiling
- **Focus on bottlenecks**: 80/20 rule - 20% of code causes 80% of slowness
- **Benchmark**: Compare before and after
- **Don't over-optimize**: Readable code > micro-optimizations
- **Monitor in production**: Synthetic tests don't catch everything
- **Set budgets**: Define acceptable performance targets
- **Automate testing**: Include performance tests in CI
