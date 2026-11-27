"""Static checks for docs/paper_latex (no TeX installation needed):
undefined generated macros, missing bibliography keys, undefined \\ref labels, TODO markers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "paper_latex"
PREFIX = r"(?:auc|aucsd|ece|delta|deltaci|p|cv|cvsd|cvmin|tmp|rqtwo|rqthree|rag|lat|test|all|deploy)"


def main() -> int:
    gen = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "generated").glob("*macros.tex"))
    defined = set(re.findall(r"\\newcommand\{\\(\w+)\}", gen))
    sources = list((ROOT / "sections").glob("*.tex")) + list((ROOT / "figures").glob("*.tex")) + [ROOT / "main.tex"]
    text = {p: p.read_text(encoding="utf-8") for p in sources}
    used = set()
    for t in text.values():
        used |= set(re.findall(r"\\(" + PREFIX + r"[A-Z]\w*)", t))
    bib = set(re.findall(r"^@\w+\{([^,]+)", (ROOT / "references.bib").read_text(encoding="utf-8"), re.M))
    cited = {k.strip() for t in text.values() for group in re.findall(r"\\cite\{([^}]*)\}", t) for k in group.split(",")}
    all_tex = list(text.values()) + [p.read_text(encoding="utf-8") for p in (ROOT / "generated").glob("*.tex")]
    labels = {l for t in all_tex for l in re.findall(r"\\label\{([^}]*)\}", t)}
    refs = {r for t in all_tex for r in re.findall(r"\\ref\{([^}]*)\}", t)}
    todos = {p.name: t.count("TODO") for p, t in text.items() if "TODO" in t}
    problems = {"undefined_macros": sorted(used - defined), "missing_bib_keys": sorted(cited - bib),
                "undefined_refs": sorted(refs - labels), "todo_markers": todos}
    for k, v in problems.items():
        print(f"{k}: {v}")
    print(f"cited keys: {len(cited)} / bib entries: {len(bib)}")
    return 1 if any(problems.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
