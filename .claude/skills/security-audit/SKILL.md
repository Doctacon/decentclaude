---
name: security-audit
description: Security review workflow checking for SQL injection, XSS, CSRF, secrets, vulnerabilities, and auth/authz flaws
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Security Audit Skill

Comprehensive security review workflow that identifies vulnerabilities including SQL injection, XSS, CSRF, hardcoded secrets, dependency vulnerabilities, and authentication/authorization flaws.

## Workflow

### 1. Automated Security Scanning

Run automated tools first to catch common issues:

```bash
# Dependency vulnerability scanning
npm audit
pip-audit
safety check
go list -json -m all | nancy sleuth

# Static analysis security testing (SAST)
bandit -r . -f json -o bandit-report.json  # Python
eslint --ext .js,.jsx . --plugin security   # JavaScript
gosec ./...                                  # Go

# Secret scanning
trufflehog filesystem . --json
gitleaks detect --source . --verbose

# Container scanning (if applicable)
trivy image your-image:tag
docker scan your-image:tag
```

### 2. Manual Security Review Checklist

#### A. Injection Vulnerabilities

**SQL Injection**

Look for:
- String concatenation in SQL queries
- User input directly in queries
- Dynamic query construction

```python
# VULNERABLE
user_id = request.args.get('id')
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)

# SECURE
user_id = request.args.get('id')
query = "SELECT * FROM users WHERE id = ?"
db.execute(query, (user_id,))
```

```javascript
// VULNERABLE
const userId = req.query.id;
const query = `SELECT * FROM users WHERE id = ${userId}`;
db.query(query);

// SECURE
const userId = req.query.id;
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

**Command Injection**

Look for:
- User input in shell commands
- `exec`, `system`, `eval` with user input

```python
# VULNERABLE
filename = request.args.get('file')
os.system(f'cat {filename}')

# SECURE
filename = request.args.get('file')
# Validate filename
if not re.match(r'^[a-zA-Z0-9_-]+\.txt$', filename):
    raise ValueError('Invalid filename')
# Use safe alternatives
with open(filename, 'r') as f:
    content = f.read()
```

**NoSQL Injection**

```javascript
// VULNERABLE
const username = req.body.username;
db.users.find({ username: username });
// Attacker sends: {"$ne": null} to bypass

// SECURE
const username = String(req.body.username);
db.users.find({ username: username });
```

#### B. Cross-Site Scripting (XSS)

**Reflected XSS**

```python
# VULNERABLE
search_term = request.args.get('q')
return f"<html>Results for: {search_term}</html>"

# SECURE
from markupsafe import escape
search_term = request.args.get('q')
return f"<html>Results for: {escape(search_term)}</html>"
```

**Stored XSS**

```javascript
// VULNERABLE (React)
<div dangerouslySetInnerHTML={{__html: userComment}} />

// SECURE
<div>{userComment}</div>  // React escapes by default
```

**DOM-based XSS**

```javascript
// VULNERABLE
const name = location.hash.substring(1);
document.getElementById('welcome').innerHTML = 'Hello ' + name;

// SECURE
const name = location.hash.substring(1);
document.getElementById('welcome').textContent = 'Hello ' + name;
```

#### C. Cross-Site Request Forgery (CSRF)

Look for:
- State-changing operations without CSRF tokens
- GET requests that modify data
- Missing SameSite cookie attributes

```python
# VULNERABLE
@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form['amount']
    to_account = request.form['to']
    # Process transfer

# SECURE
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

@app.route('/transfer', methods=['POST'])
@csrf_required
def transfer():
    amount = request.form['amount']
    to_account = request.form['to']
    # Process transfer
```

```javascript
// Set SameSite cookie attribute
res.cookie('sessionId', sessionId, {
  httpOnly: true,
  secure: true,
  sameSite: 'strict'
});
```

#### D. Authentication Vulnerabilities

**Weak Password Requirements**

```python
# VULNERABLE
if len(password) >= 6:
    create_user(password)

# SECURE
import re
def validate_password(password):
    if len(password) < 12:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*]', password):
        return False
    return True
```

**Insecure Password Storage**

```python
# VULNERABLE
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# SECURE
from argon2 import PasswordHasher
ph = PasswordHasher()
password_hash = ph.hash(password)
```

**Missing Multi-Factor Authentication**

Check if MFA is:
- Available for all users
- Required for privileged accounts
- Using time-based tokens (TOTP) or hardware keys

**Broken Session Management**

```python
# VULNERABLE
session_id = "user_" + username  # Predictable

