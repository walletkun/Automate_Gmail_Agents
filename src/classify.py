"""
Raw Email -> Classificatio
One call: no loop, no tools.
"""

from .contracts import Classification, RawEmail
from .llm import call_structured

SYSTEM = """You classify incoming emails for a personal inbox triage pipeline.

Categories:

interview — a company or its recruiter is engaging you about a specific role.
Recruiter outreach about an opening, scheduling or rescheduling, take-home
assignments, interview confirmations, offers, and rejections. Automated
scheduling mail still counts if it concerns a real interview process.

personal — a real human is writing to you specifically, and it isn't about a
role at their company. School and university mail, LinkedIn reach-outs, coffee
chat requests, networking, mail from friends and family, and messages from
people you have an existing relationship with.

skip — mass mail. Retail promotions, newsletters, receipts, shipping notices,
platform notifications, and anything auto-generated for a large list. The test
is whether it was written for you, not merely addressed to you.

Guidance:
- Read the whole thread when quoted replies are present. Classify by what the
  most recent message is doing, not by what the thread started as.
- A sender's domain is weak evidence. A no-reply address can still carry a real
  interview; a personal address can still send a newsletter.
- Recruiter mass-blasts to many candidates are still interview, not skip.
- When two categories genuinely fit, choose the one with the higher cost of
  being missed, and lower your confidence.

confidence is your honest probability that this label is correct. Use the full
range. Reserve values above 0.9 for cases with no plausible alternative, and go
below 0.6 when you would want a human to check.

reasoning is one sentence naming the specific signal that decided it."""


def classify(raw: RawEmail) -> Classification:
    return call_structured(
        prompt=raw.for_prompt(),
        schema=Classification,
        system=SYSTEM
    )