#!/usr/bin/env python3
"""Check column alignment in translated terminal output.

A CJK character occupies two columns in a monospace terminal, so a translated
label is rarely the same display width as the English one. Copying the original
spacing therefore breaks the columns; the padding has to be recomputed.

What this checks, per catalog:

  1. Columns agree. Within one branch and catalog, lines whose English text
     puts a column at the same place must put the Chinese column at the same
     place as each other. The Chinese column may sit elsewhere than the English
     one -- that is the whole point -- but two lines that line up in English
     must still line up in Chinese. Only catalogs that actually pad to a column
     are held to this: where every English gap is the bare two spaces, the gap
     is a delimiter (libpq's "DETAIL:  %s") rather than padding, and nothing is
     being aligned.
  2. Structure survives. A line whose English has a run of two or more spaces
     separating columns must still have one in the translation.
  3. Continuation lines stay under their description. Where an English help
     entry wraps and the continuation is indented to the description column, the
     Chinese continuation must be indented to the Chinese description column.
  4. Metavariables are left alone. --option=DBNAME keeps DBNAME, so the option
     column keeps its width.

Exits 1 if anything fails. No database, no network; stdlib plus poio.
"""
import collections
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'bin'))
import poio

# "label:" followed by padding and a value, as pg_controldata and friends print.
LABEL = re.compile(r'^(?:[^\s%][^%\n]*?:) {2,}(?=%)')
# "  -x, --xxx=ARG   description", as --help prints.
OPTION = re.compile(r'^(?:\s+-{1,2}[\w?][^\s]*(?:, --[^\s]+)?(?:[ =][A-Z][A-Z_]*)?) {2,}(?=\S)')
INDENT = re.compile(r'^( {4,})(?=\S)')
METAVAR = re.compile(r'--[\w-]+=([A-Z][A-Z_]{2,})')
KINDS = (('label', LABEL), ('option', OPTION))


def width(text):
    """Columns the text occupies in a monospace terminal."""
    total = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        total += 2 if unicodedata.east_asian_width(ch) in 'WF' else 1
    return total


def forms(entry):
    """The translation of a message; plural entries share one Chinese form."""
    for value in entry.translations.values():
        return value
    return ''


def main():
    problems = []
    # (branch, catalog, kind, english column) -> {chinese column: [rows]}
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    # (branch, catalog, kind) -> does the English pad beyond the bare separator?
    padded = collections.defaultdict(bool)
    checked = continuations = 0

    for path in sorted((ROOT / 'zh_CN').rglob('*.po')):
        branch, catalog = path.parts[-2], path.stem
        rel = path.relative_to(ROOT)
        for entry in poio.read_po(path).active:
            english, chinese = entry.msgid, forms(entry)
            if not chinese:
                continue

            for line in english.split('\n'):
                for name in METAVAR.findall(line):
                    if name not in chinese:
                        problems.append('%s:%d metavariable %s was translated away'
                                        % (rel, entry.line, name))

            if english.count('\n') != chinese.count('\n'):
                continue          # a width-wrapped sentence joined into one line

            description_en = description_zh = None
            for en_line, zh_line in zip(english.split('\n'), chinese.split('\n')):
                matched = False
                for kind, pattern in KINDS:
                    hit_en = pattern.match(en_line)
                    if not hit_en:
                        continue
                    matched = True
                    checked += 1
                    hit_zh = pattern.match(zh_line)
                    if not hit_zh:
                        problems.append('%s:%d column separator lost: %r'
                                        % (rel, entry.line, zh_line[:60]))
                        break
                    column_en = width(en_line[:hit_en.end()])
                    column_zh = width(zh_line[:hit_zh.end()])
                    gap = len(en_line[:hit_en.end()]) - len(en_line[:hit_en.end()].rstrip())
                    if gap > 2:
                        padded[(branch, catalog, kind)] = True
                    groups[(branch, catalog, kind, column_en)][column_zh].append(
                        (str(rel), entry.line, en_line, zh_line))
                    if kind == 'option':
                        description_en, description_zh = column_en, column_zh
                    break
                if matched or description_en is None:
                    continue
                # A continuation line sitting under the description column.
                indent_en = INDENT.match(en_line)
                if not indent_en or width(indent_en.group(1)) != description_en:
                    continue
                continuations += 1
                indent_zh = INDENT.match(zh_line)
                if not indent_zh or width(indent_zh.group(1)) != description_zh:
                    problems.append(
                        '%s:%d continuation indented to %s, description column is %d: %r'
                        % (rel, entry.line,
                           width(indent_zh.group(1)) if indent_zh else 'none',
                           description_zh, zh_line[:60]))

    for (branch, catalog, kind, column_en), by_zh in sorted(groups.items()):
        if len(by_zh) == 1 or not padded[(branch, catalog, kind)]:
            continue
        winner = max(by_zh, key=lambda c: len(by_zh[c]))
        for column_zh, items in sorted(by_zh.items()):
            if column_zh == winner:
                continue
            path, line, en_line, zh_line = items[0]
            problems.append(
                '%s:%d %s lines at English column %d sit at Chinese column %d, '
                'but %d others sit at %d: %r'
                % (path, line, kind, column_en, column_zh,
                   len(by_zh[winner]), winner, zh_line[:60]))

    print('  %s aligned lines, %s continuation lines, %s column groups'
          % (format(checked, ','), format(continuations, ','), format(len(groups), ',')))
    print()
    if problems:
        print('FAIL - %d problem(s):' % len(problems))
        for line in problems[:40]:
            print('  ' + line)
        if len(problems) > 40:
            print('  ... and %d more' % (len(problems) - 40))
        return 1
    print('OK - columns agree within every group, separators and continuation '
          'indents survive, metavariables intact.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
