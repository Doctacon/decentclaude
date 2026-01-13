# DecentClaude Mayor Rig - Skills and Subagents

Complete collection of 22 production-ready Skills and 3 specialized Subagents for the decentclaude repository.

## Skills (22)

### Debugging and Development
1. **troubleshoot** - Systematic debugging workflow with hypothesis testing
2. **iterate** - Build → Test → Review → Refine development cycle
3. **refactor** - Code improvement while preserving behavior
4. **fix-ci** - CI/CD troubleshooting for GitHub Actions, GitLab CI, Jenkins

### Code Quality
5. **review-code** - Comprehensive code review with severity levels
6. **add-tests** - Test generation and coverage improvement
7. **generate-tests** - Automated test suite generation with edge cases
8. **explain-code** - Complex code analysis and documentation

### Documentation
9. **document** - README, API docs, architecture diagrams, runbooks

### Security and Performance
10. **security-audit** - Security vulnerability scanning and remediation
11. **optimize** - Performance profiling and optimization
12. **add-monitoring** - Logging, metrics, tracing, and alerts

### Architecture and Design
13. **plan-architecture** - System design with ADRs and diagrams
14. **design-api** - REST/GraphQL/gRPC API design with OpenAPI

### Infrastructure and Operations
15. **migrate** - Database, framework, and infrastructure migrations
16. **containerize** - Docker optimization with multi-stage builds
17. **setup-iac** - Terraform/Pulumi/CDK infrastructure as code
18. **triage-incident** - Incident response and mitigation

### Frontend and Accessibility
19. **build-component** - React/Vue/Svelte component development
20. **make-accessible** - WCAG compliance and accessibility improvements

### Environment and Dependencies
21. **update-deps** - Dependency update workflow with breaking change detection
22. **setup-env** - Environment variable management and setup

## Subagents (3)

### 1. debugging-expert
- **Model**: Sonnet with extended thinking
- **Expertise**: Stack traces, logs, bug reproduction, hypothesis testing
- **Tools**: Read, Grep, Glob, Bash

### 2. performance-expert
- **Model**: Sonnet
- **Expertise**: Profiling, benchmarking, bottleneck identification, optimization
- **Tools**: Read, Grep, Bash

### 3. architecture-reviewer
- **Model**: Sonnet with extended thinking
- **Expertise**: System design, scalability, reliability, ADR review, cost optimization
- **Tools**: Read, Grep, Glob

## Usage

### Invoking Skills

Skills are invoked through the Claude Code interface:

```
Use the /troubleshoot skill to debug this issue
Use /review-code to check this PR
Use /optimize to improve performance
```

### Invoking Subagents

Subagents are specialized agents that can be called for expert analysis:

```
Call the debugging-expert to analyze this stack trace
Ask the performance-expert about query optimization
Have the architecture-reviewer evaluate this design
```

## File Structure

```
.claude/
├── skills/
│   ├── troubleshoot/SKILL.md
│   ├── iterate/SKILL.md
│   ├── review-code/SKILL.md
│   ├── refactor/SKILL.md
│   ├── add-tests/SKILL.md
│   ├── document/SKILL.md
│   ├── security-audit/SKILL.md
│   ├── fix-ci/SKILL.md
│   ├── triage-incident/SKILL.md
│   ├── optimize/SKILL.md
│   ├── plan-architecture/SKILL.md
│   ├── design-api/SKILL.md
│   ├── migrate/SKILL.md
│   ├── add-monitoring/SKILL.md
│   ├── build-component/SKILL.md
│   ├── update-deps/SKILL.md
│   ├── explain-code/SKILL.md
│   ├── generate-tests/SKILL.md
│   ├── containerize/SKILL.md
│   ├── setup-iac/SKILL.md
│   ├── make-accessible/SKILL.md
│   └── setup-env/SKILL.md
└── agents/
    ├── debugging-expert.md
    ├── performance-expert.md
    └── architecture-reviewer.md
```

## Features

All skills include:
- Proper frontmatter with name, description, and allowed-tools
- Step-by-step workflows
- Code examples for multiple languages
- Best practices and anti-patterns
- Integration with relevant tools
- Production-ready patterns

All subagents include:
- Specialized expertise areas
- Systematic approaches
- Output format templates
- Collaboration guidelines
- Extended thinking support (where appropriate)

## Integration

These skills and subagents integrate with:
- **Version control**: Git workflows and best practices
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **Testing frameworks**: pytest, Jest, Go test
- **Monitoring**: Datadog, Prometheus, Grafana, Sentry
- **Cloud platforms**: AWS, GCP, Azure
- **Infrastructure**: Docker, Kubernetes, Terraform

## Best Practices

- Skills are task-oriented workflows
- Subagents provide expert analysis and review
- Use skills for systematic execution
- Use subagents for complex analysis and decision-making
- Combine skills and subagents for comprehensive solutions

## Examples

**Debugging workflow**:
1. Use `/troubleshoot` skill for systematic debugging
2. Call `debugging-expert` for complex stack trace analysis
3. Use `/fix-ci` if issue is in CI/CD pipeline

**Performance optimization**:
1. Use `/optimize` skill for profiling workflow
2. Call `performance-expert` for bottleneck analysis
3. Use `/add-monitoring` to track improvements

**Architecture review**:
1. Use `/plan-architecture` for design
2. Call `architecture-reviewer` for expert review
3. Use `/document` to create ADRs and diagrams

**Feature development**:
1. Use `/iterate` for TDD development
2. Use `/add-tests` to ensure coverage
3. Use `/review-code` before merge
4. Use `/document` to update documentation

## Maintenance

- Skills are self-contained and independently maintained
- Subagents leverage extended thinking for complex analysis
- All tools follow Claude Code best practices
- Regular updates based on evolving patterns and tools
