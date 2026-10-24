"""
Code Execution and Linting Tools.
"""

import ast
from typing import Dict, Any


class CodeTools:
    """Provides safe code verification and execution tools."""

    @staticmethod
    def code_lint(code: str, language: str = "python") -> Dict[str, Any]:
        """Performs static syntax verification on generated code snippets."""
        if language.lower() == "python":
            try:
                ast.parse(code)
                return {"valid": True, "syntax_errors": []}
            except SyntaxError as e:
                return {
                    "valid": False,
                    "syntax_errors": [
                        {
                            "line": e.lineno,
                            "offset": e.offset,
                            "text": e.text,
                            "msg": e.msg
                        }
                    ]
                }
        return {"valid": True, "note": f"Linting not strictly enforced for {language}"}

    @staticmethod
    def code_execute_sandbox(code: str, language: str = "python") -> Dict[str, Any]:
        """
        Executes code in a restricted AST sandbox environment.
        High-risk tool requiring approval if modifying external state.
        """
        if language.lower() != "python":
            return {"success": False, "error": f"Execution of {language} is unsupported in local sandbox"}

        # Restricted execution environment
        safe_globals = {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "int": int,
                "float": float,
                "str": str,
                "list": list,
                "dict": dict,
                "set": set,
                "bool": bool,
                "min": min,
                "max": max,
                "sum": sum,
            }
        }
        safe_locals: Dict[str, Any] = {}

        try:
            # Check for forbidden modules and dunder inspection vectors
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in getattr(node, "names", []):
                        if alias.name in ["os", "subprocess", "sys", "shutil", "socket", "requests", "httpx", "importlib", "ctypes", "pickle"]:
                            return {
                                "success": False,
                                "error": f"Security violation: Import of '{alias.name}' is prohibited in standard sandbox."
                            }
                elif isinstance(node, ast.Attribute):
                    if node.attr in ["__class__", "__base__", "__bases__", "__subclasses__", "__mro__", "__builtins__", "__globals__", "__code__"]:
                        return {
                            "success": False,
                            "error": f"Security violation: Access to dunder inspection attribute '{node.attr}' is prohibited in sandbox."
                        }

            exec(code, safe_globals, safe_locals)
            # Filter non-serializable objects
            clean_results = {k: str(v) for k, v in safe_locals.items() if not k.startswith("__")}
            return {
                "success": True,
                "output": clean_results
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }
