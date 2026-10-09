<div align="center">

# PostgreSQL Chinese Message Catalogs

**Complete `zh_CN` and `zh_TW` translations for PostgreSQL 14 – 19**

[![Review Workbench](https://img.shields.io/badge/Review_Workbench-pgsql.cc%2Fnls-2f6fa3?style=for-the-badge&logo=postgresql&logoColor=white)](https://pgsql.cc/nls)

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14--19-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Messages](https://img.shields.io/badge/messages-67%2C512-informational)](https://pgsql.cc/nls)
[![Translated](https://img.shields.io/badge/translated-100%25-brightgreen)](https://pgsql.cc/nls)
[![Fuzzy](https://img.shields.io/badge/fuzzy-0-brightgreen)](https://pgsql.cc/nls)
[![msgfmt](https://img.shields.io/badge/msgfmt-clean-brightgreen)](https://www.gnu.org/software/gettext/)
[![License](https://img.shields.io/badge/license-PostgreSQL-blue)](LICENSE)

</div>

**162 files and 67,512 messages per language; 324 files and 135,024 messages in total.** Both languages are 100% translated, with zero fuzzy and zero untranslated entries — every file clean under `msgfmt --check --check-format`.

The initial `zh_CN` baseline from `pgtranslation/messages.git` dated from 2019; its headers still read `Project-Id-Version: postgres (PostgreSQL) 12`. Across PostgreSQL 14 – 19 it carried a reviewed translation for 77.1% of messages; of the remaining 15,475, some 11,770 were fuzzy entries that babel matched by similarity and 3,705 were empty. This repository is a complete set rebuilt from the current templates, with terminology held to a single glossary shared across all catalogs and all six branches, and every message verified against its English original. How that was done is spelled out in [How this was made](#how-this-was-made).

## Review Workbench

The bilingual review corpus is browsable at **<https://pgsql.cc/nls>** — the English original, the existing translation and the calibrated translation side by side, filterable by catalog, full-text searchable, with the provenance of similar wordings. Corrections and second opinions are welcome there. Release archives and workbench imports are updated separately; use the downloads below for this edition’s complete catalogs.

<div align="center">

| Upstream branch | PG | Catalogs | Messages | Initial upstream | Here | Workbench | Issue | Downloads |
|:---|:---:|---:|---:|---:|:---:|:---:|:---:|:---:|
| [`master`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/master) | 19 | 28 | 12,651 | 65.3% | **100%** | [browse](https://pgsql.cc/nls/?v=19) | [#8123](https://redmine.postgresql.org/issues/8123) | [zh_CN](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-master-20261008.tar.gz) / [zh_TW](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_TW-master-20261008.tar.gz) |
| [`REL_18_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_18_STABLE) | 18 | 28 | 12,101 | 69.9% | **100%** | [browse](https://pgsql.cc/nls/?v=18) | [#8118](https://redmine.postgresql.org/issues/8118) | [zh_CN](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-REL_18_STABLE-20261008.tar.gz) / [zh_TW](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_TW-REL_18_STABLE-20261008.tar.gz) |
| [`REL_17_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_17_STABLE) | 17 | 28 | 11,512 | 74.9% | **100%** | [browse](https://pgsql.cc/nls/?v=17) | [#8119](https://redmine.postgresql.org/issues/8119) | [zh_CN](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-REL_17_STABLE-20261008.tar.gz) / [zh_TW](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_TW-REL_17_STABLE-20261008.tar.gz) |
| [`REL_16_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_16_STABLE) | 16 | 26 | 10,658 | 79.0% | **100%** | [browse](https://pgsql.cc/nls/?v=16) | [#8120](https://redmine.postgresql.org/issues/8120) | [zh_CN](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-REL_16_STABLE-20261008.tar.gz) / [zh_TW](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_TW-REL_16_STABLE-20261008.tar.gz) |
| [`REL_15_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_15_STABLE) | 15 | 26 | 10,464 | 85.7% | **100%** | [browse](https://pgsql.cc/nls/?v=15) | [#8121](https://redmine.postgresql.org/issues/8121) | [zh_CN](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-REL_15_STABLE-20261008.tar.gz) / [zh_TW](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_TW-REL_15_STABLE-20261008.tar.gz) |
| [`REL_14_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_14_STABLE) | 14 | 26 | 10,126 | 91.8% | **100%** | [browse](https://pgsql.cc/nls/?v=14) | [#8122](https://redmine.postgresql.org/issues/8122) | [zh_CN](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-REL_14_STABLE-20261008.tar.gz) / [zh_TW](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_TW-REL_14_STABLE-20261008.tar.gz) |

</div>

Catalog and message counts are per language and describe the current local
catalogs; download links refer to the 20261008 bilingual release below.
The upstream percentages describe the initial `zh_CN` baseline.

The 2026-10-09 update adds eight reviewed PG19 message instances across four
English strings and removes four superseded SSL entries. Compression-stream
wording and the SSL detail inherit existing translations; the SNI warnings now
state on/off explicitly. PG14–18 message sets are unchanged. All 324 catalogs
carry the refreshed template metadata and revision date. The release archives
below retain their published 20261008 contents.

The branch names link to the same catalogs as they stand today in the upstream translation repository, `pgtranslation/messages.git`:

```bash
git clone https://git.postgresql.org/git/pgtranslation/messages.git
```

PostgreSQL 19 lives on `master` there; there is no `REL_19_STABLE`. From PG17 on there are two extra catalogs, `pg_combinebackup` and `pg_walsummary` — of which `pg_combinebackup` is a new file for `zh_CN`.

## Download

Release [`20261008`](https://github.com/pgsty/pgnls/releases/tag/20261008) provides
complete Simplified and Traditional Chinese catalogs for PostgreSQL 14–19:
**324 PO files and 135,020 translated messages**. Each language has 162 files
and 67,510 messages, with zero fuzzy or untranslated entries.

This edition translates twenty new language/version instances across five
English messages, removes the two superseded logical-decoding entries, and
synchronizes the current Babel template dates and source references. All PO
revision dates and the final calibration record are updated to October 8, 2026.

| Archive | Covers | Catalogs | Messages |
|:---|:---|---:|---:|
| [`pg-messages-zh_CN-zh_TW-20261008.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-zh_TW-20261008.tar.gz) | Both languages, all six branches | 324 | 135,020 |
| [`pg-messages-zh_CN-20261008.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-20261008.tar.gz) | Simplified Chinese, all six branches | 162 | 67,510 |
| [`pg-messages-zh_TW-20261008.tar.gz`](https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_TW-20261008.tar.gz) | Traditional Chinese, all six branches | 162 | 67,510 |

The version table above links to the twelve individual language/branch archives.
Every archive contains only complete PO files under
`<language>/<branch>/<catalog>.po`. To use one language and branch:

```bash
curl -LO https://github.com/pgsty/pgnls/releases/download/20261008/pg-messages-zh_CN-REL_18_STABLE-20261008.tar.gz
tar -xzf pg-messages-zh_CN-REL_18_STABLE-20261008.tar.gz
cp zh_CN/REL_18_STABLE/*.po /path/to/messages/zh_CN/
```

Checksums for all fifteen archives are in
[`SHA256SUMS`](https://github.com/pgsty/pgnls/releases/download/20261008/SHA256SUMS).
Earlier editions remain available in the [release history](https://github.com/pgsty/pgnls/releases).

## Layout

```
zh_CN/<branch>/<catalog>.po       162 catalogs, one directory per upstream branch
zh_TW/<branch>/<catalog>.po       162 curated Traditional Chinese catalogs
ref/                              style guide, phrasebook, glossaries, process, errata
bin/                              standalone tools; Python 3, GNU gettext, GNU tar, gzip
Makefile                          the usual operations
LICENSE                           the PostgreSQL License, verbatim from postgres.git
```

## Branches

Each view of the catalogs lives on its own branch:

| Branch | Holds | Sync |
|:---|:---|:---|
| `main` | curated catalogs with reviewed upstream updates | manual |
| `message` | the raw state of [`pgtranslation/messages.git`](https://git.postgresql.org/git/pgtranslation/messages.git), verbatim | `bin/sync-message.sh` on that branch |
| `babel` | the aligned view `babel.postgresql.org` serves — the raw catalogs merged against each branch's current POT — as dated snapshots | `bin/sync-babel.sh` on that branch |

The two views differ by design: translations on shared msgids are
byte-identical, but the aligned view carries the day's msgid sets (new strings
empty, reworded ones fuzzy-matched, dropped ones as `#~`) while the raw one
keeps each translator's last word. `main` also carries the curated `zh_TW/`
catalogs: 67,512 messages across the same six branches, all translated.

## Usage

```
make check            validate all 324 zh_CN/zh_TW catalogs (msgfmt, completeness, headers, alignment)
make stats            message counts per catalog per branch
make mo               compile both languages to .mo under build/<branch>/<language>/LC_MESSAGES/
make dist             15 release tarballs covering both languages, plus SHA256SUMS, under dist/<date>/
make redmine          flat catalog files under dist/<date>/redmine/<language>/<branch>/
make fetch-upstream   pull a fresh zh_CN snapshot from babel into tmp/
make diff             compare zh_CN/ against that snapshot: msgid drift and coverage
make check-align      column alignment by East Asian display width, on its own
make show BRANCH=master CATALOG=psql
make clean            remove compiled build/ while preserving release assets in dist/
```

`make dist` requires GNU tar (`gtar` on macOS), gzip and `shasum`. It creates
one bilingual archive, one complete archive per language, and six branch
archives per language, plus `SHA256SUMS`. Each archive contains only PO files
preserving `<language>/<branch>/<catalog>.po`. The repository's `LICENSE` and
compiled MO files are not included. `make mo` compiles all 324 catalogs separately
for local use.

Set `STAMP` to choose the release label and `DIST` to choose the output directory:

```bash
STAMP=20261008 make dist
# Or build another copy in a fresh directory:
STAMP=20261008 DIST=/tmp/pgnls-20261008 make dist
```

The default output directory is `dist/<STAMP>/`. Existing release files are
never overwritten; choose a fresh directory to rebuild. Archive member order,
ownership, permissions and timestamps are normalized, and gzip timestamps are
omitted. `SOURCE_DATE_EPOCH` defaults to the current Git commit timestamp; when
building an exported source tree without `.git`, pass that timestamp explicitly.
The same PO files, stamp, epoch and archive tools produce identical archives.

For a PGWeb installation with the language migration applied, generate a
language-scoped review bundle from the curated catalogs and the matching Babel
snapshot:

```bash
python3 bin/pgweb-bundle.py --language zh_TW \
  --upstream tmp/babel-snapshot/download/zh_TW --output /tmp/nls-zh_TW.jsonl.gz
# In the pgweb checkout:
.venv/bin/python manage.py nls_import /tmp/nls-zh_TW.jsonl.gz --check
.venv/bin/python manage.py nls_import /tmp/nls-zh_TW.jsonl.gz
```

The default is PG14–19; repeat `--major` to select versions. English message sets
must match the snapshot. Candidates start pending, with the Babel translation
kept alongside the curated PO text; review decisions remain independent per
language. Re-importing preserves existing human review state. Historical
`zh_CN` IDs must be retained when refreshing an existing database; the importer
rejects new IDs for a source message that already exists. Bundle tests run with
`python3 -m unittest discover -s tests`.

To land these in `messages.git`, check out the matching branch and overwrite `zh_CN/`:

```bash
cp zh_CN/REL_18_STABLE/*.po /path/to/messages/zh_CN/
```

`make redmine` prepares separate language and branch directories containing
`<catalog>-zh_CN.po` or `<catalog>-zh_TW.po`, using the same bytes as the source
catalogs. Its default output is `dist/<STAMP>/redmine/`; set `OUT` to use another
directory. These flat submission files are separate from the release tarballs.

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

- **Templates** — all 324 babel `po-{14..19}-branch` catalogs were rechecked on 2026-10-09 against the builds from 2026-10-08 UTC. Both languages carry the snapshot's per-file `POT-Creation-Date` and active-message source references (`#:`). `make fetch-upstream && make diff` tells you at any time whether `zh_CN/` still matches the current upstream POT entry for entry.
- **Only what should change** — translation edits affect `msgstr` values, `fuzzy` flags, and `#|` previous-message comments. Explicit template refreshes synchronize `POT-Creation-Date` and source references (`#:`) while preserving translations and `PO-Revision-Date`. Extracted comments (`#.`), `msgctxt`, other flags, and the order of unchanged entries are preserved byte for byte.
- **Removed messages** — when a template refresh removes an active message, delete the entire old entry from `main`, including any `#~` copy created during the refresh. Compare the corresponding language, PostgreSQL branch, and catalog; a message still used elsewhere remains there. Git records superseded translations. The raw `babel` and `message` branches mirror their respective upstream sources verbatim, including any obsolete entries those sources contain.
- **Plurals** — normalised to the Chinese standard `nplurals=1; plural=0;`. The existing headers disagree: `postgres` and `psql` declared 1, nine directories declared 2, and `libpq` and `initdb` carried plural entries with no `Plural-Forms` header at all. `pg_dump`'s circular foreign-key warning uses the number-neutral wording `以下表涉及循环外键约束:` so the single Chinese plural form covers both self-references within one table and cycles among multiple tables.
- **Consistency** — one glossary governs the whole set, so similar English strings read consistently across every catalog and every branch, which is what makes six branches reviewable as one body of work rather than six.

### Catalog headers

The current `zh_CN` and `zh_TW` catalogs for PostgreSQL 14–19 are a complete
replacement translation produced in 2026. All 324 files use this comment template,
with the language variant and component adjusted to match the file:

```po
# Simplified Chinese message translation file for pg_combinebackup
# Copyright (C) 2026 PostgreSQL Global Development Group
# This file is distributed under the same license as the PostgreSQL package.
#
# Ruohang Feng (vonng@pigsty) <rh@vonng.com>, 2026.
#
```

Historical translator credits precede the current credit. Preserve their names,
email addresses, contribution dates and relative order, using
`# Name <email>, YYYY.` or `# Name <email>, YYYY-MM-DD.`. These credits acknowledge
earlier contributions; their dates do not imply participation in the 2026
retranslation. Restore missing credits only from evidence for the same catalog,
such as its historical `Last-Translator` field. A `Language-Team` field alone is
not an author list.

The copyright year identifies this complete retranslation; keep it at 2026 for
this edition rather than copying a template's old year or advancing it merely
because the calendar changes. Keep `Last-Translator` as
`Ruohang Feng <rh@vonng.com>`; the Pigsty identifier belongs in the author comment.
Set `PO-Revision-Date` to the actual revision time with its timezone. A full
release calibration records that time across all validated catalogs; retain the
upstream `POT-Creation-Date` for each file. Preserve the other machine header
fields when changing comments. `make check` validates
the comment template as well as the machine fields.

The old public-domain comments in Simplified Chinese `initdb`, `pg_config`,
`pg_ctl` and `pgscripts` came from the early `--foreign-user` template. PostgreSQL
[changed the generator to use PGDG in 2009](https://github.com/postgres/postgres/commit/ccd31eb861e727671e4a771d4bcc37f1179caec9),
and the Spanish catalogs have a
[2010 normalization precedent](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=commitdiff;h=a337a4c05ea12e10b05c9e1c51d206ac8937f4c1).
The unified header describes the current retranslation; it does not change the
status of earlier public-domain material. Bao Wei's restored credits in those
four catalogs come from their `Last-Translator` and revision dates in the
[2005 initial import](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=commit;h=a7305233d211c5fdc9c48a66ca49d614430bde46).

## Submitting upstream

Submitted the way the [NLS wiki](https://wiki.postgresql.org/wiki/NLS) asks for it: one Redmine issue per branch (numbers in the table above), with attachments named `<catalog>-zh_CN.po`. They supersede [#8117](https://redmine.postgresql.org/issues/8117), an earlier issue covering the 19 branch alone.

- **Where files go** — the [Redmine patch tracker](https://redmine.postgresql.org/projects/pgtranslation); issues are readable without an account, filing and commenting need a PostgreSQL community account.
- **Where discussion happens** — `pgsql-translators@lists.postgresql.org` ([thread](https://www.postgresql.org/message-id/CA1188D8-97A4-4F09-9E7F-42207C43BC34%40vonng.com)).
- **Status board** — [babel.postgresql.org](https://babel.postgresql.org/) is read-only and accepts no files; its percentages only move once a committer merges into `messages.git`.

## License

The translations follow PostgreSQL itself and are available under the [PostgreSQL License](LICENSE), the same terms as the software they ship with.

---

<div align="center">

Ruohang Feng &lt;rh@vonng.com&gt; · 2026-10

Catalogs last updated: 2026-10-09 12:11+0800 · zh_CN / zh_TW · PostgreSQL 14–19

Latest translation calibration and catalog validation: 2026-10-09 12:11+0800

</div>
