# GitHub MCP Server Setup Guide

## Overview

The GitHub MCP server enables Claude Code to interact with GitHub repositories, issues, pull requests, and other GitHub resources directly. This integration streamlines code review, issue management, and repository operations.

## Installation

### Prerequisites

- Node.js 16.x or higher
- GitHub account
- Repository access permissions

### Install the MCP Server

```bash
# Install via npm globally
npm install -g @modelcontextprotocol/server-github

# Or install locally in your project
npm install @modelcontextprotocol/server-github

# Or use npx (no installation required)
# This will be configured in settings.json
```

## Authentication Setup

### Option 1: Personal Access Token (Recommended for Individual Use)

1. **Create a Personal Access Token**:
   - Go to GitHub Settings: https://github.com/settings/tokens
   - Click "Generate new token" > "Generate new token (classic)"
   - Name it: `claude-code-github-access`
   - Set expiration (90 days recommended)
   - Select scopes:
     - `repo` (full repository access)
     - `read:org` (read organization data)
     - `read:user` (read user profile data)
     - `user:email` (access user email)
     - `workflow` (if you need GitHub Actions access)

2. **Copy the token** (you won't see it again!)

3. **Store securely**:
   ```bash
   # Create a secure file
   echo "ghp_your_token_here" > ~/.config/github/token
   chmod 600 ~/.config/github/token
   ```

4. **Set environment variable**:
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   export GITHUB_TOKEN=$(cat ~/.config/github/token)
   ```

### Option 2: GitHub App (Recommended for Organizations)

1. **Create a GitHub App**:
   - Go to Organization Settings > Developer settings > GitHub Apps
   - Click "New GitHub App"
   - Configure:
     - Name: `Claude Code Integration`
     - Homepage URL: Your organization URL
     - Webhook: Disabled (not needed)
     - Permissions:
       - Repository permissions:
         - Contents: Read & write
         - Issues: Read & write
         - Pull requests: Read & write
         - Metadata: Read-only
       - Organization permissions:
         - Members: Read-only

2. **Install the App** to repositories

3. **Generate private key** and configure authentication

### Option 3: OAuth App (For Web Applications)

Suitable for web-based integrations that need user authorization.

## Configuration

### Claude Code Settings

Add to your `settings.json`:

**Using Personal Access Token**:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

**Using Token from File** (more secure):

```json
{
  "mcpServers": {
    "github": {
      "command": "bash",
      "args": [
        "-c",
        "GITHUB_TOKEN=$(cat ~/.config/github/token) npx -y @modelcontextprotocol/server-github"
      ]
    }
  }
}
```

**Using Environment Variable**:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

Note: Requires `export GITHUB_TOKEN=...` in shell profile

### Verify Installation

Restart Claude Code and verify:

```
List issues in my repository owner/repo
```

## Available Tools

### Repository Operations

#### Search Repositories

Search for repositories across GitHub.

```
Search for repositories related to machine learning
```

**Parameters**:
- Query string
- Optional filters (language, stars, etc.)

**Returns**: List of matching repositories with metadata

#### Get Repository Information

Get detailed information about a repository.

```
Get information about facebook/react
```

**Returns**: Description, stars, forks, language, topics, latest commit, etc.

#### List Repository Contents

Browse files and directories in a repository.

```
List files in the src directory of facebook/react
```

**Parameters**:
- Repository (owner/repo)
- Path (optional)
- Branch/ref (optional)

**Returns**: Directory listing with file/folder information

#### Get File Contents

Read file contents from a repository.

```
Show me the README.md from facebook/react
```

**Parameters**:
- Repository (owner/repo)
- File path
- Branch/ref (optional)

**Returns**: File content (text or base64 for binary)

#### Create/Update Files

Create or update files in a repository.

```
Update the README.md in myorg/myrepo with this new content
```

**Parameters**:
- Repository
- File path
- Content
- Commit message
- Branch (optional)

**Requires**: Write permissions

### Branch Operations

#### List Branches

Get all branches in a repository.

```
List all branches in facebook/react
```

**Returns**: Branch names and latest commit info

#### Create Branch

Create a new branch.

```
Create a new branch called feature/new-component from main in myorg/myrepo
```

**Parameters**:
- Repository
- Branch name
- Source branch/commit

#### Get Branch Information

Get details about a specific branch.

```
Get information about the develop branch in myorg/myrepo
```

**Returns**: Latest commit, protection status, ahead/behind counts

### Issue Management

#### List Issues

List issues in a repository.

```
List all open issues in facebook/react
```

**Parameters**:
- Repository
- State (open, closed, all)
- Labels (optional)
- Assignee (optional)
- Sort (created, updated, comments)
- Direction (asc, desc)

**Returns**: Issue list with metadata

#### Get Issue Details

Get detailed information about an issue.

```
Show me issue #123 from facebook/react
```

**Returns**: Full issue details, comments, labels, assignees, state

#### Create Issue

Create a new issue.

```
Create an issue in myorg/myrepo:
Title: Fix login bug
Body: Users are unable to login with OAuth
Labels: bug, priority-high
Assignees: @username
```

**Parameters**:
- Repository
- Title
- Body (optional)
- Labels (optional)
- Assignees (optional)
- Milestone (optional)

**Returns**: Created issue details

#### Update Issue

Update an existing issue.

```
Update issue #123 in myorg/myrepo:
- Add label: needs-review
- Assign to: @username
- Change state to: closed
```

**Parameters**:
- Repository
- Issue number
- Title (optional)
- Body (optional)
- State (optional)
- Labels (optional)
- Assignees (optional)

#### Add Comment to Issue

Add a comment to an issue.

```
Add comment to issue #123 in myorg/myrepo:
This issue has been fixed in PR #456
```

**Parameters**:
- Repository
- Issue number
- Comment body

#### Search Issues

Search issues across repositories.

```
Search for issues with label "bug" in repositories under myorg
```

**Parameters**:
- Query string
- Filters (repo, label, assignee, etc.)

**Returns**: Matching issues

### Pull Request Management

#### List Pull Requests

List pull requests in a repository.

```
List all open pull requests in facebook/react
```

**Parameters**:
- Repository
- State (open, closed, all)
- Base branch (optional)
- Head branch (optional)
- Sort (created, updated, popularity)

**Returns**: PR list with metadata

#### Get Pull Request Details

Get detailed information about a PR.

```
Show me pull request #456 from facebook/react
```

**Returns**: PR details, diff stats, review status, checks, comments

#### Create Pull Request

Create a new pull request.

```
Create a pull request in myorg/myrepo:
Title: Add user authentication
Head: feature/auth
Base: develop
Body: This PR implements OAuth2 authentication with the following changes:
- Add OAuth2 provider configuration
- Implement login/logout flows
- Add user session management
```

**Parameters**:
- Repository
- Title
- Head branch
- Base branch
- Body (optional)
- Draft (optional)
- Maintainer can modify (optional)

**Returns**: Created PR details

#### Update Pull Request

Update an existing PR.

```
Update pull request #456 in myorg/myrepo:
- Change title to: Add user authentication with OAuth2
- Mark as ready for review
```

**Parameters**:
- Repository
- PR number
- Title (optional)
- Body (optional)
- State (optional)
- Base branch (optional)

#### Merge Pull Request

Merge a pull request.

```
Merge pull request #456 in myorg/myrepo using squash merge
```

**Parameters**:
- Repository
- PR number
- Merge method (merge, squash, rebase)
- Commit message (optional)

**Requires**: Write permissions and passing checks

#### List PR Reviews

Get reviews for a pull request.

```
Show all reviews for pull request #456 in myorg/myrepo
```

**Returns**: Review comments, approval status, requested changes

#### Add PR Review

Submit a review for a pull request.

```
Submit a review for PR #456 in myorg/myrepo:
Event: APPROVE
Body: LGTM! Great work on the authentication implementation.
```

**Parameters**:
- Repository
- PR number
- Event (APPROVE, REQUEST_CHANGES, COMMENT)
- Body (optional)
- Comments (optional, for specific code lines)

#### Request Reviewers

Request reviewers for a pull request.

```
Request review from @alice and @bob for PR #456 in myorg/myrepo
```

**Parameters**:
- Repository
- PR number
- Reviewers (usernames)
- Team reviewers (optional)

#### Get PR Diff

Get the diff/patch for a pull request.

```
Show me the diff for pull request #456 in myorg/myrepo
```

**Returns**: Full diff in unified format

#### List PR Commits

Get all commits in a pull request.

```
List all commits in pull request #456 from myorg/myrepo
```

**Returns**: Commit list with messages and authors

#### Check PR Status

Get CI/CD check status for a pull request.

```
Show check status for pull request #456 in myorg/myrepo
```

**Returns**: Status checks, required checks, conclusion

### Commit Operations

#### Get Commit Details

Get information about a specific commit.

```
Show me commit abc123def from facebook/react
```

**Parameters**:
- Repository
- Commit SHA

**Returns**: Commit message, author, date, changed files, stats

#### List Commits

List commits in a repository or on a branch.

```
List the last 20 commits on the main branch of facebook/react
```

**Parameters**:
- Repository
- Branch/ref (optional)
- Path (optional, for specific file/directory)
- Since/until dates (optional)

**Returns**: Commit history

#### Compare Commits

Compare two commits or branches.

```
Compare main...develop in myorg/myrepo
```

**Parameters**:
- Repository
- Base (commit/branch)
- Head (commit/branch)

**Returns**: Diff, changed files, commit list

### Release Management

#### List Releases

Get releases for a repository.

```
List all releases for facebook/react
```

**Returns**: Release tags, names, published dates, assets

#### Get Release Details

Get information about a specific release.

```
Show me release v18.0.0 from facebook/react
```

**Returns**: Release notes, assets, download counts

#### Create Release

Create a new release.

```
Create a release in myorg/myrepo:
Tag: v1.2.0
Name: Version 1.2.0
Body: Release notes here...
Draft: false
Prerelease: false
```

**Parameters**:
- Repository
- Tag name
- Release name
- Body (release notes)
- Draft (optional)
- Prerelease (optional)
- Target commitish (optional)

### Workflow and Actions

#### List Workflow Runs

Get workflow run history.

```
List recent workflow runs for facebook/react
```

**Parameters**:
- Repository
- Workflow (optional, specific workflow file)
- Branch (optional)
- Status (optional)

**Returns**: Workflow run details, status, conclusions

#### Get Workflow Run Details

Get detailed information about a workflow run.

```
Show me workflow run #12345 from myorg/myrepo
```

**Returns**: Jobs, steps, logs, artifacts

#### Trigger Workflow

Trigger a workflow dispatch event.

```
Trigger the deploy workflow in myorg/myrepo with inputs:
environment: production
version: v1.2.0
```

**Parameters**:
- Repository
- Workflow ID or filename
- Ref (branch/tag)
- Inputs (optional)

**Requires**: `workflow` scope in token

### User and Organization

#### Get User Information

Get information about a user.

```
Show me the GitHub profile for @octocat
```

**Returns**: Name, bio, location, company, blog, public repos

#### List User Repositories

List repositories for a user.

```
List all repositories for @octocat
```

**Parameters**:
- Username
- Type (all, owner, member)
- Sort (created, updated, pushed, full_name)

**Returns**: Repository list

#### Get Organization Information

Get information about an organization.

```
Show me information about the facebook organization
```

**Returns**: Org details, description, location, public repos

#### List Organization Repositories

List repositories for an organization.

```
List all repositories for the facebook organization
```

**Parameters**:
- Organization
- Type (all, public, private, forks, sources, member)

**Returns**: Repository list

### Search Operations

#### Search Code

Search for code across GitHub.

```
Search for "authentication" in JavaScript files across myorg repositories
```

**Parameters**:
- Query
- Filters (language, repo, user, org, path)

**Returns**: Code matches with context

#### Search Commits

Search commit messages.

```
Search for commits mentioning "fix bug" in myorg/myrepo
```

**Parameters**:
- Query
- Repository (optional)
- Author (optional)

**Returns**: Matching commits

#### Search Users

Search for GitHub users.

```
Search for users with "machine learning" in their profile
```

**Parameters**:
- Query
- Filters (location, language, followers)

**Returns**: User profiles

## Best Practices

### Security

1. **Never Commit Tokens**: Add to `.gitignore`
   ```bash
   # .gitignore
   .config/github/
   *.token
   settings.json  # If it contains tokens
   ```

2. **Use Fine-Grained Tokens**: When available, use fine-grained tokens with specific repository access

3. **Rotate Tokens Regularly**: Set expiration dates and rotate before expiry

4. **Minimum Permissions**: Only grant necessary scopes
   - Read-only operations: `repo:status`, `public_repo`
   - Full access: `repo`
   - Organizations: `read:org` only if needed

5. **Secure Storage**: Use encrypted storage for tokens
   ```bash
   # macOS Keychain
   security add-generic-password -a "github-token" -s "claude-code" -w "ghp_token"

   # Retrieve
   security find-generic-password -a "github-token" -s "claude-code" -w
   ```

### Performance

1. **Use Pagination**: For large result sets
   ```
   Get the first 100 issues from myorg/myrepo
   ```

2. **Filter Aggressively**: Reduce API calls
   ```
   List open PRs with label "priority-high" assigned to @username
   ```

3. **Cache Results**: When appropriate, ask Claude to remember context
   ```
   Get all open PRs and remember them for the next questions
   ```

### Code Review Workflow

1. **Comprehensive Reviews**:
   ```
   Review PR #456 in myorg/myrepo:
   1. Get PR details and description
   2. Check CI/CD status
   3. Get the full diff
   4. Analyze code changes
   5. Check for potential issues
   6. Submit review with comments
   ```

2. **Review Checklist**:
   - Code quality and style
   - Test coverage
   - Documentation updates
   - Breaking changes
   - Security concerns
   - Performance implications

### Issue Management

1. **Triage New Issues**:
   ```
   Get all new issues (created in last 24 hours) and:
   1. Categorize by type (bug, feature, question)
   2. Assign appropriate labels
   3. Assign to team members
   4. Set milestones if applicable
   ```

2. **Issue Templates**: Use consistent formatting
   ```
   Create an issue with:

   ## Description
   [Clear description]

   ## Steps to Reproduce
   1. Step 1
   2. Step 2

   ## Expected Behavior
   [What should happen]

   ## Actual Behavior
   [What actually happens]

   ## Environment
   - OS:
   - Version:
   ```

### Pull Request Management

1. **PR Description Template**:
   ```
   ## Summary
   [Brief description]

   ## Changes
   - Change 1
   - Change 2

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests pass
   - [ ] Manual testing completed

   ## Related Issues
   Closes #123
   Relates to #456
   ```

2. **Automated PR Checks**:
   ```
   Before merging PR #456:
   1. Verify all checks pass
   2. Ensure required reviews are approved
   3. Check for merge conflicts
   4. Verify tests are up to date
   5. Confirm changelog is updated
   ```

## Common Workflows

### Daily Standup Preparation

```
Generate my daily standup report:
1. List PRs I created that are still open
2. List PRs I reviewed yesterday
3. List issues assigned to me
4. List commits I made yesterday
5. Summarize my activity
```

### Release Process

```
Prepare release v1.2.0 for myorg/myrepo:
1. List all PRs merged since last release
2. Generate changelog from commit messages
3. Create release notes
4. Create git tag
5. Create GitHub release
6. Update version in package.json
```

### Bug Triage

```
Triage bugs in myorg/myrepo:
1. List all open issues with label "bug"
2. For each issue without "priority" label:
   - Analyze severity
   - Assign priority label
   - Assign to appropriate team member
3. Create summary report
```

### Code Review Sprint

```
Review all pending PRs in myorg/myrepo:
1. List all open PRs
2. For each PR:
   - Check if it has reviews
   - Check CI/CD status
   - Get diff size
   - Prioritize for review
3. Review top 3 priority PRs
```

### Repository Audit

```
Audit myorg/myrepo:
1. Check repository settings
2. List all branches
3. Find stale branches (no commits in 90 days)
4. List open PRs older than 30 days
5. Check security alerts
6. Verify branch protection rules
```

### Sprint Planning

```
Prepare sprint planning for myorg/myrepo:
1. List all issues in milestone "Sprint 12"
2. Categorize by label (feature, bug, tech-debt)
3. Get effort estimates from labels
4. Check team capacity
5. Generate sprint board
```

## Troubleshooting

### Authentication Errors

**Error**: `Bad credentials` or `401 Unauthorized`

**Solution**:
```bash
# Verify token
echo $GITHUB_TOKEN

# Check token scopes
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user

# Regenerate token if expired or invalid
```

**Error**: `Resource not accessible by integration`

**Solution**:
- Check token scopes include required permissions
- Verify repository access (public vs private)
- For organizations, check if SSO is required
- Ensure token is authorized for the organization

### Rate Limiting

**Error**: `API rate limit exceeded`

**Solution**:
- Check rate limit status:
  ```
  Check my GitHub API rate limit
  ```
- Authenticated requests have higher limits (5000/hour vs 60/hour)
- Use conditional requests with ETags
- Implement exponential backoff
- For organizations, consider GitHub Apps (higher limits)

### Permission Errors

**Error**: `404 Not Found` for private repository

**Solution**:
- Verify repository name is correct
- Check token has `repo` scope for private repos
- Confirm you have access to the repository
- For organization repos, check SSO authorization

**Error**: `403 Forbidden` on write operations

**Solution**:
- Verify token has write permissions
- Check branch protection rules
- Confirm you have write access to the repository
- Verify you're not trying to modify protected files

### Connection Issues

**Error**: `MCP server not responding`

**Solution**:
```bash
# Test npx installation
npx -y @modelcontextprotocol/server-github --version

# Check Node.js version
node --version  # Should be 16+

# Verify settings.json syntax
# Restart Claude Code

# Test GitHub API directly
curl https://api.github.com/user \
  -H "Authorization: token $GITHUB_TOKEN"
```

### Data Issues

**Issue**: Stale data or unexpected results

**Solution**:
- GitHub API may cache responses (60 seconds)
- Use conditional requests to check for updates
- Refresh specific resources if needed
- Check if you're looking at the correct branch/ref

## Advanced Usage

### Automated PR Workflow

```python
# Example: Automated PR creation from feature branch

1. Create feature branch from main
2. Make code changes (via Edit tool)
3. Commit changes locally
4. Push to GitHub
5. Create PR with template
6. Request reviewers based on code owners
7. Monitor CI/CD status
8. Auto-merge when approved and green
```

### Issue Automation

```python
# Example: Auto-label issues based on content

For each new issue:
1. Analyze title and body
2. Identify keywords (bug, feature, docs, etc.)
3. Apply appropriate labels
4. Set priority based on severity
5. Assign to appropriate team/person
6. Add to project board
7. Post welcome comment
```

### Release Automation

```python
# Example: Automated release notes

1. Get all commits since last release
2. Group by type (feat, fix, docs, etc.)
3. Extract PR numbers and link them
4. Generate changelog in markdown
5. Create GitHub release
6. Publish release notes
7. Notify team in Slack
```

### Multi-Repository Operations

```python
# Example: Update dependency across all repos

For each repository in organization:
1. Check if package.json exists
2. Read current dependency version
3. If outdated:
   - Create feature branch
   - Update package.json
   - Run tests
   - Create PR with changelog
   - Request review from maintainers
```

## Integration with CI/CD

### GitHub Actions Integration

Monitor and trigger workflows:

```
Check status of deploy workflow for myorg/myrepo
```

```
Trigger deployment to staging:
1. Verify main branch is green
2. Trigger deploy workflow with environment=staging
3. Monitor workflow progress
4. Report results
```

### Status Checks

Verify PR is ready to merge:

```
Check if PR #456 is ready to merge:
1. Get all required status checks
2. Verify all checks pass
3. Confirm required reviews approved
4. Check for merge conflicts
5. Verify branch is up to date
```

## Resources

- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub GraphQL API](https://docs.github.com/en/graphql)
- [GitHub Apps Documentation](https://docs.github.com/en/developers/apps)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
