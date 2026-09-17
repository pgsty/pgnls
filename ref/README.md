# Reference

The baseline the translations are held to, and the record of how they were made.
Published so the work can be checked, continued or argued with.

| File | What it is | Size |
|:---|:---|---:|
| [`style-guide.md`](style-guide.md) | The style guide. Numbered rules **R1–R14** covering message kinds, fidelity, terminology, punctuation, spacing, terminal alignment, placeholders, the whitespace contract, what stays untranslated, plurals, shared strings and change discipline. Rules are cited by ID in review notes and by the linter. | 35 KB |
| [`phrasebook.tsv`](phrasebook.tsv) | 95 decided phrase rules. Columns: `id`, `en_pattern`, `zh_required`, **`zh_forbidden`**, `scope`, `status`, `note`. This is where the forbidden wordings are recorded. | 7 KB |
| [`glossary.tsv`](glossary.tsv) | 638 terms, English to Chinese. The noun vocabulary for messages. | 17 KB |
| [`glossary-pgdoc.tsv`](glossary-pgdoc.tsv) | The PostgreSQL documentation glossary these were aligned to, so a term reads the same in a message and in the docs. | 17 KB |
| [`glossary-decisions.tsv`](glossary-decisions.tsv) | Per-term decision log: prior translation, decision, reason, scope, affected messages. 15 columns, one row per term. | 461 KB |
| [`process.md`](process.md) | How the translations were produced, in detail: the baseline, the cross-model rounds, the machine gates, the human review pass. | — |
| [`errata.md`](errata.md) | Known defects and documentation drift, open and resolved. | — |

## Reading order

Start with [`process.md`](process.md) for what was done, then
[`style-guide.md`](style-guide.md) for the rules the result is held to. The two
glossaries and the phrasebook are lookup tables rather than prose.

## Precedence

When these disagree, the style guide fixes the order: technical correctness
including the calling site in the PostgreSQL source, then the style guide, then
`phrasebook.tsv` rows marked `decided`, then the pgdoc glossary, then
`glossary.tsv`, then whatever the catalog already used consistently, and
personal preference last.

## Caveats

- `glossary-decisions.tsv` references evidence files from the working
  environment (`target-links.jsonl` and similar) that are not published; those
  columns dangle. The decisions stand without them.
- The phrasebook and glossaries were built for these catalogs. They are not a
  general-purpose PostgreSQL Chinese glossary, and the documentation project's
  own glossary is the authority for prose.
