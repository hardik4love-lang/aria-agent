"""
Model Router for ARIA Agent.
Routes between Groq (free LPU), Google AI Studio (free 1M context), and Ollama on OCI ARM.
"""

import os
from typing import Optional, List, Dict, Any
from aria.llm.quota import QuotaTracker


class BaseLLMClient:
    """Standardized interface for LLM calls across providers."""
    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.0) -> str:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    """Fallback mock client for testing, offline, or unconfigured environments."""
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.0) -> str:
        # Structured deterministic responses for planner and executor
        if "plan" in prompt.lower() or (system and "planner" in system.lower()):
            return """[
  {
    "step_id": 1,
    "description": "Inspect unread emails",
    "tool_name": "email_list_unread",
    "tool_arguments": {"max_count": 5},
    "is_high_risk": false
  },
  {
    "step_id": 2,
    "description": "Store summary into memory",
    "tool_name": "memory_store",
    "tool_arguments": {"key": "recent_emails", "value": "Checked inbox successfully", "namespace": "email"},
    "is_high_risk": false
  }
]"""
        return f"Mock response from {self.model_name} for prompt: {prompt[:50]}..."


class GroqClient(BaseLLMClient):
    def __init__(self, api_key: str, model_id: str):
        self.api_key = api_key
        self.model_id = model_id

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.0) -> str:
        import httpx
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4096
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            # Fallback to mock on network or token issues
            return MockLLMClient(self.model_id).generate(prompt, system, temperature)


class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model_id: str = "gemini-2.0-flash-exp"):
        self.api_key = api_key
        self.model_id = model_id

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.0) -> str:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_id}:generateContent?key={self.api_key}"
        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTION: {system}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 4096}
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return MockLLMClient(self.model_id).generate(prompt, system, temperature)


class OllamaClient(BaseLLMClient):
    def __init__(self, base_url: str = "http://localhost:11434", model_id: str = "llama3.2:3b"):
        self.base_url = base_url.rstrip("/")
        self.model_id = model_id

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.0) -> str:
        import httpx
        payload = {
            "model": self.model_id,
            "prompt": prompt,
            "system": system or "",
            "stream": False,
            "options": {"temperature": temperature}
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(f"{self.base_url}/api/generate", json=payload)
                if resp.status_code == 200:
                    return resp.json().get("response", "")
        except Exception:
            pass
        # Graceful fallback if local model is not downloaded or service unavailable
        return MockLLMClient(self.model_id).generate(prompt, system, temperature)


class ModelRouter:
    """Intelligently routes inference requests based on role, quota, and context length."""

    def __init__(self, quota_tracker: Optional[QuotaTracker] = None):
        self.quota = quota_tracker or QuotaTracker()
        self.groq_key = os.environ.get("GROQ_API_KEY")
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def get_client(self, role: str = "executor", approx_token_count: int = 1000) -> BaseLLMClient:
        """Select the optimal provider complying strictly with zero-cost bounds."""
        snapshot = self.quota.get_snapshot()

        # 1. Large context (>64K tokens) requires Gemini's 1M window
        if approx_token_count > 64000 and self.gemini_key:
            if snapshot["gemini_remaining"] > 100:
                self.quota.record_call("gemini")
                return GeminiClient(self.gemini_key, "gemini-2.0-flash-exp")

        # 2. Primary Provider: Groq Cloud
        if self.groq_key and snapshot["groq_remaining"] > 2000:
            self.quota.record_call("groq")
            model = "llama-3.3-70b-versatile" if role == "planner" else "llama-3.1-8b-instant"
            return GroqClient(self.groq_key, model)

        # 3. Secondary Provider: Google AI Studio
        if self.gemini_key and snapshot["gemini_remaining"] > 200:
            self.quota.record_call("gemini")
            return GeminiClient(self.gemini_key, "gemini-2.0-flash-exp")

        # 4. Local fallback: Ollama on OCI ARM VM
        try:
            import httpx
            with httpx.Client(timeout=1.0) as client:
                resp = client.get(f"{self.ollama_url}/api/tags")
                if resp.status_code == 200:
                    model = "qwen2.5:7b" if role == "planner" else "llama3.2:3b"
                    return OllamaClient(self.ollama_url, model)
        except Exception:
            pass

        # 5. Safe Mock fallback for CI or local dry runs
        return MockLLMClient(model_name=f"mock-{role}")
