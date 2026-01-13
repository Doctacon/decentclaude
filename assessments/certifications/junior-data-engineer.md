# Junior Data Engineer Certification

## Overview

The Junior Data Engineer certification validates foundational skills in data engineering with DecentClaude, dbt, and BigQuery.

**Target Audience**: Entry-level data engineers, analysts transitioning to engineering roles

**Estimated Time to Complete**: 15-20 hours (including study time)

## Prerequisites

- Basic SQL knowledge
- Familiarity with command line
- Access to BigQuery
- Completed environment setup

## Certification Requirements

To earn this certification, you must:

### 1. Complete Required Courses

- ✓ DecentClaude Fundamentals
- ✓ dbt Essentials
- ✓ BigQuery Basics

**Verification**: All course videos watched and exercises completed

### 2. Pass Required Quizzes

Must achieve 70% or higher on each:

- ✓ dbt Fundamentals Quiz (15 questions)
- ✓ BigQuery Basics Quiz (12 questions)
- ✓ Data Quality Basics Quiz (10 questions)

**Total Questions**: 37
**Pass Threshold**: 70% per quiz
**Attempts**: Unlimited

### 3. Complete Practical Exercises

Hands-on exercises to demonstrate proficiency:

#### Exercise 1: Create a Staging Model
**Time**: 30 minutes

Create a staging model that:
- References a source table
- Performs basic data cleaning
- Includes appropriate data types
- Has schema documentation
- Passes uniqueness and not_null tests

**Deliverables**:
- `models/staging/stg_your_table.sql`
- `models/staging/schema.yml` with tests
- Screenshot of successful `dbt run` and `dbt test`

#### Exercise 2: Build an Intermediate Model
**Time**: 45 minutes

Create an intermediate model that:
- Joins multiple staging models
- Calculates business metrics
- Uses CTEs for organization
- Includes comprehensive tests
- Is properly documented

**Deliverables**:
- `models/intermediate/int_your_model.sql`
- Updated `schema.yml`
- Test results showing all tests pass

#### Exercise 3: Implement Data Quality Checks
**Time**: 30 minutes

Write custom data quality checks:
- Create a Python quality check class
- Validate at least 2 quality dimensions
- Generate a quality report
- Document the checks

**Deliverables**:
- `scripts/checks/your_quality_check.py`
- Quality report output
- Documentation of checks

### 4. Complete Capstone Project

**Time**: 4-6 hours

Build a complete data pipeline:

**Scenario**: You're building analytics for an e-commerce platform.

**Requirements**:
1. Create 3 staging models (users, orders, products)
2. Build 2 intermediate models with business logic
3. Create 1 mart model for reporting
4. Add comprehensive tests
5. Include data quality checks
6. Document all models
7. Demonstrate the pipeline works end-to-end

**Deliverables**:
- Complete dbt project structure
- All models with tests
- Documentation (README + dbt docs)
- Quality check results
- Demo walkthrough (written or video)

**Evaluation Criteria**:
- Code quality (30%)
- Test coverage (25%)
- Documentation (20%)
- Functionality (25%)

### 5. Code Review

Your capstone project will be reviewed for:
- Best practices adherence
- Code organization
- SQL efficiency
- Test coverage
- Documentation quality

**Reviewers**: Senior data engineers or course instructors

## Scoring

### Component Weights

| Component | Weight | Min Score |
|-----------|--------|-----------|
| Quizzes | 30% | 70% |
| Exercises | 30% | 75% |
| Capstone Project | 40% | 75% |

### Grading Scale

- 90-100%: Distinction
- 80-89%: Merit
- 75-79%: Pass
- <75%: Not yet passed (retake required)

## Timeline

**Recommended Schedule**:

| Week | Activities | Hours |
|------|-----------|-------|
| 1 | Courses & Videos | 5-6 |
| 2 | Quizzes & Study | 3-4 |
| 3 | Practical Exercises | 3-4 |
| 4 | Capstone Project | 6-8 |
| 5 | Code Review & Revision | 2-3 |

**Total**: 4-5 weeks at 3-5 hours per week

## How to Enroll

```bash
# Register for certification
python assessments/scoring/enroll_certification.py junior-data-engineer

# Track your progress
python assessments/scoring/certification_status.py junior-data-engineer
```

## Certification Benefits

Upon completion, you will:

- Earn a verified digital certificate
- Demonstrate foundational data engineering competency
- Be listed in the team's certified engineers directory
- Qualify for junior data engineering assignments
- Have a portfolio of working data pipelines

## Certificate

Issued as:
- PDF certificate with unique ID
- Digital badge for LinkedIn
- Entry in certification registry

**Valid**: 2 years (recertification recommended)

## Study Resources

### Recommended Reading

- [Data Engineering Patterns](../../data-engineering-patterns.md)
- [Data Testing Patterns](../../data-testing-patterns.md)
- [Playbooks](../../playbooks.md)

### Practice Materials

- [Getting Started Tutorial](../../tutorials/getting-started/)
- [Example Models](../../examples/sql/)
- [Walkthroughs](../../walkthroughs/)

### Video Content

- All videos in "Junior Data Engineer Path"
- See [training/courses.yaml](../../training/courses.yaml)

## FAQs

### How long is the certification valid?

2 years. After that, recertification is recommended to stay current.

### Can I retake quizzes?

Yes, unlimited attempts on all quizzes.

### What if I fail the capstone project?

You'll receive detailed feedback and can revise and resubmit once.

### Is there a deadline?

No strict deadline, but we recommend completing within 6 weeks of starting.

### Can I get help during exercises?

You can reference documentation and tutorials, but must complete work independently.

### What happens after certification?

You'll be eligible for:
- More complex data engineering tasks
- Mentoring junior team members
- Pursuing advanced certification

## Contact

Questions about the certification program?

- Email: [certification-team@example.com]
- Slack: #certification-help
- Office hours: [Schedule]

## Version History

- v1.0.0 (2026-01-12): Initial certification program
