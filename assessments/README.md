# Assessments and Certifications

This directory contains quizzes, exams, and certification programs for validating knowledge and skills in DecentClaude and data engineering.

## Directory Structure

```
assessments/
├── README.md              # This file
├── quizzes/               # Knowledge check quizzes
├── certifications/        # Certification programs
└── scoring/               # Scoring rubrics and logic
```

## Assessment Types

### 1. Quizzes

Quick knowledge checks (5-15 questions) to validate understanding of specific topics.

- **Format**: YAML-based multiple choice and true/false
- **Scoring**: Pass/fail (70% threshold)
- **Attempts**: Unlimited
- **Time limit**: None

### 2. Certifications

Comprehensive assessments that combine:
- Multiple quizzes
- Practical exercises
- Project work
- Code reviews

**Available Certifications**:
- Junior Data Engineer
- Advanced Data Engineer
- Data Quality Specialist
- Production Operations Engineer

## Taking Assessments

### Run a Quiz

```bash
# Run a quiz interactively
python assessments/scoring/run_quiz.py quizzes/dbt-fundamentals.yaml

# View quiz results
python assessments/scoring/view_results.py
```

### Pursue a Certification

1. Review certification requirements
2. Complete prerequisite courses
3. Take required quizzes (must pass all)
4. Complete practical exercises
5. Submit capstone project
6. Receive certificate

```bash
# Check certification status
python assessments/scoring/certification_status.py junior-data-engineer

# List requirements
cat assessments/certifications/junior-data-engineer.md
```

## Quiz Format

Quizzes are defined in YAML:

```yaml
quiz_id: example-quiz
title: Example Quiz Title
description: Brief description
pass_threshold: 0.7
time_limit_minutes: null  # No time limit
questions:
  - id: q1
    type: multiple_choice
    question: "What is dbt?"
    options:
      - "A database"
      - "A transformation framework"  # correct
      - "A visualization tool"
      - "An ETL platform"
    correct_answer: 1  # 0-indexed
    explanation: "dbt is a transformation framework..."

  - id: q2
    type: true_false
    question: "Views are faster than tables in BigQuery"
    correct_answer: false
    explanation: "Tables store data, views compute at query time..."

  - id: q3
    type: multiple_select
    question: "Which are dbt materializations? (Select all)"
    options:
      - "View"
      - "Table"
      - "Incremental"
      - "Snapshot"
    correct_answers: [0, 1, 2]  # Multiple correct answers
    explanation: "Snapshot is for slowly changing dimensions..."
```

## Available Quizzes

### Beginner Level

- [dbt Fundamentals](quizzes/dbt-fundamentals.yaml)
- [BigQuery Basics](quizzes/bigquery-basics.yaml)
- [Data Quality Basics](quizzes/data-quality-basics.yaml)

### Intermediate Level

- [Advanced dbt](quizzes/advanced-dbt.yaml)
- [BigQuery Optimization](quizzes/bigquery-optimization.yaml)
- [Data Testing Strategies](quizzes/data-testing.yaml)

### Advanced Level

- [Production Engineering](quizzes/production-engineering.yaml)
- [Data Architecture](quizzes/data-architecture.yaml)
- [Incident Response](quizzes/incident-response.yaml)

## Certification Programs

### Junior Data Engineer Certification

**Requirements**:
- Complete Getting Started tutorial
- Complete dbt Essentials course
- Pass 3 quizzes:
  - dbt Fundamentals (70%+)
  - BigQuery Basics (70%+)
  - Data Quality Basics (70%+)
- Complete practical exercise
- Build a sample data pipeline

**Details**: [certifications/junior-data-engineer.md](certifications/junior-data-engineer.md)

### Advanced Data Engineer Certification

**Requirements**:
- Junior Data Engineer certification
- Complete 2 advanced courses
- Pass 4 quizzes (80%+)
- Complete capstone project
- Code review approved

**Details**: [certifications/advanced-data-engineer.md](certifications/advanced-data-engineer.md)

## Scoring System

### Quiz Scoring

- Each question worth equal points
- Partial credit for multiple select (proportional)
- Pass threshold: typically 70%
- Unlimited attempts allowed

### Certification Scoring

Weighted components:
- Quizzes: 40%
- Exercises: 30%
- Project: 30%

Minimum 75% overall to earn certification.

## Creating New Quizzes

### 1. Use the Template

```bash
cp assessments/quizzes/template.yaml assessments/quizzes/new-quiz.yaml
```

### 2. Follow Quiz Design Principles

- **Focus**: One topic per quiz
- **Length**: 10-15 questions
- **Difficulty**: Appropriate for level
- **Clarity**: Unambiguous questions
- **Educational**: Explanations for all answers

### 3. Test Your Quiz

```bash
# Validate quiz format
python assessments/scoring/validate_quiz.py quizzes/new-quiz.yaml

# Take the quiz yourself
python assessments/scoring/run_quiz.py quizzes/new-quiz.yaml --test-mode
```

### 4. Add to Index

Update this README and `quiz-index.yaml`.

## Progress Tracking

Quiz and certification progress is tracked in the user's profile:

```bash
# View your progress
python progress-tracking/analytics/view_progress.py --type assessments

# Export progress report
python progress-tracking/analytics/export_progress.py > my_progress.md
```

## Analytics

Track assessment performance:

```bash
# Quiz difficulty analysis
python assessments/scoring/analyze_difficulty.py

# Common wrong answers
python assessments/scoring/analyze_mistakes.py quiz-id

# Certification completion rates
python assessments/scoring/cert_completion_stats.py
```

## Best Practices

### For Quiz Takers

- Read questions carefully
- Don't rush (no time limit)
- Review explanations for wrong answers
- Retake quizzes to reinforce learning
- Practice with tutorials before quizzes

### For Quiz Authors

- Avoid trick questions
- Test knowledge, not memorization
- Provide detailed explanations
- Include real-world scenarios
- Review and update regularly

## Integration with Learning Paths

Quizzes are integrated with:

- **Tutorials**: Each tutorial has an associated quiz
- **Videos**: Video courses include quiz checkpoints
- **Certifications**: Multiple quizzes required
- **Walkthroughs**: Optional validation quizzes

## Feedback

Help improve assessments:

- Report unclear questions
- Suggest additional topics
- Submit new quiz questions
- Share certification experiences

## Related Resources

- [Tutorials](../tutorials/) - Interactive learning
- [Training Videos](../training/) - Video content
- [Progress Tracking](../progress-tracking/) - Track your learning
- [Walkthroughs](../walkthroughs/) - Practical task guides