# SECURE
import secrets
session_id = secrets.token_urlsafe(32)
```

#### E. Authorization Vulnerabilities

**Broken Access Control**

```python
# VULNERABLE
@app.route('/user/<user_id>/profile')
def get_profile(user_id):
    user = User.query.get(user_id)
    return jsonify(user.to_dict())

# SECURE
@app.route('/user/<user_id>/profile')
@login_required
def get_profile(user_id):
    if current_user.id != user_id and not current_user.is_admin:
        abort(403)
    user = User.query.get(user_id)
    return jsonify(user.to_dict())
```

**Insecure Direct Object References (IDOR)**

```python
# VULNERABLE
@app.route('/document/<doc_id>')
def get_document(doc_id):
    doc = Document.query.get(doc_id)
    return send_file(doc.path)

# SECURE
@app.route('/document/<doc_id>')
@login_required
def get_document(doc_id):
    doc = Document.query.get(doc_id)
    if not doc or doc.owner_id != current_user.id:
        abort(404)  # Don't reveal if doc exists
    return send_file(doc.path)
```

#### F. Sensitive Data Exposure

**Hardcoded Secrets**

```bash
# Search for hardcoded secrets
grep -r "password\s*=\s*['\"]" --include="*.py" --include="*.js" .
grep -r "api_key\s*=\s*['\"]" --include="*.py" --include="*.js" .
grep -r "secret\s*=\s*['\"]" --include="*.py" --include="*.js" .
```

```python
# VULNERABLE
API_KEY = "sk_live_1234567890abcdef"
db_password = "admin123"

# SECURE
import os
API_KEY = os.environ['API_KEY']
db_password = os.environ['DB_PASSWORD']
```

**Sensitive Data in Logs**

```python
# VULNERABLE
logger.info(f"User logged in: {username} with password {password}")

# SECURE
logger.info(f"User logged in: {username}")
```

**Missing Encryption**

Check for:
- Passwords stored in plaintext
- API keys stored unencrypted
- PII transmitted over HTTP
- Database not using TLS

```python
# SECURE: Encrypt sensitive fields
from cryptography.fernet import Fernet

key = os.environ['ENCRYPTION_KEY']
cipher = Fernet(key)

encrypted_ssn = cipher.encrypt(ssn.encode())
```

#### G. Security Misconfiguration

**Debug Mode in Production**

```python
# VULNERABLE
app.run(debug=True)

# SECURE
app.run(debug=False)
# Or use environment variable
app.run(debug=os.environ.get('DEBUG', 'False') == 'True')
```

**Verbose Error Messages**

```python
# VULNERABLE
@app.errorhandler(Exception)
def handle_error(e):
    return str(e), 500  # Exposes stack traces

# SECURE
@app.errorhandler(Exception)
def handle_error(e):
    logger.exception(e)
    return "Internal server error", 500
```

**Missing Security Headers**

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

**CORS Misconfiguration**

```javascript
// VULNERABLE
app.use(cors({
  origin: '*'  // Allows any origin
}));

// SECURE
app.use(cors({
  origin: 'https://trusted-domain.com',
  credentials: true
}));
```

#### H. File Upload Vulnerabilities

```python
# VULNERABLE
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save(f'/uploads/{file.filename}')

# SECURE
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file', 400

    file = request.files['file']

    # Validate filename
    if not allowed_file(file.filename):
        return 'Invalid file type', 400

    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    if size > MAX_FILE_SIZE:
        return 'File too large', 400
    file.seek(0)

    # Secure filename
    filename = secure_filename(file.filename)

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{filename}"

    # Save outside web root
    filepath = os.path.join('/secure/uploads', unique_filename)
    file.save(filepath)

    return 'Upload successful', 200
```

#### I. API Security

**Rate Limiting**

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass
```

**API Key Exposure**

```javascript
// VULNERABLE (API key in client-side code)
const API_KEY = 'sk_live_1234567890';
fetch(`https://api.example.com/data?key=${API_KEY}`);

