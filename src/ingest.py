"""
Stage 1: .eml file on disk -> RawEmail

No LLM here. Pure parsing, and more annoying than you'd expect.

Get fixtures: open an email in Gmail -> three-dot menu -> "Download message".
Collect ~6: two interview invites, a personal email, a promo, a newsletter,
and one weird one. The weird one is where the bugs live.
"""

import email
import email.utils
import email.policy
from email.message import EmailMessage
from pathlib import Path

from .contracts import RawEmail


def parse_eml(path: Path) -> RawEmail:
    """Read a .eml file into a RawEmail."""
    with open(path, "rb") as f:
        msg: EmailMessage = email.message_from_binary_file(f, policy=email.policy.default)

    return RawEmail(
        message_id=msg.get("Message-ID", path.stem),
        thread_id=None,
        sender=str(msg.get("From", "unknown")),
        subject=str(msg.get("Subject", "(no subject)")),
        body_text=extract_body(msg),
        received_at=msg.get("Date") and email.utils.parsedate_to_datetime(msg["Date"]),
    )


def extract_body(msg: EmailMessage) -> str:
    """Pull readable text out of a MIME tree.

    TODO(session 1): the naive version below is deliberately incomplete.
    Run it across all your fixtures and watch it fail, then fix what breaks:

      - Many marketing emails are text/html ONLY, no plain-text part. You'll
        get an empty string. (Fix: html2text, or BeautifulSoup .get_text())
      - Nested multipart/alternative inside multipart/mixed.
      - Attachments -- skip parts with a Content-Disposition of "attachment".
      - Charset issues. errors="replace" keeps you from crashing on those.

    This is the stage that will eat your first evening. That's normal, and
    it's why Gmail comes LAST -- fight this offline where iteration is free.
    """
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or "utf-8",
                                          errors="replace")
        return ""  # <- you will hit this. handle text/html when you do.

    payload = msg.get_payload(decode=True)
    if payload:
        return payload.decode(msg.get_content_charset() or "utf-8", errors="replace")
    return ""
