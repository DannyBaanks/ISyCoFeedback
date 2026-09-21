"""Small OpenAI-compatible chat-completions transport."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProviderError(RuntimeError):
    """Raised when a provider cannot return a valid repair response."""


class OpenAICompatibleProvider:
    def __init__(self, base_url: str, model: str, api_key: str, timeout_seconds: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def request(self, envelope: dict[str, object]) -> str:
        """Send a bounded envelope and return the provider's message content."""
        request = self.build_request(envelope)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise ProviderError(f"OpenAI-compatible request failed: {error}") from error
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ProviderError("provider response has no choices[0].message.content") from error

    def build_request(self, envelope: dict[str, object]) -> Request:
        """Build a request while keeping the API key in the header only."""
        payload = {"model": self.model, "messages": [{"role": "user", "content": json.dumps(envelope)}]}
        return Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
