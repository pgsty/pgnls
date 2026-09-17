"""Lossless gettext PO reader and surgical msgstr/fuzzy patcher (stdlib only).

Source bytes are authoritative: parsed strings serve indexing and validation, never
whole-file serialization. Unchanged files and entries are returned byte-for-byte.
"""
from __future__ import annotations

import codecs
from dataclasses import dataclass, field
import hashlib
from functools import cached_property
import json
from pathlib import Path
import re
from typing import Optional


class POError(ValueError):
    pass


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) < 2 or value[0] != '"' or value[-1] != '"':
        raise POError(f"Invalid PO quoted string: {value[:100]!r}")
    value = value[1:-1]
    result = []
    escapes = {'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r',
               't': '\t', 'v': '\v', '\\': '\\', '"': '"', "'": "'", '?': '?'}
    i = 0
    while i < len(value):
        c = value[i]
        if c == '"':
            raise POError('Unescaped quote in PO string')
        if c != '\\':
            result.append(c)
            i += 1
            continue
        i += 1
        if i == len(value):
            raise POError('Trailing backslash in PO string')
        c = value[i]
        if c in escapes:
            result.append(escapes[c])
            i += 1
        elif c in '01234567':
            m = re.match(r'[0-7]{1,3}', value[i:])
            result.append(chr(int(m[0], 8)))
            i += len(m[0])
        elif c == 'x':
            m = re.match(r'[0-9a-fA-F]+', value[i + 1:])
            if not m:
                raise POError('Invalid hexadecimal PO escape')
            result.append(chr(int(m[0], 16)))
            i += 1 + len(m[0])
        else:
            raise POError(f'Unknown PO escape: \\{c}')
    return ''.join(result)


def quote(value: str) -> str:
    """One legal PO quoted string; actual line endings become PO escapes."""
    escapes = {'\\': '\\\\', '"': '\\"', '\a': '\\a', '\b': '\\b', '\f': '\\f',
               '\n': '\\n', '\r': '\\r', '\t': '\\t', '\v': '\\v'}
    out = []
    for c in value:
        if c in escapes:
            out.append(escapes[c])
        elif ord(c) < 32 or ord(c) == 127:
            out.append(f'\\{ord(c):03o}')
        else:
            out.append(c)
    return '"' + ''.join(out) + '"'


