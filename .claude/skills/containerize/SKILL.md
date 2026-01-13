---
name: containerize
description: Containerization workflow creating optimized Dockerfiles with multi-stage builds, health checks, and security best practices
allowed-tools:
  - Read
  - Write
  - Bash
---

# Containerize Skill

Containerization workflow for creating production-ready Docker images with multi-stage builds, optimized layer caching, security hardening, and health checks.

## Dockerfile Best Practices

### Multi-Stage Build

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy only necessary files from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs package.json ./

# Switch to non-root user
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### Python Example

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

### Optimization Techniques

**Layer caching**:
```dockerfile
# Copy dependency files first (changes less often)
COPY package*.json ./
RUN npm ci

# Copy source code last (changes more often)
COPY . .
```

**Minimize image size**:
- Use alpine base images
- Multi-stage builds
- Remove build dependencies
- Use .dockerignore

**.dockerignore**:
```
node_modules
npm-debug.log
.git
.env
*.md
tests
.pytest_cache
__pycache__
```

### Security Hardening

```dockerfile
# 1. Use specific version tags
FROM node:18.17.0-alpine

# 2. Run as non-root user
USER nodejs

# 3. Read-only filesystem
docker run --read-only --tmpfs /tmp myapp

# 4. Drop capabilities
docker run --cap-drop=ALL myapp

# 5. Scan for vulnerabilities
docker scan myapp:latest
```

## Docker Compose

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s

  db:
    image: postgres:15-alpine
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  db-data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

## Best Practices

- Use official base images
- Specify exact versions
- Multi-stage builds for smaller images
- Run as non-root user
- Add health checks
- Use .dockerignore
- Scan images for vulnerabilities
- Minimize layers
- Cache dependencies separately from source
