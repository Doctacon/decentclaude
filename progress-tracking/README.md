# Skill Progression Tracking

This directory contains the skill progression and learning analytics system for DecentClaude.

## Overview

Track your learning journey through:
- Skill acquisition and mastery
- Course and tutorial completion
- Quiz and certification progress
- Practical project work
- Learning analytics and insights

## Directory Structure

```
progress-tracking/
├── README.md                  # This file
├── skill-map.yaml             # Skill taxonomy and dependencies
├── progression-model.md       # How skills build on each other
├── user-profiles.yaml         # User learning profile template
└── analytics/                 # Progress analytics scripts
    ├── view_progress.py       # View your progress
    ├── generate_reports.py    # Generate progress reports
    └── analytics_dashboard.py # Visual dashboard
```

## Skill Taxonomy

Skills are organized hierarchically:

```
Data Engineering
├── SQL & Query Languages
│   ├── Basic SQL
│   ├── Advanced SQL
│   └── BigQuery Specific
├── Transformation Frameworks
│   ├── dbt Basics
│   ├── dbt Advanced
│   └── SQLMesh
├── Data Quality
│   ├── Testing Strategies
│   ├── Quality Frameworks
│   └── Monitoring
└── Operations
    ├── Deployment
    ├── Incident Response
    └── Performance Tuning
```

See [skill-map.yaml](skill-map.yaml) for complete taxonomy.

## Skill Levels

Each skill has 5 proficiency levels:

1. **Novice**: Awareness, basic understanding
2. **Beginner**: Can perform with guidance
3. **Intermediate**: Can perform independently
4. **Advanced**: Can handle complex scenarios
5. **Expert**: Can teach others, innovate

## Tracking Your Progress

### View Current Progress

```bash
# Overall progress summary
python progress-tracking/analytics/view_progress.py

# Progress in specific area
python progress-tracking/analytics/view_progress.py --area dbt

# Detailed skill breakdown
python progress-tracking/analytics/view_progress.py --detailed
```

### Update Progress

Progress is automatically updated when you:
- Complete tutorials
- Pass quizzes
- Finish exercises
- Earn certifications
- Complete walkthroughs

Manual updates:
```bash
# Mark a skill as learned
python progress-tracking/analytics/update_skill.py --skill "dbt-basics" --level intermediate

# Record completed activity
python progress-tracking/analytics/log_activity.py --type tutorial --id getting-started
```

## Learning Paths

Recommended skill progression paths:

### Path 1: Junior Data Engineer

```
Level 1 (Foundation):
  - Basic SQL → dbt Basics → BigQuery Basics

Level 2 (Core Skills):
  - Advanced SQL → dbt Testing → Data Quality Basics

Level 3 (Proficiency):
  - dbt Advanced → BigQuery Optimization → Production Basics
```

### Path 2: Analytics Engineer

```
Level 1 (Foundation):
  - Basic SQL → dbt Basics → Dimensional Modeling

Level 2 (Core Skills):
  - Advanced SQL → dbt Advanced → Metrics Framework

Level 3 (Proficiency):
  - Performance Tuning → Data Visualization → Stakeholder Management
```

### Path 3: Data Operations Engineer

```
Level 1 (Foundation):
  - Basic SQL → dbt Basics → Monitoring Basics

Level 2 (Core Skills):
  - Incident Response → Data Quality → Debugging

Level 3 (Proficiency):
  - Production Engineering → CI/CD → Scalability
```

## Progress Reports

### Generate Personal Report

```bash
# HTML report with visualizations
python progress-tracking/analytics/generate_reports.py --format html

# Markdown summary
python progress-tracking/analytics/generate_reports.py --format markdown

# Export to JSON
python progress-tracking/analytics/generate_reports.py --format json
```

Sample report includes:
- Skills mastered vs. in progress
- Completion percentages by area
- Recommended next steps
- Time spent learning
- Achievements and certifications

### Team Analytics (for managers)

```bash
# Team skill matrix
python progress-tracking/analytics/team_analytics.py --team data-engineering

# Skill gap analysis
python progress-tracking/analytics/skill_gaps.py

# Training recommendations
python progress-tracking/analytics/recommend_training.py
```

## Skill Dependencies

Skills have prerequisites:

```yaml
skill: dbt-incremental-models
prerequisites:
  - dbt-basics (intermediate)
  - dbt-testing (intermediate)
recommended:
  - bigquery-partitioning (beginner)
```

The system:
- Shows which skills you're ready for
- Recommends prerequisite learning
- Tracks dependency completion

## Achievements & Badges

Earn badges for milestones:

**Learning Badges**:
- 🎓 First Tutorial Complete
- 📚 Completed 5 Courses
- 🎯 100% Quiz Score
- 🏆 First Certification

**Skill Badges**:
- 🥉 Bronze: 5 skills at Intermediate+
- 🥈 Silver: 10 skills at Intermediate+
- 🥇 Gold: 15 skills at Advanced+
- 💎 Platinum: 5 skills at Expert

