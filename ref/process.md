# How these translations were produced

This is the long form of the README's *How this was made*. It exists so that the
claim "verified and reviewed by a human" can be checked rather than taken on
faith, and so that anyone picking the work up knows what the rules are.

The short version: a written baseline first, then many rounds of machine
translation and cross-review held to that baseline, mechanical gates on every
round, and a complete human review pass at the end. Not hand translation.

## 1. The baseline, written down before any translating

Two documents govern everything downstream, and they were finished first:

| File | What it fixes |
|:---|:---|
| [`style-guide.md`](style-guide.md) | Rules **R1–R14**: message kinds and their punctuation, fidelity to the original, term choice, spacing, terminal alignment by display width, placeholders, the whitespace and newline contract, what stays untranslated, plural handling, shared strings, change discipline |
| [`phrasebook.tsv`](phrasebook.tsv) | 95 decided phrase rules: an English pattern, the Chinese required for it, and the Chinese **forbidden** for it |
| [`glossary.tsv`](glossary.tsv) | 638 terms, the noun vocabulary |
| [`glossary-pgdoc.tsv`](glossary-pgdoc.tsv) | The PostgreSQL documentation glossary these were aligned to, so a term reads the same in a message and in the docs |
| [`glossary-decisions.tsv`](glossary-decisions.tsv) | Per-term decision log: what the prior translation was, what it became, why, and which messages it touched |

The precedence order is set in the style guide and was followed throughout:
technical correctness including source context, then the style guide, then the
decided phrasebook rows, then the pgdoc glossary, then the NLS glossary, then
whatever the catalog already used consistently, and personal preference last.

`phrasebook.tsv` is where the forbidden wordings live. For example:

```
P01  \bcould not\b   required 无法   forbidden 不能|未能|没能
P04  \bmust not\b    required 不得|不能   forbidden 无法
```

The distinction those two encode — an attempt that failed versus a rule that
forbids — is exactly the kind of thing that drifts when many hands or many
rounds touch the same corpus, which is why it is written down rather than left
to judgement.

## 2. Cross-model translation and review

Each message went through eight to ten rounds of translation and review between
different models (Codex, Astra and Fable 5.1). Each round re-read the previous
round's output against:

- the English original and, where the wording was ambiguous, the calling site in
  the PostgreSQL source;
- the style guide and the phrasebook;
- how the same or a similar English string had been rendered in the other 161
  catalogs and in the other five branches.

Rounds disagreeing with each other is what surfaced most of the wording
problems. Agreement was never treated as proof — it is cheap for models to agree
on a plausible mistranslation.

## 3. Mechanical gates, on every round

Run over the whole set, not a sample:

- `msgfmt --check --check-format` on every file
- placeholder identity, including positional `%n$s` reordering
- plural form counts and the `Plural-Forms` header
- the whitespace, newline and tab contract against the English
- column alignment computed by East Asian display width, since a CJK character
  occupies two terminal columns and copying the original padding breaks the
  columns (see `bin/check-align.py` in the repository root)
- the phrasebook and glossary, as a lint pass with rule IDs, so a finding points
  at the rule it violates

## 4. The human review pass

Every message was then read against its English original, using the workbench at
<https://pgsql.cc/nls>, which shows the English, the existing translation and
the candidate side by side, with similar wordings elsewhere in the corpus and
their real provenance.

What that pass was for is best shown by what it caught in entries upstream had
**not** marked fuzzy, so no tool would have questioned them:

| English | Upstream `zh_CN` | Here |
|:---|:---|:---|
| `views must not contain SELECT INTO` | 视**力**中不能包含 — *eyesight*, not *view* | 视**图**中不得包含 |
| `operator %s is not a valid ordering operator` | 操作符 %s **不时**有效的 — typo for 不是 | 操作符 %s **不是**有效的 |
| `pg_hba.conf rejects connection for host …` | 拒绝……的**复制**连接 — invents *replication* | 拒绝……的连接 |

## Known gaps

Kept here rather than quietly fixed, because a reference that hides its own
loose ends is not much of a reference.

- **`glossary-decisions.tsv` has dangling evidence references.** Its evidence
  column points at `target-links.jsonl`, `term-evidence.jsonl` and similar files
  from the working environment, which are not published — they are large and
  mostly intermediate. The decisions themselves stand on their own.
- **An earlier draft glossary said `cluster` = 集群.** Practice settled on
  集簇 for the storage-level cluster and 聚簇 for the `CLUSTER` command, which
  is the correct distinction; the live corpus uses 集簇 809 times, 聚簇 116, and
  集群 nowhere. See [`errata.md`](errata.md).
- **`multixact "members" limit exceeded`** renders `"members"` as 成员 in five
  files. It is the name of the `pg_multixact/members` storage area and the
  quotes are marking a name, so it should stay untranslated. Listed in
  [`errata.md`](errata.md); not yet fixed.
