from pathlib import Path
from src.ingest import parse_eml
from src.classify import classify

for f in sorted(Path('fixtures').glob('*.eml')):
    e = parse_eml(f)
    c = classify(e)
    print(f"{f.name}")
    print(f"  {c.category.value}  ({c.confidence})")
    print(f"  {c.reasoning}\n")
