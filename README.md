# Bíblia ARC1911

Almeida Revista e Corrigida, Lisboa, 1911 (*A Biblia Sagrada*, reimpressão da de 1900), em Markdown. A grafia é a da edição. A estruturação é [CC0 1.0](LICENSE).

O caminho é o mesmo dos outros repositórios de extração: a URL, os bytes em `archive/`, o pipeline, os capítulos em `canon/`. A gramática está em [`docs/format.md`](docs/format.md) (`edition-canon/1`).

```text
https://www.gutenberg.org/cache/epub/62383/pg62383.txt
  → pipeline/fetch_archive.py
  → archive/pg62383.txt
  → pipeline/build_canon.py
  → canon/NN-BBB/CC.md
  → pipeline/build_bible.py
  → dist/biblia.md
```

Os capítulos estão em [CANON.md](CANON.md): um clique no livro, outro no número do capítulo.

| Peça | Onde |
|---|---|
| Upstream | Project Gutenberg [62383](https://www.gutenberg.org/ebooks/62383) |
| Download | `https://www.gutenberg.org/cache/epub/62383/pg62383.txt` |
| Inventário | [`manifest.json`](manifest.json) |
| Capítulos | [CANON.md](CANON.md) |
| Prefácio e títulos | [`front/`](front/) |
| Conferência | [`QUALITY.md`](QUALITY.md) |

## Reconstruir

```bash
python3 pipeline/fetch_archive.py
python3 pipeline/build_canon.py
python3 pipeline/verify.py
python3 pipeline/build_bible.py
python3 pipeline/build_bible.py --original
python3 pipeline/build_bible.py --testament ot
python3 pipeline/build_bible.py --testament nt
python3 pipeline/build_bible.py --original --testament ot
python3 pipeline/build_bible.py --original --testament nt
```

`build_bible.py` junta os capítulos num Markdown só. `--testament ot` fica com as pastas 01-39. `--testament nt` fica com as pastas 41-67. Sem esse argumento, saem os dois. Sem `--original`, os títulos dos livros são os nomes modernos (`# Gênesis`). Com `--original`, entra o prefácio de 1911 e o título de cada livro como na edição. A folha do Novo Testamento entra só quando o Novo Testamento entra no ficheiro. O índice de páginas do volume não entra: gera-se à parte, se for preciso um PDF. A saída vai para `dist/`, que não se guarda no Git. O nome do ficheiro ganha `-original`, `-ot` e `-nt` conforme as opções. `--output` troca esse caminho e mantém a mesma seleção.

Material que não é texto de leitura vai para `extra/` e declara-se na lista `extras` do manifesto. Esta edição não tem. A regra está em [`docs/format.md`](docs/format.md).

`fetch_archive.py` só volta a descarregar se o sha256 não bater com o manifesto.

## Notas

As chamadas da edição (`[1]`, `[A]`, `[AEX]`) são notas de rodapé Markdown. O identificador não usa esse número nem essa letra, porque o número recomeça em cada capítulo e a letra corre a Bíblia toda. A forma estável é:

```text
[^GEN_1_14_a]
```

USFM, capítulo, primeiro versículo a que a nota se refere, e letra. A letra é a ordem das notas naquele capítulo (`a`, `b`, … `z`, `aa`). Uma chamada no título de secção ancora-se no primeiro versículo da secção. Juntar todos os capítulos num Markdown só não repete âncoras.

Referência cruzada e leitura alternativa entram na mesma sequência. O texto da nota é o da edição (*Pro. 8.23*, *ou, estações*).

## O que fica de fora do versículo

Títulos de secção (`###`), datas *Antes de Christo* e *Anno Domini*, paralelos de secção, letras do acróstico em Lamentações, e a superscrição do salmo. Essa superscrição fica no salmo cuja primeira linha ela precede na transcrição: `####` quando já há um `###`, e `###` quando o salmo não tem secção. Nada disto é nota. O título do livro e o prefácio não ficam no capítulo. Estão em [`front/`](front/).

## Licença

Texto de 1911: domínio público. O ficheiro do Gutenberg, com o cabeçalho da licença do ebook, fica em `archive/`. A estruturação e os scripts: [CC0](LICENSE). Ver [`NOTICE.md`](NOTICE.md).
