"""
Tests for ARIA Tool Suite.
"""

import tempfile
from aria.tools.email_tools import EmailTools
from aria.tools.github_tools import GitHubTools
from aria.tools.memory_tools import MemoryTools
from aria.tools.code_tools import CodeTools


def test_email_tools_simulation():
    tools = EmailTools()
    unread = tools.email_list_unread(max_count=2)
    assert isinstance(unread, list)
    assert len(unread) > 0

    read_res = tools.email_read("101")
    assert "body" in read_res
    assert "<untrusted_external_content" in read_res["body"]

    draft = tools.email_draft_reply("101", "colleague@example.com", "Review", "Looks good!")
    assert draft["status"] == "ready_for_review"


def test_github_tools_simulation():
    gh = GitHubTools()
    issues = gh.gh_list_issues()
    assert isinstance(issues, list)
    assert len(issues) > 0

    issue = gh.gh_create_issue("Test Task", "Implement feature")
    assert issue["success"] is True

    review = gh.gh_review_pr(10)
    assert "diff_summary" in review


def test_memory_tools():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_name = tmp.name

    mem = MemoryTools(memory_file=tmp_name)
    store_res = mem.memory_store("user_timezone", "UTC+1", namespace="preferences")
    assert store_res["success"] is True

    items = mem.memory_retrieve("timezone", namespace="preferences")
    assert len(items) == 1
    assert items[0]["value"] == "UTC+1"


def test_code_tools():
    valid_code = "def add(a, b):\n    return a + b\nresult = add(2, 3)"
    lint = CodeTools.code_lint(valid_code)
    assert lint["valid"] is True

    exec_res = CodeTools.code_execute_sandbox(valid_code)
    assert exec_res["success"] is True
    assert exec_res["output"]["result"] == "5"

    # Test security violation in sandbox
    dangerous_code = "import os\nos.system('dir')"
    danger_res = CodeTools.code_execute_sandbox(dangerous_code)
    assert danger_res["success"] is False
    assert "Security violation" in danger_res["error"]
