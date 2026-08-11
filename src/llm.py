"""
Talks to the LLM
If needed we can swap providers in this file
"""

import os
from typing import TypeVar

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

load_dotenv()

MODEL = "gemini-3.6-flash"
T = TypeVar("T", bound=BaseModel)

_client = None

def get_client() -> genai.Client:
    """Lazy init so importing this module doesn't require a key"""
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is missing")
        _client = genai.Client(api_key=key)
        
    return _client


def call_structured(prompt: str, schema: type[T], system: str = "") -> T:
    """Send a prompt, get back a validated instance of `schema`."""
    response = get_client().models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "system_instruction": system,
            "response_mime_type": "application/json",
            "response_schema": schema,
        },
    )
    
    print(response)
    return response.parsed