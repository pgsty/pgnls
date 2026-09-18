#!/bin/bash
# Refresh zh_CN/ and zh_TW/ on the upstream branch from pgtranslation/messages.git.
#
# The upstream branch is a plain mirror of what the real repository holds:
# no babel POT merge, no local edits. Run it on the upstream branch only;
# it refuses everywhere else so it can never clobber the curated zh_CN/ on main.
#
# The clone is kept in tmp/messages so repeat runs are incremental fetches.
# If git.postgresql.org is slow from your network, export https_proxy first,
# e.g.  https_proxy=http://127.0.0.1:8118 bin/sync-upstream.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO=https://git.postgresql.org/git/pgtranslation/messages.git
CLONE="$ROOT/tmp/messages"
BRANCHES="master REL_18_STABLE REL_17_STABLE REL_16_STABLE REL_15_STABLE REL_14_STABLE"

[ "$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)" = "upstream" ] || {
  echo "refusing: switch to the upstream branch first; this overwrites zh_CN/ and zh_TW/" >&2
  exit 1
}

if [ -d "$CLONE/.git" ]; then
  git -C "$CLONE" fetch origin --prune
else
  mkdir -p "$ROOT/tmp"
  git clone "$REPO" "$CLONE"
fi

stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
for b in $BRANCHES; do
  mkdir -p "$stage/$b"
  (cd "$CLONE" && git archive "origin/$b" zh_CN zh_TW) | tar -x -C "$stage/$b"
  rsync -a --delete "$stage/$b/zh_CN/" "$ROOT/zh_CN/$b/"
  mkdir -p "$ROOT/zh_TW/$b"
  rsync -a --delete "$stage/$b/zh_TW/" "$ROOT/zh_TW/$b/"
  echo "  $b: zh_CN=$(ls "$ROOT/zh_CN/$b" | wc -l | tr -d ' ')  zh_TW=$(ls "$ROOT/zh_TW/$b" | wc -l | tr -d ' ')"
done

echo
echo 'staged. validate with:  for f in zh_TW/*/*.po zh_CN/*/*.po; do msgfmt -o /dev/null "$f" || echo "FAIL $f"; done'
echo 'then review with git status/diff, commit, and push.'
