---
name: fix-ci
description: CI/CD troubleshooting workflow for analyzing build, test, and deployment failures across GitHub Actions, GitLab CI, and Jenkins
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
---

# Fix CI Skill

CI/CD troubleshooting workflow that analyzes build, test, and deployment failures, identifies root causes, and suggests fixes for GitHub Actions, GitLab CI, Jenkins, and other CI systems.

## Workflow

### 1. Identify the Failure

**Locate the failed job**:
```bash
# GitHub Actions
gh run list --limit 10
gh run view <run-id>
gh run view <run-id> --log-failed

# GitLab CI
gitlab-ci-lint .gitlab-ci.yml
gitlab ci trace <job-id>

# Jenkins
# View console output from Jenkins UI
```

**Determine failure type**:
- Build failure (compilation, dependency installation)
- Test failure (unit, integration, e2e tests)
- Linting/formatting failure
- Deployment failure
- Timeout
- Infrastructure/environment issue

### 2. Analyze Logs

**Download and review logs**:
```bash
# GitHub Actions
gh run view <run-id> --log > ci-logs.txt

# GitLab CI
gitlab ci trace <job-id> > ci-logs.txt

# Search for errors
grep -i "error\|failed\|exception" ci-logs.txt
grep -B5 -A5 "exit code [1-9]" ci-logs.txt
```

**Common log patterns**:

**Build failures**:
```
Error: Could not find or load main class
fatal error: file.h: No such file or directory
npm ERR! 404 Not Found - GET https://registry.npmjs.org/package
```

**Test failures**:
```
FAILED tests/test_module.py::test_function - AssertionError
TypeError: Cannot read property 'x' of undefined
panic: runtime error: invalid memory address
```

**Deployment failures**:
```
Error: connect ECONNREFUSED
Deployment timed out after 10 minutes
ImagePullBackOff
```

### 3. Common CI Issues and Fixes

#### A. Dependency Installation Failures

**Issue: Package not found**

```yaml
# BEFORE (GitHub Actions)
- name: Install dependencies
  run: pip install -r requirements.txt

# Error: Could not find a version that satisfies the requirement package==1.2.3
```

**Fix 1: Update lock file**
```bash
# Regenerate lock file
pip freeze > requirements.txt
# Or use specific index
pip install --index-url https://pypi.org/simple -r requirements.txt
```

**Fix 2: Use cache**
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

- name: Install dependencies
  run: pip install -r requirements.txt
```

**Issue: Dependency version conflict**

```yaml
# BEFORE
- run: npm install

# Error: ERESOLVE unable to resolve dependency tree
```

**Fix**:
```yaml
- run: npm ci  # Use exact versions from lock file
# Or
- run: npm install --legacy-peer-deps
```

#### B. Build Failures

**Issue: Compilation error**

```yaml
# BEFORE
- run: make build

# Error: gcc: error: file.c: No such file or directory
```

**Fix: Ensure correct working directory**
```yaml
- name: Build
  working-directory: ./src
  run: make build
```

**Issue: Missing build tools**

```yaml
# BEFORE
- run: go build

# Error: go: command not found
```

**Fix: Install build environment**
```yaml
- name: Set up Go
  uses: actions/setup-go@v4
  with:
    go-version: '1.19'

- run: go build
```

#### C. Test Failures

**Issue: Flaky tests**

```yaml
# BEFORE
- run: npm test

# Sometimes passes, sometimes fails
```

**Fix 1: Retry failed tests**
```yaml
- name: Run tests
  run: npm test -- --maxRetries=3
```

**Fix 2: Increase timeout**
```yaml
- name: Run tests
  run: npm test -- --testTimeout=10000
```

**Fix 3: Fix the flaky test**
```javascript
// BEFORE (timing dependent)
test('data loads', async () => {
  triggerLoad();
  await sleep(1000);  // Race condition
  expect(data).toBeDefined();
});

