from abc import ABC, abstractmethod
from typing import List
import vinyl.lex as lex

from ..patch import unittest


class TestLexerBase(ABC, unittest.TestCase):
    @staticmethod
    @abstractmethod
    def good_inputs() -> List[str]:
        return []

    @staticmethod
    @abstractmethod
    def bad_inputs() -> List[str]:
        return []

    @staticmethod
    @abstractmethod
    def token_class() -> type(lex.BaseToken):
        return lex.BaseToken

    def test_good_inputs(self):
        for good in self.good_inputs():
            istream = lex.StringStream(good)
            self.assertIsInstance(next(lex.Lexer(istream)), self.token_class())

    def test_bad_inputs(self):
        for bad in self.bad_inputs():
            istream = lex.StringStream(bad)
            try:
                self.assertNotEqual(type(next(lex.Lexer(istream))), self.token_class())
            except StopIteration:
                self.assertTrue(istream.ended)
            except Exception as e:
                self.assertIsInstance(e, lex.SyntacticalError)


class TestIdentifierLexer(TestLexerBase):
    @staticmethod
    def good_inputs() -> List[str]:
        return [
            'a',
            'hello',
            'こんにちは',
            ' \tafter_Whitespace',
            'hasANumber42',
        ]

    @staticmethod
    def bad_inputs() -> List[str]:
        return TestKeywordLexer.good_inputs() + \
               TestSymbolLexer.good_inputs() + [
            '1number',
            '.E13',
            '1e3',
            ' ',
            '\n\n\n\n\n\n\n\n'
        ]

    @staticmethod
    def token_class() -> type(lex.IdentifierToken):
        return lex.IdentifierToken


class TestKeywordLexer(TestLexerBase):
    @staticmethod
    def good_inputs() -> List[str]:
        return [enum.value for enum in lex.KeywordTokenKind]

    @staticmethod
    def bad_inputs() -> List[str]:
        return TestSymbolLexer.good_inputs()

    @staticmethod
    def token_class() -> type(lex.KeywordToken):
        return lex.KeywordToken


class TestSymbolLexer(TestLexerBase):
    @staticmethod
    def good_inputs() -> List[str]:
        return [enum.value for enum in lex.SymbolTokenKind]

    @staticmethod
    def bad_inputs() -> List[str]:
        return TestKeywordLexer.good_inputs()

    @staticmethod
    def token_class() -> type(lex.SymbolToken):
        return lex.SymbolToken


class TestIntegerLexer(TestLexerBase):
    @staticmethod
    def good_inputs() -> List[str]:
        return [
            '1',
            '1_000',
            '0xBEEFi',
            '0b1000_0001_1001u32'
        ]

    @staticmethod
    def bad_inputs() -> List[str]:
        return TestFloatLexer.good_inputs()

    @staticmethod
    def token_class() -> type(lex.IntegerToken):
        return lex.IntegerToken


class TestFloatLexer(TestLexerBase):
    @staticmethod
    def good_inputs() -> List[str]:
        return []

    @staticmethod
    def bad_inputs() -> List[str]:
        return TestIntegerLexer.good_inputs()

    @staticmethod
    def token_class() -> type(lex.FloatToken):
        return lex.FloatToken