<div align="center">

# PostgreSQL Simplified Chinese Message Catalogs

**Complete `zh_CN` translations for PostgreSQL 14 – 19**

[![Review Workbench](https://img.shields.io/badge/Review_Workbench-pgsql.cc%2Fnls-2f6fa3?style=for-the-badge&logo=postgresql&logoColor=white)](https://pgsql.cc/nls)

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14--19-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Messages](https://img.shields.io/badge/messages-67%2C487-informational)](https://pgsql.cc/nls)
[![Translated](https://img.shields.io/badge/translated-100%25-brightgreen)](https://pgsql.cc/nls)
[![Fuzzy](https://img.shields.io/badge/fuzzy-0-brightgreen)](https://pgsql.cc/nls)
[![msgfmt](https://img.shields.io/badge/msgfmt-clean-brightgreen)](https://www.gnu.org/software/gettext/)
[![License](https://img.shields.io/badge/license-PostgreSQL-blue)](LICENSE)

</div>

**162 files, 67,487 messages, 100% translated, zero fuzzy, zero untranslated** — every file clean under `msgfmt --check --check-format`.

The `zh_CN` catalogs currently in `pgtranslation/messages.git` date from 2019; their headers still read `Project-Id-Version: postgres (PostgreSQL) 12`. Across PostgreSQL 14 – 19 they carry a reviewed translation for 77.1% of messages; of the remaining 15,475, some 11,770 are fuzzy entries that babel matched by similarity and 3,705 are empty. This repository is a complete set rebuilt from the current templates: every message checked by hand against the English original, with terminology held to a single glossary shared across all catalogs and all six branches.

## Review Workbench

Every message is browsable at **<https://pgsql.cc/nls>** — the English original, the existing translation and the calibrated translation side by side, filterable by catalog, full-text searchable, with the real provenance of similar wordings. Corrections and second opinions are welcome there.

<div align="center">

| Upstream branch | PG | Catalogs | Messages | Upstream | Here | Workbench | Issue |
|:---|:---:|---:|---:|---:|:---:|:---:|:---:|
| [`master`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/master) | 19 | 28 | 12,636 | 65.3% | **100%** | [browse](https://pgsql.cc/nls/?v=19) | [#8123](https://redmine.postgresql.org/issues/8123) |
| [`REL_18_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_18_STABLE) | 18 | 28 | 12,098 | 69.9% | **100%** | [browse](https://pgsql.cc/nls/?v=18) | [#8118](https://redmine.postgresql.org/issues/8118) |
| [`REL_17_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_17_STABLE) | 17 | 28 | 11,509 | 74.9% | **100%** | [browse](https://pgsql.cc/nls/?v=17) | [#8119](https://redmine.postgresql.org/issues/8119) |
| [`REL_16_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_16_STABLE) | 16 | 26 | 10,656 | 79.0% | **100%** | [browse](https://pgsql.cc/nls/?v=16) | [#8120](https://redmine.postgresql.org/issues/8120) |
| [`REL_15_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_15_STABLE) | 15 | 26 | 10,463 | 85.7% | **100%** | [browse](https://pgsql.cc/nls/?v=15) | [#8121](https://redmine.postgresql.org/issues/8121) |
| [`REL_14_STABLE`](https://git.postgresql.org/gitweb/?p=pgtranslation/messages.git;a=tree;f=zh_CN;hb=refs/heads/REL_14_STABLE) | 14 | 26 | 10,125 | 91.8% | **100%** | [browse](https://pgsql.cc/nls/?v=14) | [#8122](https://redmine.postgresql.org/issues/8122) |

</div>

The branch names link to the same catalogs as they stand today in the upstream translation repository, `pgtranslation/messages.git`:

```bash
git clone https://git.postgresql.org/git/pgtranslation/messages.git
```

PostgreSQL 19 lives on `master` there; there is no `REL_19_STABLE`. From PG17 on there are two extra catalogs, `pg_combinebackup` and `pg_walsummary` — of which `pg_combinebackup` is a new file for `zh_CN`.

## Layout

```
zh_CN/<branch>/<catalog>.po       162 catalogs, one directory per upstream branch
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

## Method

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
