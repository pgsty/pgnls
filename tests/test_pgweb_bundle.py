import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

BIN = Path(__file__).resolve().parents[1] / 'bin'
sys.path.insert(0, str(BIN))
from poio import quote

spec = importlib.util.spec_from_file_location('pgweb_bundle', BIN / 'pgweb-bundle.py')
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.english = 'could not open file "%s"'
        for language, translation in [('zh_CN', '不能打开文件 "%s"'), ('zh_TW', '不能開啟檔案 "%s"')]:
            self.write(language, translation)

    def write(self, language, translation, english=None, fuzzy=False):
        header = 'Language: ' + language + '\nContent-Type: text/plain; charset=UTF-8\nPlural-Forms: nplurals=1; plural=0;\n'
        for parent, text, flags in [(self.root / language, translation, 'fuzzy, c-format' if fuzzy else 'c-format'),
                                    (self.root / 'upstream' / language, '旧译 "%s"', 'fuzzy, c-format')]:
            path = parent / 'master' / 'psql.po'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('msgid ""\nmsgstr ' + quote(header) + '\n\n#, ' + flags + '\nmsgid ' +
                            quote(english or self.english) + '\nmsgstr ' + quote(text) + '\n')

    def build(self, language):
        return bundle.build(language, {19}, self.root / 'upstream' / language, self.root)

    def test_languages_have_distinct_stable_ids_and_independent_candidates(self):
        cn, tw = self.build('zh_CN')[0], self.build('zh_TW')[0]
        self.assertNotEqual(cn['id'], tw['id'])
        self.assertEqual(tw['id'], self.build('zh_TW')[0]['id'])
        self.assertEqual(tw['suggested_forms'], {'': '不能開啟檔案 "%s"'})
        self.assertEqual((tw['language'], tw['pg_major']), ('zh_TW', 19))
        self.assertEqual((tw['human']['status'], tw['human']['version']), ('pending', 0))
        self.assertEqual(tw['context']['upstream']['status'], 'fuzzy')
        self.assertNotIn('fuzzy', tw['flags'])

    def test_original_translation_and_recommendation_revision_are_preserved(self):
        before = self.build('zh_TW')[0]
        self.write('zh_TW', '無法開啟檔案 "%s"')
        after = self.build('zh_TW')[0]
        self.assertEqual(before['id'], after['id'])
        self.assertNotEqual(before['revision'], after['revision'])
        self.assertEqual(after['original_forms'], {'': '旧译 "%s"'})

    def test_existing_identity_is_reused_before_revision_hashing(self):
        before = self.build('zh_CN')[0]
        path = self.root / 'identities.json'
        row = {key: before[key] for key in ('language', 'pg_major', 'component', 'msgctxt', 'msgid', 'msgid_plural')}
        row['id'] = 'legacy-message-id'
        path.write_text(json.dumps({'schema': 'pgnls-message-identities-v1', 'messages': [row]}))
        identities = bundle.load_identities(path)
        actual = bundle.build('zh_CN', {19}, self.root / 'upstream/zh_CN', self.root, identities)[0]
        self.assertEqual(actual['id'], 'legacy-message-id')
        expected = hashlib.sha256(json.dumps({'id': actual['id'], 'forms': actual['suggested_forms'],
            'plural_forms': actual['plural_forms']}, ensure_ascii=False,
            sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(actual['revision'], expected)
        self.assertNotEqual(before['revision'], actual['revision'])
        self.assertEqual(self.build('zh_TW')[0]['id'],
            bundle.build('zh_TW', {19}, self.root / 'upstream/zh_TW', self.root, identities)[0]['id'])
        path.write_text(json.dumps({'schema': 'pgnls-message-identities-v1', 'messages': [row, row]}))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            bundle.load_identities(path)

    def test_source_drift_and_missing_catalogs_fail_before_import(self):
        path = self.root / 'upstream/zh_TW/master/psql.po'
        path.write_text(path.read_text().replace('could not open', 'cannot open'))
        with self.assertRaisesRegex(ValueError, 'English messages differ'):
            self.build('zh_TW')
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'catalog files differ'):
            self.build('zh_TW')

    def test_incomplete_or_wrong_language_candidates_are_rejected(self):
        self.write('zh_TW', '不能開啟檔案 "%s"', fuzzy=True)
        with self.assertRaisesRegex(ValueError, 'incomplete candidate'):
            self.build('zh_TW')
        self.write('zh_TW', '')
        with self.assertRaisesRegex(ValueError, 'incomplete candidate'):
            self.build('zh_TW')
        self.write('zh_TW', '不能開啟檔案 "%s"')
        path = self.root / 'zh_TW/master/psql.po'
        path.write_text(path.read_text().replace('Language: zh_TW', 'Language: zh_CN'))
        with self.assertRaisesRegex(ValueError, 'incorrect Language'):
            self.build('zh_TW')
        self.write('zh_TW', '不能開啟檔案 "%s"')
        path = self.root / 'upstream/zh_TW/master/psql.po'
        path.write_text(path.read_text().replace('Language: zh_TW', 'Language: zh_CN'))
        with self.assertRaisesRegex(ValueError, 'incorrect Babel Language'):
            self.build('zh_TW')


if __name__ == '__main__':
    unittest.main()
