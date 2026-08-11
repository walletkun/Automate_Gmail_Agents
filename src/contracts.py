"""
Used for parsing in email and model for classification results
"""


from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class RawEmail(BaseModel):
    sender: str
    subject: str
    body_text: str
    received_at: datetime
    message_id: str
    thread_id: str | None = None

    def for_prompt(self) -> str:
        """How this email should present itself to LLM"""

        return f"From: {self.sender}\nSubject: {self.subject}\n---\n{self.body_text}"

class Category(str, Enum):
    INTERVIEW = "interview"
    PERSONAL = "personal"
    SKIP = "skip"

class Classification(BaseModel):
    category: Category
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str




