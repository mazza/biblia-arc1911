#!/usr/bin/env python3
"""Rebuild canon/ from the pinned Project Gutenberg text of ARC1911.

Reads archive/pg62383.txt. Writes one Markdown file per chapter under
canon/<folder>/<chapter>.md. See docs/format.md.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from books import BOOKS, Book, chapter_filename, note_letter  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "archive" / "pg62383.txt"
CANON = ROOT / "canon"
EDITION = "arc1911"

START = "*** START OF THE PROJECT GUTENBERG EBOOK"
END = "*** END OF THE PROJECT GUTENBERG EBOOK"
NT_BANNER_PREFIX = "O NOVO TESTAMENTO DE NOSSO SENHOR JESUS CHRISTO"

CUE_RE = re.compile(r"\[(\d+|[A-Z]{1,3})\]")
VERSE_RE = re.compile(r"^(\d+)\s+(.+)$")
NOTE_RE = re.compile(r"^\[(\d+)\]\s*(.*)$")
ALT_RE = re.compile(r"^\[([A-Z]{1,3})\]\s*(.*)$")
HEADING_RE = re.compile(r"^_(.+)_$")
DATE_RE = re.compile(r"^\[(?:Antes de Christo|Anno Domini).*\]$")
# The transcription prints the psalm's own superscription as its own
# paragraph immediately before that psalm's first line, after the
# section title when there is one.
SUPERSCRIPTION_RE = re.compile(
    r"^(?:Para o cantor-m[oó]r|Psalmo|Maschil|Mictam|Michtham|Michtam|"
    r"Schiggaion|Cantico|Cântico|Oração)\b",
    re.I,
)
ITALIC_RE = re.compile(r"_([^_]+)_")
# A verse sometimes continues in the same Gutenberg paragraph: the next
# verse number follows sentence punctuation ("...mantimento. 5 Não").
EMBEDDED_VERSE_RE = re.compile(r"(?<=[.!?:;])\s+(?=\d{1,3}\s+)")
# Lamentations prints the acrostic name in front of the verse, and on the
# first verse of a later chapter in front of the chapter number.
_ACROSTIC_NAMES = (
    "ALEPH|BETH|GIMEL|DALETH|HE|VAU|ZAIN|HETH|TETH|JOD|CAPH|LAMED|"
    "MEM|NUN|SAMECH|AIN|PE|TSADE|KOPH|COPH|RESCH|SCHIN|TAU"
)
ACROSTIC_RE = re.compile(
    rf"^({_ACROSTIC_NAMES})\.\s+"
    rf"((?:\[(?:\d+|[A-Z]{{1,3}})\]\s+)*)"
    rf"(\d+)\s+(.+)$"
)

# The 1911 print put the Hebrew superscription of psalm N at the foot of
# psalm N-1. Titles may open with the genre or with the director line.
_TITLE_START = (
    r"(?:Para o cantor-m[oó]r|"
    r"Psalmo|Maschil|Mictam|Michtham|Michtam|Schiggaion|"
    r"Cantico|Cântico|Oração)"
)
PSALM_TITLE_RE = re.compile(
    rf"^(?P<body>.*?)(?:\s+)(?P<title>{_TITLE_START}\b.*)$",
    re.S,
)


@dataclass
class Verse:
    number: int
    text: str
    furniture: list[tuple[str, str]] = field(default_factory=list)
    superscription: str | None = None


@dataclass
class Chapter:
    book: Book
    number: int
    verses: list[Verse] = field(default_factory=list)
    notes: dict[str, str] = field(default_factory=dict)


def paragraphs(text: str) -> list[str]:
    start = text.find(START)
    end = text.find(END)
    if start < 0 or end < 0:
        raise SystemExit("Project Gutenberg START/END markers not found")
    body = text[start:end]
    out: list[str] = []
    for block in re.split(r"\n\s*\n", body):
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        out.append(re.sub(r"\s+", " ", " ".join(lines)).strip())
    return out


PARALLEL_RE = re.compile(
    r"^(?:[1-3]\s+)?[A-ZÁÉÍÓÚÂÊÔÃÕ][A-Za-zÁÉÍÓÚÂÊÔÃÕáéíóúâêôãõç.]*\..*\d"
)


def italics(text: str) -> str:
    return ITALIC_RE.sub(r"*\1*", text)


def _find_chapter(chapters: list[Chapter], folder: str, number: int) -> Chapter:
    for chapter in chapters:
        if chapter.book.folder == folder and chapter.number == number:
            return chapter
    raise SystemExit(f"missing chapter {folder} {number}")


def _find_verse(chapter: Chapter, number: int) -> Verse:
    for verse in chapter.verses:
        if verse.number == number:
            return verse
    raise SystemExit(f"missing verse {chapter.book.folder} {chapter.number}:{number}")


def align_verse_limits(chapters: list[Chapter]) -> list[str]:
    """Make each chapter end on the Protestant verse maximum.

    The words stay the transcription's. Three closing sentences were given
    their own number; they join the verse the maximum still includes.
    Two sentences that the maximum numbers apart were printed inside the
    neighbouring verse; they are split at that sentence boundary.
    """
    notes: list[str] = []

    def join(folder: str, chapter_number: int, extra: int) -> None:
        chapter = _find_chapter(chapters, folder, chapter_number)
        previous = _find_verse(chapter, extra - 1)
        current = _find_verse(chapter, extra)
        previous.text = f"{previous.text} {current.text}".strip()
        chapter.verses = [verse for verse in chapter.verses if verse.number != extra]
        notes.append(f"{folder} {chapter_number}:{extra} joined into {extra - 1}")

    join("07-JDG", 5, 32)
    join("09-1SA", 20, 43)
    join("11-1KI", 22, 54)

    chapter = _find_chapter(chapters, "48-2CO", 13)
    verse = _find_verse(chapter, 12)
    head, separator, tail = verse.text.partition(". ")
    if separator != ". " or not tail.startswith("Todos os sanctos"):
        raise SystemExit(f"2 Cor 13:12 did not split cleanly: {verse.text!r}")
    verse.text = head + "."
    for item in chapter.verses:
        if item.number >= 13:
            item.number += 1
    index = next(i for i, item in enumerate(chapter.verses) if item.number == 12)
    chapter.verses.insert(index + 1, Verse(13, tail))
    notes.append("48-2CO 13:12 split; benediction is 14")

    chapter13 = _find_chapter(chapters, "67-REV", 13)
    first = _find_verse(chapter13, 1)
    prefix = "E eu puz-me sobre a areia do mar, "
    if not first.text.startswith(prefix):
        raise SystemExit(f"Rev 13:1 did not split cleanly: {first.text!r}")
    first.text = first.text[len(prefix) :]
    chapter12 = _find_chapter(chapters, "67-REV", 12)
    chapter12.verses.append(Verse(18, "E eu puz-me sobre a areia do mar"))
    notes.append("67-REV 12:18 taken from the opening clause of 13:1")
    return notes


def peel_psalm_titles(chapters: list[Chapter]) -> int:
    by_num = {ch.number: ch for ch in chapters}
    moved = 0
    for n in range(1, 150):
        chapter = by_num.get(n)
        nxt = by_num.get(n + 1)
        if chapter is None or nxt is None or not chapter.verses or not nxt.verses:
            continue
        last = chapter.verses[-1]
        match = PSALM_TITLE_RE.match(last.text.strip())
        if not match:
            continue
        body = match.group("body").strip()
        title = match.group("title").strip()
        if not body or not title:
            continue
        last.text = body
        target = nxt.verses[0]
        if target.superscription:
            target.superscription = f"{target.superscription} {title}"
        else:
            target.superscription = title
        moved += 1
    return moved


def split_verse_paragraph(
    para: str,
) -> list[tuple[str | None, int, str]] | None:
    """Return (acrostic, printed number, text) pieces, or None."""
    acrostic = None
    match = ACROSTIC_RE.match(para)
    if match:
        acrostic = match.group(1)
        number = int(match.group(3))
        rest = (match.group(2) + match.group(4)).strip()
    else:
        match = VERSE_RE.match(para)
        if not match:
            return None
        number = int(match.group(1))
        rest = match.group(2).strip()
    chunks = EMBEDDED_VERSE_RE.split(rest)
    pieces: list[tuple[str | None, int, str]] = [(acrostic, number, chunks[0].strip())]
    for chunk in chunks[1:]:
        embedded = re.match(r"(\d{1,3})\s+(.*)$", chunk.strip())
        if not embedded:
            prev = pieces[-1]
            pieces[-1] = (prev[0], prev[1], f"{prev[2]} {chunk}".strip())
            continue
        pieces.append((None, int(embedded.group(1)), embedded.group(2).strip()))
    return pieces


def title_marker(para: str, title: str) -> str | None:
    """Return ``""`` when ``para`` is the book title, the alt-note key when
    the title carries a leading cue, or ``None`` when it is not the title.
    """
    if para == title:
        return ""
    match = re.fullmatch(rf"\[([A-Z]{{1,3}})\] {re.escape(title)}", para)
    if match:
        return match.group(1)
    return None


def parse(
    text: str,
) -> tuple[list[Chapter], dict[str, str], dict[str, str], str | None, list[str], list[str]]:
    chapters: list[Chapter] = []
    alts: dict[str, str] = {}
    title_cues: dict[str, str] = {}
    warnings: list[str] = []
    notices: list[str] = []
    banner: str | None = None
    next_book = 0
    book: Book | None = None
    chapter: Chapter | None = None
    expected: int | None = None
    in_notes = False
    pending: list[tuple[str, str]] = []
    mode = "body"

    def take(number: int, verse_text: str, *, new_chapter: bool, acrostic: str | None) -> None:
        nonlocal chapter, expected, in_notes
        if book is None:
            raise RuntimeError("verse outside a book")
        furniture = list(pending)
        pending.clear()
        if acrostic:
            furniture.append(("acrostic", acrostic))
        if new_chapter:
            if chapter is not None and number != chapter.number + 1:
                warnings.append(
                    f"{book.folder}: chapter {number} follows {chapter.number}"
                )
            chapter = Chapter(book, number)
            chapters.append(chapter)
            chapter.verses.append(Verse(1, verse_text, furniture=furniture))
            expected = 2
        else:
            if chapter is None:
                raise RuntimeError("verse outside a chapter")
            chapter.verses.append(Verse(number, verse_text, furniture=furniture))
            expected = number + 1
        in_notes = False

    def following_number(paras: list[str], start: int) -> int | None:
        for para in paras[start:]:
            if para == "NOTAS":
                return None
            if next_book < len(BOOKS) and title_marker(para, BOOKS[next_book].title) is not None:
                return None
            if NOTE_RE.match(para):
                return None
            pieces = split_verse_paragraph(para)
            if pieces:
                return pieces[0][1]
        return None

    def accept_number(
        number: int,
        rest: str,
        acrostic: str | None,
        following: int | None,
    ) -> None:
        """Decide whether ``number`` opens a chapter or continues a verse.

        The edition prints chapter 1 as ``1 <verse>``, and every later
        chapter as ``<chapter> <verse 1>`` with the verse number omitted.
        A following paragraph numbered 2 is that signal. A following
        paragraph numbered expected+1 keeps this line in the same chapter;
        if the printed number disagrees, the print is off by a digit and
        the sequential number is the verse address.
        """
        if chapter is None:
            if number == 1:
                take(1, rest, new_chapter=True, acrostic=acrostic)
            else:
                take(number, rest, new_chapter=True, acrostic=acrostic)
            return
        opens_chapter = following == 2 and not (number == 1 and expected == 1)
        if opens_chapter or in_notes:
            take(number, rest, new_chapter=True, acrostic=acrostic)
            return
        if following == (expected or 0) + 1 or following is None:
            if number != expected:
                notices.append(
                    f"{book.folder} {chapter.number}: printed verse {number} "
                    f"read as {expected}"
                )
            take(expected or number, rest, new_chapter=False, acrostic=acrostic)
            return
        if number != expected:
            take(number, rest, new_chapter=True, acrostic=acrostic)
            return
        take(number, rest, new_chapter=False, acrostic=acrostic)

    paras = paragraphs(text)
    index = 0
    while index < len(paras):
        para = paras[index]
        index += 1
        if mode == "notas":
            alt = ALT_RE.match(para)
            if alt:
                key, body = alt.group(1), alt.group(2).strip()
                if key in alts:
                    warnings.append(f"duplicate alt note [{key}]")
                alts[key] = body
            continue

        if para == "NOTAS":
            mode = "notas"
            book = None
            chapter = None
            continue

        if next_book < len(BOOKS):
            marker = title_marker(para, BOOKS[next_book].title)
            if marker is not None:
                book = BOOKS[next_book]
                next_book += 1
                chapter = None
                expected = None
                in_notes = False
                if marker:
                    title_cues[book.folder] = marker
                lost = [item for item in pending if item[0] in {"heading", "date"}]
                if lost:
                    warnings.append(f"furniture left before {book.folder}")
                pending.clear()
                continue

        if para.startswith(NT_BANNER_PREFIX):
            banner = para
            continue

        if book is None:
            continue

        heading = HEADING_RE.match(para)
        if heading:
            pending.append(("heading", heading.group(1).strip()))
            continue
        if DATE_RE.match(para):
            pending.append(("date", para))
            continue

        note = NOTE_RE.match(para)
        if note and chapter is not None and chapter.verses:
            key, body = note.group(1), note.group(2).strip()
            if key in chapter.notes:
                warnings.append(
                    f"{book.folder} {chapter.number}: duplicate xref [{key}]"
                )
            chapter.notes[key] = body
            in_notes = True
            continue

        pieces = split_verse_paragraph(para)
        if pieces:
            for offset, (acrostic, number, rest) in enumerate(pieces):
                if offset + 1 < len(pieces):
                    nxt = pieces[offset + 1][1]
                else:
                    nxt = following_number(paras, index)
                accept_number(number, rest, acrostic, nxt)
            continue

        pending.append(("extra", para))

    if next_book != len(BOOKS):
        missing = ", ".join(b.folder for b in BOOKS[next_book:])
        warnings.append(f"books not found: {missing}")
    if any(item[0] in {"heading", "date"} for item in pending):
        warnings.append(f"furniture left at end ({len(pending)})")
    return chapters, alts, title_cues, banner, warnings, notices


def apply_cues(
    text: str,
    usfm: str,
    chapter: int,
    verse: int,
    counter: list[int],
    footnotes: list[tuple[str, str]],
    xref_notes: dict[str, str],
    alts: dict[str, str],
    missing: list[str],
) -> str:
    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key.isdigit():
            body = xref_notes.get(key)
            kind = "xref"
        else:
            body = alts.get(key)
            kind = "alt"
        if body is None:
            missing.append(f"{usfm} {chapter}:{verse} [{key}] ({kind})")
            body = ""
        ident = f"{usfm}_{chapter}_{verse}_{note_letter(counter[0])}"
        counter[0] += 1
        footnotes.append((ident, italics(body)))
        return f"[^{ident}]"

    text = CUE_RE.sub(repl, italics(text))
    # The transcription writes "word [cue];". The marker replaces the cue
    # and stays against the word when punctuation follows.
    return re.sub(r"\s+(\[\^[^\]]+\])(?=[,.;:!?])", r"\1", text)


def write_edition_titles(
    banner: str | None,
    title_cues: dict[str, str],
    alts: dict[str, str],
    missing: list[str],
) -> None:
    """Keep the 1911 book titles out of the chapter files."""
    from books import BOOKS

    front = ROOT / "front"
    front.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Títulos da edição",
        "",
        "Não entram nos capítulos. `pipeline/build_bible.py --original` volta a pô-los.",
        "",
    ]
    if banner:
        lines.extend(["## Novo Testamento", "", banner, ""])
    for book in BOOKS:
        lines.extend([f"## {book.folder}", ""])
        cue = title_cues.get(book.folder)
        if cue:
            body = alts.get(cue, "")
            if not body:
                missing.append(f"{book.usfm} title [{cue}]")
            ident = f"{book.usfm}_title_a"
            lines.append(f"[^{ident}] {book.title}")
            lines.append("")
            lines.append(f"[^{ident}]: {italics(body)}")
            lines.append("")
        else:
            lines.extend([book.title, ""])
    (front / "titles.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def render_chapter(
    chapter: Chapter,
    alts: dict[str, str],
    missing: list[str],
) -> str:
    book = chapter.book
    lines: list[str] = [
        "<!--",
        f"edition: {EDITION}",
        f"book: {book.folder}",
        f"chapter: {chapter.number}",
        "lang: pt",
        "-->",
        "",
    ]
    footnotes: list[tuple[str, str]] = []
    lines.append(f"## {book.chapter_name} {chapter.number}")
    lines.append("")
    counter = [0]

    for verse in chapter.verses:

        def convert(text: str, verse_number: int = verse.number) -> str:
            return apply_cues(
                text,
                book.usfm,
                chapter.number,
                verse_number,
                counter,
                footnotes,
                chapter.notes,
                alts,
                missing,
            )

        title_level = 3
        for kind, text in verse.furniture:
            superscription = (
                kind == "extra"
                and book.usfm == "PSA"
                and SUPERSCRIPTION_RE.match(text)
            )
            if kind == "heading" or superscription:
                lines.append(f"{'#' * title_level} {convert(text)}")
                lines.append("")
                title_level = min(title_level + 1, 4)
            elif kind == "date":
                lines.append(text)
                lines.append("")
            elif kind == "acrostic":
                label = text if text.endswith(".") else f"{text}."
                lines.append(label)
                lines.append("")
            else:
                rendered = convert(text).strip()
                if PARALLEL_RE.match(text.strip()):
                    lines.append(f"#### ({rendered})")
                else:
                    lines.append(rendered)
                lines.append("")
        if verse.superscription:
            lines.append(f"{'#' * title_level} {convert(verse.superscription)}")
            lines.append("")
        lines.append(f"**{verse.number}** {convert(verse.text)}")
        lines.append("")

    if footnotes:
        for ident, body in footnotes:
            lines.append(f"[^{ident}]: {body}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# Navigation names. The chapter files keep the edition's own spelling.
PT_NAME = {
    "01-GEN": "Gênesis",
    "02-EXO": "Êxodo",
    "03-LEV": "Levítico",
    "04-NUM": "Números",
    "05-DEU": "Deuteronômio",
    "06-JOS": "Josué",
    "07-JDG": "Juízes",
    "08-RUT": "Rute",
    "09-1SA": "1 Samuel",
    "10-2SA": "2 Samuel",
    "11-1KI": "1 Reis",
    "12-2KI": "2 Reis",
    "13-1CH": "1 Crônicas",
    "14-2CH": "2 Crônicas",
    "15-EZR": "Esdras",
    "16-NEH": "Neemias",
    "17-EST": "Ester",
    "18-JOB": "Jó",
    "19-PSA": "Salmos",
    "20-PRO": "Provérbios",
    "21-ECC": "Eclesiastes",
    "22-SNG": "Cântico dos Cânticos",
    "23-ISA": "Isaías",
    "24-JER": "Jeremias",
    "25-LAM": "Lamentações",
    "26-EZK": "Ezequiel",
    "27-DAN": "Daniel",
    "28-HOS": "Oseias",
    "29-JOL": "Joel",
    "30-AMO": "Amós",
    "31-OBA": "Obadias",
    "32-JON": "Jonas",
    "33-MIC": "Miqueias",
    "34-NAM": "Naum",
    "35-HAB": "Habacuque",
    "36-ZEP": "Sofonias",
    "37-HAG": "Ageu",
    "38-ZEC": "Zacarias",
    "39-MAL": "Malaquias",
    "41-MAT": "Mateus",
    "42-MRK": "Marcos",
    "43-LUK": "Lucas",
    "44-JHN": "João",
    "45-ACT": "Atos",
    "46-ROM": "Romanos",
    "47-1CO": "1 Coríntios",
    "48-2CO": "2 Coríntios",
    "49-GAL": "Gálatas",
    "50-EPH": "Efésios",
    "51-PHP": "Filipenses",
    "52-COL": "Colossenses",
    "53-1TH": "1 Tessalonicenses",
    "54-2TH": "2 Tessalonicenses",
    "55-1TI": "1 Timóteo",
    "56-2TI": "2 Timóteo",
    "57-TIT": "Tito",
    "58-PHM": "Filemom",
    "59-HEB": "Hebreus",
    "60-JAS": "Tiago",
    "61-1PE": "1 Pedro",
    "62-2PE": "2 Pedro",
    "63-1JN": "1 João",
    "64-2JN": "2 João",
    "65-3JN": "3 João",
    "66-JUD": "Judas",
    "67-REV": "Apocalipse",
}


def chapter_row(folder: str, numbers: list[int]) -> str:
    cells = [f"[{n}](canon/{folder}/{chapter_filename(folder, n)})" for n in numbers]
    cells.extend("" for _ in range(10 - len(cells)))
    return "| " + " | ".join(cells) + " |"


def write_canon_index() -> None:
    """Write CANON.md from the chapter files that exist."""
    from books import BOOKS

    present: list[tuple[Book, list[int]]] = []
    for book in BOOKS:
        folder = CANON / book.folder
        if not folder.is_dir():
            continue
        numbers = sorted(
            int(path.stem) for path in folder.glob("*.md") if path.stem.isdigit()
        )
        if numbers:
            present.append((book, numbers))
    lines = [
        "# Cânone",
        "",
        "Cada número abre o capítulo.",
        "",
    ]
    for book, numbers in present:
        lines.append(f"## {PT_NAME[book.folder]}")
        lines.append("")
        # The first ten chapters are the header row. A Markdown table
        # needs one, and an empty header is only there to satisfy that.
        width = min(10, len(numbers))
        head = chapter_row(book.folder, numbers[:width])
        # chapter_row pads to 10; trim when the book has fewer chapters.
        if width < 10:
            cells = [
                f"[{n}](canon/{book.folder}/{chapter_filename(book.folder, n)})"
                for n in numbers
            ]
            head = "| " + " | ".join(cells) + " |"
        lines.append(head)
        lines.append("|" + "|".join("---" for _ in range(width)) + "|")
        for start in range(width, len(numbers), 10):
            lines.append(chapter_row(book.folder, numbers[start : start + 10]))
        lines.append("")
    (ROOT / "CANON.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    if not ARCHIVE.is_file():
        print(f"missing {ARCHIVE}", file=sys.stderr)
        print("run: python3 pipeline/fetch_archive.py", file=sys.stderr)
        return 1
    text = ARCHIVE.read_text(encoding="utf-8")
    chapters, alts, title_cues, banner, warnings, notices = parse(text)
    notices.extend(align_verse_limits(chapters))
    missing: list[str] = []
    write_edition_titles(banner, title_cues, alts, missing)
    psalms = [ch for ch in chapters if ch.book.usfm == "PSA"]
    moved = peel_psalm_titles(psalms)
    written = 0
    # Drop a previous canon so a shrunk chapter cannot linger.
    if CANON.exists():
        for path in CANON.rglob("*.md"):
            path.unlink()
    for chapter in chapters:
        dest = CANON / chapter.book.folder / chapter_filename(
            chapter.book.folder, chapter.number
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            render_chapter(chapter, alts, missing),
            encoding="utf-8",
        )
        written += 1
    write_canon_index()
    verses = sum(len(ch.verses) for ch in chapters)
    print(
        f"chapters {written}  verses {verses}  alt-notes {len(alts)}  "
        f"psalm-titles moved {moved}",
        file=sys.stderr,
    )
    for item in notices:
        print(f"notice: {item}", file=sys.stderr)
    for item in warnings:
        print(f"warning: {item}", file=sys.stderr)
    if missing:
        print(f"missing note texts: {len(missing)}", file=sys.stderr)
        for item in missing[:20]:
            print(f"  {item}", file=sys.stderr)
    if warnings or missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
