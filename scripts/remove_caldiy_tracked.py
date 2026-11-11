#!/usr/bin/env python3
"""Remove cal.diy from tracked_prs in pr_review_fixer.py"""
import pathlib

fixer_path = pathlib.Path('src/aria/github/pr_review_fixer.py')
content = fixer_path.read_text(encoding='utf-8')

# Remove the calcom/cal.diy entry line
old_line = '            {"repo": "calcom/cal.diy", "pr_number": 30365, "title": "fix(settings): honor old primary email deletion (#30365)"}\n'
if old_line in content:
    # Fix the preceding line to not have trailing comma if this was last
    # Replace with closing bracket comment
    content = content.replace(
        '            {"repo": "tenstorrent/tt-metal", "pr_number": 62546, "title": "[Bug fix] allocator: preserve default L1 address alignment after explicit reservations (#62539)"},\n'
        '            {"repo": "calcom/cal.diy", "pr_number": 30365, "title": "fix(settings): honor old primary email deletion (#30365)"}\n',
        '            {"repo": "tenstorrent/tt-metal", "pr_number": 62546, "title": "[Bug fix] allocator: preserve default L1 address alignment after explicit reservations (#62539)"}\n'
        '            # calcom/cal.diy permanently excluded - PRs closed 2026-10-31 (spams CI emails)\n'
    )
    fixer_path.write_text(content, encoding='utf-8')
    print('SUCCESS: Removed cal.diy from tracked_prs list')
else:
    print('Pattern not found in file')
    # Show what's near line 811
    lines = content.split('\n')
    for i, line in enumerate(lines[808:815], 809):
        print(f'{i}: {repr(line)}')
