import os
import tempfile
import unittest
import json_lib
from json_lib.lexer import LexError
from json_lib.parser import ParseError


SAMPLE_PATH = os.path.join(os.path.dirname(__file__), '..', 'sample.json')


class TestLoad(unittest.TestCase):

    def test_load_simple_file(self):
        result = json_lib.load(SAMPLE_PATH)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['title'], 'JSON POC')
        self.assertEqual(result['version'], 1)
        self.assertIs(result['stable'], True)
        self.assertAlmostEqual(result['score'], 9.5)
        self.assertEqual(result['tags'], ['json', 'poc', 'python'])
        self.assertEqual(result['author'], {'name': 'Alice', 'active': True})
        self.assertIsNone(result['note'])

    def test_load_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            json_lib.load('nonexistent_file.json')

    def test_load_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         delete=False, encoding='utf-8') as f:
            f.write('{invalid}')
            path = f.name
        try:
            with self.assertRaises((LexError, ParseError)):
                json_lib.load(path)
        finally:
            os.unlink(path)


class TestDump(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            suffix='.json', delete=False, encoding='utf-8', mode='w'
        )
        self._tmp.close()
        self.path = self._tmp.name

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_dump_creates_file(self):
        json_lib.dump({'x': 1}, self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_dump_file_content(self):
        json_lib.dump({'key': 'value'}, self.path)
        with open(self.path, encoding='utf-8') as f:
            content = f.read()
        self.assertIn('"key"', content)
        self.assertIn('"value"', content)

    def test_dump_load_empty_object(self):
        json_lib.dump({}, self.path)
        result = json_lib.load(self.path)
        self.assertEqual(result, {})

    def test_dump_load_empty_array(self):
        json_lib.dump([], self.path)
        result = json_lib.load(self.path)
        self.assertEqual(result, [])

    def test_dump_indent_pretty(self):
        json_lib.dump({'a': 1}, self.path, indent=2)
        with open(self.path, encoding='utf-8') as f:
            content = f.read()
        self.assertIn('\n', content)
        self.assertIn('  ', content)


class TestRoundTrip(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(
            suffix='.json', delete=False, encoding='utf-8', mode='w'
        )
        self._tmp.close()
        self.path = self._tmp.name

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_round_trip_simple(self):
        original = {'name': 'Bob', 'age': 25}
        json_lib.dump(original, self.path)
        result = json_lib.load(self.path)
        self.assertEqual(result, original)

    def test_round_trip_nested(self):
        original = {'outer': {'inner': [1, 2, 3]}}
        json_lib.dump(original, self.path)
        result = json_lib.load(self.path)
        self.assertEqual(result, original)

    def test_round_trip_all_types(self):
        original = {
            'str':   'hello',
            'int':   42,
            'float': 3.14,
            'true':  True,
            'false': False,
            'null':  None,
            'list':  [1, 'two', None],
            'obj':   {'nested': True},
        }
        json_lib.dump(original, self.path)
        result = json_lib.load(self.path)
        self.assertEqual(result['str'],   original['str'])
        self.assertEqual(result['int'],   original['int'])
        self.assertAlmostEqual(result['float'], original['float'])
        self.assertIs(result['true'],     True)
        self.assertIs(result['false'],    False)
        self.assertIsNone(result['null'])
        self.assertEqual(result['list'],  original['list'])
        self.assertEqual(result['obj'],   original['obj'])


if __name__ == "__main__":
    unittest.main()
