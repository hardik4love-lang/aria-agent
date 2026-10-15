"""
Autonomous Code Patcher and Bug-Fix Generator.
"""

import ast
from typing import Dict, Any, Optional
from aria.llm.router import ModelRouter
from aria.tools.code_tools import CodeTools


class AutonomousPatcher:
    """Generates and validates code patches before proposing PRs."""

    def __init__(self, router: Optional[ModelRouter] = None):
        self.router = router or ModelRouter()

    def generate_patch(self, original_code: str, issue_description: str, file_path: str) -> Dict[str, Any]:
        """Generates a proposed modification for a given file and issue."""
        client = self.router.get_client(role="planner")
        prompt = (
            f"Fix the following issue in `{file_path}`:\n"
            f"Issue: {issue_description}\n\n"
            f"Original code:\n```python\n{original_code}\n```\n\n"
            f"Output ONLY the complete updated code inside ```python ... ``` without explanation."
        )

        response = client.generate(prompt=prompt, system="You are an autonomous senior software engineer.")
        
        # Extract code block
        cleaned = response.strip()
        if "```python" in cleaned:
            cleaned = cleaned.split("```python", 1)[1].split("```", 1)[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```", 1)[1].split("```", 1)[0]

        updated_code = cleaned.strip()

        # Validate syntax
        lint_result = CodeTools.code_lint(updated_code, language="python" if file_path.endswith(".py") else "text")

        return {
            "file_path": file_path,
            "original_length": len(original_code),
            "updated_length": len(updated_code),
            "updated_code": updated_code,
            "is_valid_syntax": lint_result.get("valid", False),
            "lint_errors": lint_result.get("syntax_errors", [])
        }
