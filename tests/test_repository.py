import os
import tempfile
import unittest
from app.repository import Repository


class TestRepositoryCreate(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)  # 파일 없는 상태로 시작
        self.repo = Repository(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_create_returns_record_with_id(self):
        record = self.repo.create({'name': 'Alice'})
        self.assertIn('id', record)

    def test_create_stores_all_fields(self):
        record = self.repo.create({'name': 'Alice', 'age': '30'})
        self.assertEqual(record['name'], 'Alice')
        self.assertEqual(record['age'], '30')

    def test_create_assigns_incremental_id(self):
        r1 = self.repo.create({'name': 'Alice'})
        r2 = self.repo.create({'name': 'Bob'})
        self.assertLess(r1['id'], r2['id'])

    def test_create_initializes_file_if_not_exists(self):
        self.repo.create({'key': 'value'})
        self.assertTrue(os.path.exists(self._tmp.name))

    def test_create_different_fields_per_record(self):
        r1 = self.repo.create({'title': 'meeting'})
        r2 = self.repo.create({'name': 'Alice', 'phone': '010-0000-0000'})
        self.assertNotEqual(r1['id'], r2['id'])
        self.assertIn('title', r1)
        self.assertIn('phone', r2)


class TestRepositoryRead(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.repo = Repository(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_read_all_empty_when_no_file(self):
        result = self.repo.read_all()
        self.assertEqual(result, [])

    def test_read_all_returns_all_records(self):
        self.repo.create({'name': 'Alice'})
        self.repo.create({'name': 'Bob'})
        result = self.repo.read_all()
        self.assertEqual(len(result), 2)

    def test_read_one_existing(self):
        created = self.repo.create({'name': 'Alice'})
        result = self.repo.read_one(created['id'])
        self.assertEqual(result['name'], 'Alice')

    def test_read_one_nonexistent_returns_none(self):
        result = self.repo.read_one(999)
        self.assertIsNone(result)


class TestRepositoryUpdate(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.repo = Repository(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_update_existing_record(self):
        created = self.repo.create({'name': 'Alice', 'age': '30'})
        updated = self.repo.update(created['id'], {'name': 'Bob'})
        self.assertEqual(updated['name'], 'Bob')
        self.assertEqual(updated['age'], '30')  # 나머지 필드 유지

    def test_update_adds_new_field(self):
        created = self.repo.create({'name': 'Alice'})
        updated = self.repo.update(created['id'], {'email': 'alice@example.com'})
        self.assertEqual(updated['email'], 'alice@example.com')
        self.assertEqual(updated['name'], 'Alice')

    def test_update_nonexistent_returns_none(self):
        result = self.repo.update(999, {'name': 'Ghost'})
        self.assertIsNone(result)

    def test_update_persists_to_file(self):
        created = self.repo.create({'name': 'Alice'})
        self.repo.update(created['id'], {'name': 'Bob'})
        reloaded = Repository(self._tmp.name).read_one(created['id'])
        self.assertEqual(reloaded['name'], 'Bob')


class TestRepositoryDelete(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.repo = Repository(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_delete_existing_returns_true(self):
        created = self.repo.create({'name': 'Alice'})
        result = self.repo.delete(created['id'])
        self.assertTrue(result)

    def test_delete_removes_record(self):
        created = self.repo.create({'name': 'Alice'})
        self.repo.delete(created['id'])
        self.assertIsNone(self.repo.read_one(created['id']))

    def test_delete_nonexistent_returns_false(self):
        result = self.repo.delete(999)
        self.assertFalse(result)

    def test_delete_only_removes_target(self):
        r1 = self.repo.create({'name': 'Alice'})
        r2 = self.repo.create({'name': 'Bob'})
        self.repo.delete(r1['id'])
        self.assertIsNone(self.repo.read_one(r1['id']))
        self.assertIsNotNone(self.repo.read_one(r2['id']))


class TestRepositorySearch(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.repo = Repository(self._tmp.name)

    def tearDown(self):
        if os.path.exists(self._tmp.name):
            os.unlink(self._tmp.name)

    def test_search_by_key_value(self):
        self.repo.create({'name': 'Alice', 'city': 'Seoul'})
        self.repo.create({'name': 'Bob', 'city': 'Busan'})
        result = self.repo.search('name', 'Alice')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Alice')

    def test_search_no_match_returns_empty(self):
        self.repo.create({'name': 'Alice'})
        result = self.repo.search('name', 'Charlie')
        self.assertEqual(result, [])

    def test_search_multiple_matches(self):
        self.repo.create({'city': 'Seoul', 'name': 'Alice'})
        self.repo.create({'city': 'Seoul', 'name': 'Bob'})
        self.repo.create({'city': 'Busan', 'name': 'Charlie'})
        result = self.repo.search('city', 'Seoul')
        self.assertEqual(len(result), 2)

    def test_search_nonexistent_key_returns_empty(self):
        self.repo.create({'name': 'Alice'})
        result = self.repo.search('email', 'alice@example.com')
        self.assertEqual(result, [])


class TestRepositoryPersistence(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self._tmp.close()
        os.unlink(self._tmp.name)
        self.path = self._tmp.name

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_data_persists_across_instances(self):
        repo1 = Repository(self.path)
        created = repo1.create({'name': 'Alice'})

        repo2 = Repository(self.path)
        result = repo2.read_one(created['id'])
        self.assertEqual(result['name'], 'Alice')

    def test_multiple_records_persist(self):
        repo1 = Repository(self.path)
        repo1.create({'name': 'Alice'})
        repo1.create({'name': 'Bob'})

        repo2 = Repository(self.path)
        self.assertEqual(len(repo2.read_all()), 2)


if __name__ == '__main__':
    unittest.main()
