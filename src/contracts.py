"""
Data contracts between pipeline stages.

Write this file FIRST and change it deliberately. Every stage is a pure
function from one of these models to another. If you keep that true, each
stage stays independently testable and swappable.

    ingest    : Path        -> RawEmail
    classify  : RawEmail    -> Classification
    research  : Classification -> ResearchBundle     (session 3)
    synthesize: ResearchBundle -> Digest             (session 4)
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Category(str, Enum):
    """What kind of email this is. Drives routing in the pipeline."""

    INTERVIEW = "interview"
    PERSONAL = "personal"
    USEFUL = "useful"
    SKIP = "skip"


class RawEmail(BaseModel):
    """Output of stage 1. A parsed email, no interpretation applied yet."""

    message_id: str
    thread_id: str | None = None
    sender: str
    subject: str
    body_text: str
    received_at: datetime | None = None

    def for_prompt(self, max_chars: int = 2000) -> str:
        """Compact representation to hand to an LLM.

        Truncating matters more than you'd think: some marketing emails are
        tens of thousands of tokens of footer boilerplate.
        """
        return (
            f"From: {self.sender}\n"
            f"Subject: {self.subject}\n"
            f"---\n"
            f"{self.body_text[:max_chars]}"
        )


class Entities(BaseModel):
    """Structured facts pulled out of the email. All optional by design --
    a personal email has no company, and forcing one invites hallucination."""

    company: str | None = None
    role: str | None = None
    deadline: str | None = None


class Classification(BaseModel):
    """Output of stage 2. The LLM's judgment, in a shape code can branch on."""

    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="One sentence. Useful when debugging.")
    entities: Entities = Field(default_factory=Entities)

    @property
    def should_process(self) -> bool:
        """Routing decision lives in CODE, not in the model.

        The LLM's only job was producing the category. What that category
        means for control flow is your decision, and staying deterministic
        here is what makes the system debuggable.
        """
        return self.category != Category.SKIP and self.confidence >= 0.6


# ---------------------------------------------------------------------------
# Stages 3 and 4 -- not needed until sessions 3 and 4. Sketched so the shape
# of the pipeline is visible from day one.
# ---------------------------------------------------------------------------


class Resource(BaseModel):
    url: str
    title: str
    why_relevant: str


class ResearchBundle(BaseModel):
    company_profile: str | None = None
    likely_questions: list[str] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)


class Digest(BaseModel):
    subject: str
    markdown_body: str
    run_id: str
