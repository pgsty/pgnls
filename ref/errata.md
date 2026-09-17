# Errata

Known defects and documentation drift, listed rather than quietly patched.
Verified counts come from the published catalogs, not from memory.

## Open

### `"members"` should not be translated

`multixact "members" limit exceeded` and its companions render `"members"` as
成员. It is the name of the `pg_multixact/members` storage area — the quotes in
the English are marking a name, not emphasising a noun — so it should stay as
`"members"`, the way other on-disk names are left alone.

Affected: 5 files. Not yet fixed; queued for the next revision, and disclosed on
the Redmine issues rather than left for a reviewer to find.

## Resolved

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
