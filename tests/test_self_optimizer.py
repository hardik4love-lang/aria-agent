"""
Tests for SelfOptimizer.
"""

import os
import json
import tempfile
from aria.optimization.self_optimizer import SelfOptimizer


def test_self_optimizer():
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "audit_2026-10.jsonl")
        entries = [
            {"timestamp": "2026-10-15T12:00:00Z", "task_id": "t1", "event_type": "TASK_INTAKE", "details": {}},
            {"timestamp": "2026-10-15T12:01:00Z", "task_id": "t1", "event_type": "TASK_COMPLETED", "details": {}},
            {"timestamp": "2026-10-15T12:05:00Z", "task_id": "t2", "event_type": "TASK_INTAKE", "details": {}}
        ]
        with open(log_file, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")

        optimizer = SelfOptimizer(logs_dir=tmpdir)
        perf = optimizer.analyze_performance()

        assert perf["tasks_started"] == 2
        assert perf["tasks_completed"] == 1
        assert perf["completion_rate_pct"] == 50.0

        report = optimizer.generate_health_report()
        assert "Self-Optimization Report" in report
        assert "50.0%" in report
