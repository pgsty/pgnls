#!/usr/bin/env python3
"""Validate every catalog under zh_CN/ — no database, no network, stdlib + GNU msgfmt.

Per file: it parses losslessly, compiles under `msgfmt --check --check-format`,
is 100% translated with no fuzzy flag, no empty form, no surviving msgstr[1] and
no leftover '#|' previous-message comment, and carries the header fields this
repository commits to. Exits 1 on the first category of problem found.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'bin'))
import poio

BRANCHES = [('master', 19), ('REL_18_STABLE', 18), ('REL_17_STABLE', 17),
            ('REL_16_STABLE', 16), ('REL_15_STABLE', 15), ('REL_14_STABLE', 14)]
EXPECTED = {'master': (28, 12638), 'REL_18_STABLE': (28, 12098), 'REL_17_STABLE': (28, 11509),
            'REL_16_STABLE': (26, 10656), 'REL_15_STABLE': (26, 10463), 'REL_14_STABLE': (26, 10125)}
HEADER = {
    'Report-Msgid-Bugs-To': 'pgsql-bugs@lists.postgresql.org',
    'Language': 'zh_CN',
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=UTF-8',
    'Content-Transfer-Encoding': '8bit',
    'Plural-Forms': 'nplurals=1; plural=0;',
    'Language-Team': 'Chinese (Simplified) <pgsql-translators@postgresql.org>',
    'Last-Translator': 'Ruohang Feng <rh@vonng.com>',
}


def main():
    problems = []
    grand_files = grand_msgs = 0
    rows = []
    have_msgfmt = subprocess.run(['which', 'msgfmt'], capture_output=True).returncode == 0
    if not have_msgfmt:
        problems.append('msgfmt not found on PATH; install GNU gettext for the strict check')

    for branch, major in BRANCHES:
        directory = ROOT / 'zh_CN' / branch
        if not directory.is_dir():
            problems.append('missing directory: zh_CN/%s' % branch)
            continue
        files = sorted(directory.glob('*.po'))
        msgs = 0
        for path in files:
            rel = path.relative_to(ROOT)
            po = poio.read_po(path)

            if have_msgfmt:
                run = subprocess.run(['msgfmt', '--check', '--check-format', '--statistics',
                                      '-o', '/dev/null', str(path)], capture_output=True, text=True)
                out = run.stdout + run.stderr
                if run.returncode != 0:
                    problems.append('%s: msgfmt failed: %s' % (rel, out.strip().splitlines()[0]))
                    continue
                if 'untranslated' in out or 'fuzzy' in out:
                    problems.append('%s: not complete: %s' % (rel, out.strip()))
                found = re.search(r'(\d+) translated messages?\.', out)
                n = int(found.group(1)) if found else 0
            else:
                n = len(po.active)

            for entry in po.active:
                if 'fuzzy' in entry.flags:
                    problems.append('%s:%d fuzzy flag survived' % (rel, entry.line))
                if entry.previous:
                    problems.append('%s:%d "#|" previous-message comment survived' % (rel, entry.line))
                if 'msgstr[1]' in entry.fields:
                    problems.append('%s:%d msgstr[1] survived the plural collapse' % (rel, entry.line))
                if not all(entry.translations.values()):
                    problems.append('%s:%d empty translation' % (rel, entry.line))

            meta = po.metadata
            for key, want in HEADER.items():
                if meta.get(key) != want:
                    problems.append('%s: header %s is %r, expected %r' % (rel, key, meta.get(key), want))
            want_version = '%s (PostgreSQL) %d' % (path.stem, major)
            if meta.get('Project-Id-Version') != want_version:
                problems.append('%s: header Project-Id-Version is %r, expected %r'
                                % (rel, meta.get('Project-Id-Version'), want_version))
            if 'X-Generator' in meta:
                problems.append('%s: stale X-Generator header' % rel)
            if len(po.active) != n:
                problems.append('%s: %d entries but msgfmt counted %d' % (rel, len(po.active), n))
            msgs += n

        want_files, want_msgs = EXPECTED.get(branch, (len(files), msgs))
        flag = '' if (len(files), msgs) == (want_files, want_msgs) else \
               '   != expected %d/%d' % (want_files, want_msgs)
        if flag:
            problems.append('zh_CN/%s: %d catalogs / %d messages, expected %d / %d'
                            % (branch, len(files), msgs, want_files, want_msgs))
        rows.append('  %-16s PG%-3d %2d catalogs %7s messages%s'
                    % (branch, major, len(files), '{:,}'.format(msgs), flag))
        grand_files += len(files)
        grand_msgs += msgs

    print('\n'.join(rows))
    print('  %-16s      %2d catalogs %7s messages' % ('TOTAL', grand_files, '{:,}'.format(grand_msgs)))
    print()
    if problems:
        print('FAIL — %d problem(s):' % len(problems))
        for line in problems[:40]:
            print('  ' + line)
        if len(problems) > 40:
            print('  ... and %d more' % (len(problems) - 40))
        return 1
    print('OK — every catalog is 100% translated, 0 fuzzy, 0 untranslated, msgfmt clean.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
