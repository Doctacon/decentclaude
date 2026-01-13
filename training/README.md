# Video Training Library

This directory contains the metadata and organization system for DecentClaude video training content.

## Overview

The video training library provides structured video content for learning DecentClaude, dbt, BigQuery, and data engineering best practices.

## Directory Structure

```
training/
├── README.md              # This file
├── manifest.json          # Video library index
├── courses.yaml           # Course definitions and structure
├── video-index.md         # Searchable catalog
└── transcripts/           # Video transcripts for search
```

## Available Courses

Courses are organized by skill level and topic. See `courses.yaml` for the complete curriculum.

### Beginner Track

1. **DecentClaude Fundamentals**
   - Introduction to DecentClaude
   - Environment setup
   - Your first transformation

2. **dbt Essentials**
   - dbt basics
   - Models and tests
   - Documentation

3. **BigQuery Basics**
   - SQL fundamentals
   - BigQuery console
   - Cost management basics

### Intermediate Track

4. **Advanced dbt Patterns**
   - Incremental models
   - Snapshots
   - Macros and packages

5. **BigQuery Optimization**
   - Partitioning and clustering
   - Query optimization
   - Cost reduction strategies

6. **Data Quality Engineering**
   - Testing strategies
   - Custom quality checks
   - Monitoring and alerting

### Advanced Track

7. **Production Data Engineering**
   - CI/CD for data
   - Incident response
   - Performance tuning

8. **Scalable Data Architecture**
   - Multi-project setups
   - Data mesh patterns
   - Enterprise practices

## Using the Training Library

### Search for Videos

```bash
# Search by topic
grep -i "partitioning" training/video-index.md

# Search transcripts
grep -ri "incremental model" training/transcripts/

# Find videos by course
yq '.courses[] | select(.id == "dbt-essentials") | .videos[]' training/courses.yaml
```

### Track Your Progress

See [Progress Tracking](../progress-tracking/README.md) for how to track video completion.

### Access Videos

Videos are hosted on [platform] and accessible with your company credentials.

**Access URL**: [To be configured]

## Video Metadata Format

Each video in the library has metadata:

```yaml
id: unique-video-id
title: Video Title
course: course-id
duration_minutes: 15
level: beginner|intermediate|advanced
topics:
  - topic1
  - topic2
prerequisites:
  - prerequisite-video-id
related_resources:
  - path/to/doc.md
  - path/to/tutorial
```

## Creating New Training Videos

### Recording Guidelines

1. **Length**: 5-15 minutes per video
2. **Focus**: One concept per video
3. **Format**: Screen recording + narration
4. **Quality**: 1080p minimum, clear audio

### Required Content

- Introduction (30 seconds)
- Learning objectives (1 minute)
- Main content (10-12 minutes)
- Summary and next steps (1-2 minutes)

### Adding to the Library

1. Record and edit video
2. Upload to video platform
3. Generate transcript
4. Add metadata to `manifest.json`
5. Update `courses.yaml`
6. Add entry to `video-index.md`
7. Save transcript to `transcripts/`

```bash
# Template for adding new video
cat >> training/manifest.json << EOF
  {
    "id": "new-video-id",
    "title": "Video Title",
    "url": "https://video-platform/new-video",
    "duration_minutes": 15,
    "level": "intermediate",
    "topics": ["topic1", "topic2"],
    "created_date": "2024-01-15",
    "updated_date": "2024-01-15"
  }
EOF
```

## Video Transcript Format

Transcripts should include:

- Timestamp markers every 30-60 seconds
- Speaker identification (if multiple)
- Code snippets in markdown code blocks
- Links to referenced resources

Example:
```
[00:00] Introduction
Welcome to this video on dbt incremental models...

[00:30] What are incremental models?
Incremental models are...

[01:15] Creating an incremental model
```sql
{{ config(materialized='incremental') }}
SELECT ...
```
...
```

## Playlists

Curated playlists for common learning paths:

- **New Hire Onboarding**: [video-id-1, video-id-2, ...]
- **dbt Certification Prep**: [video-id-3, video-id-4, ...]
- **BigQuery Optimization**: [video-id-5, video-id-6, ...]
- **Incident Response Training**: [video-id-7, video-id-8, ...]

See `courses.yaml` for complete playlist definitions.

## Integration with Assessments

Videos are linked to assessments:

- Watch video
- Complete quiz
- Earn certificate

See [Assessments](../assessments/README.md) for details.

## Analytics

Track video engagement:

```bash
# View completion rates
python progress-tracking/analytics/video_completion_stats.py

# Most watched videos
python progress-tracking/analytics/popular_videos.py
```

## Contributing

### Suggest New Videos

Submit a request:

```yaml
title: Proposed Video Title
topic: Topic area
level: Skill level
justification: Why this video is needed
outline: |
  - Point 1
  - Point 2
  - Point 3
```

### Improve Existing Videos

- Report issues with video quality
- Suggest content updates
- Submit corrected transcripts

## Related Resources

- [Tutorials](../tutorials/) - Interactive text-based learning
- [Walkthroughs](../walkthroughs/) - Step-by-step task guides
- [Documentation](../docs/) - Reference materials
- [Assessments](../assessments/) - Quizzes and certifications
