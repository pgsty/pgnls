#!/bin/bash
# Lay out the catalogs under dist/redmine/<branch>/ using the flat
# <catalog>-zh_CN.po naming the Redmine patch tracker asks for, one directory
# per issue. Same bytes as zh_CN/, different filenames.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/redmine"
rm -rf "$OUT"
cd "$ROOT"
for branch in master REL_18_STABLE REL_17_STABLE REL_16_STABLE REL_15_STABLE REL_14_STABLE; do
    mkdir -p "$OUT/$branch"
    for f in "zh_CN/$branch"/*.po; do
        cp "$f" "$OUT/$branch/$(basename "$f" .po)-zh_CN.po"
    done
    printf '  %-16s %2d files\n' "$branch" "$(ls "$OUT/$branch" | wc -l)"
done
echo
echo "  attach the contents of dist/redmine/<branch>/ to that branch's issue"
