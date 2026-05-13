# Blog Angle Tracker

Track and manage blog post ideas extracted from the content digest. Helps Justin manage which blog angles are pending, in progress, drafted, published, or skipped.

## Features

- **Initialize from digest**: Automatically extract all blog angles from the latest content digest
- **Status tracking**: Track angles through the writing pipeline (pending → in_progress → draft → published → skipped)
- **Priority filtering**: Focus on high-priority angles first
- **Status updates**: Quick commands to move angles through the pipeline
- **Reports**: Generate markdown or JSON reports of all angles
- **Manual entry**: Add custom blog angles not in the digest

## Installation

No installation required. Just run the script:

```bash
cd ~/.openclaw/workspace/tools/blog-angle-tracker
python3 main.py --help
```

## Usage

### Initialize tracking from latest digest

```bash
python3 main.py --init
```

This reads the latest `content-digest-YYYY-MM-DD.md` file and creates tracking entries for all blog angles.

### Generate status report

```bash
# Markdown report (default)
python3 main.py --report

# JSON report
python3 main.py --report --format json
```

The report includes:
- Summary by status and priority
- Pending high-priority angles (top 5)
- All angles grouped by status

### List all angles

```bash
# List all angles
python3 main.py --list

# Filter by status
python3 main.py --list --status pending

# Filter by priority
python3 main.py --list --priority high

# Combined filters
python3 main.py --list --status pending --priority high
```

### Update angle status

```bash
# Start working on an angle
python3 main.py --update github-agentic-workflows --status in_progress

# Mark as draft
python3 main.py --update github-agentic-workflows --status draft

# Publish
python3 main.py --update github-agentic-workflows --status published

# Skip (not pursuing)
python3 main.py --update github-agentic-workflows --status skipped

# Add notes when updating
python3 main.py --update github-agentic-workflows --status in_progress --notes "Found great examples in Marcus's latest learning"
```

### Add new angle manually

```bash
# Add new angle
python3 main.py --add "New AI Tool Discovered" --priority high

# Add with notes
python3 main.py --add "Breaking AI News" --priority high --notes "Check intel briefing 2026-05-13"
```

## Workflow

1. **Daily**: Run `--init` to sync with latest digest
2. **Morning**: Run `--list --status pending --priority high` to see what to work on
3. **During work**: Update status as you progress (`--update ... --status in_progress`)
4. **When done**: Update to `draft` or `published`
5. **End of day**: Run `--report` to see progress

## Data Storage

Tracking data is stored in `~/.openclaw/workspace/blog-angle-tracking.json`

Each angle tracks:
- Title and slug
- Priority (high/medium/low)
- Status (pending/in_progress/draft/published/skipped)
- Created and updated timestamps
- Source digest file
- Optional notes

## Integration with Content Pipeline

The blog-angle-tracker is designed to work with the content-pipeline workflow:

1. Content pipeline runs daily via cron
2. Extracts blog angles from Marcus/Galen's learnings
3. Creates `content-digest-YYYY-MM-DD.md`
4. Blog-angle-tracker reads this digest
5. Justin manages which angles to write
6. Status updates track progress

## Priority System

- **High**: Must write soon, timely topics
- **Medium**: Good content, write when possible
- **Low**: Evergreen topics, write when time permits

## Status System

- **Pending**: Not started, ready to pick up
- **In Progress**: Currently writing or researching
- **Draft**: First draft complete, needs review
- **Published**: Live on blog
- **Skipped**: Not pursuing (duplicate, outdated, not relevant)

## Example Report Output

```markdown
# Blog Angle Tracking Report

Generated: 2026-05-13 14:15:00 UTC

## Summary

- Total angles: 36

### By Status
- ⏳ pending: 28
- 🔄 in_progress: 3
- 📝 draft: 4
- ✅ published: 1
- ⏭️ skipped: 0

### By Priority
- 🔴 high: 15
- 🟡 medium: 12
- 🟢 low: 9

## Pending High Priority

### GitHub Agentic Workflows: AI-Driven Repository Automation or Recipe for Spam?
- **Created**: 2026-05-13
- **Slug**: `github-agentic-workflows-ai-driven-repository-automation-or-`
...
```

## License

MIT License - Part of OpenSeneca squad tools
