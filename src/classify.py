"""
Stage 2: RawEmail -> Classification

One API call. No loop, no tools. This is Level 0 of the curriculum applied to
a real problem.
"""

from .contracts import Classification, RawEmail
from .llm import call_structured

SYSTEM = """You are an email triage assistant.

Classify the email into exactly one category:
  - interview : an invitation, scheduling request, or update about a job interview
  - personal  : real correspondence from a real person who knows the recipient
  - useful    : promotional or automated, but genuinely worth reading
  - skip      : promotional noise, receipts, notifications, mass marketing

Set confidence honestly. Low confidence on a borderline email is more useful
than false certainty. Only populate entities you can actually see in the text --
never guess a company or role."""

# TODO(session 1): the prompt above is a starting point, not an answer.
# Things worth trying, one at a time, measuring against your fixtures:
#   - Add 2-3 few-shot examples. Usually the single biggest accuracy jump.
#   - Sharpen the useful/skip boundary. It's the one that will annoy you most,
#     because "genuinely worth reading" means something specific to YOU that
#     the model can't infer. This is exactly the gap prefs.json fills later.
#   - Ask for reasoning BEFORE category in the schema field order and see if
#     accuracy changes. (It often does. Think about why.)


def classify(raw: RawEmail) -> Classification:
    return call_structured(
        prompt=raw.for_prompt(),
        schema=Classification,
        system=SYSTEM,
    )
