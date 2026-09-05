"""
Entry point.

    uv run main.py fixtures/interview_stripe.eml

Note what this does NOT take: a Gmail connection. The pipeline's input is a
file path, and keeping it that way for as long as possible is the single
biggest thing protecting your iteration speed.
"""

import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

from src.classify import classify
from src.ingest import parse_eml

RUNS = Path("runs")


def log(run_dir: Path, name: str, obj) -> None:
    """Write every stage output to disk.

    This is not optional. When the final output is wrong you need to know
    WHICH STAGE went wrong, and you cannot get that from the end result. It
    also gives you free replay -- feed a saved stage-3 output into stage 4
    while iterating on formatting, without re-paying for research.
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = obj.model_dump(mode="json") if hasattr(obj, "model_dump") else obj
    (run_dir / f"{name}.json").write_text(json.dumps(payload, indent=2, default=str))


def main(eml_path: str) -> None:
    run_id = f"{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
    run_dir = RUNS / run_id
    print(f"run_id: {run_id}\n")

    print("[1/2] ingest")
    raw = parse_eml(Path(eml_path))
    log(run_dir, "01_raw", raw)
    print(f"  from: {raw.sender}")
    print(f"  subj: {raw.subject}")
    print(f"  body: {len(raw.body_text)} chars")
    if not raw.body_text.strip():
        print("  !! empty body -- go fix extract_body() in src/ingest.py")

    print("\n[2/2] classify")
    result = classify(raw)
    log(run_dir, "02_classification", result)
    print(f"  category   : {result.category.value}")
    print(f"  confidence : {result.confidence}")
    print(f"  reasoning  : {result.reasoning}")

    print(f"-> logs in {run_dir}/")

    # Stages 3-5 land here in later sessions. Resist adding them until stage
    # 2 is solid across every fixture.


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: uv run main.py <path-to-.eml>")
        sys.exit(1)
    main(sys.argv[1])