@dataclass
class Entry:
    fields: dict[str, str]
    spans: dict[str, tuple[int, int]]
    start: int
    end: int
    line: int
    raw: bytes
    obsolete: bool = False
    flags: list[str] = field(default_factory=list)
    flag_spans: list[tuple[int, int]] = field(default_factory=list)
    comments: list[str] = field(default_factory=list)
    translator_comments: list[str] = field(default_factory=list)
    extracted_comments: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    previous: dict[str, str] = field(default_factory=dict)

    @property
    def msgid(self):
        return self.fields['msgid']

    @property
    def msgctxt(self):
        return self.fields.get('msgctxt')

    @property
    def msgid_plural(self):
        return self.fields.get('msgid_plural')

    @property
    def is_header(self):
        return self.msgid == '' and 'msgctxt' not in self.fields and 'msgid_plural' not in self.fields

    @property
    def translations(self):
        if 'msgid_plural' not in self.fields:
            return {None: self.fields.get('msgstr', '')}
        return {int(k[7:-1]): v for k, v in self.fields.items() if re.fullmatch(r'msgstr\[\d+\]', k)}

    @property
    def status(self):
        values = list(self.translations.values())
        if not values or not all(values):
            return 'empty'
        return 'fuzzy' if 'fuzzy' in self.flags else 'translated'

    def message_id(self, version, language, component):
        key = [str(version), language, component, 'msgctxt' in self.fields,
               self.fields.get('msgctxt'), self.msgid,
               'msgid_plural' in self.fields, self.msgid_plural]
        encoded = json.dumps(key, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        return 'm_' + hashlib.sha256(encoded).hexdigest()

    def form_id(self, version, language, component, index):
        return self.message_id(version, language, component) + ':' + ('s' if index is None else str(index))


@dataclass
class POFile:
    data: bytes
    encoding: str
    entries: list[Entry]
    path: Optional[str] = None

    @cached_property
    def sha256(self):
        return hashlib.sha256(self.data).hexdigest()

    @property
    def active(self):
        return [e for e in self.entries if not e.obsolete and not e.is_header]

    @property
    def header(self):
        headers = [e for e in self.entries if not e.obsolete and e.is_header]
        return headers[0] if headers else None

    @property
    def metadata(self):
        value = self.header.fields.get('msgstr', '') if self.header else ''
        result = {}
        for line in value.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                result[k] = v.lstrip()
        return result

    def patch(self, changes: dict[int, dict[Optional[int], str]], clear_fuzzy=True) -> bytes:
        """Patch entries addressed by their byte start offset; never mutate this object."""
        patches = []
        by_start = {e.start: e for e in self.entries}
        for start, translations in changes.items():
            if start not in by_start:
                raise POError(f'Unknown entry offset {start}')
            e = by_start[start]
            if e.obsolete or e.is_header:
                raise POError('Header and obsolete edits require a separate metadata workflow')
            if set(translations) != set(e.translations):
                raise POError('Translation forms must exactly match the original entry')
            for index, text in translations.items():
                if not isinstance(text, str) or not text:
                    raise POError('Approved translation must be non-empty text')
                if text == e.translations[index]:
                    continue
                name = 'msgstr' if index is None else f'msgstr[{index}]'
                a, b = e.spans[name]
                old = self.data[a:b]
                newline = b'\r\n' if old.endswith(b'\r\n') else b'\n' if old.endswith(b'\n') else b''
                replacement = (name + ' ' + quote(text)).encode(self.encoding) + newline
                patches.append((a, b, replacement))
            if clear_fuzzy and 'fuzzy' in e.flags:
                for a, b in e.flag_spans:
                    line = self.data[a:b].decode(self.encoding)
                    body = line.rstrip('\r\n')
                    newline = line[len(body):]
                    prefix = body[:body.index(',') + 1]
                    tokens = body[len(prefix):].split(',')
                    keep = [t for t in tokens if t.strip() != 'fuzzy']
                    if len(keep) == len(tokens):
                        continue
                    replacement = (prefix + ','.join(keep) + newline).encode(self.encoding) if any(t.strip() for t in keep) else b''
                    patches.append((a, b, replacement))
        result = self.data
        boundary = len(result)
        for a, b, replacement in sorted(patches, reverse=True):
            if b > boundary:
                raise POError('Overlapping byte patches')
            result = result[:a] + replacement + result[b:]
            boundary = a
        return result


FIELD = re.compile(r'^(msgctxt|msgid_plural|msgid|msgstr(?:\[\d+\])?)\s+(".*")\s*$')


def parse_bytes(data: bytes, path=None) -> POFile:
    charset = re.search(br'charset=([A-Za-z0-9_.-]+)', data[:16384], re.I)
    encoding = charset[1].decode('ascii') if charset else 'utf-8'
    if encoding.upper() == 'CHARSET':
        encoding = 'utf-8'
    try:
        encoding = codecs.lookup(encoding).name
    except LookupError as exc:
        raise POError(f'Unsupported PO encoding: {encoding}') from exc
    lines = data.splitlines(keepends=True)
    offsets, offset = [], 0
    for raw in lines:
        offsets.append(offset)
        offset += len(raw)
    result = []
    entry = None
    current = None
    previous_current = None
    pending = []

    def finish():
        nonlocal entry, current, previous_current
        if entry is not None:
            if 'msgid' not in entry.fields:
                raise POError(f'Missing msgid at line {entry.line}')
            if 'msgid_plural' in entry.fields:
                if 'msgstr' in entry.fields or not entry.translations:
                    raise POError(f'Invalid plural forms at line {entry.line}')
            elif 'msgstr' not in entry.fields or any(k.startswith('msgstr[') for k in entry.fields):
                raise POError(f'Invalid singular msgstr at line {entry.line}')
            entry.raw = data[entry.start:entry.end]
            result.append(entry)
        entry, current, previous_current = None, None, None

    def comment(item):
        nonlocal previous_current
        n, a, b, line = item
        entry.comments.append(line)
        entry.end = b
        normalized = '#' + line[2:] if line.startswith('#~|') else line[2:].lstrip() if line.startswith('#~') else line
        if normalized.startswith('#,'):
            entry.flags.extend(x.strip() for x in normalized[2:].split(',') if x.strip())
            entry.flag_spans.append((a, b))
        elif normalized.startswith('#.'):
            entry.extracted_comments.append(normalized[2:].lstrip())
        elif normalized.startswith('#:'):
            entry.references.extend(normalized[2:].split())
        elif normalized.startswith('#|'):
            payload = normalized[2:].lstrip()
            match = FIELD.match(payload)
            if match:
                previous_current = match[1]
                entry.previous[previous_current] = unquote(match[2])
            elif payload.startswith('"') and previous_current:
                entry.previous[previous_current] += unquote(payload)
        elif normalized.startswith('#'):
            entry.translator_comments.append(normalized[1:].lstrip())

    for n, raw in enumerate(lines, 1):
        a, b = offsets[n-1], offsets[n-1] + len(raw)
        try:
            line = raw.decode(encoding).rstrip('\r\n')
        except UnicodeDecodeError as exc:
            raise POError(f'{path or "<bytes>"}:{n}: invalid {encoding} text') from exc
        if n == 1:
            line = line.removeprefix('\ufeff')
        if not line.strip():
            finish()
            pending = []
            continue
        obsolete = line.startswith('#~') and not line.startswith('#~|')
        payload = line[2:].lstrip() if obsolete else line
        match = FIELD.match(payload)
        continuation = payload.startswith('"')
        if not match and not continuation:
            if not line.startswith('#'):
                raise POError(f'{path or "<bytes>"}:{n}: unexpected PO syntax {line[:100]!r}')
            if entry and any(k.startswith('msgstr') for k in entry.fields):
                finish()
            pending.append((n, a, b, line))
            continue
        if match and match[1] in ('msgid', 'msgctxt') and entry is not None and (match[1] in entry.fields or any(k.startswith('msgstr') for k in entry.fields)):
            finish()
        if entry is None:
            if not match:
                raise POError(f'Orphan PO continuation at line {n}')
            entry = Entry({}, {}, pending[0][1] if pending else a, b, pending[0][0] if pending else n, b'', obsolete)
            for item in pending:
                comment(item)
            pending = []
        if obsolete != entry.obsolete:
            raise POError(f'Mixed obsolete and current fields at line {n}')
        if match:
            current, value = match.groups()
            if current in entry.fields:
                raise POError(f'Duplicate {current} at line {n}')
            entry.fields[current] = unquote(value)
            entry.spans[current] = (a, b)
        else:
            if current is None:
                raise POError(f'Orphan continuation at line {n}')
            entry.fields[current] += unquote(payload)
            entry.spans[current] = (entry.spans[current][0], b)
        entry.end = b
    finish()
    po = POFile(data, encoding, result, str(path) if path else None)
    seen = set()
    for e in po.entries:
        if e.obsolete:
            continue
        key = ('msgctxt' in e.fields, e.msgctxt, e.msgid)
        if key in seen:
            raise POError(f'Duplicate active message key at line {e.line}')
        seen.add(key)
    return po


def read_po(path) -> POFile:
    path = Path(path)
    return parse_bytes(path.read_bytes(), path)
