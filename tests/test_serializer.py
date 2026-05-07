import unittest
from json_lib.serializer import serialize, SerializeError


class TestSerializePrimitives(unittest.TestCase):

    def test_serialize_string(self):
        self.assertEqual(serialize("hello"), '"hello"')

    def test_serialize_integer(self):
        self.assertEqual(serialize(42), '42')

    def test_serialize_float(self):
        self.assertEqual(serialize(3.14), '3.14')

    def test_serialize_bool_true(self):
        self.assertEqual(serialize(True), 'true')

    def test_serialize_bool_false(self):
        self.assertEqual(serialize(False), 'false')

    def test_serialize_none(self):
        self.assertEqual(serialize(None), 'null')

    def test_serialize_bool_not_int(self):
        # bool은 int 서브클래스이므로 true/false가 출력되어야 함
        self.assertNotEqual(serialize(True), '1')
        self.assertNotEqual(serialize(False), '0')
        self.assertEqual(serialize(True), 'true')
        self.assertEqual(serialize(False), 'false')


class TestSerializeStringEscape(unittest.TestCase):

    def test_serialize_string_escape_quote(self):
        self.assertEqual(serialize('foo"bar'), r'"foo\"bar"')

    def test_serialize_string_escape_backslash(self):
        self.assertEqual(serialize('foo\\bar'), r'"foo\\bar"')

    def test_serialize_string_escape_newline(self):
        self.assertEqual(serialize('foo\nbar'), r'"foo\nbar"')

    def test_serialize_string_escape_tab(self):
        self.assertEqual(serialize('foo\tbar'), r'"foo\tbar"')


class TestSerializeObject(unittest.TestCase):

    def test_serialize_empty_object(self):
        self.assertEqual(serialize({}), '{}')

    def test_serialize_simple_object(self):
        result = serialize({"key": "value"})
        self.assertEqual(result, '{"key": "value"}')

    def test_serialize_nested(self):
        result = serialize({"a": {"b": 1}})
        self.assertEqual(result, '{"a": {"b": 1}}')


class TestSerializeArray(unittest.TestCase):

    def test_serialize_empty_array(self):
        self.assertEqual(serialize([]), '[]')

    def test_serialize_simple_array(self):
        self.assertEqual(serialize([1, 2, 3]), '[1, 2, 3]')

    def test_serialize_array_mixed(self):
        result = serialize([1, "two", True, None])
        self.assertEqual(result, '[1, "two", true, null]')


class TestSerializeIndent(unittest.TestCase):

    def test_serialize_indent_object(self):
        result = serialize({"a": 1, "b": 2}, indent=2)
        expected = '{\n  "a": 1,\n  "b": 2\n}'
        self.assertEqual(result, expected)

    def test_serialize_indent_array(self):
        result = serialize([1, 2, 3], indent=2)
        expected = '[\n  1,\n  2,\n  3\n]'
        self.assertEqual(result, expected)

    def test_serialize_indent_nested(self):
        result = serialize({"a": [1, 2]}, indent=2)
        expected = '{\n  "a": [\n    1,\n    2\n  ]\n}'
        self.assertEqual(result, expected)


class TestSerializeError(unittest.TestCase):

    def test_serialize_unsupported_type_set(self):
        with self.assertRaises(SerializeError):
            serialize({1, 2, 3})

    def test_serialize_unsupported_type_tuple(self):
        with self.assertRaises(SerializeError):
            serialize((1, 2))


if __name__ == "__main__":
    unittest.main()
