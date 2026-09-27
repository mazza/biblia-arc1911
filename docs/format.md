# edition-canon/1

Gramática dos repositórios de uma edição (português, inglês, grego ou outra).
O texto visível é o da edição. Os identificadores não dependem da língua.

## Árvore

```text
manifest.json     provenance, URLs, sha256, extras, passos do pipeline
archive/          bytes de upstream, sem edição
prepared/         Markdown contínuo derivado; esta edição não o usa
front/            prefácio e títulos da edição, fora dos capítulos
extra/            ficheiros que não são o texto de leitura; pode não existir
pipeline/         scripts que regeneram canon/ e a Bíblia completa
canon/NN-BBB/CC.md
CANON.md          índice de leitura, gerado
```

`NN` é a ordem protestante com dois dígitos, saltando o 40.
`BBB` é o código USFM (`GEN`, `1SA`, `PSA`, `JHN`, `REV`).
`CC` é o capítulo com dois dígitos (`01.md`). Em Salmos (`19-PSA`) são três dígitos (`001.md`), porque o livro tem 150 capítulos.

Nada em `canon/` se edita à mão. Corre-se o pipeline.

## Caminho

A extração começa na URL. `archive/` guarda esses bytes sem edição. O que o pipeline deriva fica fora de `archive/`.

```text
URL em manifest.json
  → pipeline/fetch_archive.py
  → archive/
  → prepared/          (esta edição: "prepared": [], o passo não corre)
  → pipeline/build_canon.py
  → canon/
  → pipeline/build_bible.py [--original] [--testament ot|nt] [--output CAMINHO]
  → dist/
```

`fetch_archive.py` só volta a descarregar se o sha256 não bater com o manifesto. Nesta edição a URL é a do texto do Gutenberg 62383, e o resultado de leitura é `canon/`. `prepared/` fica na gramática para edições que montam um Markdown contínuo antes dos capítulos. Aqui a lista é vazia e o passo não corre. `extra/` não entra neste caminho: `build_bible.py` não o lê, e `--testament` não parte um ficheiro cujo `scope` é `ot-nt`.

## Ficheiro de capítulo

```markdown
<!--
edition: arc1911
book: 01-GEN
chapter: 1
lang: pt
-->

## Nome na edição 1

### Título de secção da edição

#### Superscrição do salmo, quando a secção já ocupou o nível anterior

[Antes de Christo 4004]

#### (Luc. 3.23-38.)

ALEPH.

**1** Texto com *itálico* e uma nota[^GEN_1_1_a] no sítio da chamada.

[^GEN_1_1_a]: Texto da nota, como na edição.
```

| Peça | Regra |
|---|---|
| Comentário | `edition`, `book`, `chapter`, `lang`. Aqui `lang` é `pt`. `text` é opcional e esta edição omite-o; uma edição cujo corpo ainda é OCR escreve `text: ocr`. |
| `#` | Não entra no capítulo. O título de 1911 está em `front/titles.md`. O prefácio está em `front/preface.md`. O Markdown da Bíblia inteira é que os usa. |
| `##` | Nome do livro nesta edição e o número do capítulo, em todos os ficheiros. |
| `###` | Título de secção. Na transcrição vinha em itálico, numa linha só. |
| `####` | Superscrição do salmo quando o `###` da secção já está nesse bloco. Se o salmo não tem secção, a superscrição fica em `###`. Fica no salmo cuja primeira linha ela precede na transcrição. |
| Data | Linha própria (`[Antes de Christo …]`, `[Anno Domini …]`). Não é nota. |
| Paralelo | `#### (Luc. 3.23-38.)`. Os parênteses guardam a referência para se poder resgatá-la. Uma edição sem paralelos simplesmente não tem esta linha. |
| Acróstico | Linha própria (`ALEPH.`) imediatamente antes do versículo. |
| Versículo | `**N**` no início do parágrafo. Um versículo, um parágrafo. |
| Itálico | `*…*` onde a edição marca palavra acrescentada. |

## Identificador de nota

