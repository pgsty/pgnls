#!/bin/bash
# Refresh zh_CN/ and zh_TW/ on the babel branch from babel.postgresql.org.
#
# babel serves the pgtranslation/messages.git catalogs merged against each
# branch's current POT, so this is the aligned view: today's msgid sets, new
# strings empty, reworded strings fuzzy-matched, dropped strings kept as #~
# comments. Each sync is one dated snapshot commit; the message branch holds
# the raw repository state instead.
#
# Run it on the babel branch only; it refuses everywhere else so it can never
# clobber the curated zh_CN/ on main. When comparing two snapshots, filter the
# POT-Creation-Date lines first: babel regenerates daily and every file would
# otherwise show as changed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRANCHES="19:master 18:REL_18_STABLE 17:REL_17_STABLE 16:REL_16_STABLE 15:REL_15_STABLE 14:REL_14_STABLE"
CAT26="ecpg ecpglib initdb libpq pg_amcheck pg_archivecleanup pg_basebackup pg_checksums pg_config pg_controldata pg_ctl pg_dump pg_resetwal pg_rewind pg_test_fsync pg_test_timing pg_upgrade pg_verifybackup pg_waldump pgscripts plperl plpgsql plpython pltcl postgres psql"
CAT28="$CAT26 pg_combinebackup pg_walsummary"

[ "$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)" = "babel" ] || {
  echo "refusing: switch to the babel branch first; this overwrites zh_CN/ and zh_TW/" >&2
  exit 1
}

stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
for lang in zh_CN zh_TW; do
  for vb in $BRANCHES; do
    v="${vb%%:*}"; b="${vb##*:}"
    if [ "$v" -ge 17 ]; then CATS="$CAT28"; else CATS="$CAT26"; fi
    dir="$stage/$lang/$b"
    mkdir -p "$dir"
    miss=0
    for c in $CATS; do
      f="$dir/$c.po"
      code=$(curl -sS -w '%{http_code}' -o "$f" "https://babel.postgresql.org/po-$v-branch/$c-$lang.po" || echo 000)
      if [ "$code" != "200" ]; then
        rm -f "$f"
        miss=$((miss + 1))
      fi
    done
    mkdir -p "$ROOT/$lang/$b"
    rsync -a --delete "$dir/" "$ROOT/$lang/$b/"
    echo "  $lang/$b: $(ls "$ROOT/$lang/$b" | wc -l | tr -d ' ') files${miss:+, $miss not served}"
  done
done

echo
echo 'staged. validate with:  for f in zh_CN/*/*.po zh_TW/*/*.po; do msgfmt -o /dev/null "$f" || echo "FAIL $f"; done'
echo 'then review with git status, commit as one dated snapshot, and push.'
