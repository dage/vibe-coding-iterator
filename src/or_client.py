# src/or_client.py
"""
Tiny OpenRouter client + stateful Conversation.

- Async-only (no streaming)
- Backoff on 429/5xx/timeout/network; never on 402 (insufficient credits)
- Images: accept local bytes/paths and encode to base64 data: URLs
- Attribution headers required via env (see _Settings below)

Env (per README/setup.sh):
  VIBES_API_KEY        - required
  VIBES_CODE_MODEL     - default code model slug (e.g., openai/gpt-4o-mini)
  VIBES_VISION_MODEL   - default vision model slug
  VIBES_APP_NAME       - required; used for attribution headers (X-Title) and a simple Referer

Docs: OpenRouter is OpenAI-compatible; images accept base64 data URLs; attribution headers required.
"""

from __future__ import annotations
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import base64, mimetypes, asyncio, random, os, re

from pydantic import BaseSettings, Field
from openai import (
    AsyncOpenAI,
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
)

# ---------------- Settings & client ---------------- #

TIMEOUT_SECONDS: float = 120.0


class _Settings(BaseSettings):
    api_key: str = Field(..., env="VIBES_API_KEY")
    base_url: str = Field("https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")

    # Defaults so callers can omit `model=...`
    code_model: str  = Field("openai/gpt-4o-mini", env="VIBES_CODE_MODEL")
    vision_model: str = Field("openai/gpt-4o-mini", env="VIBES_VISION_MODEL")

    # Required attribution
    app_name: str = Field(..., env="VIBES_APP_NAME")


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.strip().lower()).strip("-")


@lru_cache
def _settings() -> _Settings:
    return _Settings()  # parsed once per process


@lru_cache
def _client() -> AsyncOpenAI:
    s = _settings()
    headers: Dict[str, str] = {
        "X-Title": s.app_name,
        # Minimal referer using the app name; avoids extra config.
        "HTTP-Referer": f"https://{_slug(s.app_name)}.local",
    }
    return AsyncOpenAI(
        api_key=s.api_key,
        base_url=s.base_url,
        timeout=TIMEOUT_SECONDS,
        default_headers=headers,
    )


# -------------- Internal helpers -------------- #

def _guess_mime(path: Union[str, Path]) -> str:
    mt, _ = mimetypes.guess_type(str(path))
    return mt or "image/png"


def encode_image_to_data_url(
    data: Union[bytes, str, Path],
    mime: Optional[str] = None,
) -> str:
    """
    Accepts raw bytes or a filesystem path; returns a data: URL suitable
    for OpenAI/OpenRouter Chat Completions image input.
    """
    if isinstance(data, (str, Path)) and Path(str(data)).exists():
        p = Path(str(data))
        raw = p.read_bytes()
        mime = mime or _guess_mime(p)
    elif isinstance(data, (bytes, bytearray)):
        raw = bytes(data)
        mime = mime or "image/png"
    elif isinstance(data, str) and data.startswith("data:"):
        # already a data URL; pass through
        return data
    else:
        raise ValueError("encode_image_to_data_url expects bytes, data: URL, or existing file path")

    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{b64}"


async def _retry(coro_fn, max_tries: int = 5, base: float = 0.5):
    """
    Exponential backoff for transient conditions:
      - 429 (rate limit), 408 (timeout), 5xx, network/timeout errors.
    Never retries 402 (insufficient credits).
    """
    for i in range(max_tries):
        try:
            return await coro_fn()
        except (RateLimitError, APITimeoutError, APIConnectionError) as e:
            # always back off for these
            if i == max_tries - 1:
                raise
            await asyncio.sleep(base * (2 ** i) + random.random() * 0.1)
        except APIStatusError as e:
            code = getattr(e, "status_code", None)
            if code == 402:
                # no credits – surface immediately
                raise
            if code in (408, 429, 500, 502, 503, 504):
                if i == max_tries - 1:
                    raise
                await asyncio.sleep(base * (2 ** i) + random.random() * 0.1)
            else:
                raise


# -------------- Public stateless helpers -------------- #

async def chat(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Stateless chat. Returns the assistant message string.
    """
    s = _settings()

    async def call():
        return await _client().chat.completions.create(
            model=model or s.code_model,
            messages=messages,
            **kwargs,
        )

    res = await _retry(call)
    return res.choices[0].message.content or ""


async def vision_single(
    prompt: str,
    image: Union[bytes, str, Path],
    model: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Stateless single-image helper. Encodes to data URL and sends one user message
    containing prompt + image. Prefer using Conversation for multi-turn or multi-image.
    """
    s = _settings()
    data_url = encode_image_to_data_url(image)
    msgs = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url}},
        ],
    }]
    return await chat(msgs, model=model or s.vision_model, **kwargs)


# ---------------- Stateful Conversation ---------------- #

class Conversation:
    """
    Lightweight stateful chat wrapper that supports:
      - text-only turns
      - image-only turns
      - mixed text + N images in one turn

    You can inspect .messages for UI rendering, or use .message(i).
    """

    def __init__(self, model: Optional[str] = None):
        self._messages: List[Dict[str, Any]] = []
        self._model = model  # optional override per-conversation

    # ---- system / history management ----

    def set_system(self, content: str) -> None:
        if self._messages and self._messages[0].get("role") == "system":
            self._messages[0]["content"] = content
        else:
            self._messages.insert(0, {"role": "system", "content": content})

    def reset(self) -> None:
        self._messages.clear()

    # ---- inspection helpers for UI ----

    @property
    def messages(self) -> List[Dict[str, Any]]:
        # Return a shallow copy to avoid accidental mutation by UI
        return list(self._messages)

    def message(self, index: int) -> Dict[str, Any]:
        return self._messages[index]

    def __len__(self) -> int:
        return len(self._messages)

    # ---- user turn construction ----

    def _build_user_content(
        self,
        prompt: Optional[str],
        images: Optional[List[Union[bytes, str, Path]]],
    ) -> List[Dict[str, Any]]:
        parts: List[Dict[str, Any]] = []
        if prompt:
            parts.append({"type": "text", "text": prompt})
        for img in images or []:
            data_url = encode_image_to_data_url(img)
            parts.append({"type": "image_url", "image_url": {"url": data_url}})
        if not parts:
            raise ValueError("User turn must include text and/or at least one image")
        return parts

    # ---- main ask API (minimal surface) ----

    async def ask(
        self,
        prompt: Optional[str] = None,
        images: Optional[List[Union[bytes, str, Path]]] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Add a user turn (text, images, or both), send to model, store assistant reply, return reply text.
        - `images`: list of bytes/paths/data URLs; will be encoded as data URLs
        - `model`: overrides conversation default just for this call
        """
        user_msg: Dict[str, Any] = {"role": "user"}
        user_msg["content"] = self._build_user_content(prompt, images)
        self._messages.append(user_msg)

        reply = await chat(
            self._messages,
            model=model or self._model or _settings().code_model,
            **kwargs,
        )

        self._messages.append({"role": "assistant", "content": reply})
        return reply