// AFTER (event driven)
test('data loads', async () => {
  const promise = waitForLoad();
  triggerLoad();
  await promise;
  expect(data).toBeDefined();
});
```

**Issue: Tests pass locally but fail in CI**

Common causes:
- Environment differences
- Missing environment variables
- Database not initialized
- Timezone differences
- Parallel test execution conflicts

**Fix: Match CI environment locally**
```bash
# Run tests in Docker matching CI environment
docker run --rm -v $(pwd):/app -w /app node:16 npm test

# Or use act to run GitHub Actions locally
act -j test
```

#### D. Linting/Formatting Failures

**Issue: Code style violations**

```yaml
# BEFORE
- run: eslint .

# Error: Expected indentation of 2 spaces
```

**Fix 1: Auto-fix**
```yaml
- run: eslint --fix .
- run: git diff --exit-code  # Fail if auto-fix made changes
```

**Fix 2: Add pre-commit hook**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.0.0
    hooks:
      - id: eslint
        args: [--fix]
```

#### E. Timeout Issues

**Issue: Job timeout**

```yaml
# BEFORE
- name: Run tests
  run: pytest
  timeout-minutes: 5

# Error: Job timed out
```

**Fix 1: Increase timeout**
```yaml
- name: Run tests
  run: pytest
  timeout-minutes: 30
```

**Fix 2: Run tests in parallel**
```yaml
- name: Run tests
  run: pytest -n auto  # Use pytest-xdist
```

**Fix 3: Split tests across jobs**
```yaml
strategy:
  matrix:
    test-group: [unit, integration, e2e]

steps:
  - name: Run ${{ matrix.test-group }} tests
    run: pytest tests/${{ matrix.test-group }}
```

#### F. Environment Variable Issues

**Issue: Missing secrets**

```yaml
# BEFORE
- run: deploy.sh

# Error: AWS_ACCESS_KEY_ID not set
```

**Fix: Add secrets**
```yaml
# GitHub Actions
- run: deploy.sh
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

# GitLab CI
deploy:
  script: deploy.sh
  variables:
    AWS_ACCESS_KEY_ID: $CI_AWS_ACCESS_KEY_ID
```

#### G. Docker Build Failures

**Issue: Image build fails**

```yaml
# BEFORE
- run: docker build -t myapp .

# Error: COPY failed: file not found
```

**Fix 1: Check .dockerignore**
```dockerfile
# .dockerignore
node_modules
.git
*.log
```

**Fix 2: Multi-stage build**
```dockerfile
# BEFORE
FROM node:16
COPY . .
RUN npm install
RUN npm run build

# AFTER
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:16-slim
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --production
CMD ["node", "dist/index.js"]
```

**Issue: Image pull rate limit**

```yaml
# Error: toomanyrequests: Rate limit exceeded
```

**Fix: Authenticate to Docker Hub**
```yaml
- name: Login to Docker Hub
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

#### H. Deployment Failures

**Issue: Kubernetes deployment fails**

```yaml
# Error: ImagePullBackOff
```

**Fix 1: Check image exists**
```yaml
- name: Verify image
  run: docker pull myregistry/myapp:${{ github.sha }}
```

**Fix 2: Add image pull secret**
```yaml
# k8s deployment
spec:
  imagePullSecrets:
    - name: regcred
```

**Issue: Health check fails**

```yaml
# Error: Deployment exceeded its progress deadline
```

**Fix: Adjust health check**
```yaml
# k8s deployment
spec:
  containers:
    - name: app
      livenessProbe:
        httpGet:
          path: /health
          port: 8080
        initialDelaySeconds: 30  # Increase if app slow to start
        periodSeconds: 10
        timeoutSeconds: 5
        failureThreshold: 3
```

### 4. Debugging Strategies

#### Enable Debug Logging

**GitHub Actions**:
```yaml
- name: Debug
  run: |
    echo "Runner OS: ${{ runner.os }}"
    echo "Working directory: $(pwd)"
    echo "Files:"
    ls -la
    echo "Environment:"
    env | sort