```text
[^<USFM>_<chapter>_<verse>_<letter>]
```

Exemplo: `[^GEN_1_14_a]`, `[^1SA_20_42_b]`, `[^PSA_23_1_a]`.

- O código USFM é o da pasta, sem o prefixo de ordem (`MAT`, não `41-MAT`, nem o nome do livro na língua da edição).
- Capítulo e versículo são os da edição, sem zero à esquerda. O versículo é o primeiro a que a nota se refere.
- A letra é a ordem das notas naquele capítulo: a primeira é `a`, depois `b`. Depois de `z` vem `aa`, `ab`, `ac`. Uma nota nova no meio do capítulo muda a letra de todas as seguintes. A letra não recomeça em cada versículo e não é a letra impressa na edição.
- Uma chamada impressa num título de secção ancora-se no primeiro versículo dessa secção. A marca fica no título. A nota do título de Jó fica em `front/titles.md`, com o identificador `[^JOB_title_a]`.
- Referências e leituras alternativas entram na mesma sequência. O texto da definição distingue as duas.
- O número ou a letra da chamada na edição (`[12]`, `[AEX]`) não entra no identificador: esse número recomeça em cada capítulo e a letra corre a Bíblia toda. Os dois colidem se os capítulos forem um só Markdown.

O identificador é único dentro da edição. Concatenar `canon/` num único Markdown não repete âncoras.

## Conteúdo extra

`extra/` guarda material publicado com a edição que não é o texto de leitura. `build_bible.py` não o lê. Cada ficheiro é um objeto na lista `extras` de `manifest.json`:

| Campo | Sentido |
|---|---|
| `id` | Token único, em minúsculas, com hífens. |
| `path` | Ficheiro dentro de `extra/`. `extra/README.md` é a nota para pessoas e não entra na lista. |
| `role` | Token do mesmo formato. `morphology` é uma tabela palavra a palavra. |
| `media_type` | Tipo e subtipo, por exemplo `text/tab-separated-values`. |
| `scope` | `ot` (pastas 01-39), `nt` (pastas 41-67) ou `ot-nt` quando o ficheiro cobre os dois. |
| `description` | O que o ficheiro é. |
| `sha256` | Hash dos bytes. |
| `bytes` | Tamanho em bytes. |

`pipeline/verify.py` confere a lista com o diretório, incluindo o hash. Uma edição sem este material publica `"extras": []` e não cria `extra/`. Quando há entradas, `extra/README.md` é obrigatório. O comando `--testament` escolhe capítulos. Um extra declara o seu próprio `scope` e sai inteiro.

## Markdown completo

`build_bible.py` junta `canon/` num Markdown. Com `--original` lê também `front/`.

```bash
python3 pipeline/build_bible.py [--original] [--testament ot|nt] [--output CAMINHO]
```

Sem `--testament`, os dois testamentos. `ot` fica com as pastas 01-39. `nt` fica com as pastas 41-67. A pasta 40 não existe.

Sem `--original`, o título do livro é o nome moderno (`# Gênesis`, `# Salmos`). Com `--original`, o prefácio de 1911 abre o ficheiro e o título do livro é o da edição. Esse prefácio entra também quando a exportação é um testamento só, para o recorte dizer de que edição saiu. A folha «O NOVO TESTAMENTO…» entra só quando o Novo Testamento entra no ficheiro, imediatamente antes de Mateus.

A saída por omissão fica em `dist/`, que não se guarda no Git:

| Opções | Ficheiro |
|---|---|
| *(nenhuma)* | `biblia.md` |
| `--original` | `biblia-original.md` |
| `--testament ot` | `biblia-ot.md` |
| `--testament nt` | `biblia-nt.md` |
| `--original --testament ot` | `biblia-original-ot.md` |
| `--original --testament nt` | `biblia-original-nt.md` |

`--output` troca o caminho e mantém a mesma seleção. O radical aqui é `biblia`. Os sufixos `-original`, `-ot` e `-nt` são os mesmos em todos os repositórios de edição. Uma edição em inglês usa o radical `bible`.
