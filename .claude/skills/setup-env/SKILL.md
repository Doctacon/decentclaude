---
name: setup-env
description: Dev environment setup workflow creating .env.example, documenting variables, configuring secrets management, and writing setup documentation
allowed-tools:
  - Read
  - Write
  - Bash
---

# Setup Env Skill

Development environment setup workflow for creating configuration templates, documenting environment variables, setting up secrets management, and creating comprehensive setup guides.

## Environment Variables

### .env.example Template

```.env
# Application
NODE_ENV=development
PORT=3000
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/myapp
DB_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379
REDIS_TTL=3600

# External APIs
STRIPE_API_KEY=sk_test_your_key_here
SENDGRID_API_KEY=SG.your_key_here
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRATION=24h
SESSION_SECRET=your-session-secret

# Feature Flags
FEATURE_NEW_CHECKOUT=false
FEATURE_BETA_ACCESS=false

# Monitoring
DATADOG_API_KEY=your_datadog_key
SENTRY_DSN=https://public@sentry.io/project-id
```

### .env (Not committed)

```.env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://admin:devpassword123@localhost:5432/myapp_dev
JWT_SECRET=local-dev-secret-not-for-production
STRIPE_API_KEY=sk_test_51abc123...
```

### .gitignore
```
.env
.env.local
.env.*.local
*.key
*.pem
secrets/
```

## Configuration Loading

### Node.js
```javascript
require('dotenv').config();

const config = {
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT, 10) || 3000,
  database: {
    url: process.env.DATABASE_URL,
    poolSize: parseInt(process.env.DB_POOL_SIZE, 10) || 10
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: process.env.JWT_EXPIRATION || '24h'
  }
};

// Validate required variables
const required = ['DATABASE_URL', 'JWT_SECRET'];
for (const key of required) {
  if (!process.env[key]) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
}

module.exports = config;
```

### Python
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv('FLASK_ENV', 'development')
    PORT = int(os.getenv('PORT', 5000))
    DATABASE_URL = os.getenv('DATABASE_URL')
    JWT_SECRET = os.getenv('JWT_SECRET')

    @classmethod
    def validate(cls):
        required = ['DATABASE_URL', 'JWT_SECRET']
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")

Config.validate()
```

## Secrets Management

### AWS Secrets Manager
```bash
# Store secret
aws secretsmanager create-secret \
    --name myapp/prod/db_password \
    --secret-string "super-secret-password"

# Retrieve secret
aws secretsmanager get-secret-value \
    --secret-id myapp/prod/db_password \
    --query SecretString \
    --output text
```

### Docker Secrets
```bash
echo "my_secret_password" | docker secret create db_password -

# Use in compose
services:
  app:
    secrets:
      - db_password
```

### Kubernetes Secrets
```bash
kubectl create secret generic app-secrets \
    --from-literal=db-password=supersecret \
    --from-literal=api-key=abc123

# Use in pod
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: db-password
```

## Setup README

```markdown
# Development Setup

## Prerequisites
- Node.js 18+
- PostgreSQL 14+
- Redis 7+
- Docker (optional)

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/org/repo.git
cd repo
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Setup Environment
```bash
cp .env.example .env
# Edit .env with your local values
```

### 4. Setup Database
```bash
# Create database
createdb myapp_dev

# Run migrations
npm run migrate
```

### 5. Start Application
```bash
npm run dev
```

Application runs at http://localhost:3000

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NODE_ENV | No | development | Environment (development/production) |
| PORT | No | 3000 | Server port |
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| JWT_SECRET | Yes | - | Secret for JWT signing |
| STRIPE_API_KEY | Yes | - | Stripe API key (test/live) |

## Docker Setup (Alternative)

```bash
docker-compose up
```

## Troubleshooting

**Database connection fails**
- Check PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL is correct

**Port already in use**
- Change PORT in .env
- Kill process: `lsof -ti:3000 | xargs kill`
```

## Best Practices
- Never commit .env files
- Use .env.example as template
- Document all variables
- Validate required variables on startup
- Use secrets managers in production
- Different secrets per environment
- Rotate secrets regularly
- Least privilege access
