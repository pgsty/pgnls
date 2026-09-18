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

## Traditional Chinese (zh_TW) reference set

Three sibling files re-calibrate the whole system for Traditional Chinese.
The structural rules (message kinds, punctuation layers, alignment,
placeholders) carry over from the Simplified guide unchanged; the terminology,
orthography and word-choice layers are re-decided against the official
in-tree PostgreSQL `zh_TW` messages (psql, pg_dump, initdb, pg_ctl, libpq —
the backend `postgres.po` has no official zh_TW yet) and Taiwan-standard
computing usage. See the intro of [`style-guide-tw.md`](style-guide-tw.md)
for what diverges and why.

| File | What it is |
|:---|:---|
| [`style-guide-tw.md`](style-guide-tw.md) | The zh_TW style guide: rules **R0–R14**. R0 is the TW-only calibration layer — Taiwan orthography, the high-frequency word table, the row/column/筆 rules, the simplified→traditional bootstrap pipeline with its forbidden-artifact list, and the alignment duty towards the five officially translated components. Appendix B lists every decision that differs from the Simplified guide with its evidence. |
| [`glossary-tw.tsv`](glossary-tw.tsv) | 638 terms, three columns of interest: `English`, `zh_CN`, `zh_TW`, plus an evidence grade: **官方 68** (the decided word-form itself occurs in the official zh_TW messages), **官方推定 121** (component terms officially evidenced, compound derived), **MS 281**, **裁定 48**, **字符 119**. The `zh_CN`→`zh_TW` columns are the complete term mapping — but only for a single-pass longest-first engine with protected spans, never a sequential sed chain (19 target-contains-source chains would corrupt), and single-character rows (表/行/列/位/块/堆/页/锁) are glossary entries, not string replacements. See R0.4 of the TW guide. |
| [`phrasebook-tw.tsv`](phrasebook-tw.tsv) | The 95 phrase rules re-decided for zh_TW. The forbidden column doubles as the machine-conversion artifact blocklist (運算符、排序規則、死鎖、遊標、保存點、主頁、集群、外部表、使用者對應…). |

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
