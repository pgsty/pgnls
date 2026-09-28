#!/usr/bin/env python3
"""Build a language-scoped PGWeb bundle from curated PO files and a Babel snapshot.

PO translations become review candidates, never automatic human approvals.
The existing pgweb nls_import command preserves any review work already saved.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from poio import read_po

ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = ('zh_CN', 'zh_TW')


def key(entry):
    return entry.msgctxt, entry.msgid, entry.msgid_plural or ''


def forms(entry):
    return {'' if index is None else str(index): value for index, value in entry.translations.items()}


def load_identities(path):
    if path is None:
        return {}
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8') as stream:
        payload = json.load(stream)
    if payload.get('schema') != 'pgnls-message-identities-v1':
        raise ValueError('Expected a PGWeb message identity export')
    identities, ids = {}, set()
    for row in payload['messages']:
        identity = (row['language'], row['pg_major'], row['component'], row['msgctxt'],
                    row['msgid'], row['msgid_plural'] or '')
        if identity in identities or row['id'] in ids:
            raise ValueError('Duplicate existing message identity or ID')
        identities[identity] = row['id']; ids.add(row['id'])
    return identities


def build(language, majors, upstream, root=ROOT, identities=None):
    identities = identities or {}
    rows = []
    for major in sorted(majors, reverse=True):
        branch = 'master' if major == 19 else f'REL_{major}_STABLE'
        curated = root / language / branch
        sources = upstream / branch
        paths = sorted(curated.glob('*.po'))
        if not paths or {p.name for p in paths} != {p.name for p in sources.glob('*.po')}:
            raise ValueError(f'{language} PG{major}: curated and Babel catalog files differ')
        ordinal = 0
        for path in paths:
            po, original = read_po(path), read_po(sources / path.name)
            metadata, old_metadata = po.metadata, original.metadata
            if metadata.get('Language') != language:
                raise ValueError(f'{path}: incorrect Language header')
            if old_metadata.get('Language') != language:
                raise ValueError(f'{sources / path.name}: incorrect Babel Language header')
            originals = {key(entry): entry for entry in original.active}
            current = {key(entry): entry for entry in po.active}
            if len(current) != len(po.active) or len(originals) != len(original.active) or current.keys() != originals.keys():
                raise ValueError(f'{path}: active English messages differ from Babel')
            for entry in po.active:
                ordinal += 1
                translation = forms(entry)
                if 'fuzzy' in entry.flags or not translation or not all(translation.values()):
                    raise ValueError(f'{path}: incomplete candidate: {entry.msgid}')
                old = originals[key(entry)]
                prior = forms(old)
                mid = identities.get((language, major, path.stem, *key(entry))) or entry.message_id(str(major), language, path.stem)
                revision = hashlib.sha256(json.dumps({'id': mid, 'forms': translation,
                    'plural_forms': metadata.get('Plural-Forms', '')}, ensure_ascii=False,
                    sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                matching = all(prior.get(k, '') == text for k, text in translation.items())
                kind = 'retained' if matching else 'revised' if any(prior.values()) else 'new'
                rows.append({'id': mid, 'language': language, 'pg_major': major, 'number': ordinal,
                    'component': path.stem, 'msgid': entry.msgid, 'msgid_plural': entry.msgid_plural or '',
                    'msgctxt': entry.msgctxt, 'flags': list(entry.flags),
                    'plural_forms': metadata.get('Plural-Forms', ''),
                    'original_forms': prior, 'suggested_forms': translation,
                    'suggestion_source': f'pgnls {language} PO',
                    'calibration': {'kind': kind, 'label': 'PO 译文待审校', 'previous_forms': prior,
                                    'previous_changed': not matching, 'recommendation_revision': revision},
                    'old_assessment': 'keep' if matching else 'change' if any(prior.values()) else 'empty',
                    'assessment_reason': f'从 pgnls {language} PO 导入候选；保留本语言的独立审校状态。',
                    'context': {'locations': '\n'.join(old.references),
                        'curated_po': {'path': f'{language}/{branch}/{path.name}', 'sha256': po.sha256},
                        'upstream': {'language': language, 'version': str(major), 'branch': branch,
                            'url': f'https://babel.postgresql.org/po-{major}-branch/{path.stem}-{language}.po',
                            'sha256': original.sha256, 'pot_creation_date': old_metadata.get('POT-Creation-Date', ''),
                            'plural_forms': old_metadata.get('Plural-Forms', ''), 'references': old.references,
                            'flags': old.flags, 'previous': old.previous, 'status': old.status}},
                    'revision': revision, 'workbook_sha256': '', 'plural_issue': '',
                    'human': {'status': 'pending', 'version': 0, 'forms': translation, 'note': ''}})
    if len({row['id'] for row in rows}) != len(rows):
        raise ValueError('Duplicate message IDs')
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language', choices=LANGUAGES, required=True)
    parser.add_argument('--major', type=int, choices=range(14, 20), action='append',
                        help='Repeat to select versions; defaults to PG14–19')
    parser.add_argument('--upstream', type=Path, required=True, help='Babel snapshot language directory')
    parser.add_argument('--output', type=Path, required=True, help='New .jsonl or .jsonl.gz file')
    parser.add_argument('--identity-map', type=Path, help='Existing PGWeb IDs from manage.py nls_export_ids')
    args = parser.parse_args()
    rows = build(args.language, set(args.major or range(14, 20)), args.upstream,
                 identities=load_identities(args.identity_map))
    header = {'kind': 'header', 'schema': 'pgnls-message-bundle-v1', 'language': args.language,
              'total': len(rows), 'source': 'pgnls PO catalogs'}
    opener = gzip.open if args.output.name.endswith('.gz') else open
    with opener(args.output, 'xt', encoding='utf-8') as output:
        for row in [header, *rows]:
            output.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(json.dumps({'language': args.language, 'messages': len(rows), 'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
