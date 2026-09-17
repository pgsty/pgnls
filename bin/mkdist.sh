#!/bin/bash
# Build the release assets into dist/: one zip per branch using the flat naming
# the Redmine patch tracker asks for, plus a tarball of the repository layout
# and a checksum file. dist/ is not tracked.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
STAMP="$(date +%Y%m%d)"
rm -rf "$DIST"; mkdir -p "$DIST/.stage"
cd "$ROOT"

for b in master REL_18_STABLE REL_17_STABLE REL_16_STABLE REL_15_STABLE REL_14_STABLE; do
  out="$DIST/.stage/$b"; mkdir -p "$out"
  for f in "zh_CN/$b/"*.po; do
    cp "$f" "$out/$(basename "$f" .po)-zh_CN.po"      # <catalog>-zh_CN.po, as Redmine expects
  done
  (cd "$DIST/.stage" && zip -qr "$DIST/$b-zh_CN-$STAMP.zip" "$b")
  echo "  $b  $(ls "$out" | wc -l | tr -d ' ') catalogs"
done

# Full set in the repository layout, ready to drop over messages.git
tar -czf "$DIST/postgresql-14-19-zh_CN-$STAMP.tar.gz" zh_CN
rm -rf "$DIST/.stage"
(cd "$DIST" && shasum -a 256 ./* > SHA256SUMS)
echo
ls -la "$DIST"
