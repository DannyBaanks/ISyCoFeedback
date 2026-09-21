import json

from isycofeedback.providers.openai_compatible import OpenAICompatibleProvider


def test_openai_compatible_provider_builds_bounded_request_without_key_in_body() -> None:
    provider = OpenAICompatibleProvider("https://example.test/v1", "fake-model", "super-secret")

    request = provider.build_request({"failure": "TEST_FAILURE", "attempt": 1})

    assert request.full_url == "https://example.test/v1/chat/completions"
    assert json.loads(request.data)["model"] == "fake-model"
    assert "super-secret" not in request.data.decode()
    assert request.headers["Authorization"] == "Bearer super-secret"
