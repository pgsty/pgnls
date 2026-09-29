#!/bin/bash
# Lay out both languages under OUT/<language>/<branch>/ with the flat
# <catalog>-<language>.po naming the Redmine patch tracker asks for.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="${STAMP:-$(date +%Y%m%d)}"
OUT="${OUT:-${DIST:-$ROOT/dist/$STAMP}/redmine}"
LANGUAGES="zh_CN zh_TW"
BRANCHES="master REL_18_STABLE REL_17_STABLE REL_16_STABLE REL_15_STABLE REL_14_STABLE"
export LC_ALL=C COPYFILE_DISABLE=1
cd "$ROOT"

# Refuse the whole operation before copying if any expected output exists.
for language in $LANGUAGES; do
    for branch in $BRANCHES; do
        for file in "$language/$branch/"*.po; do
            if [ ! -f "$file" ] || [ -L "$file" ]; then
                echo "Missing or non-regular catalog: $file" >&2
                exit 1
            fi
            name="$(basename "$file" .po)-$language.po"
            if [ -e "$OUT/$language/$branch/$name" ] || [ -L "$OUT/$language/$branch/$name" ]; then
                echo "Refusing to overwrite $OUT/$language/$branch/$name; choose a new OUT" >&2
                exit 1
            fi
        done
    done
done
set -o noclobber
for language in $LANGUAGES; do
    for branch in $BRANCHES; do
        mkdir -p "$OUT/$language/$branch"
        files=("$language/$branch/"*.po)
        for file in "${files[@]}"; do
            cat "$file" > "$OUT/$language/$branch/$(basename "$file" .po)-$language.po"
        done
        printf '  %-5s %-16s %2d files\n' "$language" "$branch" "${#files[@]}"
    done
done

echo
echo "Attach the files from $OUT/<language>/<branch>/ to the corresponding issue"
