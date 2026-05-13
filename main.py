#!/usr/bin/env python3
"""
Blog Angle Tracker - Track and Manage Blog Post Ideas from Content Digest

Reads blog angles from the content digest and tracks their status as they move
through the writing pipeline (pending → in_progress → draft → published).

Usage:
    python3 main.py --report           # Generate status report
    python3 main.py --list              # List all angles with status
    python3 main.py --update <slug> --status <status>  # Update angle status
    python3 main.py --add <title> --priority <high|medium|low>  # Add new angle
    python3 main.py --init              # Initialize tracking from latest digest
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import glob

# Configuration
DEFAULT_LEARNINGS_DIR = Path.home() / ".openclaw" / "learnings"
DEFAULT_OUTPUT_DIR = Path.home() / ".openclaw" / "workspace" / "outputs"
TRACKING_FILE = Path.home() / ".openclaw" / "workspace" / "blog-angle-tracking.json"

# Valid statuses
VALID_STATUSES = ["pending", "in_progress", "draft", "published", "skipped"]

# Valid priorities
VALID_PRIORITIES = ["high", "medium", "low"]


def slugify_title(title: str) -> str:
    """Convert title to URL-friendly slug."""
    # Remove priority markers
    title = re.sub(r'\*\*+', '', title)
    # Convert to lowercase, replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    # Limit length
    return slug[:100]


def extract_blog_angles_from_digest(digest_path: Path) -> List[Dict[str, str]]:
    """Extract blog angles from a content digest file."""
    angles = []
    current_section = None

    with open(digest_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Detect section
            if line.startswith('## Blog Angles'):
                current_section = 'blog_angles'
                continue

            if not current_section:
                continue

            # Parse blog angle line
            # Format: "N. Priority — Title"
            match = re.match(r'^\d+\.\s+(\*\*)?(High|Medium|Low)\s*(\*\*)?\s*—\s+(.+)$', line)
            if match:
                priority = match.group(2).lower()
                title = match.group(4).strip()

                # Clean up title (remove bold markers if present)
                title = re.sub(r'\*\*+', '', title)

                angles.append({
                    'title': title,
                    'priority': priority,
                    'slug': slugify_title(title),
                    'source': digest_path.name
                })

    return angles


def load_tracking() -> Dict[str, Dict]:
    """Load tracking data from file."""
    if TRACKING_FILE.exists():
        try:
            with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load tracking file: {e}", file=sys.stderr)
            return {}
    return {}


def save_tracking(data: Dict[str, Dict]) -> None:
    """Save tracking data to file."""
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)


def get_latest_digest() -> Optional[Path]:
    """Get the latest content digest file."""
    digest_pattern = DEFAULT_OUTPUT_DIR / "content-digest-*.md"
    digest_files = sorted(glob.glob(str(digest_pattern)), reverse=True)

    if digest_files:
        return Path(digest_files[0])
    return None


def init_tracking() -> int:
    """Initialize tracking from the latest content digest."""
    digest = get_latest_digest()
    if not digest:
        print("Error: No content digest found. Run content pipeline first.", file=sys.stderr)
        return 1

    print(f"Reading blog angles from: {digest}")

    # Extract angles from digest
    angles = extract_blog_angles_from_digest(digest)
    print(f"Found {len(angles)} blog angles")

    # Load existing tracking
    tracking = load_tracking()

    # Add new angles
    added = 0
    for angle in angles:
        slug = angle['slug']
        if slug not in tracking:
            tracking[slug] = {
                'title': angle['title'],
                'priority': angle['priority'],
                'status': 'pending',
                'source_digest': angle['source'],
                'created_at': datetime.now().isoformat(),
                'updated_at': None,
                'notes': ''
            }
            added += 1
        else:
            # Update existing angle's priority if it changed
            if tracking[slug]['priority'] != angle['priority']:
                tracking[slug]['priority'] = angle['priority']
                print(f"  Updated priority for: {angle['title']}")

    # Save tracking
    save_tracking(tracking)

    print(f"✓ Added {added} new angles to tracking")
    print(f"  Total angles: {len(tracking)}")

    return 0


def generate_report(format: str = 'markdown') -> str:
    """Generate a status report of all blog angles."""
    tracking = load_tracking()

    if not tracking:
        return "# Blog Angle Tracking\n\nNo angles tracked. Run --init first.\n"

    # Sort by priority (high, medium, low) and then by creation date
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    sorted_angles = sorted(
        tracking.values(),
        key=lambda x: (priority_order.get(x['priority'], 99), x.get('created_at', ''))
    )

    if format == 'json':
        return json.dumps({
            'timestamp': datetime.now().isoformat(),
            'total_angles': len(tracking),
            'by_status': {status: sum(1 for a in tracking.values() if a['status'] == status) for status in VALID_STATUSES},
            'by_priority': {priority: sum(1 for a in tracking.values() if a['priority'] == priority) for priority in VALID_PRIORITIES},
            'angles': sorted_angles
        }, indent=2)

    # Markdown format
    output = []
    output.append("# Blog Angle Tracking Report")
    output.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    output.append(f"\n## Summary\n")
    output.append(f"- Total angles: {len(tracking)}")

    # By status
    output.append("\n### By Status\n")
    for status in VALID_STATUSES:
        count = sum(1 for a in tracking.values() if a['status'] == status)
        emoji = {'pending': '⏳', 'in_progress': '🔄', 'draft': '📝', 'published': '✅', 'skipped': '⏭️'}
        output.append(f"- {emoji[status]} {status}: {count}")

    # By priority
    output.append("\n### By Priority\n")
    for priority in VALID_PRIORITIES:
        count = sum(1 for a in tracking.values() if a['priority'] == priority)
        emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
        output.append(f"- {emoji[priority]} {priority}: {count}")

    # Pending high-priority angles (highlight for action)
    output.append("\n## Pending High Priority\n")
    high_pending = [a for a in sorted_angles if a['status'] == 'pending' and a['priority'] == 'high']
    if high_pending:
        for angle in high_pending[:5]:  # Show top 5
            created = angle.get('created_at', '')[:10] if angle.get('created_at') else 'unknown'
            output.append(f"\n### {angle['title']}")
            output.append(f"- **Created**: {created}")
            output.append(f"- **Slug**: `{angle['slug']}`")
            if angle.get('notes'):
                output.append(f"- **Notes**: {angle['notes']}")
        if len(high_pending) > 5:
            output.append(f"\n*...and {len(high_pending) - 5} more high-priority angles*")
    else:
        output.append("\nNo pending high-priority angles. Great job! 🎉")

    # All angles by status
    for status in VALID_STATUSES:
        angles_with_status = [a for a in sorted_angles if a['status'] == status]
        if not angles_with_status:
            continue

        status_emoji = {'pending': '⏳', 'in_progress': '🔄', 'draft': '📝', 'published': '✅', 'skipped': '⏭️'}
        output.append(f"\n## {status_emoji[status]} {status.replace('_', ' ').title()} ({len(angles_with_status)})\n")

        for angle in angles_with_status:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
            created = angle.get('created_at', '')[:10] if angle.get('created_at') else 'unknown'
            updated = angle.get('updated_at', '')[:10] if angle.get('updated_at') else ''

            output.append(f"### {priority_emoji[angle['priority']]} {angle['title']}")
            output.append(f"- **Slug**: `{angle['slug']}`")
            output.append(f"- **Created**: {created}")
            if updated:
                output.append(f"- **Updated**: {updated}")
            if angle.get('notes'):
                output.append(f"- **Notes**: {angle['notes']}")
            output.append("")

    return "\n".join(output)


def list_angles(status_filter: Optional[str] = None, priority_filter: Optional[str] = None) -> str:
    """List blog angles with optional filtering."""
    tracking = load_tracking()

    if not tracking:
        return "No angles tracked. Run --init first."

    # Filter angles
    filtered = tracking.values()
    if status_filter:
        filtered = [a for a in filtered if a['status'] == status_filter]
    if priority_filter:
        filtered = [a for a in filtered if a['priority'] == priority_filter]

    if not filtered:
        return f"No angles found matching filters (status={status_filter}, priority={priority_filter})."

    # Sort
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    filtered = sorted(
        filtered,
        key=lambda x: (priority_order.get(x['priority'], 99), x.get('created_at', ''))
    )

    # Format output
    output = []
    for angle in filtered:
        status_emoji = {'pending': '⏳', 'in_progress': '🔄', 'draft': '📝', 'published': '✅', 'skipped': '⏭️'}
        priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}

        output.append(f"{status_emoji[angle['status']]} {priority_emoji[angle['priority']]} {angle['title']}")
        output.append(f"  Slug: {angle['slug']}")
        output.append(f"  Status: {angle['status']} | Priority: {angle['priority']}")

    return "\n".join(output)


def update_angle_status(slug: str, status: str, notes: Optional[str] = None) -> int:
    """Update the status of a blog angle."""
    if status not in VALID_STATUSES:
        print(f"Error: Invalid status '{status}'. Valid statuses: {', '.join(VALID_STATUSES)}", file=sys.stderr)
        return 1

    tracking = load_tracking()

    if slug not in tracking:
        print(f"Error: Angle with slug '{slug}' not found. Run --list to see available angles.", file=sys.stderr)
        return 1

    # Update status
    tracking[slug]['status'] = status
    tracking[slug]['updated_at'] = datetime.now().isoformat()

    # Update notes if provided
    if notes:
        tracking[slug]['notes'] = notes

    # Save
    save_tracking(tracking)

    print(f"✓ Updated angle: {tracking[slug]['title']}")
    print(f"  Status: {status}")
    if notes:
        print(f"  Notes: {notes}")

    return 0


def add_angle(title: str, priority: str, notes: Optional[str] = None) -> int:
    """Add a new blog angle manually."""
    if priority not in VALID_PRIORITIES:
        print(f"Error: Invalid priority '{priority}'. Valid priorities: {', '.join(VALID_PRIORITIES)}", file=sys.stderr)
        return 1

    tracking = load_tracking()

    slug = slugify_title(title)

    if slug in tracking:
        print(f"Warning: Angle with slug '{slug}' already exists. Updating priority instead.", file=sys.stderr)
        tracking[slug]['priority'] = priority
        tracking[slug]['updated_at'] = datetime.now().isoformat()
        if notes:
            tracking[slug]['notes'] = notes
    else:
        tracking[slug] = {
            'title': title,
            'priority': priority,
            'status': 'pending',
            'source_digest': 'manual',
            'created_at': datetime.now().isoformat(),
            'updated_at': None,
            'notes': notes or ''
        }
        print(f"✓ Added new angle: {title}")

    save_tracking(tracking)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Track and manage blog post ideas from content digest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize tracking from latest digest
  python3 main.py --init

  # Generate status report
  python3 main.py --report

  # List all angles
  python3 main.py --list

  # Update angle status
  python3 main.py --update github-agentic-workflows --status in_progress

  # Add new angle manually
  python3 main.py --add "New AI Tool Discovered" --priority high --notes "Found in intel briefing"

  # List only pending high-priority angles
  python3 main.py --list --status pending --priority high
        """
    )

    parser.add_argument("--init", action="store_true", help="Initialize tracking from latest content digest")
    parser.add_argument("--report", action="store_true", help="Generate status report")
    parser.add_argument("--list", action="store_true", help="List all angles")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format for report")
    parser.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")
    parser.add_argument("--priority", choices=VALID_PRIORITIES, help="Filter by priority")
    parser.add_argument("--update", metavar="SLUG", help="Update angle status by slug")
    parser.add_argument("--add", metavar="TITLE", help="Add new angle manually")
    parser.add_argument("--notes", metavar="NOTES", help="Add notes to an angle")

    args = parser.parse_args()

    # Handle actions
    if args.init:
        return init_tracking()
    elif args.report:
        print(generate_report(format=args.format))
        return 0
    elif args.list:
        print(list_angles(status_filter=args.status, priority_filter=args.priority))
        return 0
    elif args.update:
        if not args.status:
            parser.error("--update requires --status")
        return update_angle_status(args.update, args.status, args.notes)
    elif args.add:
        if not args.priority:
            parser.error("--add requires --priority")
        return add_angle(args.add, args.priority, args.notes)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