// SECURE (API key on server)
// Client calls your backend, backend uses API key
fetch('/api/data');  // Your backend endpoint
```

**Missing Input Validation**

```python
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    email = fields.Email(required=True)
    age = fields.Integer(
        required=True,
        validate=validate.Range(min=13, max=120)
    )
    username = fields.String(
        required=True,
        validate=validate.Regexp(r'^[a-zA-Z0-9_]{3,20}$')
    )

@app.route('/users', methods=['POST'])
def create_user():
    schema = UserSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Create user with validated data
```

### 3. Dependency Vulnerabilities

Check for known vulnerabilities in dependencies:

```bash
# Python
pip-audit
safety check --json
pip list --outdated

# JavaScript
npm audit
npm audit fix
yarn audit

# Go
go list -json -m all | nancy sleuth

# General (check against CVE databases)
snyk test
```

Review dependencies:
- Last update date (abandoned packages?)
- Known security issues
- Permissions required
- Alternatives with better security

### 4. Generate Security Report

Document findings using this template:

```markdown
# Security Audit Report

**Date**: YYYY-MM-DD
**Auditor**: Name
**Scope**: Components/services audited

## Executive Summary

- Total vulnerabilities found: X
- Critical: X
- High: X
- Medium: X
- Low: X

## Critical Vulnerabilities

### [CRITICAL-001] SQL Injection in User Search

**Location**: `app/routes/search.py`, line 45

**Description**: User input is directly concatenated into SQL query without parameterization.

**Vulnerable Code**:
```python
query = f"SELECT * FROM users WHERE name = '{search_term}'"
```

**Impact**: Attacker can execute arbitrary SQL, potentially dumping entire database or modifying data.

**Proof of Concept**:
```
GET /search?q=' OR '1'='1
Returns all users
```

**Remediation**:
```python
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (search_term,))
```

**CVSS Score**: 9.8 (Critical)
**Status**: Open
**Assigned To**: Dev Team
**Due Date**: ASAP

---

### [CRITICAL-002] Hardcoded AWS Credentials

**Location**: `config/settings.py`, line 12

**Description**: AWS access keys hardcoded in source code and committed to git.

**Vulnerable Code**:
```python
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
```

**Impact**: Anyone with repository access has full access to AWS account.

**Remediation**:
1. Rotate exposed credentials immediately
2. Move to environment variables
3. Use IAM roles instead
4. Add secrets to .gitignore
5. Scan git history and remove exposed secrets

**CVSS Score**: 10.0 (Critical)
**Status**: Open
**Assigned To**: DevOps
**Due Date**: ASAP

## High Vulnerabilities

### [HIGH-001] Missing CSRF Protection

...

## Medium Vulnerabilities

...

## Low Vulnerabilities

...

## Recommendations

1. Implement automated security scanning in CI/CD
2. Conduct quarterly security audits
3. Security training for developers
4. Bug bounty program
5. Penetration testing

## Tools Used

- Bandit (SAST)
- npm audit (dependency scan)
- Manual code review
- OWASP ZAP (DAST)

## Next Steps

1. Prioritize and fix critical vulnerabilities
2. Implement recommended security controls
3. Re-audit after fixes applied
```

### 5. Severity Scoring

Use CVSS (Common Vulnerability Scoring System):

- **Critical (9.0-10.0)**: Immediate action required
  - Remote code execution
  - Authentication bypass
  - Data breach

- **High (7.0-8.9)**: Fix within 1 week
  - SQL injection
  - XSS
  - Privilege escalation

- **Medium (4.0-6.9)**: Fix within 1 month
  - Missing security headers
  - Weak password policy
  - Information disclosure

- **Low (0.1-3.9)**: Fix when convenient
  - Verbose error messages
  - Missing rate limiting
  - Outdated dependencies (no known exploits)

## Security Best Practices

### Defense in Depth

Layer multiple security controls:
- Input validation
- Output encoding
- Authentication
- Authorization
- Logging/monitoring
- Rate limiting
- WAF (Web Application Firewall)

### Principle of Least Privilege

- Database user has minimal permissions
- API keys scoped to necessary operations
- User roles restrict access

### Secure Defaults

- Debug mode off in production
- HTTPS enforced
- Secure cookies (HttpOnly, Secure, SameSite)
- Strong password requirements

### Security Headers

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=()
```

## Compliance Considerations

- **GDPR**: Right to erasure, data portability, consent
- **PCI-DSS**: If handling credit cards
- **HIPAA**: If handling health data
- **SOC 2**: Security, availability, confidentiality

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
