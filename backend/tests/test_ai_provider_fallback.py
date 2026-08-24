from app.ai.provider import AIProviderError, FallbackAIProvider


def test_fallback_stays_inside_gemini_before_other_providers(monkeypatch):
    provider = FallbackAIProvider()
    monkeypatch.setattr(provider.settings, "gemini_api_key", "g-key")
    monkeypatch.setattr(provider.settings, "gemini_model", "gemini-primary")
    monkeypatch.setattr(provider.settings, "gemini_fallback_models", "gemini-backup-1,gemini-backup-2")
    monkeypatch.setattr(provider.settings, "groq_api_key", "groq-key")
    monkeypatch.setattr(provider.settings, "ai_provider_order", "gemini,groq")

    def gemini_side_effect(*, model: str, **kwargs):
        if model == "gemini-primary":
            raise AIProviderError("primary down")
        return f"ok:{model}"

    def groq_never_called(**kwargs):
        raise AssertionError("groq should not be called when gemini backup succeeds")

    monkeypatch.setattr(provider, "_gemini_generate", gemini_side_effect)
    monkeypatch.setattr(provider, "_groq_generate", groq_never_called)

    response = provider.generate("hello")
    assert response.provider == "gemini"
    assert response.model == "gemini-backup-1"
    assert response.attempts == ["gemini:gemini-primary", "gemini:gemini-backup-1"]


def test_fallback_moves_to_next_provider_when_all_gemini_models_fail(monkeypatch):
    provider = FallbackAIProvider()
    monkeypatch.setattr(provider.settings, "gemini_api_key", "g-key")
    monkeypatch.setattr(provider.settings, "gemini_model", "gemini-primary")
    monkeypatch.setattr(provider.settings, "gemini_fallback_models", "gemini-backup-1")
    monkeypatch.setattr(provider.settings, "groq_api_key", "groq-key")
    monkeypatch.setattr(provider.settings, "groq_model", "llama-oss")
    monkeypatch.setattr(provider.settings, "ai_provider_order", "gemini,groq")

    def gemini_fail(**kwargs):
        raise AIProviderError("gemini unavailable")

    monkeypatch.setattr(provider, "_gemini_generate", gemini_fail)
    monkeypatch.setattr(provider, "_groq_generate", lambda **kwargs: "groq-ok")

    response = provider.generate("hello")
    assert response.provider == "groq"
    assert response.model == "llama-oss"
    assert response.attempts == [
        "gemini:gemini-primary",
        "gemini:gemini-backup-1",
        "groq:llama-oss",
    ]
