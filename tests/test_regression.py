"""
Regression Tests — docs/SPEC.md 요구사항 기준

각 테스트 클래스는 SPEC.md의 항목 하나에 대응합니다.
요구사항에 명시된 기능이 실제로 동작하는지를 검증합니다.
"""

import os
import tempfile
import unittest
from unittest.mock import patch
from app.repository import Repository
from app.console import ConsoleApp


def make_repo():
    """임시 파일 기반 Repository와 경로를 반환합니다."""
    tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    tmp.close()
    os.unlink(tmp.name)
    return Repository(tmp.name), tmp.name


class TestSpecCreate(unittest.TestCase):
    """SPEC: Create — 새로운 데이터를 입력 받아 JSON 파일에 저장."""

    def setUp(self):
        self.repo, self.path = make_repo()

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_created_data_is_saved_to_file(self):
        """생성한 데이터가 JSON 파일에 실제로 저장되어야 한다."""
        self.repo.create({'name': 'Alice', 'age': '30'})
        self.assertTrue(os.path.exists(self.path))

    def test_created_data_can_be_reloaded(self):
        """저장된 데이터는 새 인스턴스에서도 동일하게 읽혀야 한다."""
        self.repo.create({'name': 'Alice', 'age': '30'})
        reloaded = Repository(self.path).read_all()
        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded[0]['name'], 'Alice')
        self.assertEqual(reloaded[0]['age'], '30')

    def test_created_record_has_unique_id(self):
        """생성된 각 레코드는 고유한 ID를 가져야 한다."""
        r1 = self.repo.create({'title': 'first'})
        r2 = self.repo.create({'title': 'second'})
        self.assertNotEqual(r1['id'], r2['id'])

    def test_create_via_console_saves_to_file(self):
        """콘솔 추가 명령으로 입력한 데이터가 파일에 저장되어야 한다."""
        app = ConsoleApp(self.path)
        inputs = ['name', 'Bob', 'city', 'Seoul', '']
        with patch('builtins.input', side_effect=inputs), patch('builtins.print'):
            app.cmd_create()
        records = self.repo.read_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Bob')
        self.assertEqual(records[0]['city'], 'Seoul')

    def test_create_supports_any_fields(self):
        """필드 구조가 고정되지 않고 어떤 키-값이든 저장되어야 한다."""
        r1 = self.repo.create({'title': 'meeting', 'date': '2026-05-07'})
        r2 = self.repo.create({'product': 'pen', 'price': '1000', 'stock': '50'})
        self.assertIn('title', r1)
        self.assertIn('product', r2)
        self.assertNotIn('product', r1)


class TestSpecRead(unittest.TestCase):
    """SPEC: Read — 전체 목록 보기 및 특정 ID/키값으로 검색 기능."""

    def setUp(self):
        self.repo, self.path = make_repo()
        self.r1 = self.repo.create({'name': 'Alice', 'city': 'Seoul'})
        self.r2 = self.repo.create({'name': 'Bob',   'city': 'Busan'})
        self.r3 = self.repo.create({'name': 'Carol', 'city': 'Seoul'})

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_read_all_returns_every_record(self):
        """전체 목록 조회 시 저장된 모든 레코드가 반환되어야 한다."""
        result = self.repo.read_all()
        self.assertEqual(len(result), 3)

    def test_read_by_id_returns_correct_record(self):
        """특정 ID 조회 시 해당 레코드만 반환되어야 한다."""
        result = self.repo.read_one(self.r2['id'])
        self.assertEqual(result['name'], 'Bob')

    def test_read_by_id_returns_none_for_missing(self):
        """존재하지 않는 ID 조회 시 None이 반환되어야 한다."""
        self.assertIsNone(self.repo.read_one(999))

    def test_search_by_key_value_returns_matching_records(self):
        """키-값 검색 시 해당 조건에 맞는 레코드만 반환되어야 한다."""
        result = self.repo.search('city', 'Seoul')
        self.assertEqual(len(result), 2)
        names = {r['name'] for r in result}
        self.assertIn('Alice', names)
        self.assertIn('Carol', names)
        self.assertNotIn('Bob', names)

    def test_search_returns_empty_when_no_match(self):
        """검색 결과가 없을 때 빈 목록이 반환되어야 한다."""
        result = self.repo.search('city', 'Daegu')
        self.assertEqual(result, [])

    def test_search_via_console_shows_only_matching(self):
        """콘솔 검색 명령이 일치하는 레코드만 출력해야 한다."""
        app = ConsoleApp(self.path)
        printed = []
        with patch('builtins.input', side_effect=['city', 'Seoul']), \
             patch('builtins.print', side_effect=lambda *a, **k: printed.append(' '.join(str(x) for x in a))):
            app.cmd_search()
        output = '\n'.join(printed)
        self.assertIn('Alice', output)
        self.assertIn('Carol', output)
        self.assertNotIn('Bob', output)


