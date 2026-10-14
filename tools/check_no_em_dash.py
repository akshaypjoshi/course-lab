#!/usr/bin/env python3
"""Fail if any text file in the repository contains an em dash (U+2014) or a horizontal bar (U+2015)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = {".md", ".py", ".mjs", ".js", ".ts", ".tsx", ".json", ".yml", ".yaml", ".sh", ".css", ".html", ".txt", ""}
DASHES = (chr(0x2014), chr(0x2015))
bad = 0
for p in sorted(ROOT.rglob("*")):
    if not p.is_file() or ".git" in p.parts or p.suffix not in TEXT:
        continue
    for n, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if any(c in line for c in DASHES):
            print(f"{p.relative_to(ROOT)}:{n}: {line.strip()[:120]}")
            bad += 1
if bad:
    sys.exit(f"{bad} line(s) with an em dash; use a comma, colon, parentheses or a new sentence.")
print("no em dashes")
