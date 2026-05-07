import unittest
from json_lib.lexer import tokenize, TokenType, LexError


class TestLexerString(unittest.TestCase):

    def test_string_simple(self):
        tokens = tokenize('"hello"')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].value, "hello")

    def test_string_escape(self):
        tokens = tokenize(r'"foo\"bar"')
        self.assertEqual(tokens[0].value, 'foo"bar')

        tokens = tokenize(r'"foo\\bar"')
        self.assertEqual(tokens[0].value, 'foo\\bar')

        tokens = tokenize(r'"foo\nbar"')
        self.assertEqual(tokens[0].value, 'foo\nbar')

        tokens = tokenize(r'"foo\tbar"')
        self.assertEqual(tokens[0].value, 'foo\tbar')

    def test_string_unterminated(self):
        with self.assertRaises(LexError):
            tokenize('"hello')


class TestLexerNumber(unittest.TestCase):

    def test_number_integer(self):
        tokens = tokenize('42')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, 42)
        self.assertIsInstance(tokens[0].value, int)

    def test_number_negative(self):
        tokens = tokenize('-7')
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertEqual(tokens[0].value, -7)

    def test_number_float(self):
        tokens = tokenize('3.14')
        self.assertEqual(tokens[0].type, TokenType.NUMBER)
        self.assertAlmostEqual(tokens[0].value, 3.14)
        self.assertIsInstance(tokens[0].value, float)

    def test_number_invalid(self):
        with self.assertRaises(LexError):
            tokenize('-')


class TestLexerKeyword(unittest.TestCase):

    def test_bool_true(self):
        tokens = tokenize('true')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.BOOL)
        self.assertIs(tokens[0].value, True)

    def test_bool_false(self):
        tokens = tokenize('false')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.BOOL)
        self.assertIs(tokens[0].value, False)

    def test_null(self):
        tokens = tokenize('null')
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.NULL)
        self.assertIsNone(tokens[0].value)


class TestLexerStructural(unittest.TestCase):

    def test_structural_tokens(self):
        tokens = tokenize('{}[]:,')
        types = [t.type for t in tokens]
        self.assertEqual(types, [
            TokenType.LBRACE,
            TokenType.RBRACE,
            TokenType.LBRACKET,
            TokenType.RBRACKET,
            TokenType.COLON,
            TokenType.COMMA,
        ])

    def test_whitespace_ignored(self):
        tokens = tokenize('  {  \t\n  }  ')
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.LBRACE)
        self.assertEqual(tokens[1].type, TokenType.RBRACE)

    def test_unknown_character(self):
        with self.assertRaises(LexError):
            tokenize('@')


class TestLexerComposite(unittest.TestCase):

    def test_composite_object(self):
        tokens = tokenize('{"name": "Alice", "age": 30}')
        types = [t.type for t in tokens]
        self.assertEqual(types, [
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.STRING,
            TokenType.COMMA,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.NUMBER,
            TokenType.RBRACE,
        ])
        self.assertEqual(tokens[1].value, "name")
        self.assertEqual(tokens[3].value, "Alice")
        self.assertEqual(tokens[5].value, "age")
        self.assertEqual(tokens[7].value, 30)

    def test_composite_array(self):
        tokens = tokenize('[1, true, null, "x"]')
        types = [t.type for t in tokens]
        self.assertEqual(types, [
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.BOOL,
            TokenType.COMMA,
            TokenType.NULL,
            TokenType.COMMA,
            TokenType.STRING,
            TokenType.RBRACKET,
        ])
        self.assertEqual(tokens[1].value, 1)
        self.assertIs(tokens[3].value, True)
        self.assertIsNone(tokens[5].value)
        self.assertEqual(tokens[7].value, "x")

    def test_nested_structure(self):
        tokens = tokenize('{"a": [1, {"b": 2}]}')
        types = [t.type for t in tokens]
        self.assertEqual(types, [
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.LBRACKET,
            TokenType.NUMBER,
            TokenType.COMMA,
            TokenType.LBRACE,
            TokenType.STRING,
            TokenType.COLON,
            TokenType.NUMBER,
            TokenType.RBRACE,
            TokenType.RBRACKET,
            TokenType.RBRACE,
        ])


if __name__ == "__main__":
    unittest.main()
