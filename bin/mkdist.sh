#!/bin/bash
# Build reproducible Chinese catalog archives without replacing existing assets.
# Each language gets six branch archives and a complete archive; a bilingual
# archive and SHA256SUMS complete the release. GNU tar is required.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="${STAMP:-$(date +%Y%m%d)}"
DIST="${DIST:-$ROOT/dist/$STAMP}"
LANGUAGES="zh_CN zh_TW"
BRANCHES="master REL_18_STABLE REL_17_STABLE REL_16_STABLE REL_15_STABLE REL_14_STABLE"
export LC_ALL=C COPYFILE_DISABLE=1
cd "$ROOT"

if [[ ! "$STAMP" =~ ^[a-zA-Z0-9_.-]+$ ]]; then
    echo "STAMP must contain only letters, digits, dots, underscores or hyphens" >&2
    exit 1
fi
if [ -z "${SOURCE_DATE_EPOCH:-}" ]; then
    if [ ! -e "$ROOT/.git" ]; then
        echo "Set SOURCE_DATE_EPOCH when building from an exported source tree" >&2
        exit 1
    fi
    SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)"
fi
if [[ ! "$SOURCE_DATE_EPOCH" =~ ^[0-9]+$ ]]; then
    echo "SOURCE_DATE_EPOCH must be a Unix timestamp in seconds" >&2
    exit 1
fi

TAR="$(command -v gtar || true)"
if [ -z "$TAR" ]; then
    if tar --version 2>/dev/null | head -1 | grep -q 'GNU tar'; then
        TAR="$(command -v tar)"
    else
        echo "GNU tar not found. On macOS: brew install gnu-tar" >&2
        exit 1
    fi
fi

# Check all inputs and output names before writing any release assets.
if [ ! -f LICENSE ] || [ -L LICENSE ]; then
    echo "Missing or non-regular LICENSE" >&2
    exit 1
fi
ASSETS=("pg-messages-zh_CN-zh_TW-$STAMP.tar.gz")
ALL_FILES=()
for language in $LANGUAGES; do
    ASSETS+=("pg-messages-$language-$STAMP.tar.gz")
    for branch in $BRANCHES; do
        ASSETS+=("pg-messages-$language-$branch-$STAMP.tar.gz")
        files=("$language/$branch/"*.po)
        for file in "${files[@]}"; do
            if [ ! -f "$file" ] || [ -L "$file" ]; then
                echo "Missing or non-regular catalog: $file" >&2
                exit 1
            fi
        done
        ALL_FILES+=("${files[@]}")
    done
done
for name in "${ASSETS[@]}" SHA256SUMS; do
    if [ -e "$DIST/$name" ] || [ -L "$DIST/$name" ]; then
        echo "Refusing to overwrite $DIST/$name; choose a new DIST or STAMP" >&2
        exit 1
    fi
done
mkdir -p "$DIST"
DIST="$(cd "$DIST" && pwd)"
STAGE="$(mktemp -d "$DIST/.mkdist.XXXXXX")"
trap 'rm -rf "$STAGE"' EXIT

archive() {
    local name="$1"
    shift
    printf '%s\n' LICENSE "$@" | sort > "$STAGE/files"
    "$TAR" --format=gnu --owner=0 --group=0 --numeric-owner \
        --mode=0644 --mtime="@$SOURCE_DATE_EPOCH" --no-recursion \
        -cf - -T "$STAGE/files" | gzip -n > "$STAGE/$name"
    printf '  %-55s %3d catalogs\n' "$name" "$#"
}

archive "pg-messages-zh_CN-zh_TW-$STAMP.tar.gz" "${ALL_FILES[@]}"
for language in $LANGUAGES; do
    LANGUAGE_FILES=()
    for branch in $BRANCHES; do
        files=("$language/$branch/"*.po)
        LANGUAGE_FILES+=("${files[@]}")
        archive "pg-messages-$language-$branch-$STAMP.tar.gz" "${files[@]}"
    done
    archive "pg-messages-$language-$STAMP.tar.gz" "${LANGUAGE_FILES[@]}"
done

cd "$STAGE"
shasum -a 256 ./*.tar.gz > SHA256SUMS
# Hard links fail if a destination appeared after the preflight check.
for name in "${ASSETS[@]}" SHA256SUMS; do
    ln "$STAGE/$name" "$DIST/$name"
done
echo
echo "Release assets: $DIST"
