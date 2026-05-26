import hashlib
import json
import math
import re
import urllib.error
import urllib.request

from app.config import settings

TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


class HashingEmbeddingProvider:
    """Local placeholder embedding provider for development without API keys."""

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * settings.embedding_dimension
        tokens = TOKEN_RE.findall(text.lower())
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % settings.embedding_dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[idx] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class BailianEmbeddingProvider:
    def __init__(self) -> None:
        if not settings.dashscope_api_key:
            raise RuntimeError("DASHSCOPE_API_KEY is required when EMBEDDING_PROVIDER=bailian")
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"

    def embed(self, text: str) -> list[float]:
        payload = {
            "model": settings.embedding_model,
            "input": text,
            "dimensions": settings.embedding_dimension,
            "encoding_format": "float",
        }
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.dashscope_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Bailian embedding request failed: {exc.code} {detail}") from exc
        return [float(value) for value in result["data"][0]["embedding"]]


def get_embedding_provider():
    if settings.embedding_provider == "bailian":
        return BailianEmbeddingProvider()
    return HashingEmbeddingProvider()


embedding_provider = get_embedding_provider()
