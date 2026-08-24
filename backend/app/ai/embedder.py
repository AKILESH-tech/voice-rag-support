import hashlib
import math
import httpx
from app.config import settings


class EmbeddingAdapter:
    EMBEDDING_DIM = 768

    def embed(self, text: str) -> list[float]:
        if not settings.gemini_api_key:
            return self._fallback_embed(text)
        try:
            return self._gemini_embed(text)
        except Exception:
            return self._fallback_embed(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]

    def _gemini_embed(self, text: str) -> list[float]:
        url = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
        response = httpx.post(
            url,
            params={"key": settings.gemini_api_key},
            json={"model": "models/text-embedding-004", "content": {"parts": [{"text": text}]}},
            timeout=settings.ai_timeout_seconds,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Gemini embed HTTP {response.status_code}: {response.text[:200]}")
        data = response.json()
        values = data["embedding"]["values"]
        # Pad or truncate to EMBEDDING_DIM
        if len(values) < self.EMBEDDING_DIM:
            values = values + [0.0] * (self.EMBEDDING_DIM - len(values))
        return values[: self.EMBEDDING_DIM]

    def _fallback_embed(self, text: str) -> list[float]:
        """Deterministic hash-based embedding for fallback."""
        vec = [0.0] * self.EMBEDDING_DIM
        words = text.lower().split()
        for word in words:
            h = int(hashlib.sha256(word.encode()).hexdigest(), 16)
            idx = h % self.EMBEDDING_DIM
            vec[idx] += 1.0
        # L2 normalize
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
