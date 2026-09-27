#!/usr/bin/env python3
"""Check canon/ against the edition-canon/1 grammar."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from books import BOOKS, chapter_filename, note_letter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "canon"
LIMITS = Path(__file__).resolve().parent / "verse_limits.tsv"
TITLES = ROOT / "front" / "titles.md"
INDEX = ROOT / "CANON.md"

HEADER_RE = re.compile(
    r"<!--\nedition: arc1911\nbook: ([0-9]{2}-[0-9A-Z]{3})\nchapter: (\d+)\nlang: pt\n-->"
)
MARKER_RE = re.compile(r"\[\^([0-9A-Z]+_\d+_\d+_[a-z]+)\]")
DEF_RE = re.compile(r"^\[\^([0-9A-Z]+_\d+_\d+_[a-z]+)\]: ", re.M)
ID_PARTS = re.compile(r"^([0-9A-Z]+)_(\d+)_(\d+)_([a-z]+)$")
VERSE_RE = re.compile(r"^\*\*(\d+)\*\* ", re.M)
RAW_CUE_RE = re.compile(r"\[(?:\d+|[A-Z]{1,3})\]")


def load_limits() -> dict[tuple[str, int], int]:
    limits: dict[tuple[str, int], int] = {}
    for line in LIMITS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("book"):
            continue
        folder, chapter, maximum = line.split("\t")
        limits[(folder, int(chapter))] = int(maximum)
    return limits


EXTRA_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
SCOPES = {"ot", "nt", "ot-nt"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_extras(errors: list[str]) -> int:
    """Declared extras must match extra/. Return how many the manifest lists."""
    try:
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"manifest.json: {exc}")
        return 0
    extras = manifest.get("extras")
    if not isinstance(extras, list):
        errors.append("manifest.json: extras must be a list")
        return 0
    declared: set[str] = set()
    seen_ids: set[str] = set()
    for index, item in enumerate(extras):
        where = f"manifest.json extras[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: must be an object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or EXTRA_ID_RE.fullmatch(ident) is None:
            errors.append(f"{where}: id must be kebab-case")
        elif ident in seen_ids:
            errors.append(f"{where}: duplicate id {ident}")
        else:
            seen_ids.add(ident)
        role = item.get("role")
        if not isinstance(role, str) or EXTRA_ID_RE.fullmatch(role) is None:
            errors.append(f"{where}: role must be kebab-case")
        media = item.get("media_type")
        if (
            not isinstance(media, str)
            or media.count("/") != 1
            or " " in media
            or any(part == "" for part in media.split("/"))
        ):
            errors.append(f"{where}: media_type must be a type/subtype")
        if item.get("scope") not in SCOPES:
            errors.append(f"{where}: scope must be ot, nt, or ot-nt")
        description = item.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{where}: description is required")
        digest = item.get("sha256")
        if not isinstance(digest, str) or SHA_RE.fullmatch(digest) is None:
            errors.append(f"{where}: sha256 must be 64 lowercase hex characters")
            digest = None
        size = item.get("bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            errors.append(f"{where}: bytes must be a non-negative integer")
            size = None
        path_text = item.get("path")
        if (
            not isinstance(path_text, str)
            or path_text == "extra/README.md"
            or not path_text.startswith("extra/")
            or path_text.endswith("/")
            or any(part in {"", ".", ".."} for part in path_text.split("/"))
        ):
            errors.append(f"{where}: path must be a file under extra/")
            continue
        if path_text in declared:
            errors.append(f"{where}: duplicate path {path_text}")
            continue
        declared.add(path_text)
        path = ROOT / path_text
        if not path.is_file():
            errors.append(f"{path_text}: missing")
            continue
        actual_size = path.stat().st_size
        if size is not None and actual_size != size:
            errors.append(f"{path_text}: bytes {actual_size}, manifest {size}")
        if digest is not None and sha256_file(path) != digest:
            errors.append(f"{path_text}: sha256 does not match")
    extra_dir = ROOT / "extra"
    if not extras:
        if extra_dir.exists():
            errors.append("extra/ exists but extras is empty")
        return 0
    if not (extra_dir / "README.md").is_file():
        errors.append("extra/README.md missing")
    if extra_dir.exists() and not extra_dir.is_dir():
        errors.append("extra must be a directory")
        return len(extras)
    if extra_dir.is_dir():
        for file in sorted(path for path in extra_dir.rglob("*") if path.is_file()):
            rel = file.relative_to(ROOT).as_posix()
            if rel == "extra/README.md":
                continue
            if rel not in declared:
                errors.append(f"{rel}: not listed in manifest extras")
    return len(extras)


def check_stage(errors: list[str], key: str) -> None:
    """Pinned archive or prepared files must match the manifest hash and size.

    An edition that does not build a continuous Markdown publishes
    ``"prepared": []``. The key stays, so the manifest has the same shape.
    """
    try:
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"manifest.json: {exc}")
        return
    items = manifest.get(key)
    if not isinstance(items, list):
        errors.append(f"manifest.json: {key} must be a list")
        return
    for index, item in enumerate(items):
        where = f"manifest.json {key}[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: must be an object")
            continue
        path_text = item.get("path")
        if (
            not isinstance(path_text, str)
            or path_text.startswith("/")
            or any(part in {"", ".", ".."} for part in path_text.split("/"))
        ):
            errors.append(f"{where}: path is required")
            continue
        path = ROOT / path_text
        if not path.is_file():
            errors.append(f"{path_text}: missing")
            continue
        digest = item.get("sha256")
        if not isinstance(digest, str) or SHA_RE.fullmatch(digest) is None:
            errors.append(f"{where}: sha256 must be 64 lowercase hex characters")
        elif sha256_file(path) != digest:
            errors.append(f"{path_text}: sha256 does not match")
        size = item.get("bytes")
        actual = path.stat().st_size
        if isinstance(size, bool) or not isinstance(size, int) or actual != size:
            errors.append(f"{path_text}: bytes {actual}, manifest {size}")


def main() -> int:
    errors: list[str] = []
    check_stage(errors, "archive")
    check_stage(errors, "prepared")
    extra_count = check_extras(errors)
    ids: dict[str, str] = {}
    limits = load_limits()
    chapter_counts: dict[str, int] = {}
    for folder, _chapter in limits:
        chapter_counts[folder] = chapter_counts.get(folder, 0) + 1
    files = 0
    verses = 0
    index = INDEX.read_text(encoding="utf-8") if INDEX.is_file() else ""
    titles = TITLES.read_text(encoding="utf-8") if TITLES.is_file() else ""
    if not (ROOT / "front" / "preface.md").is_file():
        errors.append("front/preface.md missing")
    for book in BOOKS:
        expected = chapter_counts.get(book.folder)
        if expected is None:
            errors.append(f"{book.folder}: no rows in verse_limits.tsv")
            expected = 0
        if f"## {book.folder}\n" not in titles:
            errors.append(f"front/titles.md missing {book.folder}")
        folder = CANON / book.folder
        found = sorted(folder.glob("*.md")) if folder.is_dir() else []
        if len(found) != expected:
            errors.append(f"{book.folder}: {len(found)} chapters, expected {expected}")
        for path in found:
            files += 1
            text = path.read_text(encoding="utf-8")
            if not text.endswith("\n"):
                errors.append(f"{path}: missing final newline")
            header = HEADER_RE.match(text)
            if not header:
                errors.append(f"{path}: bad header")
                continue
            expected = chapter_filename(book.folder, int(header.group(2)))
            if header.group(1) != book.folder or expected != path.name:
                errors.append(f"{path}: header does not match path")
            if re.search(r"(?m)^# ", text):
                errors.append(f"{path}: book title belongs in front/titles.md")
            numbers = [int(n) for n in VERSE_RE.findall(text)]
            if numbers != list(range(1, len(numbers) + 1)):
                errors.append(f"{path}: verse numbers {numbers[:8]}…")
            chapter_number = int(header.group(2))
            maximum = limits.get((book.folder, chapter_number))
            if maximum is None:
                errors.append(f"{path}: no verse limit")
            elif not numbers or numbers[-1] != maximum or len(numbers) != maximum:
                errors.append(
                    f"{path}: {len(numbers)} verses, limit {maximum}"
                )
            verses += len(numbers)
            link = f"](canon/{book.folder}/{path.name})"
            if link not in index:
                errors.append(f"{path}: missing from CANON.md")
            # Raw bracket cues belong only in the archive, not in canon.
            for line in text.splitlines():
                if line.startswith("[^") or line.startswith("<!--"):
                    continue
                if RAW_CUE_RE.search(line):
                    errors.append(f"{path}: raw cue left in line: {line[:80]}")
                    break
            markers: list[str] = []
            defs: list[str] = []
            for line in text.splitlines():
                found = DEF_RE.match(line)
                if found:
                    defs.append(found.group(1))
                else:
                    markers.extend(MARKER_RE.findall(line))
            if markers != defs:
                errors.append(
                    f"{path}: markers {len(markers)} definitions {len(defs)}"
                )
            verse_set = set(numbers)
            for note_index, ident in enumerate(defs):
                parsed = ID_PARTS.match(ident)
                expect = note_letter(note_index)
                if (
                    not parsed
                    or parsed.group(1) != book.usfm
                    or int(parsed.group(2)) != chapter_number
                    or parsed.group(4) != expect
                    or int(parsed.group(3)) not in verse_set
                ):
                    errors.append(
                        f"{path}: note {ident} is not "
                        f"{book.usfm}_{chapter_number}_<verse>_{expect}"
                    )
            for ident in defs:
                if ident in ids:
                    errors.append(f"duplicate id {ident} in {path} and {ids[ident]}")
                else:
                    ids[ident] = str(path.relative_to(ROOT))
            usfm = book.usfm
            for ident in defs:
                if not ident.startswith(usfm + "_"):
                    errors.append(f"{path}: id {ident} is not {usfm}")
    if files != 1189:
        errors.append(f"files {files}, expected 1189")
    print(f"files {files}  verses {verses}  footnotes {len(ids)}  extras {extra_count}")
    for item in errors[:40]:
        print(f"error: {item}", file=sys.stderr)
    if len(errors) > 40:
        print(f"... {len(errors) - 40} more", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
