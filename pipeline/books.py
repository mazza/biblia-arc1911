"""Protestant canon identity shared by edition repositories.

Folder names and USFM codes are the stable tokens. ``chapter_name`` is
the edition's name in each chapter's ``##`` heading. ``title`` is the
1911 book title, written to ``front/titles.md`` and not into the chapter.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    folder: str
    usfm: str
    chapter_name: str
    title: str

    @property
    def order(self) -> int:
        return int(self.folder.split("-", 1)[0])


BOOKS: tuple[Book, ...] = (
    Book("01-GEN", "GEN", "Genesis", "O PRIMEIRO LIVRO DE MOYSÉS CHAMADO GENESIS."),
    Book("02-EXO", "EXO", "Exodo", "O SEGUNDO LIVRO DE MOYSÉS CHAMADO EXODO."),
    Book("03-LEV", "LEV", "Levitico", "O TERCEIRO LIVRO DE MOYSÉS CHAMADO LEVITICO."),
    Book("04-NUM", "NUM", "Numeros", "O QUARTO LIVRO DE MOYSÉS CHAMADO NUMEROS."),
    Book("05-DEU", "DEU", "Deuteronomio", "O QUINTO LIVRO DE MOYSÉS CHAMADO DEUTERONOMIO."),
    Book("06-JOS", "JOS", "Josué", "O LIVRO DE JOSUÉ."),
    Book("07-JDG", "JDG", "Juizes", "O LIVRO DOS JUIZES."),
    Book("08-RUT", "RUT", "Ruth", "O LIVRO DE RUTH."),
    Book("09-1SA", "1SA", "I Samuel", "O PRIMEIRO LIVRO DE SAMUEL."),
    Book("10-2SA", "2SA", "II Samuel", "O SEGUNDO LIVRO DE SAMUEL."),
    Book("11-1KI", "1KI", "I Reis", "O PRIMEIRO LIVRO DOS REIS."),
    Book("12-2KI", "2KI", "II Reis", "O SEGUNDO LIVRO DOS REIS."),
    Book("13-1CH", "1CH", "I Chronicas", "O PRIMEIRO LIVRO DAS CHRONICAS."),
    Book("14-2CH", "2CH", "II Chronicas", "O SEGUNDO LIVRO DAS CHRONICAS."),
    Book("15-EZR", "EZR", "Esdras", "O LIVRO DE ESDRAS."),
    Book("16-NEH", "NEH", "Nehemias", "O LIVRO DE NEHEMIAS."),
    Book("17-EST", "EST", "Esther", "O LIVRO DE ESTHER."),
    Book("18-JOB", "JOB", "Job", "O LIVRO DE JOB."),
    Book("19-PSA", "PSA", "Psalmo", "O LIVRO DOS PSALMOS."),
    Book("20-PRO", "PRO", "Proverbios", "PROVERBIOS DE SALOMÃO."),
    Book("21-ECC", "ECC", "Ecclesiastes", "LIVRO DO ECCLESIASTES, OU PRÉGADOR."),
    Book("22-SNG", "SNG", "Cantico dos Canticos", "CANTARES DE SALOMÃO."),
    Book("23-ISA", "ISA", "Isaias", "ISAIAS."),
    Book("24-JER", "JER", "Jeremias", "JEREMIAS."),
    Book("25-LAM", "LAM", "Lamentações de Jeremias", "LAMENTAÇÕES DE JEREMIAS."),
    Book("26-EZK", "EZK", "Ezequiel", "EZEQUIEL."),
    Book("27-DAN", "DAN", "Daniel", "DANIEL."),
    Book("28-HOS", "HOS", "Oseas", "OSEAS."),
    Book("29-JOL", "JOL", "Joel", "JOEL."),
    Book("30-AMO", "AMO", "Amós", "AMÓS."),
    Book("31-OBA", "OBA", "Obadias", "OBADIAS."),
    Book("32-JON", "JON", "Jonas", "JONAS."),
    Book("33-MIC", "MIC", "Miqueas", "MIQUEAS."),
    Book("34-NAM", "NAM", "Nahum", "NAHUM."),
    Book("35-HAB", "HAB", "Habacuc", "HABACUC."),
    Book("36-ZEP", "ZEP", "Sofonias", "SOFONIAS."),
    Book("37-HAG", "HAG", "Aggeo", "AGGEO."),
    Book("38-ZEC", "ZEC", "Zacharias", "ZACHARIAS."),
    Book("39-MAL", "MAL", "Malachias", "MALACHIAS."),
    Book("41-MAT", "MAT", "S. Mattheus", "O SANCTO EVANGELHO SEGUNDO S. MATTHEUS."),
    Book("42-MRK", "MRK", "S. Marcos", "O SANCTO EVANGELHO SEGUNDO S. MARCOS."),
    Book("43-LUK", "LUK", "S. Lucas", "O SANCTO EVANGELHO SEGUNDO S. LUCAS."),
    Book("44-JHN", "JHN", "S. João", "O SANCTO EVANGELHO SEGUNDO S. JOÃO."),
    Book("45-ACT", "ACT", "Actos", "ACTOS DOS APOSTOLOS."),
    Book("46-ROM", "ROM", "Romanos", "EPISTOLA DE S. PAULO AOS ROMANOS."),
    Book("47-1CO", "1CO", "I Corinthios", "PRIMEIRA EPISTOLA DE S. PAULO APOSTOLO AOS CORINTHIOS."),
    Book("48-2CO", "2CO", "II Corinthios", "SEGUNDA EPISTOLA DE S. PAULO APOSTOLO AOS CORINTHIOS."),
    Book("49-GAL", "GAL", "Galatas", "EPISTOLA DE S. PAULO APOSTOLO AOS GALATAS."),
    Book("50-EPH", "EPH", "Ephesios", "EPISTOLA DE S. PAULO APOSTOLO AOS EPHESIOS."),
    Book("51-PHP", "PHP", "Philippenses", "EPISTOLA DE S. PAULO APOSTOLO AOS PHILIPPENSES."),
    Book("52-COL", "COL", "Colossenses", "EPISTOLA DE S. PAULO APOSTOLO AOS COLOSSENSES."),
    Book("53-1TH", "1TH", "I Thessalonicenses", "PRIMEIRA EPISTOLA DE S. PAULO APOSTOLO AOS THESSALONICENSES."),
    Book("54-2TH", "2TH", "II Thessalonicenses", "SEGUNDA EPISTOLA DE S. PAULO APOSTOLO AOS THESSALONICENSES."),
    Book("55-1TI", "1TI", "I Timotheo", "PRIMEIRA EPISTOLA DE S. PAULO APOSTOLO A TIMOTHEO."),
    Book("56-2TI", "2TI", "II Timotheo", "SEGUNDA EPISTOLA DE S. PAULO APOSTOLO A TIMOTHEO."),
    Book("57-TIT", "TIT", "Tito", "EPISTOLA DE S. PAULO APOSTOLO A TITO."),
    Book("58-PHM", "PHM", "Philemon", "EPISTOLA DE S. PAULO APOSTOLO A PHILEMON."),
    Book("59-HEB", "HEB", "Hebreos", "EPISTOLA DE S. PAULO APOSTOLO AOS HEBREOS."),
    Book("60-JAS", "JAS", "S. Thiago", "EPISTOLA UNIVERSAL DO APOSTOLO S. THIAGO."),
    Book("61-1PE", "1PE", "I S. Pedro", "PRIMEIRA EPISTOLA UNIVERSAL DO APOSTOLO S. PEDRO."),
    Book("62-2PE", "2PE", "II S. Pedro", "SEGUNDA EPISTOLA UNIVERSAL DO APOSTOLO S. PEDRO."),
    Book("63-1JN", "1JN", "I S. João", "PRIMEIRA EPISTOLA UNIVERSAL DO APOSTOLO S. JOÃO."),
    Book("64-2JN", "2JN", "II S. João", "SEGUNDA EPISTOLA DO APOSTOLO S. JOÃO."),
    Book("65-3JN", "3JN", "III S. João", "TERCEIRA EPISTOLA DO APOSTOLO S. JOÃO."),
    Book("66-JUD", "JUD", "S. Judas", "EPISTOLA UNIVERSAL DO APOSTOLO S. JUDAS."),
    Book("67-REV", "REV", "Apocalypse", "APOCALYPSE DO APOSTOLO S. JOÃO."),
)

BY_FOLDER = {b.folder: b for b in BOOKS}
BY_USFM = {b.usfm: b for b in BOOKS}


def books_for(testament: str | None) -> tuple[Book, ...]:
    """Books for one export.

    ``ot`` is folders 01-39, ``nt`` is folders 41-67, and ``None`` is every
    book in ``BOOKS``. Folder 40 is not used.
    """
    if testament is None:
        return BOOKS
    if testament == "ot":
        return tuple(book for book in BOOKS if book.order < 40)
    if testament == "nt":
        return tuple(book for book in BOOKS if book.order > 40)
    raise ValueError(f"unknown testament {testament!r}")


def chapter_filename(folder: str, number: int) -> str:
    """Salmos usa ``001.md``–``150.md``. Os outros livros ficam com dois dígitos."""
    width = 3 if folder == "19-PSA" else 2
    return f"{number:0{width}d}.md"


def note_letter(index: int) -> str:
    """Letra da nota na posição ``index`` dentro do capítulo.

    ``0`` é ``a``, ``25`` é ``z``, ``26`` é ``aa``, ``27`` é ``ab``.
    Uma nota nova desloca as letras das notas seguintes desse capítulo.
    """
    n = index + 1
    chars: list[str] = []
    while n:
        n, rem = divmod(n - 1, 26)
        chars.append(chr(ord("a") + rem))
    return "".join(reversed(chars))
