from dataclasses import dataclass, field

import httpx

from app.config import settings


@dataclass
class AIResponse:
    text: str
    provider: str
    model: str
    attempts: list[str] = field(default_factory=list)


class AIProviderError(RuntimeError):
    pass


class FallbackAIProvider:
    def __init__(self) -> None:
        self.settings = settings

    @staticmethod
    def _csv(raw: str) -> list[str]:
        return [item.strip() for item in raw.split(",") if item.strip()]

    def configured_provider_order(self) -> list[str]:
        allowed = {"gemini", "groq", "openrouter", "huggingface"}
        order = [provider for provider in self._csv(self.settings.ai_provider_order) if provider in allowed]
        return order or ["gemini", "groq", "openrouter", "huggingface"]

    def gemini_model_chain(self) -> list[str]:
        chain = [self.settings.gemini_model, *self._csv(self.settings.gemini_fallback_models)]
        seen: set[str] = set()
        ordered: list[str] = []
        for model in chain:
            if model and model not in seen:
                seen.add(model)
                ordered.append(model)
        return ordered

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> AIResponse:
        attempts: list[str] = []
        failures: list[str] = []

        for provider in self.configured_provider_order():
            if provider == "gemini":
                if not self.settings.gemini_api_key:
                    failures.append("gemini: missing GEMINI_API_KEY")
                    continue
                for model in self.gemini_model_chain():
                    attempts.append(f"gemini:{model}")
                    try:
                        text = self._gemini_generate(
                            model=model,
                            prompt=prompt,
                            system_prompt=system_prompt,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        return AIResponse(text=text, provider="gemini", model=model, attempts=attempts)
                    except AIProviderError as exc:
                        failures.append(f"gemini:{model} -> {exc}")
                continue

            if provider == "groq":
                if not self.settings.groq_api_key:
                    failures.append("groq: missing GROQ_API_KEY")
                    continue
                model = self.settings.groq_model
                attempts.append(f"groq:{model}")
                try:
                    text = self._groq_generate(
                        model=model,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    return AIResponse(text=text, provider="groq", model=model, attempts=attempts)
                except AIProviderError as exc:
                    failures.append(f"groq:{model} -> {exc}")
                continue

            if provider == "openrouter":
                if not self.settings.openrouter_api_key:
                    failures.append("openrouter: missing OPENROUTER_API_KEY")
                    continue
                model = self.settings.openrouter_model
                attempts.append(f"openrouter:{model}")
                try:
                    text = self._openrouter_generate(
                        model=model,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    return AIResponse(text=text, provider="openrouter", model=model, attempts=attempts)
                except AIProviderError as exc:
                    failures.append(f"openrouter:{model} -> {exc}")
                continue

            if provider == "huggingface":
                if not self.settings.huggingface_api_key:
                    failures.append("huggingface: missing HUGGINGFACE_API_KEY")
                    continue
                model = self.settings.huggingface_model
                attempts.append(f"huggingface:{model}")
                try:
                    text = self._huggingface_generate(
                        model=model,
                        prompt=prompt,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    return AIResponse(text=text, provider="huggingface", model=model, attempts=attempts)
                except AIProviderError as exc:
                    failures.append(f"huggingface:{model} -> {exc}")

        raise AIProviderError("No provider succeeded. " + " | ".join(failures))

    def _gemini_generate(
        self,
        *,
        model: str,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }
        if system_prompt:
            payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

        response = httpx.post(
            url,
            params={"key": self.settings.gemini_api_key},
            json=payload,
            timeout=self.settings.ai_timeout_seconds,
        )
        if response.status_code >= 400:
            raise AIProviderError(f"http_{response.status_code}: {response.text[:250]}")
        data = response.json()
        try:
            candidates = data["candidates"]
            parts = candidates[0]["content"]["parts"]
            text = "".join(part.get("text", "") for part in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(f"malformed_response: {exc}") from exc
        if not text:
            raise AIProviderError("empty_response")
        return text

    def _groq_generate(
        self,
        *,
        model: str,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> str:
        return self._openai_compatible_generate(
            provider_name="groq",
            url="https://api.groq.com/openai/v1/chat/completions",
            api_key=self.settings.groq_api_key or "",
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _openrouter_generate(
        self,
        *,
        model: str,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> str:
        return self._openai_compatible_generate(
            provider_name="openrouter",
            url="https://openrouter.ai/api/v1/chat/completions",
            api_key=self.settings.openrouter_api_key or "",
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _openai_compatible_generate(
        self,
        *,
        provider_name: str,
        url: str,
        api_key: str,
        model: str,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=self.settings.ai_timeout_seconds,
        )
        if response.status_code >= 400:
            raise AIProviderError(f"http_{response.status_code}: {response.text[:250]}")
        data = response.json()
        try:
            text = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError(f"{provider_name}_malformed_response: {exc}") from exc
        if not text:
            raise AIProviderError("empty_response")
        return text

    def _huggingface_generate(
        self,
        *,
        model: str,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> str:
        final_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = httpx.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers={
                "Authorization": f"Bearer {self.settings.huggingface_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "inputs": final_prompt,
                "parameters": {"max_new_tokens": max_tokens, "temperature": temperature},
            },
            timeout=self.settings.ai_timeout_seconds,
        )
        if response.status_code >= 400:
            raise AIProviderError(f"http_{response.status_code}: {response.text[:250]}")
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            raise AIProviderError(f"api_error: {data['error']}")
        if not isinstance(data, list) or not data:
            raise AIProviderError("malformed_response")
        text = str(data[0].get("generated_text", "")).strip()
        if not text:
            raise AIProviderError("empty_response")
        return text
