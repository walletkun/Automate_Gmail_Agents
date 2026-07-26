"""
The single place this project talks to Anthropic.

Keep it that way. When you add the agent loop in session 2, it goes here, and
every stage upstream keeps working unchanged.
"""

import json
import os
from typing import TypeVar

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

MODEL = "claude-sonnet-4-6"

# Lazily constructed. Otherwise importing anything in this project requires a
# key, and you can't test the ingest stage until you've set one up.
_client = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
            )
        _client = anthropic.Anthropic(api_key=key)
    return _client

T = TypeVar("T", bound=BaseModel)

# Flip this on and watch every call. Turning it off should feel like a loss.
VERBOSE = True


def call(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    """One raw API call. Level 0 of the curriculum, nothing more."""
    response = get_client().messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )

    if VERBOSE:
        # Watch these numbers. Token usage compounding across agent loop
        # iterations is the thing that surprises people about agent cost.
        print(f"  [llm] stop_reason={response.stop_reason} usage={response.usage}")

    return response.content[0].text


def call_structured(prompt: str, schema: type[T], system: str = "") -> T:
    """Force the model into a Pydantic shape.

    Two things make this reliable, and both matter more than prompt wording:
      1. Handing the model the actual JSON schema, not a prose description.
      2. Prefilling the assistant turn with '{' so it cannot open with
         "Here's the JSON:" or a markdown fence.

    TODO(session 1): this raises on malformed output. Decide what you want --
    retry once with the error fed back? fall back to a default? Make that
    choice deliberately; it's a real design decision, not an edge case.
    """
    schema_json = json.dumps(schema.model_json_schema(), indent=2)
    full_system = (
        f"{system}\n\n"
        f"Respond with ONLY a JSON object matching this schema. "
        f"No prose, no markdown fences.\n\n{schema_json}"
    ).strip()

    response = get_client().messages.create(
        model=MODEL,
        max_tokens=2048,
        system=full_system,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "{"},  # prefill
        ],
    )

    raw = "{" + response.content[0].text

    if VERBOSE:
        print(f"  [llm] structured -> {raw[:120]}...")

    try:
        return schema.model_validate_json(raw)
    except ValidationError as e:
        print(f"  [llm] PARSE FAILED. Raw output:\n{raw}\n")
        raise e
