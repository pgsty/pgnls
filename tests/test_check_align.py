"""Regression coverage for approved psql usage placeholder localization."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('check_align', ROOT / 'bin/check-align.py')
check_align = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_align)


class LocalizedUsageTests(unittest.TestCase):
    def check(self, english, chinese, language='zh_TW', branch='master', catalog='psql'):
        return check_align.missing_metavariables(english, chinese, language, branch, catalog)

    def test_approved_complete_examples_pass(self):
        for english, chinese in check_align.LOCALIZED_PSQL_USAGE.items():
            with self.subTest(english=english):
                self.assertEqual(self.check(english, chinese), [])

    def test_changed_commands_values_and_optional_brackets_fail(self):
        for english, chinese in check_align.LOCALIZED_PSQL_USAGE.items():
            variants = [chinese.replace('--', '-', 1), chinese.replace('值', '', 1),
                        chinese.replace('\\', '', 1), chinese.replace('名稱', '名', 1)]
            if '[' in chinese:
                variants += [chinese.replace('[', '', 1), chinese.replace(']', '', 1)]
            for changed in variants:
                with self.subTest(chinese=changed):
                    self.assertEqual(self.check(english, changed), ['NAME'])

    def test_exception_is_scoped_to_reviewed_language_branch_and_catalog(self):
        for english, chinese in check_align.LOCALIZED_PSQL_USAGE.items():
            self.assertEqual(self.check(english, chinese, language='zh_CN'), ['NAME'])
            self.assertEqual(self.check(english, chinese, branch='REL_18_STABLE'), ['NAME'])
            self.assertEqual(self.check(english, chinese, catalog='pg_dump'), ['NAME'])

    def test_option_list_metavariables_still_require_original_names(self):
        english = '  -d, --dbname=DBNAME    database to connect to\n'
        self.assertEqual(self.check(english, '  -d, --dbname=DBNAME    連線的資料庫\n'), [])
        self.assertEqual(self.check(english, '  -d, --dbname=資料庫    連線的資料庫\n'), ['DBNAME'])


if __name__ == '__main__':
    unittest.main()
