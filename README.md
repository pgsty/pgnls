<div align="center">

# PostgreSQL Simplified Chinese Message Catalogs

**Complete `zh_CN` translations for PostgreSQL 14 – 19**

[![Review Workbench](https://img.shields.io/badge/Review_Workbench-pgsql.cc%2Fnls-2f6fa3?style=for-the-badge&logo=postgresql&logoColor=white)](https://pgsql.cc/nls)

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14--19-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Messages](https://img.shields.io/badge/messages-67%2C489-informational)](https://pgsql.cc/nls)
[![Translated](https://img.shields.io/badge/translated-100%25-brightgreen)](https://pgsql.cc/nls)
[![Fuzzy](https://img.shields.io/badge/fuzzy-0-brightgreen)](https://pgsql.cc/nls)
[![msgfmt](https://img.shields.io/badge/msgfmt-clean-brightgreen)](https://www.gnu.org/software/gettext/)
[![License](https://img.shields.io/badge/license-PostgreSQL-blue)](LICENSE)

</div>

**162 files, 67,489 messages, 100% translated, zero fuzzy, zero untranslated** — every file clean under `msgfmt --check --check-format`.

The `zh_CN` catalogs currently in `pgtranslation/messages.git` date from 2019; their headers still read `Project-Id-Version: postgres (PostgreSQL) 12`. Across PostgreSQL 14 – 19 they carry a reviewed translation for 77.1% of messages; of the remaining 15,475, some 11,770 are fuzzy entries that babel matched by similarity and 3,705 are empty. This repository is a complete set rebuilt from the current templates, with terminology held to a single glossary shared across all catalogs and all six branches, and every message verified against its English original. How that was done is spelled out in [How this was made](#how-this-was-made).

## Review Workbench

Every message is browsable at **<https://pgsql.cc/nls>** — the English original, the existing translation and the calibrated translation side by side, filterable by catalog, full-text searchable, with the real provenance of similar wordings. Corrections and second opinions are welcome there.

<div align="center">

| Upstream branch | PG | Catalogs | Messages | Upstream | Here | Workbench | Issue | Download |
|:---|:---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| [`master`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/master) | 19 | 28 | 12,638 | 65.3% | **100%** | [browse](https://pgsql.cc/nls/?v=19) | [#8123](https://redmine.postgresql.org/issues/8123) | [`tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-master-20260917.tar.gz) |
| [`REL_18_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_18_STABLE) | 18 | 28 | 12,098 | 69.9% | **100%** | [browse](https://pgsql.cc/nls/?v=18) | [#8118](https://redmine.postgresql.org/issues/8118) | [`tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_18_STABLE-20260917.tar.gz) |
| [`REL_17_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_17_STABLE) | 17 | 28 | 11,509 | 74.9% | **100%** | [browse](https://pgsql.cc/nls/?v=17) | [#8119](https://redmine.postgresql.org/issues/8119) | [`tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_17_STABLE-20260917.tar.gz) |
| [`REL_16_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_16_STABLE) | 16 | 26 | 10,656 | 79.0% | **100%** | [browse](https://pgsql.cc/nls/?v=16) | [#8120](https://redmine.postgresql.org/issues/8120) | [`tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_16_STABLE-20260917.tar.gz) |
| [`REL_15_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_15_STABLE) | 15 | 26 | 10,463 | 85.7% | **100%** | [browse](https://pgsql.cc/nls/?v=15) | [#8121](https://redmine.postgresql.org/issues/8121) | [`tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_15_STABLE-20260917.tar.gz) |
| [`REL_14_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_14_STABLE) | 14 | 26 | 10,125 | 91.8% | **100%** | [browse](https://pgsql.cc/nls/?v=14) | [#8122](https://redmine.postgresql.org/issues/8122) | [`tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_14_STABLE-20260917.tar.gz) |

</div>

The branch names link to the same catalogs as they stand today in the upstream translation repository, `pgtranslation/messages.git`:

```bash
git clone https://git.postgresql.org/git/pgtranslation/messages.git
```

PostgreSQL 19 lives on `master` there; there is no `REL_19_STABLE`. From PG17 on there are two extra catalogs, `pg_combinebackup` and `pg_walsummary` — of which `pg_combinebackup` is a new file for `zh_CN`.

## Download

Release [`20260917`](https://github.com/pgsty/pgnls/releases/tag/20260917) carries one archive per
upstream branch plus the whole set. Each unpacks to `zh_CN/<branch>/<catalog>.po`, so a
branch directory drops straight into `messages.git`.

| Archive | Covers | Catalogs | Messages |
|:---|:---|---:|---:|
| [`pg-messages-zh_CN-20260917.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-20260917.tar.gz) | **all six branches** | 162 | 67,487 |
| [`pg-messages-zh_CN-master-20260917.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-master-20260917.tar.gz) | PostgreSQL 19 | 28 | 12,636 |
| [`pg-messages-zh_CN-REL_18_STABLE-20260917.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_18_STABLE-20260917.tar.gz) | PostgreSQL 18 | 28 | 12,098 |
| [`pg-messages-zh_CN-REL_17_STABLE-20260917.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_17_STABLE-20260917.tar.gz) | PostgreSQL 17 | 28 | 11,509 |
| [`pg-messages-zh_CN-REL_16_STABLE-20260917.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_16_STABLE-20260917.tar.gz) | PostgreSQL 16 | 26 | 10,656 |
| [`pg-messages-zh_CN-REL_15_STABLE-20260917.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_15_STABLE-20260917.tar.gz) | PostgreSQL 15 | 26 | 10,463 |
| [`pg-messages-zh_CN-REL_14_STABLE-20260917.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_14_STABLE-20260917.tar.gz) | PostgreSQL 14 | 26 | 10,125 |

```bash
curl -LO https://github.com/pgsty/pgnls/releases/download/20260917/pg-messages-zh_CN-REL_18_STABLE-20260917.tar.gz
tar -xzf pg-messages-zh_CN-REL_18_STABLE-20260917.tar.gz
cp zh_CN/REL_18_STABLE/*.po /path/to/messages/zh_CN/
```

Checksums for every archive are in `SHA256SUMS` on the same release page.

## Layout

```
zh_CN/<branch>/<catalog>.po       162 catalogs, one directory per upstream branch
ref/                              style guide, phrasebook, glossaries, process, errata
bin/                              standalone tools; Python 3 and GNU gettext only
Makefile                          the usual operations
LICENSE                           the PostgreSQL License, verbatim from postgres.git
```

## Usage

```
make check            validate all 162 catalogs (msgfmt, completeness, headers, alignment)
make stats            message counts per catalog per branch
make mo               compile to .mo under build/
make dist             release assets: six branch zips, a tarball, SHA256SUMS
make fetch-upstream   pull a fresh zh_CN snapshot from babel into tmp/
make diff             compare zh_CN/ against that snapshot: msgid drift and coverage
make check-align      column alignment by East Asian display width, on its own
make show BRANCH=master CATALOG=psql
make clean
```

To land these in `messages.git`, check out the matching branch and overwrite `zh_CN/`:

```bash
cp zh_CN/REL_18_STABLE/*.po /path/to/messages/zh_CN/
```

The zips from `make dist` use the flat `<catalog>-zh_CN.po` naming the Redmine patch tracker asks for — same bytes as `zh_CN/`, different filenames. The tarball keeps this repository's layout.

## History

The first commit holds the catalogs exactly as they stand upstream, merged by
babel against each branch's current POT so the message sets already match. Every
commit after it calibrates one catalog across all of its branches, so the diff
for any component reads on its own:

```bash
git log --oneline                          # one commit per catalog
git show <commit>                          # what changed in that catalog
git diff $(git rev-list --max-parents=0 HEAD) -- zh_CN/master/psql.po
```

## How this was made

Machine-assisted translation, verified and reviewed by a human — not hand
translation, which is what the `pgsql-translators` thread was told before any of
it started.

A glossary and style guide were fixed first. Each message then went through eight
to ten rounds of translation and cross-review between models (Codex, Astra,
Fable 5.1), every round held to that baseline and gated on `msgfmt`, placeholder,
plural and column-alignment checks. A complete human review pass came last,
message by message against the English, on the workbench.

The baseline is published in [`ref/`](ref/): the style guide (rules R1–R14), the
phrasebook (95 rules, each with the required and forbidden Chinese), two
glossaries and the per-term decision log. [`ref/process.md`](ref/process.md) has
the long version; [`ref/errata.md`](ref/errata.md) has the known defects.

## File handling

- **Templates** — the babel `po-{14..19}-branch` snapshot of 2026-09-17. `make fetch-upstream && make diff` tells you at any time whether `zh_CN/` still matches the current upstream POT entry for entry.
- **Only what should change** — `msgstr` values, `fuzzy` flags, and `#|` previous-message comments. Source references (`#:`), extracted comments (`#.`), `msgctxt`, other flags, entry order and obsolete `#~` entries are preserved byte for byte, so running `msgmerge` against a newer POT should be a no-op for the entries in common.
- **Plurals** — normalised to the Chinese standard `nplurals=1; plural=0;`. The existing headers disagree: `postgres` and `psql` declared 1, nine directories declared 2, and `libpq` and `initdb` carried plural entries with no `Plural-Forms` header at all. Across the whole set, `pg_dump`'s circular foreign-key message is the only entry whose two Chinese forms differed in meaning; collapsing keeps the singular wording, and upstream has been asked to rule on it.
- **Consistency** — one glossary governs the whole set, so similar English strings read consistently across every catalog and every branch, which is what makes six branches reviewable as one body of work rather than six.

## Submitting upstream

Submitted the way the [NLS wiki](https://wiki.postgresql.org/wiki/NLS) asks for it: one Redmine issue per branch (numbers in the table above), with attachments named `<catalog>-zh_CN.po`. They supersede [#8117](https://redmine.postgresql.org/issues/8117), an earlier issue covering the 19 branch alone.

- **Where files go** — the [Redmine patch tracker](https://redmine.postgresql.org/projects/pgtranslation); issues are readable without an account, filing and commenting need a PostgreSQL community account.
- **Where discussion happens** — `pgsql-translators@lists.postgresql.org` ([thread](https://www.postgresql.org/message-id/CA1188D8-97A4-4F09-9E7F-42207C43BC34%40vonng.com)).
- **Status board** — [babel.postgresql.org](https://babel.postgresql.org/) is read-only and accepts no files; its percentages only move once a committer merges into `messages.git`.

## License

The translations follow PostgreSQL itself and are available under the [PostgreSQL License](LICENSE), the same terms as the software they ship with.

---

<div align="center">

Ruohang Feng &lt;rh@vonng.com&gt; · 2026-09

</div>
