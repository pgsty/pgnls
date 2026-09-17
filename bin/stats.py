#!/usr/bin/env python3
"""Per-catalog message counts across zh_CN/. No database, no network."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'bin'))
import poio

BRANCHES = [('master', 19), ('REL_18_STABLE', 18), ('REL_17_STABLE', 17),
            ('REL_16_STABLE', 16), ('REL_15_STABLE', 15), ('REL_14_STABLE', 14)]

catalogs, totals = {}, {}
for branch, major in BRANCHES:
    for path in sorted((ROOT / 'zh_CN' / branch).glob('*.po')):
        po = poio.read_po(path)
        catalogs.setdefault(path.stem, {})[branch] = len(po.active)
        totals[branch] = totals.get(branch, 0) + len(po.active)

width = max(len(c) for c in catalogs)
head = '%-*s' % (width, 'catalog') + ''.join('%9s' % b.replace('_STABLE', '').replace('REL_', '')
                                             for b, _ in BRANCHES)
print(head)
print('-' * len(head))
for catalog in sorted(catalogs):
    row = '%-*s' % (width, catalog)
    for branch, _ in BRANCHES:
        n = catalogs[catalog].get(branch)
        row += '%9s' % ('{:,}'.format(n) if n else '-')
    print(row)
print('-' * len(head))
print('%-*s' % (width, 'TOTAL') + ''.join('%9s' % '{:,}'.format(totals[b]) for b, _ in BRANCHES))
print()
print('%d catalogs across 6 branches, %s messages in total'
      % (len(catalogs), '{:,}'.format(sum(totals.values()))))
