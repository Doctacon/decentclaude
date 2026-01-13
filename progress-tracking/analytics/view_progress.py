#!/usr/bin/env python3
"""
View your learning progress in DecentClaude.

This script displays your current skill levels, completed courses,
earned certifications, and recommended next steps.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)


class ProgressTracker:
    """Track and display user learning progress."""

    def __init__(self, user_profile_path: Optional[str] = None):
        self.user_profile_path = user_profile_path or self._get_default_profile_path()
        self.skill_map_path = Path(__file__).parent.parent / "skill-map.yaml"

        self.user_profile = self._load_user_profile()
        self.skill_map = self._load_skill_map()

    def _get_default_profile_path(self) -> str:
        """Get default user profile path."""
        home = Path.home()
        profile_dir = home / ".decentclaude"
        profile_dir.mkdir(exist_ok=True)
        return str(profile_dir / "user_profile.yaml")

    def _load_user_profile(self) -> Dict:
        """Load user profile from file."""
        if not os.path.exists(self.user_profile_path):
            return self._create_default_profile()

        with open(self.user_profile_path, 'r') as f:
            return yaml.safe_load(f) or self._create_default_profile()

    def _create_default_profile(self) -> Dict:
        """Create a default user profile."""
        return {
            'user_id': os.environ.get('USER', 'default'),
            'started_date': datetime.now().strftime('%Y-%m-%d'),
            'target_role': 'Junior Data Engineer',
            'learning_path': 'junior-data-engineer',
            'skills': {},
            'completed_activities': {
                'tutorials': [],
                'courses': [],
                'quizzes': [],
                'certifications': []
            }
        }

    def _load_skill_map(self) -> Dict:
        """Load skill map from YAML file."""
        if not self.skill_map_path.exists():
            print(f"Warning: Skill map not found at {self.skill_map_path}")
            return {'skill_domains': []}

        with open(self.skill_map_path, 'r') as f:
            return yaml.safe_load(f)

    def display_summary(self):
        """Display progress summary."""
        print("=" * 60)
        print("  DecentClaude Learning Progress")
        print("=" * 60)
        print()

        # User info
        print(f"User: {self.user_profile['user_id']}")
        print(f"Started: {self.user_profile['started_date']}")
        print(f"Target Role: {self.user_profile['target_role']}")
        print(f"Learning Path: {self.user_profile['learning_path']}")
        print()

        # Skills summary
        skills = self.user_profile.get('skills', {})
        if skills:
            print("📚 Skills Overview:")
            print()

            level_counts = {'novice': 0, 'beginner': 0, 'intermediate': 0, 'advanced': 0, 'expert': 0}
            for skill_data in skills.values():
                level = skill_data.get('level', 'novice')
                level_counts[level] = level_counts.get(level, 0) + 1

            total_skills = len(skills)
            print(f"  Total Skills: {total_skills}")
            for level, count in level_counts.items():
                if count > 0:
                    bar = "█" * min(count, 20)
                    print(f"  {level.capitalize():12}: {bar} ({count})")
            print()
        else:
            print("📚 No skills tracked yet. Complete tutorials to start!")
            print()

        # Completed activities
        activities = self.user_profile.get('completed_activities', {})
        print("✅ Completed Activities:")
        print()
        print(f"  Tutorials:      {len(activities.get('tutorials', []))}")
        print(f"  Courses:        {len(activities.get('courses', []))}")
        print(f"  Quizzes:        {len(activities.get('quizzes', []))}")
        print(f"  Certifications: {len(activities.get('certifications', []))}")
        print()

        # Certifications
        certs = activities.get('certifications', [])
        if certs:
            print("🏆 Earned Certifications:")
            for cert in certs:
                print(f"  • {cert}")
            print()

    def display_detailed_skills(self):
        """Display detailed skill breakdown."""
        print("=" * 60)
        print("  Detailed Skills Breakdown")
        print("=" * 60)
        print()

        skills = self.user_profile.get('skills', {})
        if not skills:
            print("No skills tracked yet.")
            return

        for skill_id, skill_data in skills.items():
            level = skill_data.get('level', 'novice')
            confidence = skill_data.get('confidence', 0)
            last_practiced = skill_data.get('last_practiced', 'Never')

            # Display skill
            skill_name = skill_id.replace('-', ' ').title()
            print(f"📌 {skill_name}")
            print(f"   Level: {level.capitalize()}")
            print(f"   Confidence: {confidence}/5 {'★' * confidence}{'☆' * (5 - confidence)}")
            print(f"   Last Practiced: {last_practiced}")

            # Evidence
            evidence = skill_data.get('evidence', [])
            if evidence:
                print("   Evidence:")
                for item in evidence[:3]:  # Show max 3 items
                    print(f"     • {item}")
            print()

    def display_recommendations(self):
        """Display recommended next steps."""
        print("=" * 60)
        print("  Recommended Next Steps")
        print("=" * 60)
        print()

        # For now, show simple recommendations
        # In a full implementation, this would analyze skill gaps and prerequisites

        skills = self.user_profile.get('skills', {})

        if not skills or len(skills) < 3:
            print("🎯 Getting Started:")
            print()
            print("  1. Complete the Getting Started tutorial")
            print("     Path: tutorials/getting-started/")
            print("     Time: 30 minutes")
            print()
            print("  2. Take the dbt Fundamentals quiz")
            print("     Path: assessments/quizzes/dbt-fundamentals.yaml")
            print("     Time: 15 minutes")
            print()
            print("  3. Watch: Introduction to DecentClaude")
            print("     See: training/courses.yaml")
            print("     Time: 10 minutes")
        else:
            print("🎯 Continue Your Journey:")
            print()
            print("  1. Work on Advanced dbt Patterns")
            print("     Recommended based on your dbt-basics progress")
            print()
            print("  2. Take BigQuery Optimization course")
            print("     Aligns with your learning path")
            print()
            print("  3. Practice with walkthroughs")
            print("     Build real-world skills")

        print()

    def save_profile(self):
        """Save user profile to file."""
        with open(self.user_profile_path, 'w') as f:
            yaml.dump(self.user_profile, f, default_flow_style=False)
        print(f"Progress saved to: {self.user_profile_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="View your DecentClaude learning progress"
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed skill breakdown'
    )
    parser.add_argument(
        '--area',
        type=str,
        help='Filter by specific skill area (e.g., dbt, bigquery)'
    )
    parser.add_argument(
        '--profile',
        type=str,
        help='Path to user profile file'
    )

    args = parser.parse_args()

    tracker = ProgressTracker(user_profile_path=args.profile)

    if args.detailed:
        tracker.display_detailed_skills()
    else:
        tracker.display_summary()

    tracker.display_recommendations()


if __name__ == "__main__":
    main()
