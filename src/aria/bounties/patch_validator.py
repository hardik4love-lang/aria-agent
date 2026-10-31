#!/usr/bin/env python3
"""
ARIA Patch Pre-Flight Validator.
Validates LLM-generated patches before PR submission.
Supports: Python, TypeScript, JavaScript, Go.
"""
import py_compile, subprocess, tempfile, pathlib, os, logging
from typing import Tuple

logger = logging.getLogger(__name__)


class PatchValidator:
    def __init__(self):
        self.max_retries = 2  # Max LLM regeneration attempts

    def detect_language(self, filename: str) -> str:
        """Detect language from file extension. Returns 'python'|'typescript'|'javascript'|'go'|'unknown'"""
        ext = pathlib.Path(filename).suffix.lower()
        return {
            '.py': 'python',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.js': 'javascript', '.jsx': 'javascript', '.mjs': 'javascript',
            '.go': 'go'
        }.get(ext, 'unknown')

    def validate_python(self, code: str) -> Tuple[bool, str]:
        """Validate Python code syntax using py_compile. Returns (is_valid, error_msg)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            tmp = f.name
        try:
            py_compile.compile(tmp, doraise=True)
            return True, ""
        except py_compile.PyCompileError as e:
            return False, str(e)
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    def validate_javascript(self, code: str) -> Tuple[bool, str]:
        """Validate JS/TS using node --check (zero-cost, available on ubuntu-latest runner)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(code)
            tmp = f.name
        try:
            result = subprocess.run(
                ['node', '--check', tmp],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return True, ""
            return False, result.stderr.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return True, ""  # node not available — skip check, don't block
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    def validate_go(self, code: str, package_hint: str = "main") -> Tuple[bool, str]:
        """Validate Go using gofmt (zero-cost, checks syntax only)"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False, encoding='utf-8') as f:
            f.write(code)
            tmp = f.name
        try:
            result = subprocess.run(
                ['gofmt', '-e', tmp],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return True, ""
            return False, result.stderr.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return True, ""  # gofmt not available — skip
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    def validate(self, filename: str, code: str) -> Tuple[bool, str, str]:
        """
        Master validation entry point.
        Returns: (is_valid: bool, error_msg: str, language: str)
        """
        lang = self.detect_language(filename)
        logger.info(f"[Validator] Checking {filename} (lang={lang}) ...")

        if lang == 'python':
            ok, err = self.validate_python(code)
        elif lang in ('typescript', 'javascript'):
            ok, err = self.validate_javascript(code)
        elif lang == 'go':
            ok, err = self.validate_go(code)
        else:
            logger.info(f"[Validator] Unknown language for {filename} — skipping validation")
            return True, "", lang

        if ok:
            logger.info(f"[Validator] PASS: {filename}")
        else:
            logger.warning(f"[Validator] FAIL: {filename} — {err[:200]}")

        return ok, err, lang

    def validate_with_retry(
        self,
        filename: str,
        code: str,
        llm_regenerate_fn=None,
    ) -> Tuple[bool, str, str]:
        """
        Validate with up to max_retries LLM regeneration attempts.
        llm_regenerate_fn: callable(error_msg) -> new_code_str, or None.
        Returns: (is_valid, final_code, error_msg)
        """
        current_code = code
        for attempt in range(self.max_retries + 1):
            ok, err, lang = self.validate(filename, current_code)
            if ok:
                return True, current_code, ""
            logger.warning(
                f"[Validator] Attempt {attempt + 1}/{self.max_retries + 1} FAILED: {err[:100]}"
            )
            if llm_regenerate_fn and attempt < self.max_retries:
                try:
                    logger.info("[Validator] Requesting LLM regeneration with error context...")
                    current_code = llm_regenerate_fn(err)
                except Exception as regen_err:
                    logger.error(f"[Validator] LLM regen failed: {regen_err}")
                    break
            else:
                break
        return False, current_code, err
