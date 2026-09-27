#!/usr/bin/env python3
"""Assemble one Markdown file from canon/.

By default the book titles are the modern Portuguese names and the
1911 preface stays out. ``--original`` uses the edition's own book titles
and puts ``front/preface.md`` at the front. ``--testament ot`` keeps
folders 01-39. ``--testament nt`` keeps folders 41-67. The New Testament
title page is included only when that testament is in the file.
Files in ``extra/`` stay out of this Markdown.

The printed index of page numbers is not included: those pages belong
to the 1911 volume.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from books import books_for, chapter_filename  # noqa: E402
from build_canon import PT_NAME  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "canon"
FRONT = ROOT / "front"
STEM = "biblia"
COMMENT_RE = re.compile(r"\A<!--\n.*?\n-->\n+", re.S)
HEADING_RE = re.compile(r"^## .+$", re.M)


def load_titles() -> tuple[str | None, dict[str, str]]:
    text = (FRONT / "titles.md").read_text(encoding="utf-8")
    banner = None
    titles: dict[str, str] = {}
    parts = re.split(r"^## ", text, flags=re.M)
    for part in parts[1:]:
        heading, _, body = part.partition("\n")
        body = body.strip()
        if heading.strip() == "Novo Testamento":
            banner = body.split("\n\n", 1)[0].strip()
            continue
        folder = heading.strip()
        titles[folder] = body
    return banner, titles


def chapter_markdown(book, number: int, modern: bool) -> str:
    path = CANON / book.folder / chapter_filename(book.folder, number)
    text = COMMENT_RE.sub("", path.read_text(encoding="utf-8")).strip()
    if modern:
        name = "Salmo" if book.usfm == "PSA" else PT_NAME[book.folder]
    else:
        name = book.chapter_name
    return HEADING_RE.sub(f"## {name} {number}", text, count=1)


def edition_heading(block: str) -> tuple[str, str]:
    """Split a stored title into the heading line and any footnote under it."""
    first, _, rest = block.partition("\n")
    return first.strip(), rest.strip()


def build(modern: bool, testament: str | None = None) -> str:
    banner, titles = load_titles()
    parts: list[str] = []
    if not modern:
        preface = (FRONT / "preface.md").read_text(encoding="utf-8").strip()
        preface = re.sub(r"\n<!--\n.*?\n-->\s*\Z", "", preface, count=1, flags=re.S)
        parts.append(preface.strip())
    for book in books_for(testament):
        if modern:
            parts.append(f"# {PT_NAME[book.folder]}")
        else:
            if book.usfm == "MAT" and banner:
                parts.append(f"# {banner}")
            heading, note = edition_heading(titles[book.folder])
            parts.append(f"# {heading}")
            if note:
                parts.append(note)
        numbers = sorted(
            int(path.stem)
            for path in (CANON / book.folder).glob("*.md")
            if path.stem.isdigit()
        )
        for number in numbers:
            parts.append(chapter_markdown(book, number, modern))
    return "\n\n".join(parts).rstrip() + "\n"


def default_output(original: bool, testament: str | None) -> Path:
    pieces = [STEM]
    if original:
        pieces.append("original")
    if testament:
        pieces.append(testament)
    return ROOT / "dist" / ("-".join(pieces) + ".md")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Junta os capítulos de canon/ num Markdown."
    )
    parser.add_argument(
        "--original",
        action="store_true",
        help="Prefácio de 1911 e títulos dos livros como na edição.",
    )
    parser.add_argument(
        "--testament",
        choices=("ot", "nt"),
        help="Só o Antigo Testamento (pastas 01-39) ou só o Novo (pastas 41-67).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Ficheiro de saída. Por omissão, dist/biblia.md, "
            "com -original e -ot ou -nt conforme as opções."
        ),
    )
    args = parser.parse_args()
    destination = args.output or default_output(args.original, args.testament)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        build(modern=not args.original, testament=args.testament),
        encoding="utf-8",
    )
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
