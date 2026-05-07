import unittest
from json_lib.lexer import tokenize
from json_lib.parser import parse, ParseError


def tok(text):
    return tokenize(text)


class TestParserPrimitives(unittest.TestCase):

    def test_parse_string(self):
        result = parse(tok('"hello"'))
        self.assertEqual(result, "hello")
        self.assertIsInstance(result, str)

    def test_parse_integer(self):
        result = parse(tok('42'))
        self.assertEqual(result, 42)
        self.assertIsInstance(result, int)

    def test_parse_float(self):
        result = parse(tok('3.14'))
        self.assertAlmostEqual(result, 3.14)
        self.assertIsInstance(result, float)

    def test_parse_bool_true(self):
        result = parse(tok('true'))
        self.assertIs(result, True)

    def test_parse_bool_false(self):
        result = parse(tok('false'))
        self.assertIs(result, False)

    def test_parse_null(self):
        result = parse(tok('null'))
        self.assertIsNone(result)


class TestParserObject(unittest.TestCase):

    def test_parse_empty_object(self):
        result = parse(tok('{}'))
        self.assertEqual(result, {})
        self.assertIsInstance(result, dict)

    def test_parse_simple_object(self):
        result = parse(tok('{"key": "value"}'))
        self.assertEqual(result, {"key": "value"})

    def test_parse_object_multiple_keys(self):
        result = parse(tok('{"a": 1, "b": true, "c": null}'))
        self.assertEqual(result, {"a": 1, "b": True, "c": None})

    def test_parse_nested_object(self):
        result = parse(tok('{"outer": {"inner": 42}}'))
        self.assertEqual(result, {"outer": {"inner": 42}})

    def test_parse_object_with_array(self):
        result = parse(tok('{"nums": [1, 2, 3]}'))
        self.assertEqual(result, {"nums": [1, 2, 3]})


class TestParserArray(unittest.TestCase):

    def test_parse_empty_array(self):
        result = parse(tok('[]'))
        self.assertEqual(result, [])
        self.assertIsInstance(result, list)

    def test_parse_simple_array(self):
        result = parse(tok('[1, 2, 3]'))
        self.assertEqual(result, [1, 2, 3])

    def test_parse_array_mixed_types(self):
        result = parse(tok('[1, "two", true, null, 3.14]'))
        self.assertEqual(result, [1, "two", True, None, 3.14])

    def test_parse_nested_array(self):
        result = parse(tok('[[1, 2], [3, 4]]'))
        self.assertEqual(result, [[1, 2], [3, 4]])


class TestParserErrors(unittest.TestCase):

    def test_unexpected_token(self):
        with self.assertRaises(ParseError):
            parse(tok(':'))

    def test_missing_colon(self):
        with self.assertRaises(ParseError):
            parse(tok('{"key" "value"}'))

    def test_missing_closing_brace(self):
        with self.assertRaises(ParseError):
            parse(tok('{"key": "value"'))

    def test_missing_closing_bracket(self):
        with self.assertRaises(ParseError):
            parse(tok('[1, 2'))

    def test_trailing_tokens(self):
        with self.assertRaises(ParseError):
            parse(tok('42 99'))


if __name__ == "__main__":
    unittest.main()
