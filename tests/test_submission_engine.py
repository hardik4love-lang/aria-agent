"""
Tests for ARIA Bounty Submission Engine and Batch Dispatch.
"""

import pytest
from aria.bounties.submission_engine import BountySubmissionEngine

def test_job_id_normalization():
    assert BountySubmissionEngine.normalize_job_id("job-01") == "job-01"
    assert BountySubmissionEngine.normalize_job_id("job-1") == "job-01"
    assert BountySubmissionEngine.normalize_job_id("1") == "job-01"
    assert BountySubmissionEngine.normalize_job_id("/submit job-02") == "job-02"
    assert BountySubmissionEngine.normalize_job_id("/submit job-01 to /submit job-10") == "all"
    assert BountySubmissionEngine.normalize_job_id("job-01 to job-10") == "all"
    assert BountySubmissionEngine.normalize_job_id("all") == "all"
    assert BountySubmissionEngine.normalize_job_id("1-10") == "all"

def test_dispatch_all_submissions():
    res = BountySubmissionEngine.dispatch_all_submissions()
    assert res["success"] is True
    assert res["total_dispatched"] == 10
    assert "570" in res["total_value_usd"]
    assert len(res["results"]) == 10