class TestSpecUpdate(unittest.TestCase):
    """SPEC: Update — 기존 데이터를 선택하여 특정 필드 수정."""

    def setUp(self):
        self.repo, self.path = make_repo()
        self.record = self.repo.create({'name': 'Alice', 'age': '30', 'city': 'Seoul'})

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_update_modifies_specified_field(self):
        """수정 대상 필드의 값이 변경되어야 한다."""
        self.repo.update(self.record['id'], {'name': 'Bob'})
        updated = self.repo.read_one(self.record['id'])
        self.assertEqual(updated['name'], 'Bob')

    def test_update_preserves_other_fields(self):
        """수정하지 않은 나머지 필드는 그대로 유지되어야 한다."""
        self.repo.update(self.record['id'], {'name': 'Bob'})
        updated = self.repo.read_one(self.record['id'])
        self.assertEqual(updated['age'], '30')
        self.assertEqual(updated['city'], 'Seoul')

    def test_update_persists_to_file(self):
        """수정된 내용은 파일에 반영되어 재로드 후에도 유지되어야 한다."""
        self.repo.update(self.record['id'], {'age': '31'})
        reloaded = Repository(self.path).read_one(self.record['id'])
        self.assertEqual(reloaded['age'], '31')

    def test_update_nonexistent_id_has_no_effect(self):
        """존재하지 않는 ID 수정 시 데이터에 영향이 없어야 한다."""
        result = self.repo.update(999, {'name': 'Ghost'})
        self.assertIsNone(result)
        all_records = self.repo.read_all()
        self.assertEqual(len(all_records), 1)

    def test_update_via_console_rejects_nonexistent_field(self):
        """콘솔 수정 명령에서 존재하지 않는 필드는 추가되지 않아야 한다."""
        app = ConsoleApp(self.path)
        inputs = [str(self.record['id']), 'email', '']
        with patch('builtins.input', side_effect=inputs), patch('builtins.print'):
            app.cmd_update()
        updated = self.repo.read_one(self.record['id'])
        self.assertNotIn('email', updated)


class TestSpecDelete(unittest.TestCase):
    """SPEC: Delete — 특정 데이터를 안전하게 삭제."""

    def setUp(self):
        self.repo, self.path = make_repo()
        self.record = self.repo.create({'name': 'Alice'})

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_delete_removes_target_record(self):
        """삭제 후 해당 레코드가 존재하지 않아야 한다."""
        self.repo.delete(self.record['id'])
        self.assertIsNone(self.repo.read_one(self.record['id']))

    def test_delete_preserves_other_records(self):
        """삭제 시 다른 레코드는 영향받지 않아야 한다."""
        r2 = self.repo.create({'name': 'Bob'})
        self.repo.delete(self.record['id'])
        self.assertIsNotNone(self.repo.read_one(r2['id']))

    def test_delete_via_console_requires_confirmation(self):
        """콘솔 삭제는 확인(y/n) 없이 즉시 삭제되지 않아야 한다 — 안전한 삭제."""
        app = ConsoleApp(self.path)
        # 'n' 으로 취소
        with patch('builtins.input', side_effect=[str(self.record['id']), 'n']), \
             patch('builtins.print'):
            app.cmd_delete()
        self.assertIsNotNone(self.repo.read_one(self.record['id']))

    def test_delete_via_console_confirmed_removes_record(self):
        """콘솔 삭제에서 'y' 확인 후 레코드가 삭제되어야 한다."""
        app = ConsoleApp(self.path)
        with patch('builtins.input', side_effect=[str(self.record['id']), 'y']), \
             patch('builtins.print'):
            app.cmd_delete()
        self.assertIsNone(self.repo.read_one(self.record['id']))

    def test_delete_nonexistent_id_has_no_effect(self):
        """존재하지 않는 ID 삭제 시도는 기존 데이터에 영향이 없어야 한다."""
        result = self.repo.delete(999)
        self.assertFalse(result)
        self.assertEqual(len(self.repo.read_all()), 1)


if __name__ == '__main__':
    unittest.main()
