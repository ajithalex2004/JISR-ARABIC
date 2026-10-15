"""Provider adapters behind the AI gateway: one class per AI company, same interface.

Each adapter turns a provider-neutral AIRequest into that provider's API call and returns
(text, model, input_tokens, output_tokens). Errors are raised as they come so the gateway can
tell an outage (switch provider) from a bad request (report it to the caller).
"""
import base64
import io
import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("fahim.ai")

# Gemini file uploads (used for textbook page images when drafting) last 48 hours; reuse them
# within a day so a chapter's pages are uploaded once, not once per prompt.
_UPLOAD_TTL_SECONDS = 24 * 3600
_uploads: Dict[Tuple[str, float, int], Tuple[Any, float]] = {}


def _int(value) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _attachment_bytes(data) -> bytes:
    return data.read_bytes() if isinstance(data, Path) else data


def strip_code_fence(text: str) -> str:
    return re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", (text or "").strip()).strip()


class ProviderError(RuntimeError):
    """An HTTP error from a provider, carrying the status code for the gateway to classify."""

    def __init__(self, provider: str, code: int, message: str):
        super().__init__(f"{code} {message}")
        self.provider = provider
        self.code = code


class GeminiProvider:
    name = "gemini"

    def __init__(self, client=None):
        self._client = client

    def client(self):
        if self._client is not None:
            return self._client
        from backend.modules.tutoring.assistant import _get_gemini_client
        return _get_gemini_client()

    def available(self) -> bool:
        return self.client() is not None

    def model_for(self, request) -> str:
        from backend.modules.tutoring.assistant import GEMINI_MODEL
        return request.gemini_model or GEMINI_MODEL

    def _upload(self, client, path: Path):
        stat = path.stat()
        key = (str(path), stat.st_mtime, stat.st_size)
        cached = _uploads.get(key)
        if cached and time.time() - cached[1] < _UPLOAD_TTL_SECONDS:
            return cached[0]
        uploaded = client.files.upload(file=str(path))
        if len(_uploads) > 500:
            _uploads.clear()
        _uploads[key] = (uploaded, time.time())
        return uploaded

    def generate(self, request) -> Tuple[str, str, int, int]:
        from google.genai import types
        from backend.modules.tutoring.assistant import _child_safety_settings

        client = self.client()
        if client is None:
            raise ProviderError(self.name, 401, "GEMINI_API_KEY is not set or the Gemini client could not start")
        model = self.model_for(request)
        parts = []
        for data, mime in request.attachments:
            # Files on disk (textbook pages) go through the Files API; in-memory data goes inline.
            parts.append(self._upload(client, data) if isinstance(data, Path)
                         else types.Part.from_bytes(data=data, mime_type=mime))
        contents = [*parts, request.prompt] if parts else request.prompt

        config: Dict[str, Any] = {}
        if request.system:
            config["system_instruction"] = request.system
        if request.temperature is not None:
            config["temperature"] = request.temperature
        if request.max_tokens:
            config["max_output_tokens"] = request.max_tokens
        if request.json:
            config["response_mime_type"] = "application/json"
        if request.schema:
            config["response_schema"] = request.schema
        if request.child_safe:
            config["safety_settings"] = _child_safety_settings(types)
        kwargs: Dict[str, Any] = {"model": model, "contents": contents}
        if config:
            kwargs["config"] = types.GenerateContentConfig(**config)
        response = client.models.generate_content(**kwargs)
        usage = getattr(response, "usage_metadata", None)
        text = getattr(response, "text", None)
        return (text if isinstance(text, str) else "", model,
                _int(getattr(usage, "prompt_token_count", 0)),
                _int(getattr(usage, "candidates_token_count", 0)) + _int(getattr(usage, "thoughts_token_count", 0)))


class AnthropicProvider:
    """Claude via the Messages API (plain HTTPS, no extra SDK dependency)."""

    name = "anthropic"
    URL = "https://api.anthropic.com/v1/messages"
    # Per-request image limit is 5 MB; scanned pages are shrunk to stay under it.
    MAX_IMAGE_BYTES = 4_500_000

    def available(self) -> bool:
        return bool(os.getenv("ANTHROPIC_API_KEY", "").strip())

    def model_for(self, request) -> str:
        if request.tier == "strong":
            return os.getenv("FAHIM_ANTHROPIC_STRONG_MODEL", "").strip() or "claude-sonnet-5-5"
        return os.getenv("FAHIM_ANTHROPIC_MODEL", "").strip() or "claude-haiku-5-5"

    def _image_block(self, data: bytes, mime: str) -> Dict[str, Any]:
        if len(data) > self.MAX_IMAGE_BYTES:
            from PIL import Image
            image = Image.open(io.BytesIO(data)).convert("RGB")
            image.thumbnail((2000, 2000))
            out = io.BytesIO()
            image.save(out, format="JPEG", quality=85)
            data, mime = out.getvalue(), "image/jpeg"
        return {"type": "image", "source": {"type": "base64", "media_type": mime,
                                            "data": base64.b64encode(data).decode()}}

    def _system(self, request) -> str:
        lines = [request.system] if request.system else []
        if request.child_safe:
            lines.append("Every user is a school child: keep all content age-appropriate and safe.")
        if request.json:
            lines.append("Reply with one valid JSON object only: no markdown, no code fences, no text around it.")
        if request.schema:
            lines.append("The JSON must follow this schema (types are given in upper case):\n"
                         + json.dumps(request.schema, ensure_ascii=False))
        return "\n\n".join(lines)

    def generate(self, request) -> Tuple[str, str, int, int]:
        import httpx

        key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not key:
            raise ProviderError(self.name, 401, "ANTHROPIC_API_KEY is not set")
        model = self.model_for(request)
        content: List[Dict[str, Any]] = []
        for data, mime in request.attachments:
            raw = _attachment_bytes(data)
            if mime == "application/pdf":
                content.append({"type": "document", "source": {"type": "base64", "media_type": mime,
                                                               "data": base64.b64encode(raw).decode()}})
            else:
                content.append(self._image_block(raw, mime))
        content.append({"type": "text", "text": request.prompt})
        body: Dict[str, Any] = {
            "model": model,
            "max_tokens": request.max_tokens or 4096,
            "messages": [{"role": "user", "content": content}],
        }
        system = self._system(request)
        if system:
            body["system"] = system
        if request.temperature is not None:
            body["temperature"] = request.temperature
        response = httpx.post(self.URL, json=body, timeout=request.timeout, headers={
            "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json",
        })
        if response.status_code >= 400:
            try:
                message = response.json().get("error", {}).get("message") or response.text
            except Exception:
                message = response.text
            raise ProviderError(self.name, response.status_code, " ".join(str(message).split())[:300])
        data = response.json()
        text = "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")
        if request.json:
            text = strip_code_fence(text)
        usage = data.get("usage") or {}
        return text, data.get("model") or model, _int(usage.get("input_tokens")), _int(usage.get("output_tokens"))


PROVIDERS = {"gemini": GeminiProvider, "anthropic": AnthropicProvider}
