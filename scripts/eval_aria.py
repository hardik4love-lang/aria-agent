#!/usr/bin/env python3
"""ARIA Live Evaluation Script"""
import json, pathlib, time, os

base = pathlib.Path('D:/aria-agent')

# Submissions log
s = base / 'data/submissions_log.jsonl'
if s.exists():
    lines = [l for l in s.read_text(encoding='utf-8').strip().split('\n') if l.strip()]
    recent = [json.loads(l) for l in lines[-10:]]
    success = [r for r in recent if r.get('status') == 'SUCCESS']
    failed  = [r for r in recent if r.get('status') != 'SUCCESS']
    print(f"SUBMISSIONS (last 10): {len(success)} success / {len(failed)} failed")
    for r in recent[-5:]:
        print(f"  [{r.get('status','?')}] {r.get('repo','?')}#{r.get('pr_number','?')} @ {r.get('timestamp','?')[:16]}")
else:
    print("SUBMISSIONS: no log found")

# Healing log
h = base / 'data/pr_healing_log.jsonl'
if h.exists():
    lines = [l for l in h.read_text(encoding='utf-8').strip().split('\n') if l.strip()]
    healed = [json.loads(l) for l in lines]
    ok  = [r for r in healed if r.get('status') == 'HEALED']
    skp = [r for r in healed if 'SKIP' in r.get('status','')]
    fail= [r for r in healed if 'FAIL' in r.get('status','')]
    print(f"\nPR HEALING (total): {len(ok)} healed / {len(skp)} skipped / {len(fail)} failed")
else:
    print("\nPR HEALING: no log")

# Solved issues
si = base / 'data/solved_issue_ids.json'
if si.exists():
    ids = json.loads(si.read_text())
    print(f"\nSOLVED ISSUE IDs in memory: {len(ids)}")

# Pending queue
pq = base / 'data/pending_queue.json'
if pq.exists():
    q = json.loads(pq.read_text())
    print(f"PENDING QUEUE: {len(q)} issues queued")
    for item in q[:3]:
        print(f"  - {item.get('repo','?')}#{item.get('number','?')} ${item.get('bounty_usd',0)}")

# Vector brain
vb = base / 'data/vector_brain_fallback.json'
vbdir = base / 'data/vector_brain'
if vb.exists():
    data = json.loads(vb.read_text())
    print(f"\nVECTOR BRAIN (fallback JSON): {len(data)} entries")
elif vbdir.exists():
    print(f"\nVECTOR BRAIN (ChromaDB dir): exists")
else:
    print("\nVECTOR BRAIN: NOT INITIALIZED (no data yet)")

# Cooldown tracker
cd = base / 'state/pr_cooldown_tracker.json'
if cd.exists():
    data = json.loads(cd.read_text())
    print(f"\nCOOLDOWN TRACKER: {len(data)} PRs tracked")

print("\n=== EVAL COMPLETE ===")
