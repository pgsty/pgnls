#!/bin/bash
# Build the release archives into dist/: one tarball per upstream branch plus one
# holding all six, and a SHA256SUMS covering them. Every archive unpacks to
# zh_CN/<branch>/<catalog>.po, the layout messages.git expects.
#
# GNU tar is required. BSD tar on macOS stores AppleDouble (._*) companions for
# extended attributes, which would ship resource-fork junk to everyone else.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$ROOT/dist"
STAMP="${STAMP:-$(date +%Y%m%d)}"
PREFIX="pg-messages-zh_CN"
BRANCHES="master REL_18_STABLE REL_17_STABLE REL_16_STABLE REL_15_STABLE REL_14_STABLE"

TAR="$(command -v gtar || true)"
if [ -z "$TAR" ]; then
    if tar --version 2>/dev/null | head -1 | grep -q 'GNU tar'; then
        TAR="$(command -v tar)"
    else
        echo "GNU tar not found. On macOS: brew install gnu-tar" >&2
        exit 1
    fi
fi

# Belt and braces: tell BSD utilities not to write ._* alongside, and tell GNU
# tar to leave any that already exist on disk out of the archive.
export COPYFILE_DISABLE=1
EXCLUDE=(--exclude='.DS_Store' --exclude='._*' --exclude='.AppleDouble'
         --exclude='__MACOSX' --exclude='*.swp')
# Fixed ownership so the archives do not carry this machine's uid/gid.
OWNER=(--owner=0 --group=0 --numeric-owner)

rm -rf "$DIST"
mkdir -p "$DIST"
cd "$ROOT"

"$TAR" "${EXCLUDE[@]}" "${OWNER[@]}" -czf "$DIST/$PREFIX-$STAMP.tar.gz" zh_CN
printf '  %-46s %2d catalogs\n' "$PREFIX-$STAMP.tar.gz" "$(find zh_CN -name '*.po' | wc -l)"

for branch in $BRANCHES; do
    name="$PREFIX-$branch-$STAMP.tar.gz"
    "$TAR" "${EXCLUDE[@]}" "${OWNER[@]}" -czf "$DIST/$name" "zh_CN/$branch"
    printf '  %-46s %2d catalogs\n' "$name" "$(ls "zh_CN/$branch"/*.po | wc -l)"
done

cd "$DIST"
shasum -a 256 ./*.tar.gz > SHA256SUMS
echo
ls -l
