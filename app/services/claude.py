"""The only place that talks to the Anthropic API."""

import logging
import time
from typing import TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

from app.config import get_settings
from app.errors import AIError
from app.services.prompts import system_prompt

log = logging.getLogger("kita")

T = TypeVar("T", bound=BaseModel)

_client: anthropic.AsyncAnthropic | None = None


def get_client() -> anthropic.AsyncAnthropic:
    global _client
    if _client is None:
        key = get_settings().anthropic_api_key or None  # None -> SDK reads env / ant profile
        _client = anthropic.AsyncAnthropic(api_key=key, timeout=60.0, max_retries=2)
    return _client


async def generate(prompt_name: str, messages: list[dict], output: type[T]) -> T:
    """Call Claude with a cached system prompt and parse the reply into `output`.

    Retries once if the reply doesn't validate; raises AIError otherwise.
    """
    settings = get_settings()
    system = [{
        "type": "text",
        "text": system_prompt(prompt_name),
        "cache_control": {"type": "ephemeral"},
    }]

    for attempt in (1, 2):
        start = time.perf_counter()
        try:
            response = await get_client().messages.parse(
                model=settings.model,
                max_tokens=4000,
                system=system,
                messages=messages,
                output_config={"effort": "low"},
                output_format=output,
            )
        except (anthropic.APIConnectionError, anthropic.RateLimitError, anthropic.APIStatusError) as e:
            raise AIError("ai_unavailable", f"{type(e).__name__}: {e}") from e
        except ValidationError as e:
            log.warning("%s attempt %d: invalid output: %s", prompt_name, attempt, e)
            continue

        u = response.usage
        log.info(
            "%s ok in %.1fs req=%s in=%s cache_read=%s out=%s",
            prompt_name, time.perf_counter() - start, response._request_id,
            u.input_tokens, u.cache_read_input_tokens, u.output_tokens,
        )

        if response.stop_reason == "refusal":
            raise AIError("ai_unavailable", "model refused")
        if response.parsed_output is not None:
            return response.parsed_output
        log.warning("%s attempt %d: no parsed output (stop=%s)", prompt_name, attempt, response.stop_reason)

    raise AIError("ai_bad_output", f"{prompt_name}: could not parse model output")
