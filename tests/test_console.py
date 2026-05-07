import os
import tempfile
import unittest
from unittest.mock import patch, call
from app.repository import Repository
from app.console import ConsoleApp, format_record, format_record_list


class TestFormatRecord(unittest.TestCase):

    def test_format_record_includes_id(self):
        record = {'id': 1, 'name': 'Alice'}
        result = format_record(record)
        self.assertIn('1', result)

    def test_format_record_includes_all_fields(self):
        record = {'id': 1, 'name': 'Alice', 'age': '30'}
        result = format_record(record)
        self.assertIn('name', result)
        self.assertIn('Alice', result)
        self.assertIn('age', result)
        self.assertIn('30', result)

    def test_format_record_excludes_id_from_fields(self):
        record = {'id': 1, 'name': 'Alice'}
        result = format_record(record)
        lines = result.strip().splitlines()
        field_lines = [l for l in lines if 'id' in l.lower() and 'name' not in l.lower()]
        # id 는 헤더 역할로만 쓰이고 필드 목록에 중복 출력되지 않아야 함
        self.assertLessEqual(len(field_lines), 1)


class TestFormatRecordList(unittest.TestCase):

    def test_empty_list_message(self):
        result = format_record_list([])
        self.assertIn('없', result)  # "데이터가 없습니다" 류의 메시지

    def test_list_includes_all_ids(self):
        records = [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
        result = format_record_list(records)
        self.assertIn('1', result)
        self.assertIn('2', result)

    def test_list_includes_field_values(self):
        records = [{'id': 1, 'name': 'Alice'}]
        result = format_record_list(records)
        self.assertIn('Alice', result)


class TestConsoleCreate(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.app = ConsoleApp(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_create_record_via_input(self):
        inputs = ['name', 'Alice', 'age', '30', '', '0']
        with patch('builtins.input', side_effect=inputs), \
             patch('builtins.print'):
            self.app.cmd_create()

        repo = Repository(self._tmp.name)
        records = repo.read_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Alice')
        self.assertEqual(records[0]['age'], '30')

    def test_create_empty_input_does_not_save(self):
        inputs = ['']
        with patch('builtins.input', side_effect=inputs), \
             patch('builtins.print'):
            self.app.cmd_create()

        repo = Repository(self._tmp.name)
        self.assertEqual(len(repo.read_all()), 0)


class TestConsoleDelete(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.repo = Repository(self._tmp.name)
        self.app = ConsoleApp(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_delete_existing_record_with_confirmation(self):
        record = self.repo.create({'name': 'Alice'})
        with patch('builtins.input', side_effect=[str(record['id']), 'y']), \
             patch('builtins.print'):
            self.app.cmd_delete()
        self.assertIsNone(self.repo.read_one(record['id']))

    def test_delete_cancelled_by_confirmation(self):
        record = self.repo.create({'name': 'Alice'})
        with patch('builtins.input', side_effect=[str(record['id']), 'n']), \
             patch('builtins.print'):
            self.app.cmd_delete()
        self.assertIsNotNone(self.repo.read_one(record['id']))

    def test_delete_nonexistent_prints_error(self):
        printed = []
        with patch('builtins.input', return_value='999'), \
             patch('builtins.print', side_effect=lambda *a, **k: printed.append(' '.join(str(x) for x in a))):
            self.app.cmd_delete()
        self.assertTrue(any('없' in line or 'error' in line.lower() or '실패' in line for line in printed))


class TestConsoleUpdate(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.repo = Repository(self._tmp.name)
        self.app = ConsoleApp(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_update_existing_record(self):
        record = self.repo.create({'name': 'Alice', 'age': '30'})
        inputs = [str(record['id']), 'name', 'Bob', '']
        with patch('builtins.input', side_effect=inputs), \
             patch('builtins.print'):
            self.app.cmd_update()
        updated = self.repo.read_one(record['id'])
        self.assertEqual(updated['name'], 'Bob')
        self.assertEqual(updated['age'], '30')

    def test_update_nonexistent_field_shows_error(self):
        record = self.repo.create({'name': 'Alice'})
        # 존재하지 않는 필드 'email' 입력 후 종료
        inputs = [str(record['id']), 'email', '']
        printed = []
        with patch('builtins.input', side_effect=inputs), \
             patch('builtins.print', side_effect=lambda *a, **k: printed.append(' '.join(str(x) for x in a))):
            self.app.cmd_update()
        # 필드가 추가되지 않아야 함
        updated = self.repo.read_one(record['id'])
        self.assertNotIn('email', updated)
        # 오류 안내 메시지가 출력되어야 함
        self.assertTrue(any('없' in line for line in printed))

    def test_update_skips_invalid_then_accepts_valid(self):
        record = self.repo.create({'name': 'Alice', 'age': '30'})
        # 존재하지 않는 'email' 입력 후 존재하는 'name' 수정
        inputs = [str(record['id']), 'email', 'name', 'Bob', '']
        with patch('builtins.input', side_effect=inputs), \
             patch('builtins.print'):
            self.app.cmd_update()
        updated = self.repo.read_one(record['id'])
        self.assertNotIn('email', updated)
        self.assertEqual(updated['name'], 'Bob')


class TestConsoleSearch(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.repo = Repository(self._tmp.name)
        self.app = ConsoleApp(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_search_prints_matching_records(self):
        self.repo.create({'name': 'Alice', 'city': 'Seoul'})
        self.repo.create({'name': 'Bob', 'city': 'Busan'})
        printed = []
        with patch('builtins.input', side_effect=['name', 'Alice']), \
             patch('builtins.print', side_effect=lambda *a, **k: printed.append(' '.join(str(x) for x in a))):
            self.app.cmd_search()
        self.assertTrue(any('Alice' in line for line in printed))
        self.assertFalse(any('Bob' in line for line in printed))

    def test_search_no_results_prints_message(self):
        self.repo.create({'name': 'Alice'})
        printed = []
        with patch('builtins.input', side_effect=['name', 'Charlie']), \
             patch('builtins.print', side_effect=lambda *a, **k: printed.append(' '.join(str(x) for x in a))):
            self.app.cmd_search()
        self.assertTrue(any('없' in line for line in printed))


if __name__ == '__main__':
    unittest.main()
