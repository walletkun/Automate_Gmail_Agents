"""
.eml file on disk -> RawEmail
No LLM here, just parsing
"""

import email
import email.policy
import email.utils
from email.message import EmailMessage
from pathlib import Path

from .contracts import RawEmail

def parse_eml(path: Path) -> RawEmail:
    """Read from a .eml file into RawEmail"""
    with open(path, 'rb') as f:
        msg: EmailMessage = email.message_from_binary_file(f, policy=email.policy.default)

    return RawEmail(
        sender=msg.get("From"),
        subject=msg.get("Subject"),
        body_text=extract_body(msg),
        received_at=email.utils.parsedate_to_datetime(msg.get("Date")),
        message_id=msg.get("Message-ID"),
        thread_id=None
    )

def extract_body(msg:EmailMessage) -> str:
    """Pull readable text out of MIME tree

    - get_body() with a preferencelist to pick the part
    - get_content() to turn that part into a string
    - handle the None case
    """

    part = msg.get_body(preferencelist=('plain', 'html', 'related'))

    if not part:
        return ""

    content = part.get_content()
    
    return content
    
    
    