# Errata

Known defects and documentation drift, listed rather than quietly patched.
Verified counts come from the published catalogs, not from memory.

## Open

None currently recorded.

## Resolved

### `"members"` — earlier erratum withdrawn

An earlier erratum said that `members` in `multixact "members" limit exceeded`
must remain in English because it names the `pg_multixact/members` storage area.
Reviewing the complete calling context on 2026-09-29 does not support that
requirement.

`GetNewMultiXactId` checks whether allocating new member records would cross the
member-space wraparound boundary. The accompanying detail compares the requested
member count with the remaining capacity, and the hint recommends VACUUM with
lower multixact freeze ages. This is a member-space capacity error, not a path
access error. The storage directory has the same name, but that and the quotation
marks do not require treating the word as a literal path in this message.
See the [PG18 source context](https://github.com/postgres/postgres/blob/REL_18_STABLE/src/backend/access/transam/multixact.c).

The existing translations, `多事务 "成员" 超过限制` and
`超過多重交易 "成員" 的限制`, are retained. The message occurs in ten active
entries across PG14–18 and both languages; the earlier count of five included
only Simplified Chinese. PG19 has no active entry for this message.

### `cluster` — glossary drift

An earlier draft glossary (`nls-v2`) recorded `cluster` = 集群. That is wrong for
PostgreSQL: a "database cluster" is the set of databases sharing one data
directory, not a group of machines, and Chinese readers take 集群 to mean the
latter.

Practice settled on the correct distinction and the published catalogs follow it
consistently:

| English | Chinese | Occurrences |
|:---|:---|---:|
| `cluster` (the storage-level database cluster) | 集簇 | 809 |
| `CLUSTER` (the command that rewrites a table in index order) | 聚簇 | 116 |
| — | 集群 | 0 |

The 8 occurrences of 集群 that `grep` finds in the tree are all inside obsolete
`#~` entries, which are upstream's own earlier translations preserved byte for
byte and never shown to a user.

`glossary.tsv` and `style-guide.md` as published carry the correct form; the
superseded `nls-v2` draft is not published.
