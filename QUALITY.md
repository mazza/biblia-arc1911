# Qualidade

Regenerado de `archive/pg62383.txt` (Project Gutenberg 62383, sha256
`bf9c6053…`). A conferência é `python3 pipeline/verify.py`.

| Conferência | Resultado |
|---|---|
| 66 livros, 1 189 capítulos | passa |
| Cada capítulo acaba no limite protestante de `pipeline/verse_limits.tsv` | passa |
| Versículos seguidos a partir de 1 | passa |
| Notas `[^USFM_chapter_verse_letter]` únicas em todo o cânone | passa |
| Cada chamada tem uma definição no mesmo ficheiro | passa |
| Nenhuma chamada crua `[12]` ou `[A]` no Markdown | passa |
| Nenhum título de livro dentro de `canon/` | passa |
| `CANON.md` liga cada capítulo que existe | passa |
| `front/titles.md` tem os 66 títulos | passa |

São 31 104 versículos e 21 359 notas nos capítulos. A nota do título de Jó está em `front/titles.md` (`[^JOB_title_a]`).

Cinco fronteiras da transcrição do Gutenberg não caíam nesse limite. As palavras ficam. Só o número muda:

| Lugar | Ajuste |
|---|---|
| Juízes 5 | A frase final junta-se ao versículo 31. A transcrição numerava-a 32. |
| 1 Samuel 20 | A frase final junta-se ao versículo 42. A transcrição numerava-a 43. |
| 1 Reis 22 | A frase final junta-se ao versículo 53. A transcrição numerava-a 54. |
| 2 Coríntios 13 | *Todos os sanctos vos saudam* é o 13. A bênção é o 14. A transcrição metia as duas saudações no 12 e a bênção no 13. |
| Apocalipse 12 | *E eu puz-me sobre a areia do mar* é o 12:18. A transcrição abria o capítulo 13 com essa oração. |

3 João conserva o versículo 15. O limite é 15.

Marcos 4: a transcrição imprime `31` entre o 33 e o 35. O texto é o do versículo 34, e o cânone trata-o como 34. O ficheiro do Gutenberg não foi alterado.

A superscrição do salmo fica no salmo cuja primeira linha ela precede. Lamentações conserva os nomes do acróstico (`ALEPH.`, `BETH.`, …). Títulos de secção, datas, itálico e referências ficam na grafia da transcrição.

Isto não é edição crítica nem modernização. *Fórma* e *abysmo* são o texto de 1911. O Gutenberg avisa que algumas referências estão erradas. Ficaram como na transcrição.
