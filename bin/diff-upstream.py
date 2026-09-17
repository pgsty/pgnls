#!/usr/bin/env python3
"""Compare zh_CN/ against a babel snapshot: msgid drift, and before/after coverage.

    bin/diff-upstream.py tmp/upstream-20260917
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'bin'))
import poio

BRANCHES = [('master', 19, 'po-19-branch'), ('REL_18_STABLE', 18, 'po-18-branch'),
            ('REL_17_STABLE', 17, 'po-17-branch'), ('REL_16_STABLE', 16, 'po-16-branch'),
            ('REL_15_STABLE', 15, 'po-15-branch'), ('REL_14_STABLE', 14, 'po-14-branch')]


def key(entry):
    return (entry.msgctxt, entry.msgid, entry.msgid_plural)


def survey(po):
    translated = fuzzy = empty = 0
    for entry in po.active:
        values = list(entry.translations.values())
        if not values or not all(values):
            empty += 1
        elif 'fuzzy' in entry.flags:
            fuzzy += 1
        else:
            translated += 1
    return translated, fuzzy, empty


def main(snapshot):
    snapshot = Path(snapshot)
    if not snapshot.is_dir():
        sys.exit('no such snapshot: %s  (run bin/fetch-upstream.sh first)' % snapshot)
    drift = []
    print('%-16s %8s %8s %8s %9s %9s' % ('branch', 'msgs', 'new', 'gone', 'their %', 'ours %'))
    print('-' * 62)
    grand = [0, 0, 0, 0]
    for branch, major, slug in BRANCHES:
        ours_total = theirs_translated = added = removed = 0
        for path in sorted((ROOT / 'zh_CN' / branch).glob('*.po')):
            ours = poio.read_po(path)
            theirs_path = snapshot / slug / (path.stem + '-zh_CN.po')
            if not theirs_path.exists():
                drift.append('%s/%s: absent from the snapshot' % (branch, path.stem))
                continue
            theirs = poio.read_po(theirs_path)
            a = {key(e) for e in ours.active}
            b = {key(e) for e in theirs.active}
            if a != b:
                added += len(b - a)
                removed += len(a - b)
                drift.append('%s/%s: upstream has %d we lack, we have %d upstream dropped'
                             % (branch, path.stem, len(b - a), len(a - b)))
            ours_total += len(a)
            theirs_translated += survey(theirs)[0]
        pct = 100.0 * theirs_translated / ours_total if ours_total else 0.0
        print('%-16s %8s %8d %8d %8.1f%% %8.1f%%'
              % (branch, '{:,}'.format(ours_total), added, removed, pct, 100.0))
        grand[0] += ours_total; grand[1] += theirs_translated
        grand[2] += added; grand[3] += removed
    print('-' * 62)
    print('%-16s %8s %8d %8d %8.1f%% %8.1f%%'
          % ('TOTAL', '{:,}'.format(grand[0]), grand[2], grand[3],
             100.0 * grand[1] / grand[0] if grand[0] else 0.0, 100.0))
    print()
    if drift:
        print('msgid drift — upstream moved since these files were built:')
        for line in drift[:30]:
            print('  ' + line)
        if len(drift) > 30:
            print('  ... and %d more' % (len(drift) - 30))
        return 1
    print('No msgid drift: zh_CN/ matches this snapshot entry for entry.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'tmp'))