**Contribution Badges**:
- 📝 Tutorial Contributor
- 🐛 Bug Reporter
- 🎥 Video Creator
- 🤝 Peer Mentor

## Analytics Dashboard

Launch interactive dashboard:

```bash
python progress-tracking/analytics/analytics_dashboard.py
```

Dashboard shows:
- Skill radar chart
- Learning timeline
- Quiz performance trends
- Time investment by topic
- Comparison to learning path
- Recommended next actions

## User Profile

Your learning profile tracks:

```yaml
user_id: your-id
started_date: 2024-01-15
target_role: "Senior Data Engineer"
learning_path: "senior-data-engineer"

skills:
  dbt-basics:
    level: intermediate
    last_practiced: 2024-02-01
    confidence: 4/5
    evidence:
      - "Completed dbt-essentials course"
      - "Passed dbt-fundamentals quiz (85%)"
      - "Built 3 production models"

  bigquery-optimization:
    level: beginner
    last_practiced: 2024-01-28
    confidence: 3/5
    evidence:
      - "Completed partitioning tutorial"
      - "Optimized 2 slow queries"

completed_activities:
  tutorials:
    - getting-started (2024-01-15)
  courses:
    - dbt-essentials (2024-01-25)
  certifications:
    - junior-data-engineer (2024-02-15)

goals:
  short_term:
    - "Master incremental models"
    - "Complete BigQuery optimization course"
  long_term:
    - "Earn Advanced Data Engineer certification"
    - "Become dbt expert"
```

## Personalized Recommendations

Based on your profile, get recommendations:

```bash
python progress-tracking/analytics/recommend_next.py
```

Recommendations consider:
- Current skill levels
- Learning path
- Time available
- Prerequisites met
- Career goals

Example output:
```
Recommended Next Steps:

1. 🎯 Tutorial: Incremental Models (30 min)
   Why: You're ready for this based on your dbt-basics skill
   Impact: Unlocks advanced-dbt skill path

2. 📚 Course: BigQuery Optimization (3 hours)
   Why: Aligns with your role goal
   Impact: Critical for senior engineer path

3. ✅ Quiz: dbt Advanced (15 min)
   Why: Validate your recent learning
   Impact: Confidence boost, certification progress
```

## Time Tracking

Automatically track time spent:

```python
# Time is logged automatically when using:
# - Tutorials
# - Videos
# - Quizzes
# - Exercises

# View time investment
python progress-tracking/analytics/time_report.py

# Sample output:
# Total learning time: 42 hours
# - Tutorials: 12 hours
# - Videos: 18 hours
# - Exercises: 10 hours
# - Quizzes: 2 hours
#
# By topic:
# - dbt: 25 hours
# - BigQuery: 12 hours
# - Data Quality: 5 hours
```

## Skill Assessment

Self-assess your skills:

```bash
python progress-tracking/analytics/skill_assessment.py
```

Interactive assessment:
- Answer questions about skill usage
- Rate your confidence
- Provide evidence
- Get proficiency recommendation

## Progress Visualization

Generate visualizations:

```bash
# Skill radar chart
python progress-tracking/analytics/visualize.py --type radar

# Learning timeline
python progress-tracking/analytics/visualize.py --type timeline

# Skill tree with dependencies
python progress-tracking/analytics/visualize.py --type tree
```

## Integration with Other Systems

Progress tracking integrates with:

- **Tutorials**: Auto-marks completion
- **Quizzes**: Records scores and passes
- **Certifications**: Tracks requirements
- **Walkthroughs**: Logs completions
- **Videos**: Tracks watch progress

## Data Privacy

Your progress data:
- Stored locally (not cloud synced)
- Personal to you
- Can be exported/deleted anytime
- Aggregated anonymously for team analytics (opt-in)

## Best Practices

### Effective Progress Tracking

1. **Set clear goals**: Define what you want to achieve
2. **Regular practice**: Consistent > intensive
3. **Track honestly**: Self-assessment accuracy matters
4. **Review progress**: Weekly check-ins
5. **Celebrate milestones**: Acknowledge achievements

### Using Analytics

- Check progress weekly
- Update goals quarterly
- Export reports for performance reviews
- Share achievements with team
- Request feedback from mentors

## Troubleshooting

### Progress not updating?

```bash
# Verify activity logging
python progress-tracking/analytics/check_logs.py

# Manual sync
python progress-tracking/analytics/sync_progress.py
```

### Reset progress?

```bash
# Backup first
python progress-tracking/analytics/backup_progress.py

# Reset specific skill
python progress-tracking/analytics/reset_skill.py --skill dbt-basics

# Full reset (careful!)
python progress-tracking/analytics/reset_all.py --confirm
```

## Contributing

Help improve the progression system:

- Suggest new skills
- Refine skill definitions
- Improve recommendations
- Report inaccurate tracking
- Share your learning journey

## Related Resources

- [Skill Map](skill-map.yaml) - Complete skill taxonomy
- [Progression Model](progression-model.md) - How skills build
- [Tutorials](../tutorials/) - Practice and learn
- [Assessments](../assessments/) - Validate knowledge
- [Training Videos](../training/) - Video content
