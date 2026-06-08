# vql


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.2-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.75-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-2.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.7471 (2 commits)
- 👤 **Human dev:** ~$200 (2.0h @ $100/h, 30min dedup)

Generated on 2026-06-08 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

**VQL (Visual Query Language)** — język wektorowego opisu fotografii i rysunków.

Samodzielna paczka Python z IR (`VQLProgram`), kompilatorem NL→VQL, walidacją i rendererami SVG/PNG. Sterowana przez standaryzowany DSL i bus CQRS/ES w paczkach `*2vql`.

## Instalacja

```bash
pip install vql          # core
pip install vql[png]     # eksport PNG (cairosvg)
bash install-dev.sh      # pełny stack dev (*2vql)
```

## Szybki start

```python
from vql import VQLFacade, nl_to_program, render_to_svg

program = nl_to_program("narysuj czerwone koło", width=400, height=400)
svg = render_to_svg(program)
```

```bash
# Control DSL
dsl2vql -c 'COMPILE "narysuj niebieski kwadrat"'
nlp2vql apply "wygeneruj program z kołem" --file app.vql.json
rest2vql serve --port 8216
```

## Struktura monorepo

- `src/vql/` — domena (schema, compiler, renderers, drawing)
- `packages/dsl2vql/` — grammar, schema, protobuf, bus CQRS
- `packages/uri2vql/`, `nlp2vql/`, `cli2vql/`, `mcp2vql/`, `rest2vql/` — adaptery wejścia

Szczegóły: [packages/README.md](packages/README.md)

## License

Licensed under Apache-2.0.
