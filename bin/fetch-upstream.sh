#!/bin/bash
# Fetch a fresh zh_CN snapshot from babel into tmp/upstream-<date>/ for comparison.
# Nothing is written inside zh_CN/; the snapshot is gitignored working material.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/tmp/upstream-$(date +%Y%m%d)"
CAT26="ecpg ecpglib initdb libpq pg_amcheck pg_archivecleanup pg_basebackup pg_checksums pg_config pg_controldata pg_ctl pg_dump pg_resetwal pg_rewind pg_test_fsync pg_test_timing pg_upgrade pg_verifybackup pg_waldump pgscripts plperl plpgsql plpython pltcl postgres psql"
CAT28="$CAT26 pg_combinebackup pg_walsummary"
mkdir -p "$OUT"
for v in 14 15 16 17 18 19; do
  mkdir -p "$OUT/po-$v-branch"
  if [ "$v" -ge 17 ]; then CATS="$CAT28"; else CATS="$CAT26"; fi
  for c in $CATS; do
    f="$OUT/po-$v-branch/$c-zh_CN.po"
    [ -s "$f" ] && continue
    code=$(curl -sS -w '%{http_code}' -o "$f" "https://babel.postgresql.org/po-$v-branch/$c-zh_CN.po" || echo 000)
    [ "$code" = "200" ] || { echo "MISS v$v $c http=$code"; rm -f "$f"; }
  done
  echo "  po-$v-branch: $(ls "$OUT/po-$v-branch" | wc -l | tr -d ' ') files"
done
echo
echo "snapshot: $OUT"
echo "compare:  bin/diff-upstream.py $OUT"