```

Or enable runner diagnostic logging:
```bash
# Set repository secret
ACTIONS_RUNNER_DEBUG=true
ACTIONS_STEP_DEBUG=true
```

**GitLab CI**:
```yaml
variables:
  CI_DEBUG_TRACE: "true"
```

#### Use Matrix Strategy to Isolate Issues

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    node: [14, 16, 18]
  fail-fast: false  # Don't cancel other jobs

steps:
  - uses: actions/setup-node@v3
    with:
      node-version: ${{ matrix.node }}
  - run: npm test
```

#### SSH into Runner (Self-hosted)

```yaml
- name: Setup tmate session
  uses: mxschmitt/action-tmate@v3
  if: failure()  # Only on failure
```

### 5. CI Configuration Best Practices

#### Efficient Caching

```yaml
# GitHub Actions
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: |
      ~/.npm
      ~/.cache/pip
      ~/.cache/go-build
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json', '**/requirements.txt', '**/go.sum') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```

#### Parallel Jobs

```yaml
jobs:
  test:
    strategy:
      matrix:
        test-suite: [unit, integration, e2e]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run ${{ matrix.test-suite }} tests
        run: npm run test:${{ matrix.test-suite }}
```

#### Conditional Execution

```yaml
# Only run on main branch
- name: Deploy
  if: github.ref == 'refs/heads/main'
  run: deploy.sh

# Only run if files changed
- name: Build frontend
  if: contains(github.event.head_commit.modified, 'frontend/')
  run: npm run build
```

#### Dependency Validation

```yaml
# Validate package-lock.json is in sync
- name: Validate dependencies
  run: |
    npm ci
    git diff --exit-code package-lock.json
```

### 6. CI Health Monitoring

**Track CI metrics**:
- Build success rate
- Average build duration
- Flaky test frequency
- Time to fix ratio

**Set up alerts**:
```yaml
# Notify on failure
- name: Notify on failure
  if: failure()
  uses: rtCamp/action-slack-notify@v2
  env:
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
    SLACK_MESSAGE: 'Build failed on ${{ github.ref }}'
```

### 7. Generate Fix Report

```markdown
# CI Failure Analysis

**Build**: #1234
**Branch**: feature/new-feature
**Commit**: abc123f
**Failed At**: 2024-01-15 10:30 UTC
**Duration**: 5m 23s

## Failure Summary

Job `test` failed with exit code 1

## Root Cause

Integration tests failed due to database connection timeout.

## Error Log

```
ERROR: connect ECONNREFUSED 127.0.0.1:5432
```

## Fix Applied

1. Increased PostgreSQL startup wait time from 5s to 15s
2. Added connection retry logic in test setup
3. Added health check before running tests

## Changes

```yaml
# .github/workflows/test.yml
services:
  postgres:
    image: postgres:14
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5  # Increased from 3
```

## Verification

- Retriggered build: PASSED
- Ran locally with same config: PASSED
- Monitored next 5 builds: All PASSED

## Prevention

- Added integration test documentation
- Updated CI troubleshooting guide
- Scheduled monthly CI config review
```

## Common CI Platforms

### GitHub Actions

**Workflow syntax**: YAML in `.github/workflows/`

**Key features**:
- Matrix builds
- Reusable workflows
- Composite actions
- Environments and secrets

### GitLab CI

**Workflow syntax**: YAML in `.gitlab-ci.yml`

**Key features**:
- Pipeline stages
- Child pipelines
- Dynamic child pipelines
- Auto DevOps

### Jenkins

**Workflow syntax**: Groovy in `Jenkinsfile`

**Key features**:
- Declarative and scripted pipelines
- Shared libraries
- Extensive plugin ecosystem

### CircleCI

**Workflow syntax**: YAML in `.circleci/config.yml`

**Key features**:
- Workflows and jobs
- Orbs (reusable packages)
- Docker layer caching

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [act - Run GitHub Actions locally](https://github.com/nektos/act)
